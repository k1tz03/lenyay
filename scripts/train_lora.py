"""Entraînement LoRA de Lenyay v0.2 — À LANCER SUR LE GPU LOUÉ (pas en local).

Script AUTONOME : à uploader sur le pod avec le dataset, rien d'autre.

Sur le pod (image PyTorch, une seule fois) :
    pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo

Lancement :
    python train_lora.py dataset-2026-07-28-2299.jsonl

Produit dans lenyay-v0.2/ :
    - lora-adapter/            l'adaptateur seul (léger, archivable)
    - *q4_k_m*.gguf            LE fichier à rapatrier dans models/ en local

Réglages : QLoRA 4-bit, r=16, alpha=16, lr 2e-4 cosine, 3 époques, seed 42.
Le chat template Qwen du tokenizer est appliqué tel quel — le GGUF produit
se comporte donc exactement comme le modèle de base face à llama.cpp
(worker et éval inchangés).
"""

import argparse
import json
import random
import sys
from pathlib import Path


def load_and_validate(path: Path) -> list[dict]:
    """Charge le dataset chat JSONL et vérifie sa structure (testable sans GPU)."""
    examples = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            messages = record.get("messages")
            roles = [m.get("role") for m in messages] if isinstance(messages, list) else None
            if roles != ["system", "user", "assistant"]:
                sys.exit(f"Ligne {lineno} : format inattendu (rôles {roles}) — "
                         "le dataset doit venir de scripts/export_dataset.py")
            if not all(isinstance(m.get("content"), str) and m["content"] for m in messages):
                sys.exit(f"Ligne {lineno} : contenu vide")
            examples.append(record)
    if not examples:
        sys.exit("Dataset vide")
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tuning LoRA Lenyay v0.2")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--base-model", default="unsloth/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--out", type=Path, default=Path("lenyay-v0.2"))
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--val-fraction", type=float, default=0.05)
    args = parser.parse_args()

    examples = load_and_validate(args.dataset)
    print(f"{len(examples)} exemples valides chargés depuis {args.dataset}")

    import torch
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    try:  # le nom canonique a changé selon les versions d'unsloth
        from unsloth import FastModel
    except ImportError:  # pragma: no cover
        from unsloth import FastLanguageModel as FastModel

    model, tokenizer = FastModel.from_pretrained(
        model_name=args.base_model,
        max_seq_length=2048,
        load_in_4bit=True,
    )
    model = FastModel.get_peft_model(
        model,
        r=16,
        lora_alpha=16,
        lora_dropout=0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    def to_text(example: dict) -> dict:
        return {"text": tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False)}

    random.Random(42).shuffle(examples)
    n_val = max(1, int(len(examples) * args.val_fraction))
    ds_val = Dataset.from_list(examples[:n_val]).map(to_text, remove_columns=["messages"])
    ds_train = Dataset.from_list(examples[n_val:]).map(to_text, remove_columns=["messages"])
    print(f"train : {len(ds_train)} | validation : {len(ds_val)}")
    print("--- aperçu d'un exemple formaté (vérifie le template) ---")
    print(ds_train[0]["text"][:400])
    print("---------------------------------------------------------")

    # TRL récent a renommé max_seq_length -> max_length : on détecte.
    import inspect

    seq_param = ("max_length"
                 if "max_length" in inspect.signature(SFTConfig.__init__).parameters
                 else "max_seq_length")
    config = SFTConfig(
        output_dir=str(args.out / "checkpoints"),
        dataset_text_field="text",
        **{seq_param: 2048},
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        num_train_epochs=args.epochs,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="no",
        seed=42,
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        report_to="none",
    )
    try:  # TRL récent : processing_class ; anciennes versions : tokenizer
        trainer = SFTTrainer(model=model, processing_class=tokenizer, args=config,
                             train_dataset=ds_train, eval_dataset=ds_val)
    except TypeError:  # pragma: no cover
        trainer = SFTTrainer(model=model, tokenizer=tokenizer, args=config,
                             train_dataset=ds_train, eval_dataset=ds_val)

    try:  # n'apprendre que sur les réponses de l'assistant (qualité ++)
        from unsloth.chat_templates import train_on_responses_only
        trainer = train_on_responses_only(
            trainer,
            instruction_part="<|im_start|>user\n",
            response_part="<|im_start|>assistant\n",
        )
        print("Masquage activé : la perte ne porte que sur les réponses de l'assistant.")
    except Exception as exc:  # pragma: no cover
        print(f"(masquage indisponible — entraînement pleine séquence : {exc})")

    trainer.train()

    args.out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(args.out / "lora-adapter"))
    tokenizer.save_pretrained(str(args.out / "lora-adapter"))
    print("Adaptateur LoRA sauvé — export GGUF q4_k_m (peut prendre plusieurs minutes)...")
    model.save_pretrained_gguf(str(args.out), tokenizer, quantization_method="q4_k_m")
    print(f"\nTerminé. Rapatrie le fichier *q4_k_m*.gguf de {args.out}/ vers models/ "
          "en le renommant lenyay-v0.2-q4_k_m.gguf, puis ARRÊTE LE POD.")


if __name__ == "__main__":
    main()
