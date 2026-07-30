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
.aslink{background:none; border:none; padding:0; text-align:left; cursor:pointer}

/* ---- Mode application (bureau) : le chat, le compte, la FAQ — pas le site */
body.desktop .topnav, body.desktop .weblink{display:none}
#contrib{display:grid; gap:.35rem; padding:.6rem .65rem; background:var(--panel);
  border:1px solid var(--line); border-radius:10px}
.ctoggle{display:flex; align-items:center; gap:.5rem; font:inherit; font-size:.87rem;
  font-weight:600; border:none; background:none; cursor:pointer; color:var(--ink);
  padding:0}
.ctoggle i{width:.6rem; height:.6rem; border-radius:50%; background:#B9C6BE; flex:none}
.ctoggle[aria-pressed="true"] i{background:var(--verd); animation:beat 2.4s infinite}
.cstatus{margin:0; font-size:.76rem; color:var(--soft); line-height:1.35}

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
.picker button:disabled{opacity:.4; cursor:not-allowed}
.picker .price{font-size:.74rem; opacity:.75}
@media (max-width:1080px){ .picker .price{display:none} }
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
#lang-pick{font:inherit; font-size:.8rem; border:1px solid var(--line); border-radius:8px;
  background:var(--panel); color:var(--soft); padding:.3rem .35rem; cursor:pointer}
