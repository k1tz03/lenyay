"""La page « Découvrir » — tout ce qui explique Lenyay, hors du chat.

Le chat reste une application nue ; ici on raconte. Le fil conducteur est le
cycle jour/nuit : le jour, tu poses des questions ; la nuit, ta machine
travaille et te recrédite. La page bascule littéralement du clair au sombre
au moment où l'on passe à la nuit — la forme raconte le fond.

Les deux scènes principales sont des SVG animés (animateMotion), sans une
ligne de JavaScript d'animation : self-contained, léger, et gelé proprement
par prefers-reduced-motion.
"""

ABOUT_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Découvrir Lenyay — une IA sans datacenter</title>
<meta name="description" content="Le jour tu poses tes questions, la nuit ta machine travaille. Comment fonctionne une IA servie par ses membres, sans datacenter.">
<meta name="color-scheme" content="light">
<style>
@font-face{font-family:"Familjen"; font-style:normal; font-weight:400 700;
  font-display:swap; src:url("/static/fonts/familjen-latin.woff2") format("woff2")}
:root{
  --paper:#F2F6F3; --panel:#FFFFFF; --panel-2:#F7FAF8;
  --verd:#3F8C79; --verd-deep:#245247; --verd-pale:#DCEBE5; --line:#CFE0D8;
  --ink:#1E2B27; --soft:#5F7069;
  --night:#152420; --night-2:#1C2F29; --night-line:#2E4A41; --night-ink:#DCEBE5;
  --night-soft:#8FA69D; --amber:#C97F1E; --amber-soft:#E8B45A; --amber-pale:#F7EAD3;
  --ui:"Familjen","Avenir Next",system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace;
  --lift:0 1px 2px rgba(30,43,39,.05), 0 12px 32px -16px rgba(36,82,71,.3);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0; background:var(--paper); color:var(--ink); font-family:var(--ui);
  font-size:17px; line-height:1.65; -webkit-font-smoothing:antialiased}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *{animation:none !important; transition:none !important}
}
.wrap{max-width:1060px; margin:0 auto; padding:0 clamp(1.1rem,3.6vw,2rem)}
a{color:inherit}

/* ---- Barre ---- */
header.top{position:sticky; top:0; z-index:40; backdrop-filter:blur(10px);
  background:rgba(242,246,243,.85); border-bottom:1px solid var(--line)}
header.top .wrap{display:flex; align-items:center; gap:1rem; padding-block:.7rem}
.brand{display:flex; align-items:center; gap:.5rem; font-weight:700;
  letter-spacing:-.015em; text-decoration:none}
.brand .seal{width:1.55rem; height:1.55rem; border-radius:7px; display:grid;
  place-items:center; background:linear-gradient(145deg,var(--verd),var(--verd-deep));
  color:#fff; font-size:.82rem; font-weight:700}
header.top nav{margin-left:auto; display:flex; gap:1.1rem; font-size:.9rem; align-items:center}
header.top nav a{color:var(--soft); text-decoration:none}
header.top nav a:hover{color:var(--verd-deep)}
.cta{background:var(--verd-deep); color:#fff !important; padding:.45rem .95rem;
  border-radius:9px; font-weight:600}
.cta:hover{background:var(--verd)}
@media (max-width:720px){ header.top nav a.opt{display:none} }

/* ---- Héros ---- */
.hero{position:relative; overflow:hidden; padding:clamp(3rem,8vw,5.5rem) 0 clamp(2.6rem,6vw,4rem)}
.hero .sky{position:absolute; inset:0; pointer-events:none}
.hero .sky svg{width:100%; height:100%}
.hero .sky circle{fill:var(--verd); opacity:.14}
.hero .sky line{stroke:var(--verd); stroke-width:1; opacity:.10}
.hero .sky circle{animation:twinkle 5s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:.07}50%{opacity:.22}}
.hero h1{position:relative; font-size:clamp(2.3rem,6vw,4rem); line-height:1.02;
  letter-spacing:-.035em; margin:0 0 1.1rem; max-width:16ch; font-weight:700}
.hero h1 em{font-style:normal; color:var(--verd-deep);
  background:linear-gradient(180deg,transparent 66%, var(--verd-pale) 66%)}
.hero .lede{position:relative; font-size:clamp(1.05rem,2vw,1.25rem); color:#3C4E48;
  max-width:52ch; margin:0 0 1.8rem}
.hero .acts{position:relative; display:flex; gap:.8rem; flex-wrap:wrap}
.hero .acts a{text-decoration:none; font-weight:600; padding:.75rem 1.3rem;
  border-radius:11px}
