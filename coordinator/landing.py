"""Page publique de Lenyay — la vitrine du 7 août.

Le produit, c'est une IA gratuite qui ne tourne dans aucun datacenter. Le reste
— les problèmes de mathématiques, la vérification, les crédits — n'est que la
mécanique qui la rend possible. La page s'organise donc autour d'un troc :
ce que tu prêtes, ce que tu reçois.

Règle de la maison : on n'annonce que ce qui marche. Ce qui est en chantier est
écrit comme tel, séparément. C'est ce qui rendra crédible le jour où l'accès au
grand modèle sera là.

Une seule page, aucun framework, aucune étape de construction. La police est
hébergée avec le site (aucun appel à un CDN tiers).
"""

LANDING_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — une IA gratuite, sans datacenter</title>
<meta name="description" content="Une IA qui tourne sur nos machines, pas dans un datacenter. Prête ton ordinateur quand tu ne t'en sers pas, utilise l'IA quand tu veux.">
<meta name="color-scheme" content="light">
<style>
@font-face{
  font-family:"Familjen"; font-style:normal; font-weight:400 700; font-display:swap;
  src:url("/static/fonts/familjen-latin.woff2") format("woff2");
}
:root{
  --paper:#F7F4EE; --paper-2:#EFEBE2;
  --ink:#2C3A31; --ink-soft:#71806F; --rule:#DAD4C7;
  --grow:#3C7F58; --amber:#C97F1E; --amber-soft:#F0E2C6;
  --ui:"Familjen", "Avenir Next", system-ui, sans-serif;
  --mono:ui-monospace, SFMono-Regular, "Cascadia Mono", Consolas, monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0; background:var(--paper); color:var(--ink); font-family:var(--ui);
  font-size:17.5px; line-height:1.6; -webkit-font-smoothing:antialiased}
@media (prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }
.wrap{max-width:960px; margin:0 auto; padding:0 clamp(1.2rem,4vw,2rem)}
a{color:inherit}

.top{display:flex; align-items:baseline; gap:.9rem; padding:1.1rem 0;
     font-size:.86rem; color:var(--ink-soft)}
.top b{font-size:1.05rem; color:var(--ink); font-weight:700; letter-spacing:-.01em}
.top nav{margin-left:auto; display:flex; gap:1.2rem}
.top nav a{text-decoration:none; color:var(--ink-soft)}
.top nav a:hover{color:var(--ink); text-decoration:underline; text-underline-offset:4px}
@media (max-width:640px){ .top .opt{display:none} }

/* ---- La promesse ---------------------------------------------------- */
.hero{padding:clamp(2rem,6vw,4rem) 0 clamp(2.5rem,6vw,3.5rem)}
h1{font-size:clamp(2.1rem,5.6vw,3.6rem); line-height:1.08; font-weight:700;
   letter-spacing:-.032em; margin:0 0 1.1rem; max-width:17ch}
h1 mark{background:linear-gradient(180deg,transparent 62%, var(--amber-soft) 62%);
  color:inherit; padding:0 .06em}
.lede{font-size:clamp(1.08rem,2.1vw,1.28rem); max-width:56ch; margin:0; color:#41504a}

/* ---- Le troc --------------------------------------------------------- */
.deal{display:grid; grid-template-columns:1fr auto 1fr; gap:clamp(1rem,3vw,2rem);
  align-items:stretch; margin:clamp(2rem,5vw,3rem) 0 0}
.side{border:1px solid var(--rule); border-radius:4px; padding:1.5rem 1.6rem;
  background:var(--paper-2)}
.side.get{background:var(--paper); border-color:var(--ink); border-width:2px}
.side .role{font-size:.78rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink-soft); margin:0 0 .8rem}
.side h2{font-size:1.32rem; font-weight:700; letter-spacing:-.02em; margin:0 0 .7rem}
.side ul{margin:0; padding:0; list-style:none; display:grid; gap:.55rem;
  color:#41504a; font-size:1rem}
.side li{display:flex; gap:.6rem}
.side li::before{content:"·"; color:var(--grow); font-weight:700}
.swap{display:grid; place-items:center; color:var(--ink-soft)}
.swap svg{width:34px; height:34px}
@media (max-width:760px){
  .deal{grid-template-columns:1fr}
  .swap{transform:rotate(90deg); padding:.2rem 0}
}

/* ---- État réel -------------------------------------------------------- */
section{padding:clamp(3rem,7vw,4.6rem) 0; border-top:1px solid var(--rule)}
.tag{font-size:.78rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink-soft); margin:0 0 .9rem}
h3{font-size:clamp(1.4rem,3.2vw,1.9rem); line-height:1.2; font-weight:700;
  letter-spacing:-.02em; margin:0 0 .7rem; max-width:24ch}
