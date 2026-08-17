import * as THREE from 'three';
import './game.js';

const game = window.__rkrGame;
if (!game) throw new Error('Robledo Kitchen Rush base game did not initialize before Senior V8.');
if (game.__seniorV8) throw new Error('Senior V8 loaded twice.');

const V8_VERSION = '8.0.0';
const INTERACT_RANGE = 2.08;
const SELECT_RANGE = 4.6;
const PLAYER_COLORS = [0xe34f51, 0x4387db, 0xf2bd3f];
const SKIN_TONES = [0xf6c7a4, 0xe8aa7e, 0xcf875f, 0xa86648, 0x7b4936, 0x563225];
const HAIR_COLORS = [0x1c1715, 0x4d3021, 0x7d5335, 0xb47b3d, 0x6e2d27, 0xd2b07b];
const UNIFORM_COLORS = [0xe34f51, 0x4387db, 0x4d9a67, 0x7b5bb5, 0xef7c38, 0x303d43];
const APRON_COLORS = [0xf4eee3, 0x30383c, 0xf2bd3f, 0x4b9ca3, 0xc45b71, 0x8f6b4d];
const AVATAR_DEFAULTS = [
  { name:'Chef 1', gender:'neutral', skin:1, hair:1, hairStyle:'short', uniform:0, apron:0, accessory:'none', build:'standard' },
  { name:'Chef 2', gender:'neutral', skin:2, hair:0, hairStyle:'bun', uniform:1, apron:3, accessory:'glasses', build:'standard' },
  { name:'Chef 3', gender:'neutral', skin:3, hair:2, hairStyle:'curls', uniform:2, apron:2, accessory:'bandana', build:'standard' },
];

const INGREDIENT = {
  tomato:{name:'Tomato',emoji:'🍅'}, lettuce:{name:'Lettuce',emoji:'🥬'}, meat:{name:'Meat',emoji:'🥩'},
  potato:{name:'Potato',emoji:'🥔'}, dough:{name:'Dough',emoji:'🫓'}, cheese:{name:'Cheese',emoji:'🧀'}, bun:{name:'Bun',emoji:'🥯'},
};

const RECIPE_BOOK = {
  burger:{id:'burger',name:'Rush Burger',icon:'🍔',difficulty:'Medium',components:['bun:raw','meat:cooked','tomato:chopped'],workflow:[['Grocery','Bun'],['Grocery','Meat'],['Stove','Cook meat'],['Grocery','Tomato'],['Prep','Chop tomato'],['Plate + Counter','Assemble bun + meat + tomato'],['Table','Serve']]},
  salad:{id:'salad',name:'Garden Salad',icon:'🥗',difficulty:'Easy',components:['lettuce:chopped','tomato:chopped'],workflow:[['Grocery','Lettuce'],['Prep','Chop lettuce'],['Grocery','Tomato'],['Prep','Chop tomato'],['Plate + Counter','Assemble lettuce + tomato'],['Table','Serve']]},
  fries:{id:'fries',name:'Golden Fries',icon:'🍟',difficulty:'Medium',components:['potato:fried'],workflow:[['Grocery','Potato'],['Prep','Chop potato'],['Fryer','Fry until golden'],['Plate + Counter','Plate fries'],['Table','Serve']]},
  pizza:{id:'pizza',name:'Mini Pizza',icon:'🍕',difficulty:'Advanced',components:['dough:raw','tomato:chopped','cheese:raw'],baked:true,workflow:[['Grocery','Dough'],['Grocery','Tomato'],['Prep','Chop tomato'],['Grocery','Cheese'],['Plate + Counter','Assemble dough + tomato + cheese'],['Oven','Bake assembled plate'],['Table','Serve']]},
  grill:{id:'grill',name:'Grill Plate',icon:'🍗',difficulty:'Medium',components:['meat:cooked','lettuce:chopped'],workflow:[['Grocery','Meat'],['Stove','Cook meat'],['Grocery','Lettuce'],['Prep','Chop lettuce'],['Plate + Counter','Assemble meat + lettuce'],['Table','Serve']]},
  toast:{id:'toast',name:'Cheesy Toast',icon:'🥪',difficulty:'Easy',components:['bun:raw','cheese:raw'],baked:true,workflow:[['Grocery','Bun'],['Grocery','Cheese'],['Plate + Counter','Assemble bun + cheese'],['Oven','Bake assembled plate'],['Table','Serve']]},
};

const mouse = {
  leftDown:false,
  rightDown:false,
  moveTarget:null,
  action:null,
  selectedTarget:null,
  pointer:{x:0,y:0},
};

const effects = [];
let uiTick = 0;
let cleanlinessWarningCooldown = 0;

const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
const distanceXZ = (a,b) => Math.hypot(a.x-b.x,a.z-b.z);
const pointOf = target => target?.pos || target?.group?.position || null;
const signature = item => `${item.kind}:${item.state}`;
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function ensureConfig(){
  if (!Array.isArray(game.config.avatars)) game.config.avatars = AVATAR_DEFAULTS.map(v=>({...v}));
  while (game.config.avatars.length < 3) game.config.avatars.push({...AVATAR_DEFAULTS[game.config.avatars.length]});
  game.config.avatars = game.config.avatars.slice(0,3).map((a,i)=>({...AVATAR_DEFAULTS[i],...(a||{})}));
}
ensureConfig();

const baseSanitizeConfig = game.sanitizeConfig.bind(game);
game.sanitizeConfig = function sanitizeConfigV8(){
  baseSanitizeConfig();
  ensureConfig();
};

function saveConfig(){
  try { localStorage.setItem('robledo_kitchen_rush_config', JSON.stringify(game.config)); } catch (_) {}
}

function canvasSprite(text,bg='#26363d',fg='#fff',width=560,height=100,font=30){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const ctx=canvas.getContext('2d');
  ctx.fillStyle=bg;ctx.beginPath();ctx.roundRect(5,5,width-10,height-10,22);ctx.fill();
  ctx.fillStyle=fg;ctx.font=`800 ${font}px system-ui`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,width/2,height/2);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false}));
  sprite.userData.v8Canvas=canvas;sprite.userData.v8Texture=texture;sprite.userData.v8Text=text;
  return sprite;
}

function updateCanvasSprite(sprite,text,bg='#26363d',fg='#fff'){
  if (!sprite || sprite.userData.v8Text===text) return;
  const canvas=sprite.userData.v8Canvas,ctx=canvas?.getContext('2d');if(!ctx)return;
  ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle=bg;ctx.beginPath();ctx.roundRect(5,5,canvas.width-10,canvas.height-10,22);ctx.fill();
  ctx.fillStyle=fg;ctx.font='800 30px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,canvas.width/2,canvas.height/2);
  sprite.userData.v8Texture.needsUpdate=true;sprite.userData.v8Text=text;
}

function mat(color,opts={}){return new THREE.MeshStandardMaterial({color,roughness:opts.roughness??.7,metalness:opts.metalness??0,transparent:!!opts.transparent,opacity:opts.opacity??1});}

