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
.topnav{margin-left:auto; display:flex; gap:1.05rem; font-size:.88rem}
.topnav a{color:var(--soft); text-decoration:none}
.topnav a:hover{color:var(--verd-deep); text-decoration:underline; text-underline-offset:4px}
.topnav ~ .netstate{margin-left:0}
@media (max-width:860px){ .topnav a.opt{display:none} }
.signin{font:inherit; font-size:.86rem; font-weight:600; border:1.5px solid var(--line);
  background:var(--panel); color:var(--ink); border-radius:9px; padding:.4rem .85rem;
  cursor:pointer}
.signin:hover{border-color:var(--verd)}
.signin[hidden]{display:none}

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

.welcome{text-align:center; padding:1.6rem 0 .5rem}
.welcome h1{font-size:clamp(1.5rem,3.2vw,2rem); letter-spacing:-.025em; margin:0 0 .4rem}
.welcome p{color:var(--soft); margin:0 auto; max-width:46ch}
.samples{display:flex; gap:.5rem; flex-wrap:wrap; justify-content:center; margin-top:1.2rem}
.samples button{background:var(--panel); border:1px solid var(--line); border-radius:999px;
  padding:.45rem .9rem; font-size:.88rem; color:var(--soft); cursor:pointer}
.samples button:hover{border-color:var(--verd); color:var(--verd-deep)}
.learn{display:inline-block; margin-top:.4rem; color:var(--verd-deep); font-weight:600;
  text-decoration:none; border-bottom:1.5px solid var(--verd)}
.learn:hover{color:var(--verd)}

/* ---- Connexion ---- */
.authtabs{display:flex; gap:.3rem; background:var(--panel-2); border:1px solid var(--line);
  border-radius:10px; padding:.25rem; margin-bottom:1.1rem}
.authtabs button{flex:1; border:none; background:none; cursor:pointer; padding:.5rem;
  border-radius:8px; font-size:.9rem; color:var(--soft)}
.authtabs button[aria-selected="true"]{background:var(--panel); color:var(--ink);
  font-weight:600; box-shadow:0 1px 3px rgba(30,43,39,.12)}
.field{display:block; font-size:.85rem; font-weight:600; color:var(--soft);
  margin-bottom:.75rem}
