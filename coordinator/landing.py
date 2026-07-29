"""Page publique de Lenyay — la vitrine du 7 août.

Parti pris : un observatoire nocturne. L'essaim travaille la nuit, chaque
machine est un point de lumière. Encre profonde, vert-de-gris (la patine du
cuivre, couleur des instruments anciens), parchemin chaud. Filets fins,
petites capitales, chiffres tabulaires : un panneau d'instrument, pas une
plaquette commerciale — parce que le sujet, ici, c'est la mesure honnête.

Une seule page, aucun framework, aucune étape de construction. Les polices
sont hébergées avec le site (aucun appel à un CDN tiers : la page ne doit
rien envoyer nulle part, comme le worker).
"""

LANDING_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — un modèle d'IA entretenu par nos machines</title>
<meta name="description" content="Réseau de calcul coopératif : nos ordinateurs résolvent des problèmes vérifiables la nuit, et le modèle qui en sort appartient à tout le monde.">
<meta name="color-scheme" content="dark">
<style>
@font-face {
  font-family: "Fraunces"; font-style: normal; font-weight: 300 700;
  font-display: swap; src: url("/static/fonts/fraunces-latin.woff2") format("woff2");
}
@font-face {
  font-family: "Plex Mono"; font-style: normal; font-weight: 400;
  font-display: swap; src: url("/static/fonts/plexmono-latin.woff2") format("woff2");
}

:root{
  --ink:#070c0b; --ink-2:#0c1413; --ink-3:#111c1a;
  --line:#1e2e2b; --line-bright:#2b4340;
  --verd:#74bda7; --verd-deep:#3f7a6c; --verd-glow:rgba(116,189,167,.14);
  --parch:#ece7db; --muted:#8ba099; --copper:#c98a55;
  --serif:"Fraunces", "Iowan Old Style", Georgia, serif;
  --mono:"Plex Mono", ui-monospace, "SFMono-Regular", Consolas, monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--ink); color:var(--parch);
  font-family:var(--serif); font-size:17px; line-height:1.65;
  font-variation-settings:"SOFT" 20, "WONK" 1;
  -webkit-font-smoothing:antialiased;
}
/* Grain : une texture de papier photographique, presque invisible. */
body::after{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:99; opacity:.028;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");
}
.wrap{max-width:1080px; margin:0 auto; padding:0 clamp(1.1rem, 4vw, 2.5rem)}

/* --- Reveal au chargement ------------------------------------------- */
.rise{opacity:0; transform:translateY(14px); animation:rise .9s cubic-bezier(.2,.7,.3,1) forwards}
@keyframes rise{to{opacity:1; transform:none}}
@media (prefers-reduced-motion:reduce){
  .rise{animation:none; opacity:1; transform:none}
  html{scroll-behavior:auto}
}

/* --- En-tête --------------------------------------------------------- */
header{
  position:sticky; top:0; z-index:20; backdrop-filter:blur(8px);
  background:linear-gradient(180deg, rgba(7,12,11,.94), rgba(7,12,11,.72));
  border-bottom:1px solid var(--line);
}
header .wrap{display:flex; align-items:center; gap:1.2rem; padding-block:.85rem}
.brand{font-size:1.12rem; letter-spacing:.055em; font-weight:600;
       font-variation-settings:"SOFT" 0,"WONK" 1}
.brand .dot{color:var(--verd)}
header nav{margin-left:auto; display:flex; gap:1.4rem; font-family:var(--mono);
           font-size:.74rem; letter-spacing:.11em; text-transform:uppercase}
header nav a{color:var(--muted); text-decoration:none; transition:color .25s}
header nav a:hover{color:var(--verd)}
@media (max-width:620px){ header nav a.opt{display:none} }

/* --- Héros ----------------------------------------------------------- */
.hero{position:relative; padding:clamp(4rem,11vw,8.5rem) 0 clamp(3rem,7vw,5rem); overflow:hidden}
#sky{position:absolute; inset:0; width:100%; height:100%; z-index:0; opacity:.5}
.hero .wrap{position:relative; z-index:1}
.eyebrow{font-family:var(--mono); font-size:.75rem; letter-spacing:.2em;
         text-transform:uppercase; color:var(--verd); margin:0 0 1.6rem}