function decorateChef(group,avatar,role,index){
  group.userData.v8Avatar={...avatar};
  const oldLabels=[];group.traverse(o=>{if(o.isSprite&&o.position.y>2)oldLabels.push(o);});oldLabels.forEach(s=>s.visible=false);
  const apron=new THREE.Mesh(new THREE.BoxGeometry(.48,.56,.045),mat(APRON_COLORS[avatar.apron%APRON_COLORS.length]));apron.position.set(0,.83,.27);apron.geometry.translate(0,0,0);group.add(apron);
  const trim=new THREE.Mesh(new THREE.BoxGeometry(.5,.055,.055),mat(UNIFORM_COLORS[avatar.uniform%UNIFORM_COLORS.length]));trim.position.set(0,.63,.285);group.add(trim);
  if(avatar.hairStyle==='bun'){
    const bun=new THREE.Mesh(new THREE.SphereGeometry(.18,14,10),mat(HAIR_COLORS[avatar.hair%HAIR_COLORS.length]));bun.position.set(0,1.83,-.19);group.add(bun);
  }else if(avatar.hairStyle==='curls'){
    for(const [x,y,z] of [[-.22,1.73,-.12],[.22,1.73,-.12],[-.17,1.58,-.23],[.17,1.58,-.23]]){const c=new THREE.Mesh(new THREE.SphereGeometry(.13,12,8),mat(HAIR_COLORS[avatar.hair%HAIR_COLORS.length]));c.position.set(x,y,z);group.add(c);}
  }else if(avatar.hairStyle==='long'){
    const h=new THREE.Mesh(new THREE.CapsuleGeometry(.16,.4,4,10),mat(HAIR_COLORS[avatar.hair%HAIR_COLORS.length]));h.position.set(0,1.48,-.24);h.scale.set(1.7,1,1);group.add(h);
  }
  if(avatar.accessory==='glasses'){
    const gm=new THREE.MeshStandardMaterial({color:0x28363c,roughness:.3,metalness:.45});
    for(const x of[-.105,.105]){const rim=new THREE.Mesh(new THREE.TorusGeometry(.07,.012,6,16),gm);rim.position.set(x,1.59,.306);group.add(rim);}const bridge=new THREE.Mesh(new THREE.BoxGeometry(.07,.012,.012),gm);bridge.position.set(0,1.59,.307);group.add(bridge);
  }else if(avatar.accessory==='bandana'){
    const band=new THREE.Mesh(new THREE.CylinderGeometry(.318,.318,.08,24),mat(APRON_COLORS[avatar.apron%APRON_COLORS.length]));band.position.set(0,1.78,0);group.add(band);
  }else if(avatar.accessory==='neckerchief'){
    const scarf=new THREE.Mesh(new THREE.TorusGeometry(.17,.035,8,20),mat(APRON_COLORS[avatar.apron%APRON_COLORS.length]));scarf.rotation.x=Math.PI/2;scarf.position.set(0,1.34,.03);group.add(scarf);
  }
  const scaleX=avatar.build==='slim'?.94:avatar.build==='broad'?1.08:1;group.scale.x*=scaleX;
  const name=String(avatar.name||`Chef ${index+1}`);
  const label=canvasSprite(`${name} • ${role.toUpperCase()}`,'#223038','#fff',620,96,27);label.position.set(0,2.5,0);label.scale.set(2.8,.44,1);group.add(label);
}

const baseChefFactory = game.assets.chef.bind(game.assets);
game.assets.chef = function chefV8(color,role='chef',index=0,isBot=false){
  ensureConfig();
  const avatar=game.config.avatars[index]||AVATAR_DEFAULTS[index]||AVATAR_DEFAULTS[0];
  const skinIndex=index%this.skin.length,hairIndex=index%this.hair.length;
  const oldSkin=this.skin[skinIndex],oldHair=this.hair[hairIndex];
  this.skin[skinIndex]=SKIN_TONES[avatar.skin%SKIN_TONES.length];this.hair[hairIndex]=HAIR_COLORS[avatar.hair%HAIR_COLORS.length];
  const group=baseChefFactory(UNIFORM_COLORS[avatar.uniform%UNIFORM_COLORS.length]??color,role,index,isBot);
  this.skin[skinIndex]=oldSkin;this.hair[hairIndex]=oldHair;
  if(!isBot)decorateChef(group,avatar,role,index);
  return group;
};

function installStyles(){
  if(document.getElementById('v8-style'))return;
  const style=document.createElement('style');style.id='v8-style';style.textContent=`
  #v8-customization{margin:16px 0 8px;padding:16px;border-radius:18px;background:linear-gradient(135deg,rgba(30,52,58,.92),rgba(51,83,82,.88));color:#fff;box-shadow:0 18px 45px rgba(20,30,35,.2)}
  #v8-customization .v8-head{display:flex;align-items:end;justify-content:space-between;gap:14px;margin-bottom:12px}#v8-customization h3{margin:0;font-size:20px}#v8-customization small{opacity:.82}
  .v8-avatar-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.v8-avatar-card{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.16);border-radius:15px;padding:12px}.v8-avatar-card.inactive{display:none}
  .v8-avatar-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}.v8-avatar-title b{font-size:14px}.v8-avatar-swatch{width:28px;height:28px;border-radius:50%;border:2px solid rgba(255,255,255,.8)}
  .v8-fields{display:grid;grid-template-columns:1fr 1fr;gap:8px}.v8-fields label{font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;opacity:.82}.v8-fields input,.v8-fields select{width:100%;margin-top:3px;padding:7px;border:0;border-radius:8px;background:#fff;color:#26363d;font-weight:700}
  #v8-service-board{position:fixed;right:16px;bottom:16px;z-index:24;width:min(330px,calc(100vw - 32px));background:rgba(24,39,45,.92);color:#fff;border:1px solid rgba(255,255,255,.16);border-radius:18px;padding:12px 14px;box-shadow:0 18px 50px rgba(0,0,0,.28);backdrop-filter:blur(12px);pointer-events:auto}
  #v8-service-board.hidden{display:none}.v8-board-head{display:flex;justify-content:space-between;align-items:center;gap:10px}.v8-board-head b{font-size:14px}.v8-board-head span{font-size:10px;opacity:.76}.v8-recipe-pin{margin-top:10px;padding:10px;background:rgba(255,255,255,.08);border-radius:12px}.v8-recipe-pin .title{font-weight:900}.v8-recipe-pin .route{font-size:11px;line-height:1.4;opacity:.88;margin-top:4px}
  .v8-meter{margin-top:9px}.v8-meter-row{display:flex;justify-content:space-between;font-size:11px;font-weight:800}.v8-meter-track{height:7px;margin-top:4px;background:rgba(255,255,255,.12);border-radius:999px;overflow:hidden}.v8-meter-fill{height:100%;background:linear-gradient(90deg,#e34f51,#f2bd3f,#4d9a67);border-radius:999px}
  .v8-goals{display:grid;grid-template-columns:1fr;gap:5px;margin-top:9px}.v8-goal{display:flex;justify-content:space-between;gap:8px;font-size:11px;padding:6px 8px;border-radius:9px;background:rgba(255,255,255,.06)}.v8-goal.done{background:rgba(77,154,103,.26)}
  .v8-stock{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}.v8-stock span{font-size:10px;background:rgba(255,255,255,.08);padding:4px 6px;border-radius:8px}.v8-stock span.low{background:rgba(227,79,81,.28)}
  #v8-action-card{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:25;min-width:260px;max-width:min(560px,80vw);padding:9px 14px;border-radius:14px;background:rgba(245,241,226,.96);color:#223038;box-shadow:0 15px 40px rgba(0,0,0,.22);font-weight:800;text-align:center;pointer-events:none}#v8-action-card.hidden{display:none}#v8-action-card small{display:block;font-weight:650;opacity:.75;margin-top:2px}
  .recipe-card.v8-recipe{position:relative}.v8-difficulty{display:inline-block;font-size:10px;font-weight:900;padding:3px 7px;border-radius:999px;background:#26363d;color:#fff;margin-bottom:6px}.v8-flow{display:grid;gap:5px;margin-top:9px}.v8-flow div{display:grid;grid-template-columns:92px 1fr;gap:7px;font-size:11px;text-align:left;padding:6px;border-radius:8px;background:rgba(34,48,56,.06)}.v8-flow b{color:#d65e38}.v8-pin-btn{margin-top:9px;width:100%;padding:7px;border-radius:9px;border:0;background:#26363d;color:#fff;font-weight:900;cursor:pointer}
  .order-card{cursor:pointer}.order-card:hover{transform:translateY(-1px)}
  @media(max-width:900px){.v8-avatar-grid{grid-template-columns:1fr}.v8-fields{grid-template-columns:1fr 1fr}#v8-service-board{width:280px}.v8-avatar-card.inactive{display:none}}
  `;document.head.appendChild(style);
}
installStyles();

