"use strict";

const $ = (id) => document.getElementById(id);
const canvas = $("gameCanvas");
const ctx = canvas.getContext("2d", { alpha: false });
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const dist2 = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
const rand = (a, b) => Math.random() * (b - a) + a;
const randi = (a, b) => Math.floor(rand(a, b + 1));

const UI = {
  day: $("dayValue"), time: $("timeValue"), cash: $("cashValue"), rep: $("repValue"), lives: $("livesValue"),
  served: $("servedValue"), servedProgress: $("servedProgress"), earned: $("earnedValue"), strikes: $("strikeValue"),
  orders: $("orderList"), rush: $("rushBadge"), carried: $("carriedDish"), route: $("stationRoute"),
  statusTitle: $("statusTitle"), statusText: $("statusText"), actionWrap: $("actionProgressWrap"), actionBar: $("actionProgress"), actionText: $("actionProgressText"),
  prompt: $("interactionPrompt"), promptTitle: $("promptTitle"), promptText: $("promptText"), toast: $("toast"),
  start: $("startOverlay"), management: $("managementOverlay"), quiz: $("quizOverlay"), help: $("helpOverlay"), end: $("endOverlay"),
  managementTitle: $("managementTitle"), managementSummary: $("managementSummary"), managementCash: $("managementCash"), dayReport: $("dayReport"), nextDay: $("nextDayBtn"),
  quizTag: $("quizTag"), questionEn: $("questionEn"), questionEs: $("questionEs"), answerGrid: $("answerGrid"), quizFeedback: $("quizFeedback"), continueQuiz: $("continueQuizBtn"),
  endIcon: $("endIcon"), endTitle: $("endTitle"), endText: $("endText"), endStats: $("endStats")
};

const recipes = {
  salad:  { name: "Green Salad", icon: "🥗", price: 14, route: ["fridge", "prep", "pass"] },
  burger: { name: "Bistro Burger", icon: "🍔", price: 21, route: ["fridge", "prep", "stove", "pass"] },
  pasta:  { name: "Hot Pasta", icon: "🍝", price: 19, route: ["fridge", "prep", "stove", "pass"] },
  soup:   { name: "Tomato Soup", icon: "🍲", price: 17, route: ["fridge", "prep", "stove", "pass"] },
  toast:  { name: "Chef Toast", icon: "🥪", price: 16, route: ["fridge", "prep", "stove", "pass"] }
};
const recipeKeys = Object.keys(recipes);

const stations = [
  { id:"fridge", name:"Refrigerador", icon:"🧊", x:-6.1, z:-4.45, w:1.45, d:1.2, h:2.4, color:"#5ba6dd", interact:{x:-6.1,z:-3.35}, baseTime:.7 },
  { id:"prep", name:"Mesa de preparación", icon:"🔪", x:-2.8, z:-4.45, w:2.55, d:1.2, h:1.05, color:"#c89962", interact:{x:-2.8,z:-3.35}, baseTime:2.55 },
  { id:"stove", name:"Estufa", icon:"🔥", x:.75, z:-4.45, w:2.05, d:1.2, h:1.12, color:"#697686", interact:{x:.75,z:-3.35}, baseTime:3.35 },
  { id:"pass", name:"Pase de servicio", icon:"🔔", x:4.65, z:-2.45, w:1.25, d:3.5, h:1.05, color:"#c78355", interact:{x:3.65,z:-2.45}, baseTime:.65 },
  { id:"sink", name:"Lavaplatos", icon:"💧", x:-6.05, z:-1.0, w:1.45, d:1.4, h:1.05, color:"#568ca6", interact:{x:-4.95,z:-1}, baseTime:1.2 },
  { id:"trash", name:"Basura", icon:"🗑️", x:-6.1, z:2.15, w:1.1, d:1.1, h:1.0, color:"#55606b", interact:{x:-4.95,z:2.15}, baseTime:.2 }
];
const stationById = Object.fromEntries(stations.map(s => [s.id, s]));

const tables = [
  {x:-2.2,z:1.65,w:1.45,d:1.25},{x:.3,z:2.75,w:1.45,d:1.25},{x:2.55,z:1.25,w:1.45,d:1.25},{x:-1.0,z:4.45,w:1.45,d:1.25},{x:2.1,z:4.15,w:1.45,d:1.25}
];
const tableSeats = tables.map((t,i)=>({x:t.x + (i%2?.85:-.85), z:t.z+.15}));
const obstacles = [
  ...stations.map(s=>({x:s.x,z:s.z,w:s.w,d:s.d})),
  ...tables.map(t=>({x:t.x,z:t.z,w:t.w+1.0,d:t.d+1.0}))
];

