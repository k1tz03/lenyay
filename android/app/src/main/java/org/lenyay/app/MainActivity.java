package org.lenyay.app;

// L'application Android de Lenyay — une coquille native autour du chat,
// comme l'application de bureau : la page bascule d'elle-même en mode
// application. Zéro dépendance : la WebView du système suffit, l'APK reste
// minuscule et le build ne peut presque pas casser.
//
// La contribution (calcul nocturne pendant la charge) est le chantier
// suivant : un service de premier plan + llama.cpp compilé pour arm64.
// Elle s'ajoutera ici sans changer cette coquille.

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView web;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#F2F6F3"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);        // le chat est une application JS
        s.setDomStorageEnabled(true);        // la langue choisie (localStorage)
        s.setSupportZoom(false);
        // La page reconnaît l'application à cette signature et masque la
        // navigation du site (même mécanisme que la coquille de bureau).
        s.setUserAgentString(s.getUserAgentString() + " LenyayApp/0.9");
        CookieManager.getInstance().setAcceptCookie(true); // la session du compte

        final String home = getString(R.string.lenyay_url);
        final String homeHost = Uri.parse(home).getHost();

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                // Lenyay reste dans l'app ; le reste (GitHub…) part au navigateur.
                if (url.getHost() != null && url.getHost().equals(homeHost)) {
                    return false;
                }
                startActivity(new Intent(Intent.ACTION_VIEW, url));
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request,
                                        android.webkit.WebResourceError error) {
                if (request.isForMainFrame()) {
                    view.loadData(
                        "<html><body style='font-family:sans-serif;background:#F2F6F3;"
                        + "color:#1E2B27;display:flex;align-items:center;justify-content:center;"
                        + "height:95vh;text-align:center'><div><h2>Lenyay</h2>"
                        + "<p>Pas de connexion — réessaie dans un instant.<br>"
                        + "No connection — try again in a moment.</p></div></body></html>",
                        "text/html; charset=utf-8", "utf-8");
                }
            }
        });

        if (savedInstanceState == null) {
            web.loadUrl(home);
        } else {
            web.restoreState(savedInstanceState);
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState); // la rotation ne perd pas la conversation
    }

    @Override
    public void onBackPressed() {
        // Le bouton retour navigue dans l'app avant de la quitter.
        if (web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            ((View) web.getParent()).clearFocus();
            web.destroy();
        }
        super.onDestroy();
    }
}