.field input{display:block; width:100%; margin-top:.3rem; font:inherit; font-size:.98rem;
  font-weight:400; padding:.62rem .75rem; border:1px solid var(--line); border-radius:9px;
  background:#fff; color:var(--ink)}
.field input:focus{outline:2px solid var(--verd); outline-offset:-1px}
.autherr{min-height:1.1rem; margin:.1rem 0 .3rem; font-size:.85rem; color:#B4541E}
.authnote{margin:.7rem 0 0; font-size:.82rem; color:var(--soft)}
.leave{margin-top:.55rem; width:100%; padding:.6rem; font-size:.88rem; border-radius:9px;
  border:1px solid var(--line); background:none; color:var(--soft); cursor:pointer}
.leave:hover{color:#B4541E; border-color:#E0BFA8}

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

/* ---- Le compte ---- */
dialog#dlg{max-width:34rem}
.acct-head{display:flex; align-items:flex-start; gap:1rem; margin-bottom:1rem}
.acct-head h3{margin:0}
.acct-head .sub{margin:.15rem 0 0; font-size:.83rem; color:var(--soft)}
.bal-big{margin-left:auto; text-align:right; line-height:1.05}
.bal-big b{font-size:1.9rem; color:var(--verd-deep); font-variant-numeric:tabular-nums}
.bal-big span{display:block; font-size:.76rem; color:var(--soft)}
.totals{display:grid; grid-template-columns:repeat(3,1fr); gap:.5rem; margin-bottom:1rem}
.totals div{background:var(--panel-2); border:1px solid var(--line); border-radius:9px;
  padding:.55rem .6rem; text-align:center}
.totals b{display:block; font-size:1.02rem; font-variant-numeric:tabular-nums}
.totals span{font-size:.74rem; color:var(--soft)}
.up{color:var(--verd-deep)} .down{color:var(--amber)}
.tabs{display:flex; gap:.25rem; border-bottom:1px solid var(--line); margin-bottom:.7rem;
  overflow-x:auto}
.tabs button{background:none; border:none; cursor:pointer; padding:.45rem .6rem;
  font-size:.85rem; color:var(--soft); border-bottom:2px solid transparent; white-space:nowrap}
.tabs button[aria-selected="true"]{color:var(--ink); border-color:var(--verd); font-weight:600}
.tabbody{max-height:15rem; overflow-y:auto; margin-bottom:.4rem}
.ledger{margin:0; padding:0; list-style:none; display:grid; gap:.1rem}
.ledger li{display:grid; grid-template-columns:1.5rem 1fr auto auto; gap:.55rem;
  align-items:center; padding:.45rem .2rem; border-bottom:1px solid var(--line)}
.ledger .ic{text-align:center; font-size:.9rem}
.ledger .what{display:flex; flex-direction:column; min-width:0}
.ledger .what b{font-size:.88rem; font-weight:600; overflow:hidden; text-overflow:ellipsis;
  white-space:nowrap}
.ledger .what em{font-style:normal; font-size:.76rem; color:var(--soft)}
.ledger .what time{font-size:.72rem; color:var(--soft)}
.ledger .amt{font-variant-numeric:tabular-nums; font-weight:700; font-size:.9rem}
.ledger .bal{font-variant-numeric:tabular-nums; font-size:.78rem; color:var(--soft);
  min-width:2.4rem; text-align:right}
.devs{margin:0; padding:0; list-style:none; display:grid; gap:.4rem}
.devs li{display:flex; justify-content:space-between; gap:.6rem; padding:.5rem .65rem;
  background:var(--panel-2); border:1px solid var(--line); border-radius:9px; font-size:.9rem}
.devs span{color:var(--soft); font-size:.82rem}
.empty{font-size:.86rem; color:var(--soft); margin:.6rem 0 0}
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
      <a class="sidelink" href="/decouvrir">Qu'est-ce que Lenyay ?</a>
      <a class="sidelink" href="/dashboard">Le réseau en direct</a>
    </footer>
  </aside>

  <main class="main">
    <div class="bar">
      <button class="burger" id="burger" aria-label="Fils">☰</button>
      <div class="picker" id="picker"></div>
      <nav class="topnav">
        <a href="/decouvrir">Découvrir</a>
        <a href="/decouvrir#nuit" class="opt">Comment ça marche</a>
        <a href="/decouvrir#participer" class="opt">Participer</a>
        <a href="/dashboard" class="opt">Le réseau</a>
      </nav>
      <span class="netstate"><i></i><span id="net">réseau</span></span>
      <button class="signin" id="signin">Se connecter</button>
    </div>

    <div class="stream" id="stream">
      <div class="inner" id="turns"></div>
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

<dialog id="dlg"><div class="dlg" id="dlg-body"></div></dialog>

<script>
const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString("fr-FR");
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
    `<button data-t="${t.id}" aria-pressed="${t.id === tier}"
       title="${esc(t.model)} — ${esc(t.about)}">
       ${esc(t.label)} <span class="price">${esc(t.model)} · ${t.cost} cr.</span></button>`).join("");
  $("picker").querySelectorAll("button").forEach(b => b.onclick = () => {
    tier = b.dataset.t;
    $("picker").querySelectorAll("button").forEach(o =>
      o.setAttribute("aria-pressed", o.dataset.t === tier));
  });
}

/* ---------- Compte : session par cookie, e-mail + mot de passe ---------- */
async function loadAccount(){
  const r = await fetch("/accounts/me");     // le cookie de session suffit
  if(!r.ok) return;
  account = await r.json(); account.key = account.account_key;
  paintWallet(); loadThreads();
}
function paintWallet(){
  if(!account) return;
  $("wallet-n").innerHTML = "<b>" + fmt(account.credits) + "</b>";
  $("wallet-who").textContent = account.handle;
  $("signin").hidden = true;
}
function authForm(mode){
  const login = mode === "login";
  $("dlg-body").innerHTML = `
    <div class="authtabs">
      <button data-m="login" aria-selected="${login}">Se connecter</button>
      <button data-m="register" aria-selected="${!login}">Créer un compte</button>
    </div>
    ${login ? "" : `<label class="field">Pseudo
      <input id="a-handle" maxlength="40" placeholder="visible sur le tableau de bord"></label>`}
    <label class="field">E-mail
      <input id="a-email" type="email" autocomplete="email" placeholder="toi@exemple.fr"></label>
    <label class="field">Mot de passe
      <input id="a-pass" type="password" autocomplete="${login ? "current-password" : "new-password"}"
        placeholder="${login ? "" : "8 caractères minimum"}"></label>
    <p class="autherr" id="a-err"></p>
    <button class="go" id="a-go">${login ? "Se connecter" : "Créer mon compte — 20 crédits offerts"}</button>
    ${login ? "" : `<p class="authnote">Pas de carte bancaire, pas de newsletter. L'e-mail ne
      sert qu'à retrouver ton compte.</p>`}`;
  $("dlg-body").querySelectorAll(".authtabs button").forEach(b =>
    b.onclick = () => authForm(b.dataset.m));
  $("a-go").onclick = async () => {
    const email = $("a-email").value.trim(), password = $("a-pass").value;
    const body = login ? {email, password}
      : {email, password, handle: ($("a-handle").value || "anonyme").trim()};
    const r = await fetch(login ? "/auth/login" : "/auth/register", {
      method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
    if(!r.ok){
      const d = await r.json().catch(() => ({}));
      $("a-err").textContent = typeof d.detail === "string" ? d.detail
        : (login ? "Connexion impossible." : "Vérifie l'e-mail et le mot de passe (8 caractères min).");
      return;
    }
    await loadAccount();
    $("dlg").close();
    if(window._authResolve){ window._authResolve(true); window._authResolve = null; }
  };
  $("a-pass").addEventListener("keydown", e => { if(e.key === "Enter") $("a-go").click(); });
}
async function ensureAccount(){
  if(account) return true;
  return new Promise(resolve => {
    window._authResolve = resolve;
    authForm("register");
    $("dlg").showModal();
    $("dlg").addEventListener("close", () => {
      if(window._authResolve){ window._authResolve(false); window._authResolve = null; }
    }, {once:true});
  });
}
async function logout(){
  await fetch("/auth/logout", {method:"POST"});
  account = null; conv = null;
  $("signin").hidden = false;
  $("wallet-n").textContent = "—"; $("wallet-who").textContent = "compte";
  $("threads").innerHTML = ""; $("dlg").close(); blank();
}
$("signin").onclick = () => { authForm("login"); $("dlg").showModal(); };
/* ---------- Le compte : solde, gains, dépenses, machines ---------- */
const KINDS = {
  daily:    ["🌱", "Recharge quotidienne"],
  welcome:  ["🎁", "Bienvenue"],
  solved:   ["🧮", "Calculs"],
  served:   ["💬", "Réponse servie"],
  question: ["✳️", "Question"],
  subscription: ["💳", "Abonnement"],
  adjust:   ["•", "Ajustement"],
};
const when = iso => {
  const d = new Date(iso);
  return isNaN(d) ? "" : d.toLocaleDateString("fr-FR", {day:"2-digit", month:"short"}) +
    " " + d.toLocaleTimeString("fr-FR", {hour:"2-digit", minute:"2-digit"});
};
function lines(entries){
  if(!entries.length) return `<p class="empty">Rien pour l'instant.</p>`;
  return `<ul class="ledger">` + entries.map(e => {
    const [icon, fallback] = KINDS[e.kind] || KINDS.adjust;
    return `<li>
      <span class="ic">${icon}</span>
      <span class="what"><b>${esc(e.label || fallback)}</b>
        ${e.device_name ? `<em>${esc(e.device_name)}</em>` : ""}
        <time>${when(e.created_at)}</time></span>
      <span class="amt ${e.amount >= 0 ? "up" : "down"}">${e.amount >= 0 ? "+" : ""}${fmt(e.amount)}</span>
      <span class="bal">${fmt(e.balance_after)}</span>
    </li>`;
  }).join("") + `</ul>`;
}
async function openAccount(tab = "solde"){
  if(!account) return ensureAccount();
  const [me, led] = await Promise.all([
    (await api("/accounts/me")).json(),
    (await api("/accounts/ledger")).json(),
  ]);
  account = {...me, key:account.key}; paintWallet();
  const gains = led.entries.filter(e => e.amount > 0);
  const depenses = led.entries.filter(e => e.amount < 0);
  const devices = me.devices.length
    ? `<ul class="devs">${me.devices.map(d =>
        `<li><b>${esc(d.device_name)}</b><span>${fmt(d.credits||0)} crédits produits</span></li>`).join("")}</ul>`
    : `<p class="empty">Aucune machine rattachée. Installe Lenyay et rattache-la :
       tes nuits deviennent des crédits.</p>`;

  $("dlg-body").innerHTML = `
    <div class="acct-head">
      <div>
        <h3>${esc(me.handle)}</h3>
        <p class="sub">${esc(me.email || "Compte Lenyay")}</p>
      </div>
      <div class="bal-big"><b>${fmt(me.credits)}</b><span>crédits</span></div>
    </div>
    <div class="totals">
      <div><b class="up">+${fmt(led.summary.earned)}</b><span>gagnés</span></div>
      <div><b class="down">−${fmt(led.summary.spent)}</b><span>dépensés</span></div>
      <div><b>${me.devices.length}</b><span>machine${me.devices.length > 1 ? "s" : ""}</span></div>
    </div>
    <div class="tabs" id="acct-tabs">
      <button data-t="solde">Machines</button>
      <button data-t="gains">Crédits gagnés</button>
      <button data-t="depenses">Facturation</button>
      <button data-t="cle">Mes machines & clé</button>
    </div>
    <div class="tabbody" id="acct-body"></div>
    <button class="go" onclick="document.getElementById('dlg').close()">Fermer</button>
    <button class="leave" id="do-logout">Se déconnecter</button>`;

  const views = {
    solde: devices,
    gains: lines(gains),
    depenses: depenses.length
      ? lines(depenses) + `<p class="empty">Aucun paiement : Lenyay ne facture pas
         d'argent. L'abonnement arrivera pour ceux qui préfèrent ne pas contribuer.</p>`
      : `<p class="empty">Aucune dépense pour l'instant.</p>`,
    cle: `<p class="empty">Cette clé rattache une machine à ton compte : lance le worker
       avec <code>LENYAY_ACCOUNT_KEY</code> et ses gains alimenteront ta bourse. Ce n'est
       pas un mot de passe — ton identité, c'est ton e-mail.</p>
       <div class="key">${account.key}</div>`,
  };
  const show = t => {
    $("acct-body").innerHTML = views[t];
    $("acct-tabs").querySelectorAll("button").forEach(b =>
      b.setAttribute("aria-selected", b.dataset.t === t));
  };
  $("acct-tabs").querySelectorAll("button").forEach(b => b.onclick = () => show(b.dataset.t));
  $("do-logout").onclick = logout;
  show(tab);
  $("dlg").showModal();
}
$("wallet").onclick = () => openAccount("solde");

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
/* L'accueil : on montre le cycle plutôt que de le raconter. Sans lui, on n'a
   qu'un chatbot de plus — et personne ne comprend pourquoi prêter sa machine. */
/* L'accueil reste nu : le chat d'abord. L'explication complète vit sur
   /decouvrir, liée en haut de page et ici. */
function blank(){
  $("turns").innerHTML = `
  <div class="welcome">
    <h1>Pose ta question au réseau.</h1>
    <p>Elle sera traitée par l'ordinateur d'un membre — pas par un datacenter.
      <a class="learn" href="/decouvrir">Comprendre comment ça marche&nbsp;→</a></p>
    <div class="samples">
      <button>Explique-moi la photosynthèse simplement</button>
      <button>Écris un mot d'excuse à mon voisin</button>
      <button>Combien font 17 % de 340 ?</button>
    </div>
  </div>`;
  document.querySelectorAll(".samples button").forEach(b =>
    b.onclick = () => send(b.textContent.trim()));
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
  $("dlg-body").innerHTML = `<h3>Plus de crédits pour aujourd'hui</h3>
    <p>${esc(detail)}</p>
    <ul>
      <li><b>Demain</b> — ton solde remonte automatiquement : de quoi quelques
        questions simples chaque jour.</li>
      <li><b>Contribuer</b> — laisse Lenyay tourner : chaque calcul vérifié te
        recrédite, sans limite.</li>
      <li><b>S'abonner</b> — bientôt, un petit abonnement pour utiliser sans
        contribuer.</li>
    </ul>
    <button class="go" onclick="document.getElementById('dlg').close();location.href='/decouvrir#participer'">
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

// L'accueil s'affiche AVANT tout appel réseau : même hors ligne, le visiteur
// doit comprendre où il est tombé et comment le réseau fonctionne.
blank();
loadTiers(); loadAccount(); net(); setInterval(net, 15000);
</script>
</body>
</html>"""
