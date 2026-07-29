"""La console d'administration — réservée à qui détient le jeton.

La page ne contient aucun secret : elle demande le jeton, le garde en
sessionStorage (fermé l'onglet, oublié le jeton) et l'envoie en en-tête
X-Admin-Token à chaque appel. Côté serveur, tout passe par require_admin.
"""

ADMIN_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lenyay — administration</title>
<meta name="robots" content="noindex">
<style>
@font-face{font-family:"Familjen"; font-style:normal; font-weight:400 700;
  font-display:swap; src:url("/static/fonts/familjen-latin.woff2") format("woff2")}
:root{
  --bg:#12201B; --panel:#182A24; --panel-2:#1F332C; --line:#2E4A41;
  --ink:#E4EFE9; --soft:#8FA69D; --verd:#5FB394; --amber:#E8B45A; --red:#E07856;
  --ui:"Familjen","Avenir Next",system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace;
}
*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink); font-family:var(--ui);
  font-size:15.5px; line-height:1.55}
.wrap{max-width:1080px; margin:0 auto; padding:1.4rem clamp(1rem,3vw,2rem) 3rem}
h1{font-size:1.3rem; letter-spacing:-.015em; margin:0; display:flex; gap:.6rem;
  align-items:center}
h1 .seal{width:1.5rem; height:1.5rem; border-radius:7px; display:grid; place-items:center;
  background:var(--verd); color:#0E1A15; font-size:.8rem; font-weight:700}
h1 small{color:var(--soft); font-weight:400; font-size:.85rem; margin-left:.3rem}
.gate{max-width:26rem; margin:14vh auto 0; background:var(--panel);
  border:1px solid var(--line); border-radius:14px; padding:1.6rem}
.gate p{color:var(--soft); font-size:.92rem; margin:.4rem 0 1rem}
.gate input{width:100%; font:inherit; font-family:var(--mono); font-size:.9rem;
  padding:.65rem .8rem; border:1px solid var(--line); border-radius:9px;
  background:var(--bg); color:var(--ink)}
.gate button{margin-top:.8rem; width:100%; font:inherit; font-weight:600; padding:.7rem;
  border:none; border-radius:9px; background:var(--verd); color:#0E1A15; cursor:pointer}
.gate .err{color:var(--red); font-size:.86rem; min-height:1.1rem; margin:.5rem 0 0}

.chips{display:flex; gap:.7rem; flex-wrap:wrap; margin:1.3rem 0 1.5rem}
.chip{background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:.55rem .9rem; font-size:.85rem; color:var(--soft)}
.chip b{color:var(--ink); font-variant-numeric:tabular-nums; font-size:1.05rem;
  display:block; letter-spacing:-.01em}

table{width:100%; border-collapse:collapse; background:var(--panel);
  border:1px solid var(--line); border-radius:12px; overflow:hidden; font-size:.88rem}
th,td{padding:.6rem .8rem; text-align:left; border-bottom:1px solid var(--line)}
th{font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; color:var(--soft);
  background:var(--panel-2); font-weight:600}
td b{font-weight:600}
td .mail{color:var(--soft); font-size:.8rem; display:block}
.num{font-variant-numeric:tabular-nums; text-align:right}
.plus{color:var(--verd)} .minus{color:var(--amber)}
.state-ok{color:var(--verd)} .state-ban{color:var(--red); font-weight:600}
.act{display:flex; gap:.4rem; justify-content:flex-end}
.act button{font:inherit; font-size:.78rem; padding:.3rem .6rem; border-radius:7px;
  border:1px solid var(--line); background:none; color:var(--ink); cursor:pointer}
.act button:hover{border-color:var(--verd)}
.act button.warn:hover{border-color:var(--red); color:var(--red)}
.bar{display:flex; align-items:center; gap:.8rem; margin-bottom:.7rem}
.bar input{flex:1; max-width:20rem; font:inherit; font-size:.88rem; padding:.5rem .7rem;
  border:1px solid var(--line); border-radius:9px; background:var(--panel); color:var(--ink)}
.bar .out{margin-left:auto; font-size:.8rem; color:var(--soft); background:none;
  border:none; cursor:pointer; text-decoration:underline}
.msg{min-height:1.2rem; font-size:.85rem; color:var(--verd); margin:.6rem 0 0}
.msg.bad{color:var(--red)}
@media (max-width:760px){ .hide-sm{display:none} }
</style>
</head>
<body>
<div class="wrap">
  <div class="gate" id="gate">
    <h1><span class="seal">L</span> Administration</h1>
    <p>Cette console exige le jeton défini par <code>LENYAY_ADMIN_TOKEN</code> sur le
      serveur. Il sera envoyé en en-tête <code>X-Admin-Token</code> et gardé le temps
      de cet onglet seulement.</p>
    <input id="tok" type="password" placeholder="jeton d'administration" autocomplete="off">
    <button id="enter">Entrer</button>
    <p class="err" id="gate-err"></p>
  </div>

  <div id="console" hidden>
    <div class="bar">
      <h1><span class="seal">L</span> Membres <small id="count"></small></h1>
      <input id="filter" placeholder="filtrer par pseudo ou e-mail">
      <button class="out" id="out">quitter</button>
    </div>
    <div class="chips" id="chips"></div>
    <table>
      <thead><tr>
        <th>Membre</th><th class="num">Solde</th><th class="num hide-sm">Gagné</th>
        <th class="num hide-sm">Dépensé</th><th class="num hide-sm">Machines</th>
        <th class="num hide-sm">Questions</th><th>État</th><th></th>
      </tr></thead>
      <tbody id="rows"></tbody>
    </table>
    <p class="msg" id="msg"></p>
  </div>
</div>

<script>
const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString("fr-FR");
const esc = s => { const d = document.createElement("div"); d.textContent = s ?? ""; return d.innerHTML; };
let token = sessionStorage.getItem("lenyay.admin") || "";
let members = [];

const api = (url, opt = {}) => fetch(url, {...opt, headers: {
  "Content-Type": "application/json", "X-Admin-Token": token, ...(opt.headers || {})}});

function say(text, bad){ const m = $("msg"); m.textContent = text; m.className = "msg" + (bad ? " bad" : "");
  setTimeout(() => { m.textContent = ""; }, 4000); }

async function refresh(){
  const [mr, or_] = await Promise.all([api("/admin/members"), api("/admin/overview")]);
  if(!mr.ok){ leave(); return; }
  members = (await mr.json()).members;
  const o = await or_.json();
  $("count").textContent = members.length + " compte" + (members.length > 1 ? "s" : "");
  $("chips").innerHTML = `
    <div class="chip"><b>${fmt(o.stats.devices_seen)}</b>machines vues</div>
    <div class="chip"><b>${fmt(o.stats.accepted_rollouts)}</b>calculs vérifiés</div>
    <div class="chip"><b>${fmt(o.questions.pending)}</b>questions en attente</div>
    <div class="chip"><b>${fmt(o.questions.done)}</b>questions servies</div>
    <div class="chip"><b>${fmt(o.banned)}</b>suspendus</div>`;
  paint();
}
function paint(){
  const q = ($("filter").value || "").toLowerCase();
  $("rows").innerHTML = members
    .filter(m => !q || (m.handle || "").toLowerCase().includes(q)
                    || (m.email || "").toLowerCase().includes(q))
    .map(m => `<tr>
      <td><b>${esc(m.handle)}</b><span class="mail">${esc(m.email || "compte machine (clé seule)")}</span></td>
      <td class="num"><b>${fmt(m.credits)}</b></td>
      <td class="num hide-sm plus">+${fmt(m.earned)}</td>
      <td class="num hide-sm minus">−${fmt(m.spent)}</td>
      <td class="num hide-sm">${fmt(m.devices)}</td>
      <td class="num hide-sm">${fmt(m.questions)}</td>
      <td class="${m.banned ? "state-ban" : "state-ok"}">${m.banned ? "suspendu" : "actif"}</td>
      <td class="act">
        <button data-c="${m.account_id}">± crédits</button>
        <button class="warn" data-b="${m.account_id}" data-v="${m.banned ? 0 : 1}">
          ${m.banned ? "rétablir" : "suspendre"}</button>
      </td></tr>`).join("");
  $("rows").querySelectorAll("[data-c]").forEach(b => b.onclick = async () => {
    const amount = parseInt(prompt("Montant (négatif pour retirer) :", "10"), 10);
    if(!amount) return;
    const reason = prompt("Motif (visible dans le relevé du membre) :", "") || "";
    const r = await api(`/admin/members/${b.dataset.c}/credits`, {
      method:"POST", body: JSON.stringify({amount, reason})});
    say(r.ok ? "Crédits ajustés." : "Refusé : " + r.status, !r.ok); refresh();
  });
  $("rows").querySelectorAll("[data-b]").forEach(b => b.onclick = async () => {
    const banned = b.dataset.v === "1";
    if(banned && !confirm("Suspendre ce compte ? Il perd tout accès immédiatement.")) return;
    const r = await api(`/admin/members/${b.dataset.b}/ban`, {
      method:"POST", body: JSON.stringify({banned})});
    say(r.ok ? (banned ? "Compte suspendu." : "Compte rétabli.") : "Refusé : " + r.status, !r.ok);
    refresh();
  });
}
function leave(){
  sessionStorage.removeItem("lenyay.admin"); token = "";
  $("console").hidden = true; $("gate").hidden = false;
  $("gate-err").textContent = "Jeton refusé ou expiré.";
}
async function enter(){
  token = $("tok").value.trim();
  const r = await api("/admin/overview");
  if(!r.ok){ $("gate-err").textContent = r.status === 403
    ? "Administration désactivée sur ce serveur." : "Jeton refusé."; return; }
  sessionStorage.setItem("lenyay.admin", token);
  $("gate").hidden = true; $("console").hidden = false;
  refresh(); setInterval(refresh, 20000);
}
$("enter").onclick = enter;
$("tok").addEventListener("keydown", e => { if(e.key === "Enter") enter(); });
$("filter") && ($("filter").oninput = paint);
$("out").onclick = () => { leave(); $("gate-err").textContent = ""; };
if(token){ enter0(); } async function enter0(){ $("tok").value = token; enter(); }
</script>
</body>
</html>"""