function avatarOptions(values,current){return values.map(([value,label])=>`<option value="${value}" ${String(current)===String(value)?'selected':''}>${label}</option>`).join('');}
function renderCustomization(){
  const slots=document.getElementById('crew-slots');if(!slots)return;
  let panel=document.getElementById('v8-customization');if(!panel){panel=document.createElement('section');panel.id='v8-customization';slots.insertAdjacentElement('afterend',panel);}
  ensureConfig();
  const gender=[['female','Female'],['male','Male'],['nonbinary','Non-binary'],['neutral','Neutral / not specified']];
  const hairStyle=[['short','Short'],['bun','Bun'],['curls','Curls'],['long','Long']];
  const accessory=[['none','None'],['glasses','Glasses'],['bandana','Bandana'],['neckerchief','Neckerchief']];
  const build=[['slim','Slim'],['standard','Standard'],['broad','Broad']];
  panel.innerHTML=`<div class="v8-head"><div><span class="eyebrow">SENIOR V8 • CHARACTER PERSONALIZATION</span><h3>Customize every active chef</h3></div><small>Gender does not restrict hair, colors, clothes or accessories.</small></div><div class="v8-avatar-grid">${game.config.avatars.map((a,i)=>`<article class="v8-avatar-card ${i>=game.config.humanCount?'inactive':''}" data-avatar="${i}"><div class="v8-avatar-title"><b>PLAYER ${i+1}</b><i class="v8-avatar-swatch" style="background:#${UNIFORM_COLORS[a.uniform%UNIFORM_COLORS.length].toString(16).padStart(6,'0')}"></i></div><div class="v8-fields">
    <label>Name<input data-field="name" maxlength="18" value="${escapeHtml(a.name)}"/></label>
    <label>Gender<select data-field="gender">${avatarOptions(gender,a.gender)}</select></label>
    <label>Skin tone<select data-field="skin">${SKIN_TONES.map((_,n)=>`<option value="${n}" ${Number(a.skin)===n?'selected':''}>Tone ${n+1}</option>`).join('')}</select></label>
    <label>Body build<select data-field="build">${avatarOptions(build,a.build)}</select></label>
    <label>Hair<select data-field="hairStyle">${avatarOptions(hairStyle,a.hairStyle)}</select></label>
    <label>Hair color<select data-field="hair">${HAIR_COLORS.map((_,n)=>`<option value="${n}" ${Number(a.hair)===n?'selected':''}>Color ${n+1}</option>`).join('')}</select></label>
    <label>Uniform<select data-field="uniform">${UNIFORM_COLORS.map((_,n)=>`<option value="${n}" ${Number(a.uniform)===n?'selected':''}>Uniform ${n+1}</option>`).join('')}</select></label>
    <label>Apron<select data-field="apron">${APRON_COLORS.map((_,n)=>`<option value="${n}" ${Number(a.apron)===n?'selected':''}>Apron ${n+1}</option>`).join('')}</select></label>
    <label>Accessory<select data-field="accessory">${avatarOptions(accessory,a.accessory)}</select></label>
  </div></article>`).join('')}</div>`;
  panel.querySelectorAll('[data-avatar]').forEach(card=>{
    const index=Number(card.dataset.avatar);card.querySelectorAll('[data-field]').forEach(input=>{
      const save=()=>{const field=input.dataset.field;let value=input.value;if(['skin','hair','uniform','apron'].includes(field))value=Number(value);game.config.avatars[index][field]=value;saveConfig();if(field==='uniform'){const sw=card.querySelector('.v8-avatar-swatch');sw.style.background=`#${UNIFORM_COLORS[value%UNIFORM_COLORS.length].toString(16).padStart(6,'0')}`;}};
      input.addEventListener(input.tagName==='INPUT'?'input':'change',save);
    });
  });
}

const baseRenderCrewSetup=game.renderCrewSetup.bind(game);
game.renderCrewSetup=function renderCrewSetupV8(){
  baseRenderCrewSetup();ensureConfig();
  const cards=[...document.querySelectorAll('#crew-slots .crew-slot')];cards.forEach((card,i)=>{
    if(i>=game.config.humanCount){card.style.display='none';return;}card.style.display='';card.classList.remove('bot');card.classList.add('human');
    const kind=card.querySelector('.crew-kind');if(kind)kind.textContent=game.config.humanCount===1?'SOLO HUMAN':'HUMAN';
    const line=card.querySelector('.device-line');if(line){if(i===0)line.textContent='🖱 P1 • left/right click both perform kitchen actions';if(i===1)line.textContent='⌨ P2 • WASD • F target • E interact • Q throw';if(i===2)line.textContent='⌨ P3 • arrows • . target • Enter interact • / throw';}
  });
  const micro=document.querySelector('#crew-screen .setup-panel .micro');if(micro)micro.textContent='Choose 1, 2 or 3 human players. In solo mode you start completely alone: no AI chefs are added. The solo service rate and customer patience scale so one chef can take orders, cook, serve and clean personally.';
  renderCustomization();
};

function renderRecipeBook(){
  const grid=document.getElementById('recipe-grid');if(!grid)return;
  grid.innerHTML=Object.values(RECIPE_BOOK).map(r=>`<article class="recipe-card v8-recipe" data-recipe="${r.id}"><div class="recipe-icon">${r.icon}</div><span class="v8-difficulty">${r.difficulty}</span><h3>${r.name}</h3><div class="ingredients">${r.components.map(sig=>{const[k,s]=sig.split(':');return`${INGREDIENT[k]?.emoji||''} ${s==='raw'?'':`${s} `}${INGREDIENT[k]?.name||k}`}).join(' + ')}</div><div class="v8-flow">${r.workflow.map(([station,action],i)=>`<div><b>${i+1}. ${station}</b><span>${action}</span></div>`).join('')}</div><button class="v8-pin-btn" data-pin="${r.id}">PIN RECIPE</button></article>`).join('');
  grid.querySelectorAll('[data-pin]').forEach(btn=>btn.onclick=()=>{game.v8PinnedRecipe=btn.dataset.pin;updateServiceBoard(true);game.flash(`${RECIPE_BOOK[btn.dataset.pin].name} pinned to service board.`);});
}
renderRecipeBook();

function installServiceUI(){
  if(!document.getElementById('v8-service-board')){const el=document.createElement('aside');el.id='v8-service-board';el.className='hidden';document.getElementById('game-shell')?.appendChild(el);}
  if(!document.getElementById('v8-action-card')){const el=document.createElement('div');el.id='v8-action-card';el.className='hidden';document.getElementById('game-shell')?.appendChild(el);}
}
installServiceUI();

const baseTier=game.tier.bind(game);
game.tier=function tierV8(){
  const t=baseTier();const humans=clamp(Number(this.config.humanCount)||1,1,3);
  if(humans===1)return{...t,customerCap:Math.min(t.customerCap,2+Math.floor(this.business.expansionTier/2)),partySize:Math.min(t.partySize,2)};
  if(humans===2)return{...t,customerCap:Math.min(t.customerCap,4),partySize:Math.min(t.partySize,3)};
  return t;
};

function cleanupRemovedPlayer(player){
  player.group?.removeFromParent();
  player.__v8SelectionRing?.removeFromParent();
  if(player.held){player.held.dispose?.();player.held=null;}
}

const baseSpawnPlayers=game.spawnPlayers.bind(game);
game.spawnPlayers=function spawnPlayersV8(){
  baseSpawnPlayers();
  const desired=clamp(Number(this.config.humanCount)||1,1,3);
  const keep=this.players.filter(p=>p.human).slice(0,desired);
  this.players.filter(p=>!keep.includes(p)).forEach(cleanupRemovedPlayer);
  this.players=keep;
  this.players.forEach(installHumanController);
  this.renderPlayerHud();
  this.qaRecord('v8-human-roster',{humans:this.players.length,bots:0});
};

const baseRenderPlayerHud=game.renderPlayerHud.bind(game);
game.renderPlayerHud=function renderPlayerHudV8(){
  baseRenderPlayerHud();ensureConfig();
  this.players.forEach((p,i)=>{const chip=document.querySelector(`#player-hud .player-chip.p${i+1} .line b`);if(chip)chip.textContent=`P${i+1} • ${game.config.avatars[i]?.name||`Chef ${i+1}`} • ${p.role.toUpperCase()}`;const em=document.querySelector(`#player-hud .player-chip.p${i+1} .line em`);if(em)em.textContent=this.players.length===1?'SOLO':'HUMAN';});
};

