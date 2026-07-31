plugins {
    id("com.android.application")
}

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
}
