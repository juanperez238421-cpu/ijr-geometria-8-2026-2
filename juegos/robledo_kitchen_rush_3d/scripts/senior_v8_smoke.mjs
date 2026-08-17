const port = Number(process.env.CDP_PORT || 9333);
const endpoint = `http://127.0.0.1:${port}/json`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function waitForPage(){
  for(let i=0;i<400;i++){
    try{
      const pages=await fetch(endpoint).then(r=>r.json());
      const page=pages.find(p=>p.type==='page'&&p.url.includes('127.0.0.1'));
      if(page)return page;
    }catch{}
    await sleep(100);
  }
  throw new Error('Chrome DevTools page did not become available');
}

class CDP{
  constructor(url){this.ws=new WebSocket(url);this.next=1;this.pending=new Map();this.exceptions=[];this.consoleErrors=[];this.ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id&&this.pending.has(msg.id)){const{resolve,reject}=this.pending.get(msg.id);this.pending.delete(msg.id);msg.error?reject(new Error(JSON.stringify(msg.error))):resolve(msg.result);}else if(msg.method==='Runtime.exceptionThrown')this.exceptions.push(msg.params?.exceptionDetails?.exception?.description||msg.params?.exceptionDetails?.text||'Runtime exception');else if(msg.method==='Runtime.consoleAPICalled'&&msg.params?.type==='error')this.consoleErrors.push((msg.params.args||[]).map(x=>x.value??x.description??'').join(' '));};}
  async open(){if(this.ws.readyState!==WebSocket.OPEN)await new Promise((resolve,reject)=>{this.ws.onopen=resolve;this.ws.onerror=reject;});}
  send(method,params={}){const id=this.next++;return new Promise((resolve,reject)=>{this.pending.set(id,{resolve,reject});this.ws.send(JSON.stringify({id,method,params}));});}
  async eval(expression){const result=await this.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text||'Evaluation failed');return result.result?.value;}
}

async function waitEval(cdp,expression,timeout=10000){const until=Date.now()+timeout;let last;while(Date.now()<until){last=await cdp.eval(expression);if(last)return last;await sleep(100);}throw new Error(`Timed out waiting for ${expression}; last=${JSON.stringify(last)}`);}
async function key(cdp,code,keyValue,hold=300){await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',code,key:keyValue});await sleep(hold);await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',code,key:keyValue});await sleep(120);}
async function mouseClick(cdp,x,y,button='left',hold=90){await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',x,y});await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button,clickCount:1});await sleep(hold);await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button,clickCount:1});await sleep(180);}

const page=await waitForPage();const cdp=new CDP(page.webSocketDebuggerUrl);await cdp.open();await cdp.send('Runtime.enable');await cdp.send('Page.enable');
await cdp.eval(`localStorage.clear();location.reload();true`);await sleep(500);await waitEval(cdp,`document.readyState==='complete'&&!!window.__rkrGame&&!!window.__rkrGame.__seniorV8`,15000);

const setup=await cdp.eval(`(()=>{const g=window.__rkrGame;g.config.humanCount=1;g.config.roles=['chef','prep','service'];g.config.menu=['salad','burger'];g.config.avatars[0]={...g.config.avatars[0],name:'SOLO QA',gender:'female',hairStyle:'bun',uniform:4,apron:3,accessory:'glasses'};g.business.cash=430;g.business.satisfaction=80;g.business.plan=[];g.plan=[];g.enterBuildMode();g.autoLayout();const plan=g.plan.map(q=>({key:q.key,x:q.x,z:q.z}));g.openRestaurant();g.spawnTimer=9999;g.timeLeft=9999;return{version:g.__seniorV8.version,players:g.players.length,bots:g.players.filter(p=>!p.human).length,plan,recipeCards:document.querySelectorAll('#recipe-grid .v8-recipe').length,customizer:!!document.getElementById('v8-customization'),avatar:g.config.avatars[0],board:!document.getElementById('v8-service-board').classList.contains('hidden')};})()`);
if(setup.version!=='8.0.0'||setup.players!==1||setup.bots!==0||setup.recipeCards!==6||!setup.customizer||!setup.board)throw new Error(`Senior V8 solo/customization setup failed: ${JSON.stringify(setup)}`);
if(!setup.plan.some(q=>q.key==='grocery')||!setup.plan.some(q=>q.key==='prep')||!setup.plan.some(q=>q.key==='stove')||setup.plan.filter(q=>q.key==='table').length<2)throw new Error(`Senior V8 layout missing required production/dining fixtures: ${JSON.stringify(setup.plan)}`);
const tables=setup.plan.filter(q=>q.key==='table');if(tables.some(t=>t.z<1.7))throw new Error(`Dining layout is not separated from kitchen: ${JSON.stringify(tables)}`);

// P1 left click must now be a REAL interaction, not just selection/movement.
const platePoint=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type==='plate');p.group.position.set(s.pos.x,0,s.pos.z+1.35);const v=s.pos.clone();v.y=1.05;v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2};})()`);
await sleep(300);await mouseClick(cdp,platePoint.x,platePoint.y,'left',90);await waitEval(cdp,`!!window.__rkrGame.players[0].held?.isPlate`,3000);
const leftInteraction=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:p.held?.description?.(),target:p.selectedTarget?.type,events:g.qaEvents.filter(e=>e.type==='v8-human-interact').length};})()`);
if(leftInteraction.held!=='plate'||leftInteraction.target!=='plate')throw new Error(`P1 left-click interaction failed: ${JSON.stringify(leftInteraction)}`);
await cdp.eval(`(()=>{const p=window.__rkrGame.players[0];p.held?.dispose();p.held=null;return true;})()`);

