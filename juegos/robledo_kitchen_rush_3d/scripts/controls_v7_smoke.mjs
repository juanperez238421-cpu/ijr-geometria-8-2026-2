const port = Number(process.env.CDP_PORT || 9333);
const endpoint = `http://127.0.0.1:${port}/json`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function waitForPage(){for(let i=0;i<400;i++){try{const pages=await fetch(endpoint).then(r=>r.json());const page=pages.find(p=>p.type==='page'&&p.url.includes('127.0.0.1'));if(page)return page;}catch{}await sleep(100);}throw new Error('Chrome DevTools page did not become available');}
class CDP{constructor(url){this.ws=new WebSocket(url);this.next=1;this.pending=new Map();this.exceptions=[];this.consoleErrors=[];this.ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id&&this.pending.has(msg.id)){const{resolve,reject}=this.pending.get(msg.id);this.pending.delete(msg.id);msg.error?reject(new Error(JSON.stringify(msg.error))):resolve(msg.result);}else if(msg.method==='Runtime.exceptionThrown')this.exceptions.push(msg.params?.exceptionDetails?.exception?.description||msg.params?.exceptionDetails?.text||'Runtime exception');else if(msg.method==='Runtime.consoleAPICalled'&&msg.params?.type==='error')this.consoleErrors.push((msg.params.args||[]).map(x=>x.value??x.description??'').join(' '));};}async open(){if(this.ws.readyState!==WebSocket.OPEN)await new Promise((resolve,reject)=>{this.ws.onopen=resolve;this.ws.onerror=reject;});}send(method,params={}){const id=this.next++;return new Promise((resolve,reject)=>{this.pending.set(id,{resolve,reject});this.ws.send(JSON.stringify({id,method,params}));});}async eval(expression){const result=await this.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text||'Evaluation failed');return result.result?.value;}}
async function waitEval(cdp,expression,timeout=8000){const until=Date.now()+timeout;let last;while(Date.now()<until){last=await cdp.eval(expression);if(last)return last;await sleep(100);}throw new Error(`Timed out waiting for ${expression}; last=${JSON.stringify(last)}`);}
async function key(cdp,code,keyValue,hold=220){await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',code,key:keyValue});await sleep(hold);await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',code,key:keyValue});await sleep(90);}
async function mouseClick(cdp,x,y,button='left',hold=80){await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',x,y});await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button,clickCount:1});await sleep(hold);await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button,clickCount:1});await sleep(120);}

const page=await waitForPage();const cdp=new CDP(page.webSocketDebuggerUrl);await cdp.open();await cdp.send('Runtime.enable');await cdp.send('Page.enable');
await cdp.eval(`localStorage.clear();location.reload();true`);await sleep(400);await waitEval(cdp,`document.readyState==='complete'&&!!window.__rkrGame&&!!window.__rkrGame.__controlsV7`,15000);

const setup=await cdp.eval(`(()=>{const g=window.__rkrGame;g.config.humanCount=3;g.config.roles=['chef','prep','service'];g.config.menu=['salad','burger'];g.business.cash=430;g.business.satisfaction=80;g.business.plan=[];g.plan=[];g.enterBuildMode();g.autoLayout();g.openRestaurant();g.spawnTimer=9999;g.timeLeft=9999;return{v:g.__controlsV7.version,humans:g.players.filter(p=>p.human).length,roles:g.players.map(p=>p.role),plan:g.plan.map(q=>q.key),controls:[...document.querySelectorAll('#controls-screen article')].slice(0,3).map(x=>x.textContent)};})()`);
if(setup.v!=='7.0.0'||setup.humans!==3||!setup.plan.includes('grocery')||!setup.controls[0].includes('MOUSE')||!setup.controls[1].includes('WASD')||!setup.controls[2].includes('Arrow'))throw new Error(`Controls V7 setup failed: ${JSON.stringify(setup)}`);
await sleep(300);

// P2 must move with WASD only.
const p2Before=await cdp.eval(`window.__rkrGame.players[1].group.position.x`);
await key(cdp,'KeyD','d',180);
const p2After=await cdp.eval(`window.__rkrGame.players[1].group.position.x`);
if(!(p2After>p2Before+.18))throw new Error(`P2 WASD movement failed: ${p2Before} -> ${p2After}`);

// P3 must move with arrow keys.
const p3Before=await cdp.eval(`window.__rkrGame.players[2].group.position.z`);
await key(cdp,'ArrowDown','ArrowDown',180);
const p3After=await cdp.eval(`window.__rkrGame.players[2].group.position.z`);
if(!(p3After>p3Before+.18))throw new Error(`P3 arrow movement failed: ${p3Before} -> ${p3After}`);

// P2 F selects and E interacts. Holding E on Plate Rack must pick exactly once,
// proving the old frame-by-frame pick/return toggle is gone.
await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[1],s=g.stations.find(x=>x.type==='plate');p.group.position.set(s.pos.x,0,s.pos.z+1.25);p.selectedTarget=null;p.prevInteract=false;return true;})()`);
await key(cdp,'KeyF','f',60);
const p2Selected=await cdp.eval(`window.__rkrGame.players[1].selectedTarget?.type`);
if(p2Selected!=='plate')throw new Error(`P2 F selection failed: ${p2Selected}`);
await key(cdp,'KeyE','e',420);
const p2Plate=await cdp.eval(`(()=>{const p=window.__rkrGame.players[1];return{held:!!p.held?.isPlate,desc:p.held?.description?.()||null,target:p.selectedTarget?.type,nearest:window.__rkrGame.nearestInteractable(p.group.position,1.88)?.type||null};})()`);
if(!p2Plate.held||p2Plate.target!=='plate'||p2Plate.nearest!=='plate')throw new Error(`P2 interaction edge-gating failed: ${JSON.stringify(p2Plate)}`);
await cdp.eval(`(()=>{const p=window.__rkrGame.players[1];if(p.held){p.held.dispose();p.held=null;}p.selectedTarget=null;return true;})()`);

// P3 Period selects the nearby Grocery compartment and Enter picks a real ingredient.
await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[2],s=g.stations.find(x=>x.type==='storage');p.group.position.set(s.pos.x,0,s.pos.z+.55);p.selectedTarget=null;p.prevInteract=false;return true;})()`);
await key(cdp,'Period','.',60);
const p3Selected=await cdp.eval(`(()=>{const p=window.__rkrGame.players[2];return{type:p.selectedTarget?.type,kind:p.selectedTarget?.kind};})()`);
if(p3Selected.type!=='storage')throw new Error(`P3 Period selection failed: ${JSON.stringify(p3Selected)}`);
await key(cdp,'Enter','Enter',180);
const p3Ingredient=await cdp.eval(`(()=>{const p=window.__rkrGame.players[2];return{held:p.held?.kind||null,target:p.selectedTarget?.kind||null};})()`);
if(!p3Ingredient.held||p3Ingredient.held!==p3Ingredient.target)throw new Error(`P3 Enter grocery interaction failed: ${JSON.stringify(p3Ingredient)}`);
await cdp.eval(`(()=>{const p=window.__rkrGame.players[2];if(p.held){p.held.dispose();p.held=null;}p.selectedTarget=null;return true;})()`);

