package com.example.fantamasterai

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Bitmap
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.*
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import kotlinx.coroutines.*
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private val scope = CoroutineScope(Dispatchers.Main + Job())

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Imposta la barra di stato e la barra di navigazione con sfondo scuro e icone chiare
        window.statusBarColor = 0xFF0A0E1A.toInt()
        window.navigationBarColor = 0xFF0A0E1A.toInt()
        val insetsController = WindowCompat.getInsetsController(window, window.decorView)
        insetsController.isAppearanceLightStatusBars = false
        insetsController.isAppearanceLightNavigationBars = false

        val rootLayout = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(0xFF0A0E1A.toInt())
        }

        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(0xFF0A0E1A.toInt())
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = true
            settings.allowContentAccess = true
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.cacheMode = WebSettings.LOAD_DEFAULT
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            // Ottimizzazioni per tablet e schermi touch
            settings.builtInZoomControls = true
            settings.displayZoomControls = false

            webViewClient = object : WebViewClient() {
                override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                }

                override fun onReceivedError(
                    view: WebView?,
                    request: WebResourceRequest?,
                    error: WebResourceError?
                ) {
                    super.onReceivedError(view, request, error)
                    if (request?.isForMainFrame == true) {
                        loadLocalAsset()
                    }
                }
            }

            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                    return super.onConsoleMessage(consoleMessage)
                }
            }

            addJavascriptInterface(WebAppInterface(this@MainActivity), "Android")
        }

        rootLayout.addView(webView)
        setContentView(rootLayout)

        // Padding dinamico in base alle safe insets (notifiche/orologio/notch e barra gesture)
        ViewCompat.setOnApplyWindowInsetsListener(rootLayout) { view, insets ->
            val statusBars = insets.getInsets(WindowInsetsCompat.Type.statusBars())
            val navBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
            view.setPadding(0, statusBars.top, 0, navBars.bottom)
            insets
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })

        determineAndLoadUrl()
    }

    private fun determineAndLoadUrl() {
        val prefs = getSharedPreferences("FantaMasterAI", Context.MODE_PRIVATE)
        val savedServerUrl = prefs.getString("server_url", null)

        scope.launch {
            var urlToLoad = "file:///android_asset/Dashboard_Fanta_1000.html"

            if (!savedServerUrl.isNullOrBlank()) {
                val reachable = withContext(Dispatchers.IO) { isServerReachable(savedServerUrl) }
                if (reachable) {
                    urlToLoad = savedServerUrl
                }
            }

            webView.loadUrl(urlToLoad)
        }
    }

    fun loadLocalAsset() {
        webView.loadUrl("file:///android_asset/Dashboard_Fanta_1000.html")
        Toast.makeText(this, "Caricata versione offline locale", Toast.LENGTH_SHORT).show()
    }

    private fun isServerReachable(urlString: String): Boolean {
        return try {
            val endpoint = if (urlString.endsWith("/")) urlString + "api/info" else "$urlString/api/info"
            val url = URL(endpoint)
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 1200
            conn.readTimeout = 1200
            conn.requestMethod = "GET"
            val responseCode = conn.responseCode
            responseCode in 200..399
        } catch (e: Exception) {
            false
        }
    }

    inner class WebAppInterface(private val context: Context) {
        @JavascriptInterface
        fun getServerUrl(): String? {
            val prefs = context.getSharedPreferences("FantaMasterAI", Context.MODE_PRIVATE)
            return prefs.getString("server_url", null)
        }

        @JavascriptInterface
        fun setServerUrl(url: String) {
            val prefs = context.getSharedPreferences("FantaMasterAI", Context.MODE_PRIVATE)
            prefs.edit().putString("server_url", url).apply()
            scope.launch {
                val reachable = withContext(Dispatchers.IO) { isServerReachable(url) }
                if (reachable) {
                    webView.loadUrl(url)
                    Toast.makeText(context, "Connesso a $url", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(context, "Server non raggiungibile all'indirizzo $url", Toast.LENGTH_LONG).show()
                }
            }
        }

        @JavascriptInterface
        fun showToast(message: String) {
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}
