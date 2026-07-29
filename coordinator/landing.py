"""L'application Lenyay — la conversation d'abord, l'explication ensuite.

Disposition d'un assistant : fils de conversation à gauche, échange au centre,
choix du modèle et bourse à portée. Le discours sur le projet passe sous le
pli : qui arrive ici veut d'abord poser sa question.

Palette : vert-de-gris (patine du cuivre) sur fond clair et chaud.

Une seule page, aucun framework, aucune étape de construction. La police est
hébergée avec le site (aucun appel à un CDN tiers).
"""

LANDING_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — l'IA servie par nos machines</title>
<meta name="description" content="Pose ta question : elle est traitée par l'ordinateur d'un autre membre. Gratuit, sans datacenter.">
<meta name="color-scheme" content="light">
<style>
@font-face{font-family:"Familjen"; font-style:normal; font-weight:400 700;
  font-display:swap; src:url("/static/fonts/familjen-latin.woff2") format("woff2")}
:root{
  --bg:#F2F6F3; --panel:#FFFFFF; --panel-2:#F6FAF8; --side:#EAF1EC;
  --verd:#3F8C79; --verd-deep:#245247; --verd-pale:#DCEBE5; --line:#CFE0D8;
  --ink:#1E2B27; --soft:#5F7069; --amber:#C97F1E; --amber-pale:#F7EAD3;
  --ui:"Familjen","Avenir Next",system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace;
  --lift:0 1px 2px rgba(30,43,39,.05), 0 10px 28px -14px rgba(36,82,71,.25);
}
*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink); font-family:var(--ui);
  font-size:16.5px; line-height:1.6; -webkit-font-smoothing:antialiased}
a{color:inherit}
button{font:inherit}

/* ================= L'application ================= */
.app{display:grid; grid-template-columns:270px minmax(0,1fr); height:100dvh}
@media (max-width:900px){ .app{grid-template-columns:1fr} .side{display:none}
  .side.open{display:flex; position:fixed; inset:0 auto 0 0; width:82%; z-index:60} }

/* ---- Colonne des fils ---- */
.side{background:var(--side); border-right:1px solid var(--line); display:flex;
  flex-direction:column; min-height:0}
.side header{display:flex; align-items:center; gap:.55rem; padding:.9rem 1rem}
.logo{display:flex; align-items:center; gap:.5rem; font-weight:700; letter-spacing:-.015em}
.logo .seal{width:1.5rem; height:1.5rem; border-radius:7px; display:grid; place-items:center;
  background:linear-gradient(145deg,var(--verd),var(--verd-deep)); color:#fff;
  font-size:.8rem; font-weight:700}
.newconv{margin:0 .75rem .6rem; padding:.6rem .9rem; border-radius:9px; cursor:pointer;
  background:var(--verd-deep); color:#fff; border:none; font-weight:600; font-size:.92rem;
  display:flex; align-items:center; gap:.5rem; justify-content:center}
.newconv:hover{background:var(--verd)}
.threads{flex:1; overflow-y:auto; padding:.2rem .5rem 1rem; min-height:0}
.thread{display:flex; align-items:center; gap:.4rem; padding:.5rem .6rem; border-radius:8px;
  cursor:pointer; color:var(--soft); font-size:.92rem}