const quizBank = [
  {tag:"Area",en:"A rectangle is 12 cm long and 7 cm wide. What is its area?",es:"Un rectángulo mide 12 cm por 7 cm. ¿Cuál es su área?",options:["19 cm²","38 cm²","84 cm²","96 cm²"],correct:2,explain:"A = b·h = 12·7 = 84 cm²."},
  {tag:"Area",en:"A square has side length 9 m. What is its area?",es:"Un cuadrado tiene lado de 9 m. ¿Cuál es su área?",options:["18 m²","36 m²","72 m²","81 m²"],correct:3,explain:"A = s² = 9² = 81 m²."},
  {tag:"Triangle",en:"A triangle has base 14 cm and height 8 cm. Find its area.",es:"Un triángulo tiene base 14 cm y altura 8 cm. Halla su área.",options:["44 cm²","56 cm²","88 cm²","112 cm²"],correct:1,explain:"A = (b·h)/2 = 56 cm²."},
  {tag:"Trapezoid",en:"A trapezoid has bases 8 cm and 14 cm, and height 5 cm. Find its area.",es:"Un trapecio tiene bases 8 cm y 14 cm, y altura 5 cm. Halla su área.",options:["44 cm²","50 cm²","55 cm²","110 cm²"],correct:2,explain:"A = ((B+b)h)/2 = 55 cm²."},
  {tag:"Circle",en:"A circle has radius 4 cm. What is its exact area?",es:"Un círculo tiene radio 4 cm. ¿Cuál es su área exacta?",options:["4π cm²","8π cm²","16π cm²","32π cm²"],correct:2,explain:"A = πr² = 16π cm²."},
  {tag:"Circle",en:"A circle has diameter 10 m. What is its exact circumference?",es:"Un círculo tiene diámetro 10 m. ¿Cuál es su circunferencia exacta?",options:["5π m","10π m","20π m","25π m"],correct:1,explain:"C = πd = 10π m."},
  {tag:"Semicircle",en:"A semicircle has radius 6 cm. What is its area?",es:"Un semicírculo tiene radio 6 cm. ¿Cuál es su área?",options:["6π cm²","12π cm²","18π cm²","36π cm²"],correct:2,explain:"A = πr²/2 = 18π cm²."},
  {tag:"Shaded Area",en:"A 10×8 rectangle contains an unshaded 4×3 rectangle. What is the shaded area?",es:"Un rectángulo 10×8 contiene un rectángulo sin sombrear 4×3. ¿Área sombreada?",options:["12 cm²","56 cm²","68 cm²","80 cm²"],correct:2,explain:"80 − 12 = 68 cm²."},
  {tag:"Shaded Area",en:"A square has side 12 cm. A circle of radius 3 cm is removed. What remains?",es:"Un cuadrado tiene lado 12 cm. Se retira un círculo de radio 3 cm. ¿Qué área queda?",options:["144−3π","144−6π","144−9π","132π"],correct:2,explain:"12² − π·3² = 144 − 9π."},
  {tag:"Shaded Area",en:"A ring has outer radius 5 cm and inner radius 2 cm. Find its area.",es:"Un anillo tiene radio exterior 5 cm e interior 2 cm. Halla su área.",options:["3π cm²","7π cm²","21π cm²","29π cm²"],correct:2,explain:"π(25−4)=21π cm²."},
  {tag:"Perimeter",en:"A rectangle measures 9 cm by 5 cm. What is its perimeter?",es:"Un rectángulo mide 9 cm por 5 cm. ¿Cuál es su perímetro?",options:["14 cm","28 cm","45 cm","90 cm"],correct:1,explain:"P = 2(9+5) = 28 cm."},
  {tag:"Triangle",en:"A triangle has area 45 cm² and base 10 cm. What is its height?",es:"Un triángulo tiene área 45 cm² y base 10 cm. ¿Cuál es su altura?",options:["4.5 cm","8 cm","9 cm","18 cm"],correct:2,explain:"45=(10h)/2 → h=9 cm."},
  {tag:"Circle",en:"A circle has area 49π cm². What is its radius?",es:"Un círculo tiene área 49π cm². ¿Cuál es su radio?",options:["3.5 cm","7 cm","14 cm","49 cm"],correct:1,explain:"πr²=49π → r=7 cm."},
  {tag:"Sector",en:"A 90° sector has radius 8 cm. What is its exact area?",es:"Un sector de 90° tiene radio 8 cm. ¿Cuál es su área exacta?",options:["8π cm²","16π cm²","32π cm²","64π cm²"],correct:1,explain:"One quarter of π·8² is 16π cm²."},
  {tag:"Shaded Area",en:"A 10×10 square has four 2×2 corner squares removed. What area remains?",es:"A un cuadrado 10×10 se le quitan cuatro cuadrados 2×2. ¿Qué área queda?",options:["68","76","84","92"],correct:2,explain:"100 − 4(4) = 84."},
  {tag:"Concept",en:"Which unit is appropriate for area?",es:"¿Qué unidad es apropiada para medir área?",options:["cm","cm²","cm³","degrees"],correct:1,explain:"Area uses square units, such as cm²."},
  {tag:"Composite Area",en:"Two non-overlapping rectangles are 6×4 and 3×2. What is their total area?",es:"Dos rectángulos sin superposición miden 6×4 y 3×2. ¿Área total?",options:["18","24","30","36"],correct:2,explain:"24+6=30 square units."},
  {tag:"Concept",en:"For a shaded region with a hole, what is the usual strategy?",es:"Para una región sombreada con un hueco, ¿qué estrategia se usa normalmente?",options:["Add both areas","Multiply areas","Outer area − inner area","Use perimeter only"],correct:2,explain:"Shaded area = outer area − removed area."}
];

const logoImg = new Image();
logoImg.src = "../../assets/logo_colegio_transparente.png";

const keys = new Set();
let W = innerWidth, H = innerHeight, DPR = 1;
let lastTime = performance.now();
let faceQueue = [];
let spriteQueue = [];
let toastTimer = 0;
let actionId = 0;

const game = {
  started:false, running:false, paused:true, day:1, maxDays:5, shiftLength:75, timeLeft:75,
  cash:100, rep:70, lives:3, strikes:0, servedToday:0, earnedToday:0, totalServed:0, totalEarned:0,
  target:5, spawnTimer:2, orders:[], customers:[], nextOrderId:1, nextCustomerId:1, carried:null,
  action:null, afterQuiz:null, quizQuestion:null, quizAnswered:false, helperTimer:12,
  upgrades:{prep:1,stove:1,decor:1,server:0},
  player:{x:-1.5,z:.1,y:0,dir:0,speed:3.15},
  camera:{x:0,z:0},
  stats:{walkouts:0,quizRight:0,quizTotal:0},
  best:Number(localStorage.getItem("robledoBistro3DBest")||0)
};

