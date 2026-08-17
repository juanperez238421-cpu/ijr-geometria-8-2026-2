const port=Number(process.env.CDP_PORT||9333);
const endpoint=`http://127.0.0.1:${port}/json`;
const gameUrl='http://127.0.0.1:8765/index.html';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function waitPage(){
  for(let i=0;i<400;i++){
    try{const pages=await fetch(endpoint).then(r=>r.json());const page=pages.find(p=>p.type==='page');if(page)return page;}catch{}
    await sleep(100);
  }
  throw new Error('Chrome DevTools page unavailable');
}

class CDP{
  constructor(url){
    this.ws=new WebSocket(url);this.id=1;this.pending=new Map();this.exceptions=[];this.errors=[];
    this.ws.onmessage=e=>{
      const m=JSON.parse(e.data);
      if(m.id&&this.pending.has(m.id)){const q=this.pending.get(m.id);this.pending.delete(m.id);m.error?q.reject(new Error(JSON.stringify(m.error))):q.resolve(m.result);}
      else if(m.method==='Runtime.exceptionThrown')this.exceptions.push(m.params?.exceptionDetails?.exception?.description||m.params?.exceptionDetails?.text||'Runtime exception');
      else if(m.method==='Runtime.consoleAPICalled'&&m.params?.type==='error')this.errors.push((m.params.args||[]).map(x=>x.value??x.description??'').join(' '));
    };
  }
  async open(){if(this.ws.readyState!==WebSocket.OPEN)await new Promise((resolve,reject)=>{this.ws.onopen=resolve;this.ws.onerror=reject;});}
  send(method,params={}){const id=this.id++;return new Promise((resolve,reject)=>{this.pending.set(id,{resolve,reject});this.ws.send(JSON.stringify({id,method,params}));});}
  async eval(expression){const r=await this.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text||'Evaluation failed');return r.result?.value;}
}

