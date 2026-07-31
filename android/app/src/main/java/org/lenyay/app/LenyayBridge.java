package org.lenyay.app;

// Le pont entre la page et l'application — le pendant Android de l'API
// pywebview du bureau. La page voit window.lenyayAndroid et branche le même
// interrupteur « Contribuer ». Retours synchrones (chaînes JSON).

import android.content.Context;
import android.content.Intent;
import android.webkit.JavascriptInterface;

public class LenyayBridge {

    private final Context context;

    public LenyayBridge(Context context) {
        this.context = context;
    }

    @JavascriptInterface
    public String status() {
        return WorkerService.statusJson();
    }

    @JavascriptInterface
    public void startContribute() {
        Intent i = new Intent(context, WorkerService.class);
        context.startForegroundService(i);
    }

    @JavascriptInterface
    public void stopContribute() {
        context.stopService(new Intent(context, WorkerService.class));
    }

    @JavascriptInterface
    public void setAccountKey(String key) {
        // Les gains de ce téléphone iront sur le compte connecté dans la page.
        context.getSharedPreferences("lenyay", Context.MODE_PRIVATE)
               .edit().putString("account_key", key).apply();
    }
}
