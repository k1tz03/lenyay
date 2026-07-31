package org.lenyay.app;

// Le moteur, vu de Java. Si la bibliothèque native n'est pas dans l'APK
// (build sans llama.dir), l'application fonctionne quand même — sans
// contribution : available() dit la vérité, personne ne promet à sa place.
public final class Llm {

    private static final boolean NATIVE_OK;

    static {
        boolean ok;
        try {
            System.loadLibrary("lenyay_llm");
            ok = true;
        } catch (UnsatisfiedLinkError e) {
            ok = false;
        }
        NATIVE_OK = ok;
    }

    private Llm() {}

    public static boolean available() {
        return NATIVE_OK;
    }

    /** Charge le modèle (idempotent). 0 = prêt. */
    public static native int load(String modelPath);

    /** Une réponse complète, bloquante. null = échec. */
    public static native String answer(String systemPrompt, String userPrompt,
                                       int maxTokens);
}