async function waitEval(cdp,expr,timeout=10000){
  const end=Date.now()+timeout;let last;
  while(Date.now()<end){try{last=await cdp.eval(expr);if(last)return last;}catch{}await sleep(100);}
  throw new Error(`Timed out waiting for ${expr}; last=${JSON.stringify(last)}`);
}
async function mouse(cdp,x,y,button='left',hold=85){
  await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',x,y});
  await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button,clickCount:1});
  await sleep(hold);
  await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button,clickCount:1});
  await sleep(180);
}
async function key(cdp,code,keyValue,hold=700){
  await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',code,key:keyValue});
  await sleep(hold);
  await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',code,key:keyValue});
  await sleep(180);
}
async function stationPoint(cdp,type,kind=null,y=1.0,offset=1.35){
  return cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type===${JSON.stringify(type)}${kind?`&&x.kind===${JSON.stringify(kind)}`:''});if(!s)throw new Error('station missing');g.__seniorV9.cancelTask?.('QA POSITION');p.group.position.set(s.pos.x,0,s.pos.z+${offset});g.cameraRig.update(.65);const v=s.pos.clone();v.y=${y};v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2};})()`);
}

const page=await waitPage();const cdp=new CDP(page.webSocketDebuggerUrl);await cdp.open();
await cdp.send('Runtime.enable');await cdp.send('Page.enable');await cdp.send('Page.navigate',{url:gameUrl});
await waitEval(cdp,`location.origin==='http://127.0.0.1:8765'&&document.readyState==='complete'&&!!window.__rkrGame?.__seniorV9`,15000);
await cdp.eval(`localStorage.clear();true`);await cdp.send('Page.reload',{ignoreCache:true});
await waitEval(cdp,`document.readyState==='complete'&&!!window.__rkrGame?.__seniorV9`,15000);cdp.exceptions.length=0;cdp.errors.length=0;

// First validate local co-op controls in a fresh 3-human service, before any long-running solo task exists.
const coop=await cdp.eval(`(()=>{const g=window.__rkrGame;g.config.humanCount=3;g.config.roles=['chef','prep','service'];g.config.menu=['salad','burger'];g.business.cash=500;g.business.plan=[];g.plan=[];g.enterBuildMode();g.autoLayout();g.openRestaurant();g.spawnTimer=9999;g.timeLeft=9999;const b=g.currentBounds();const staticFree=(p,x,z)=>{if(x<-b.xMax+.65||x>b.xMax-.65||z<b.zMin+.65||z>b.zMax-.65)return false;for(const o of g.obstacles)if(Math.abs(x-o.x)<o.w/2+p.radius+.10&&Math.abs(z-o.z)<o.d/2+p.radius+.10)return false;return true;};const lane=(p,dx,dz)=>{for(let z=Math.max(b.zMin+1,-.3);z<=Math.min(b.zMax-1,1.5);z+=.35)for(let x=-b.xMax+1;x<=b.xMax-1;x+=.4)if(staticFree(p,x,z)&&staticFree(p,x+dx,z+dz))return{x,z};return null;};return{players:g.players.length,bots:g.players.filter(p=>!p.human).length,l2:lane(g.players[1],1.25,0),l3:lane(g.players[2],0,1.25),state:g.state};})()`);
if(coop.players!==3||coop.bots!==0||coop.state!=='playing'||!coop.l2||!coop.l3)throw new Error(`Fresh local co-op setup failed: ${JSON.stringify(coop)}`);

const p2State0=await cdp.eval(`(()=>{const g=window.__rkrGame,l=${JSON.stringify(coop.l2)};g.players[0].group.position.set(99,0,99);g.players[2].group.position.set(-99,0,-99);g.players[1].group.position.set(l.x,0,l.z);return{input:g.input.state(1),human:g.players[1].human,index:g.players[1].index,x:g.players[1].group.position.x};})()`);
const p2Before=p2State0.x;await key(cdp,'KeyD','d',700);const p2After=await cdp.eval(`window.__rkrGame.players[1].group.position.x`);
if(!(p2After>p2Before+.20)){
  const diag=await cdp.eval(`(()=>{const g=window.__rkrGame;return{keys:[...g.input.keys],state:g.input.state(1),human:g.players[1].human,index:g.players[1].index,installed:!!g.players[1].__v8Installed,pos:{x:g.players[1].group.position.x,z:g.players[1].group.position.z}};})()`);
  throw new Error(`P2 WASD real-key movement failed ${p2Before}->${p2After}: ${JSON.stringify(diag)}`);
}

const p3State0=await cdp.eval(`(()=>{const g=window.__rkrGame,l=${JSON.stringify(coop.l3)};g.players[0].group.position.set(99,0,99);g.players[1].group.position.set(-99,0,-99);g.players[2].group.position.set(l.x,0,l.z);return{input:g.input.state(2),human:g.players[2].human,index:g.players[2].index,z:g.players[2].group.position.z};})()`);
const p3Before=p3State0.z;await key(cdp,'ArrowDown','ArrowDown',700);const p3After=await cdp.eval(`window.__rkrGame.players[2].group.position.z`);
if(!(p3After>p3Before+.20)){
  const diag=await cdp.eval(`(()=>{const g=window.__rkrGame;return{keys:[...g.input.keys],state:g.input.state(2),human:g.players[2].human,index:g.players[2].index,installed:!!g.players[2].__v8Installed,pos:{x:g.players[2].group.position.x,z:g.players[2].group.position.z}};})()`);
  throw new Error(`P3 arrow real-key movement failed ${p3Before}->${p3After}: ${JSON.stringify(diag)}`);
}

// Restart as true solo and validate the redesigned interaction contract with real pointer events.
const setup=await cdp.eval(`(()=>{const g=window.__rkrGame;g.config.humanCount=1;g.restartService();g.spawnTimer=9999;g.timeLeft=9999;g.__seniorV9.applyPointerOwnership?.();const plan=g.plan.map(q=>({key:q.key,x:q.x,z:q.z}));return{version:g.__seniorV9.version,patch:g.__seniorV9.patchLevel,players:g.players.length,bots:g.players.filter(p=>!p.human).length,plan,overlay:document.getElementById('v9-input-layer').classList.contains('active'),canvas:getComputedStyle(g.canvas).pointerEvents,actionCard:getComputedStyle(document.getElementById('v8-action-card')).display};})()`);
if(setup.version!=='9.0.0'||setup.players!==1||setup.bots!==0||!setup.overlay||setup.canvas!=='none'||setup.actionCard!=='none')throw new Error(`V9 solo/input ownership failed: ${JSON.stringify(setup)}`);
if(!setup.plan.some(q=>q.key==='grocery')||!setup.plan.some(q=>q.key==='prep')||!setup.plan.some(q=>q.key==='stove')||setup.plan.filter(q=>q.key==='table').length<2)throw new Error(`V9 work-triangle layout incomplete: ${JSON.stringify(setup.plan)}`);

const plate=await stationPoint(cdp,'plate');await mouse(cdp,plate.x,plate.y,'left');
await waitEval(cdp,`!!window.__rkrGame.players[0].held?.isPlate`,4500);await waitEval(cdp,`!window.__rkrGame.__seniorV9.state.task`,2500);
const plateResult=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:p.held?.description?.(),done:g.qaEvents.filter(e=>e.type==='v9-task-complete').length};})()`);
if(plateResult.held!=='plate'||plateResult.done<1)throw new Error(`Real left-click plate pickup failed: ${JSON.stringify(plateResult)}`);
await cdp.eval(`(()=>{const p=window.__rkrGame.players[0];p.held?.dispose();p.held=null;return true;})()`);