.hero .acts .go{background:var(--verd-deep); color:#fff}
.hero .acts .go:hover{background:var(--verd)}
.hero .acts .alt{border:1.5px solid var(--line); color:var(--ink); background:var(--panel)}
.hero .acts .alt:hover{border-color:var(--verd)}
.hero .figures{position:relative; display:flex; gap:clamp(1.4rem,4vw,3rem);
  flex-wrap:wrap; margin-top:2.6rem; padding-top:1.4rem; border-top:1px solid var(--line)}
.hero .figures b{display:block; font-size:1.5rem; letter-spacing:-.02em;
  font-variant-numeric:tabular-nums; color:var(--verd-deep)}
.hero .figures span{font-size:.85rem; color:var(--soft)}

/* ---- Sections communes ---- */
section{padding:clamp(3.2rem,7vw,5rem) 0}
.kicker{display:flex; align-items:center; gap:.7rem; font-size:.78rem;
  letter-spacing:.16em; text-transform:uppercase; color:var(--verd); font-weight:600;
  margin:0 0 1rem}
.kicker::before{content:""; width:2.2rem; height:2px; background:var(--verd)}
h2{font-size:clamp(1.7rem,3.8vw,2.5rem); line-height:1.12; letter-spacing:-.028em;
  margin:0 0 .8rem; max-width:24ch; font-weight:700}
.note{color:var(--soft); max-width:60ch; margin:0}

/* ---- La scène (jour et nuit partagent la grammaire) ---- */
.scene{margin-top:2.2rem; background:var(--panel); border:1px solid var(--line);
  border-radius:18px; box-shadow:var(--lift); overflow:hidden}
.scene svg{display:block; width:100%; height:auto}
.scene .strip{display:grid; grid-template-columns:repeat(3,1fr); border-top:1px solid var(--line)}
.scene .strip div{padding:1.1rem 1.2rem; border-left:1px solid var(--line)}
.scene .strip div:first-child{border-left:none}
.scene .strip b{display:flex; align-items:center; gap:.5rem; font-size:.95rem;
  margin-bottom:.3rem}
.scene .strip i{width:.6rem; height:.6rem; border-radius:50%; flex:none; font-style:normal}
.scene .strip p{margin:0; font-size:.88rem; color:var(--soft)}
@media (max-width:700px){ .scene .strip{grid-template-columns:1fr}
  .scene .strip div{border-left:none; border-top:1px solid var(--line)} }

/* ---- La nuit : la page devient sombre ---- */
.night{background:linear-gradient(180deg,var(--night) 0%, var(--night-2) 100%);
  color:var(--night-ink)}
.night .kicker{color:var(--amber-soft)}
.night .kicker::before{background:var(--amber-soft)}
.night h2{color:#F1F7F3}
.night .note{color:var(--night-soft)}
.night .scene{background:rgba(255,255,255,.03); border-color:var(--night-line);
  box-shadow:none}
.night .scene .strip, .night .scene .strip div{border-color:var(--night-line)}
.night .scene .strip p{color:var(--night-soft)}

/* ---- La preuve : une vraie trace ---- */
.exhibit{margin-top:2.2rem; display:grid; grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);
  gap:1.2rem; align-items:start}
@media (max-width:860px){ .exhibit{grid-template-columns:1fr} }
.trace{background:rgba(255,255,255,.04); border:1px solid var(--night-line);
  border-radius:14px; overflow:hidden}
.trace .head{display:flex; gap:.6rem; align-items:center; padding:.7rem 1rem;
  border-bottom:1px solid var(--night-line); font-size:.8rem; color:var(--night-soft)}
.trace .head .id{font-family:var(--mono)}
.trace .head .ok{margin-left:auto; color:#7FC8A9; font-weight:600}
.trace pre{margin:0; padding:1rem 1.1rem; font-family:var(--mono); font-size:.8rem;
  line-height:1.6; color:#C7DAD1; white-space:pre-wrap; word-wrap:break-word}
.trace pre b{color:#F1F7F3}
.exhibit aside{display:grid; gap:1rem}
.claim{border-left:3px solid var(--amber-soft); padding:.2rem 0 .2rem 1.1rem}
.claim b{display:block; font-size:1.05rem; color:#F1F7F3; margin-bottom:.2rem}
.claim p{margin:0; font-size:.93rem; color:var(--night-soft)}

/* ---- L'économie ---- */
.market{margin-top:2.2rem; display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
  gap:1.1rem}
.offer{background:var(--panel); border:1px solid var(--line); border-radius:16px;
  padding:1.5rem 1.5rem 1.3rem; box-shadow:var(--lift); position:relative; overflow:hidden}
.offer::after{content:""; position:absolute; inset:auto 0 0 0; height:4px}
.offer.rapide::after{background:var(--verd)}
.offer.costaud::after{background:var(--amber)}
.offer.code::after{background:var(--night)}
.offer.geant::after{background:linear-gradient(90deg,var(--verd),var(--amber))}
.offer h3{margin:0; font-size:1.25rem; letter-spacing:-.015em}
.offer .model{font-size:.83rem; color:var(--soft); margin:.15rem 0 1rem}
.offer .flows{display:grid; gap:.55rem; margin:0 0 1rem}
.offer .flows div{display:flex; justify-content:space-between; align-items:baseline;
  gap:.8rem; font-size:.94rem}
.offer .flows b{font-variant-numeric:tabular-nums; font-size:1.15rem}
.offer .flows .earn b{color:var(--verd-deep)}
.offer .flows .cost b{color:var(--amber)}
.offer p.about{margin:0; font-size:.9rem; color:var(--soft)}
.wall{margin-top:1.6rem; background:var(--panel-2); border:1px dashed var(--line);
  border-radius:14px; padding:1.2rem 1.4rem; max-width:70ch}
.wall p{margin:0; color:#3C4E48; font-size:.97rem}
.wall b{color:var(--ink)}

/* ---- L'honnêteté ---- */
.honest{margin-top:2.2rem; display:flex; gap:clamp(1.5rem,5vw,3.5rem); flex-wrap:wrap;
  align-items:flex-start}
.honest .fig b{font-size:clamp(2.6rem,6vw,3.6rem); letter-spacing:-.03em; line-height:1;
  font-variant-numeric:tabular-nums; display:block}
.honest .fig span{color:var(--soft); font-size:.88rem}
.honest .fig.now b{color:var(--verd-deep)}
.honest .story{flex:1; min-width:min(34ch,100%); color:#3C4E48; margin:0; max-width:58ch}
.state{display:grid; gap:1.1rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  margin-top:2rem}
.panel{background:var(--panel); border:1px solid var(--line); border-radius:14px;
  padding:1.3rem 1.4rem; box-shadow:var(--lift)}
.panel.soon{background:var(--panel-2); border-style:dashed; box-shadow:none}
.panel h4{margin:0 0 .9rem; display:flex; align-items:center; gap:.55rem; font-size:1rem}
.pill{font-size:.68rem; letter-spacing:.09em; text-transform:uppercase; padding:.14rem .5rem;
  border-radius:4px; font-weight:700}
.panel.now .pill{background:var(--verd); color:#fff}
.panel.soon .pill{background:var(--amber-pale); color:#7A5312; border:1px solid #E7D3AE}
.panel ul{margin:0; padding:0; list-style:none; display:grid; gap:.5rem; font-size:.96rem;
  color:#3C4E48}
.panel li{display:flex; gap:.6rem}
.panel.now li::before{content:"✓"; color:var(--verd); font-weight:700}
.panel.soon li::before{content:"→"; color:var(--amber)}

/* ---- Participer ---- */
.os{display:flex; gap:1.1rem; margin:1.8rem 0 .7rem; font-size:.92rem}
.os button{background:none; border:none; padding:0 0 3px; cursor:pointer; font:inherit;
  color:var(--soft); border-bottom:2px solid transparent}
.os button[aria-selected="true"]{color:var(--ink); border-color:var(--verd); font-weight:600}
.cmd{display:flex; border:1px solid var(--line); border-radius:11px; background:var(--panel);
  overflow:hidden; max-width:660px; box-shadow:var(--lift)}
.cmd code{font-family:var(--mono); font-size:.87rem; padding:.9rem 1rem; flex:1;
  overflow-x:auto; white-space:nowrap}
.cmd button{font:inherit; font-size:.85rem; font-weight:600; padding:0 1.15rem;
  cursor:pointer; background:var(--verd-deep); color:#fff; border:none}
.cmd button:hover{background:var(--verd)}
.after{color:var(--soft); font-size:.95rem; margin:1rem 0 0; max-width:62ch}
.after code{font-family:var(--mono); background:var(--panel-2); border:1px solid var(--line);
  border-radius:5px; padding:.1rem .4rem; font-size:.85rem}
.pledge{margin:1.7rem 0 0; padding:0; list-style:none; display:grid; gap:.5rem; max-width:62ch}
.pledge li{display:flex; gap:.7rem; font-size:.96rem}
.pledge li::before{content:"non"; flex:none; font-size:.68rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--amber); border:1px solid var(--amber);
  border-radius:3px; padding:0 .3rem; height:1.2rem; line-height:1.15rem; margin-top:.26rem}

footer{border-top:1px solid var(--line); padding:2rem 0 3rem; color:var(--soft);
  font-size:.88rem}
footer .wrap{display:flex; gap:1.3rem; flex-wrap:wrap}
footer .right{margin-left:auto}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <a class="brand" href="/"><span class="seal">L</span> Lenyay</a>
    <nav>
      <a href="#jour" class="opt">Le jour</a>
      <a href="#nuit" class="opt">La nuit</a>
      <a href="#economie" class="opt">Les crédits</a>
      <a href="#etat" class="opt">Où on en est</a>
      <a href="#participer">Participer</a>
      <a href="/dashboard" class="opt">Le réseau</a>
      <a class="cta" href="/">Ouvrir le chat</a>
    </nav>
  </div>
</header>

<div class="hero">
  <div class="sky" aria-hidden="true">
    <svg viewBox="0 0 1200 520" preserveAspectRatio="xMidYMid slice">
      <line x1="150" y1="90" x2="420" y2="170"/><line x1="420" y1="170" x2="700" y2="80"/>
      <line x1="700" y1="80" x2="980" y2="200"/><line x1="420" y1="170" x2="560" y2="330"/>
      <line x1="980" y1="200" x2="1120" y2="90"/><line x1="560" y1="330" x2="900" y2="420"/>
      <line x1="150" y1="90" x2="80" y2="280"/><line x1="80" y1="280" x2="560" y2="330"/>
      <circle cx="150" cy="90" r="5"/><circle cx="420" cy="170" r="7" style="animation-delay:.7s"/>
      <circle cx="700" cy="80" r="4" style="animation-delay:1.4s"/>
      <circle cx="980" cy="200" r="6" style="animation-delay:2.1s"/>
      <circle cx="1120" cy="90" r="4" style="animation-delay:2.8s"/>
      <circle cx="560" cy="330" r="6" style="animation-delay:3.5s"/>
      <circle cx="80" cy="280" r="5" style="animation-delay:4.2s"/>
      <circle cx="900" cy="420" r="5" style="animation-delay:1s"/>
    </svg>
  </div>
  <div class="wrap">
    <h1>Le jour, tu lui parles.<br>La nuit, <em>ta machine la nourrit</em>.</h1>
    <p class="lede">Lenyay est une IA sans datacenter : elle vit sur les ordinateurs
      de ses membres. Chaque question est servie par la machine de quelqu'un, et
      chaque nuit de calcul rend le service gratuit pour celui qui la prête.</p>
    <div class="acts">
      <a class="go" href="/">Poser une question</a>
      <a class="alt" href="#participer">Prêter ma machine — 5 min</a>
    </div>
    <div class="figures">
      <div><b id="f-devices">—</b><span>machines dans le réseau</span></div>
      <div><b id="f-done">—</b><span>calculs vérifiés</span></div>
      <div><b id="f-rate">—</b><span>de réussite</span></div>
      <div><b>0 €</b><span>de serveurs d'inférence</span></div>
    </div>
  </div>
</div>

<section id="jour">
  <div class="wrap">
    <p class="kicker">Le jour</p>
    <h2>Ta question voyage jusqu'à la machine d'un membre.</h2>
    <p class="note">Pas d'API d'entreprise derrière : le coordinateur met ta question
      en file, et le premier ordinateur du réseau capable d'y répondre la décroche.
      La réponse revient signée du nom de la machine qui l'a produite.</p>

    <div class="scene">
      <svg viewBox="0 0 1000 300" role="img" aria-label="Le trajet d'une question : de toi au coordinateur, puis à la machine d'un membre, et retour">
        <defs>
          <path id="aller1" d="M 150,150 C 260,90 380,90 490,148"/>
          <path id="aller2" d="M 510,152 C 620,210 740,210 850,152"/>
          <path id="retour" d="M 850,168 C 640,275 360,275 152,166"/>
        </defs>
        <use href="#aller1" fill="none" stroke="#CFE0D8" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>
        <use href="#aller2" fill="none" stroke="#CFE0D8" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>
        <use href="#retour" fill="none" stroke="#E8D9BC" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>

        <!-- toi -->
        <g>
          <circle cx="130" cy="150" r="34" fill="#DCEBE5"/>
          <circle cx="130" cy="150" r="34" fill="none" stroke="#3F8C79" stroke-width="1.5"/>
          <text x="130" y="157" text-anchor="middle" font-size="22">💬</text>
          <text x="130" y="212" text-anchor="middle" font-size="14" fill="#5F7069" font-family="inherit">toi</text>
        </g>
        <!-- coordinateur -->
        <g>
          <rect x="462" y="112" width="76" height="76" rx="18" fill="#245247"/>
          <text x="500" y="158" text-anchor="middle" font-size="24">🕸️</text>
          <text x="500" y="222" text-anchor="middle" font-size="14" fill="#5F7069">le coordinateur</text>
          <text x="500" y="240" text-anchor="middle" font-size="11.5" fill="#8FA69B">met en file, vérifie, crédite</text>
        </g>
        <!-- la machine d'un membre -->
        <g>
          <circle cx="870" cy="150" r="34" fill="#DCEBE5"/>
          <circle cx="870" cy="150" r="34" fill="none" stroke="#3F8C79" stroke-width="1.5"/>
          <text x="870" y="158" text-anchor="middle" font-size="22">💻</text>
          <text x="870" y="212" text-anchor="middle" font-size="14" fill="#5F7069">portable-anna</text>
          <text x="870" y="230" text-anchor="middle" font-size="11.5" fill="#8FA69B">modèle déjà chargé</text>
        </g>

        <!-- la question (vert sombre) puis la réponse (ambre) -->
        <circle r="7" fill="#245247">
          <animateMotion dur="9s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" begin="0s" calcMode="linear">
            <mpath href="#aller1"/>
          </animateMotion>
          <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
            values="0;1;1;0;0" keyTimes="0;.04;.3;.34;1"/>
        </circle>
        <circle r="7" fill="#245247">
          <animateMotion dur="9s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;.34;.62;1" begin="0s" calcMode="linear">
            <mpath href="#aller2"/>
          </animateMotion>
          <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
            values="0;0;1;1;0;0" keyTimes="0;.34;.38;.58;.62;1"/>
        </circle>
        <circle r="7" fill="#C97F1E">
          <animateMotion dur="9s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;.68;.96;1" begin="0s" calcMode="linear">
            <mpath href="#retour"/>
          </animateMotion>
          <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
            values="0;0;1;1;0" keyTimes="0;.68;.72;.94;1"/>
        </circle>
        <!-- la machine « réfléchit » pendant le creux -->
        <g>
          <circle cx="852" cy="104" r="3.5" fill="#3F8C79">
            <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
              values="0;0;1;0;1;0;0" keyTimes="0;.60;.63;.645;.66;.68;1"/>
          </circle>
          <circle cx="866" cy="98" r="3.5" fill="#3F8C79">
            <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
              values="0;0;1;0;1;0;0" keyTimes="0;.615;.645;.66;.675;.69;1"/>
          </circle>
          <circle cx="880" cy="104" r="3.5" fill="#3F8C79">
            <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
              values="0;0;1;0;1;0;0" keyTimes="0;.63;.66;.675;.69;.705;1"/>
          </circle>
        </g>
      </svg>
      <div class="strip">
        <div><b><i style="background:#245247"></i>Ta question part</b>
          <p>Elle coûte quelques crédits, selon le modèle choisi. Le serveur ne la lit
            pas : il la route.</p></div>
        <div><b><i style="background:#3F8C79"></i>Une machine éprouvée la prend</b>
          <p>Seules les machines ayant un historique de calculs vérifiés peuvent
            répondre — pas les inconnues.</p></div>
        <div><b><i style="background:#C97F1E"></i>La réponse revient signée</b>
          <p>« Répondu par portable-anna » : tu sais toujours quel ordinateur t'a
            servi, et son propriétaire est crédité.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="night" id="nuit">
  <div class="wrap">
    <p class="kicker">La nuit</p>
    <h2>Pendant que tu dors, ta machine gagne ta place.</h2>
    <p class="note">Elle résout des problèmes de mathématiques dont le serveur connaît
      la réponse — impossible de tricher, inutile de faire confiance. Chaque solution
      juste devient un crédit pour toi et une leçon pour le modèle commun.</p>

    <div class="scene">
      <svg viewBox="0 0 1000 300" role="img" aria-label="La nuit : le coordinateur distribue des problèmes, les machines renvoient leurs solutions, les crédits reviennent">
        <defs>
          <path id="n-out1" d="M 465,140 C 380,105 300,105 218,132"/>
          <path id="n-out2" d="M 535,140 C 620,105 700,105 782,132"/>
          <path id="n-back1" d="M 214,148 C 300,190 380,190 462,158"/>
          <path id="n-back2" d="M 786,148 C 700,190 620,190 538,158"/>
        </defs>
        <use href="#n-out1" fill="none" stroke="#2E4A41" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>
        <use href="#n-out2" fill="none" stroke="#2E4A41" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>
        <use href="#n-back1" fill="none" stroke="#4A3A20" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>
        <use href="#n-back2" fill="none" stroke="#4A3A20" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>

        <text x="70" y="70" font-size="20" opacity=".8">🌙</text>
        <circle cx="930" cy="55" r="1.8" fill="#DCEBE5" opacity=".5"/>
        <circle cx="880" cy="80" r="1.4" fill="#DCEBE5" opacity=".35"/>
        <circle cx="120" cy="110" r="1.4" fill="#DCEBE5" opacity=".35"/>
        <circle cx="960" cy="120" r="1.6" fill="#DCEBE5" opacity=".45"/>

        <!-- coordinateur, au centre -->
        <g>
          <rect x="462" y="110" width="76" height="76" rx="18" fill="#0F1A16" stroke="#3F8C79" stroke-width="1.5"/>
          <text x="500" y="156" text-anchor="middle" font-size="24">🕸️</text>
          <text x="500" y="222" text-anchor="middle" font-size="13.5" fill="#8FA69D">7 473 problèmes au catalogue</text>
        </g>
        <!-- deux machines qui veillent -->
        <g>
          <circle cx="185" cy="140" r="32" fill="#1C2F29" stroke="#3F8C79" stroke-width="1.4"/>
          <text x="185" y="148" text-anchor="middle" font-size="20">💻</text>
          <text x="185" y="200" text-anchor="middle" font-size="13.5" fill="#8FA69D">worker-julien</text>
        </g>
        <g>
          <circle cx="815" cy="140" r="32" fill="#1C2F29" stroke="#3F8C79" stroke-width="1.4"/>
          <text x="815" y="148" text-anchor="middle" font-size="20">💻</text>
          <text x="815" y="200" text-anchor="middle" font-size="13.5" fill="#8FA69D">vieux-pc-atelier</text>
        </g>

        <!-- problèmes qui partent (verts), crédits qui reviennent (ambre) -->
        <circle r="6" fill="#3F8C79">
          <animateMotion dur="7s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1"><mpath href="#n-out1"/></animateMotion>
          <animate attributeName="opacity" dur="7s" repeatCount="indefinite" values="0;1;1;0;0" keyTimes="0;.05;.4;.46;1"/>
        </circle>
        <circle r="6" fill="#3F8C79">
          <animateMotion dur="7s" repeatCount="indefinite" begin="1.2s" keyPoints="0;1" keyTimes="0;1"><mpath href="#n-out2"/></animateMotion>
          <animate attributeName="opacity" dur="7s" repeatCount="indefinite" begin="1.2s" values="0;1;1;0;0" keyTimes="0;.05;.4;.46;1"/>
        </circle>
        <circle r="6" fill="#E8B45A">
          <animateMotion dur="7s" repeatCount="indefinite" begin="3.1s" keyPoints="0;1" keyTimes="0;1"><mpath href="#n-back1"/></animateMotion>
          <animate attributeName="opacity" dur="7s" repeatCount="indefinite" begin="3.1s" values="0;1;1;0;0" keyTimes="0;.05;.4;.46;1"/>
        </circle>
        <circle r="6" fill="#E8B45A">
          <animateMotion dur="7s" repeatCount="indefinite" begin="4.4s" keyPoints="0;1" keyTimes="0;1"><mpath href="#n-back2"/></animateMotion>
          <animate attributeName="opacity" dur="7s" repeatCount="indefinite" begin="4.4s" values="0;1;1;0;0" keyTimes="0;.05;.4;.46;1"/>
        </circle>
      </svg>
      <div class="strip">
        <div><b><i style="background:#3F8C79"></i>Des problèmes vérifiables</b>
          <p>La réponse attendue reste au serveur : une solution est juste ou fausse,
            sans arbitre humain.</p></div>
        <div><b><i style="background:#E8B45A"></i>Des crédits en retour</b>
          <p>Chaque solution juste crédite ton compte — c'est ce que tu dépenseras
            le jour, en questions.</p></div>
        <div><b><i style="background:#DCEBE5"></i>Un modèle qui apprend</b>
          <p>Les raisonnements justes forment un corpus, et le modèle commun est
            réentraîné avec — il appartient à tout le monde.</p></div>
      </div>
    </div>

    <div class="exhibit">
      <div class="trace">
        <div class="head"><span class="id">gsm8k-train-0037</span>
          <span>résolu par une machine du réseau</span><span class="ok">✓ vérifié</span></div>
        <pre><b>Problème :</b> Five friends eat at a fast-food chain and order 5 hamburgers
($3 each), 4 sets of French fries ($1.20), 5 sodas ($0.5 each) and
1 spaghetti ($2.7). How much will each pay if they split the bill?

<b>Ce que la machine a écrit :</b>
- Hamburgers : 5 × $3 = $15
- Frites : 4 × $1.20 = $4.80
- Sodas : 5 × $0.5 = $2.50
- Spaghetti : $2.70
- Total : $25 → $25 / 5 amis = <b>$5 chacun</b></pre>
      </div>
      <aside>
        <div class="claim"><b>Rien n'est reconstitué.</b>
          <p>Cet énoncé vient du catalogue réel, ce raisonnement a été écrit par
            l'ordinateur d'un membre, et cette vérification est celle du serveur.</p></div>
        <div class="claim"><b>Tricher ne rapporte rien.</b>
          <p>La réponse attendue ne quitte jamais le serveur. Une machine qui envoie
            n'importe quoi n'est simplement pas créditée.</p></div>
        <div class="claim"><b>Les maths ne sont qu'un début.</b>
          <p>Tout travail dont le résultat se vérifie fera l'affaire. C'est la
            vérification qui compte, pas le sujet.</p></div>
      </aside>
    </div>
  </div>
</section>

<section id="economie">
  <div class="wrap">
    <p class="kicker">Les crédits</p>
    <h2>Un troc honnête, pas une monnaie.</h2>
    <p class="note">Les crédits comptent l'équilibre entre ce que tu donnes et ce que
      tu prends. Ils ne s'achètent pas, ne se revendent pas, et ne vaudront jamais
      d'argent. Tu en reçois 20 à l'ouverture du compte.</p>

    <div class="market">
      <div class="offer rapide">
        <h3>Rapide</h3>
        <p class="model">Qwen2.5 — 1,5 milliard de paramètres</p>
        <div class="flows">
          <div class="cost"><span>Poser une question</span><b>−1 crédit</b></div>
          <div class="earn"><span>La servir avec ta machine</span><b>+3 crédits</b></div>
        </div>
        <p class="about">Questions courantes, réponse en quelques secondes. Tourne sur
          à peu près n'importe quel ordinateur.</p>
      </div>
      <div class="offer costaud">
        <h3>Costaud</h3>
        <p class="model">Qwen2.5 — 7 milliards de paramètres</p>
        <div class="flows">
          <div class="cost"><span>Poser une question</span><b>−5 crédits</b></div>
          <div class="earn"><span>La servir avec ta machine</span><b>+12 crédits</b></div>
        </div>
        <p class="about">Raisonnements longs, rédaction. Demande ~8 Go de mémoire
          libre — et rapporte quatre fois plus à qui le sert.</p>
      </div>
      <div class="offer code">
        <h3>Code</h3>
        <p class="model">Qwen2.5-Coder — spécialisé programmation</p>
        <div class="flows">
          <div class="cost"><span>Poser une question</span><b>−12 crédits</b></div>
          <div class="earn"><span>La servir avec ta machine</span><b>+25 crédits</b></div>
        </div>
        <p class="about">Écrire, corriger, expliquer du code. Le palier le plus cher —
          c'est le vrai poste de calcul, et le plus rentable à servir.</p>
      </div>
      <div class="offer geant">
        <h3>Géant</h3>
        <p class="model">Qwen2.5 — 14 milliards de paramètres</p>
        <div class="flows">
          <div class="cost"><span>Poser une question</span><b>−20 crédits</b></div>
          <div class="earn"><span>La servir avec ta machine</span><b>+45 crédits</b></div>
        </div>
        <p class="about">Le plus grand modèle du réseau (~12 Go de mémoire libre).
          N'apparaît dans le chat que si une machine peut le servir.</p>
      </div>
    </div>

    <div class="wall">
      <p><b>Et si je ne contribue pas ?</b> Chaque jour, ton solde remonte à
        5 crédits : de quoi poser quelques questions simples, gratuitement, pour
        toujours. L'usage intensif — de longues sessions, du code — se gagne en
        laissant ta machine contribuer, ou s'achètera avec un petit abonnement.
        Comme il n'y a aucun datacenter à payer, il restera modeste — et il est
        en construction : nous ne le vendrons pas avant qu'il existe.</p>
    </div>
  </div>
</section>

<section id="etat">
  <div class="wrap">
    <p class="kicker">Où on en est</p>
    <h2>On n'annonce que ce qui marche.</h2>
    <p class="note">Lenyay se construit en public — le code est ouvert, les chiffres
      aussi, y compris quand ils ne sont pas flatteurs.</p>

    <div class="honest">
      <div class="fig"><b>71,5 %</b><span>v0.1 — le modèle d'origine, sur nos 200
        problèmes d'examen</span></div>
      <div class="fig now"><b>71,0 %</b><span>v0.2 — après notre premier
        entraînement</span></div>
      <p class="story">Notre premier essai n'a rien amélioré, et nous l'affichons.
        Nous avions entraîné le modèle sur des problèmes qu'il savait déjà résoudre :
        il a réappris ce qu'il connaissait. L'essaim chasse désormais ceux qu'il
        <em>rate</em> — ce sont eux qui enseignent. Le prochain chiffre sera obtenu
        dans les mêmes conditions, bon ou mauvais.</p>
    </div>

    <div class="state">
      <div class="panel now">
        <h4><span class="pill">Disponible</span></h4>
        <ul>
          <li>Conversations suivies, avec mémoire du fil</li>
          <li>Deux modèles au choix, facturés en crédits</li>
          <li>Compte avec e-mail et mot de passe, relevé complet des crédits</li>
          <li>L'IA hors ligne sur ta propre machine (<code>--chat</code>), sans limite</li>
          <li>Le réseau tourne et réentraîne le modèle avec ce qu'il produit</li>
        </ul>
      </div>
      <div class="panel soon">
        <h4><span class="pill">En construction</span></h4>
        <ul>
          <li>Abonnement, pour utiliser sans contribuer</li>
          <li>Un très grand modèle réparti sur plusieurs machines</li>
          <li>Participer depuis un téléphone Android</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="participer">
  <div class="wrap">
    <p class="kicker">Participer</p>
    <h2>Une commande, et ta machine rejoint le réseau.</h2>
    <p class="note">Rien ne s'installe hors de son dossier, aucun mot de passe système
      n'est demandé, et désinstaller revient à supprimer un dossier.</p>

    <div class="os" role="tablist">
      <button role="tab" aria-selected="true" data-os="win">Windows</button>
      <button role="tab" aria-selected="false" data-os="nix">Linux / macOS</button>
    </div>
    <div class="cmd">
      <code id="cmd-text">irm https://lenyay.org/install.ps1 | iex</code>
      <button id="copy" type="button">Copier</button>
    </div>
    <p class="after">Au premier démarrage, le modèle se télécharge une fois (1,1 Go).
      Rattache la machine à ton compte pour que ses gains alimentent tes crédits — et
      parle au modèle hors ligne quand tu veux avec <code>lenyay --chat</code>.
      <a href="https://github.com/k1tz03/lenyay/blob/main/REJOINDRE.md">Guide complet</a>.</p>

    <ul class="pledge">
      <li>de cryptomonnaie, ni de minage.</li>
      <li>de démarrage automatique dans ton dos.</li>
      <li>de publicité, ni de traceur sur ce site.</li>
      <li>de crédits échangeables contre de l'argent.</li>
      <li>de promesse sur ce qui n'existe pas encore.</li>
    </ul>
  </div>
</section>

<footer>
  <div class="wrap">
    <span>Lenyay — un bien commun</span>
    <a href="https://github.com/k1tz03/lenyay">Le code, entièrement ouvert</a>
    <a href="/dashboard">Le réseau en direct</a>
    <a href="/">Ouvrir le chat</a>
    <span class="right">Construit en public</span>
  </div>
</footer>

<script>
const fmt = n => Number(n).toLocaleString("fr-FR");
(async () => {
  try{
    const s = await (await fetch("/stats", {cache:"no-store"})).json();
    document.getElementById("f-devices").textContent = fmt(s.devices_seen);
    document.getElementById("f-done").textContent = fmt(s.accepted_rollouts);
    document.getElementById("f-rate").textContent = (100 * s.acceptance_rate).toFixed(0) + " %";
  }catch(e){}
})();
const CMD = {win:"irm https://lenyay.org/install.ps1 | iex",
             nix:"curl -fsSL https://lenyay.org/install.sh | bash"};
document.querySelectorAll(".os button").forEach(b => b.onclick = () => {
  document.querySelectorAll(".os button").forEach(o => o.setAttribute("aria-selected","false"));
  b.setAttribute("aria-selected","true");
  document.getElementById("cmd-text").textContent = CMD[b.dataset.os];
});
document.getElementById("copy").onclick = async e => {
  try{ await navigator.clipboard.writeText(document.getElementById("cmd-text").textContent);
    e.target.textContent = "Copié"; setTimeout(() => e.target.textContent = "Copier", 1600);
  }catch(err){ e.target.textContent = "Ctrl+C"; }
};
</script>
</body>
</html>"""