function validTarget(target){
  if(!target||target.dead)return false;
  if(target.type==='table')return game.tables.includes(target);
  if(game.stations.includes(target))return true;
  if(game.items.includes(target))return !target.dead;
  return !!target.group?.parent;
}
function labelOf(target){
  if(!target)return'NONE';if(target.type==='storage')return`${INGREDIENT[target.kind]?.name||target.kind} • Grocery`;if(target.type==='table')return`Table ${target.id+1}`;if(typeof target.description==='function')return target.description();return String(target.type||target.kind||'target').replace(/\b\w/g,m=>m.toUpperCase());
}

function makeSelectionRing(player){
  if(player.__v8SelectionRing)return;
  const ring=new THREE.Mesh(new THREE.RingGeometry(.52,.69,36),new THREE.MeshBasicMaterial({color:PLAYER_COLORS[player.index],transparent:true,opacity:.95,side:THREE.DoubleSide,depthTest:false}));
  ring.rotation.x=-Math.PI/2;ring.visible=false;ring.renderOrder=120;game.scene.add(ring);player.__v8SelectionRing=ring;
}
function selectTarget(player,target){
  player.selectedTarget=validTarget(target)?target:null;if(player.index===0)mouse.selectedTarget=player.selectedTarget;
  makeSelectionRing(player);const ring=player.__v8SelectionRing;if(!player.selectedTarget){ring.visible=false;return;}
  const p=pointOf(player.selectedTarget);if(p){ring.position.set(p.x,.075,p.z);ring.visible=true;}
}
function updateSelectionRing(player){
  if(!validTarget(player.selectedTarget)){selectTarget(player,null);return;}const p=pointOf(player.selectedTarget);if(p&&player.__v8SelectionRing){player.__v8SelectionRing.position.set(p.x,.075,p.z);player.__v8SelectionRing.rotation.z+=.015;player.__v8SelectionRing.visible=true;}
}

const baseClearGameplay=game.clearGameplay.bind(game);
game.clearGameplay=function clearGameplayV8(keepStatic=false){
  for(const p of this.players||[])p.__v8SelectionRing?.removeFromParent();
  for(const e of effects)if(e.kind==='particle')e.group?.removeFromParent();
  effects.length=0;mouse.action=null;mouse.moveTarget=null;mouse.selectedTarget=null;mouse.leftDown=false;mouse.rightDown=false;
  return baseClearGameplay(keepStatic);
};

function carriedItems(){return new Set(game.players.map(p=>p.held).filter(Boolean));}
game.nearestInteractable=function nearestInteractableV8(pos,range=INTERACT_RANGE){
  let best=null,bd=range;const carried=carriedItems();
  for(const s of this.stations){const d=distanceXZ(pos,s.pos);if(d<bd){best=s;bd=d;}}
  for(const t of this.tables){const d=distanceXZ(pos,t.pos);if(d<bd){best=t;bd=d;}}
  for(const item of this.items){if(carried.has(item)||item.dead||item.airborne||item.onSurface)continue;const d=distanceXZ(pos,item.group.position);if(d<bd){best=item;bd=d;}}
  return best;
};

function targetsFor(player,range=SELECT_RANGE){
  const pos=player.group.position,carried=carriedItems(),out=[];
  for(const s of game.stations)if(distanceXZ(pos,s.pos)<=range)out.push(s);
  for(const t of game.tables)if(distanceXZ(pos,t.pos)<=range)out.push(t);
  for(const i of game.items)if(!carried.has(i)&&!i.dead&&!i.airborne&&!i.onSurface&&distanceXZ(pos,i.group.position)<=range)out.push(i);
  out.sort((a,b)=>distanceXZ(pos,pointOf(a))-distanceXZ(pos,pointOf(b)));return out;
}
function cycleTarget(player){const list=targetsFor(player);if(!list.length){selectTarget(player,null);return;}const i=list.indexOf(player.selectedTarget);selectTarget(player,list[(i+1)%list.length]);game.flash(`P${player.index+1} target: ${labelOf(player.selectedTarget)}`);}

function pointerNdc(event){const r=game.canvas.getBoundingClientRect();return new THREE.Vector2(((event.clientX-r.left)/r.width)*2-1,-(((event.clientY-r.top)/r.height)*2-1));}
function belongsTo(object,group){for(let n=object;n;n=n.parent)if(n===group)return true;return false;}
function floorFromPointer(event){game.raycaster.setFromCamera(pointerNdc(event),game.camera);const p=new THREE.Vector3();return game.raycaster.ray.intersectPlane(game.floorPlane,p)?p:null;}
function targetNearWorldPoint(point,player){
  if(!point)return null;let best=null,bd=1.75;const carried=carriedItems();
  for(const s of game.stations){const d=distanceXZ(point,s.pos);if(d<bd){best=s;bd=d;}}
  for(const t of game.tables){const d=distanceXZ(point,t.pos);if(d<bd){best=t;bd=d;}}
  for(const i of game.items){if(carried.has(i)||i.dead||i.airborne||i.onSurface)continue;const d=distanceXZ(point,i.group.position);if(d<bd){best=i;bd=d;}}
  return best;
}
function targetFromPointer(event,player){
  game.raycaster.setFromCamera(pointerNdc(event),game.camera);
  const roots=[...game.fixtureRoot.children,...game.itemRoot.children];const hits=game.raycaster.intersectObjects(roots,true);
  for(const hit of hits){
    const item=game.items.find(i=>i!==player.held&&!i.dead&&belongsTo(hit.object,i.group));if(item)return item;
    const table=game.tables.find(t=>belongsTo(hit.object,t.group));if(table)return table;
    const stations=game.stations.filter(s=>belongsTo(hit.object,s.group));if(stations.length){stations.sort((a,b)=>hit.point.distanceToSquared(a.pos)-hit.point.distanceToSquared(b.pos));return stations[0];}
  }
  return targetNearWorldPoint(floorFromPointer(event),player);
}

function freePoint(player,p){return !game.blocked(player,p);}
function approachPoint(player,target){
  const center=pointOf(target);if(!center)return null;if(!target.type||!['table','storage','prep','stove','fryer','oven','sink','counter','plate','trash'].includes(target.type))return center.clone?.()||new THREE.Vector3(center.x,0,center.z);
  const radius=target.type==='table'?1.72:target.type==='storage'?1.18:1.52,candidates=[];
  for(let i=0;i<24;i++){const a=i*Math.PI/12,c=new THREE.Vector3(center.x+Math.cos(a)*radius,0,center.z+Math.sin(a)*radius);if(freePoint(player,c))candidates.push(c);}
  if(!candidates.length)return new THREE.Vector3(center.x,0,center.z);
  candidates.sort((a,b)=>a.distanceToSquared(player.group.position)-b.distanceToSquared(player.group.position));return candidates[0];
}
function steerPlayer(player,destination,dt,boost=1){
  if(!destination)return false;const delta=destination.clone().sub(player.group.position);delta.y=0;const dist=delta.length();if(dist<.08)return false;delta.normalize();player.facing.copy(delta);player.group.rotation.y=Math.atan2(delta.x,delta.z);const step=player.speed*boost*dt,before=player.group.position.clone();game.moveCrew(player,delta.clone().multiplyScalar(step));
  if(before.distanceToSquared(player.group.position)<1e-7){const side=new THREE.Vector3(-delta.z,0,delta.x);const sign=player.__v8AvoidSign||1;game.moveCrew(player,side.multiplyScalar(sign*step*.85));if(before.distanceToSquared(player.group.position)<1e-7){player.__v8AvoidSign=-sign;game.moveCrew(player,new THREE.Vector3(delta.z,0,-delta.x).multiplyScalar(sign*step*.85));}}
  return before.distanceToSquared(player.group.position)>1e-7;
}

