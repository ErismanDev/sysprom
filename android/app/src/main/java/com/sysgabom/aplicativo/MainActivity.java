package com.sysgabom.aplicativo;

import android.app.Activity;
import android.os.Bundle;
import android.net.Uri;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.os.Build;
import android.webkit.CookieManager;
import android.webkit.SslErrorHandler;
import android.net.http.SslError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceError;
import android.webkit.WebResourceResponse;

public class MainActivity extends Activity {
    private WebView webView;
    private String lastMainUrl;
    private String appHost;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        try {
            settings.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.TEXT_AUTOSIZING);
        } catch (Throwable ignored) {
            try {
                settings.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.SINGLE_COLUMN);
            } catch (Throwable ignored2) {}
        }

        if (Build.VERSION.SDK_INT >= 19) {
            WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);
        }
        if (Build.VERSION.SDK_INT >= 21) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        }
        CookieManager.getInstance().setAcceptCookie(true);
        if (Build.VERSION.SDK_INT >= 21) {
            CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);
        }
        try {
            Uri baseUri = Uri.parse(BuildConfig.BASE_URL);
            appHost = baseUri.getHost();
        } catch (Throwable ignored) {
            appHost = null;
        }
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (request == null || !request.isForMainFrame()) {
                    return false;
                }
                String url = request.getUrl().toString();
                Uri uri = Uri.parse(url);
                String host = uri.getHost();
                boolean isSameAppHost = appHost != null && host != null && host.equalsIgnoreCase(appHost);
                if (isSameAppHost) {
                    if (!uri.getQueryParameterNames().contains("apk")) {
                        String newUrl = uri.buildUpon().appendQueryParameter("apk", "1").build().toString();
                        lastMainUrl = newUrl;
                        view.loadUrl(newUrl);
                        return true;
                    }
                    lastMainUrl = url;
                    return false;
                }
                return false;
            }
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request != null && request.isForMainFrame()) {
                    String msg = String.valueOf(error.getDescription());
                    showError(msg);
                }
            }
            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                if (BuildConfig.ALLOW_INSECURE_SSL) {
                    handler.proceed();
                    return;
                }
                String msg = "Falha SSL";
                showError(msg);
            }
            @Override
            public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse errorResponse) {
                if (request != null && request.isForMainFrame()) {
                    int code = errorResponse.getStatusCode();
                    if (code >= 400 && code < 500) {
                        String fallback = BuildConfig.BASE_URL;
                        lastMainUrl = fallback;
                        view.loadUrl(fallback);
                        return;
                    }
                    String msg = "HTTP " + code;
                    showError(msg);
                }
            }
        });
        webView.setWebChromeClient(new WebChromeClient());

        lastMainUrl = BuildConfig.BASE_URL;
        webView.loadUrl(lastMainUrl);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    private void showError(String message) {
        String html = "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"></head><body style=\"font-family:sans-serif;padding:16px\"><h2>Erro ao carregar</h2><p>" +
                (message == null ? "" : message) +
                "</p>" +
                (lastMainUrl != null ? ("<p style=\"color:#666;font-size:12px\">URL: " + lastMainUrl + "</p>") : "") +
                "<button onclick=\"location.reload()\" style=\"padding:10px 16px;font-size:16px\">Tentar novamente</button></body></html>";
        webView.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null);
    }
}