// P1 left click must create a click-to-move destination and physically move Player 1.
await cdp.eval(`(()=>{const g=window.__rkrGame;const ps=g.players;ps[0].group.position.set(-3.1,0,.15);ps[1].group.position.set(0,0,.15);ps[2].group.position.set(3.1,0,.15);g.__controlsV7.selectTarget(ps[0],null);g.__controlsV7.mouse.moveTarget=null;g.cameraRig.setMode('classic');return true;})()`);
await sleep(250);
const floorPoint=await cdp.eval(`(()=>{const g=window.__rkrGame,v=g.players[0].group.position.clone();v.z+=1.5;v.y=0;v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2,z0:g.players[0].group.position.z};})()`);
await mouseClick(cdp,floorPoint.x,floorPoint.y,'left',60);
await sleep(500);
const p1Moved=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{z:p.group.position.z,hasMove:!!g.__controlsV7.mouse.moveTarget};})()`);
if(!(p1Moved.z>floorPoint.z0+.28))throw new Error(`P1 left-click movement failed: ${JSON.stringify({floorPoint,p1Moved})}`);

// P1 left click on a fixture selects it; right click/hold interacts without camera conflict.
const p1PlatePoint=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],s=g.stations.find(x=>x.type==='plate');p.group.position.set(s.pos.x,0,s.pos.z+1.25);p.prevInteract=false;g.__controlsV7.selectTarget(p,null);const v=s.pos.clone();v.y=1.0;v.project(g.camera);const r=g.canvas.getBoundingClientRect();return{x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2,yaw:g.cameraRig.yaw};})()`);
await mouseClick(cdp,p1PlatePoint.x,p1PlatePoint.y,'left',70);
const p1Selected=await cdp.eval(`window.__rkrGame.players[0].selectedTarget?.type`);
if(p1Selected!=='plate')throw new Error(`P1 left-click fixture selection failed: ${p1Selected}`);
await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',x:p1PlatePoint.x,y:p1PlatePoint.y});
await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',x:p1PlatePoint.x,y:p1PlatePoint.y,button:'right',clickCount:1});
await sleep(420);
await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',x:p1PlatePoint.x,y:p1PlatePoint.y,button:'right',clickCount:1});
await sleep(120);
const p1Result=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0];return{held:!!p.held?.isPlate,target:p.selectedTarget?.type,right:g.__controlsV7.mouse.rightDown,yaw:g.cameraRig.yaw};})()`);
if(!p1Result.held||p1Result.target!=='plate'||p1Result.right||Math.abs(p1Result.yaw-p1PlatePoint.yaw)>.02)throw new Error(`P1 right-click interaction/camera ownership failed: ${JSON.stringify({p1PlatePoint,p1Result})}`);

// Carried-item exclusion: while P1 holds a plate, station targeting must not resolve to the held plate.
const heldExclusion=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.players[0],n=g.nearestInteractable(p.group.position,1.88);return{nearestType:n?.type||null,isHeld:n===p.held,held:p.held?.description?.()||null};})()`);
if(heldExclusion.isHeld||!heldExclusion.nearestType)throw new Error(`Held-item targeting regression remains: ${JSON.stringify(heldExclusion)}`);

if(cdp.exceptions.length)throw new Error(`Runtime exceptions detected: ${cdp.exceptions.join(' | ')}`);
if(cdp.consoleErrors.length)throw new Error(`Console errors detected: ${cdp.consoleErrors.join(' | ')}`);
console.log('Controls V7 deterministic browser E2E passed:',JSON.stringify({setup,p2Before,p2After,p3Before,p3After,p2Plate,p3Ingredient,p1Moved,p1Result,heldExclusion}));
cdp.ws.close();