// P1 right click must pick a physical grocery ingredient and decrement finite stock.
const tomatoPoint=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type==='storage'&&x.kind==='tomato');p.group.position.set(s.pos.x,0,s.pos.z+.72);const v=s.pos.clone();v.y=1.0;v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2,stock:g.v8Stock.tomato};})()`);
await mouseClick(cdp,tomatoPoint.x,tomatoPoint.y,'right',230);await waitEval(cdp,`window.__rkrGame.players[0].held?.kind==='tomato'`,3000);
const rightInteraction=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:p.held?.kind,state:p.held?.state,stock:g.v8Stock.tomato,target:p.selectedTarget?.kind};})()`);
if(rightInteraction.held!=='tomato'||rightInteraction.stock!==tomatoPoint.stock-1)throw new Error(`P1 right-click grocery interaction failed: ${JSON.stringify({tomatoPoint,rightInteraction})}`);

// Smart left click on Prep must place + perform the preparation animation/work until chopped.
const prepPoint=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type==='prep');p.group.position.set(s.pos.x,0,s.pos.z+1.38);const v=s.pos.clone();v.y=1.05;v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2};})()`);
await mouseClick(cdp,prepPoint.x,prepPoint.y,'left',90);await waitEval(cdp,`window.__rkrGame.stations.find(x=>x.type==='prep')?.slot?.state==='chopped'`,4500);
const prepResult=await cdp.eval(`(()=>{const g=window.__rkrGame,s=g.stations.find(x=>x.type==='prep');return{slot:s.slot?.kind,state:s.slot?.state,held:g.players[0].held?.kind||null,interactions:g.v8Shift.interactions};})()`);
if(prepResult.slot!=='tomato'||prepResult.state!=='chopped'||prepResult.interactions<2)throw new Error(`Smart prep workflow failed: ${JSON.stringify(prepResult)}`);

// NPCs must carry V8 behavior metadata + speech bubble and respond to service states.
const npc=await cdp.eval(`(()=>{const g=window.__rkrGame;g.spawnParty();const p=g.parties.at(-1);if(!p)return null;return{id:p.id,state:p.state,hasV8:!!p.v8,regular:!!p.v8?.regular,trait:p.v8?.traits,bubble:!!p.v8?.bubble,customers:p.customers.length};})()`);
if(!npc||!npc.hasV8||!npc.bubble||npc.customers<1)throw new Error(`Dynamic NPC decoration failed: ${JSON.stringify(npc)}`);

// Live service board must expose recipe route, stock, goals and cleanliness.
const board=await cdp.eval(`(()=>{const el=document.getElementById('v8-service-board');return{text:el.textContent,stock:Object.keys(window.__rkrGame.v8Stock).length,clean:window.__rkrGame.__seniorV8.cleanliness()};})()`);
if(!board.text.includes('CLEANLINESS')||!board.text.includes('Serve 3 tables')||board.stock<4||board.clean<0||board.clean>100)throw new Error(`Service board/management mechanics failed: ${JSON.stringify(board)}`);

// Switch to 3 humans: P2 must use WASD and P3 must use arrows; no bot should appear.
await cdp.eval(`(()=>{const g=window.__rkrGame;g.config.humanCount=3;g.restartService();g.spawnTimer=9999;g.timeLeft=9999;g.players[0].group.position.set(-3,0,.1);g.players[1].group.position.set(0,0,.1);g.players[2].group.position.set(3,0,.1);return{players:g.players.length,bots:g.players.filter(p=>!p.human).length};})()`);
const roster3=await cdp.eval(`({players:window.__rkrGame.players.length,bots:window.__rkrGame.players.filter(p=>!p.human).length})`);if(roster3.players!==3||roster3.bots!==0)throw new Error(`Three-human roster failed: ${JSON.stringify(roster3)}`);
const p2Before=await cdp.eval(`window.__rkrGame.players[1].group.position.x`);await key(cdp,'KeyD','d',350);const p2After=await cdp.eval(`window.__rkrGame.players[1].group.position.x`);if(!(p2After>p2Before+.35))throw new Error(`P2 WASD movement failed: ${p2Before} -> ${p2After}`);
const p3Before=await cdp.eval(`window.__rkrGame.players[2].group.position.z`);await key(cdp,'ArrowDown','ArrowDown',350);const p3After=await cdp.eval(`window.__rkrGame.players[2].group.position.z`);if(!(p3After>p3Before+.35))throw new Error(`P3 arrow movement failed: ${p3Before} -> ${p3After}`);

if(cdp.exceptions.length)throw new Error(`Runtime exceptions detected: ${cdp.exceptions.join(' | ')}`);
if(cdp.consoleErrors.length)throw new Error(`Console errors detected: ${cdp.consoleErrors.join(' | ')}`);
console.log('Senior V8 deterministic browser E2E passed:',JSON.stringify({setup,leftInteraction,rightInteraction,prepResult,npc,board,roster3,p2Before,p2After,p3Before,p3After}));
cdp.ws.close();
