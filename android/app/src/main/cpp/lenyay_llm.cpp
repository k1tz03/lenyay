// Le moteur de contribution mobile — pont JNI minimal au-dessus de llama.cpp.
//
// Une seule opération : answer(system, user) → texte complet. Pas de
// streaming, pas de conversation continue : le worker résout des tâches,
// chaque appel repart d'un contexte propre. Modelé sur l'exemple officiel
// examples/llama.android (mêmes appels, même ordre), réduit à l'essentiel.

#include <android/log.h>
#include <jni.h>
#include <string>
#include <unistd.h>

#include "chat.h"
#include "common.h"
#include "llama.h"
#include "sampling.h"

#define TAG "lenyay_llm"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

constexpr int N_CTX      = 2048;   // une tâche + sa réponse, largement
constexpr int BATCH_SIZE = 256;
constexpr int HEADROOM   = 4;

static llama_model             *g_model    = nullptr;
static llama_context           *g_ctx      = nullptr;
static llama_batch              g_batch;
static common_sampler          *g_sampler  = nullptr;
static common_chat_templates_ptr g_templates;

extern "C" JNIEXPORT jint JNICALL
Java_org_lenyay_app_Llm_load(JNIEnv *env, jclass, jstring jpath) {
    if (g_model) { return 0; }  // déjà chargé
    llama_backend_init();

    const char *path = env->GetStringUTFChars(jpath, nullptr);
    LOGI("Chargement du modèle : %s", path);
    llama_model_params mp = llama_model_default_params();
    g_model = llama_model_load_from_file(path, mp);
    env->ReleaseStringUTFChars(jpath, path);
    if (!g_model) { LOGE("Échec du chargement du modèle"); return 1; }

    const int n_threads = std::max(2, std::min(4, (int) sysconf(_SC_NPROCESSORS_ONLN) - 2));
    llama_context_params cp = llama_context_default_params();
    cp.n_ctx = N_CTX;
    cp.n_batch = BATCH_SIZE;
    cp.n_ubatch = BATCH_SIZE;
    cp.n_threads = n_threads;
    cp.n_threads_batch = n_threads;
    g_ctx = llama_init_from_model(g_model, cp);
    if (!g_ctx) { LOGE("Échec de la création du contexte"); return 2; }

    g_batch = llama_batch_init(BATCH_SIZE, 0, 1);
    g_templates = common_chat_templates_init(g_model, "");

    common_params_sampling sp;
    sp.temp = 0.8f;               // la température du worker de bureau
    g_sampler = common_sampler_init(g_model, sp);
    LOGI("Modèle prêt (%d threads)", n_threads);
    return 0;
}

// Décode une suite de jetons par lots ; renvoie false si llama_decode échoue.
static bool decode_all(const llama_tokens &tokens, llama_pos start,
                       bool last_logit) {
    for (int i = 0; i < (int) tokens.size(); i += BATCH_SIZE) {
        const int n = std::min((int) tokens.size() - i, BATCH_SIZE);
        common_batch_clear(g_batch);
        for (int j = 0; j < n; j++) {
            const bool want = last_logit && (i + j == (int) tokens.size() - 1);
            common_batch_add(g_batch, tokens[i + j], start + i + j, {0}, want);
        }
        if (llama_decode(g_ctx, g_batch) != 0) { return false; }
    }
    return true;
}

// Tronque proprement une chaîne à sa dernière séquence UTF-8 complète :
// NewStringUTF plante la JVM sur de l'UTF-8 invalide.
static void trim_to_valid_utf8(std::string &s) {
    while (!s.empty()) {
        const auto last = (unsigned char) s.back();
        if ((last & 0x80) == 0) { return; }              // ASCII final : ok
        size_t i = s.size();
        while (i > 0 && ((unsigned char) s[i - 1] & 0xC0) == 0x80) { i--; }
        if (i == 0) { s.clear(); return; }
        const auto lead = (unsigned char) s[i - 1];
        const size_t need = (lead & 0xE0) == 0xC0 ? 2 : (lead & 0xF0) == 0xE0 ? 3
                          : (lead & 0xF8) == 0xF0 ? 4 : 0;
        if (need && s.size() - i + 1 == need) { return; }  // séquence complète
        s.resize(i - 1);                                    // séquence coupée
    }
}

extern "C" JNIEXPORT jstring JNICALL
Java_org_lenyay_app_Llm_answer(JNIEnv *env, jclass, jstring jsystem,
                               jstring juser, jint n_predict) {
    if (!g_ctx) { return nullptr; }

    // Contexte propre à chaque tâche : rien ne fuit d'une tâche à l'autre.
    llama_memory_clear(llama_get_memory(g_ctx), false);
    common_sampler_reset(g_sampler);

    const char *csystem = env->GetStringUTFChars(jsystem, nullptr);
    const char *cuser   = env->GetStringUTFChars(juser, nullptr);
    std::vector<common_chat_msg> history;
    common_chat_msg sys_msg;  sys_msg.role = "system"; sys_msg.content = csystem;
    std::string f_sys = common_chat_format_single(g_templates.get(), history,
                                                  sys_msg, false, false);
    history.push_back(sys_msg);
    common_chat_msg usr_msg;  usr_msg.role = "user"; usr_msg.content = cuser;
    std::string f_usr = common_chat_format_single(g_templates.get(), history,
                                                  usr_msg, true, false);
    env->ReleaseStringUTFChars(jsystem, csystem);
    env->ReleaseStringUTFChars(juser, cuser);

    const auto sys_tokens = common_tokenize(g_ctx, f_sys, true, true);
    const auto usr_tokens = common_tokenize(g_ctx, f_usr, false, true);
    const int prompt_len = (int) (sys_tokens.size() + usr_tokens.size());
    if (prompt_len >= N_CTX - HEADROOM - 16) {
        LOGE("Tâche trop longue pour le contexte mobile (%d jetons)", prompt_len);
        return nullptr;
    }

    if (!decode_all(sys_tokens, 0, false) ||
        !decode_all(usr_tokens, (llama_pos) sys_tokens.size(), true)) {
        LOGE("llama_decode a échoué sur l'amorce");
        return nullptr;
    }

    const llama_vocab *vocab = llama_model_get_vocab(g_model);
    llama_pos pos = prompt_len;
    const llama_pos stop = std::min((llama_pos) (N_CTX - HEADROOM),
                                    pos + n_predict);
    std::string out;
    while (pos < stop) {
        const llama_token tok = common_sampler_sample(g_sampler, g_ctx, -1);
        common_sampler_accept(g_sampler, tok, true);
        if (llama_vocab_is_eog(vocab, tok)) { break; }
        out += common_token_to_piece(g_ctx, tok);

        common_batch_clear(g_batch);
        common_batch_add(g_batch, tok, pos, {0}, true);
        if (llama_decode(g_ctx, g_batch) != 0) {
            LOGE("llama_decode a échoué en génération");
            break;
        }
        pos++;
    }

    trim_to_valid_utf8(out);
    return env->NewStringUTF(out.c_str());
}