function smartHintForHeld(player){
  const h=player.held;if(!h)return'Take an order, pick an ingredient, collect a clean plate, or clean a table.';
  if(h.isPlate){if(h.dirty)return'Bring the dirty plate to the Sink and hold interact to wash.';const rid=identifyRecipeV8(h);if(rid)return`${RECIPE_BOOK[rid].name} is ready — serve the matching table.`;if(!h.components.length)return'Place this clean plate on the Counter, then add prepared ingredients.';return'Continue adding the exact recipe components at the Counter.';}
  if(h.kind==='meat'&&h.state==='raw')return'Raw meat → Stove.';
  if(h.kind==='potato'&&h.state==='raw')return'Raw potato → Prep Board first.';
  if(h.kind==='potato'&&h.state==='chopped')return'Chopped potato → Fryer.';
  if(['tomato','lettuce'].includes(h.kind)&&h.state==='raw')return`${INGREDIENT[h.kind].name} → Prep Board.`;
  if(['chopped','cooked','fried'].includes(h.state)||['bun','cheese','dough'].includes(h.kind))return`${INGREDIENT[h.kind]?.name||h.kind} is ready for assembly at a Counter with a clean plate.`;
  return'Use the highlighted kitchen station.';
}

function identifyRecipeV8(plate){
  if(!plate?.isPlate||plate.dirty||plate.burnt)return null;const sigs=(plate.components||[]).map(signature).sort();for(const r of Object.values(RECIPE_BOOK)){const req=[...r.components].sort();if(req.length===sigs.length&&req.every((x,i)=>x===sigs[i])&&!!r.baked===!!plate.baked)return r.id;}return null;
}

function queueAction(player,target,mode='smart'){
  if(!validTarget(target))return;selectTarget(player,target);const dest=approachPoint(player,target);mouse.moveTarget=dest;mouse.action={target,mode,didFire:false,started:performance.now(),destination:dest,lastWorkState:null};
  game.flash(`P1 → ${labelOf(target)} • ${mode==='hold'?'RIGHT HOLD':'CLICK ACTION'} queued`);
}

function keyboardState(index){
  const keys=game.input.keys,gp=game.input.pollGamepad(index);const map=index===1?{up:'KeyW',down:'KeyS',left:'KeyA',right:'KeyD',interact:'KeyE',select:'KeyF',throw:'KeyQ',dash:'ShiftLeft'}:{up:'ArrowUp',down:'ArrowDown',left:'ArrowLeft',right:'ArrowRight',interact:'Enter',select:'Period',throw:'Slash',dash:'ShiftRight'};
  let x=(keys.has(map.right)?1:0)-(keys.has(map.left)?1:0),y=(keys.has(map.down)?1:0)-(keys.has(map.up)?1:0);if(gp&&(Math.abs(gp.x)+Math.abs(gp.y)>.05)){x=gp.x;y=gp.y;}
  return{x,y,interact:keys.has(map.interact)||!!gp?.interact,select:keys.has(map.select)||false,throw:keys.has(map.throw)||!!gp?.throw,dash:keys.has(map.dash)||!!gp?.dash};
}
const originalInputState=game.input.state.bind(game.input);
game.input.state=function inputStateV8(index){
  if(index===0){const gp=this.pollGamepad(0);return{x:gp?.x||0,y:gp?.y||0,interact:mouse.rightDown||!!gp?.interact,select:false,throw:false,dash:!!gp?.dash};}
  if(index===1||index===2)return keyboardState(index);return originalInputState(index);
};

function installHumanController(player){
  if(!player.human||player.__v8Installed)return;player.__v8Installed=true;player.prevInteract=false;player.prevSelect=false;player.prevThrow=false;player.__v8AvoidSign=player.index%2?1:-1;makeSelectionRing(player);
  const basePick=player.pick.bind(player);player.pick=function pickV8(item){const ok=basePick(item);if(ok){item.__v8HeldAt=performance.now();item.__v8BaseScale=item.group.scale.clone();pulseObject(this.group,PLAYER_COLORS[this.index]);emitParticles(item.group.position,PLAYER_COLORS[this.index],5);}return ok;};
  player.updateHuman=function updateHumanV8(dt,input){
    this.dashCooldown=Math.max(0,this.dashCooldown-dt);let dx=input.x||0,dz=input.y||0;let autoMoving=false;
    if(this.index===0&&!dx&&!dz){
      if(mouse.action&&validTarget(mouse.action.target)){
        const target=mouse.action.target,p=pointOf(target),distance=p?distanceXZ(this.group.position,p):999;
        if(distance>INTERACT_RANGE-.08){const dest=approachPoint(this,target);mouse.action.destination=dest;autoMoving=steerPlayer(this,dest,dt,1);}
        else{
          const continuous=target.type==='prep'||target.type==='sink';
          const shouldWork=mouse.action.mode==='smart'?(!mouse.action.didFire||continuous):mouse.rightDown&&(!mouse.action.didFire||continuous);
          if(shouldWork){const before=interactionFingerprint(this,target);game.interact(this,target,dt,true);const after=interactionFingerprint(this,target);mouse.action.didFire=true;if(before!==after)interactionSuccess(this,target,before,after);}
          if(mouse.action.mode==='smart'){
            if(!continuous||smartWorkComplete(this,target))mouse.action=null;
          }else if(!mouse.rightDown)mouse.action=null;
        }
      }else if(mouse.moveTarget){const d=distanceXZ(this.group.position,mouse.moveTarget);if(d>.14)autoMoving=steerPlayer(this,mouse.moveTarget,dt,1);else mouse.moveTarget=null;}
    }
    const len=Math.hypot(dx,dz);if(len>.001){dx/=Math.max(1,len);dz/=Math.max(1,len);this.facing.set(dx,0,dz);this.group.rotation.y=Math.atan2(dx,dz);mouse.moveTarget=null;mouse.action=null;}
    const boost=input.dash&&this.dashCooldown<=0?1.65:1;if(boost>1)this.dashCooldown=.22;if(len>.001)game.moveCrew(this,new THREE.Vector3(dx,0,dz).multiplyScalar(this.speed*boost*dt));
    this.animate(dt,len>.05||autoMoving,boost);
    if(input.select&&!this.prevSelect)cycleTarget(this);this.prevSelect=!!input.select;
    if(input.throw&&!this.prevThrow)this.throwItem();this.prevThrow=!!input.throw;
    if(this.index>0){let target=this.selectedTarget;if(!validTarget(target)||distanceXZ(this.group.position,pointOf(target))>INTERACT_RANGE)target=game.nearestInteractable(this.group.position,INTERACT_RANGE);const continuous=target&&(target.type==='prep'||target.type==='sink');if(input.interact&&target&&(continuous||!this.prevInteract)){const before=interactionFingerprint(this,target);game.interact(this,target,dt,true);const after=interactionFingerprint(this,target);if(before!==after)interactionSuccess(this,target,before,after);}this.prevInteract=!!input.interact;}
    updateSelectionRing(this);animateHeldItem(this,dt);
  };
}

function interactionFingerprint(player,target){return JSON.stringify({held:player.held?`${player.held.kind}:${player.held.state}:${player.held.dirty?'dirty':''}`:null,slot:target?.slot?`${target.slot.kind}:${target.slot.state}:${target.slot.dirty?'dirty':''}:${target.slot.baked?'baked':''}`:null,progress:Math.round((target?.progress||0)*10),party:target?.party?.state||null,dirty:target?.dirty||0});}
function smartWorkComplete(player,target){if(target.type==='prep')return !target.slot||target.slot.state!=='raw';if(target.type==='sink')return !target.slot||!target.slot.dirty;return true;}
function interactionSuccess(player,target,before,after){
  game.v8Shift.interactions++;pulseTarget(target);const p=pointOf(target)||player.group.position;emitParticles(p,PLAYER_COLORS[player.index],4);game.qaRecord('v8-human-interact',{player:player.index+1,target:target.type||target.kind,before,after});
}