.eyebrow::before{content:""; display:inline-block; width:2.2rem; height:1px;
  background:var(--verd-deep); vertical-align:middle; margin-right:.8rem}
h1{
  font-size:clamp(2.7rem, 7.4vw, 5.3rem); line-height:1.02; margin:0 0 1.5rem;
  font-weight:400; letter-spacing:-.022em; max-width:16ch;
  font-variation-settings:"SOFT" 0,"WONK" 1,"opsz" 120;
}
h1 em{font-style:italic; color:var(--verd)}
.lede{font-size:clamp(1.05rem,2vw,1.28rem); color:#c9d3ce; max-width:56ch; margin:0 0 2.6rem}
.cta{display:flex; gap:.9rem; flex-wrap:wrap; align-items:center}
.btn{
  display:inline-flex; align-items:center; gap:.6rem; padding:.8rem 1.5rem;
  border-radius:2px; font-family:var(--mono); font-size:.82rem; letter-spacing:.06em;
  text-decoration:none; border:1px solid var(--verd-deep); color:var(--ink);
  background:var(--verd); transition:transform .2s, box-shadow .25s, background .25s;
}
.btn:hover{transform:translateY(-2px); box-shadow:0 10px 30px -12px var(--verd)}
.btn.ghost{background:transparent; color:var(--parch); border-color:var(--line-bright)}
.btn.ghost:hover{border-color:var(--verd); color:var(--verd); box-shadow:none}

/* --- Bandeau de mesures --------------------------------------------- */
.readout{
  margin-top:clamp(3rem,7vw,4.5rem); border:1px solid var(--line);
  background:linear-gradient(180deg, var(--ink-2), rgba(12,20,19,.35));
  display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr));
}
.readout div{padding:1.35rem 1.5rem; border-right:1px solid var(--line)}
.readout div:last-child{border-right:none}
.readout b{
  display:block; font-family:var(--mono); font-size:1.75rem; font-weight:400;
  color:var(--verd); font-variant-numeric:tabular-nums; line-height:1.15;
}
.readout span{font-family:var(--mono); font-size:.68rem; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted)}
.pulse{display:inline-block; width:.4rem; height:.4rem; border-radius:50%;
  background:var(--verd); margin-right:.45rem; vertical-align:middle;
  animation:beat 2.6s ease-in-out infinite}
@keyframes beat{0%,100%{opacity:1}50%{opacity:.25}}
@media (max-width:640px){ .readout div{border-right:none; border-bottom:1px solid var(--line)} }

/* --- Sections -------------------------------------------------------- */
section{padding:clamp(3.5rem,8vw,6.5rem) 0; border-top:1px solid var(--line)}
.num{font-family:var(--mono); font-size:.72rem; letter-spacing:.2em; color:var(--verd-deep);
     text-transform:uppercase; margin:0 0 .9rem}
h2{font-size:clamp(1.7rem,3.6vw,2.5rem); line-height:1.15; font-weight:400;
   margin:0 0 1.1rem; letter-spacing:-.015em; max-width:22ch;
   font-variation-settings:"SOFT" 0,"WONK" 1}
