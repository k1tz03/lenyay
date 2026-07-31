"""Les traductions de l'application — six langues, un seul dictionnaire.

Le français est la langue de référence : chaque clé DOIT exister dans toutes
les langues (un test l'impose — une langue trouée n'atteint jamais la prod).
Le HTML garde le français en dur comme contenu par défaut ; le JS applique la
langue choisie au chargement (localStorage → langue du navigateur → anglais).

Volontairement sans bibliothèque : un dict, un pivot, un test.
"""

LANGS = ["fr", "en", "es", "de", "pt", "it"]

S = {
    # --- Lancement ---
    "banner.free": {
        "fr": "🎉 Lancement : tout est gratuit. Les abonnements viendront dans un second temps.",
        "en": "🎉 Launch: everything is free. Subscriptions will come later.",
        "es": "🎉 Lanzamiento: todo es gratis. Las suscripciones llegarán más adelante.",
        "de": "🎉 Start: alles ist kostenlos. Abos kommen später.",
        "pt": "🎉 Lançamento: tudo é grátis. As assinaturas chegarão mais tarde.",
        "it": "🎉 Lancio: tutto è gratuito. Gli abbonamenti arriveranno in seguito."},
    "banner.install": {
        "fr": "Sur Android : menu du navigateur → « Ajouter à l'écran d'accueil » pour installer Lenyay.",
        "en": "On Android: browser menu → \"Add to Home screen\" to install Lenyay.",
        "es": "En Android: menú del navegador → «Añadir a pantalla de inicio» para instalar Lenyay.",
        "de": "Auf Android: Browsermenü → „Zum Startbildschirm hinzufügen“, um Lenyay zu installieren.",
        "pt": "No Android: menu do navegador → «Adicionar ao ecrã principal» para instalar a Lenyay.",
        "it": "Su Android: menu del browser → «Aggiungi a schermata Home» per installare Lenyay."},

    # --- Barre et navigation ---
    "nav.discover": {
        "fr": "Découvrir", "en": "Discover", "es": "Descubrir",
        "de": "Entdecken", "pt": "Descobrir", "it": "Scopri"},
    "nav.how": {
        "fr": "Comment ça marche", "en": "How it works", "es": "Cómo funciona",
        "de": "So funktioniert es", "pt": "Como funciona", "it": "Come funziona"},
    "nav.join": {
        "fr": "Participer", "en": "Contribute", "es": "Participar",
        "de": "Mitmachen", "pt": "Participar", "it": "Partecipa"},
    "nav.network": {
        "fr": "Le réseau", "en": "The network", "es": "La red",
        "de": "Das Netzwerk", "pt": "A rede", "it": "La rete"},
    "nav.signin": {
        "fr": "Se connecter", "en": "Sign in", "es": "Iniciar sesión",
        "de": "Anmelden", "pt": "Entrar", "it": "Accedi"},
    "net.live": {
        "fr": "réseau", "en": "network", "es": "red", "de": "Netzwerk",
        "pt": "rede", "it": "rete"},
    "net.stats": {
        "fr": "{d} machines · {c} calculs", "en": "{d} machines · {c} solved",
        "es": "{d} máquinas · {c} cálculos", "de": "{d} Rechner · {c} gelöst",
        "pt": "{d} máquinas · {c} cálculos", "it": "{d} macchine · {c} calcoli"},
    "tier.offline": {
        "fr": "aucune machine en ligne pour ce modèle",
        "en": "no machine online for this model",
        "es": "ninguna máquina en línea para este modelo",
        "de": "kein Rechner für dieses Modell online",
        "pt": "nenhuma máquina online para este modelo",
        "it": "nessuna macchina online per questo modello"},

    # --- Colonne des fils ---
    "side.new": {
        "fr": "＋ Nouvelle conversation", "en": "＋ New chat",
        "es": "＋ Nueva conversación", "de": "＋ Neuer Chat",
        "pt": "＋ Nova conversa", "it": "＋ Nuova chat"},
    "side.empty": {
        "fr": "Aucune conversation.", "en": "No conversations yet.",
        "es": "Sin conversaciones.", "de": "Noch keine Chats.",
        "pt": "Nenhuma conversa.", "it": "Nessuna conversazione."},
    "side.credits": {
        "fr": "crédits", "en": "credits", "es": "créditos", "de": "Credits",
        "pt": "créditos", "it": "crediti"},
    "side.account": {
        "fr": "compte", "en": "account", "es": "cuenta", "de": "Konto",
        "pt": "conta", "it": "account"},
    "side.faq": {
        "fr": "FAQ & aide", "en": "FAQ & help", "es": "FAQ y ayuda",
        "de": "FAQ & Hilfe", "pt": "FAQ e ajuda", "it": "FAQ e aiuto"},
    "side.what": {
        "fr": "Qu'est-ce que Lenyay ?", "en": "What is Lenyay?",
        "es": "¿Qué es Lenyay?", "de": "Was ist Lenyay?",
        "pt": "O que é a Lenyay?", "it": "Che cos'è Lenyay?"},
    "side.livenet": {
        "fr": "Le réseau en direct", "en": "The network, live",
        "es": "La red en directo", "de": "Das Netzwerk, live",
        "pt": "A rede ao vivo", "it": "La rete in diretta"},
    "contrib.off": {
        "fr": "Contribuer : arrêté", "en": "Contribute: off",
        "es": "Contribuir: parado", "de": "Beitragen: aus",
        "pt": "Contribuir: parado", "it": "Contribuisci: fermo"},
    "contrib.on": {
        "fr": "Contribuer : actif", "en": "Contribute: on",
        "es": "Contribuir: activo", "de": "Beitragen: aktiv",
        "pt": "Contribuir: ativo", "it": "Contribuisci: attivo"},
    "contrib.idle": {
        "fr": "Ta machine peut gagner des crédits en travaillant pour le réseau.",
        "en": "Your machine can earn credits by working for the network.",
        "es": "Tu máquina puede ganar créditos trabajando para la red.",
        "de": "Dein Rechner kann Credits verdienen, indem er für das Netzwerk arbeitet.",
        "pt": "A tua máquina pode ganhar créditos trabalhando para a rede.",
        "it": "La tua macchina può guadagnare crediti lavorando per la rete."},
    "contrib.busy": {
        "fr": "Ta machine travaille pour le réseau.",
        "en": "Your machine is working for the network.",
        "es": "Tu máquina está trabajando para la red.",
        "de": "Dein Rechner arbeitet für das Netzwerk.",
        "pt": "A tua máquina está trabalhando para a rede.",
        "it": "La tua macchina sta lavorando per la rete."},

    # --- Accueil ---
    "hero.title": {
        "fr": "Pose ta question au réseau.", "en": "Ask the network.",
        "es": "Haz tu pregunta a la red.", "de": "Frag das Netzwerk.",
        "pt": "Faz a tua pergunta à rede.", "it": "Fai la tua domanda alla rete."},
    "hero.sub": {
        "fr": "Elle sera traitée par l'ordinateur d'un membre — pas par un datacenter.",
        "en": "A member's computer will answer it — not a datacenter.",
        "es": "La responderá el ordenador de un miembro — no un centro de datos.",
        "de": "Der Rechner eines Mitglieds beantwortet sie — kein Rechenzentrum.",
        "pt": "Será respondida pelo computador de um membro — não por um datacenter.",
        "it": "Risponderà il computer di un membro — non un datacenter."},
    "hero.learn": {
        "fr": "Comprendre comment ça marche →", "en": "See how it works →",
        "es": "Entender cómo funciona →", "de": "So funktioniert es →",
        "pt": "Perceber como funciona →", "it": "Capire come funziona →"},
    "hero.s1": {
        "fr": "Explique-moi la photosynthèse simplement",
        "en": "Explain photosynthesis simply",
        "es": "Explícame la fotosíntesis de forma sencilla",
        "de": "Erkläre mir die Photosynthese einfach",
        "pt": "Explica-me a fotossíntese de forma simples",
        "it": "Spiegami la fotosintesi in modo semplice"},
    "hero.s2": {
        "fr": "Écris un mot d'excuse à mon voisin",
        "en": "Write an apology note to my neighbor",
        "es": "Escribe una nota de disculpa a mi vecino",
        "de": "Schreibe eine Entschuldigung an meinen Nachbarn",
        "pt": "Escreve um pedido de desculpas ao meu vizinho",
        "it": "Scrivi un biglietto di scuse al mio vicino"},
    "hero.s3": {
        "fr": "Combien font 17 % de 340 ?", "en": "What is 17% of 340?",
        "es": "¿Cuánto es el 17 % de 340?", "de": "Wie viel sind 17 % von 340?",
        "pt": "Quanto é 17% de 340?", "it": "Quanto fa il 17% di 340?"},

    # --- Composer ---
    "composer.ph": {
        "fr": "Écris ton message…", "en": "Type your message…",
        "es": "Escribe tu mensaje…", "de": "Schreib deine Nachricht…",
        "pt": "Escreve a tua mensagem…", "it": "Scrivi il tuo messaggio…"},
    "composer.legal": {
        "fr": "Ta question est lue par la machine d'un autre membre — n'y mets rien de confidentiel.",
        "en": "Your question is read by another member's machine — don't include anything confidential.",
        "es": "Tu pregunta la lee la máquina de otro miembro — no incluyas nada confidencial.",
        "de": "Deine Frage wird vom Rechner eines anderen Mitglieds gelesen — nichts Vertrauliches eingeben.",
        "pt": "A tua pergunta é lida pela máquina de outro membro — não incluas nada confidencial.",
        "it": "La tua domanda è letta dalla macchina di un altro membro — non inserire nulla di riservato."},

    # --- Conversation ---
    "turn.you": {"fr": "toi", "en": "you", "es": "tú", "de": "du", "pt": "tu", "it": "tu"},
    "turn.by": {
        "fr": "Répondu par", "en": "Answered by", "es": "Respondido por",
        "de": "Beantwortet von", "pt": "Respondido por", "it": "Risposta di"},
    "turn.waiting": {
        "fr": "en attente d'une machine", "en": "waiting for a machine",
        "es": "esperando una máquina", "de": "warte auf einen Rechner",
        "pt": "à espera de uma máquina", "it": "in attesa di una macchina"},
    "turn.writing": {
        "fr": "{d} rédige", "en": "{d} is writing", "es": "{d} está escribiendo",
        "de": "{d} schreibt", "pt": "{d} está a escrever", "it": "{d} sta scrivendo"},
    "turn.machine": {
        "fr": "une machine", "en": "a machine", "es": "una máquina",
        "de": "ein Rechner", "pt": "uma máquina", "it": "una macchina"},
    "turn.none": {
        "fr": "Aucune machine disponible pour l'instant. Ta question reste en file.",
        "en": "No machine available right now. Your question stays in the queue.",
        "es": "Ninguna máquina disponible por ahora. Tu pregunta sigue en cola.",
        "de": "Gerade kein Rechner verfügbar. Deine Frage bleibt in der Warteschlange.",
        "pt": "Nenhuma máquina disponível agora. A tua pergunta fica na fila.",
        "it": "Nessuna macchina disponibile ora. La tua domanda resta in coda."},
    "turn.fail": {
        "fr": "Le réseau n'a pas pu prendre la question. Réessaie.",
        "en": "The network couldn't take your question. Try again.",
        "es": "La red no pudo aceptar la pregunta. Inténtalo de nuevo.",
        "de": "Das Netzwerk konnte die Frage nicht annehmen. Versuch es erneut.",
        "pt": "A rede não conseguiu aceitar a pergunta. Tenta novamente.",
        "it": "La rete non ha potuto accettare la domanda. Riprova."},
    "turn.regen": {
        "fr": "↻ Régénérer", "en": "↻ Regenerate", "es": "↻ Regenerar",
        "de": "↻ Neu erzeugen", "pt": "↻ Regenerar", "it": "↻ Rigenera"},
    "turn.regen.tip": {
        "fr": "Reposer la même question à une autre machine ({c} cr.)",
        "en": "Ask the same question to another machine ({c} cr.)",
        "es": "Hacer la misma pregunta a otra máquina ({c} cr.)",
        "de": "Dieselbe Frage einem anderen Rechner stellen ({c} Cr.)",
        "pt": "Fazer a mesma pergunta a outra máquina ({c} cr.)",
        "it": "Fare la stessa domanda a un'altra macchina ({c} cr.)"},
    "fb.thanks": {
        "fr": "Merci — ça aide à améliorer Lenyay.", "en": "Thanks — this helps improve Lenyay.",
        "es": "Gracias — esto ayuda a mejorar Lenyay.", "de": "Danke — das hilft, Lenyay zu verbessern.",
        "pt": "Obrigado — isto ajuda a melhorar a Lenyay.", "it": "Grazie — aiuta a migliorare Lenyay."},
    "fb.noted": {
        "fr": "Noté, merci.", "en": "Noted, thanks.", "es": "Anotado, gracias.",
        "de": "Notiert, danke.", "pt": "Anotado, obrigado.", "it": "Preso nota, grazie."},
    "copy": {"fr": "Copier", "en": "Copy", "es": "Copiar", "de": "Kopieren",
             "pt": "Copiar", "it": "Copia"},
    "copied": {"fr": "Copié", "en": "Copied", "es": "Copiado", "de": "Kopiert",
               "pt": "Copiado", "it": "Copiato"},

    # --- Connexion ---
    "auth.login": {
        "fr": "Se connecter", "en": "Sign in", "es": "Iniciar sesión",
        "de": "Anmelden", "pt": "Entrar", "it": "Accedi"},
    "auth.register": {
        "fr": "Créer un compte", "en": "Create account", "es": "Crear cuenta",
        "de": "Konto erstellen", "pt": "Criar conta", "it": "Crea account"},
    "auth.handle": {
        "fr": "Pseudo", "en": "Nickname", "es": "Apodo", "de": "Nutzername",
        "pt": "Alcunha", "it": "Nickname"},
    "auth.handle.ph": {
        "fr": "visible sur le tableau de bord", "en": "shown on the dashboard",
        "es": "visible en el panel", "de": "im Dashboard sichtbar",
        "pt": "visível no painel", "it": "visibile nella dashboard"},
    "auth.email": {"fr": "E-mail", "en": "Email", "es": "Correo", "de": "E-Mail",
                   "pt": "E-mail", "it": "Email"},
    "auth.pass": {
        "fr": "Mot de passe", "en": "Password", "es": "Contraseña",
        "de": "Passwort", "pt": "Palavra-passe", "it": "Password"},
    "auth.pass.ph": {
        "fr": "8 caractères minimum", "en": "at least 8 characters",
        "es": "mínimo 8 caracteres", "de": "mindestens 8 Zeichen",
        "pt": "mínimo 8 caracteres", "it": "almeno 8 caratteri"},
    "auth.consent": {
        "fr": "Aider à améliorer Lenyay : mes conversations que je note 👍 pourront servir à entraîner le modèle, après retrait de mes données personnelles. Révocable à tout moment.",
        "en": "Help improve Lenyay: conversations I rate 👍 may be used to train the model, after my personal data is removed. Revocable anytime.",
        "es": "Ayudar a mejorar Lenyay: las conversaciones que valore con 👍 podrán usarse para entrenar el modelo, tras eliminar mis datos personales. Revocable en cualquier momento.",
        "de": "Hilf, Lenyay zu verbessern: Chats, die ich mit 👍 bewerte, dürfen zum Training genutzt werden — nach Entfernung meiner persönlichen Daten. Jederzeit widerrufbar.",
        "pt": "Ajudar a melhorar a Lenyay: as conversas que eu avaliar com 👍 poderão treinar o modelo, após remoção dos meus dados pessoais. Revogável a qualquer momento.",
        "it": "Aiuta a migliorare Lenyay: le conversazioni che valuto 👍 potranno addestrare il modello, dopo la rimozione dei miei dati personali. Revocabile in ogni momento."},
    "auth.go.login": {
        "fr": "Se connecter", "en": "Sign in", "es": "Iniciar sesión",
        "de": "Anmelden", "pt": "Entrar", "it": "Accedi"},
    "auth.go.register": {
        "fr": "Créer mon compte — 20 crédits offerts",
        "en": "Create my account — 20 free credits",
        "es": "Crear mi cuenta — 20 créditos gratis",
        "de": "Konto erstellen — 20 Credits geschenkt",
        "pt": "Criar a minha conta — 20 créditos grátis",
        "it": "Crea il mio account — 20 crediti in omaggio"},
    "auth.note": {
        "fr": "Pas de carte bancaire, pas de newsletter. L'e-mail ne sert qu'à retrouver ton compte.",
        "en": "No credit card, no newsletter. Your email is only used to recover your account.",
        "es": "Sin tarjeta bancaria, sin boletines. El correo solo sirve para recuperar tu cuenta.",
        "de": "Keine Kreditkarte, kein Newsletter. Die E-Mail dient nur der Kontowiederherstellung.",
        "pt": "Sem cartão bancário, sem newsletter. O e-mail serve apenas para recuperar a conta.",
        "it": "Nessuna carta di credito, nessuna newsletter. L'email serve solo a recuperare l'account."},
    "auth.err.login": {
        "fr": "Connexion impossible.", "en": "Couldn't sign in.",
        "es": "No se pudo iniciar sesión.", "de": "Anmeldung fehlgeschlagen.",
        "pt": "Não foi possível entrar.", "it": "Accesso non riuscito."},
    "auth.err.register": {
        "fr": "Vérifie l'e-mail et le mot de passe (8 caractères min).",
        "en": "Check the email and password (8 characters min).",
        "es": "Comprueba el correo y la contraseña (mínimo 8 caracteres).",
        "de": "Prüfe E-Mail und Passwort (mind. 8 Zeichen).",
        "pt": "Verifica o e-mail e a palavra-passe (mínimo 8 caracteres).",
        "it": "Controlla email e password (minimo 8 caratteri)."},

    # --- Compte ---
    "acct.tab.devices": {
        "fr": "Machines", "en": "Machines", "es": "Máquinas", "de": "Rechner",
        "pt": "Máquinas", "it": "Macchine"},
    "acct.tab.earned": {
        "fr": "Crédits gagnés", "en": "Credits earned", "es": "Créditos ganados",
        "de": "Verdiente Credits", "pt": "Créditos ganhos", "it": "Crediti guadagnati"},
    "acct.tab.billing": {
        "fr": "Facturation", "en": "Billing", "es": "Facturación",
        "de": "Abrechnung", "pt": "Faturação", "it": "Fatturazione"},
    "acct.tab.key": {
        "fr": "Mes machines & clé", "en": "My machines & key",
        "es": "Mis máquinas y clave", "de": "Meine Rechner & Schlüssel",
        "pt": "As minhas máquinas e chave", "it": "Le mie macchine e chiave"},
    "acct.earned": {"fr": "gagnés", "en": "earned", "es": "ganados",
                    "de": "verdient", "pt": "ganhos", "it": "guadagnati"},
    "acct.spent": {"fr": "dépensés", "en": "spent", "es": "gastados",
                   "de": "ausgegeben", "pt": "gastos", "it": "spesi"},
    "acct.machines": {"fr": "machine(s)", "en": "machine(s)", "es": "máquina(s)",
                      "de": "Rechner", "pt": "máquina(s)", "it": "macchina/e"},
    "acct.empty": {
        "fr": "Rien pour l'instant.", "en": "Nothing yet.", "es": "Nada por ahora.",
        "de": "Noch nichts.", "pt": "Nada por enquanto.", "it": "Niente per ora."},
    "acct.nodevice": {
        "fr": "Aucune machine rattachée. Installe Lenyay et rattache-la : tes nuits deviennent des crédits.",
        "en": "No machine linked. Install Lenyay and link one: your nights become credits.",
        "es": "Ninguna máquina vinculada. Instala Lenyay y vincula una: tus noches se convierten en créditos.",
        "de": "Kein Rechner verknüpft. Installiere Lenyay und verknüpfe einen: deine Nächte werden zu Credits.",
        "pt": "Nenhuma máquina associada. Instala a Lenyay e associa uma: as tuas noites viram créditos.",
        "it": "Nessuna macchina collegata. Installa Lenyay e collegane una: le tue notti diventano crediti."},
    "acct.produced": {
        "fr": "crédits produits", "en": "credits produced", "es": "créditos producidos",
        "de": "Credits erzeugt", "pt": "créditos produzidos", "it": "crediti prodotti"},
    "acct.nobilling": {
        "fr": "Aucun paiement : Lenyay ne facture pas d'argent. L'abonnement arrivera pour ceux qui préfèrent ne pas contribuer.",
        "en": "No payments: Lenyay doesn't charge money. A subscription will come for those who prefer not to contribute.",
        "es": "Sin pagos: Lenyay no cobra dinero. Llegará una suscripción para quienes prefieran no contribuir.",
        "de": "Keine Zahlungen: Lenyay berechnet kein Geld. Ein Abo kommt für alle, die nicht beitragen möchten.",
        "pt": "Sem pagamentos: a Lenyay não cobra dinheiro. Haverá uma subscrição para quem preferir não contribuir.",
        "it": "Nessun pagamento: Lenyay non addebita denaro. Arriverà un abbonamento per chi preferisce non contribuire."},
    "acct.nospend": {
        "fr": "Aucune dépense pour l'instant.", "en": "No spending yet.",
        "es": "Sin gastos por ahora.", "de": "Noch keine Ausgaben.",
        "pt": "Sem despesas por enquanto.", "it": "Nessuna spesa per ora."},
    "acct.keyinfo": {
        "fr": "Cette clé rattache une machine à ton compte : lance le worker avec LENYAY_ACCOUNT_KEY et ses gains alimenteront ta bourse. Ce n'est pas un mot de passe — ton identité, c'est ton e-mail.",
        "en": "This key links a machine to your account: run the worker with LENYAY_ACCOUNT_KEY and its earnings feed your balance. It is not a password — your identity is your email.",
        "es": "Esta clave vincula una máquina a tu cuenta: lanza el worker con LENYAY_ACCOUNT_KEY y sus ganancias alimentarán tu saldo. No es una contraseña — tu identidad es tu correo.",
        "de": "Dieser Schlüssel verknüpft einen Rechner mit deinem Konto: starte den Worker mit LENYAY_ACCOUNT_KEY und seine Erträge fließen auf dein Guthaben. Er ist kein Passwort — deine Identität ist deine E-Mail.",
        "pt": "Esta chave associa uma máquina à tua conta: executa o worker com LENYAY_ACCOUNT_KEY e os ganhos alimentam o teu saldo. Não é uma palavra-passe — a tua identidade é o teu e-mail.",
        "it": "Questa chiave collega una macchina al tuo account: avvia il worker con LENYAY_ACCOUNT_KEY e i suoi guadagni alimentano il tuo saldo. Non è una password — la tua identità è la tua email."},
    "acct.optlearn": {
        "fr": "Aider à améliorer Lenyay. Mes conversations notées 👍 peuvent servir à entraîner le modèle, données personnelles retirées. Révocable ici à tout moment.",
        "en": "Help improve Lenyay. My 👍-rated conversations may train the model, personal data removed. Revocable here anytime.",
        "es": "Ayudar a mejorar Lenyay. Mis conversaciones con 👍 pueden entrenar el modelo, sin datos personales. Revocable aquí en cualquier momento.",
        "de": "Hilf, Lenyay zu verbessern. Meine 👍-Chats dürfen das Modell trainieren, ohne persönliche Daten. Hier jederzeit widerrufbar.",
        "pt": "Ajudar a melhorar a Lenyay. As minhas conversas com 👍 podem treinar o modelo, sem dados pessoais. Revogável aqui a qualquer momento.",
        "it": "Aiuta a migliorare Lenyay. Le mie conversazioni con 👍 possono addestrare il modello, senza dati personali. Revocabile qui in ogni momento."},
    "acct.close": {"fr": "Fermer", "en": "Close", "es": "Cerrar", "de": "Schließen",
                   "pt": "Fechar", "it": "Chiudi"},
    "acct.logout": {
        "fr": "Se déconnecter", "en": "Sign out", "es": "Cerrar sesión",
        "de": "Abmelden", "pt": "Sair", "it": "Esci"},
    "kind.daily": {
        "fr": "Recharge quotidienne", "en": "Daily top-up", "es": "Recarga diaria",
        "de": "Tägliche Aufladung", "pt": "Recarga diária", "it": "Ricarica giornaliera"},
    "kind.welcome": {
        "fr": "Bienvenue", "en": "Welcome", "es": "Bienvenida", "de": "Willkommen",
        "pt": "Boas-vindas", "it": "Benvenuto"},
    "kind.solved": {
        "fr": "Calculs", "en": "Solved tasks", "es": "Cálculos", "de": "Gelöste Aufgaben",
        "pt": "Cálculos", "it": "Calcoli"},
    "kind.served": {
        "fr": "Réponse servie", "en": "Answer served", "es": "Respuesta servida",
        "de": "Antwort geliefert", "pt": "Resposta servida", "it": "Risposta servita"},
    "kind.question": {
        "fr": "Question", "en": "Question", "es": "Pregunta", "de": "Frage",
        "pt": "Pergunta", "it": "Domanda"},
    "kind.adjust": {
        "fr": "Ajustement", "en": "Adjustment", "es": "Ajuste", "de": "Anpassung",
        "pt": "Ajuste", "it": "Rettifica"},

    # --- Mur de crédits ---
    "wall.title": {
        "fr": "Plus de crédits pour aujourd'hui", "en": "Out of credits for today",
        "es": "Sin créditos por hoy", "de": "Keine Credits mehr für heute",
        "pt": "Sem créditos por hoje", "it": "Crediti esauriti per oggi"},
    "wall.tomorrow": {
        "fr": "Demain — ton solde remonte automatiquement : de quoi quelques questions simples chaque jour.",
        "en": "Tomorrow — your balance refills automatically: enough for a few simple questions every day.",
        "es": "Mañana — tu saldo se recarga automáticamente: suficiente para algunas preguntas sencillas cada día.",
        "de": "Morgen — dein Guthaben füllt sich automatisch auf: genug für ein paar einfache Fragen pro Tag.",
        "pt": "Amanhã — o teu saldo recarrega automaticamente: dá para algumas perguntas simples por dia.",
        "it": "Domani — il tuo saldo si ricarica automaticamente: basta per qualche domanda semplice al giorno."},
    "wall.contribute": {
        "fr": "Contribuer — laisse Lenyay tourner : chaque calcul vérifié te recrédite, sans limite.",
        "en": "Contribute — let Lenyay run: every verified task credits you back, without limit.",
        "es": "Contribuir — deja Lenyay funcionando: cada cálculo verificado te recarga, sin límite.",
        "de": "Beitragen — lass Lenyay laufen: jede geprüfte Aufgabe bringt dir Credits, ohne Limit.",
        "pt": "Contribuir — deixa a Lenyay a correr: cada cálculo verificado recarrega-te, sem limite.",
        "it": "Contribuisci — lascia Lenyay in esecuzione: ogni calcolo verificato ti ricarica, senza limiti."},
    "wall.subscribe": {
        "fr": "S'abonner — bientôt, un petit abonnement pour utiliser sans contribuer.",
        "en": "Subscribe — soon, a small subscription to use without contributing.",
        "es": "Suscribirse — pronto, una pequeña suscripción para usar sin contribuir.",
        "de": "Abonnieren — bald ein kleines Abo, um ohne Beitrag zu nutzen.",
        "pt": "Assinar — em breve, uma pequena subscrição para usar sem contribuir.",
        "it": "Abbonati — presto, un piccolo abbonamento per usare senza contribuire."},
    "wall.cta": {
        "fr": "Voir comment contribuer", "en": "See how to contribute",
        "es": "Ver cómo contribuir", "de": "So kannst du beitragen",
        "pt": "Ver como contribuir", "it": "Scopri come contribuire"},

    # --- FAQ ---
    "faq.title": {"fr": "FAQ & aide", "en": "FAQ & help", "es": "FAQ y ayuda",
                  "de": "FAQ & Hilfe", "pt": "FAQ e ajuda", "it": "FAQ e aiuto"},
    "faq.q1": {
        "fr": "C'est quoi, Lenyay ?", "en": "What is Lenyay?", "es": "¿Qué es Lenyay?",
        "de": "Was ist Lenyay?", "pt": "O que é a Lenyay?", "it": "Che cos'è Lenyay?"},
    "faq.a1": {
        "fr": "Une IA sans datacenter : chaque réponse est produite par l'ordinateur d'un membre du réseau. Le jour tu poses tes questions, la nuit ta machine peut travailler pour les autres et te faire gagner des crédits.",
        "en": "An AI without datacenters: every answer is produced by a member's computer. By day you ask questions; by night your machine can work for others and earn you credits.",
        "es": "Una IA sin centros de datos: cada respuesta la produce el ordenador de un miembro. De día haces preguntas; de noche tu máquina puede trabajar para otros y ganarte créditos.",
        "de": "Eine KI ohne Rechenzentrum: Jede Antwort erzeugt der Rechner eines Mitglieds. Tagsüber stellst du Fragen, nachts kann dein Rechner für andere arbeiten und Credits verdienen.",
        "pt": "Uma IA sem datacenters: cada resposta é produzida pelo computador de um membro. De dia fazes perguntas; à noite a tua máquina pode trabalhar para os outros e ganhar créditos.",
        "it": "Un'IA senza datacenter: ogni risposta è prodotta dal computer di un membro. Di giorno fai domande; di notte la tua macchina può lavorare per gli altri e farti guadagnare crediti."},
    "faq.q2": {
        "fr": "Combien ça coûte ?", "en": "How much does it cost?", "es": "¿Cuánto cuesta?",
        "de": "Was kostet es?", "pt": "Quanto custa?", "it": "Quanto costa?"},
    "faq.a2": {
        "fr": "Rien. Tu reçois 20 crédits à l'inscription, et chaque jour ton solde remonte à 5 crédits minimum — de quoi poser quelques questions simples. Pour un usage intensif : laisse ta machine contribuer, chaque calcul vérifié te recrédite sans limite.",
        "en": "Nothing. You get 20 credits at sign-up, and every day your balance refills to at least 5 credits — enough for a few simple questions. For heavy use: let your machine contribute, every verified task credits you back without limit.",
        "es": "Nada. Recibes 20 créditos al registrarte, y cada día tu saldo sube a un mínimo de 5 créditos — suficiente para algunas preguntas sencillas. Para uso intensivo: deja que tu máquina contribuya, cada cálculo verificado te recarga sin límite.",
        "de": "Nichts. Du bekommst 20 Credits bei der Anmeldung, und täglich füllt sich dein Guthaben auf mindestens 5 Credits — genug für ein paar einfache Fragen. Für intensive Nutzung: Lass deinen Rechner beitragen, jede geprüfte Aufgabe bringt Credits ohne Limit.",
        "pt": "Nada. Recebes 20 créditos ao registares-te, e todos os dias o teu saldo sobe para pelo menos 5 créditos — dá para algumas perguntas simples. Para uso intensivo: deixa a tua máquina contribuir, cada cálculo verificado recarrega sem limite.",
        "it": "Niente. Ricevi 20 crediti all'iscrizione e ogni giorno il tuo saldo risale ad almeno 5 crediti — basta per qualche domanda semplice. Per un uso intensivo: lascia contribuire la tua macchina, ogni calcolo verificato ti ricarica senza limiti."},
    "faq.q3": {
        "fr": "C'est quoi, les crédits ?", "en": "What are credits?",
        "es": "¿Qué son los créditos?", "de": "Was sind Credits?",
        "pt": "O que são os créditos?", "it": "Cosa sono i crediti?"},
    "faq.a3": {
        "fr": "Le compteur du troc : une question en coûte quelques-uns (1 à 20 selon le modèle), un travail rendu par ta machine en rapporte davantage. Ils ne s'achètent pas et ne valent pas d'argent.",
        "en": "The barter meter: a question costs a few (1 to 20 depending on the model), work done by your machine earns more. They can't be bought and aren't worth money.",
        "es": "El contador del trueque: una pregunta cuesta unos pocos (de 1 a 20 según el modelo), el trabajo de tu máquina gana más. No se compran y no valen dinero.",
        "de": "Der Tauschzähler: Eine Frage kostet einige (1 bis 20 je nach Modell), Arbeit deines Rechners bringt mehr ein. Sie sind nicht käuflich und kein Geld wert.",
        "pt": "O contador da troca: uma pergunta custa alguns (1 a 20 conforme o modelo), o trabalho da tua máquina rende mais. Não se compram e não valem dinheiro.",
        "it": "Il contatore del baratto: una domanda ne costa alcuni (da 1 a 20 secondo il modello), il lavoro della tua macchina ne rende di più. Non si comprano e non valgono denaro."},
    "faq.q4": {
        "fr": "Comment contribuer ?", "en": "How do I contribute?",
        "es": "¿Cómo contribuyo?", "de": "Wie trage ich bei?",
        "pt": "Como contribuo?", "it": "Come contribuisco?"},
    "faq.a4": {
        "fr": "Active « Contribuer » dans l'application (ou lance le programme Lenyay sur ton ordinateur). Ta machine résout des problèmes vérifiables — maths, code — et sert les questions des autres membres. Tu arrêtes quand tu veux.",
        "en": "Turn on \"Contribute\" in the app (or run the Lenyay program on your computer). Your machine solves verifiable problems — math, code — and serves other members' questions. Stop whenever you want.",
        "es": "Activa «Contribuir» en la aplicación (o ejecuta el programa Lenyay en tu ordenador). Tu máquina resuelve problemas verificables — matemáticas, código — y atiende las preguntas de otros miembros. Paras cuando quieras.",
        "de": "Aktiviere »Beitragen« in der App (oder starte das Lenyay-Programm auf deinem Rechner). Dein Rechner löst prüfbare Aufgaben — Mathe, Code — und beantwortet Fragen anderer Mitglieder. Du hörst auf, wann du willst.",
        "pt": "Ativa «Contribuir» na aplicação (ou executa o programa Lenyay no teu computador). A tua máquina resolve problemas verificáveis — matemática, código — e serve as perguntas dos outros membros. Paras quando quiseres.",
        "it": "Attiva «Contribuisci» nell'app (o avvia il programma Lenyay sul tuo computer). La tua macchina risolve problemi verificabili — matematica, codice — e serve le domande degli altri membri. Ti fermi quando vuoi."},
    "faq.q5": {
        "fr": "Mes conversations sont-elles privées ?", "en": "Are my conversations private?",
        "es": "¿Mis conversaciones son privadas?", "de": "Sind meine Chats privat?",
        "pt": "As minhas conversas são privadas?", "it": "Le mie conversazioni sono private?"},
    "faq.a5": {
        "fr": "Ta question est lue par la machine du membre qui y répond — n'y mets rien de confidentiel. Rien ne sert à entraîner le modèle sans ton accord explicite ET un 👍 de ta part, après retrait des données personnelles (e-mails, numéros).",
        "en": "Your question is read by the machine of the member who answers it — don't include anything confidential. Nothing trains the model without your explicit consent AND a 👍 from you, after personal data (emails, numbers) is removed.",
        "es": "Tu pregunta la lee la máquina del miembro que responde — no incluyas nada confidencial. Nada entrena el modelo sin tu consentimiento explícito Y un 👍 tuyo, tras eliminar los datos personales (correos, números).",
        "de": "Deine Frage liest der Rechner des antwortenden Mitglieds — nichts Vertrauliches eingeben. Nichts trainiert das Modell ohne deine ausdrückliche Zustimmung UND ein 👍 von dir, nach Entfernung persönlicher Daten (E-Mails, Nummern).",
        "pt": "A tua pergunta é lida pela máquina do membro que responde — não incluas nada confidencial. Nada treina o modelo sem o teu consentimento explícito E um 👍 teu, após remoção dos dados pessoais (e-mails, números).",
        "it": "La tua domanda è letta dalla macchina del membro che risponde — non inserire nulla di riservato. Nulla addestra il modello senza il tuo consenso esplicito E un tuo 👍, dopo la rimozione dei dati personali (email, numeri)."},
    "faq.q6": {
        "fr": "Pourquoi la réponse met parfois du temps ?", "en": "Why are answers sometimes slow?",
        "es": "¿Por qué a veces tarda la respuesta?", "de": "Warum dauern Antworten manchmal?",
        "pt": "Porque é que a resposta às vezes demora?", "it": "Perché a volte la risposta è lenta?"},
    "faq.a6": {
        "fr": "Il faut qu'une machine du réseau soit disponible pour ton modèle. Les modèles sans machine en ligne sont grisés. Tu peux aussi régénérer une réponse qui ne convient pas — une autre machine s'en chargera.",
        "en": "A network machine must be available for your model. Models with no machine online are grayed out. You can also regenerate an unsatisfying answer — another machine will take it.",
        "es": "Debe haber una máquina de la red disponible para tu modelo. Los modelos sin máquina en línea aparecen en gris. También puedes regenerar una respuesta que no convenza — otra máquina se encargará.",
        "de": "Ein Rechner im Netzwerk muss für dein Modell verfügbar sein. Modelle ohne Rechner online sind ausgegraut. Du kannst eine Antwort auch neu erzeugen lassen — ein anderer Rechner übernimmt.",
        "pt": "É preciso que uma máquina da rede esteja disponível para o teu modelo. Modelos sem máquina online ficam a cinzento. Também podes regenerar uma resposta que não sirva — outra máquina trata disso.",
        "it": "Serve una macchina della rete disponibile per il tuo modello. I modelli senza macchina online sono in grigio. Puoi anche rigenerare una risposta che non convince — se ne occuperà un'altra macchina."},
    "faq.q7": {
        "fr": "Comment supprimer mon compte ou mes données ?", "en": "How do I delete my account or data?",
        "es": "¿Cómo borro mi cuenta o mis datos?", "de": "Wie lösche ich Konto oder Daten?",
        "pt": "Como apago a minha conta ou os meus dados?", "it": "Come elimino il mio account o i miei dati?"},
    "faq.a7": {
        "fr": "Supprime tes conversations une à une (elles disparaissent immédiatement), et écris-nous pour l'effacement complet du compte — c'est un droit, pas une faveur.",
        "en": "Delete your conversations one by one (they disappear immediately), and write to us for full account erasure — it's a right, not a favor.",
        "es": "Borra tus conversaciones una a una (desaparecen de inmediato), y escríbenos para el borrado completo de la cuenta — es un derecho, no un favor.",
        "de": "Lösche deine Chats einzeln (sie verschwinden sofort) und schreib uns für die vollständige Kontolöschung — das ist ein Recht, kein Gefallen.",
        "pt": "Apaga as tuas conversas uma a uma (desaparecem de imediato) e escreve-nos para o apagamento completo da conta — é um direito, não um favor.",
        "it": "Elimina le tue conversazioni una a una (spariscono subito) e scrivici per la cancellazione completa dell'account — è un diritto, non un favore."},
}


def bundle() -> dict:
    """Pivot {langue: {clé: texte}} pour l'injection dans la page."""
    return {lang: {key: variants[lang] for key, variants in S.items()}
            for lang in LANGS}


def missing() -> list[tuple[str, str]]:
    """Les trous (clé, langue) — doit être vide, un test l'impose."""
    return [(key, lang) for key, variants in S.items()
            for lang in LANGS if not variants.get(lang, "").strip()]