function pulseObject(group,color=0xffffff){if(!group)return;effects.push({kind:'pulse',group,t:0,d:.28,color,base:group.scale.clone()});}
function pulseTarget(target){const group=target?.group;if(group)pulseObject(group,0xf2bd3f);}
function emitParticles(position,color=0xf2bd3f,count=6){
  if(!position)return;for(let i=0;i<count;i++){const m=new THREE.Mesh(new THREE.SphereGeometry(.035,7,6),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.9}));m.position.copy(position).add(new THREE.Vector3((Math.random()-.5)*.35,.7+Math.random()*.35,(Math.random()-.5)*.35));m.userData.v=new THREE.Vector3((Math.random()-.5)*.8,.7+Math.random()*.7,(Math.random()-.5)*.8);game.scene.add(m);effects.push({kind:'particle',group:m,t:0,d:.55});}}
function animateHeldItem(player){const item=player.held;if(!item)return;const age=(performance.now()-(item.__v8HeldAt||performance.now()))/1000;item.group.rotation.y+=.03;item.group.position.y+=Math.sin(age*8)*.018;}
function updateEffects(dt){for(let i=effects.length-1;i>=0;i--){const e=effects[i];e.t+=dt;const q=clamp(e.t/e.d,0,1);if(e.kind==='particle'){e.group.position.addScaledVector(e.group.userData.v,dt);e.group.userData.v.y-=2.3*dt;if(e.group.material)e.group.material.opacity=1-q;}else if(e.kind==='pulse'&&e.group.parent){const s=1+Math.sin(q*Math.PI)*.12;e.group.scale.copy(e.base).multiplyScalar(s);}if(q>=1){if(e.kind==='particle')e.group.removeFromParent();else if(e.kind==='pulse'&&e.group.parent)e.group.scale.copy(e.base);effects.splice(i,1);}}
}

// Both mouse buttons now perform a real action. Left-clicking an object is a smart
// action (approach + interact); right-clicking is manual hold-to-work. Floor left
// click remains click-to-move. Capture phase prevents the older camera listener
// from stealing the service interaction.
game.canvas.addEventListener('contextmenu',e=>{if(game.state==='playing')e.preventDefault();});
game.canvas.addEventListener('pointerdown',event=>{
  if(game.state!=='playing')return;const p1=game.players[0];if(!p1?.human)return;mouse.pointer={x:event.clientX,y:event.clientY};
  if(event.button===0){mouse.leftDown=true;const target=targetFromPointer(event,p1);if(target)queueAction(p1,target,'smart');else{selectTarget(p1,null);mouse.action=null;const floor=floorFromPointer(event);if(floor)mouse.moveTarget=floor.clone();}event.preventDefault();event.stopImmediatePropagation();}
  else if(event.button===2){mouse.rightDown=true;const target=targetFromPointer(event,p1)||p1.selectedTarget||game.nearestInteractable(p1.group.position,SELECT_RANGE);if(target)queueAction(p1,target,'hold');game.cameraRig.dragging=false;event.preventDefault();event.stopImmediatePropagation();}
  else if(event.button===1){if(p1.held)p1.throwItem();event.preventDefault();event.stopImmediatePropagation();}
},true);
game.canvas.addEventListener('pointerup',event=>{if(game.state!=='playing')return;if(event.button===0)mouse.leftDown=false;if(event.button===2){mouse.rightDown=false;game.cameraRig.dragging=false;if(mouse.action?.mode==='hold')mouse.action=null;}event.preventDefault();event.stopImmediatePropagation();},true);
game.canvas.addEventListener('pointercancel',()=>{mouse.leftDown=false;mouse.rightDown=false;if(mouse.action?.mode==='hold')mouse.action=null;},true);
game.canvas.addEventListener('mouseleave',()=>{mouse.leftDown=false;mouse.rightDown=false;if(mouse.action?.mode==='hold')mouse.action=null;},true);

function refreshControlsCopy(){
  const cards=document.querySelectorAll('#controls-screen .controls-grid article');
  if(cards[0])cards[0].innerHTML='<h3>PLAYER 1 • MOUSE</h3><p><b>Left click floor:</b> move<br/><b>Left click object:</b> approach + interact automatically<br/><b>Right click / hold:</b> interact / work manually<br/><b>Middle click:</b> throw held item</p>';
  if(cards[1])cards[1].innerHTML='<h3>PLAYER 2 • KEYBOARD</h3><p><b>Move:</b> WASD<br/><b>Target:</b> F<br/><b>Interact / work:</b> E<br/><b>Throw:</b> Q • <b>Dash:</b> Left Shift</p>';
  if(cards[2])cards[2].innerHTML='<h3>PLAYER 3 • KEYBOARD</h3><p><b>Move:</b> Arrow keys<br/><b>Target:</b> . (Period)<br/><b>Interact / work:</b> Enter<br/><b>Throw:</b> / • <b>Dash:</b> Right Shift</p>';
  if(cards[3])cards[3].innerHTML='<h3>CAMERA</h3><p><b>Service:</b> C cycles camera • Home resets • wheel zoom<br/><b>Build mode:</b> right-drag orbits camera<br/><b>Important:</b> during service right mouse belongs to Player 1 interaction.</p>';
}
refreshControlsCopy();

function ergonomicLayout(){
  const original=game.__v8OriginalAutoLayout;original();
  const b=game.currentBounds(),kitchenBack=b.zMin+1.15,kitchenFront=Math.min(-1.55,b.zMin+4.4);const byKey={};for(const q of game.plan)(byKey[q.key]??=[]).push(q);
  const set=(key,index,x,z,rot=0)=>{const q=byKey[key]?.[index];if(q){q.x=clamp(x,-b.xMax+.8,b.xMax-.8);q.z=clamp(z,b.zMin+.8,b.zMax-.8);q.rot=rot;}};
  set('grocery',0,0,kitchenBack,0);set('sink',0,-b.xMax+1.35,kitchenBack+.15,0);set('plate',0,-b.xMax+3.15,kitchenBack+.15,0);set('trash',0,b.xMax-1.2,kitchenBack+.15,0);
  const production=['prep','stove','fryer','oven','counter'],available=production.flatMap(k=>(byKey[k]||[]).map((q,i)=>({k,i,q})));const spacing=1.85,start=-((available.length-1)*spacing)/2;available.forEach((entry,i)=>set(entry.k,entry.i,start+i*spacing,kitchenFront,0));
  const tables=byKey.table||[],cols=Math.min(3,Math.max(2,Math.ceil(Math.sqrt(tables.length)))),rows=Math.ceil(tables.length/cols),xGap=Math.min(4.2,(b.xMax*2-3)/Math.max(1,cols-1)),zStart=2.15,zGap=3.15;tables.forEach((q,i)=>{const row=Math.floor(i/cols),col=i%cols,x=(col-(Math.min(cols,tables.length-row*cols)-1)/2)*xGap,z=zStart+row*zGap;q.x=clamp(x,-b.xMax+1.7,b.xMax-1.7);q.z=clamp(z,1.8,b.zMax-1.5);q.rot=(row%2)*Math.PI/2;});
  game.business.plan=game.plan.map(q=>({...q}));game.saveBusiness();game.renderPlanVisuals();game.updateBuildUI();game.updateGhost();game.flash('SENIOR V8 LAYOUT — clear production line, service aisle and spaced dining tables.');
}
game.__v8OriginalAutoLayout=game.autoLayout.bind(game);game.autoLayout=ergonomicLayout;

function initStock(){const needed=game.requiredIngredients?.()||Object.keys(INGREDIENT);const base=game.config.humanCount===1?8:game.config.humanCount===2?11:14;game.v8Stock={};needed.forEach(k=>game.v8Stock[k]=base);}
function storageCost(kind){return['meat','cheese'].includes(kind)?10:7;}
const baseInteract=game.interact.bind(game);
game.interact=function interactV8(player,target,dt,held){
  if(target?.type==='storage'&&!player.held){
    if(!this.v8Stock)this.v8Stock={};if(this.v8Stock[target.kind]==null)this.v8Stock[target.kind]=8;
    if(this.v8Stock[target.kind]<=0){const cost=storageCost(target.kind);if(this.business.cash<cost){this.sfx.bad();this.flash(`${INGREDIENT[target.kind]?.name||target.kind} is out of stock. Need $${cost} to restock.`);return;}this.business.cash-=cost;this.v8Stock[target.kind]=4;this.saveBusiness();this.flash(`Restocked ${INGREDIENT[target.kind]?.name||target.kind} ×4 for $${cost}.`);}
    const beforeHeld=player.held;baseInteract(player,target,dt,held);if(!beforeHeld&&player.held?.kind===target.kind){this.v8Stock[target.kind]=Math.max(0,this.v8Stock[target.kind]-1);player.held.__v8HeldAt=performance.now();}
    return;
  }
  return baseInteract(player,target,dt,held);
};

