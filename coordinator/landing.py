"""Page publique de Lenyay — le produit, utilisable sur place.

Le visiteur ne lit pas une promesse : il pose une question, et la machine d'un
autre membre y répond sous ses yeux, en quelques secondes. Le reste de la page
n'est là que pour expliquer ce qu'il vient de voir.

Palette : le vert-de-gris de Lenyay (patine du cuivre) sur un fond clair et
chaud — accueillant, mais pas fade : surfaces posées, ombres douces, matière.

Une seule page, aucun framework, aucune étape de construction. La police est
hébergée avec le site (aucun appel à un CDN tiers).
"""

LANDING_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — une IA gratuite, servie par nos machines</title>
<meta name="description" content="Pose ta question : elle sera traitée par l'ordinateur d'un autre membre du réseau. Aucun datacenter, aucun abonnement.">
<meta name="color-scheme" content="light">
<style>
@font-face{
  font-family:"Familjen"; font-style:normal; font-weight:400 700; font-display:swap;
  src:url("/static/fonts/familjen-latin.woff2") format("woff2");
}
:root{
  --bg:#F1F5F2; --card:#FFFFFF; --card-2:#F7FAF8;
  --verd:#3F8C79;            /* le vert-de-gris, patine du cuivre */
  --verd-deep:#245247; --verd-pale:#DCEBE5; --verd-line:#C3DBD2;
  --ink:#1E2B27; --ink-soft:#5F7069;
  --amber:#C97F1E; --amber-pale:#F6E9D2;
  --ui:"Familjen", "Avenir Next", system-ui, sans-serif;
  --mono:ui-monospace, SFMono-Regular, "Cascadia Mono", Consolas, monospace;
  --lift:0 1px 2px rgba(30,43,39,.05), 0 8px 24px -12px rgba(36,82,71,.22);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0; color:var(--ink); font-family:var(--ui); font-size:17px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
  background:
    radial-gradient(60rem 40rem at 82% -8%, #E4F0EA 0%, transparent 60%),
    radial-gradient(50rem 34rem at -10% 8%, #F5EFE2 0%, transparent 55%),
    var(--bg);
  background-attachment:fixed;
}
@media (prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }
.wrap{max-width:1120px; margin:0 auto; padding:0 clamp(1.1rem,3.6vw,2rem)}
a{color:inherit}

/* ---- Barre ------------------------------------------------------------ */
header{position:sticky; top:0; z-index:40; backdrop-filter:blur(10px);
  background:rgba(241,245,242,.82); border-bottom:1px solid var(--verd-line)}
header .wrap{display:flex; align-items:center; gap:.9rem; padding-block:.75rem}
.brand{display:flex; align-items:center; gap:.55rem; font-weight:700; font-size:1.1rem;
  letter-spacing:-.015em}
.brand .seal{width:1.6rem; height:1.6rem; border-radius:7px; display:grid; place-items:center;
  background:linear-gradient(145deg,var(--verd),var(--verd-deep)); color:#fff;
  font-size:.86rem; font-weight:700}
header nav{margin-left:auto; display:flex; align-items:center; gap:1.15rem; font-size:.92rem}
header nav a{color:var(--ink-soft); text-decoration:none}
header nav a:hover{color:var(--verd-deep)}
.purse{display:flex; align-items:center; gap:.45rem; background:var(--amber-pale);
  border:1px solid #E7D3AE; color:#7A5312; border-radius:999px; padding:.28rem .75rem;
  font-size:.86rem; font-weight:600}
.purse b{font-variant-numeric:tabular-nums}
@media (max-width:820px){ header nav a.opt{display:none} }

/* ---- Haut de page : le pitch + le produit ----------------------------- */
.top{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);
  gap:clamp(1.5rem,4vw,3rem); align-items:start; padding:clamp(2.2rem,5vw,3.6rem) 0}
@media (max-width:940px){ .top{grid-template-columns:1fr} }
.badge{display:inline-flex; align-items:center; gap:.45rem; background:var(--verd-pale);
  color:var(--verd-deep); border:1px solid var(--verd-line); border-radius:999px;
  padding:.3rem .8rem; font-size:.82rem; font-weight:600; margin-bottom:1.1rem}
.badge i{width:.45rem; height:.45rem; border-radius:50%; background:var(--verd);
  animation:beat 2.4s ease-in-out infinite}
@keyframes beat{0%,100%{opacity:1}50%{opacity:.25}}
h1{font-size:clamp(2rem,4.6vw,3.15rem); line-height:1.06; font-weight:700;
  letter-spacing:-.032em; margin:0 0 1rem}
h1 em{font-style:normal; color:var(--verd-deep);
  background:linear-gradient(180deg,transparent 64%, var(--verd-pale) 64%)}
.lede{font-size:1.08rem; color:#3C4E48; margin:0 0 1.5rem; max-width:46ch}
.facts{display:grid; gap:.6rem; margin:0 0 1.6rem; padding:0; list-style:none}
.facts li{display:flex; gap:.6rem; color:#3C4E48}
.facts li svg{flex:none; margin-top:.32rem; color:var(--verd)}
.mini{display:flex; gap:1.3rem; flex-wrap:wrap; font-size:.9rem; color:var(--ink-soft);
  border-top:1px solid var(--verd-line); padding-top:1rem}
.mini b{color:var(--ink); font-variant-numeric:tabular-nums}

/* ---- Le chat ---------------------------------------------------------- */
.chat{background:var(--card); border:1px solid var(--verd-line); border-radius:16px;
  box-shadow:var(--lift); overflow:hidden; display:flex; flex-direction:column;
  min-height:26rem}
.chat-head{display:flex; align-items:center; gap:.6rem; padding:.85rem 1.1rem;
  border-bottom:1px solid var(--verd-line); background:var(--card-2)}
.chat-head .t{font-weight:700; font-size:.98rem}
.chat-head .s{margin-left:auto; font-size:.8rem; color:var(--ink-soft)}
.chat-body{flex:1; padding:1.1rem; display:flex; flex-direction:column; gap:.9rem;
  overflow-y:auto; max-height:30rem}
.msg{max-width:88%; padding:.7rem .95rem; border-radius:13px; font-size:.98rem;
  line-height:1.55; white-space:pre-wrap}
.msg.me{align-self:flex-end; background:var(--verd-deep); color:#EAF3F0;
  border-bottom-right-radius:4px}
.msg.ai{align-self:flex-start; background:var(--verd-pale); border:1px solid var(--verd-line);
  border-bottom-left-radius:4px}
.msg.sys{align-self:center; background:transparent; color:var(--ink-soft); font-size:.88rem;
  text-align:center; max-width:100%; padding:.2rem}
.by{font-size:.78rem; color:var(--ink-soft); margin-top:.35rem; display:flex;
  align-items:center; gap:.35rem}
.by b{color:var(--verd-deep)}
.wait{display:flex; align-items:center; gap:.5rem; color:var(--ink-soft); font-size:.9rem}
.wait span{width:.4rem; height:.4rem; border-radius:50%; background:var(--verd);
  animation:hop 1.2s infinite}
.wait span:nth-child(2){animation-delay:.15s} .wait span:nth-child(3){animation-delay:.3s}
@keyframes hop{0%,60%,100%{transform:translateY(0); opacity:.4}30%{transform:translateY(-4px); opacity:1}}
.chat-foot{border-top:1px solid var(--verd-line); padding:.75rem; background:var(--card-2)}
.row{display:flex; gap:.55rem}
.row input, .row textarea{flex:1; font:inherit; font-size:.98rem; padding:.7rem .85rem;
  border:1px solid var(--verd-line); border-radius:10px; background:#fff; color:var(--ink);
  resize:none}
.row input:focus, .row textarea:focus{outline:2px solid var(--verd); outline-offset:-1px}
.row button{font:inherit; font-weight:600; font-size:.95rem; padding:.7rem 1.15rem;
  border:none; border-radius:10px; background:var(--verd-deep); color:#fff; cursor:pointer;
  transition:background .18s}
.row button:hover:not(:disabled){background:var(--verd)}
.row button:disabled{opacity:.5; cursor:default}
.hint{font-size:.82rem; color:var(--ink-soft); margin:.55rem .2rem 0}
.hint b{color:var(--ink)}

/* ---- Sections --------------------------------------------------------- */
section{padding:clamp(2.6rem,6vw,4.4rem) 0}
.tag{font-size:.78rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--verd); font-weight:600; margin:0 0 .8rem}
h2{font-size:clamp(1.5rem,3.2vw,2.1rem); line-height:1.16; font-weight:700;
  letter-spacing:-.025em; margin:0 0 .7rem; max-width:24ch}
.note{color:var(--ink-soft); max-width:62ch; margin:0}

.grid3{display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
  margin-top:1.9rem}
.tile{background:var(--card); border:1px solid var(--verd-line); border-radius:14px;
  padding:1.35rem 1.4rem; box-shadow:var(--lift)}
.tile .n{width:2rem; height:2rem; border-radius:9px; background:var(--verd-pale);
  color:var(--verd-deep); display:grid; place-items:center; font-weight:700; font-size:.9rem;
  margin-bottom:.8rem}
.tile h3{font-size:1.05rem; margin:0 0 .45rem; font-weight:700}
.tile p{margin:0; color:var(--ink-soft); font-size:.97rem}

.two{display:grid; gap:1.3rem; grid-template-columns:repeat(auto-fit,minmax(290px,1fr));
  margin-top:1.8rem}
.panel{background:var(--card); border:1px solid var(--verd-line); border-radius:14px;
  padding:1.4rem; box-shadow:var(--lift)}
.panel.soon{background:var(--card-2); border-style:dashed}
.panel h4{margin:0 0 .9rem; display:flex; align-items:center; gap:.55rem; font-size:1.02rem}
.pill{font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; padding:.14rem .5rem;
  border-radius:4px; font-weight:700}
.panel.now .pill{background:var(--verd); color:#fff}
.panel.soon .pill{background:var(--amber-pale); color:#7A5312; border:1px solid #E7D3AE}
.panel ul{margin:0; padding:0; list-style:none; display:grid; gap:.5rem; color:#3C4E48;
  font-size:.98rem}
.panel li{display:flex; gap:.6rem}
.panel.now li::before{content:"✓"; color:var(--verd); font-weight:700}
.panel.soon li::before{content:"→"; color:var(--amber)}

/* ---- Participer -------------------------------------------------------- */
.os{display:flex; gap:1.1rem; margin:1.6rem 0 .7rem; font-size:.92rem}
.os button{background:none; border:none; padding:0 0 3px; cursor:pointer; font:inherit;
  color:var(--ink-soft); border-bottom:2px solid transparent}
.os button[aria-selected="true"]{color:var(--ink); border-color:var(--verd); font-weight:600}
.cmd{display:flex; border:1px solid var(--verd-line); border-radius:10px; background:var(--card);
  overflow:hidden; max-width:680px; box-shadow:var(--lift)}
.cmd code{font-family:var(--mono); font-size:.87rem; padding:.85rem 1rem; flex:1;
  overflow-x:auto; white-space:nowrap}
.cmd button{font:inherit; font-size:.85rem; font-weight:600; padding:0 1.1rem; cursor:pointer;
  background:var(--verd-deep); color:#fff; border:none}
.cmd button:hover{background:var(--verd)}
.after{color:var(--ink-soft); font-size:.95rem; margin:1rem 0 0; max-width:62ch}
.after a{text-decoration-color:var(--verd)}
.pledge{margin:1.4rem 0 0; padding:0; list-style:none; display:grid; gap:.5rem; max-width:62ch}
.pledge li{display:flex; gap:.7rem}
.pledge li::before{content:"non"; flex:none; font-size:.7rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--amber); border:1px solid var(--amber); border-radius:3px;
  padding:0 .3rem; height:1.2rem; line-height:1.15rem; margin-top:.24rem}

/* ---- Compte ------------------------------------------------------------ */
dialog{border:none; border-radius:16px; padding:0; max-width:29rem; width:calc(100% - 2rem);
  box-shadow:0 24px 60px -20px rgba(30,43,39,.45); color:var(--ink)}
dialog::backdrop{background:rgba(30,43,39,.35)}
.dlg{padding:1.5rem}
.dlg h3{margin:0 0 .5rem; font-size:1.2rem}
.dlg p{margin:0 0 1rem; color:var(--ink-soft); font-size:.95rem}
.dlg .key{font-family:var(--mono); font-size:.82rem; background:var(--verd-pale);
  border:1px solid var(--verd-line); border-radius:8px; padding:.6rem .7rem;
  word-break:break-all; margin:.6rem 0}
.dlg .close{margin-top:.9rem; width:100%; justify-content:center}
.devices{margin:.8rem 0 0; padding:0; list-style:none; display:grid; gap:.4rem;
  font-size:.92rem}
.devices li{display:flex; gap:.6rem; align-items:baseline; color:var(--ink-soft)}
.devices b{color:var(--ink)}

footer{border-top:1px solid var(--verd-line); padding:2rem 0 3rem; color:var(--ink-soft);
  font-size:.9rem}
footer .wrap{display:flex; gap:1.3rem; flex-wrap:wrap}
footer .right{margin-left:auto}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <span class="brand"><span class="seal">L</span> Lenyay</span>
    <nav>
      <a href="#comment" class="opt">Comment ça marche</a>
      <a href="#etat" class="opt">Où on en est</a>
      <a href="/dashboard" class="opt">Le réseau</a>
      <a href="#participer">Participer</a>
      <button class="purse" id="purse" type="button" hidden>
        <b id="purse-n">0</b> crédits
      </button>
      <button class="purse" id="signup" type="button">Créer un compte</button>
    </nav>
  </div>
</header>

<div class="wrap">
  <div class="top">
    <div>
      <span class="badge"><i></i><span id="net-live">réseau actif</span></span>
      <h1>Une IA gratuite, servie par <em>nos machines</em>.</h1>
      <p class="lede">Pose ta question : elle part sur le réseau et c'est l'ordinateur
        d'un autre membre qui y répond. Aucun datacenter, aucun abonnement.</p>
      <ul class="facts">
        <li><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>
          20 crédits offerts à l'ouverture du compte — de quoi essayer tout de suite.</li>
        <li><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>
          Prête ta machine quand tu ne t'en sers pas : tu regagnes des crédits.</li>
        <li><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>
          Ni mot de passe, ni adresse e-mail, ni carte bancaire.</li>
      </ul>
      <p class="mini">
        <span><b id="s-devices">—</b> machines</span>
        <span><b id="s-done">—</b> calculs vérifiés</span>
        <span><b id="s-rate">—</b> de réussite</span>
      </p>
    </div>

    <div class="chat">
      <div class="chat-head">
        <span class="t">Demande au réseau</span>
        <span class="s" id="chat-state">prêt</span>
      </div>
      <div class="chat-body" id="log">
        <div class="msg ai">Bonjour ! Je suis l'IA de Lenyay. Ta question sera traitée
par l'ordinateur d'un membre du réseau — pose-la et regarde qui répond.</div>
      </div>
      <div class="chat-foot">
        <div class="row">
          <textarea id="q" rows="2" placeholder="Pose ta question…"></textarea>
          <button id="send" type="button">Envoyer</button>
        </div>
        <p class="hint" id="hint">Une question coûte <b>3 crédits</b>. Elle est lue par la
          machine d'un autre membre : n'y mets rien de confidentiel.</p>
      </div>
    </div>
  </div>
</div>

<section id="comment">
  <div class="wrap">
    <p class="tag">Comment ça marche</p>
    <h2>Un troc, pas un abonnement.</h2>
    <p class="note">Tu prêtes du temps de calcul quand ta machine ne fait rien. En échange,
      tu utilises l'IA quand ça t'arrange. Les crédits ne font que compter l'équilibre
      entre les deux.</p>
    <div class="grid3">
      <div class="tile">
        <div class="n">1</div>
        <h3>Tu poses une question</h3>
        <p>Elle rejoint une file d'attente et coûte quelques crédits. Rien n'est envoyé
          à une entreprise : le réseau, c'est nous.</p>
      </div>
      <div class="tile">
        <div class="n">2</div>
        <h3>Une machine la prend</h3>
        <p>Celle d'un membre, allumée à ce moment-là, avec le modèle déjà chargé. Tu vois
          son nom apparaître dans la réponse.</p>
      </div>
      <div class="tile">
        <div class="n">3</div>
        <h3>Elle est payée, tu es servi</h3>
        <p>Son propriétaire gagne des crédits, que tu regagneras à ton tour en laissant
          ta machine travailler la nuit.</p>
      </div>
    </div>
  </div>
</section>

<section id="etat">
  <div class="wrap">
    <p class="tag">Où on en est</p>
    <h2>On n'annonce que ce qui marche.</h2>
    <p class="note">Lenyay se construit en public. Voici ce qui fonctionne aujourd'hui,
      et ce sur quoi nous travaillons — pas de flou entre les deux.</p>
    <div class="two">
      <div class="panel now">
        <h4><span class="pill">Disponible</span></h4>
        <ul>
          <li>Poser une question, servie par la machine d'un membre</li>
          <li>L'IA hors ligne sur ta propre machine, sans limite (<code>--chat</code>)</li>
          <li>Compte, crédits gagnés et dépensés, appareils rattachés</li>
          <li>Le réseau tourne et réentraîne le modèle avec ce qu'il produit</li>
        </ul>
      </div>
      <div class="panel soon">
        <h4><span class="pill">En construction</span></h4>
        <ul>
          <li>Un modèle plus grand, servi par plusieurs machines à la fois</li>
          <li>Participer depuis un téléphone Android</li>
          <li>Conversations suivies, avec mémoire du fil</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="participer">
  <div class="wrap">
    <p class="tag">Participer</p>
    <h2>Prête ta machine, regagne des crédits.</h2>
    <p class="note">L'installation prend cinq minutes. Rien ne s'installe hors de son
      dossier, aucun mot de passe n'est demandé, et tu arrêtes quand tu veux.</p>
    <div class="os" role="tablist">
      <button role="tab" aria-selected="true" data-os="win">Windows</button>
      <button role="tab" aria-selected="false" data-os="nix">Linux / macOS</button>
    </div>
    <div class="cmd">
      <code id="cmd-text">irm https://lenyay.org/install.ps1 | iex</code>
      <button id="copy" type="button">Copier</button>
    </div>
    <p class="after">Au premier démarrage, le modèle se télécharge une fois (1,1 Go).
      Rattache ensuite ta machine à ton compte pour que ses gains alimentent tes crédits.
      <a href="https://github.com/k1tz03/lenyay/blob/main/REJOINDRE.md">Guide complet</a>.</p>
    <ul class="pledge">
      <li>de cryptomonnaie, ni de minage.</li>
      <li>de donnée personnelle : ni e-mail, ni mot de passe, ni carte bancaire.</li>
      <li>de démarrage automatique dans ton dos.</li>
      <li>de publicité, ni de traceur sur cette page.</li>
      <li>de crédits échangeables contre de l'argent.</li>
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

<dialog id="dlg">
  <div class="dlg" id="dlg-body"></div>
</dialog>

<script>
const fmt = n => n.toLocaleString("fr-FR");
const $ = id => document.getElementById(id);
const KEY = "lenyay.account";
let account = null;

// --- Compte : une clé, pas de mot de passe -----------------------------
async function loadAccount(){
  const key = localStorage.getItem(KEY);
  if(!key) return;
  try{
    const r = await fetch("/accounts/me", {headers:{"X-Account-Key":key}});
    if(!r.ok){ localStorage.removeItem(KEY); return; }
    account = await r.json(); account.key = key;
    paintPurse();
  }catch(e){}
}
function paintPurse(){
  if(!account) return;
  $("purse").hidden = false; $("signup").hidden = true;
  $("purse-n").textContent = fmt(account.credits);
}
async function createAccount(){
  const handle = (prompt("Choisis un pseudo (visible sur le tableau de bord) :", "") || "").trim();
  if(handle === null) return;
  const r = await fetch("/accounts", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({handle: handle || "anonyme"})});
  if(!r.ok){ alert("Création impossible pour le moment."); return; }
  const a = await r.json();
  localStorage.setItem(KEY, a.account_key);
  account = {handle:a.handle, credits:a.credits, key:a.account_key, devices:[], questions:[]};
  paintPurse();
  showDialog(`<h3>Compte créé</h3>
    <p>Tu as <b>${a.credits} crédits</b> pour commencer. Ta clé est ta seule identité :
    garde-la si tu veux retrouver ton compte depuis un autre navigateur.</p>
    <div class="key">${a.account_key}</div>
    <button class="row-btn close" onclick="document.getElementById('dlg').close()"
      style="font:inherit;font-weight:600;padding:.7rem 1.15rem;border:none;border-radius:10px;background:var(--verd-deep);color:#fff;cursor:pointer">C'est noté</button>`);
}
function showDialog(html){ $("dlg-body").innerHTML = html; $("dlg").showModal(); }

$("signup").addEventListener("click", createAccount);
$("purse").addEventListener("click", async () => {
  const r = await fetch("/accounts/me", {headers:{"X-Account-Key":account.key}});
  const me = await r.json(); account = {...me, key:account.key}; paintPurse();
  const devices = me.devices.length
    ? `<ul class="devices">${me.devices.map(d =>
        `<li><b>${escapeHtml(d.device_name)}</b> · ${fmt(d.credits||0)} crédits gagnés</li>`).join("")}</ul>`
    : `<p>Aucune machine rattachée. Installe Lenyay et rattache-la pour gagner des crédits.</p>`;
  showDialog(`<h3>${escapeHtml(me.handle)}</h3>
    <p><b>${fmt(me.credits)} crédits</b> · ${me.questions.length} question(s) posée(s)</p>
    ${devices}
    <div class="key">${account.key}</div>
    <p style="font-size:.86rem">Ta clé de compte — conserve-la.</p>
    <button class="close" onclick="document.getElementById('dlg').close()"
      style="font:inherit;font-weight:600;padding:.7rem 1.15rem;border:none;border-radius:10px;background:var(--verd-deep);color:#fff;cursor:pointer;width:100%">Fermer</button>`);
});
function escapeHtml(s){ const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// --- Le chat ------------------------------------------------------------
function bubble(cls, text){
  const el = document.createElement("div");
  el.className = "msg " + cls; el.textContent = text;
  $("log").append(el); $("log").scrollTop = $("log").scrollHeight;
  return el;
}
function waiting(text){
  const el = document.createElement("div");
  el.className = "msg ai";
  el.innerHTML = `<span class="wait">${text} <span></span><span></span><span></span></span>`;
  $("log").append(el); $("log").scrollTop = $("log").scrollHeight;
  return el;
}

async function send(){
  const text = $("q").value.trim();
  if(!text) return;
  if(!account){
    bubble("sys", "Crée un compte pour poser ta question — 20 crédits offerts.");
    await createAccount();
    if(!account) return;
  }
  $("q").value = ""; $("send").disabled = true; $("chat-state").textContent = "envoi…";
  bubble("me", text);

  let r = await fetch("/ask", {method:"POST",
    headers:{"Content-Type":"application/json","X-Account-Key":account.key},
    body: JSON.stringify({prompt:text})});
  if(r.status === 402){
    bubble("sys", "Crédits épuisés. Lance Lenyay sur ta machine pour en regagner.");
    $("send").disabled = false; $("chat-state").textContent = "prêt"; return;
  }
  if(!r.ok){
    bubble("sys", "Le réseau n'a pas pu prendre la question. Réessaie dans un instant.");
    $("send").disabled = false; $("chat-state").textContent = "prêt"; return;
  }
  const asked = await r.json();
  account.credits = asked.credits_left; paintPurse();

  const pending = waiting("en attente d'une machine disponible");
  $("chat-state").textContent = "en attente";
  let tries = 0;
  const timer = setInterval(async () => {
    tries++;
    try{
      const s = await (await fetch("/ask/" + asked.question_id)).json();
      if(s.status === "serving"){
        pending.innerHTML = `<span class="wait">${escapeHtml(s.device_name || "une machine")} rédige <span></span><span></span><span></span></span>`;
        $("chat-state").textContent = "en cours";
      }
      if(s.status === "done"){
        clearInterval(timer);
        pending.remove();
        const el = bubble("ai", s.answer);
        const by = document.createElement("p");
        by.className = "by";
        by.innerHTML = `Répondu par <b>${escapeHtml(s.device_name || "une machine du réseau")}</b>`;
        el.append(by);
        $("send").disabled = false; $("chat-state").textContent = "prêt";
      }
      if(tries > 100){
        clearInterval(timer); pending.remove();
        bubble("sys", "Aucune machine n'était disponible. Ta question reste en file : reviens dans un moment.");
        $("send").disabled = false; $("chat-state").textContent = "prêt";
      }
    }catch(e){}
  }, 2000);
}
$("send").addEventListener("click", send);
$("q").addEventListener("keydown", e => {
  if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); send(); }
});

// --- Le réseau, en direct ------------------------------------------------
async function readStats(){
  try{
    const s = await (await fetch("/stats", {cache:"no-store"})).json();
    $("s-devices").textContent = fmt(s.devices_seen);
    $("s-done").textContent = fmt(s.accepted_rollouts);
    $("s-rate").textContent = (100 * s.acceptance_rate).toFixed(0) + " %";
    $("net-live").textContent = s.devices_seen + " machine" + (s.devices_seen > 1 ? "s" : "") + " sur le réseau";
  }catch(e){}
}
readStats(); setInterval(readStats, 15000); loadAccount();

// --- Installation --------------------------------------------------------
const COMMANDS = {
  win: "irm https://lenyay.org/install.ps1 | iex",
  nix: "curl -fsSL https://lenyay.org/install.sh | bash",
};
document.querySelectorAll(".os button").forEach(b => {
  b.addEventListener("click", () => {
    document.querySelectorAll(".os button").forEach(o => o.setAttribute("aria-selected","false"));
    b.setAttribute("aria-selected","true");
    $("cmd-text").textContent = COMMANDS[b.dataset.os];
  });
});
$("copy").addEventListener("click", async e => {
  try{
    await navigator.clipboard.writeText($("cmd-text").textContent);
    e.target.textContent = "Copié"; setTimeout(() => { e.target.textContent = "Copier"; }, 1800);
  }catch(err){ e.target.textContent = "Ctrl+C"; }
});
</script>
</body>
</html>"""
