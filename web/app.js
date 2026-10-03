const EMO_CN = {neutral:"平静", focused:"专注", happy:"开心", excited:"激动", nervous:"紧张", scolded:"闷着气", sad:"难过", startled:"受惊", intimate:"亲近", aroused:"燥热"};
function $(id){return document.getElementById(id);}
document.querySelectorAll(".tab").forEach(t=>t.addEventListener("click",()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
  document.querySelectorAll(".page").forEach(x=>x.classList.remove("active"));
  t.classList.add("active"); $("page-"+t.dataset.tab).classList.add("active");
}));
window.applyState=function(s){
  if(!s)return; $("line").textContent=s.line; $("hrVal").textContent=s.heart_rate; $("tempVal").textContent=s.temperature;
  $("brVal").textContent=s.breathing.rate; $("brLbl").textContent="呼吸 · "+s.breathing.label; $("chordTag").textContent=s.chord.chord; $("chordDesc").textContent=s.chord.desc;
  $("heartIcon").style.animationDuration=(60/s.heart_rate).toFixed(2)+"s";
  const map={touch:"touchBar",smell:"smellBar",taste:"tasteBar",sound:"soundBar"}, lbl={touch:"touchLbl",smell:"smellLbl",taste:"tasteLbl",sound:"soundLbl"};
  for(const k in map){const v=s.senses[k]; $(map[k]).style.width=(v.value*100)+"%"; $(lbl[k]).textContent=v.value.toFixed(2);}
  $("emotionBadge").textContent="当前情绪 · "+(EMO_CN[s.emotion]||s.emotion); $("updated").textContent="更新于 "+new Date(s.ts*1000).toLocaleTimeString("zh-CN");
};
async function refresh(){try{const r=await fetch("/api/state",{cache:"no-store"});window.applyState(await r.json());}catch(e){$("line").textContent="连接断开，重试中…";}}
function renderMenu(groups){
  const root=$("touchMenu"); root.innerHTML="";
  for(const group of groups){
    const sec=document.createElement("section"); sec.className="touch-group";
    const h=document.createElement("h2"); h.textContent=group.group; sec.appendChild(h);
    for(const zone of group.zones){
      const row=document.createElement("div"); row.className="touch-row";
      const name=document.createElement("div"); name.className="zone-name"; name.textContent="【"+zone.name+"】"; row.appendChild(name);
      const acts=document.createElement("div"); acts.className="action-list";
      for(const action of zone.actions){
        const b=document.createElement("button"); b.className="action-btn"; b.textContent=action;
        b.addEventListener("click",()=>sendAction(zone.name,action,b)); acts.appendChild(b);
      }
      row.appendChild(acts); sec.appendChild(row);
    }
    root.appendChild(sec);
  }
}
async function loadMenu(){try{const r=await fetch("/api/touch-menu",{cache:"no-store"});const d=await r.json();renderMenu(d.groups||[]);}catch(e){$("touchMenu").innerHTML="<div class=\"menu-loading\">菜单暂时无法加载</div>";}}
async function sendAction(zone,action,button){
  button.classList.add("pressed"); setTimeout(()=>button.classList.remove("pressed"),180);
  try{const r=await fetch("/api/touch-action",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({zone,action})});const d=await r.json();if(d.ok&&window.applyState)window.applyState(d.state);}catch(e){}
}
refresh(); setInterval(refresh,3000); loadMenu();