.intro{color:#bdc9c4; max-width:62ch; margin:0 0 2.8rem}

.steps{display:grid; gap:1px; background:var(--line); border:1px solid var(--line);
       grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.steps article{background:var(--ink); padding:1.7rem 1.6rem}
.steps h3{font-size:1.06rem; font-weight:600; margin:.7rem 0 .55rem;
          font-variation-settings:"SOFT" 0,"WONK" 1}
.steps p{margin:0; color:var(--muted); font-size:.96rem}
.steps .k{font-family:var(--mono); font-size:.72rem; color:var(--verd); letter-spacing:.14em}

/* --- La preuve ------------------------------------------------------- */
.proof{display:grid; grid-template-columns:1fr 1fr; gap:1px; background:var(--line);
       border:1px solid var(--line); margin-bottom:1.6rem}
.proof div{background:var(--ink-2); padding:1.8rem}
.proof .label{font-family:var(--mono); font-size:.7rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin-bottom:.5rem}
.proof .val{font-family:var(--mono); font-size:2.6rem; color:var(--parch);
  font-variant-numeric:tabular-nums; line-height:1}
.proof .val small{font-size:.9rem; color:var(--muted); margin-left:.5rem}
.proof div.now .val{color:var(--verd)}
@media (max-width:560px){ .proof{grid-template-columns:1fr} }
.note{border-left:2px solid var(--copper); padding:.2rem 0 .2rem 1.2rem;
      color:#c9d3ce; max-width:64ch}
.note strong{color:var(--parch); font-weight:600}

/* --- Rejoindre ------------------------------------------------------- */
.tabs{display:flex; gap:.4rem; margin-bottom:.9rem}
.tab{font-family:var(--mono); font-size:.74rem; letter-spacing:.1em; padding:.5rem 1rem;
  background:transparent; color:var(--muted); border:1px solid var(--line);
  border-radius:2px; cursor:pointer; transition:.2s}
.tab[aria-selected="true"]{color:var(--verd); border-color:var(--verd-deep);
  background:var(--verd-glow)}
.cmd{display:flex; align-items:stretch; border:1px solid var(--line-bright);
     background:var(--ink-2); border-radius:2px; overflow:hidden}
.cmd code{font-family:var(--mono); font-size:.86rem; padding:1.05rem 1.2rem; flex:1;
  overflow-x:auto; white-space:nowrap; color:var(--parch)}
.cmd code::before{content:"$ "; color:var(--verd-deep)}
.cmd button{font-family:var(--mono); font-size:.72rem; letter-spacing:.1em; padding:0 1.3rem;
  background:var(--ink-3); color:var(--muted); border:none; border-left:1px solid var(--line);
  cursor:pointer; transition:.2s; text-transform:uppercase}
.cmd button:hover{color:var(--verd)}
.after{color:var(--muted); font-size:.95rem; margin-top:1rem}

/* --- Garanties ------------------------------------------------------- */
.nots{list-style:none; padding:0; margin:0; display:grid; gap:.15rem;
      grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.nots li{padding:.7rem 0 .7rem 1.9rem; position:relative; color:#c4cfca; font-size:.98rem}
.nots li::before{content:"—"; position:absolute; left:0; color:var(--verd-deep);
                 font-family:var(--mono)}

footer{border-top:1px solid var(--line); padding:2.6rem 0 3.4rem; color:var(--muted);
       font-family:var(--mono); font-size:.76rem; letter-spacing:.05em}
footer .wrap{display:flex; gap:1.4rem; flex-wrap:wrap; align-items:center}
footer a{color:var(--muted); text-decoration:none; border-bottom:1px solid var(--line-bright)}
footer a:hover{color:var(--verd)}
footer .right{margin-left:auto}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <span class="brand">Lenyay<span class="dot">.</span></span>
    <nav>
      <a href="#principe">Le principe</a>
      <a href="#preuve" class="opt">La preuve</a>
      <a href="#rejoindre">Rejoindre</a>
      <a href="/dashboard">Tableau de bord</a>
    </nav>
  </div>
</header>

<div class="hero">
  <canvas id="sky" aria-hidden="true"></canvas>
  <div class="wrap">
    <p class="eyebrow rise" style="animation-delay:.05s">Réseau de calcul coopératif</p>
    <h1 class="rise" style="animation-delay:.15s">Nos machines entretiennent un modèle <em>commun</em>.</h1>
    <p class="lede rise" style="animation-delay:.28s">
      La nuit, pendant que ton ordinateur ne sert à rien, il résout des problèmes de
      mathématiques. Chaque solution est vérifiée, archivée, et sert à améliorer un
      modèle d'IA qui n'appartient à personne — donc à tout le monde.
    </p>
    <div class="cta rise" style="animation-delay:.4s">
      <a class="btn" href="#rejoindre">Rejoindre l'essaim</a>
      <a class="btn ghost" href="/dashboard">Voir l'essaim en direct</a>
    </div>

    <div class="readout rise" style="animation-delay:.55s">
      <div><b id="s-rollouts">—</b><span>rollouts vérifiés</span></div>
      <div><b id="s-devices">—</b><span><i class="pulse"></i>appareils</span></div>
      <div><b id="s-rate">—</b><span>taux d'acceptation</span></div>
      <div><b id="s-tasks">—</b><span>problèmes au catalogue</span></div>
    </div>
  </div>
</div>

<section id="principe">
  <div class="wrap">
    <p class="num">01 — Le principe</p>
    <h2>Un travail que l'on peut vérifier.</h2>
    <p class="intro">
      Tout repose sur une idée simple : nous ne distribuons que des problèmes dont la
      réponse est vérifiable. Impossible de tricher, impossible de se tromper sur ce
      qui a réellement été produit.
    </p>
    <div class="steps">
      <article>
        <span class="k">01</span>
        <h3>Ta machine reçoit un problème</h3>
        <p>Un énoncé de mathématiques, et rien d'autre. Jamais la réponse — elle reste
        au serveur. Ta machine ne peut être créditée qu'en résolvant vraiment.</p>
      </article>
      <article>
        <span class="k">02</span>
        <h3>Un petit modèle raisonne</h3>
        <p>Il tourne chez toi, hors ligne, sur ton processeur. Il écrit son raisonnement
        pas à pas et propose un résultat.</p>
      </article>
      <article>
        <span class="k">03</span>
        <h3>Le raisonnement est archivé</h3>
        <p>Si la réponse est juste, la trace rejoint un corpus ouvert. C'est avec lui
        que l'on entraîne la version suivante du modèle.</p>
      </article>
    </div>
  </div>
</section>

<section id="preuve">
  <div class="wrap">
    <p class="num">02 — La preuve</p>
    <h2>Ce que ça donne, sans arrondir.</h2>
    <p class="intro">
      Un jeu de 200 problèmes est mis de côté et n'est jamais distribué à l'essaim.
      Chaque version du modèle y est évaluée dans des conditions identiques.
      Voici les chiffres — y compris quand ils ne nous arrangent pas.
    </p>
    <div class="proof">
      <div>
        <p class="label">v0.1 — modèle d'origine</p>
        <p class="val">71,5 %<small>143 / 200</small></p>
      </div>
      <div class="now">
        <p class="label">v0.2 — après notre premier entraînement</p>
        <p class="val">71,0 %<small>142 / 200</small></p>
      </div>
    </div>
    <p class="note">
      <strong>Le premier essai n'a rien amélioré</strong> — et c'est instructif. Nous avions
      entraîné le modèle sur les problèmes qu'il savait déjà résoudre : il a réappris ce
      qu'il connaissait. L'essaim chasse désormais les problèmes qu'il <em>rate</em>, car ce
      sont les solutions durement gagnées qui apprennent quelque chose. Le prochain
      chiffre publié ici sera obtenu de la même manière, quel qu'il soit.
    </p>
  </div>
</section>

<section id="rejoindre">
  <div class="wrap">
    <p class="num">03 — Rejoindre</p>
    <h2>Une commande, puis tu oublies.</h2>
    <p class="intro">
      L'installation prend deux à cinq minutes. Rien ne s'installe hors de son dossier,
      aucun droit administrateur n'est demandé, et tu arrêtes quand tu veux.
    </p>
    <div class="tabs" role="tablist">
      <button class="tab" role="tab" aria-selected="true" data-os="win">Windows</button>
      <button class="tab" role="tab" aria-selected="false" data-os="nix">Linux / macOS</button>
    </div>
    <div class="cmd">
      <code id="cmd-text">irm https://lenyay.org/install.ps1 | iex</code>
      <button id="copy" type="button">Copier</button>
    </div>
    <p class="after">
      Un raccourci apparaît sur ton bureau. Au premier lancement, le modèle se télécharge
      une fois (environ 1,1 Go), puis ta machine se met au travail.
      <a href="https://github.com/k1tz03/lenyay/blob/main/REJOINDRE.md" style="color:var(--verd)">Guide complet et questions fréquentes</a>.
    </p>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="num">04 — Garanties</p>
    <h2>Ce que Lenyay ne fait pas.</h2>
    <ul class="nots">
      <li>Aucune cryptomonnaie, aucun minage.</li>
      <li>Aucune donnée personnelle envoyée : ton appareil est un numéro.</li>
      <li>Aucun démarrage automatique : tu lances, tu arrêtes.</li>
      <li>Aucune publicité, aucun traceur sur cette page.</li>
      <li>Les crédits comptent ta contribution ; ils ne s'échangent pas et ne valent pas d'argent.</li>
      <li>Le code est ouvert et lisible, de bout en bout.</li>
    </ul>
  </div>
</section>

<footer>
  <div class="wrap">
    <span>Lenyay — bien commun</span>
    <a href="https://github.com/k1tz03/lenyay">Code source</a>
    <a href="/dashboard">Tableau de bord</a>
    <span class="right">Prononcer « leny-ay »</span>
  </div>
</footer>

<script>
// --- Mesures en direct ---------------------------------------------------
const fmt = n => n.toLocaleString("fr-FR");
async function readStats(){
  try{
    const r = await fetch("/stats", {cache:"no-store"});
    if(!r.ok) return;
    const s = await r.json();
    countTo("s-rollouts", s.accepted_rollouts);
    countTo("s-devices", s.devices_seen);
    countTo("s-tasks", s.tasks_in_catalog);
    document.getElementById("s-rate").textContent =
      (100 * s.acceptance_rate).toFixed(1).replace(".", ",") + " %";
  }catch(e){ /* la page reste lisible sans les chiffres */ }
}
// Petit compteur qui monte. La valeur est posée AVANT l'animation : dans un
// onglet en arrière-plan, requestAnimationFrame ne se déclenche jamais et le
// chiffre resterait sinon indéfiniment vide.
function countTo(id, value){
  const el = document.getElementById(id);
  el.textContent = fmt(value);
  if(matchMedia("(prefers-reduced-motion: reduce)").matches || document.hidden) return;
  const start = performance.now(), dur = 1100;
  const step = now => {
    const t = Math.min(1, (now - start) / dur);
    el.textContent = fmt(Math.round(value * (1 - Math.pow(1 - t, 3))));
    if(t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
readStats();
setInterval(readStats, 15000);

// --- Commande d'installation --------------------------------------------
const COMMANDS = {
  win: "irm https://lenyay.org/install.ps1 | iex",
  nix: "curl -fsSL https://lenyay.org/install.sh | bash",
};
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.setAttribute("aria-selected", "false"));
    tab.setAttribute("aria-selected", "true");
    document.getElementById("cmd-text").textContent = COMMANDS[tab.dataset.os];
  });
});
document.getElementById("copy").addEventListener("click", async e => {
  try{
    await navigator.clipboard.writeText(document.getElementById("cmd-text").textContent);
    e.target.textContent = "Copié";
    setTimeout(() => { e.target.textContent = "Copier"; }, 1800);
  }catch(err){ e.target.textContent = "Ctrl+C"; }
});

// --- La constellation ----------------------------------------------------
// Chaque point est une machine ; elles dérivent lentement et se relient
// quand elles se rapprochent. C'est l'essaim, littéralement.
(function sky(){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const canvas = document.getElementById("sky");
  const ctx = canvas.getContext("2d");
  let pts = [], w = 0, h = 0, raf = null;

  function resize(){
    const dpr = Math.min(devicePixelRatio || 1, 2);
    w = canvas.offsetWidth; h = canvas.offsetHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(48, Math.round(w * h / 26000));
    pts = Array.from({length:n}, () => ({
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - .5) * .13, vy: (Math.random() - .5) * .13,
      r: Math.random() * 1.1 + .5,
    }));
  }
  function frame(){
    ctx.clearRect(0, 0, w, h);
    for(const p of pts){
      p.x += p.vx; p.y += p.vy;
      if(p.x < 0 || p.x > w) p.vx *= -1;
      if(p.y < 0 || p.y > h) p.vy *= -1;
    }
    for(let i = 0; i < pts.length; i++){
      for(let j = i + 1; j < pts.length; j++){
        const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
        const d2 = dx*dx + dy*dy;
        if(d2 < 20000){
          ctx.strokeStyle = "rgba(116,189,167," + (.16 * (1 - d2/20000)) + ")";
          ctx.beginPath(); ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y); ctx.stroke();
        }
      }
    }
    ctx.fillStyle = "rgba(140,205,185,.55)";
    for(const p of pts){
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.284); ctx.fill();
    }
    raf = requestAnimationFrame(frame);
  }
  addEventListener("resize", resize);
  document.addEventListener("visibilitychange", () => {
    if(document.hidden){ cancelAnimationFrame(raf); raf = null; }
    else if(!raf){ raf = requestAnimationFrame(frame); }
  });
  resize(); frame();
})();
</script>
</body>
</html>"""
