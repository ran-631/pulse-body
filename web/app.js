const EMO_CN = {
  neutral:"平静", focused:"专注", happy:"开心", excited:"激动",
  nervous:"紧张", scolded:"闷着气", sad:"难过", startled:"受惊",
  intimate:"亲近", aroused:"燥热",
};
function $(id){ return document.getElementById(id); }

// Tab 切换
document.querySelectorAll(".tab").forEach(t=>{
  t.addEventListener("click", ()=>{
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    document.querySelectorAll(".page").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    $("page-"+t.dataset.tab).classList.add("active");
  });
});

// 把状态渲染到界面（触碰后也复用）
window.applyState = function(s){
  if(!s) return;
  $("line").textContent = s.line;
  $("hrVal").textContent = s.heart_rate;
  $("tempVal").textContent = s.temperature;
  $("brVal").textContent = s.breathing.rate;
  $("brLbl").textContent = "呼吸 · " + s.breathing.label;
  $("chordTag").textContent = s.chord.chord;
  $("chordDesc").textContent = s.chord.desc;
  const dur = (60 / s.heart_rate).toFixed(2);
  $("heartIcon").style.animationDuration = dur + "s";
  const map = {touch:"touchBar",smell:"smellBar",taste:"tasteBar",sound:"soundBar"};
  const lbl = {touch:"touchLbl",smell:"smellLbl",taste:"tasteLbl",sound:"soundLbl"};
  for(const k in map){
    const v = s.senses[k];
    $(map[k]).style.width = (v.value*100) + "%";
    $(lbl[k]).textContent = v.label;
  }
  $("emotionBadge").textContent = "当前情绪 · " + (EMO_CN[s.emotion]||s.emotion);
  const d = new Date(s.ts*1000);
  $("updated").textContent = "更新于 " + d.toLocaleTimeString("zh-CN");
};

async function refresh(){
  try{
    const r = await fetch("/api/state", {cache:"no-store"});
    window.applyState(await r.json());
  }catch(e){ $("line").textContent = "连接断开，重试中…"; }
}

refresh();
setInterval(refresh, 3000);
if(window.initTouch) initTouch();
