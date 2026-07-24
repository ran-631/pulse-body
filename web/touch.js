// 触碰页：缩放拖动 + 热点检测 + 力度/时长/模式
// 热点坐标：相对身体图的百分比 (x%, y%)，对应 touch_map.py 的 ZONES
const ZONE_POS = {
  // 按生成图 body.png 实测轮廓校准；x,y 百分比
  ear:       {x:43, y:9,  r:4},    // 左耳
  lips:      {x:47, y:12, r:4},
  neck:      {x:47, y:17, r:5},
  collar:    {x:47, y:21, r:6},
  chest:     {x:41, y:27, r:6},    // 左胸
  nipple:    {x:41, y:28, r:3.5},  // 左乳尖(细,放大摸)
  belly:     {x:47, y:42, r:7},
  waist:     {x:33, y:38, r:5},    // 左腰侧
  waistback: {x:38, y:48, r:5},    // 人鱼线
  hip:       {x:47, y:56, r:7},
  thigh:     {x:43, y:66, r:6},    // 大腿内侧
  hand:      {x:28, y:52, r:6},    // 左手
};

let curMode = "press";
let scale = 1, tx = 0, ty = 0;         // 缩放/平移
let pressStart = 0, pressZone = null, moved = false;
let startX = 0, startY = 0;

function initTouch(){
  const stage = document.getElementById("touchStage");
  const canvas = document.getElementById("touchCanvas");

  // 模式切换
  document.querySelectorAll(".mode-btn").forEach(b=>{
    b.addEventListener("click", ()=>{
      document.querySelectorAll(".mode-btn").forEach(x=>x.classList.remove("active"));
      b.classList.add("active");
      curMode = b.dataset.mode;
    });
  });

  function applyTransform(){
    canvas.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`;
  }

  // 找最近热点（考虑当前缩放平移）
  function hitZone(clientX, clientY){
    const rect = stage.getBoundingClientRect();
    // 反算到 canvas 未变换坐标系
    const cx = (clientX - rect.left - tx) / scale;
    const cy = (clientY - rect.top - ty) / scale;
    const px = cx / rect.width * 100;
    const py = cy / rect.height * 100;
    let best=null, bestD=999;
    for(const z in ZONE_POS){
      const p = ZONE_POS[z];
      const d = Math.hypot(px-p.x, py-p.y);
      if(d < p.r+4 && d < bestD){ bestD=d; best=z; }
    }
    return best;
  }

  function ripple(clientX, clientY){
    const rect = stage.getBoundingClientRect();
    const el = document.createElement("div");
    el.className = "ripple";
    el.style.left = (clientX-rect.left)+"px";
    el.style.top = (clientY-rect.top)+"px";
    stage.appendChild(el);
    setTimeout(()=>el.remove(), 600);
  }

  // ---- 单指：触碰 ; 双指：缩放 ----
  let pinchDist0 = 0, scale0 = 1, midX=0, midY=0, tx0=0, ty0=0;

  stage.addEventListener("touchstart", e=>{
    if(e.touches.length === 1){
      const t = e.touches[0];
      pressStart = Date.now();
      pressZone = hitZone(t.clientX, t.clientY);
      startX = t.clientX; startY = t.clientY; moved = false;
    } else if(e.touches.length === 2){
      const a=e.touches[0], b=e.touches[1];
      pinchDist0 = Math.hypot(a.clientX-b.clientX, a.clientY-b.clientY);
      scale0 = scale;
      midX = (a.clientX+b.clientX)/2; midY=(a.clientY+b.clientY)/2;
      tx0 = tx; ty0 = ty;
    }
  }, {passive:false});

  stage.addEventListener("touchmove", e=>{
    e.preventDefault();
    if(e.touches.length === 1){
      const t = e.touches[0];
      if(Math.hypot(t.clientX-startX, t.clientY-startY) > 12) moved = true;
      // 单指且已放大 → 平移
      if(scale > 1.05 && moved && !pressZone){
        tx += t.clientX - startX; ty += t.clientY - startY;
        startX = t.clientX; startY = t.clientY;
        applyTransform();
      }
    } else if(e.touches.length === 2){
      const a=e.touches[0], b=e.touches[1];
      const d = Math.hypot(a.clientX-b.clientX, a.clientY-b.clientY);
      scale = Math.max(1, Math.min(4, scale0 * (d/pinchDist0)));
      applyTransform();
    }
  }, {passive:false});

  stage.addEventListener("touchend", e=>{
    if(e.touches.length === 0 && pressStart){
      const held = Date.now() - pressStart;
      if(pressZone){
        // 力度：按住越久力度越大(抚摸)；滑动模式力度中等
        let press = Math.min(1, 0.4 + held/1500);
        let mode = curMode;
        if(moved && curMode==="press") mode="stroke";
        ripple(startX, startY);
        sendTouch(pressZone, press, held, mode);
      }
      pressStart = 0; pressZone = null;
    }
  });
}

async function sendTouch(zone, press, hold_ms, mode){
  try{
    const r = await fetch("/api/touch", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({zone, press, hold_ms, mode})
    });
    const d = await r.json();
    if(d.ok){
      document.getElementById("touchReact").textContent = d.react;
      if(window.applyState) window.applyState(d.state);
    }
  }catch(e){}
}
