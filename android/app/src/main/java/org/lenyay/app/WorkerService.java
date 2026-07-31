package org.lenyay.app;

// La contribution mobile : un service de premier plan qui résout des tâches
// du catalogue PENDANT LA CHARGE uniquement. Débranché = pause immédiate.
// C'est le contrat affiché à l'utilisateur : sa batterie n'est jamais mise
// à contribution, seule sa prise l'est.

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
import android.os.Build;
import android.os.IBinder;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class WorkerService extends Service {

    public static final String MODEL_URL =
        "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/"
        + "qwen2.5-1.5b-instruct-q4_k_m.gguf";
    // Le même prompt que le worker de bureau : mêmes conditions, même corpus.
    public static final String MATH_PROMPT =
        "You are a careful math tutor. Solve the problem step by step. "
        + "End with the final numeric result on its own line, "
        + "in the exact format: #### <number>";
    public static final String CODE_PROMPT =
        "You are a careful Python programmer. Write the requested function. "
        + "Reply with a single ```python code block containing the complete "
        + "solution, then one short sentence of explanation.";

    private static final String CHANNEL = "lenyay_worker";
    private static volatile String state = "arrêté";
    private static volatile int solved = 0;
    private static volatile int credits = 0;

    private Thread loop;
    private volatile boolean running;

    public static String statusJson() {
        return "{\"running\":" + (state != "arrêté") + ",\"detail\":\""
            + state + " · " + solved + " ✓ · " + credits + " cr.\"}";
    }

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (Build.VERSION.SDK_INT >= 26) {
            nm.createNotificationChannel(new NotificationChannel(
                CHANNEL, "Contribution Lenyay",
                NotificationManager.IMPORTANCE_LOW));
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        startForeground(1, note("Lenyay se prépare…"));
        if (loop == null || !loop.isAlive()) {
            running = true;
            loop = new Thread(this::run, "lenyay-worker");
            loop.start();
        }
        return START_NOT_STICKY; // jamais de redémarrage dans le dos de l'utilisateur
    }

    @Override
    public void onDestroy() {
        running = false;
        state = "arrêté";
        if (loop != null) loop.interrupt();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) { return null; }

    private Notification note(String text) {
        Notification.Builder b = Build.VERSION.SDK_INT >= 26
            ? new Notification.Builder(this, CHANNEL)
            : new Notification.Builder(this);
        return b.setContentTitle("Lenyay — contribution")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_notify_sync)
                .setOngoing(true).build();
    }

    private void update(String text) {
        state = text;
        getSystemService(NotificationManager.class).notify(1, note(text));
    }

    private boolean charging() {
        Intent i = registerReceiver(null,
            new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        int st = i == null ? -1 : i.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
        return st == BatteryManager.BATTERY_STATUS_CHARGING
            || st == BatteryManager.BATTERY_STATUS_FULL;
    }

    // ------------------------------------------------------------------ HTTP

    private String base() { return getString(R.string.lenyay_url); }

    private JSONObject http(String method, String path, JSONObject body,
                            String apiKey) throws Exception {
        HttpURLConnection c = (HttpURLConnection)
            new URL(base() + path).openConnection();
        c.setRequestMethod(method);
        c.setConnectTimeout(15000);
        c.setReadTimeout(60000);
        if (apiKey != null) c.setRequestProperty("X-API-Key", apiKey);
        if (body != null) {
            c.setRequestProperty("Content-Type", "application/json");
            c.setDoOutput(true);
            try (OutputStream os = c.getOutputStream()) {
                os.write(body.toString().getBytes(StandardCharsets.UTF_8));
            }
        }
        int code = c.getResponseCode();
        InputStream is = code < 400 ? c.getInputStream() : c.getErrorStream();
        StringBuilder sb = new StringBuilder();
        if (is != null) {
            try (BufferedReader r = new BufferedReader(
                     new InputStreamReader(is, StandardCharsets.UTF_8))) {
                String line;
                while ((line = r.readLine()) != null) sb.append(line);
            }
        }
        if (code >= 400) throw new Exception("HTTP " + code + " sur " + path);
        return new JSONObject(sb.toString());
    }

    /** L'identité de l'appareil, créée au premier passage, liée au compte. */
    private String apiKey() throws Exception {
        File f = new File(getFilesDir(), "device.json");
        if (f.exists()) {
            String txt = new String(java.nio.file.Files.readAllBytes(f.toPath()),
                                    StandardCharsets.UTF_8);
            return new JSONObject(txt).getString("api_key");
        }
        JSONObject req = new JSONObject()
            .put("device_name", "android-" + Build.MODEL)
            .put("tier", "rapide");
        String account = getSharedPreferences("lenyay", MODE_PRIVATE)
            .getString("account_key", null);
        if (account != null) req.put("account_key", account);
        JSONObject resp = http("POST", "/devices/register", req, null);
        java.nio.file.Files.write(f.toPath(),
            resp.toString().getBytes(StandardCharsets.UTF_8));
        return resp.getString("api_key");
    }

    /** Le modèle : téléchargé une fois (1,1 Go), en charge uniquement. */
    private File model() throws Exception {
        File dir = new File(getFilesDir(), "models");
        dir.mkdirs();
        File f = new File(dir, "qwen2.5-1.5b-instruct-q4_k_m.gguf");
        if (f.exists() && f.length() > 1_000_000_000L) return f;

        File tmp = new File(dir, f.getName() + ".part");
        long have = tmp.exists() ? tmp.length() : 0;
        HttpURLConnection c = (HttpURLConnection) new URL(MODEL_URL).openConnection();
        if (have > 0) c.setRequestProperty("Range", "bytes=" + have + "-");
        c.setConnectTimeout(15000);
        c.setReadTimeout(60000);
        try (InputStream in = c.getInputStream();
             FileOutputStream out = new FileOutputStream(tmp, have > 0)) {
            byte[] buf = new byte[1 << 16];
            long total = have;
            int n;
            long lastNote = 0;
            while (running && (n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
                total += n;
                if (total - lastNote > 50_000_000L) {   // toutes les ~50 Mo
                    update("Téléchargement du modèle : " + (total >> 20) + " Mo");
                    lastNote = total;
                    if (!charging()) throw new Exception("débranché pendant le téléchargement");
                }
            }
        }
        if (!running) throw new InterruptedException();
        tmp.renameTo(f);
        return f;
    }

    // ------------------------------------------------------------------ boucle

    private void run() {
        try {
            if (!Llm.available()) {
                update("moteur absent de cette version");
                return;
            }
            update("en attente de la charge…");
            while (running && !charging()) Thread.sleep(30_000);

            update("préparation du modèle…");
            File gguf = model();
            update("chargement du modèle…");
            if (Llm.load(gguf.getAbsolutePath()) != 0) {
                update("échec du chargement du modèle");
                return;
            }
            String key = apiKey();

            while (running) {
                if (!charging()) {              // le contrat : la prise, pas la batterie
                    update("en pause — branche le téléphone");
                    Thread.sleep(60_000);
                    continue;
                }
                JSONObject work = http("GET", "/work?n=1", null, key);
                JSONArray tasks = work.getJSONArray("tasks");
                if (tasks.length() == 0) {
                    update("catalogue épuisé — pause");
                    Thread.sleep(300_000);
                    continue;
                }
                JSONObject task = tasks.getJSONObject(0);
                String kind = task.optString("kind", "math");
                update("calcul en cours…");
                String trace = Llm.answer(
                    kind.equals("code") ? CODE_PROMPT : MATH_PROMPT,
                    task.getString("prompt"), 640);
                if (trace == null || trace.isEmpty()) continue;

                JSONObject result = new JSONObject()
                    .put("task_id", task.getString("task_id"))
                    .put("attempt", 1)
                    .put("lease", task.getString("lease"))
                    .put("trace", trace);
                JSONObject resp = http("POST", "/results",
                    new JSONObject().put("results", new JSONArray().put(result)), key);
                credits = resp.optInt("total_credits", credits);
                JSONArray verdicts = resp.optJSONArray("verdicts");
                if (verdicts != null && verdicts.length() > 0
                        && verdicts.getJSONObject(0).optBoolean("accepted")) {
                    solved++;
                }
                update(solved + " résolu(s) · " + credits + " crédits");
            }
        } catch (InterruptedException ignored) {
        } catch (Exception e) {
            update("erreur : " + e.getMessage());
        } finally {
            state = "arrêté";
            stopSelf();
        }
    }
}