.thread:hover{background:#E0EBE3; color:var(--ink)}
.thread.on{background:var(--verd-pale); color:var(--verd-deep); font-weight:600}
.thread span{flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.thread .x{opacity:0; border:none; background:none; cursor:pointer; color:var(--soft);
  padding:0 .2rem; font-size:1rem}
.thread:hover .x{opacity:.7}
.side footer{border-top:1px solid var(--line); padding:.8rem 1rem; display:grid; gap:.55rem}
.wallet{display:flex; align-items:center; gap:.5rem; background:var(--amber-pale);
  border:1px solid #E7D3AE; color:#7A5312; border-radius:9px; padding:.45rem .7rem;
  font-size:.88rem; font-weight:600; cursor:pointer; width:100%}
.wallet b{font-variant-numeric:tabular-nums}
.wallet .g{margin-left:auto; font-weight:500; opacity:.8; font-size:.8rem}
.sidelink{color:var(--soft); font-size:.85rem; text-decoration:none}
.sidelink:hover{color:var(--verd-deep)}

/* ---- Zone de conversation ---- */
.main{display:flex; flex-direction:column; min-width:0; min-height:0}
.bar{display:flex; align-items:center; gap:.7rem; padding:.7rem 1.1rem;
  border-bottom:1px solid var(--line); background:rgba(242,246,243,.85);
  backdrop-filter:blur(8px)}
.burger{display:none; background:none; border:none; cursor:pointer; font-size:1.2rem}
@media (max-width:900px){ .burger{display:block} }
.picker{display:flex; gap:.3rem; background:var(--panel); border:1px solid var(--line);
  border-radius:999px; padding:.22rem}
.picker button{border:none; background:none; cursor:pointer; border-radius:999px;
  padding:.35rem .85rem; font-size:.86rem; color:var(--soft); display:flex; gap:.4rem;
  align-items:center}
.picker button[aria-pressed="true"]{background:var(--verd-deep); color:#fff; font-weight:600}
.picker .price{font-size:.74rem; opacity:.75}
.netstate{margin-left:auto; font-size:.83rem; color:var(--soft); display:flex;
  align-items:center; gap:.4rem}
.netstate i{width:.45rem; height:.45rem; border-radius:50%; background:var(--verd);
  animation:beat 2.4s ease-in-out infinite}
@keyframes beat{0%,100%{opacity:1}50%{opacity:.25}}
@media (max-width:620px){ .netstate{display:none} }

.stream{flex:1; overflow-y:auto; padding:1.4rem 1.1rem 1rem; min-height:0}
.inner{max-width:760px; margin:0 auto; display:flex; flex-direction:column; gap:1.1rem}
.turn{display:flex; gap:.8rem}
.turn .who{width:1.85rem; height:1.85rem; border-radius:8px; flex:none; display:grid;
  place-items:center; font-size:.78rem; font-weight:700}
.turn.me .who{background:var(--verd-deep); color:#fff}
.turn.ai .who{background:var(--verd-pale); color:var(--verd-deep);
  border:1px solid var(--line)}
.turn .body{min-width:0; flex:1}
.turn .body .txt{white-space:pre-wrap; word-wrap:break-word}
.turn.ai .body .txt{background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:.85rem 1rem; box-shadow:var(--lift)}
.meta{font-size:.78rem; color:var(--soft); margin-top:.4rem; display:flex; gap:.5rem;
  align-items:center; flex-wrap:wrap}
.meta b{color:var(--verd-deep)}
.chip{border:1px solid var(--line); border-radius:999px; padding:.05rem .45rem;
  background:var(--panel-2)}
.dots span{display:inline-block; width:.4rem; height:.4rem; border-radius:50%;
  background:var(--verd); margin-right:.2rem; animation:hop 1.2s infinite}
.dots span:nth-child(2){animation-delay:.15s} .dots span:nth-child(3){animation-delay:.3s}
@keyframes hop{0%,60%,100%{transform:translateY(0);opacity:.35}30%{transform:translateY(-4px);opacity:1}}

.welcome{text-align:center; padding:2.5rem 0 1rem}
.welcome h1{font-size:clamp(1.6rem,3.4vw,2.15rem); letter-spacing:-.025em; margin:0 0 .5rem}
.welcome p{color:var(--soft); margin:0 auto; max-width:44ch}
.samples{display:flex; gap:.5rem; flex-wrap:wrap; justify-content:center; margin-top:1.4rem}
.samples button{background:var(--panel); border:1px solid var(--line); border-radius:999px;
  padding:.45rem .9rem; font-size:.88rem; color:var(--soft); cursor:pointer}
.samples button:hover{border-color:var(--verd); color:var(--verd-deep)}

.composer{border-top:1px solid var(--line); background:rgba(242,246,243,.9); padding:.85rem 1.1rem}
.composer .inner{gap:.5rem}
.box{display:flex; gap:.5rem; align-items:flex-end; background:var(--panel);
  border:1px solid var(--line); border-radius:14px; padding:.5rem .5rem .5rem .9rem;
  box-shadow:var(--lift)}
.box textarea{flex:1; border:none; outline:none; resize:none; font:inherit; font-size:1rem;
  background:none; color:var(--ink); max-height:9rem; padding:.35rem 0}
.box button{border:none; border-radius:10px; background:var(--verd-deep); color:#fff;
  width:2.4rem; height:2.4rem; cursor:pointer; display:grid; place-items:center}
.box button:hover:not(:disabled){background:var(--verd)}
.box button:disabled{opacity:.45; cursor:default}
.legalese{font-size:.78rem; color:var(--soft); text-align:center}

/* ---- Sous le pli : l'explication ---- */
.below{background:var(--panel); border-top:1px solid var(--line)}
.wrap{max-width:1000px; margin:0 auto; padding:0 clamp(1.1rem,3.6vw,2rem)}
.below section{padding:clamp(2.4rem,5vw,3.6rem) 0; border-bottom:1px solid var(--line)}
.tag{font-size:.76rem; letter-spacing:.14em; text-transform:uppercase; color:var(--verd);
  font-weight:600; margin:0 0 .7rem}
h2{font-size:clamp(1.35rem,2.8vw,1.85rem); line-height:1.18; letter-spacing:-.02em;
  margin:0 0 .6rem; max-width:26ch}
.note{color:var(--soft); max-width:62ch; margin:0}
.grid3{display:grid; gap:.9rem; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  margin-top:1.6rem}
.tile{background:var(--panel-2); border:1px solid var(--line); border-radius:12px;
  padding:1.15rem 1.2rem}
.tile .n{width:1.8rem; height:1.8rem; border-radius:8px; background:var(--verd-pale);
  color:var(--verd-deep); display:grid; place-items:center; font-weight:700; font-size:.85rem;
  margin-bottom:.6rem}
.tile h3{font-size:1rem; margin:0 0 .35rem}
.tile p{margin:0; color:var(--soft); font-size:.94rem}
.two{display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
  margin-top:1.5rem}
.panel{background:var(--panel-2); border:1px solid var(--line); border-radius:12px; padding:1.2rem}
.panel.soon{border-style:dashed}
.panel h4{margin:0 0 .8rem; display:flex; align-items:center; gap:.5rem; font-size:.98rem}
.pill{font-size:.68rem; letter-spacing:.09em; text-transform:uppercase; padding:.12rem .45rem;
  border-radius:4px; font-weight:700}
.panel.now .pill{background:var(--verd); color:#fff}
.panel.soon .pill{background:var(--amber-pale); color:#7A5312; border:1px solid #E7D3AE}
.panel ul{margin:0; padding:0; list-style:none; display:grid; gap:.45rem; font-size:.95rem;
  color:#3C4E48}
.panel li{display:flex; gap:.55rem}
.panel.now li::before{content:"✓"; color:var(--verd); font-weight:700}
.panel.soon li::before{content:"→"; color:var(--amber)}
.cmd{display:flex; border:1px solid var(--line); border-radius:10px; background:var(--panel-2);
  overflow:hidden; max-width:640px; margin-top:1.3rem}
.cmd code{font-family:var(--mono); font-size:.85rem; padding:.8rem .95rem; flex:1;
  overflow-x:auto; white-space:nowrap}
.cmd button{font-size:.84rem; font-weight:600; padding:0 1rem; cursor:pointer;
  background:var(--verd-deep); color:#fff; border:none}
.os{display:flex; gap:1rem; margin-top:1.3rem; font-size:.9rem}
.os button{background:none; border:none; padding:0 0 3px; cursor:pointer; color:var(--soft);
  border-bottom:2px solid transparent}
.os button[aria-selected="true"]{color:var(--ink); border-color:var(--verd); font-weight:600}
.pledge{margin:1.2rem 0 0; padding:0; list-style:none; display:grid; gap:.45rem; max-width:60ch}
.pledge li{display:flex; gap:.65rem; font-size:.95rem}
.pledge li::before{content:"non"; flex:none; font-size:.68rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--amber); border:1px solid var(--amber); border-radius:3px;
  padding:0 .28rem; height:1.15rem; line-height:1.1rem; margin-top:.24rem}
.foot{padding:1.6rem 0 2.4rem; color:var(--soft); font-size:.87rem; display:flex; gap:1.2rem;
  flex-wrap:wrap}
.foot .right{margin-left:auto}

dialog{border:none; border-radius:16px; padding:0; max-width:28rem; width:calc(100% - 2rem);
  box-shadow:0 24px 60px -20px rgba(30,43,39,.45); color:var(--ink)}
dialog::backdrop{background:rgba(30,43,39,.4)}
.dlg{padding:1.4rem}
.dlg h3{margin:0 0 .5rem}
.dlg p{margin:0 0 .9rem; color:var(--soft); font-size:.94rem}
.dlg .key{font-family:var(--mono); font-size:.78rem; background:var(--verd-pale);
  border:1px solid var(--line); border-radius:8px; padding:.55rem .65rem; word-break:break-all}
.dlg input{width:100%; font:inherit; padding:.6rem .75rem; border:1px solid var(--line);
  border-radius:9px; margin-bottom:.8rem}
.dlg .go{width:100%; padding:.7rem; border:none; border-radius:9px; background:var(--verd-deep);
  color:#fff; font-weight:600; cursor:pointer; margin-top:.6rem}
.dlg ul{margin:.6rem 0 0; padding:0; list-style:none; display:grid; gap:.35rem; font-size:.9rem}
.dlg ul li{display:flex; gap:.5rem; color:var(--soft)}
.dlg ul b{color:var(--ink)}
</style>
</head>
<body>

<div class="app">
  <aside class="side" id="side">
    <header>
      <span class="logo"><span class="seal">L</span> Lenyay</span>
    </header>
    <button class="newconv" id="new-conv">＋ Nouvelle conversation</button>
    <div class="threads" id="threads"></div>
    <footer>
      <button class="wallet" id="wallet">
        <span id="wallet-n">—</span> crédits <span class="g" id="wallet-who">compte</span>
      </button>
      <a class="sidelink" href="#projet">Qu'est-ce que Lenyay ?</a>
      <a class="sidelink" href="/dashboard">Le réseau en direct</a>
    </footer>
  </aside>

  <main class="main">
    <div class="bar">
      <button class="burger" id="burger" aria-label="Fils">☰</button>
      <div class="picker" id="picker"></div>
      <span class="netstate"><i></i><span id="net">réseau</span></span>
    </div>

    <div class="stream" id="stream">
      <div class="inner" id="turns">
        <div class="welcome">
          <h1>Pose ta question au réseau.</h1>
          <p>Elle sera traitée par l'ordinateur d'un membre, pas par un datacenter.
            Tu as des crédits offerts pour commencer.</p>
          <div class="samples">
            <button>Explique-moi la photosynthèse simplement</button>
            <button>Écris un mot d'excuse à mon voisin</button>
            <button>Combien font 17 % de 340 ?</button>
          </div>
        </div>
      </div>
    </div>

    <div class="composer">
      <div class="inner">
        <div class="box">
          <textarea id="q" rows="1" placeholder="Écris ton message…"></textarea>
          <button id="send" aria-label="Envoyer">↑</button>
        </div>
        <p class="legalese">Ta question est lue par la machine d'un autre membre —
          n'y mets rien de confidentiel.</p>
      </div>
    </div>
  </main>
</div>

<div class="below" id="projet">
  <div class="wrap">
    <section>
      <p class="tag">Ce que c'est</p>
      <h2>Une IA gratuite qui ne tourne dans aucun datacenter.</h2>
      <p class="note">Elle tourne sur nos ordinateurs. Tu prêtes le tien quand tu ne t'en
        sers pas — la nuit, par exemple — et tu utilises l'IA quand ça t'arrange. Les
        crédits ne font que compter l'équilibre entre les deux.</p>
      <div class="grid3">
        <div class="tile"><div class="n">1</div><h3>Tu poses une question</h3>
          <p>Elle rejoint une file. Le modèle « Costaud » coûte plus cher : il est plus
            lent et demande une machine plus solide.</p></div>
        <div class="tile"><div class="n">2</div><h3>Une machine la prend</h3>
          <p>Celle d'un membre, allumée à ce moment-là, modèle déjà chargé. Son nom
            apparaît sous la réponse.</p></div>
        <div class="tile"><div class="n">3</div><h3>Chacun y gagne</h3>
          <p>Son propriétaire est crédité ; toi, tu regagnes des crédits en laissant ta
            machine travailler à son tour.</p></div>
      </div>
    </section>

    <section>
      <p class="tag">Où on en est</p>
      <h2>On n'annonce que ce qui marche.</h2>
      <div class="two">
        <div class="panel now">
          <h4><span class="pill">Disponible</span></h4>
          <ul>
            <li>Conversations suivies, avec mémoire du fil</li>
            <li>Deux modèles au choix, facturés en crédits</li>
            <li>Compte, crédits gagnés et dépensés, machines rattachées</li>
            <li>L'IA hors ligne sur ta machine (<code>--chat</code>), sans limite</li>
          </ul>
        </div>
        <div class="panel soon">
          <h4><span class="pill">En construction</span></h4>
          <ul>
            <li>Abonnement pour continuer sans contribuer</li>
            <li>Un très grand modèle réparti sur plusieurs machines</li>
            <li>Participer depuis un téléphone Android</li>
          </ul>
        </div>
      </div>
    </section>

    <section>
      <p class="tag">Participer</p>
      <h2>Prête ta machine, regagne des crédits.</h2>
      <p class="note">Cinq minutes d'installation. Rien ne s'installe hors de son dossier,
        aucun mot de passe n'est demandé, tu arrêtes quand tu veux.</p>
      <div class="os" role="tablist">
        <button role="tab" aria-selected="true" data-os="win">Windows</button>
        <button role="tab" aria-selected="false" data-os="nix">Linux / macOS</button>
      </div>
      <div class="cmd">
        <code id="cmd-text">irm https://lenyay.org/install.ps1 | iex</code>
        <button id="copy">Copier</button>
      </div>
      <ul class="pledge">
        <li>de cryptomonnaie, ni de minage.</li>
        <li>de donnée personnelle : ni e-mail, ni mot de passe, ni carte bancaire.</li>
        <li>de démarrage automatique dans ton dos.</li>
        <li>de publicité, ni de traceur sur cette page.</li>
      </ul>
    </section>

    <div class="foot">
      <span>Lenyay — un bien commun</span>
      <a href="https://github.com/k1tz03/lenyay">Le code, entièrement ouvert</a>
      <a href="/dashboard">Le réseau en direct</a>
      <span class="right">Construit en public</span>
    </div>
  </div>
</div>

<dialog id="dlg"><div class="dlg" id="dlg-body"></div></dialog>

<script>
const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString("fr-FR");
const KEY = "lenyay.account";
let account = null, tiers = [], tier = "rapide", conv = null, polling = null;

const esc = s => { const d = document.createElement("div"); d.textContent = s ?? ""; return d.innerHTML; };
const api = (url, opt = {}) => fetch(url, {...opt, headers: {
  "Content-Type": "application/json",
  ...(account ? {"X-Account-Key": account.key} : {}),
  ...(opt.headers || {}),
}});

/* ---------- Paliers ---------- */
async function loadTiers(){
  const d = await (await fetch("/tiers")).json();
  tiers = d.tiers; tier = d.default;
  $("picker").innerHTML = tiers.map(t =>
    `<button data-t="${t.id}" aria-pressed="${t.id === tier}" title="${esc(t.about)}">
       ${esc(t.label)} <span class="price">${t.cost} cr.</span></button>`).join("");
  $("picker").querySelectorAll("button").forEach(b => b.onclick = () => {
    tier = b.dataset.t;
    $("picker").querySelectorAll("button").forEach(o =>
      o.setAttribute("aria-pressed", o.dataset.t === tier));
  });
}

/* ---------- Compte ---------- */
async function loadAccount(){
  const key = localStorage.getItem(KEY);
  if(!key) return;
  const r = await fetch("/accounts/me", {headers:{"X-Account-Key":key}});
  if(!r.ok){ localStorage.removeItem(KEY); return; }
  account = {...await r.json(), key};
  paintWallet(); loadThreads();
}
function paintWallet(){
  if(!account) return;
  $("wallet-n").innerHTML = "<b>" + fmt(account.credits) + "</b>";
  $("wallet-who").textContent = account.handle;
}
async function ensureAccount(){
  if(account) return true;
  return new Promise(resolve => {
    $("dlg-body").innerHTML = `<h3>Bienvenue</h3>
      <p>Choisis un pseudo. Pas d'e-mail, pas de mot de passe : ta clé suffit.
      Tu commences avec des crédits offerts.</p>
      <input id="h" placeholder="ton pseudo" maxlength="40">
      <button class="go" id="ok">Créer mon compte</button>`;
    $("dlg").showModal();
    $("ok").onclick = async () => {
      const handle = ($("h").value || "anonyme").trim();
      const r = await fetch("/accounts", {method:"POST",
        headers:{"Content-Type":"application/json"}, body:JSON.stringify({handle})});
      if(!r.ok){ $("dlg").close(); resolve(false); return; }
      const a = await r.json();
      localStorage.setItem(KEY, a.account_key);
      account = {handle:a.handle, credits:a.credits, key:a.account_key, devices:[], questions:[]};
      paintWallet(); loadThreads();
      $("dlg-body").innerHTML = `<h3>C'est fait, ${esc(a.handle)}</h3>
        <p>Tu as <b>${a.credits} crédits</b>. Voici ta clé : garde-la pour retrouver ton
        compte depuis un autre navigateur.</p>
        <div class="key">${a.account_key}</div>
        <button class="go" onclick="document.getElementById('dlg').close()">Commencer</button>`;
      resolve(true);
    };
  });
}
$("wallet").onclick = async () => {
  if(!account) return ensureAccount();
  const me = await (await api("/accounts/me")).json();
  account = {...me, key:account.key}; paintWallet();
  const devices = me.devices.length
    ? `<ul>${me.devices.map(d => `<li><b>${esc(d.device_name)}</b> · ${fmt(d.credits||0)} crédits gagnés</li>`).join("")}</ul>`
    : `<p>Aucune machine rattachée. Installe Lenyay et rattache-la pour gagner des crédits
       au lieu d'en dépenser.</p>`;
  $("dlg-body").innerHTML = `<h3>${esc(me.handle)}</h3>
    <p><b>${fmt(me.credits)} crédits</b></p>${devices}
    <p style="margin-top:1rem">Ta clé de compte :</p>
    <div class="key">${account.key}</div>
    <button class="go" onclick="document.getElementById('dlg').close()">Fermer</button>`;
  $("dlg").showModal();
};

/* ---------- Fils ---------- */
async function loadThreads(){
  if(!account) return;
  const d = await (await api("/conversations")).json();
  $("threads").innerHTML = d.conversations.map(c =>
    `<div class="thread ${c.id === conv ? "on" : ""}" data-id="${c.id}">
       <span>${esc(c.title)}</span><button class="x" data-del="${c.id}">×</button></div>`).join("")
    || `<p style="padding:.6rem;color:var(--soft);font-size:.88rem">Aucune conversation.</p>`;
  $("threads").querySelectorAll(".thread").forEach(el => el.onclick = e => {
    if(e.target.dataset.del) return;
    openThread(el.dataset.id);
  });
  $("threads").querySelectorAll("[data-del]").forEach(b => b.onclick = async e => {
    e.stopPropagation();
    await api("/conversations/" + b.dataset.del, {method:"DELETE"});
    if(conv === b.dataset.del){ conv = null; blank(); }
    loadThreads();
  });
}
function blank(){
  $("turns").innerHTML = `<div class="welcome"><h1>Pose ta question au réseau.</h1>
    <p>Elle sera traitée par l'ordinateur d'un membre, pas par un datacenter.</p></div>`;
}
async function openThread(id){
  conv = id;
  const d = await (await api("/conversations/" + id)).json();
  $("turns").innerHTML = "";
  d.messages.forEach(m => addTurn(m.role === "user" ? "me" : "ai", m.content,
    m.role === "assistant" ? m : null));
  loadThreads(); scroll();
}
function addTurn(kind, text, meta){
  const el = document.createElement("div");
  el.className = "turn " + kind;
  el.innerHTML = `<div class="who">${kind === "me" ? "toi" : "IA"}</div>
    <div class="body"><div class="txt"></div></div>`;
  el.querySelector(".txt").textContent = text;
  if(meta){
    const m = document.createElement("p");
    m.className = "meta";
    m.innerHTML = `Répondu par <b>${esc(meta.device_name || "une machine")}</b>` +
      (meta.tier ? ` <span class="chip">${esc(meta.tier)}</span>` : "");
    el.querySelector(".body").append(m);
  }
  $("turns").append(el); scroll();
  return el;
}
const scroll = () => { $("stream").scrollTop = $("stream").scrollHeight; };

/* ---------- Envoyer ---------- */
async function send(text){
  text = (text ?? $("q").value).trim();
  if(!text) return;
  if(!await ensureAccount()) return;
  if(!conv){
    conv = (await (await api("/conversations", {method:"POST"})).json()).id;
    $("turns").innerHTML = "";
  }
  $("q").value = ""; $("q").style.height = "auto"; $("send").disabled = true;
  addTurn("me", text);

  const r = await api(`/conversations/${conv}/messages`, {method:"POST",
    body: JSON.stringify({prompt:text, tier})});
  if(r.status === 402){
    const d = await r.json();
    outOfCredits(d.detail);
    $("send").disabled = false; return;
  }
  if(!r.ok){ addTurn("ai", "Le réseau n'a pas pu prendre la question. Réessaie."); $("send").disabled = false; return; }
  const asked = await r.json();
  account.credits = asked.credits_left; paintWallet(); loadThreads();

  const pending = addTurn("ai", "");
  pending.querySelector(".txt").innerHTML =
    `<span class="dots">en attente d'une machine <span></span><span></span><span></span></span>`;
  let tries = 0;
  clearInterval(polling);
  polling = setInterval(async () => {
    tries++;
    try{
      const s = await (await fetch("/ask/" + asked.question_id)).json();
      if(s.status === "serving"){
        pending.querySelector(".txt").innerHTML =
          `<span class="dots">${esc(s.device_name || "une machine")} rédige <span></span><span></span><span></span></span>`;
      }
      if(s.status === "done"){
        clearInterval(polling); pending.remove();
        addTurn("ai", s.answer, {device_name:s.device_name, tier});
        $("send").disabled = false;
      }
      if(tries > 120){
        clearInterval(polling); pending.querySelector(".txt").textContent =
          "Aucune machine disponible pour l'instant. Ta question reste en file.";
        $("send").disabled = false;
      }
    }catch(e){}
  }, 2000);
}
function outOfCredits(detail){
  $("dlg-body").innerHTML = `<h3>Plus de crédits</h3>
    <p>${esc(detail)}</p>
    <ul>
      <li><b>Contribuer</b> — laisse Lenyay tourner : chaque calcul vérifié te recrédite.</li>
      <li><b>S'abonner</b> — bientôt, pour utiliser sans contribuer.</li>
    </ul>
    <button class="go" onclick="document.getElementById('dlg').close();location.hash='#projet'">
      Voir comment contribuer</button>`;
  $("dlg").showModal();
}
$("send").onclick = () => send();
$("q").addEventListener("keydown", e => {
  if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); send(); }
});
$("q").addEventListener("input", e => {
  e.target.style.height = "auto";
  e.target.style.height = Math.min(e.target.scrollHeight, 144) + "px";
});
document.querySelectorAll(".samples button").forEach(b => b.onclick = () => send(b.textContent.trim()));
$("new-conv").onclick = async () => {
  if(!await ensureAccount()) return;
  conv = null; blank(); loadThreads(); $("q").focus();
};
$("burger").onclick = () => $("side").classList.toggle("open");

/* ---------- Réseau et installation ---------- */
async function net(){
  try{
    const s = await (await fetch("/stats", {cache:"no-store"})).json();
    $("net").textContent = s.devices_seen + " machine" + (s.devices_seen > 1 ? "s" : "") +
      " · " + fmt(s.accepted_rollouts) + " calculs";
  }catch(e){}
}
const CMD = {win:"irm https://lenyay.org/install.ps1 | iex",
             nix:"curl -fsSL https://lenyay.org/install.sh | bash"};
document.querySelectorAll(".os button").forEach(b => b.onclick = () => {
  document.querySelectorAll(".os button").forEach(o => o.setAttribute("aria-selected","false"));
  b.setAttribute("aria-selected","true"); $("cmd-text").textContent = CMD[b.dataset.os];
});
$("copy").onclick = async e => {
  try{ await navigator.clipboard.writeText($("cmd-text").textContent);
    e.target.textContent = "Copié"; setTimeout(() => e.target.textContent = "Copier", 1600);
  }catch(err){ e.target.textContent = "Ctrl+C"; }
};

loadTiers(); loadAccount(); net(); setInterval(net, 15000);
</script>
</body>
</html>"""