function decorateItem(item){
  if(!item||item.__v8Decorated)return;item.__v8Decorated=true;item.__v8Spawn=performance.now();item.__v8BaseScale=item.group.scale.clone();
  const halo=new THREE.Mesh(new THREE.RingGeometry(.25,.33,20),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.22,side:THREE.DoubleSide,depthTest:false}));halo.rotation.x=-Math.PI/2;halo.position.y=.035;item.group.add(halo);item.__v8Halo=halo;
}
const baseSpawnItem=game.spawnItem.bind(game);game.spawnItem=function spawnItemV8(kind,state='raw',plate=false,pos=null){const item=baseSpawnItem(kind,state,plate,pos);decorateItem(item);return item;};
function animateItems(){const held=carriedItems(),t=performance.now()/1000;for(const item of game.items){if(item.dead)continue;decorateItem(item);if(item.__v8Halo)item.__v8Halo.material.opacity=held.has(item)?.08:(.18+.08*Math.sin(t*4+(item.__v8Spawn||0)));if(!held.has(item)&&!item.onSurface&&!item.airborne)item.group.rotation.y+=.006;}}

function partyBubbleText(party){
  if(party.state==='entering')return party.v8?.regular?'⭐ REGULAR':'👋 ARRIVING';if(party.state==='browsing')return'📖 CHOOSING';if(party.state==='readyToOrder')return'🙋 READY TO ORDER';if(party.state==='waiting'){const pct=party.patience/party.patienceMax;return pct>.66?'🙂 WAITING':pct>.35?'😐 GETTING HUNGRY':'😟 PLEASE HURRY';}if(party.state==='eating')return'😋 ENJOYING';if(party.state==='leaving')return party.v8?.servedFast?'⭐ GREAT SERVICE':'👋 LEAVING';return'';
}
function decorateParty(party){
  if(!party||party.v8)return;const loyalty=Number(game.business.loyalty)||0,regular=Math.random()<Math.min(.28,.06+loyalty*.0025);const traits=['Patient','Chatty','Food critic','In a hurry','Celebrating','Quiet'][Math.floor(Math.random()*6)];party.v8={regular,traits,servedFast:false};if(regular){party.patience*=1.1;party.patienceMax*=1.1;}
  const bubble=canvasSprite(partyBubbleText(party),regular?'#8b6a22':'#26363d','#fff',520,90,25);bubble.scale.set(2.1,.38,1);bubble.position.set(0,2.42,0);party.customers[0]?.group?.add(bubble);party.v8.bubble=bubble;
  if(regular&&party.customers[0]){const ring=new THREE.Mesh(new THREE.TorusGeometry(.38,.035,8,24),new THREE.MeshBasicMaterial({color:0xf2bd3f,transparent:true,opacity:.75}));ring.rotation.x=Math.PI/2;ring.position.y=.04;party.customers[0].group.add(ring);party.v8.regularRing=ring;}
  const baseUpdate=party.update.bind(party);party.update=function updatePartyV8(dt){const before=this.state;baseUpdate(dt);const text=partyBubbleText(this);if(this.v8?.bubble)updateCanvasSprite(this.v8.bubble,text,this.v8.regular?'#8b6a22':'#26363d','#fff');const now=performance.now()/1000;for(let i=0;i<this.customers.length;i++){const c=this.customers[i],limbs=c.group.userData.limbs;if(['browsing','readyToOrder','waiting','eating'].includes(this.state)){c.group.rotation.z=Math.sin(now*1.8+i)*.015;if(limbs&&this.state==='readyToOrder'&&i===0)limbs.rArm.rotation.z=-.55-.15*Math.sin(now*5);else if(limbs)limbs.rArm.rotation.z*=.82;}else c.group.rotation.z*=.8;}if(before!==this.state)game.qaRecord('v8-npc-state',{party:this.id,from:before,to:this.state,regular:this.v8?.regular,trait:this.v8?.traits});};
}
const baseSpawnParty=game.spawnParty.bind(game);game.spawnParty=function spawnPartyV8(){const before=new Set(this.parties);baseSpawnParty();for(const p of this.parties)if(!before.has(p)){decorateParty(p);const factor=this.config.humanCount===1?1.32:this.config.humanCount===2?1.12:1;p.patience*=factor;p.patienceMax*=factor;}};

function resetShift(){game.v8Shift={served:0,fast:0,burns:0,interactions:0,washed:0,bonusPaid:false,cleanBonusPaid:false};game.business.loyalty=Number(game.business.loyalty)||0;game.business.chefXP=Number(game.business.chefXP)||0;initStock();game.v8PinnedRecipe=game.config.menu?.[0]||'salad';}
game.v8Shift={served:0,fast:0,burns:0,interactions:0,washed:0,bonusPaid:false,cleanBonusPaid:false};

const baseCompleteTable=game.completeTable.bind(game);game.completeTable=function completeTableV8(party,server,tip){const fast=party.waitElapsed<=30;baseCompleteTable(party,server,tip);this.v8Shift.served++;if(fast)this.v8Shift.fast++;this.business.chefXP=(Number(this.business.chefXP)||0)+10+(fast?5:0);if(fast)this.business.loyalty=clamp((Number(this.business.loyalty)||0)+2,0,100);if(party.v8){party.v8.servedFast=fast;if(party.v8.regular){const bonus=fast?16:8;this.business.cash+=bonus;this.flash(`Regular guest bonus +$${bonus} • loyalty ${Math.round(this.business.loyalty)}%`);}}this.saveBusiness();checkShiftGoals();};

const baseUpdateStations=game.updateStations.bind(game);game.updateStations=function updateStationsV8(dt){const before=new Map(this.stations.map(s=>[s,s.slot?.burnt||false]));baseUpdateStations(dt);for(const s of this.stations){if(s.slot&&!before.get(s)&&s.slot.burnt){this.v8Shift.burns++;emitParticles(s.pos,0xe34f51,10);pulseTarget(s);}if(s.slot&&['stove','fryer','oven'].includes(s.type)){const ready=s.ready,steamChance=ready?.08:.025;if(Math.random()<steamChance*dt*60)emitParticles(new THREE.Vector3(s.pos.x,1.18,s.pos.z),ready?0xeeeeee:0xf2bd3f,1);}}};

function cleanliness(){let score=100;for(const t of game.tables)score-=Math.min(24,t.dirty*9);for(const s of game.stations){if(s.type==='sink'&&s.slot?.dirty)score-=12;if(s.slot?.burnt)score-=18;}score-=game.items.filter(i=>!i.dead&&!i.airborne&&!i.onSurface&&!carriedItems().has(i)).length*2;return clamp(Math.round(score),0,100);}
function checkShiftGoals(){const clean=cleanliness();const g=game.v8Shift;if(!g.bonusPaid&&g.served>=3&&g.fast>=1&&g.burns===0){g.bonusPaid=true;game.business.cash+=45;game.business.chefXP=(Number(game.business.chefXP)||0)+20;game.saveBusiness();game.flash('SHIFT GOALS COMPLETE • +$45 • +20 chef XP');}if(!g.cleanBonusPaid&&g.served>=2&&clean>=90){g.cleanBonusPaid=true;game.business.cash+=18;game.saveBusiness();game.flash('CLEAN KITCHEN BONUS • +$18');}}

