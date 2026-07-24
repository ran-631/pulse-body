// 触碰页：缩放拖动 + 热点检测 + 五种手势
const ZONE_POS = {
  // 按银发男人图校准 + 新增下面
  ear:       {x:41, y:7,  r:4},
  lips:      {x:50, y:10, r:4},
  neck:      {x:50, y:14, r:5},
  collar:    {x:50, y:18, r:6},
  chest:     {x:43, y:24, r:6},
  nipple:    {x:42, y:25, r:3.5},
  belly:     {x:50, y:36, r:7},
  waist:     {x:35, y:32, r:5},
  waistback: {x:65, y:32, r:5},
  hip:       {x:50, y:48, r:7},
  cock:      {x:50, y:53, r:5},
  thigh:     {x:44, y:62, r:7},
  hand:      {x:24, y:42, r:6},
};

let scale = 1, tx = 0, ty = 0;
let pressStart = 0, pressZone = null, moved = false;
let startX = 0, startY = 0;
let lastTapTime = 0, lastTapZone = null; // 双击检测

function initTouch(){
  const stage = document.getElementById("touchStage");
  const canvas = document.getElementById("touchCanvas");

  function applyTransform(){
    canvas.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`;
  }

  function hitZone(clientX, clientY){
    const rect = stage.getBoundingClientRect();
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

  // 小爱心动画
  function spawnHeart(clientX, clientY){
    const rect = stage.getBoundingClientRect();
    const el = document.createElement("div");
    el.className = "heart-float";
    el.textContent = "❤";
    el.style.left = (clientX-rect.left)+"px";
    el.style.top = (clientY-rect.top)+"px";
    stage.appendChild(el);
    setTimeout(()=>el.remove(), 800);
  }

  // 涟漪
  function ripple(clientX, clientY){
    const rect = stage.getBoundingClientRect();
    const el = document.createElement("div");
    el.className = "ripple";
    el.style.left = (clientX-rect.left)+"px";
    el.style.top = (clientY-rect.top)+"px";
    stage.appendChild(el);
    setTimeout(()=>el.remove(), 600);
  }

  // ---- 双指缩放 ----
  let pinchDist0 = 0, scale0 = 1;

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
    }
  }, {passive:false});

  stage.addEventListener("touchmove", e=>{
    e.preventDefault();
    if(e.touches.length === 1){
      const t = e.touches[0];
      if(Math.hypot(t.clientX-startX, t.clientY-startY) > 12) moved = true;
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
      const now = Date.now();

      if(pressZone){
        let mode, press;

        // 双击检测：两次点击间隔<400ms且同一区域
        if(now - lastTapTime < 400 && lastTapZone === pressZone && held < 300 && !moved){
          mode = "bite";  // 啃咬
          press = 0.8;
        } else if(moved){
          mode = "lick";  // 滑动=舔舐
          press = Math.min(1, 0.5 + held/2000);
        } else if(held >= 600){
          mode = "pinch"; // 长按=揉捏
          press = Math.min(1, 0.5 + held/1500);
        } else {
          mode = "press"; // 轻点=抚摸
          press = Math.min(0.6, 0.3 + held/2000);
        }

        ripple(startX, startY);
        spawnHeart(startX, startY);
        sendTouch(pressZone, press, held, mode);

        lastTapTime = now;
        lastTapZone = pressZone;
      } else {
        lastTapTime = 0;
        lastTapZone = null;
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
      // 显示模式+反应
      const modeNames = {press:"抚摸",pinch:"揉捏",lick:"舔舐",bite:"啃咬",stroke:"滑"};
      const mName = modeNames[d.mode||"press"] || d.mode || "";
      document.getElementById("touchReact").innerHTML =
        `<span class="mode-tag">${mName}</span> ${d.name}：${d.react}`;
      if(window.applyState) window.applyState(d.state);
    }
  }catch(e){}
}
