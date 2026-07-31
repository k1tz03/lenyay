import java.util.Properties

plugins {
    id("com.android.application")
}

// llama.dir (local.properties) pointe les sources llama.cpp : présent, le
// moteur de contribution est compilé ; absent, l'APK léger se construit
// quand même — Llm.available() dira la vérité à l'exécution.
val localProps = Properties().apply {
    val f = rootProject.file("local.properties")
    if (f.exists()) f.inputStream().use { s -> load(s) }
}
val llamaDir: String? = localProps.getProperty("llama.dir")

android {
    namespace = "org.lenyay.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "org.lenyay.app"
        minSdk = 26          // Android 8.0 (2017) : large couverture
        targetSdk = 34
        versionCode = 1
        versionName = "0.9.0"
        // Le coordinateur : surchargeable au build par -PlenyayUrl=https://…
        resValue("string", "lenyay_url",
            (project.findProperty("lenyayUrl") as String?) ?: "https://lenyay.org")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Signature debug pour la distribution directe (hors Play Store) ;
            // une clé de release dédiée arrivera avec la soumission au Store.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    lint {
        // lintVital plante sur un chemin Windows et n'apporte rien à une
        // coquille sans dépendance : la revue de code se fait ailleurs.
        checkReleaseBuilds = false
        abortOnError = false
    }

    if (llamaDir != null) {
        ndkVersion = "26.3.11579264"
        defaultConfig {
            ndk { abiFilters.add("arm64-v8a") }   // les téléphones réels
            externalNativeBuild {
                cmake {
                    arguments("-DLLAMA_CPP_DIR=$llamaDir")
                }
            }
        }
        externalNativeBuild {
            cmake {
                path = file("src/main/cpp/CMakeLists.txt")
                version = "3.22.1"
            }
        }
    }
}