const baseEndLevel=game.endLevel.bind(game);game.endLevel=function endLevelV8(failed=false){if(this.state==='result')return;const clean=cleanliness();if(!failed&&clean>=80&&!this.v8Shift.cleanFinishPaid){this.v8Shift.cleanFinishPaid=true;this.business.cash+=25;this.business.chefXP=(Number(this.business.chefXP)||0)+10;this.saveBusiness();}baseEndLevel(failed);document.getElementById('v8-service-board')?.classList.add('hidden');document.getElementById('v8-action-card')?.classList.add('hidden');};

const baseOpenRestaurant=game.openRestaurant.bind(game);game.openRestaurant=function openRestaurantV8(){resetShift();baseOpenRestaurant();if(this.state==='playing'){document.getElementById('v8-service-board')?.classList.remove('hidden');this.flash(this.players.length===1?'SOLO SHIFT — you are alone. Take orders, cook, serve and clean everything.':'TEAM SHIFT — every active chef is human controlled.');updateServiceBoard(true);}};

const baseCloseAllScreens=game.closeAllScreens.bind(game);game.closeAllScreens=function closeAllScreensV8(){baseCloseAllScreens();document.getElementById('v8-service-board')?.classList.add('hidden');document.getElementById('v8-action-card')?.classList.add('hidden');};

function updateServiceBoard(force=false){
  const board=document.getElementById('v8-service-board');if(!board||game.state!=='playing')return;if(!force&&uiTick<.12)return;uiTick=0;const r=RECIPE_BOOK[game.v8PinnedRecipe]||RECIPE_BOOK[game.config.menu?.[0]]||RECIPE_BOOK.salad,clean=cleanliness(),g=game.v8Shift||{},xp=Math.round(Number(game.business.chefXP)||0),level=1+Math.floor(xp/100),loyalty=Math.round(Number(game.business.loyalty)||0);
  const stock=Object.entries(game.v8Stock||{}).map(([k,v])=>`<span class="${v<=2?'low':''}">${INGREDIENT[k]?.emoji||''} ${v}</span>`).join('');
  board.innerHTML=`<div class="v8-board-head"><b>${game.players.length===1?'SOLO SERVICE':'LOCAL CO-OP'} • CHEF LV.${level}</b><span>LOYALTY ${loyalty}%</span></div><div class="v8-recipe-pin"><div class="title">${r.icon} ${r.name}</div><div class="route">${r.workflow.map(([s,a])=>`${s}: ${a}`).join(' → ')}</div></div><div class="v8-meter"><div class="v8-meter-row"><span>CLEANLINESS</span><b>${clean}%</b></div><div class="v8-meter-track"><i class="v8-meter-fill" style="width:${clean}%"></i></div></div><div class="v8-goals"><div class="v8-goal ${g.served>=3?'done':''}"><span>Serve 3 tables</span><b>${g.served||0}/3</b></div><div class="v8-goal ${g.fast>=1?'done':''}"><span>Fast service</span><b>${g.fast||0}/1</b></div><div class="v8-goal ${g.burns===0?'done':''}"><span>No burned food</span><b>${g.burns||0} burns</b></div></div><div class="v8-stock">${stock}</div>`;
}

function updateActionCard(){
  const card=document.getElementById('v8-action-card');if(!card||game.state!=='playing'){card?.classList.add('hidden');return;}const p=game.players[0];if(!p){card.classList.add('hidden');return;}const target=p.selectedTarget&&validTarget(p.selectedTarget)?labelOf(p.selectedTarget):labelOf(game.nearestInteractable(p.group.position,INTERACT_RANGE));card.innerHTML=`${escapeHtml(target==='NONE'?smartHintForHeld(p):`Target: ${target}`)}<small>${escapeHtml(smartHintForHeld(p))} • Left click object = smart action • Right hold = manual work</small>`;card.classList.remove('hidden');
}

const orders=document.getElementById('orders');orders?.addEventListener('click',event=>{const card=event.target.closest('.order-card');if(!card)return;const cards=[...orders.querySelectorAll('.order-card')],index=cards.indexOf(card),active=game.parties.filter(p=>['readyToOrder','waiting'].includes(p.state)),party=active[index],recipe=party?.orders?.[0]?.recipeId;if(recipe&&RECIPE_BOOK[recipe]){game.v8PinnedRecipe=recipe;updateServiceBoard(true);game.flash(`${RECIPE_BOOK[recipe].name} pinned from Table ${party.table.id+1}.`);}});

const baseUpdateUI=game.updateUI.bind(game);game.updateUI=function updateUIV8(){baseUpdateUI();this.players.forEach((p,i)=>{const el=document.getElementById(`p${i+1}-held`);if(el){const name=this.config.avatars?.[i]?.name||`Chef ${i+1}`,held=p.held?p.held.description():'empty hands',target=p.selectedTarget&&validTarget(p.selectedTarget)?` • ${labelOf(p.selectedTarget)}`:'';el.textContent=`${name}: ${held}${target}`;}});updateServiceBoard();updateActionCard();};

const baseLoop=game.loop.bind(game);game.loop=function loopV8(ts){
  // The base loop schedules itself through this.loop(), so wrapping once lets V8
  // add presentation/management updates without introducing a second RAF loop.
  const now=performance.now();if(this.__v8LastFrame==null)this.__v8LastFrame=now;const dt=Math.min(.05,Math.max(.001,(now-this.__v8LastFrame)/1000));this.__v8LastFrame=now;uiTick+=dt;cleanlinessWarningCooldown=Math.max(0,cleanlinessWarningCooldown-dt);updateEffects(dt);animateItems();if(this.state==='playing'&&cleanliness()<35&&cleanlinessWarningCooldown<=0){cleanlinessWarningCooldown=10;this.flash('CLEANLINESS CRITICAL — clear tables and wash dirty plates before service collapses.');}return baseLoop(ts);
};

// Menu/tutorial copy updated to reflect the actual V8 behavior.
const hero=document.querySelector('#menu-screen .hero-card p');if(hero)hero.textContent='Run a complete local restaurant: take orders, collect physical ingredients, prep, cook, assemble, serve, clean, manage stock, build loyalty and grow the business. Solo means truly solo — no AI chefs.';
const controllerNote=document.querySelector('#menu-screen .controller-note');if(controllerNote)controllerNote.innerHTML='<b>Senior V8:</b> solo mode has no bots. Player 1 uses the mouse; Players 2 and 3 use dedicated keyboards controls. Character appearance is customizable before each shift.';
const baseRenderTutorial=game.renderTutorial.bind(game);game.renderTutorial=function renderTutorialV8(){baseRenderTutorial();const title=document.getElementById('tutorial-title')?.textContent;if(title==='One kitchen, one team')document.getElementById('tutorial-body').textContent='Choose 1, 2 or 3 human players. Solo mode starts with exactly one chef and no AI helpers. The solo customer flow is balanced so that one person can take every order, cook every dish, serve every table and clean the restaurant.';if(title==='Move, interact and throw'){document.getElementById('tutorial-visual').innerHTML='<div class="keys"><kbd>P1 🖱 LEFT ACTION</kbd><kbd>P1 🖱 RIGHT HOLD</kbd><kbd>P2 WASD/F/E</kbd><kbd>P3 ↑↓←→/./ENTER</kbd></div>';document.getElementById('tutorial-body').textContent='Player 1: left click a kitchen object to approach and interact automatically; right click/hold for manual work. Player 2: WASD + F/E. Player 3: arrows + Period/Enter. The action card tells you the next useful kitchen step for whatever you are carrying.';}if(title==='Food has real states')document.getElementById('tutorial-body').textContent='Every recipe has an exact physical workflow. Raw → chopped → cooked/fried/baked states matter. The recipe book now lists the correct grocery, prep, cooking, assembly and serving route for every dish.';};

renderCustomization();
refreshControlsCopy();

game.__seniorV8={
  version:V8_VERSION,
  mouse,
  recipeBook:RECIPE_BOOK,
  identifyRecipe:identifyRecipeV8,
  selectTarget,
  targetFromPointer,
  queueAction,
  cleanliness,
  ergonomicLayout,
  renderCustomization,
};

console.info('Robledo Kitchen Rush Senior V8 active: reliable dual-click P1 interaction, true solo mode, avatar personalization, recipe routes, stock, goals and dynamic NPC service.');