.note{color:var(--ink-soft); max-width:62ch; margin:0}
.note + .note{margin-top:.9rem}

.state{display:grid; gap:1.5rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  margin-top:1.9rem}
.state h4{margin:0 0 .7rem; font-size:1.02rem; display:flex; align-items:center; gap:.55rem}
.state .pill{font-size:.7rem; letter-spacing:.09em; text-transform:uppercase;
  padding:.12rem .5rem; border-radius:2px; font-weight:600}
.state .yes .pill{background:var(--grow); color:#fff}
.state .soon .pill{background:var(--amber-soft); color:var(--amber);
  border:1px solid var(--amber)}
.state ul{margin:0; padding:0; list-style:none; display:grid; gap:.5rem;
  color:#41504a; font-size:1rem}
.state li{display:flex; gap:.6rem}
.state .yes li::before{content:"✓"; color:var(--grow); font-weight:700}
.state .soon li::before{content:"→"; color:var(--amber)}

/* ---- Mécanique (volontairement discrète) ------------------------------ */
.why{background:var(--paper-2); border-left:3px solid var(--rule);
  padding:1.2rem 1.4rem; border-radius:0 4px 4px 0; max-width:68ch; margin-top:1.6rem}
.why p{margin:0; color:#41504a}
.why p + p{margin-top:.7rem}
.why a{text-decoration-color:var(--amber); text-underline-offset:3px}

/* ---- Participer ------------------------------------------------------- */
.os{display:flex; gap:1.2rem; margin:1.7rem 0 .7rem; font-size:.92rem}
.os button{background:none; border:none; padding:0 0 3px; cursor:pointer;
  color:var(--ink-soft); font:inherit; border-bottom:2px solid transparent}
.os button[aria-selected="true"]{color:var(--ink); border-color:var(--amber); font-weight:600}
.cmd{display:flex; border:1px solid var(--rule); border-radius:3px; background:var(--paper-2);
  overflow:hidden; max-width:680px}
.cmd code{font-family:var(--mono); font-size:.88rem; padding:.9rem 1rem; flex:1;
  overflow-x:auto; white-space:nowrap}
.cmd button{font:inherit; font-size:.85rem; font-weight:600; padding:0 1.1rem;
  cursor:pointer; background:var(--ink); color:var(--paper); border:none}
.cmd button:hover{background:var(--grow)}
.then{margin:1.5rem 0 0; padding:1.1rem 1.3rem; border:1px dashed var(--rule);
  border-radius:4px; max-width:680px; background:var(--paper)}
.then p{margin:0 0 .6rem; font-weight:600}
.then code{font-family:var(--mono); font-size:.86rem; background:var(--paper-2);
  padding:.25rem .5rem; border-radius:3px; border:1px solid var(--rule)}
.then span{display:block; color:var(--ink-soft); font-size:.95rem; margin-top:.5rem}
.after{color:var(--ink-soft); font-size:.96rem; margin:1.1rem 0 0; max-width:62ch}
.after a{text-decoration-color:var(--amber); text-underline-offset:3px}

.pledge{margin:1.5rem 0 0; padding:0; list-style:none; display:grid; gap:.5rem; max-width:62ch}
.pledge li{display:flex; gap:.7rem}
.pledge li::before{content:"non"; flex:none; font-size:.7rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--amber); border:1px solid var(--amber);
  border-radius:2px; padding:0 .3rem; height:1.2rem; line-height:1.15rem; margin-top:.24rem}

.live{display:flex; gap:1.6rem; flex-wrap:wrap; margin-top:1.6rem; font-size:.95rem;
  color:var(--ink-soft)}
.live b{color:var(--ink); font-variant-numeric:tabular-nums; font-weight:700}

footer{border-top:1px solid var(--rule); padding:2rem 0 3rem; color:var(--ink-soft);
  font-size:.9rem}
footer .wrap{display:flex; gap:1.3rem; flex-wrap:wrap}
footer .right{margin-left:auto}
</style>
</head>
<body>

<div class="wrap">
  <div class="top">
    <b>Lenyay</b>
    <span class="opt">se prononce « leny-ay »</span>
    <nav>
      <a href="#etat">Où on en est</a>
      <a href="#mecanique" class="opt">Comment ça marche</a>
      <a href="/dashboard" class="opt">Le réseau</a>
      <a href="#participer">Participer</a>
    </nav>
  </div>

  <div class="hero">
    <h1>Une IA gratuite qui ne tourne dans <mark>aucun datacenter</mark>.</h1>
    <p class="lede">Elle tourne sur nos ordinateurs. Tu prêtes le tien quand tu ne t'en
      sers pas — la nuit, par exemple — et tu utilises l'IA quand ça t'arrange.
      Sans abonnement, sans compte, sans envoyer tes questions à qui que ce soit.</p>

    <div class="deal">
      <div class="side">
        <p class="role">Tu prêtes</p>
        <h2>Du temps de calcul inutilisé</h2>
        <ul>
          <li>Un cœur de processeur pendant que ta machine ne fait rien</li>
          <li>Tu lances et tu arrêtes quand tu veux, rien ne démarre tout seul</li>
          <li>Aucune donnée personnelle : ta machine reçoit des calculs publics</li>
        </ul>
      </div>
      <div class="swap" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 9h15l-3.5-3.5M20 15H5l3.5 3.5"/>
        </svg>
      </div>
      <div class="side get">
        <p class="role">Tu reçois</p>
        <h2>L'IA, gratuitement</h2>
        <ul>
          <li>Elle s'installe avec le reste et répond sur ta machine, hors ligne</li>
          <li>Des crédits qui s'accumulent à chaque calcul vérifié</li>
          <li>Un modèle qui s'améliore avec ce que le réseau produit</li>
        </ul>
      </div>
    </div>

    <p class="live">
      <span>Aujourd'hui&nbsp;: <b id="s-devices">—</b> machines</span>
      <span><b id="s-done">—</b> calculs vérifiés</span>
      <span><b id="s-rate">—</b> de réussite</span>
    </p>
  </div>
</div>

<section id="etat">
  <div class="wrap">
    <p class="tag">Où on en est vraiment</p>
    <h3>On n'annonce que ce qui marche.</h3>
    <p class="note">Lenyay se construit en public. Voici ce que tu obtiens en installant
      aujourd'hui, et ce sur quoi nous travaillons — pas de flou entre les deux.</p>

    <div class="state">
      <div class="yes">
        <h4><span class="pill">Disponible</span></h4>
        <ul>
          <li>L'IA répond sur ta machine, gratuitement, sans connexion</li>
          <li>Tes questions ne quittent jamais ton ordinateur</li>
          <li>Tes crédits sont comptés et visibles sur le tableau de bord</li>
          <li>Le réseau tourne, le modèle est réentraîné avec ce qu'il produit</li>
        </ul>
      </div>
      <div class="soon">
        <h4><span class="pill">En construction</span></h4>
        <ul>
          <li>Dépenser ses crédits pour interroger un modèle plus grand, servi par le réseau</li>
          <li>Participer depuis un téléphone Android</li>
          <li>Choisir d'autres travaux utiles que les mathématiques</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="mecanique">
  <div class="wrap">
    <p class="tag">La mécanique</p>
    <h3>Pourquoi ta machine fait des mathématiques.</h3>
    <div class="why">
      <p>Pour qu'un réseau d'inconnus produise quelque chose de fiable, il faut pouvoir
        <strong>vérifier</strong> chaque contribution. Les problèmes de mathématiques ont
        cette vertu : la réponse est juste ou fausse, sans discussion. Ta machine en reçoit
        un, écrit son raisonnement, et le serveur contrôle le résultat — la réponse
        attendue ne quitte jamais le serveur, donc personne ne peut tricher.</p>
      <p>Les raisonnements justes forment un corpus commun, avec lequel on entraîne la
        version suivante du modèle. Les mathématiques ne sont qu'un premier terrain : tout
        travail vérifiable fera l'affaire. C'est la vérification qui compte, pas le sujet.
        <a href="/dashboard">Voir le réseau en direct</a>.</p>
    </div>
  </div>
</section>

<section id="participer">
  <div class="wrap">
    <p class="tag">Participer</p>
    <h3>Une commande, cinq minutes.</h3>
    <p class="note">Rien ne s'installe hors de son dossier, aucun mot de passe n'est
      demandé, et désinstaller revient à supprimer un dossier.</p>

    <div class="os" role="tablist">
      <button role="tab" aria-selected="true" data-os="win">Windows</button>
      <button role="tab" aria-selected="false" data-os="nix">Linux / macOS</button>
    </div>
    <div class="cmd">
      <code id="cmd-text">irm https://lenyay.org/install.ps1 | iex</code>
      <button id="copy" type="button">Copier</button>
    </div>

    <div class="then">
      <p>Ensuite, pour parler à l'IA :</p>
      <code id="chat-cmd">lenyay --chat</code>
      <span>Elle répond sur ta machine, sans connexion. Pour contribuer, lance
        simplement Lenyay sans option — ou double-clique le raccourci.</span>
    </div>

    <p class="after">Au premier démarrage, le modèle se télécharge une fois (1,1 Go).
      <a href="https://github.com/k1tz03/lenyay/blob/main/REJOINDRE.md">Guide complet et questions fréquentes</a>.</p>

    <ul class="pledge">
      <li>de cryptomonnaie, ni de minage.</li>
      <li>de donnée personnelle : ta machine est un numéro.</li>
      <li>de démarrage automatique dans ton dos.</li>
      <li>de publicité, ni de traceur sur cette page.</li>
      <li>de crédits échangeables : ils comptent ta contribution, ils ne valent pas d'argent.</li>
    </ul>
  </div>
</section>

<footer>
  <div class="wrap">
    <span>Lenyay — un bien commun</span>
    <a href="https://github.com/k1tz03/lenyay">Le code, entièrement ouvert</a>
    <a href="/dashboard">Le réseau en direct</a>
    <span class="right">Construit en public</span>
  </div>
</footer>

<script>
const fmt = n => n.toLocaleString("fr-FR");
async function readStats(){
  try{
    const r = await fetch("/stats", {cache:"no-store"});
    if(!r.ok) return;
    const s = await r.json();
    document.getElementById("s-devices").textContent = fmt(s.devices_seen);
    document.getElementById("s-done").textContent = fmt(s.accepted_rollouts);
    document.getElementById("s-rate").textContent = (100 * s.acceptance_rate).toFixed(0) + " %";
  }catch(e){ /* la page reste lisible sans les chiffres */ }
}
readStats(); setInterval(readStats, 15000);

const COMMANDS = {
  win: "irm https://lenyay.org/install.ps1 | iex",
  nix: "curl -fsSL https://lenyay.org/install.sh | bash",
};
const CHAT = { win: "lenyay --chat", nix: "~/.lenyay/lenyay --chat" };
document.querySelectorAll(".os button").forEach(b => {
  b.addEventListener("click", () => {
    document.querySelectorAll(".os button").forEach(o => o.setAttribute("aria-selected","false"));
    b.setAttribute("aria-selected","true");
    document.getElementById("cmd-text").textContent = COMMANDS[b.dataset.os];
    document.getElementById("chat-cmd").textContent = CHAT[b.dataset.os];
  });
});
document.getElementById("copy").addEventListener("click", async e => {
  try{
    await navigator.clipboard.writeText(document.getElementById("cmd-text").textContent);
    e.target.textContent = "Copié";
    setTimeout(() => { e.target.textContent = "Copier"; }, 1800);
  }catch(err){ e.target.textContent = "Ctrl+C"; }
});
</script>
</body>
</html>"""