const tomato=await stationPoint(cdp,'storage','tomato',1.05,.85);const stock0=await cdp.eval(`window.__rkrGame.v8Stock.tomato`);
await mouse(cdp,tomato.x,tomato.y,'right');await sleep(300);
const rightCancel=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:p.held?.kind||null,stock:g.v8Stock.tomato,task:!!g.__seniorV9.state.task,cancels:g.qaEvents.filter(e=>e.type==='v9-right-cancel').length};})()`);
if(rightCancel.held!==null||rightCancel.stock!==stock0||rightCancel.task||rightCancel.cancels<1)throw new Error(`Right click did work instead of cancel only: ${JSON.stringify(rightCancel)}`);

const tomato2=await stationPoint(cdp,'storage','tomato',1.05,.85);await mouse(cdp,tomato2.x,tomato2.y,'left');
await waitEval(cdp,`window.__rkrGame.players[0].held?.kind==='tomato'`,5000);await waitEval(cdp,`!window.__rkrGame.__seniorV9.state.task`,2500);
const tomatoResult=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:p.held?.kind,state:p.held?.state,stock:g.v8Stock.tomato};})()`);
if(tomatoResult.held!=='tomato'||tomatoResult.state!=='raw'||tomatoResult.stock!==stock0-1)throw new Error(`Real left-click grocery pickup failed: ${JSON.stringify(tomatoResult)}`);

const prep=await stationPoint(cdp,'prep');await mouse(cdp,prep.x,prep.y,'left');
await waitEval(cdp,`window.__rkrGame.players[0].held?.kind==='tomato'&&window.__rkrGame.players[0].held?.state==='chopped'`,7000);await waitEval(cdp,`!window.__rkrGame.__seniorV9.state.task`,2500);
const prepResult=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type==='prep');return{held:p.held?.kind,state:p.held?.state,slot:s.slot?.kind||null,done:g.qaEvents.filter(e=>e.type==='v9-timed-job-complete'&&e.target==='prep').length};})()`);
if(prepResult.held!=='tomato'||prepResult.state!=='chopped'||prepResult.slot!==null||prepResult.done<1)throw new Error(`Single-click timed prep failed: ${JSON.stringify(prepResult)}`);

const npc=await cdp.eval(`(()=>{const g=window.__rkrGame;g.spawnParty();const p=g.parties.at(-1);return p?{hasV8:!!p.v8,bubble:!!p.v8?.bubble,trait:p.v8?.traits,customers:p.customers.length}:null;})()`);
if(!npc||!npc.hasV8||!npc.bubble||npc.customers<1)throw new Error(`NPC systems regressed under V9: ${JSON.stringify(npc)}`);
const management=await cdp.eval(`(()=>{const g=window.__rkrGame;g.updateUI();return{clean:g.__seniorV8.cleanliness(),board:document.getElementById('v8-service-board').textContent,statuses:g.__seniorV9.stationStatus()};})()`);
if(!management.board.includes('CLEANLINESS')||management.clean<0||management.clean>100||!Array.isArray(management.statuses))throw new Error(`Management board regression: ${JSON.stringify(management)}`);

const build=await cdp.eval(`(()=>{const g=window.__rkrGame;g.enterBuildMode();g.__seniorV9.applyPointerOwnership?.();return{state:g.state,canvas:getComputedStyle(g.canvas).pointerEvents,overlay:document.getElementById('v9-input-layer').classList.contains('active')};})()`);
if(build.state!=='build'||build.canvas!=='auto'||build.overlay)throw new Error(`Build-mode camera/pointer restoration failed: ${JSON.stringify(build)}`);

if(cdp.exceptions.length)throw new Error(`Runtime exceptions: ${cdp.exceptions.join(' | ')}`);
if(cdp.errors.length)throw new Error(`Console errors: ${cdp.errors.join(' | ')}`);
console.log('Senior V9 RELEASE E2E passed',JSON.stringify({coop,p2Before,p2After,p3Before,p3After,setup,plateResult,rightCancel,tomatoResult,prepResult,npc,management,build}));
cdp.ws.close();