#lang-pick:hover{border-color:var(--verd); color:var(--ink)}

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
.txt .prose{white-space:pre-wrap}
.txt .prose + .codebox, .txt .codebox + .prose{margin-top:.7rem}
.codebox{border:1px solid var(--line); border-radius:10px; overflow:hidden;
  background:#1C2B26}
.codehead{display:flex; align-items:center; justify-content:space-between;
  padding:.35rem .7rem; background:#243530; color:#9DB4AB; font-size:.76rem}
.codehead button{border:none; background:none; color:#9DB4AB; cursor:pointer;
  font-size:.76rem; padding:.1rem .4rem}
.codehead button:hover{color:#fff}
.codebox pre{margin:0; padding:.8rem .9rem; overflow-x:auto; font-family:var(--mono);
  font-size:.84rem; line-height:1.55; color:#DCEBE5; white-space:pre}
.meta{font-size:.78rem; color:var(--soft); margin-top:.4rem; display:flex; gap:.5rem;
  align-items:center; flex-wrap:wrap}
.meta b{color:var(--verd-deep)}
.chip{border:1px solid var(--line); border-radius:999px; padding:.05rem .45rem;
  background:var(--panel-2)}
.fb{display:flex; align-items:center; gap:.3rem; margin-top:.45rem}
.fb button{border:1px solid var(--line); background:var(--panel); border-radius:8px;
  cursor:pointer; font-size:.9rem; line-height:1; padding:.25rem .45rem; filter:grayscale(1);
  opacity:.7; transition:all .15s}
.fb button:hover{opacity:1; filter:none; border-color:var(--verd)}
.fb button[aria-pressed="true"]{opacity:1; filter:none; border-color:var(--verd);
  background:var(--verd-pale)}
.fbhint{font-size:.78rem; color:var(--soft); margin-left:.3rem}
.regen{border:1px solid var(--line); background:var(--panel); border-radius:8px;
  cursor:pointer; font-size:.78rem; color:var(--soft); padding:.25rem .55rem;
  margin-left:.35rem; transition:all .15s}
.regen:hover{color:var(--verd-deep); border-color:var(--verd)}
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

/* ---- La zone de saisie ---- */
.composer{border-top:1px solid var(--line); background:rgba(242,246,243,.9);
  padding:.85rem 1.1rem}
.composer .inner{gap:.5rem}
.box{display:flex; gap:.5rem; align-items:flex-end; background:var(--panel);
  border:1px solid var(--line); border-radius:14px; padding:.5rem .5rem .5rem .9rem;
  box-shadow:var(--lift)}
.box:focus-within{border-color:var(--verd)}
.box textarea{flex:1; border:none; outline:none; resize:none; font:inherit;
  font-size:1rem; background:none; color:var(--ink); max-height:9rem; padding:.4rem 0}
.box button{border:none; border-radius:10px; background:var(--verd-deep); color:#fff;
  width:2.5rem; height:2.5rem; flex:none; cursor:pointer; display:grid;
  place-items:center; font-size:1.1rem; transition:background .15s}
.box button:hover:not(:disabled){background:var(--verd)}
.box button:disabled{opacity:.45; cursor:default}
.legalese{font-size:.78rem; color:var(--soft); text-align:center; margin:.55rem 0 0}

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
.consent{display:flex; gap:.55rem; align-items:flex-start; font-size:.82rem;
  color:var(--soft); margin:0 0 .9rem; cursor:pointer; line-height:1.4}
.consent input{margin-top:.15rem; flex:none; accent-color:var(--verd-deep)}
.consent:hover span{color:var(--ink)}
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
.optrow{margin:.2rem 0 1rem; padding:.7rem .8rem; background:var(--panel-2);
  border:1px solid var(--line); border-radius:9px}
details.faq{border-bottom:1px solid var(--line); padding:.45rem 0}
details.faq summary{cursor:pointer; font-weight:600; font-size:.94rem}
details.faq p{margin:.45rem 0 .2rem; font-size:.9rem; color:var(--soft)}
</style>
</head>
<body>

<div class="app">
  <aside class="side" id="side">
    <header>
      <span class="logo"><span class="seal">L</span> Lenyay</span>
    </header>
    <button class="newconv" id="new-conv" data-i18n="side.new">＋ Nouvelle conversation</button>
    <div class="threads" id="threads"></div>
    <footer>
      <button class="wallet" id="wallet">
        <span id="wallet-n">—</span> <span data-i18n="side.credits">crédits</span>
        <span class="g" id="wallet-who" data-i18n="side.account">compte</span>
      </button>
      <div id="contrib" hidden>
        <button class="ctoggle" id="ctoggle"><i></i><span data-i18n="contrib.off">Contribuer : arrêté</span></button>
        <p class="cstatus" id="cstatus" data-i18n="contrib.idle">Ta machine peut gagner
          des crédits en travaillant pour le réseau.</p>
      </div>
      <button class="sidelink aslink" id="faq-link" data-i18n="side.faq">FAQ &amp; aide</button>
      <a class="sidelink weblink" href="/decouvrir" data-i18n="side.what">Qu'est-ce que Lenyay ?</a>
      <a class="sidelink weblink" href="/dashboard" data-i18n="side.livenet">Le réseau en direct</a>
    </footer>
  </aside>

  <main class="main">
    <div class="bar">
      <button class="burger" id="burger" aria-label="Fils">☰</button>
      <div class="picker" id="picker"></div>
      <nav class="topnav">
        <a href="/decouvrir" data-i18n="nav.discover">Découvrir</a>
        <a href="/decouvrir#nuit" class="opt" data-i18n="nav.how">Comment ça marche</a>
        <a href="/decouvrir#participer" class="opt" data-i18n="nav.join">Participer</a>
        <a href="/dashboard" class="opt" data-i18n="nav.network">Le réseau</a>
      </nav>
      <span class="netstate"><i></i><span id="net" data-i18n="net.live">réseau</span></span>
      <select id="lang-pick" aria-label="Langue">
        <option value="fr">FR</option><option value="en">EN</option>
        <option value="es">ES</option><option value="de">DE</option>
        <option value="pt">PT</option><option value="it">IT</option>
      </select>
      <button class="signin" id="signin" data-i18n="nav.signin">Se connecter</button>
    </div>

    <div class="stream" id="stream">
      <div class="inner" id="turns"></div>
    </div>

    <div class="composer">
      <div class="inner">
        <div class="box">
          <textarea id="q" rows="1" placeholder="Écris ton message…"
            data-i18n-ph="composer.ph"></textarea>
          <button id="send" aria-label="Envoyer">↑</button>
        </div>
        <p class="legalese" data-i18n="composer.legal">Ta question est lue par la machine
          d'un autre membre — n'y mets rien de confidentiel.</p>
      </div>
    </div>
  </main>
</div>

<dialog id="dlg"><div class="dlg" id="dlg-body"></div></dialog>

<script>
const $ = id => document.getElementById(id);

/* ---------- Langues ---------- */
/* Six langues embarquées ; le HTML reste en français par défaut et
   applyI18n() applique la langue choisie (mémorisée, sinon celle du
   navigateur, sinon l'anglais). */
const I18N = __I18N__;
const LOCALES = {fr:"fr-FR", en:"en-US", es:"es-ES", de:"de-DE", pt:"pt-PT", it:"it-IT"};
let LANG = localStorage.getItem("lenyay.lang")
  || ((navigator.language || "en").slice(0, 2));
if(!I18N[LANG]) LANG = "en";
const t = k => (I18N[LANG] && I18N[LANG][k]) || I18N.fr[k] || k;
const tf = (k, vars) => Object.entries(vars).reduce(
  (s, [name, v]) => s.replaceAll("{" + name + "}", v), t(k));
function applyI18n(){
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach(el =>
    el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-ph]").forEach(el =>
    el.placeholder = t(el.dataset.i18nPh));
  const pick = $("lang-pick"); if(pick) pick.value = LANG;
}
const fmt = n => Number(n).toLocaleString(LOCALES[LANG] || "fr-FR");
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
  tiers = d.tiers;
  // On ne propose jamais un modèle qu'aucune machine ne peut servir.
  const first = tiers.find(x => x.online > 0);
  tier = (tiers.find(x => x.id === d.default && x.online > 0) || first || {id:d.default}).id;
  $("picker").innerHTML = tiers.map(x => {
    const off = x.online === 0;
    return `<button data-t="${x.id}" aria-pressed="${x.id === tier}" ${off ? "disabled" : ""}
       title="${esc(x.model)} — ${off ? esc(t("tier.offline")) : esc(x.about)}">
       ${esc(x.label)} <span class="price">${esc(x.model)} · ${x.cost} cr.</span></button>`;
  }).join("");
  $("picker").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => {
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
  // Application de bureau : la machine se rattache au compte toute seule.
  if(window.pywebview && account.key){
    try{ window.pywebview.api.set_account_key(account.key); }catch(e){}
  }
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
      <button data-m="login" aria-selected="${login}">${esc(t("auth.login"))}</button>
      <button data-m="register" aria-selected="${!login}">${esc(t("auth.register"))}</button>
    </div>
    ${login ? "" : `<label class="field">${esc(t("auth.handle"))}
      <input id="a-handle" maxlength="40" placeholder="${esc(t("auth.handle.ph"))}"></label>`}
    <label class="field">${esc(t("auth.email"))}
      <input id="a-email" type="email" autocomplete="email" placeholder="toi@exemple.fr"></label>
    <label class="field">${esc(t("auth.pass"))}
      <input id="a-pass" type="password" autocomplete="${login ? "current-password" : "new-password"}"
        placeholder="${login ? "" : esc(t("auth.pass.ph"))}"></label>
    <p class="autherr" id="a-err"></p>
    ${login ? "" : `<label class="consent"><input type="checkbox" id="a-learn">
      <span>${esc(t("auth.consent"))}</span></label>`}
    <button class="go" id="a-go">${esc(t(login ? "auth.go.login" : "auth.go.register"))}</button>
    ${login ? "" : `<p class="authnote">${esc(t("auth.note"))}</p>`}`;
  $("dlg-body").querySelectorAll(".authtabs button").forEach(b =>
    b.onclick = () => authForm(b.dataset.m));
  $("a-go").onclick = async () => {
    const email = $("a-email").value.trim(), password = $("a-pass").value;
    const body = login ? {email, password}
      : {email, password, handle: ($("a-handle").value || "anonyme").trim(),
         learn_opt_in: $("a-learn") ? $("a-learn").checked : false};
    const r = await fetch(login ? "/auth/login" : "/auth/register", {
      method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
    if(!r.ok){
      const d = await r.json().catch(() => ({}));
      $("a-err").textContent = typeof d.detail === "string" ? d.detail
        : t(login ? "auth.err.login" : "auth.err.register");
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
  $("wallet-n").textContent = "—"; $("wallet-who").textContent = t("side.account");
  $("threads").innerHTML = ""; $("dlg").close(); blank();
}
$("signin").onclick = () => { authForm("login"); $("dlg").showModal(); };
/* ---------- Le compte : solde, gains, dépenses, machines ---------- */
const KINDS = {
  daily: "🌱", welcome: "🎁", solved: "🧮", served: "💬",
  question: "✳️", subscription: "💳", adjust: "•",
};
const when = iso => {
  const d = new Date(iso);
  const loc = LOCALES[LANG] || "fr-FR";
  return isNaN(d) ? "" : d.toLocaleDateString(loc, {day:"2-digit", month:"short"}) +
    " " + d.toLocaleTimeString(loc, {hour:"2-digit", minute:"2-digit"});
};
function lines(entries){
  if(!entries.length) return `<p class="empty">${esc(t("acct.empty"))}</p>`;
  return `<ul class="ledger">` + entries.map(e => {
    const icon = KINDS[e.kind] || KINDS.adjust;
    const fallback = t("kind." + (KINDS[e.kind] ? e.kind : "adjust"));
    // le libellé serveur est en français ; hors français, la clé locale prime
    const label = LANG === "fr" ? (e.label || fallback) : fallback;
    return `<li>
      <span class="ic">${icon}</span>
      <span class="what"><b>${esc(label)}</b>
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
        `<li><b>${esc(d.device_name)}</b><span>${fmt(d.credits||0)} ${esc(t("acct.produced"))}</span></li>`).join("")}</ul>`
    : `<p class="empty">${esc(t("acct.nodevice"))}</p>`;

  $("dlg-body").innerHTML = `
    <div class="acct-head">
      <div>
        <h3>${esc(me.handle)}</h3>
        <p class="sub">${esc(me.email || "Lenyay")}</p>
      </div>
      <div class="bal-big"><b>${fmt(me.credits)}</b><span>${esc(t("side.credits"))}</span></div>
    </div>
    <div class="totals">
      <div><b class="up">+${fmt(led.summary.earned)}</b><span>${esc(t("acct.earned"))}</span></div>
      <div><b class="down">−${fmt(led.summary.spent)}</b><span>${esc(t("acct.spent"))}</span></div>
      <div><b>${me.devices.length}</b><span>${esc(t("acct.machines"))}</span></div>
    </div>
    <div class="tabs" id="acct-tabs">
      <button data-t="solde">${esc(t("acct.tab.devices"))}</button>
      <button data-t="gains">${esc(t("acct.tab.earned"))}</button>
      <button data-t="depenses">${esc(t("acct.tab.billing"))}</button>
      <button data-t="cle">${esc(t("acct.tab.key"))}</button>
    </div>
    <div class="tabbody" id="acct-body"></div>
    <button class="go" onclick="document.getElementById('dlg').close()">${esc(t("acct.close"))}</button>
    <button class="leave" id="do-logout">${esc(t("acct.logout"))}</button>`;

  const views = {
    solde: devices,
    gains: lines(gains),
    depenses: depenses.length
      ? lines(depenses) + `<p class="empty">${esc(t("acct.nobilling"))}</p>`
      : `<p class="empty">${esc(t("acct.nospend"))}</p>`,
    cle: `
       <label class="consent optrow">
         <input type="checkbox" id="opt-learn" ${me.learn_opt_in ? "checked" : ""}>
         <span>${esc(t("acct.optlearn"))}</span>
       </label>
       <p class="empty">${esc(t("acct.keyinfo"))}</p>
       <div class="key">${account.key}</div>`,
  };
  const show = which => {
    $("acct-body").innerHTML = views[which];
    $("acct-tabs").querySelectorAll("button").forEach(b =>
      b.setAttribute("aria-selected", b.dataset.t === which));
  };
  $("acct-tabs").querySelectorAll("button").forEach(b => b.onclick = () => show(b.dataset.t));
  $("do-logout").onclick = logout;
  show(tab);
  // Délégué : le sélecteur de consentement n'existe que dans l'onglet « clé ».
  $("acct-body").addEventListener("change", async e => {
    if(e.target.id !== "opt-learn") return;
    await api("/accounts/consent", {method:"POST",
      body: JSON.stringify({opt_in: e.target.checked})});
    account.learn_opt_in = e.target.checked; me.learn_opt_in = e.target.checked;
  });
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
    || `<p style="padding:.6rem;color:var(--soft);font-size:.88rem">${esc(t("side.empty"))}</p>`;
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
    <h1>${esc(t("hero.title"))}</h1>
    <p>${esc(t("hero.sub"))}
      <a class="learn" href="/decouvrir">${esc(t("hero.learn"))}</a></p>
    <div class="samples">
      <button>${esc(t("hero.s1"))}</button>
      <button>${esc(t("hero.s2"))}</button>
      <button>${esc(t("hero.s3"))}</button>
    </div>
  </div>`;
  document.querySelectorAll(".samples button").forEach(b =>
    b.onclick = () => send(b.textContent.trim()));
}
async function openThread(id){
  conv = id;
  const d = await (await api("/conversations/" + id)).json();
  $("turns").innerHTML = "";
  const lastAi = [...d.messages].reverse().find(m => m.role === "assistant");
  d.messages.forEach(m => addTurn(m.role === "user" ? "me" : "ai", m.content,
    m.role === "assistant"
      ? {...m, message_id: m.id, can_regen: lastAi && m.id === lastAi.id} : null));
  loadThreads(); scroll();
}
/* Les réponses code arrivent en blocs ``` : on les rend dans des <pre>
   copiables. Tout passe par textContent — jamais d'HTML venu du modèle. */
function renderRich(container, text){
  const parts = String(text).split(/```([a-zA-Z]*)\n?/);
  // découpage : [texte, langue, code, texte, langue, code, ...]
  for(let i = 0; i < parts.length; i++){
    if(i % 3 === 0){
      if(parts[i].trim()){
        const p = document.createElement("div");
        p.className = "prose"; p.textContent = parts[i].trim();
        container.append(p);
      }
    } else if(i % 3 === 1){
      const lang = parts[i], code = parts[i + 1] ?? ""; i++;
      const box = document.createElement("div"); box.className = "codebox";
      const head = document.createElement("div"); head.className = "codehead";
      const lab = document.createElement("span"); lab.textContent = lang || "code";
      const cp = document.createElement("button"); cp.type = "button";
      cp.textContent = t("copy");
      cp.onclick = async () => {
        try{ await navigator.clipboard.writeText(code); cp.textContent = t("copied");
          setTimeout(() => cp.textContent = t("copy"), 1500); }catch(e){}
      };
      head.append(lab, cp);
      const pre = document.createElement("pre"); pre.textContent = code.replace(/\n$/, "");
      box.append(head, pre); container.append(box);
    }
  }
}
function feedbackBar(messageId, current){
  const bar = document.createElement("div");
  bar.className = "fb";
  const mk = (rating, glyph) => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = glyph; b.dataset.r = rating;
    b.setAttribute("aria-pressed", current === rating);
    b.onclick = async () => {
      const r = await api(`/messages/${messageId}/feedback`,
        {method:"POST", body: JSON.stringify({rating})});
      if(r.ok){
        bar.querySelectorAll("button").forEach(o =>
          o.setAttribute("aria-pressed", o.dataset.r === rating));
        hint.textContent = rating === "up" ? t("fb.thanks") : t("fb.noted");
      }
    };
    return b;
  };
  const hint = document.createElement("span"); hint.className = "fbhint";
  bar.append(mk("up", "👍"), mk("down", "👎"), hint);
  return bar;
}
function addTurn(kind, text, meta){
  const el = document.createElement("div");
  el.className = "turn " + kind;
  el.innerHTML = `<div class="who">${kind === "me" ? esc(t("turn.you")) : "IA"}</div>
    <div class="body"><div class="txt"></div></div>`;
  const txt = el.querySelector(".txt");
  if(kind === "ai" && String(text).includes("```")){ renderRich(txt, text); }
  else { txt.textContent = text; }
  if(meta){
    const m = document.createElement("p");
    m.className = "meta";
    m.innerHTML = `${esc(t("turn.by"))} <b>${esc(meta.device_name || t("turn.machine"))}</b>` +
      (meta.tier ? ` <span class="chip">${esc(meta.tier)}</span>` : "");
    el.querySelector(".body").append(m);
    // On ne peut noter que ses propres messages IA identifiés.
    if(meta.message_id){
      const bar = feedbackBar(meta.message_id, meta.rating);
      if(meta.can_regen){
        // Un seul bouton Régénérer à la fois : sur la dernière réponse.
        document.querySelectorAll(".regen").forEach(b => b.remove());
        const rg = document.createElement("button");
        rg.type = "button"; rg.className = "regen";
        const current = tiers.find(x => x.id === tier);
        rg.textContent = t("turn.regen");
        rg.title = tf("turn.regen.tip", {c: current ? current.cost : "?"});
        rg.onclick = regenerate;
        bar.append(rg);
      }
      el.querySelector(".body").append(bar);
    }
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
  if(!r.ok){ addTurn("ai", t("turn.fail")); $("send").disabled = false; return; }
  const asked = await r.json();
  account.credits = asked.credits_left; paintWallet(); loadThreads();

  pollAnswer(asked.question_id);
}

/* Suivre une question jusqu'à sa réponse (envoi initial comme régénération). */
function pollAnswer(questionId){
  const pending = addTurn("ai", "");
  pending.querySelector(".txt").innerHTML =
    `<span class="dots">${esc(t("turn.waiting"))} <span></span><span></span><span></span></span>`;
  let tries = 0;
  clearInterval(polling);
  polling = setInterval(async () => {
    tries++;
    try{
      const s = await (await fetch("/ask/" + questionId)).json();
      if(s.status === "serving"){
        pending.querySelector(".txt").innerHTML =
          `<span class="dots">${esc(tf("turn.writing", {d: s.device_name || t("turn.machine")}))} <span></span><span></span><span></span></span>`;
      }
      if(s.status === "done"){
        clearInterval(polling); pending.remove();
        addTurn("ai", s.answer, {device_name:s.device_name, tier,
                                 message_id:s.message_id, can_regen:true});
        $("send").disabled = false;
      }
      if(tries > 120){
        clearInterval(polling); pending.querySelector(".txt").textContent =
          t("turn.none");
        $("send").disabled = false;
      }
    }catch(e){}
  }, 2000);
}

/* Reposer la même question : nouvelle machine, nouveau tirage — et le même
   prix qu'une question, car l'ordinateur d'un membre refait un vrai travail. */
async function regenerate(){
  if(!conv) return;
  $("send").disabled = true;
  const r = await api(`/conversations/${conv}/regenerate`, {method:"POST",
    body: JSON.stringify({tier})});
  if(r.status === 402){
    outOfCredits((await r.json()).detail); $("send").disabled = false; return;
  }
  if(!r.ok){ $("send").disabled = false; return; }
  const asked = await r.json();
  account.credits = asked.credits_left; paintWallet();
  pollAnswer(asked.question_id);
}
function outOfCredits(detail){
  // le detail serveur est en français : hors français, le résumé local suffit
  $("dlg-body").innerHTML = `<h3>${esc(t("wall.title"))}</h3>
    ${LANG === "fr" && detail ? `<p>${esc(detail)}</p>` : ""}
    <ul>
      <li>${esc(t("wall.tomorrow"))}</li>
      <li>${esc(t("wall.contribute"))}</li>
      <li>${esc(t("wall.subscribe"))}</li>
    </ul>
    <button class="go" onclick="document.getElementById('dlg').close();location.href='/decouvrir#participer'">
      ${esc(t("wall.cta"))}</button>`;
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
    $("net").textContent = tf("net.stats",
      {d: fmt(s.devices_seen), c: fmt(s.accepted_rollouts)});
  }catch(e){}
}
// L'accueil s'affiche AVANT tout appel réseau : même hors ligne, le visiteur
// doit comprendre où il est tombé et comment le réseau fonctionne.
applyI18n();
blank();
/* ---------- FAQ (web et application) ---------- */
$("faq-link").onclick = () => {
  let html = `<h3>${esc(t("faq.title"))}</h3>`;
  for(let i = 1; i <= 7; i++){
    html += `<details class="faq"><summary>${esc(t("faq.q" + i))}</summary>
      <p>${esc(t("faq.a" + i))}</p></details>`;
  }
  html += `<button class="go" onclick="document.getElementById('dlg').close()">${esc(t("acct.close"))}</button>`;
  $("dlg-body").innerHTML = html;
  $("dlg").showModal();
};

/* ---------- Choix de la langue ---------- */
$("lang-pick").onchange = e => {
  localStorage.setItem("lenyay.lang", e.target.value);
  location.reload();   // simple et sûr : tout se réaffiche dans la langue choisie
};

/* ---------- Mode application (bureau) ---------- */
/* La coquille pywebview injecte window.pywebview : on masque le site, on
   branche l'interrupteur Contribuer sur le worker local. */
let deskTimer = null;
async function paintContrib(){
  try{
    const s = await window.pywebview.api.status();
    $("ctoggle").setAttribute("aria-pressed", s.running);
    $("ctoggle").querySelector("span").textContent =
      s.running ? t("contrib.on") : t("contrib.off");
    $("cstatus").textContent = s.running
      ? (s.detail || t("contrib.busy"))
      : t("contrib.idle");
  }catch(e){}
}
function setupDesktop(){
  if(!window.pywebview) return;
  document.body.classList.add("desktop");
  $("contrib").hidden = false;
  $("ctoggle").onclick = async () => {
    const s = await window.pywebview.api.status();
    if(s.running){ await window.pywebview.api.stop_contribute(); }
    else{
      if(account && account.key) await window.pywebview.api.set_account_key(account.key);
      await window.pywebview.api.start_contribute();
    }
    paintContrib();
  };
  clearInterval(deskTimer); deskTimer = setInterval(paintContrib, 5000);
  paintContrib();
}
window.addEventListener("pywebviewready", setupDesktop);
if(window.pywebview) setupDesktop();

loadTiers(); loadAccount(); net(); setInterval(net, 15000);
</script>
</body>
</html>"""

# Injection du dictionnaire : six langues embarquées dans la page, aucune
# requête supplémentaire, et le test de complétude interdit les trous.
import json as _json  # noqa: E402

from coordinator.i18n import bundle as _i18n_bundle  # noqa: E402

LANDING_HTML = LANDING_HTML.replace(
    "__I18N__", _json.dumps(_i18n_bundle(), ensure_ascii=False))