function resize(){
  DPR = Math.min(devicePixelRatio || 1, 2);
  W = innerWidth; H = innerHeight;
  canvas.width = Math.round(W*DPR); canvas.height = Math.round(H*DPR);
  canvas.style.width=W+"px"; canvas.style.height=H+"px";
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
addEventListener("resize", resize); resize();

function project(p){
  const scale = Math.min(W,H) / 17.5;
  const x = p.x - game.camera.x;
  const z = p.z - game.camera.z;
  return {
    x: W*.5 + (x-z)*scale*.88,
    y: H*.56 + (x+z)*scale*.44 - p.y*scale*.94,
    depth: x+z+p.y*.12,
    scale
  };
}

function hexToRgb(hex){
  const h=hex.replace("#",""); const v=parseInt(h.length===3?h.split("").map(c=>c+c).join(""):h,16);
  return [(v>>16)&255,(v>>8)&255,v&255];
}
function shade(hex, factor){
  const [r,g,b]=hexToRgb(hex); const f=(v)=>clamp(Math.round(v*factor),0,255);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
function poly(points,color,depth,stroke="rgba(4,10,18,.28)"){
  faceQueue.push({points:points.map(project),color,depth,stroke});
}
function quad(a,b,c,d,color,stroke){
  const depth=(a.x+a.z+b.x+b.z+c.x+c.z+d.x+d.z)/4 + (a.y+b.y+c.y+d.y)/16;
  poly([a,b,c,d],color,depth,stroke);
}
function addBox(x,y,z,w,h,d,color){
  const x0=x-w/2,x1=x+w/2,y0=y,y1=y+h,z0=z-d/2,z1=z+d/2;
  quad({x:x0,y:y1,z:z0},{x:x1,y:y1,z:z0},{x:x1,y:y1,z:z1},{x:x0,y:y1,z:z1},shade(color,1.18));
  quad({x:x0,y:y0,z:z1},{x:x1,y:y0,z:z1},{x:x1,y:y1,z:z1},{x:x0,y:y1,z:z1},shade(color,.86));
  quad({x:x1,y:y0,z:z0},{x:x1,y:y0,z:z1},{x:x1,y:y1,z:z1},{x:x1,y:y1,z:z0},shade(color,.73));
  quad({x:x0,y:y0,z:z0},{x:x0,y:y1,z:z0},{x:x0,y:y1,z:z1},{x:x0,y:y0,z:z1},shade(color,.64));
  quad({x:x0,y:y0,z:z0},{x:x1,y:y0,z:z0},{x:x1,y:y1,z:z0},{x:x0,y:y1,z:z0},shade(color,.58));
}
function addDiamondFloor(x,z,size,color){
  quad({x:x-size/2,y:.015,z:z-size/2},{x:x+size/2,y:.015,z:z-size/2},{x:x+size/2,y:.015,z:z+size/2},{x:x-size/2,y:.015,z:z+size/2},color,"rgba(255,255,255,.025)");
}
function drawFaces(){
  faceQueue.sort((a,b)=>a.depth-b.depth);
  for(const f of faceQueue){
    ctx.beginPath(); ctx.moveTo(f.points[0].x,f.points[0].y);
    for(let i=1;i<f.points.length;i++) ctx.lineTo(f.points[i].x,f.points[i].y);
    ctx.closePath(); ctx.fillStyle=f.color; ctx.fill();
    if(f.stroke){ctx.strokeStyle=f.stroke;ctx.lineWidth=1;ctx.stroke();}
  }
  faceQueue.length=0;
}
function textSprite(x,y,z,text,sub,color="#f7fbff",size=12){
  spriteQueue.push({p:project({x,y,z}),text,sub,color,size,depth:x+z+y*.1});
}
function drawSprites(){
  spriteQueue.sort((a,b)=>a.depth-b.depth);
  ctx.textAlign="center"; ctx.textBaseline="middle";
  for(const s of spriteQueue){
    ctx.font=`800 ${s.size}px Inter,system-ui,sans-serif`;
    const tw=ctx.measureText(s.text).width;
    ctx.fillStyle="rgba(4,10,18,.78)"; roundRect(ctx,s.p.x-tw/2-7,s.p.y-9,tw+14,18,7);ctx.fill();
    ctx.fillStyle=s.color;ctx.fillText(s.text,s.p.x,s.p.y);
    if(s.sub){ctx.font="700 9px Inter,system-ui,sans-serif";ctx.fillStyle="#a9bbd2";ctx.fillText(s.sub,s.p.x,s.p.y+14);}
  }
  spriteQueue.length=0;
}
function roundRect(c,x,y,w,h,r){
  const rr=Math.min(r,w/2,h/2); c.beginPath(); c.moveTo(x+rr,y); c.arcTo(x+w,y,x+w,y+h,rr); c.arcTo(x+w,y+h,x,y+h,rr); c.arcTo(x,y+h,x,y,rr); c.arcTo(x,y,x+w,y,rr); c.closePath();
}

function renderWorld(){
  ctx.fillStyle="#07101d";ctx.fillRect(0,0,W,H);
  const grad=ctx.createLinearGradient(0,0,0,H);grad.addColorStop(0,"#142d4c");grad.addColorStop(.5,"#0b1728");grad.addColorStop(1,"#050b13");ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
  game.camera.x=lerp(game.camera.x,game.player.x*.12,.07); game.camera.z=lerp(game.camera.z,game.player.z*.10,.07);

  for(let x=-8;x<8;x++) for(let z=-6;z<6;z++) addDiamondFloor(x+.5,z+.5,1,(x+z)%2===0?"#24384b":"#213446");
  quad({x:-8,y:0,z:-5.98},{x:8,y:0,z:-5.98},{x:8,y:3.6,z:-5.98},{x:-8,y:3.6,z:-5.98},"#263b51");
  quad({x:-7.98,y:0,z:-6},{x:-7.98,y:0,z:6},{x:-7.98,y:3.6,z:6},{x:-7.98,y:3.6,z:-6},"#1d3044");
  addBox(0,.02,5.92,16,.15,.16,"#38556d"); addBox(7.92,.02,0,.16,.15,12,"#38556d");

  addBox(-5.8,.01,-5.78,3.1,.22,.25,"#58e6b1");
  addBox(4.5,.9,-5.72,3.0,1.8,.18,"#e8edf2");

  for(const s of stations){
    addBox(s.x,0,s.z,s.w,s.h,s.d,s.color);
    if(s.id==="fridge"){addBox(s.x+.34,.18,s.z+.615,.05,1.8,.04,"#dce9ef");addBox(s.x-.28,1.22,s.z+.62,.6,.06,.05,"#92c9e4");}
    if(s.id==="prep"){addBox(s.x,1.02,s.z,2.25,.08,1.05,"#e4b778"); addBox(s.x-.55,1.11,s.z-.05,.52,.08,.4,"#8ccf79");}
    if(s.id==="stove"){for(let i=-1;i<=1;i+=2){addBox(s.x+i*.48,1.11,s.z, .62,.06,.62,"#242d35");}}
    if(s.id==="pass"){addBox(s.x,1.03,s.z,1.1,.1,3.2,"#e5aa6f");}
    if(s.id==="sink"){addBox(s.x,1.02,s.z,1.08,.08,1.0,"#a9c9d5");}
    textSprite(s.x,s.h+.22,s.z,`${s.icon} ${s.name}`,null,"#ffffff",10);
  }

  for(const [i,t] of tables.entries()){
    addBox(t.x,.02,t.z,t.w,.72,t.d,"#8d6247"); addBox(t.x,.73,t.z,t.w+.08,.08,t.d+.08,"#bc875d");
    addBox(t.x-.9,.02,t.z,.38,.58,.48,"#536779"); addBox(t.x+.9,.02,t.z,.38,.58,.48,"#536779");
    if(i===0) textSprite(t.x,1.05,t.z,"DINING",null,"#9eb0c8",9);
  }

  addBox(7.7,.02,4.8,.18,2.8,2.0,"#a46b4d"); textSprite(7.35,2.9,4.8,"ENTRADA",null,"#ffd166",10);
  drawPerson(game.player.x,game.player.z,"#58e6b1",true,game.player.dir);
  for(const c of game.customers) drawCustomer(c);

  drawFaces();
  drawStationEffects();
  drawWorldLogo();
  drawSprites();
}

function drawPerson(x,z,color,isPlayer=false,dir=0){
  addBox(x,0,z,.48,.28,.42,"#253548");
  addBox(x,.28,z,.52,.72,.38,color);
  addBox(x,.98,z,.44,.42,.44,isPlayer?"#f0c6a4":"#d7aa8c");
  if(isPlayer){addBox(x,1.39,z,.54,.10,.5,"#f5f7f8");addBox(x+.16,1.49,z,.34,.07,.34,"#f5f7f8");}
  const step=Math.sin(performance.now()/120)*.08;
  if(isPlayer && (keys.has("KeyW")||keys.has("KeyA")||keys.has("KeyS")||keys.has("KeyD")||keys.has("ArrowUp")||keys.has("ArrowDown")||keys.has("ArrowLeft")||keys.has("ArrowRight"))){
    addBox(x-.18,.05,z+step,.14,.38,.15,"#1e2938");addBox(x+.18,.05,z-step,.14,.38,.15,"#1e2938");
  }
}
function drawCustomer(c){
  const palette=["#e77b72","#6f9fe8","#c58be1","#e4b45e","#68b58a","#d984b0"];
  drawPerson(c.x,c.z,palette[c.color%palette.length],false,c.dir);
  const order=game.orders.find(o=>o.id===c.orderId);
  if(order && (order.status==="waiting"||order.status==="cooking")){
    const r=recipes[order.recipe];
    textSprite(c.x,1.72,c.z,`${r.icon} ${Math.max(0,Math.ceil(order.patience))}%`,null,order.patience<25?"#ff858d":order.patience<50?"#ffd166":"#ffffff",10);
  } else if(c.state==="eating") textSprite(c.x,1.72,c.z,"😋",null,"#5ee17f",12);
  else if(c.state==="angry") textSprite(c.x,1.72,c.z,"😠",null,"#ff6f78",12);
}
function drawStationEffects(){
  const now=performance.now()/1000;
  const stove=stationById.stove;
  for(let i=0;i<3;i++){
    const p=project({x:stove.x-.45+i*.45+Math.sin(now*2+i)*.08,y:1.42+((now*.35+i*.25)%1)*.75,z:stove.z});
    ctx.beginPath();ctx.arc(p.x,p.y,3+((now+i)%1)*3,0,Math.PI*2);ctx.fillStyle="rgba(235,241,246,.22)";ctx.fill();
  }
  if(game.action){
    const s=stationById[game.action.station]; if(s){
      const p=project({x:s.interact.x,y:.08,z:s.interact.z});ctx.strokeStyle="rgba(88,230,177,.9)";ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(p.x,p.y,26,12,0,0,Math.PI*2);ctx.stroke();
    }
  }
}
function drawWorldLogo(){
  if(!logoImg.complete) return;
  const p=project({x:4.5,y:2.15,z:-5.85});
  const size=clamp(Math.min(W,H)*.075,42,76);
  ctx.save();ctx.fillStyle="rgba(255,255,255,.94)";roundRect(ctx,p.x-size*.62,p.y-size*.62,size*1.24,size*1.24,10);ctx.fill();ctx.drawImage(logoImg,p.x-size*.5,p.y-size*.5,size,size);ctx.restore();
}

function canMoveTo(x,z){
  const r=.31; if(x<-7.4||x>7.4||z<-5.35||z>5.35) return false;
  for(const o of obstacles) if(x>o.x-o.w/2-r&&x<o.x+o.w/2+r&&z>o.z-o.d/2-r&&z<o.z+o.d/2+r) return false;
  return true;
}
function updatePlayer(dt){
  if(game.action) return;
  let dx=0,dz=0;
  if(keys.has("KeyW")||keys.has("ArrowUp")) dz-=1;
  if(keys.has("KeyS")||keys.has("ArrowDown")) dz+=1;
  if(keys.has("KeyA")||keys.has("ArrowLeft")) dx-=1;
  if(keys.has("KeyD")||keys.has("ArrowRight")) dx+=1;
  if(!dx&&!dz) return;
  const len=Math.hypot(dx,dz); dx/=len;dz/=len;
  const sprint=keys.has("ShiftLeft")||keys.has("ShiftRight"); const speed=game.player.speed*(sprint?1.48:1);
  game.player.dir=Math.atan2(dx,dz);
  const nx=game.player.x+dx*speed*dt,nz=game.player.z+dz*speed*dt;
  if(canMoveTo(nx,game.player.z)) game.player.x=nx;
  if(canMoveTo(game.player.x,nz)) game.player.z=nz;
}
function nearestStation(){
  let best=null,bestD=99;
  for(const s of stations){const d=dist2(game.player,s.interact);if(d<bestD){best=s;bestD=d;}}
  return bestD<1.45?best:null;
}
function updatePrompt(){
  if(!game.running||game.paused||game.action){UI.prompt.classList.add("hidden");return;}
  const s=nearestStation(); if(!s){UI.prompt.classList.add("hidden");return;}
  UI.prompt.classList.remove("hidden"); UI.promptTitle.textContent=s.name;
  if(s.id==="fridge"&&!game.carried) UI.promptText.textContent="Tomar el pedido más urgente";
  else if(s.id==="trash") UI.promptText.textContent=game.carried?"Desechar plato actual":"Sin plato para desechar";
  else if(game.carried){const o=game.carried;const expected=recipes[o.recipe].route[o.stage];UI.promptText.textContent=expected===s.id?"Continuar receta":"Esta no es la estación siguiente";}
  else UI.promptText.textContent="No tienes un plato activo";
}

function interact(){
  if(!game.running||game.paused||game.action) return;
  const s=nearestStation(); if(!s) return showToast("Acércate a una estación para interactuar.","bad");
  if(s.id==="trash"){discardDish();return;}
  if(s.id==="sink"){showToast("La zona de lavado mantiene la cocina operativa. No necesitas usarla ahora.");return;}
  if(!game.carried){
    if(s.id!=="fridge") return showToast("Primero toma un ticket en el refrigerador.","bad");
    const order=game.orders.filter(o=>o.status==="waiting").sort((a,b)=>a.patience-b.patience)[0];
    if(!order) return showToast("No hay pedidos pendientes. Aprovecha para moverte o revisar la sala.");
    game.carried=order;order.status="cooking";order.stage=0;beginAction(s,order);
    return;
  }
  const order=game.carried, recipe=recipes[order.recipe], expected=recipe.route[order.stage];
  if(expected!==s.id) return showToast(`Ruta incorrecta. Siguiente: ${stationById[expected].name}.`,"bad");
  beginAction(s,order);
}
function stationDuration(s){
  let t=s.baseTime;
  if(s.id==="prep") t*=Math.pow(.88,game.upgrades.prep-1);
  if(s.id==="stove") t*=Math.pow(.88,game.upgrades.stove-1);
  return Math.max(.35,t);
}
function beginAction(station,order){
  const duration=stationDuration(station); const id=++actionId;
  game.action={id,station:station.id,orderId:order.id,duration,elapsed:0};
  UI.actionWrap.classList.remove("hidden");UI.actionBar.style.width="0%";UI.actionText.textContent=`${station.icon} ${station.name}...`;
  UI.statusTitle.textContent=`Trabajando: ${station.name}`;UI.statusText.textContent="Mantente atento a la paciencia de la cola.";
}
function updateAction(dt){
  if(!game.action) return;
  game.action.elapsed+=dt; const p=clamp(game.action.elapsed/game.action.duration,0,1);UI.actionBar.style.width=`${p*100}%`;
  if(p>=1){
    const a=game.action;game.action=null;UI.actionWrap.classList.add("hidden");
    const order=game.orders.find(o=>o.id===a.orderId);if(!order||order.status!=="cooking"){updateCarriedUI();return;}
    const recipe=recipes[order.recipe];order.stage++;
    if(order.stage>=recipe.route.length){serveOrder(order);} else {
      const next=stationById[recipe.route[order.stage]];showToast(`${recipe.icon} Paso listo. Ahora: ${next.name}.`,"good");
      UI.statusTitle.textContent=`${recipe.name} en proceso`;UI.statusText.textContent=`Siguiente estación: ${next.name}.`;
    }
    updateCarriedUI();
  }
}
function discardDish(){
  if(!game.carried) return showToast("No tienes un plato para desechar.");
  const o=game.carried;o.status="waiting";o.stage=0;o.patience=Math.max(8,o.patience-15);game.carried=null;game.cash=Math.max(-50,game.cash-4);
  showToast("Plato descartado: -$4 y el cliente perdió paciencia.","bad");updateCarriedUI();updateHUD();
}

function spawnOrder(){
  if(game.orders.filter(o=>o.status==="waiting"||o.status==="cooking").length>=7) return;
  const recipe=recipeKeys[randi(0,recipeKeys.length-1)]; const maxPatience=100+(game.upgrades.decor-1)*5;
  const customer={id:game.nextCustomerId++,x:7.15,z:4.9,targetX:5.75,targetZ:4.4,state:"queue",speed:1.35,color:randi(0,5),orderId:game.nextOrderId,seat:null,eatTimer:0,dir:Math.PI};
  const order={id:game.nextOrderId++,recipe,patience:maxPatience,maxPatience,status:"waiting",stage:0,customerId:customer.id,createdAt:game.timeLeft};
  game.orders.push(order);game.customers.push(customer);reflowQueue();renderOrders();
}
function reflowQueue(){
  const active=game.orders.filter(o=>o.status==="waiting"||o.status==="cooking").sort((a,b)=>a.id-b.id);
  active.forEach((o,i)=>{const c=game.customers.find(c=>c.id===o.customerId);if(c&&c.state==="queue"){c.targetX=5.9;c.targetZ=3.6-i*.78;}});
}
function updateOrders(dt){
  const drain=1.85+game.day*.10;
  for(const o of game.orders){
    if(o.status!=="waiting"&&o.status!=="cooking") continue;
    o.patience-=drain*dt;
    if(o.patience<=0) customerWalkout(o);
  }
  renderOrders();
}
function customerWalkout(order){
  if(order.status==="angry"||order.status==="served") return;
  order.status="angry";order.patience=0;
  if(game.carried&&game.carried.id===order.id){game.carried=null;game.action=null;UI.actionWrap.classList.add("hidden");}
  const c=game.customers.find(c=>c.id===order.customerId);if(c){c.state="angry";c.targetX=7.3;c.targetZ=4.9;}
  game.rep=clamp(game.rep-6,0,100);game.strikes++;game.stats.walkouts++;
  showToast("😠 Un cliente se fue. Reputación -6.","bad");reflowQueue();updateCarriedUI();updateHUD();
  if(game.strikes>=3){game.strikes=0;loseLife("Tres clientes abandonaron el restaurante sin ser atendidos.");}
}
function serveOrder(order,helper=false){
  if(order.status!=="cooking"&&order.status!=="waiting") return;
  const r=recipes[order.recipe]; const patienceRatio=clamp(order.patience/order.maxPatience,0,1); const tip=Math.round(r.price*(.05+.25*patienceRatio));
  const revenue=helper?Math.round((r.price+tip)*.72):r.price+tip;
  order.status="served";game.cash+=revenue;game.earnedToday+=revenue;game.totalEarned+=revenue;game.servedToday++;game.totalServed++;
  game.rep=clamp(game.rep+(patienceRatio>.55?2:1),0,100);
  const c=game.customers.find(c=>c.id===order.customerId);if(c){c.state="eating";c.seat=tableSeats[(c.id-1)%tableSeats.length];c.targetX=c.seat.x;c.targetZ=c.seat.z;c.eatTimer=5+Math.random()*3;}
  if(game.carried&&game.carried.id===order.id) game.carried=null;
  showToast(helper?`🧑‍🍳 Ayudante sirvió ${r.name}: +$${revenue}.`:`${r.icon} ${r.name} servido: +$${revenue}.`,"good");
  reflowQueue();updateCarriedUI();updateHUD();renderOrders();
}
function updateCustomers(dt){
  for(const c of game.customers){
    let tx=c.targetX,tz=c.targetZ;
    const dx=tx-c.x,dz=tz-c.z,d=Math.hypot(dx,dz);
    if(d>.03){const step=Math.min(d,c.speed*dt);c.x+=dx/d*step;c.z+=dz/d*step;c.dir=Math.atan2(dx,dz);}
    if(c.state==="eating"&&d<.18){c.eatTimer-=dt;if(c.eatTimer<=0){c.state="leaving";c.targetX=7.3;c.targetZ=4.9;}}
  }
  game.customers=game.customers.filter(c=>!((c.state==="leaving"||c.state==="angry")&&c.x>7.15&&c.z>4.65));
}

function updateHelper(dt){
  if(!game.upgrades.server) return;
  game.helperTimer-=dt;if(game.helperTimer>0)return;
  game.helperTimer=Math.max(11,18-game.day*.6);
  const o=game.orders.filter(o=>o.status==="waiting").sort((a,b)=>a.patience-b.patience)[0];if(!o)return;
  serveOrder(o,true);
}

function startCampaign(){
  resetGame();game.started=true;UI.start.classList.remove("visible");startDay();
}
function resetGame(){
  Object.assign(game,{running:false,paused:true,day:1,timeLeft:75,cash:100,rep:70,lives:3,strikes:0,servedToday:0,earnedToday:0,totalServed:0,totalEarned:0,target:5,spawnTimer:1.4,orders:[],customers:[],nextOrderId:1,nextCustomerId:1,carried:null,action:null,afterQuiz:null,helperTimer:12,upgrades:{prep:1,stove:1,decor:1,server:0},stats:{walkouts:0,quizRight:0,quizTotal:0}});
  game.player.x=-1.5;game.player.z=.1;game.camera.x=0;game.camera.z=0;
  [UI.management,UI.quiz,UI.help,UI.end].forEach(o=>o.classList.remove("visible"));updateHUD();updateCarriedUI();renderOrders();
}
function startDay(){
  game.running=true;game.paused=false;game.timeLeft=game.shiftLength;game.servedToday=0;game.earnedToday=0;game.strikes=0;game.target=4+game.day;game.orders=[];game.customers=[];game.carried=null;game.action=null;game.spawnTimer=1.2;game.helperTimer=10;
  game.player.x=-1.5;game.player.z=.1;UI.management.classList.remove("visible");
  UI.statusTitle.textContent=`Día ${game.day}: servicio abierto`;UI.statusText.textContent="Toma el primer pedido en el refrigerador y sigue su receta.";
  showToast(`Día ${game.day}. Objetivo: servir ${game.target} pedidos.`,"good");updateHUD();updateCarriedUI();renderOrders();
}
function finishDay(){
  if(!game.running)return;game.running=false;game.paused=true;game.action=null;UI.actionWrap.classList.add("hidden");
  const success=game.servedToday>=game.target;
  if(success){game.rep=clamp(game.rep+4,0,100);showManagement(true);} else {
    game.rep=clamp(game.rep-5,0,100);
    loseLife(`No alcanzaste el objetivo del día (${game.servedToday}/${game.target}).`,()=>showManagement(false));
  }
}
function showManagement(success){
  game.running=false;game.paused=true;UI.management.classList.add("visible");UI.managementCash.textContent=`$${game.cash}`;
  UI.managementTitle.textContent=game.day>=game.maxDays?"Cierre de campaña":"Administración del restaurante";
  UI.managementSummary.textContent=success?"Turno completado. Puedes reinvertir antes de continuar.":"El turno quedó por debajo de la meta. Ajusta tu operación para recuperarte.";
  UI.dayReport.innerHTML=`<div class="report-stat"><span>SERVIDOS</span><strong>${game.servedToday}/${game.target}</strong></div><div class="report-stat"><span>INGRESOS</span><strong>$${game.earnedToday}</strong></div><div class="report-stat"><span>REPUTACIÓN</span><strong>${game.rep}</strong></div><div class="report-stat"><span>VIDAS</span><strong>${"❤️".repeat(game.lives)||"—"}</strong></div>`;
  UI.nextDay.textContent=game.day>=game.maxDays?"VER RESULTADOS":"COMENZAR SIGUIENTE DÍA";updateUpgradeUI();
}
function nextDay(){
  if(game.day>=game.maxDays){endGame(game.lives>0&&game.rep>=45);return;}
  game.day++;startDay();
}
function loseLife(reason,after=null){
  if(game.paused&&UI.quiz.classList.contains("visible"))return;
  game.lives=Math.max(0,game.lives-1);game.paused=true;game.afterQuiz=after;updateHUD();
  UI.quiz.classList.add("visible");UI.quizFeedback.textContent="";UI.quizFeedback.className="quiz-feedback";UI.continueQuiz.classList.add("hidden");game.quizAnswered=false;
  const q=quizBank[randi(0,quizBank.length-1)];game.quizQuestion=q;game.stats.quizTotal++;UI.quizTag.textContent=q.tag;UI.questionEn.textContent=q.en;UI.questionEs.textContent=q.es;UI.answerGrid.innerHTML="";
  q.options.forEach((opt,i)=>{const b=document.createElement("button");b.className="answer-btn";b.type="button";b.textContent=`${String.fromCharCode(65+i)}. ${opt}`;b.onclick=()=>answerQuiz(i,b);UI.answerGrid.appendChild(b);});
  UI.quizFeedback.textContent=`Motivo: ${reason}`;
}
function answerQuiz(index,button){
  if(game.quizAnswered)return;game.quizAnswered=true;const q=game.quizQuestion;const buttons=[...UI.answerGrid.children];buttons.forEach(b=>b.disabled=true);buttons[q.correct].classList.add("correct");
  if(index===q.correct){game.lives=Math.min(3,game.lives+1);game.rep=clamp(game.rep+2,0,100);game.stats.quizRight++;for(const o of game.orders)if(o.status==="waiting"||o.status==="cooking")o.patience=Math.min(o.maxPatience,o.patience+15);UI.quizFeedback.className="quiz-feedback good";UI.quizFeedback.textContent=`✓ Vida recuperada. ${q.explain}`;}
  else{button.classList.add("wrong");UI.quizFeedback.className="quiz-feedback bad";UI.quizFeedback.textContent=`✗ La vida permanece perdida. ${q.explain}`;}
  updateHUD();UI.continueQuiz.classList.remove("hidden");
}
function continueAfterQuiz(){
  UI.quiz.classList.remove("visible");
  if(game.lives<=0){endGame(false);return;}
  const after=game.afterQuiz;game.afterQuiz=null;if(after){after();return;}game.paused=false;
}
function endGame(win){
  game.running=false;game.paused=true;UI.management.classList.remove("visible");UI.quiz.classList.remove("visible");UI.end.classList.add("visible");
  const score=Math.max(0,Math.round(game.cash+game.rep*7+game.totalServed*28+game.lives*150-game.stats.walkouts*20));if(score>game.best){game.best=score;localStorage.setItem("robledoBistro3DBest",String(score));}
  UI.endIcon.textContent=win?"🏆":"🍽️";UI.endTitle.textContent=win?"¡Bistro consolidado!":"Fin de operaciones";
  UI.endText.textContent=win?"Completaste los cinco días manteniendo una operación viable. Tus decisiones de servicio y reinversión sostuvieron el restaurante.":"La campaña terminó, pero puedes reiniciar y cambiar tu estrategia de servicio, mejoras y prioridades.";
  UI.endStats.innerHTML=`<div class="end-stat"><span>PUNTUACIÓN</span><strong>${score}</strong></div><div class="end-stat"><span>MEJOR</span><strong>${game.best}</strong></div><div class="end-stat"><span>PEDIDOS</span><strong>${game.totalServed}</strong></div><div class="end-stat"><span>CAJA</span><strong>$${game.cash}</strong></div><div class="end-stat"><span>REP</span><strong>${game.rep}</strong></div><div class="end-stat"><span>QUIZ</span><strong>${game.stats.quizRight}/${game.stats.quizTotal}</strong></div>`;
}

function upgradeCost(type){
  const l=game.upgrades[type];if(type==="server")return l?0:140;if(type==="prep")return 70+(l-1)*55;if(type==="stove")return 85+(l-1)*65;if(type==="decor")return 65+(l-1)*50;return 999;
}
function buyUpgrade(type){
  if(type==="server"&&game.upgrades.server)return showToast("Ya contrataste al ayudante.");
  if(type!=="server"&&game.upgrades[type]>=4)return showToast("Esta mejora ya está al máximo.");
  const cost=upgradeCost(type);if(game.cash<cost)return showToast("No tienes caja suficiente para esa mejora.","bad");
  game.cash-=cost;if(type==="server")game.upgrades.server=1;else game.upgrades[type]++;UI.managementCash.textContent=`$${game.cash}`;updateUpgradeUI();updateHUD();showToast("Mejora comprada.","good");
}
function updateUpgradeUI(){
  const map=["prep","stove","decor","server"];
  for(const type of map){const l=game.upgrades[type],cost=upgradeCost(type);const btn=document.querySelector(`[data-upgrade="${type}"]`);const costEl=$(`${type}UpgradeCost`),textEl=$(`${type}UpgradeText`);if(!btn)continue;
    if(type==="server"){textEl.textContent=l?"Contratado · apoyo automático":"No contratado · apoyo automático";costEl.textContent=l?"LISTO":`$${cost}`;btn.disabled=!!l;}
    else{const max=l>=4;textEl.textContent=`Nivel ${l} · ${type==="decor"?"+5 paciencia base":"-12% tiempo por nivel"}`;costEl.textContent=max?"MAX":`$${cost}`;btn.disabled=max;}
  }
}

function updateHUD(){
  UI.day.textContent=`${game.day} / ${game.maxDays}`;UI.time.textContent=formatTime(game.timeLeft);UI.cash.textContent=`$${Math.round(game.cash)}`;UI.rep.textContent=Math.round(game.rep);UI.lives.textContent="❤️".repeat(game.lives)||"—";
  UI.served.textContent=`${game.servedToday} / ${game.target}`;UI.servedProgress.style.width=`${Math.min(100,game.servedToday/game.target*100)}%`;UI.earned.textContent=`$${game.earnedToday}`;UI.strikes.textContent=`${game.strikes} / 3`;
  const active=game.orders.filter(o=>o.status==="waiting"||o.status==="cooking").length;UI.rush.textContent=active>=5?"RUSH":active>=3?"BUSY":"NORMAL";UI.rush.classList.toggle("hot",active>=3);
}
function updateCarriedUI(){
  const o=game.carried;if(!o){UI.carried.className="carried-dish empty";UI.carried.innerHTML=`<span class="dish-icon">🍽️</span><div><strong>Vacía</strong><small>Ve al refrigerador para tomar un pedido.</small></div>`;UI.route.textContent="FRIDGE → PREP → COOK → PASS";return;}
  const r=recipes[o.recipe],next=r.route[o.stage];UI.carried.className="carried-dish";UI.carried.innerHTML=`<span class="dish-icon">${r.icon}</span><div><strong>${r.name}</strong><small>Cliente #${o.customerId} · paciencia ${Math.max(0,Math.round(o.patience))}%</small></div>`;
  UI.route.textContent=r.route.map((id,i)=>`${i<o.stage?"✓ ":i===o.stage?"▶ ":""}${stationById[id].name.toUpperCase()}`).join(" → ");
}
function renderOrders(){
  const active=game.orders.filter(o=>o.status==="waiting"||o.status==="cooking").sort((a,b)=>a.patience-b.patience);if(!active.length){UI.orders.innerHTML=`<div class="order-empty">Esperando clientes…</div>`;return;}
  UI.orders.innerHTML=active.map(o=>{const r=recipes[o.recipe],pct=clamp(o.patience/o.maxPatience*100,0,100),tone=pct<26?"danger":pct<52?"warning":"",stage=o.status==="cooking"?`EN COCINA · siguiente: ${stationById[r.route[o.stage]]?.name||"entrega"}`:"ESPERANDO";return `<div class="ticket ${tone}"><div class="ticket-top"><strong>${r.icon} #${o.customerId} ${r.name}</strong><span class="ticket-price">$${r.price}</span></div><div class="ticket-stage">${stage}</div><div class="patience"><span style="width:${pct}%"></span></div></div>`;}).join("");
}
function formatTime(sec){sec=Math.max(0,Math.ceil(sec));return `${String(Math.floor(sec/60)).padStart(2,"0")}:${String(sec%60).padStart(2,"0")}`;}
function showToast(text,tone=""){clearTimeout(toastTimer);UI.toast.textContent=text;UI.toast.className=`toast ${tone}`;toastTimer=setTimeout(()=>UI.toast.classList.add("hidden"),2200);}

function update(dt){
  if(game.running&&!game.paused){
    game.timeLeft-=dt;updatePlayer(dt);updateAction(dt);updateOrders(dt);updateCustomers(dt);updateHelper(dt);
    game.spawnTimer-=dt;if(game.spawnTimer<=0){spawnOrder();game.spawnTimer=Math.max(4.4,9.4-game.day*.65+rand(-1.1,1.2));}
    if(game.timeLeft<=0)finishDay();
    updateHUD();updateCarriedUI();updatePrompt();
  } else updatePrompt();
}
function loop(now){
  const dt=Math.min(.05,(now-lastTime)/1000);lastTime=now;update(dt);renderWorld();requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

addEventListener("keydown",e=>{
  keys.add(e.code);if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code))e.preventDefault();
  if(e.repeat)return;if(e.code==="KeyE")interact();if(e.code==="KeyQ")discardDish();
});
addEventListener("keyup",e=>keys.delete(e.code));

$("startBtn").onclick=startCampaign;
$("restartBtn").onclick=()=>{UI.end.classList.remove("visible");UI.start.classList.add("visible");resetGame();};
$("nextDayBtn").onclick=nextDay;
$("continueQuizBtn").onclick=continueAfterQuiz;
$("helpBtn").onclick=()=>{game.paused=true;UI.help.classList.add("visible");};
$("closeHelpBtn").onclick=()=>{UI.help.classList.remove("visible");if(game.running)game.paused=false;};
document.querySelectorAll(".upgrade-card").forEach(b=>b.addEventListener("click",()=>buyUpgrade(b.dataset.upgrade)));

updateHUD();updateCarriedUI();renderOrders();
