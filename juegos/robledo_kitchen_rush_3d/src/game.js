import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';

const COLORS = {
  ink: 0x223038, cream: 0xfff4dc, floorA: 0xe7d6bb, floorB: 0xd8c7aa,
  red: 0xe34f51, blue: 0x4387db, yellow: 0xf2bd3f, green: 0x4d9a67,
  orange: 0xef7c38, wood: 0x9b6946, steel: 0xaab6b8, darkSteel: 0x66767a,
  wall: 0xf2e8d7, counter: 0xf7f0e5, trim: 0x41545b, water: 0x4fb7dc,
};

const RECIPES = {
  burger: {
    id: 'burger', name: 'Rush Burger', icon: '🍔',
    components: ['bun:raw', 'meat:cooked', 'tomato:chopped'],
    steps: ['Take bun, meat and tomato', 'Chop tomato', 'Cook meat on stove', 'Place everything on a clean plate'],
    color: '#e46f3d', price: 180,
  },
  salad: {
    id: 'salad', name: 'Garden Salad', icon: '🥗',
    components: ['lettuce:chopped', 'tomato:chopped'],
    steps: ['Take lettuce and tomato', 'Chop both ingredients', 'Assemble on a clean plate'],
    color: '#56a65f', price: 140,
  },
  fries: {
    id: 'fries', name: 'Golden Fries', icon: '🍟',
    components: ['potato:fried'],
    steps: ['Take a potato', 'Chop potato', 'Cook it in the fryer', 'Plate before it burns'],
    color: '#e8b23f', price: 150,
  },
  pizza: {
    id: 'pizza', name: 'Mini Pizza', icon: '🍕',
    components: ['dough:raw', 'tomato:chopped', 'cheese:raw'], baked: true,
    steps: ['Take dough, tomato and cheese', 'Chop tomato', 'Assemble on a plate', 'Bake in oven until ready'],
    color: '#d95945', price: 210,
  },
  grill: {
    id: 'grill', name: 'Grill Plate', icon: '🍗',
    components: ['meat:cooked', 'lettuce:chopped'],
    steps: ['Take meat and lettuce', 'Cook meat on stove', 'Chop lettuce', 'Assemble on a clean plate'],
    color: '#8b563e', price: 200,
  },
  toast: {
    id: 'toast', name: 'Cheesy Toast', icon: '🥪',
    components: ['bun:raw', 'cheese:raw'], baked: true,
    steps: ['Take bun and cheese', 'Assemble on a plate', 'Bake until golden'],
    color: '#e2a037', price: 165,
  },
};

const INGREDIENT_META = {
  tomato: { name: 'Tomato', emoji: '🍅', choppable: true },
  lettuce: { name: 'Lettuce', emoji: '🥬', choppable: true },
  meat: { name: 'Meat', emoji: '🥩', cook: 'stove' },
  potato: { name: 'Potato', emoji: '🥔', choppable: true, cook: 'fryer' },
  dough: { name: 'Dough', emoji: '🫓' },
  cheese: { name: 'Cheese', emoji: '🧀' },
  bun: { name: 'Bun', emoji: '🥯' },
};

const LEVELS = [
  { id: 0, name: 'Bistro Basics', duration: 180, spawnEvery: 17, patience: 65, seats: 4, recipes: ['burger', 'salad', 'fries'], thresholds: [800, 1450, 2200], tint: 0xb9d8c5 },
  { id: 1, name: 'Split Service', duration: 210, spawnEvery: 14, patience: 58, seats: 5, recipes: ['burger', 'salad', 'fries', 'toast'], thresholds: [1100, 1900, 2900], tint: 0xc9d6e8 },
  { id: 2, name: 'Dinner Rush', duration: 240, spawnEvery: 11, patience: 52, seats: 6, recipes: ['burger', 'salad', 'fries', 'pizza', 'grill', 'toast'], thresholds: [1500, 2600, 3900], tint: 0xe5c9bd },
];

const GEOMETRY_QUESTIONS = [
  { q: 'A rectangle measures 8 m by 5 m. What is its area?', a: ['13 m²', '26 m²', '40 m²', '80 m²'], c: 2 },
  { q: 'A square has side length 6 cm. What is its perimeter?', a: ['12 cm', '24 cm', '36 cm', '18 cm'], c: 1 },
  { q: 'A triangle has base 10 cm and height 7 cm. What is its area?', a: ['17 cm²', '35 cm²', '70 cm²', '140 cm²'], c: 1 },
  { q: 'A circle has radius 4 cm. Which expression gives its area?', a: ['4π', '8π', '16π', '32π'], c: 2 },
  { q: 'A trapezoid has bases 6 cm and 10 cm and height 4 cm. Its area is…', a: ['16 cm²', '24 cm²', '32 cm²', '64 cm²'], c: 2 },
];

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const dist2 = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
const signature = (item) => `${item.kind}:${item.state}`;
const fmtTime = (s) => `${String(Math.max(0, Math.floor(s / 60))).padStart(2, '0')}:${String(Math.max(0, Math.floor(s % 60))).padStart(2, '0')}`;

class Sfx {
  constructor() { this.ctx = null; }
  tone(freq = 440, dur = .07, type = 'sine', gain = .045) {
    try {
      if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = this.ctx.createOscillator(); const g = this.ctx.createGain();
      o.type = type; o.frequency.value = freq; g.gain.value = gain;
      o.connect(g); g.connect(this.ctx.destination); o.start();
      g.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + dur);
      o.stop(this.ctx.currentTime + dur);
    } catch (_) {}
  }
  pickup() { this.tone(520, .06, 'triangle'); }
  chop() { this.tone(200, .035, 'square', .028); }
  cook() { this.tone(360, .05, 'sine', .025); }
  serve() { this.tone(620, .08, 'triangle'); setTimeout(() => this.tone(820, .1, 'triangle'), 70); }
  bad() { this.tone(130, .16, 'sawtooth', .04); }
  order() { this.tone(760, .05, 'square', .025); setTimeout(() => this.tone(920, .06, 'square', .025), 55); }
}

class InputManager {
  constructor() {
    this.keys = new Set();
    this.prevKeys = new Set();
    this.layouts = [
      { up: 'KeyW', down: 'KeyS', left: 'KeyA', right: 'KeyD', interact: 'KeyE', throw: 'KeyQ', dash: 'ShiftLeft' },
      { up: 'ArrowUp', down: 'ArrowDown', left: 'ArrowLeft', right: 'ArrowRight', interact: 'Enter', throw: 'Slash', dash: 'ShiftRight' },
      { up: 'KeyI', down: 'KeyK', left: 'KeyJ', right: 'KeyL', interact: 'KeyO', throw: 'KeyU', dash: 'KeyP' },
    ];
    window.addEventListener('keydown', e => { this.keys.add(e.code); if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault(); });
    window.addEventListener('keyup', e => this.keys.delete(e.code));
  }
  pollGamepad(index) {
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    const p = pads[index]; if (!p) return null;
    const dz = .22; const ax = Math.abs(p.axes[0] || 0) > dz ? p.axes[0] : 0; const ay = Math.abs(p.axes[1] || 0) > dz ? p.axes[1] : 0;
    return { x: ax, y: ay, interact: !!p.buttons[0]?.pressed, throw: !!p.buttons[2]?.pressed, dash: !!p.buttons[1]?.pressed };
  }
  state(i) {
    const l = this.layouts[i]; const gp = this.pollGamepad(i);
    let x = (this.keys.has(l.right) ? 1 : 0) - (this.keys.has(l.left) ? 1 : 0);
    let y = (this.keys.has(l.down) ? 1 : 0) - (this.keys.has(l.up) ? 1 : 0);
    if (gp && (Math.abs(gp.x) + Math.abs(gp.y) > .05)) { x = gp.x; y = gp.y; }
    const interact = this.keys.has(l.interact) || !!gp?.interact;
    const throwBtn = this.keys.has(l.throw) || !!gp?.throw;
    const dash = this.keys.has(l.dash) || !!gp?.dash;
    return { x, y, interact, throw: throwBtn, dash };
  }
  endFrame() { this.prevKeys = new Set(this.keys); }
}

function mat(color, rough = .82, metal = 0) {
  return new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal });
}
function mesh(geo, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, material); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; return m;
}
function rounded(w, h, d, r = .12, s = 3) { return new RoundedBoxGeometry(w, h, d, s, r); }

function makeLabel(text, bg = '#27343b', fg = '#fff') {
  const c = document.createElement('canvas'); c.width = 320; c.height = 86; const x = c.getContext('2d');
  x.fillStyle = bg; x.beginPath(); x.roundRect(5, 5, 310, 76, 18); x.fill();
  x.fillStyle = fg; x.font = '900 30px system-ui'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(text, 160, 43);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true })); sp.scale.set(2.3, .62, 1); return sp;
}

class AssetFactory {
  constructor() {
    this.skin = [0xf2bd95, 0xd99a73, 0x9a624a, 0xe7ae84, 0x7a4934];
  }
  chef(color) {
    const g = new THREE.Group();
    const body = mesh(rounded(.58,.78,.38,.17), mat(color), 0,.82,0); g.add(body);
    const apron = mesh(rounded(.4,.48,.04,.06), mat(0xf9f5ec), 0,.83,.215); g.add(apron);
    const head = mesh(new THREE.SphereGeometry(.27,18,14), mat(0xe0a77f), 0,1.41,0); g.add(head);
    const hatBase = mesh(new THREE.CylinderGeometry(.3,.3,.16,20), mat(0xffffff), 0,1.66,0); g.add(hatBase);
    const hatTop = mesh(new THREE.SphereGeometry(.28,16,10), mat(0xffffff), 0,1.79,0); hatTop.scale.y=.65; g.add(hatTop);
    const eyeMat = new THREE.MeshBasicMaterial({color:0x1e2529});
    for (const x of [-.09,.09]) g.add(mesh(new THREE.SphereGeometry(.025,8,8), eyeMat,x,1.44,.252));
    const armMat = mat(0xe0a77f); const legMat = mat(0x27343a);
    const leftArm = mesh(new THREE.CapsuleGeometry(.085,.34,5,8), armMat,-.39,.9,0); const rightArm=leftArm.clone(); rightArm.position.x=.39; g.add(leftArm,rightArm);
    const leftLeg = mesh(new THREE.CapsuleGeometry(.09,.35,5,8), legMat,-.17,.3,0); const rightLeg=leftLeg.clone(); rightLeg.position.x=.17; g.add(leftLeg,rightLeg);
    g.userData.limbs = { leftArm, rightArm, leftLeg, rightLeg }; return g;
  }
  customer(index = 0) {
    const palette = [0x7a4f9e,0x3d8b75,0xc6604b,0x4d70ae,0xc4922c,0x6f7681];
    const g = new THREE.Group(); const skin = this.skin[index % this.skin.length];
    const body = mesh(rounded(.5,.72,.34,.15), mat(palette[index%palette.length]),0,.72,0); g.add(body);
    const head = mesh(new THREE.SphereGeometry(.25,16,12),mat(skin),0,1.27,0);g.add(head);
    const hair = mesh(new THREE.SphereGeometry(.255,14,10),mat([0x2e211d,0x553620,0x17191b,0x76543c][index%4]),0,1.36,-.03); hair.scale.y=.65; g.add(hair);
    const eyeMat = new THREE.MeshBasicMaterial({color:0x20272a});
    for (const x of [-.08,.08]) g.add(mesh(new THREE.SphereGeometry(.02,6,6),eyeMat,x,1.29,.235));
    const legMat=mat(0x2f3941); const l=mesh(new THREE.CapsuleGeometry(.07,.28,4,7),legMat,-.14,.22,0); const r=l.clone();r.position.x=.14;g.add(l,r); return g;
  }
  ingredient(kind, state='raw') {
    const g = new THREE.Group(); let m;
    if (kind==='tomato') m=mesh(new THREE.SphereGeometry(.18,16,12),mat(state==='burnt'?0x2b211d:state==='chopped'?0xf05b4f:0xe4433e),0,.18,0);
    if (kind==='lettuce') { m=new THREE.Group(); for(let i=0;i<5;i++){const p=mesh(new THREE.SphereGeometry(.13,10,8),mat(state==='burnt'?0x283028:0x58a85d),(i%2-.5)*.15,.13+Math.floor(i/2)*.04,(i%3-1)*.09);p.scale.y=.75;m.add(p);} }
    if (kind==='meat') { m=mesh(new THREE.CylinderGeometry(.18,.18,.09,18),mat(state==='burnt'?0x1f1714:state==='cooked'?0x6b3d2c:0xb65a54),0,.09,0); }
    if (kind==='potato') { m=mesh(new THREE.SphereGeometry(.16,14,10),mat(state==='burnt'?0x2c2215:state==='fried'?0xe8b13d:state==='chopped'?0xd7ac67:0xb98850),0,.15,0); m.scale.set(1.2,.8,.9); }
    if (kind==='dough') { m=mesh(new THREE.CylinderGeometry(.2,.2,.06,20),mat(0xe5c596),0,.07,0); }
    if (kind==='cheese') { m=mesh(rounded(.28,.08,.22,.03),mat(0xf1c83a),0,.09,0); }
    if (kind==='bun') { m=mesh(new THREE.SphereGeometry(.2,16,10),mat(0xd89a4b),0,.14,0); m.scale.y=.58; }
    g.add(m); return g;
  }
  plate(dirty=false) {
    const g=new THREE.Group(); const p=mesh(new THREE.CylinderGeometry(.32,.36,.055,28),mat(dirty?0xaea391:0xf9f8ef,.45),0,.05,0);g.add(p);
    if(dirty){for(let i=0;i<3;i++)g.add(mesh(new THREE.SphereGeometry(.04,8,6),mat(0x7a4d34),-.12+i*.11,.1,(i%2)*.09-.04));} return g;
  }
  station(type, accent = COLORS.orange) {
    const g=new THREE.Group(); const base=mesh(rounded(1.25,.82,1.05,.12),mat(COLORS.counter),0,.41,0);g.add(base);
    const edge=mesh(rounded(1.32,.12,1.12,.04),mat(COLORS.trim),0,.86,0);g.add(edge);
    if(type==='prep'){g.add(mesh(rounded(.78,.06,.54,.04),mat(0xc79262),0,.95,0)); const knife=mesh(rounded(.48,.035,.07,.02),mat(0x9ca8aa,.25,.6),0,.99,.02);knife.rotation.y=.35;g.add(knife);}
    if(type==='stove'){for(const x of[-.3,.3]){const ring=mesh(new THREE.TorusGeometry(.2,.035,8,20),mat(0x20282b,.3,.8),x,.95,0);ring.rotation.x=Math.PI/2;g.add(ring);} }
    if(type==='fryer'){const bin=mesh(rounded(.72,.23,.52,.05),mat(0x6f7c80,.25,.7),0,.98,0);g.add(bin);const oil=mesh(rounded(.58,.03,.38,.02),mat(0xd5a236,.5),0,1.105,0);g.add(oil);}
    if(type==='oven'){const oven=mesh(rounded(.86,.62,.12,.07),mat(0x3f4d52,.35,.45),0,.48,.55);g.add(oven);const glass=mesh(rounded(.62,.35,.03,.04),mat(0x23343d,.2,.5),0,.5,.63);g.add(glass);}
    if(type==='sink'){const basin=mesh(rounded(.72,.18,.55,.06),mat(0x8fa3a7,.25,.7),0,.95,0);g.add(basin);const water=mesh(rounded(.6,.025,.43,.02),mat(COLORS.water,.25),0,1.04,0);g.add(water);}
    if(type==='plate'){for(let i=0;i<4;i++){const p=this.plate(false);p.position.set(0,.92+i*.045,0);p.scale.set(.75,.75,.75);g.add(p);} }
    if(type==='trash'){const lid=mesh(new THREE.CylinderGeometry(.35,.35,.09,20),mat(0x4a5a5d),0,.98,0);g.add(lid);}
    const stripe=mesh(rounded(1.0,.08,.05,.03),mat(accent),0,.55,.555);g.add(stripe); return g;
  }
  crate(kind) {
    const g=new THREE.Group();const box=mesh(rounded(.86,.58,.8,.08),mat(0x9a6a41),0,.3,0);g.add(box);const slat=mat(0xc18b54);for(const z of[-.28,.28])g.add(mesh(rounded(.9,.07,.07,.02),slat,0,.45,z));
    const item=this.ingredient(kind);item.position.set(0,.64,0);item.scale.set(1.15,1.15,1.15);g.add(item);return g;
  }
  counter() { const g=new THREE.Group();g.add(mesh(rounded(1.25,.82,1.05,.12),mat(COLORS.counter),0,.41,0));g.add(mesh(rounded(1.32,.12,1.12,.04),mat(COLORS.trim),0,.86,0));return g; }
  table(index) {
    const g=new THREE.Group(); const top=mesh(new THREE.CylinderGeometry(.72,.72,.12,28),mat(COLORS.wood),0,.73,0);g.add(top);g.add(mesh(new THREE.CylinderGeometry(.12,.16,.65,16),mat(0x6b5749),0,.36,0));
    const chairMat=mat(0x617b72);
    for(const a of [0,Math.PI/2,Math.PI,Math.PI*1.5]){
      const c=new THREE.Group();
      c.add(mesh(rounded(.52,.12,.48,.05),chairMat,0,.42,0));
      const back=mesh(rounded(.52,.55,.1,.05),chairMat,0,.72,-.2);c.add(back);
      c.position.set(Math.sin(a)*1.0,0,Math.cos(a)*1.0);c.rotation.y=a;g.add(c);
    }
    const label=makeLabel(`TABLE ${index+1}`,'#fff7e8','#26343a');label.position.set(0,1.55,0);label.scale.multiplyScalar(.62);g.add(label);return g;
  }
}

class WorldItem {
  constructor(game, kind, state='raw', isPlate=false) {
    this.game=game; this.kind=kind; this.state=state; this.isPlate=isPlate; this.components=[]; this.baked=false; this.dirty=false; this.group=isPlate?game.assets.plate(false):game.assets.ingredient(kind,state);
    this.group.userData.item=this; this.velocity=new THREE.Vector3(); this.airborne=false; this.onSurface=false; this.dead=false; game.itemRoot.add(this.group);
  }
  description() {
    if(this.isPlate){if(this.dirty)return 'dirty plate';const r=identifyRecipe(this);return r?RECIPES[r].name:`plate${this.components.length?' + '+this.components.map(c=>INGREDIENT_META[c.kind]?.name||c.kind).join(', '):''}`;}
    return `${this.state==='raw'?'':this.state+' '}${INGREDIENT_META[this.kind]?.name||this.kind}`.trim();
  }
  setState(s){this.state=s;if(!this.isPlate){this.group.remove(...this.group.children);const n=this.game.assets.ingredient(this.kind,s);while(n.children.length)this.group.add(n.children[0]);}}
  dispose(){this.dead=true;this.group.removeFromParent();}
}

function identifyRecipe(plate) {
  if(!plate?.isPlate || plate.dirty) return null;
  const sigs=plate.components.map(signature).sort();
  for(const r of Object.values(RECIPES)){
    const req=[...r.components].sort(); if(req.length!==sigs.length)continue;
    if(req.every((v,i)=>v===sigs[i]) && (!!r.baked===!!plate.baked))return r.id;
  }
  return null;
}

class Player {
  constructor(game,index,color,start) {
    this.game=game;this.index=index;this.group=game.assets.chef(color);this.group.position.copy(start);game.playerRoot.add(this.group);this.held=null;this.radius=.38;this.speed=4.3;this.facing=new THREE.Vector3(0,0,1);this.prevInteract=false;this.prevThrow=false;this.dashCooldown=0;this.walkPhase=0;
  }
  pick(item){if(this.held||!item)return false;this.held=item;item.onSurface=false;this.game.sfx.pickup();return true;}
  dropAt(pos){if(!this.held)return;const i=this.held;this.held=null;i.group.position.copy(pos);i.group.position.y=.18;i.onSurface=false;}
  throwItem(){if(!this.held)return;const i=this.held;this.held=null;i.airborne=true;i.onSurface=false;i.group.position.copy(this.group.position).add(new THREE.Vector3(0,1.05,0));i.velocity.copy(this.facing).multiplyScalar(5.5);i.velocity.y=3.2;this.game.sfx.pickup();}
  update(dt,input){
    this.dashCooldown=Math.max(0,this.dashCooldown-dt);let dx=input.x,dz=input.y;const len=Math.hypot(dx,dz);if(len>.001){dx/=Math.max(1,len);dz/=Math.max(1,len);this.facing.set(dx,0,dz);this.group.rotation.y=Math.atan2(dx,dz);}
    let boost=input.dash&&this.dashCooldown<=0?1.72:1;if(boost>1)this.dashCooldown=.18;
    const move=new THREE.Vector3(dx,0,dz).multiplyScalar(this.speed*boost*dt);this.game.movePlayer(this,move);
    if(len>.05){this.walkPhase+=dt*10*boost;const l=this.group.userData.limbs;if(l){l.leftArm.rotation.x=Math.sin(this.walkPhase)*.6;l.rightArm.rotation.x=-Math.sin(this.walkPhase)*.6;l.leftLeg.rotation.x=-Math.sin(this.walkPhase)*.35;l.rightLeg.rotation.x=Math.sin(this.walkPhase)*.35;}this.group.position.y=.02+Math.abs(Math.sin(this.walkPhase*2))*.025;}else{const l=this.group.userData.limbs;if(l){for(const p of Object.values(l))p.rotation.x*=.72;}this.group.position.y=0;}
    if(this.held){this.held.group.position.copy(this.group.position).add(new THREE.Vector3(this.facing.x*.18,1.1,this.facing.z*.18));this.held.group.rotation.y=this.group.rotation.y;}
    if(input.throw&&!this.prevThrow)this.throwItem();this.prevThrow=input.throw;
    const nearest=this.game.nearestInteractable(this.group.position,1.25);if(input.interact&&nearest)this.game.interact(this,nearest,dt,true);this.prevInteract=input.interact;
  }
}

class CustomerParty {
  constructor(game, table, size, recipes, patience) {
    this.game=game;this.table=table;this.size=size;this.orders=Array.from({length:size},()=>recipes[Math.floor(Math.random()*recipes.length)]);this.patienceMax=patience+Math.random()*12;this.patience=this.patienceMax;this.state='entering';this.browse=2.2+Math.random()*2;this.eat=0;this.customers=[];
    const door=new THREE.Vector3(9.5,0,-7.6);for(let i=0;i<size;i++){const c=game.assets.customer((game.customerSerial+i)%6);c.position.copy(door).add(new THREE.Vector3(i*.22,0,i*.18));game.customerRoot.add(c);this.customers.push({group:c,target:table.seats[i].clone(),speed:2.0+Math.random()*.45});}game.customerSerial+=size;
  }
  update(dt){
    if(this.state==='entering'){let arrived=true;for(const c of this.customers){const v=c.target.clone().sub(c.group.position);v.y=0;if(v.length()>.08){arrived=false;v.normalize();c.group.position.addScaledVector(v,c.speed*dt);c.group.rotation.y=Math.atan2(v.x,v.z);}else{c.group.position.copy(c.target);c.group.position.y=-.08;c.group.rotation.y=Math.atan2(this.table.pos.x-c.group.position.x,this.table.pos.z-c.group.position.z);}}
      if(arrived){this.state='browsing';}
    } else if(this.state==='browsing'){this.browse-=dt;if(this.browse<=0){this.state='waiting';this.game.sfx.order();this.game.flash(`Table ${this.table.id+1} placed an order!`);}}
    else if(this.state==='waiting'){this.patience-=dt;if(this.patience<=0){this.game.walkout(this);}}
    else if(this.state==='eating'){this.eat-=dt;if(this.eat<=0)this.beginLeaving();}
    else if(this.state==='leaving'){let done=true;const exit=new THREE.Vector3(10.5,0,-8);for(const c of this.customers){const v=exit.clone().sub(c.group.position);v.y=0;if(v.length()>.2){done=false;v.normalize();c.group.position.addScaledVector(v,c.speed*dt);c.group.rotation.y=Math.atan2(v.x,v.z);}}
      if(done){for(const c of this.customers)c.group.removeFromParent();this.table.party=null;this.table.dirty=Math.max(1,this.size);this.state='gone';}
    }
  }
  serve(recipeId){const idx=this.orders.indexOf(recipeId);if(idx<0)return false;this.orders.splice(idx,1);if(this.orders.length===0){const urgency=this.patience/this.patienceMax;const tip=Math.round(80+150*urgency*this.game.combo);this.game.score+=tip;this.game.combo=Math.min(8,this.game.combo+1);this.state='eating';this.eat=6+Math.random()*3;this.game.sfx.serve();this.game.flash(`Table ${this.table.id+1} complete! +${tip}`);this.game.onSuccessfulTable();}else{this.game.score+=Math.round(RECIPES[recipeId].price*.35);this.game.sfx.serve();this.game.flash(`${RECIPES[recipeId].name} served to Table ${this.table.id+1}`);}return true;}
  beginLeaving(){this.state='leaving';}
  forceLeave(){this.state='leaving';}
}

class Game {
  constructor(){
    this.canvas=document.getElementById('game-canvas');this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:true,alpha:false,powerPreference:'high-performance'});this.renderer.setPixelRatio(Math.min(2,devicePixelRatio));this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.12;
    this.scene=new THREE.Scene();this.scene.background=new THREE.Color(0xb7cfca);this.scene.fog=new THREE.Fog(0xb7cfca,23,42);this.camera=new THREE.OrthographicCamera(-10,10,7,-7,.1,100);this.camera.position.set(16,18,18);this.camera.lookAt(0,0,0);
    this.assets=new AssetFactory();this.input=new InputManager();this.sfx=new Sfx();this.playerRoot=new THREE.Group();this.itemRoot=new THREE.Group();this.customerRoot=new THREE.Group();this.worldRoot=new THREE.Group();this.scene.add(this.worldRoot,this.itemRoot,this.customerRoot,this.playerRoot);
    this.players=[];this.stations=[];this.obstacles=[];this.tables=[];this.items=[];this.parties=[];this.activeMenu=[];this.state='menu';this.levelIndex=0;this.score=0;this.combo=1;this.lives=3;this.timeLeft=0;this.spawnTimer=0;this.customerSerial=0;this.lastTs=performance.now();this.messageTimer=0;this.geometryPendingLife=false;this.progress=JSON.parse(localStorage.getItem('robledo_kitchen_rush_progress')||'{"stars":[0,0,0]}');
    this.bindUI();this.buildRecipeUI();this.buildLevelButtons();this.buildLights();this.buildDecorativeWorld();window.addEventListener('resize',()=>this.resize());this.resize();requestAnimationFrame(t=>this.loop(t));
  }
  bindUI(){
    this.ui={menu:document.getElementById('menu-screen'),recipes:document.getElementById('recipe-screen'),controls:document.getElementById('controls-screen'),pause:document.getElementById('pause-screen'),result:document.getElementById('result-screen'),geometry:document.getElementById('geometry-screen'),hud:document.getElementById('hud'),orders:document.getElementById('orders'),playerHud:document.getElementById('player-hud'),timer:document.getElementById('timer'),score:document.getElementById('score'),combo:document.getElementById('combo'),lives:document.getElementById('lives'),message:document.getElementById('message'),hint:document.getElementById('interaction-hint'),levelName:document.getElementById('level-name')};
    document.getElementById('start-btn').onclick=()=>this.startLevel(this.levelIndex);document.getElementById('recipes-btn').onclick=()=>this.showOverlay('recipes');document.getElementById('controls-btn').onclick=()=>this.showOverlay('controls');document.querySelectorAll('.close-overlay').forEach(b=>b.onclick=()=>this.closeSoftOverlay());document.getElementById('resume-btn').onclick=()=>this.resume();document.getElementById('restart-btn').onclick=()=>this.startLevel(this.levelIndex);document.getElementById('quit-btn').onclick=()=>this.toMenu();document.getElementById('replay-btn').onclick=()=>this.startLevel(this.levelIndex);document.getElementById('result-menu-btn').onclick=()=>this.toMenu();document.getElementById('next-btn').onclick=()=>this.startLevel(Math.min(LEVELS.length-1,this.levelIndex+1));
    window.addEventListener('keydown',e=>{if(e.code==='Escape'){if(!this.ui.recipes.classList.contains('hidden')||!this.ui.controls.classList.contains('hidden'))this.closeSoftOverlay();else if(this.state==='playing')this.pause();else if(this.state==='paused')this.resume();}if(e.code==='KeyM'&&this.state==='playing')this.showOverlay('recipes');});
  }
  buildRecipeUI(){document.getElementById('recipe-grid').innerHTML=Object.values(RECIPES).map(r=>`<article class="recipe-card"><div class="recipe-icon">${r.icon}</div><h3>${r.name}</h3><div class="ingredients">${r.components.map(s=>{const [k,st]=s.split(':');return `${INGREDIENT_META[k]?.emoji||''} ${st==='raw'?'':st+' '}${INGREDIENT_META[k]?.name||k}`}).join(' + ')}</div><ul>${r.steps.map(s=>`<li>${s}</li>`).join('')}</ul></article>`).join('');}
  buildLevelButtons(){const row=document.getElementById('level-row');row.innerHTML='';LEVELS.forEach((l,i)=>{const unlocked=i===0||(this.progress.stars[i-1]||0)>0;const b=document.createElement('button');b.className=`level-btn ${i===this.levelIndex?'selected':''} ${unlocked?'':'locked'}`;b.innerHTML=`${i+1}. ${l.name} ${'★'.repeat(this.progress.stars[i]||0)}`;b.disabled=!unlocked;b.onclick=()=>{this.levelIndex=i;this.buildLevelButtons();};row.appendChild(b);});}
  buildLights(){const hemi=new THREE.HemisphereLight(0xfff7e0,0x4a6871,2.2);this.scene.add(hemi);const sun=new THREE.DirectionalLight(0xfff0cf,4.3);sun.position.set(-9,18,10);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-18;sun.shadow.camera.right=18;sun.shadow.camera.top=18;sun.shadow.camera.bottom=-18;this.scene.add(sun);}
  buildDecorativeWorld(){const floor=mesh(rounded(25,.25,20,.12),mat(0xcfd7d0),0,-.2,0);floor.receiveShadow=true;this.worldRoot.add(floor);for(let x=-12;x<=12;x+=2)for(let z=-9;z<=9;z+=2){const tile=mesh(rounded(1.92,.04,1.92,.04),mat(((x+z)/2)%2===0?COLORS.floorA:COLORS.floorB),x,-.04,z);tile.receiveShadow=true;tile.castShadow=false;this.worldRoot.add(tile);}const wallMat=mat(COLORS.wall);for(const cfg of [[0,1.4,-9.7,25,.2],[ -12.4,1.4,0,.2,19.5],[12.4,1.4,3,.2,13]]){const w=mesh(rounded(cfg[3],2.8,cfg[4],.04),wallMat,cfg[0],cfg[1],cfg[2]);this.worldRoot.add(w);}const sign=makeLabel('ROBLEDO BISTRO','#ef7c38','#fff');sign.position.set(0,2.2,-9.45);sign.scale.set(4.4,1.18,1);this.worldRoot.add(sign);}
  clearGameplay(){for(const r of [this.playerRoot,this.itemRoot,this.customerRoot]){while(r.children.length)r.remove(r.children[0]);}this.stations=[];this.obstacles=[];this.tables=[];this.items=[];this.parties=[];}
  startLevel(index){
    this.levelIndex=index;const L=LEVELS[index];this.closeAllScreens();this.clearGameplay();this.state='playing';this.score=0;this.combo=1;this.lives=3;this.timeLeft=L.duration;this.spawnTimer=2.5;this.activeMenu=[...L.recipes];this.ui.hud.classList.remove('hidden');this.ui.orders.classList.remove('hidden');this.ui.playerHud.classList.remove('hidden');this.ui.levelName.textContent=L.name;this.scene.background.setHex(L.tint);this.scene.fog.color.setHex(L.tint);this.buildKitchen(index);this.spawnPlayers();this.updateUI();this.flash('SHIFT START! Three chefs, one kitchen.');
  }
  buildKitchen(level){
    const addObstacle=(x,z,w,d)=>this.obstacles.push({x,z,w,d});
    const station=(type,x,z,opts={})=>{const s={type,x,z,pos:new THREE.Vector3(x,0,z),slot:null,progress:0,cook:0,burn:0,kind:opts.kind||null,label:opts.label||type};s.group=opts.kind?this.assets.crate(opts.kind):this.assets.station(type,opts.accent||COLORS.orange);s.group.position.set(x,0,z);const lab=makeLabel(opts.label||type.toUpperCase(),opts.color||'#33454c');lab.position.set(0,1.52,0);lab.scale.multiplyScalar(.58);s.group.add(lab);
      if(['prep','stove','fryer','oven','sink'].includes(type)){const bg=mesh(rounded(.82,.075,.055,.02),mat(0x243139),0,1.22,.5);bg.castShadow=false;const fill=mesh(rounded(.76,.055,.06,.015),mat(type==='sink'?0x4fb7dc:type==='prep'?0xe4aa54:0x69b36f),-.38,1.22,.535);fill.geometry.translate(.38,0,0);fill.scale.x=.001;fill.castShadow=false;s.group.add(bg,fill);s.bar=fill;}
      this.worldRoot.add(s.group);this.stations.push(s);addObstacle(x,z,1.15,.95);return s;};
    const counter=(x,z)=>{const s={type:'counter',x,z,pos:new THREE.Vector3(x,0,z),slot:null,progress:0};s.group=this.assets.counter();s.group.position.set(x,0,z);this.worldRoot.add(s.group);this.stations.push(s);addObstacle(x,z,1.15,.95);};
    // clear prior dynamic world meshes except floor/walls/sign by tagged list
    if(this.dynamicRoot)this.dynamicRoot.removeFromParent();this.dynamicRoot=new THREE.Group();this.worldRoot.add(this.dynamicRoot);
    const oldAdd=this.worldRoot.add.bind(this.worldRoot);this.worldRoot.add=(...o)=>{this.dynamicRoot.add(...o);return this.worldRoot;};
    // Kitchen block
    station('plate',-8,-5,{label:'PLATES',color:'#4a7882'});station('sink',-6.4,-5,{label:'SINK',color:'#4aa5bc'});station('trash',-4.8,-5,{label:'TRASH',color:'#545e62'});
    station('crate',-8,-2.8,{kind:'tomato',label:'TOMATO',color:'#d84a43'});station('crate',-6.4,-2.8,{kind:'lettuce',label:'LETTUCE',color:'#4f9f58'});station('crate',-4.8,-2.8,{kind:'meat',label:'MEAT',color:'#9d5146'});station('crate',-3.2,-2.8,{kind:'potato',label:'POTATO',color:'#b08755'});station('crate',-1.6,-2.8,{kind:'bun',label:'BUN',color:'#c98e48'});station('crate',0,-2.8,{kind:'cheese',label:'CHEESE',color:'#d8ad2b'});station('crate',1.6,-2.8,{kind:'dough',label:'DOUGH',color:'#c5a36f'});
    station('prep',-6.5,-.4,{label:'CHOP',color:'#c67a45'});station('prep',-4.9,-.4,{label:'CHOP',color:'#c67a45'});station('stove',-2.7,-.4,{label:'STOVE',color:'#cc5f46'});station('fryer',-.9,-.4,{label:'FRYER',color:'#d7a839'});station('oven',.9,-.4,{label:'OVEN',color:'#b54e3f'});counter(3,-.4);counter(4.6,-.4);
    if(level>0){counter(3,-2.8);counter(4.6,-2.8);} if(level===2){counter(-2.7,1.5);counter(-.9,1.5);}
    // Dining room tables
    const tablePositions=[[-7,4],[-3.8,4],[0,4],[3.8,4],[7,4],[-5.5,7],[0,7],[5.5,7]];for(let i=0;i<LEVELS[level].seats;i++){const [x,z]=tablePositions[i];const t={id:i,pos:new THREE.Vector3(x,0,z),party:null,dirty:0,group:this.assets.table(i),seats:[]};t.group.position.set(x,0,z);this.worldRoot.add(t.group);for(const a of [0,Math.PI/2,Math.PI,Math.PI*1.5])t.seats.push(new THREE.Vector3(x+Math.sin(a)*1.0,0,z+Math.cos(a)*1.0));this.tables.push(t);addObstacle(x,z,1.35,1.35);}
    // Service/visual divider counters
    counter(6.7,-.4);counter(8.1,-.4);const pass=this.stations[this.stations.length-1];pass.type='counter';
    this.worldRoot.add=oldAdd;
  }
  spawnPlayers(){const starts=[new THREE.Vector3(-5,0,1.8),new THREE.Vector3(-2,0,1.8),new THREE.Vector3(1,0,1.8)];this.players=[new Player(this,0,COLORS.red,starts[0]),new Player(this,1,COLORS.blue,starts[1]),new Player(this,2,COLORS.yellow,starts[2])];}
  movePlayer(p,move){const tryPos=p.group.position.clone();tryPos.x+=move.x;if(!this.blocked(p,tryPos))p.group.position.x=tryPos.x;tryPos.copy(p.group.position);tryPos.z+=move.z;if(!this.blocked(p,tryPos))p.group.position.z=tryPos.z;p.group.position.x=clamp(p.group.position.x,-10.8,10.8);p.group.position.z=clamp(p.group.position.z,-8.2,8.7);}
  blocked(p,pos){for(const o of this.obstacles){if(Math.abs(pos.x-o.x)<o.w/2+p.radius&&Math.abs(pos.z-o.z)<o.d/2+p.radius)return true;}for(const q of this.players){if(q!==p&&dist2(pos,q.group.position)<p.radius+q.radius-.05)return true;}return false;}
  nearestInteractable(pos,max){let best=null,bd=max;for(const s of this.stations){const d=dist2(pos,s.pos);if(d<bd){bd=d;best=s;}}for(const t of this.tables){const d=dist2(pos,t.pos);if(d<bd){bd=d;best={type:'table',table:t,pos:t.pos};}}for(const i of this.items){if(i.dead||i.airborne||i.onSurface)continue;const d=dist2(pos,i.group.position);if(d<bd){bd=d;best={type:'loose',item:i,pos:i.group.position};}}return best;}
  interact(player,target,dt,held){
    if(target.type==='loose'){if(!player.held)player.pick(target.item);return;}
    if(target.type==='table'){this.interactTable(player,target.table);return;}
    const s=target;
    if(s.type==='crate'){if(!player.held){const i=this.newItem(s.kind);i.group.position.copy(player.group.position);player.pick(i);}return;}
    if(s.type==='plate'){if(!player.held){const i=this.newPlate(false);i.group.position.copy(player.group.position);player.pick(i);}return;}
    if(s.type==='trash'){if(player.held){player.held.dispose();player.held=null;this.sfx.bad();this.flash('Item trashed');}return;}
    if(s.type==='counter'){this.surfaceInteract(player,s);return;}
    if(s.type==='prep'){this.prepInteract(player,s,dt,held);return;}
    if(['stove','fryer','oven'].includes(s.type)){this.cookInteract(player,s);return;}
    if(s.type==='sink'){this.sinkInteract(player,s,dt,held);return;}
  }
  surfaceInteract(p,s){if(!p.held&&s.slot){p.pick(s.slot);s.slot=null;return;}if(!p.held)return;if(!s.slot){s.slot=p.held;p.held=null;s.slot.onSurface=true;s.slot.group.position.set(s.x,.94,s.z);return;}if(s.slot.isPlate&&!p.held.isPlate&&!s.slot.dirty){s.slot.components.push({kind:p.held.kind,state:p.held.state});p.held.dispose();p.held=null;this.sfx.pickup();this.refreshPlateVisual(s.slot);return;}if(p.held.isPlate&&!s.slot.isPlate&&!p.held.dirty){p.held.components.push({kind:s.slot.kind,state:s.slot.state});s.slot.dispose();s.slot=p.held;p.held=null;s.slot.onSurface=true;s.slot.group.position.set(s.x,.94,s.z);this.refreshPlateVisual(s.slot);}}
  prepInteract(p,s,dt){if(!s.slot&&p.held&&!p.held.isPlate&&INGREDIENT_META[p.held.kind]?.choppable&&p.held.state==='raw'){s.slot=p.held;p.held=null;s.slot.onSurface=true;s.slot.group.position.set(s.x,.95,s.z);s.progress=0;return;}if(!s.slot)return;if(s.slot.state!=='raw'){if(!p.held){p.pick(s.slot);s.slot=null;}return;}s.progress+=dt;this.sfx.chop();if(s.progress>=1.25){s.slot.setState('chopped');s.progress=0;this.flash(`${INGREDIENT_META[s.slot.kind].name} chopped!`);}}
  cookInteract(p,s){if(!s.slot&&p.held){if(this.canCookAt(p.held,s.type)){s.slot=p.held;p.held=null;s.slot.onSurface=true;s.slot.group.position.set(s.x,.98,s.z);s.cook=0;s.burn=0;return;}}if(s.slot&&this.isCookedForStation(s.slot,s.type)&&!p.held){p.pick(s.slot);s.slot=null;s.cook=0;s.burn=0;return;}if(s.slot&&!this.canCookAt(s.slot,s.type)&&!p.held){p.pick(s.slot);s.slot=null;}}
  canCookAt(item,type){if(item.isPlate){return type==='oven'&&!!this.preBakeRecipe(item);}if(type==='stove')return item.kind==='meat'&&item.state==='raw';if(type==='fryer')return item.kind==='potato'&&item.state==='chopped';return false;}
  isCookedForStation(item,type){if(item.isPlate)return item.baked;if(type==='stove')return item.state==='cooked'||item.state==='burnt';if(type==='fryer')return item.state==='fried'||item.state==='burnt';return false;}
  preBakeRecipe(plate){if(!plate?.isPlate||plate.baked)return null;const sigs=plate.components.map(signature).sort();for(const id of ['pizza','toast']){const r=RECIPES[id];if([...r.components].sort().join('|')===sigs.join('|'))return id;}return null;}
  sinkInteract(p,s,dt){if(!s.slot&&p.held?.isPlate&&p.held.dirty){s.slot=p.held;p.held=null;s.slot.onSurface=true;s.slot.group.position.set(s.x,.98,s.z);s.progress=0;return;}if(!s.slot)return;s.progress+=dt;if(s.progress>=1.6){s.slot.dirty=false;s.slot.components=[];s.slot.baked=false;this.refreshPlateVisual(s.slot);if(!p.held){p.pick(s.slot);s.slot=null;}s.progress=0;this.sfx.serve();this.flash('Plate washed');}}
  interactTable(p,t){if(t.dirty>0&&!p.held){const i=this.newPlate(true);i.group.position.copy(p.group.position);p.pick(i);t.dirty--;this.flash(`Dirty plate collected • ${t.dirty} left`);return;}if(!t.party||t.party.state!=='waiting'||!p.held?.isPlate)return;const r=identifyRecipe(p.held);if(!r){this.sfx.bad();this.flash('That plate does not match a finished recipe.');return;}if(t.party.serve(r)){p.held.dispose();p.held=null;}else{this.sfx.bad();this.combo=1;this.flash(`Table ${t.id+1} did not order ${RECIPES[r].name}.`);}}
  newItem(kind,state='raw'){const i=new WorldItem(this,kind,state,false);this.items.push(i);return i;}
  newPlate(dirty=false){const i=new WorldItem(this,'plate','clean',true);i.dirty=dirty;if(dirty){i.group.removeFromParent();i.group=this.assets.plate(true);this.itemRoot.add(i.group);}this.items.push(i);return i;}
  refreshPlateVisual(p){const pos=p.group.position.clone();const parent=p.group.parent;p.group.removeFromParent();p.group=this.assets.plate(p.dirty);p.group.position.copy(pos);if(parent)parent.add(p.group);for(const [idx,c] of p.components.entries()){const m=this.assets.ingredient(c.kind,c.state);m.scale.set(.55,.55,.55);m.position.set((idx%3-1)*.13,.12+Math.floor(idx/3)*.07,(idx%2-.5)*.12);p.group.add(m);}if(p.baked){const glow=mesh(new THREE.TorusGeometry(.27,.025,8,18),mat(0xe6a037),0,.12,0);glow.rotation.x=Math.PI/2;p.group.add(glow);}}
  updateStations(dt){for(const s of this.stations){
      if(s.bar){let ratio=0;if(s.type==='prep')ratio=s.slot&&s.slot.state==='raw'?s.progress/1.25:0;else if(s.type==='sink')ratio=s.slot?s.progress/1.6:0;else if(['stove','fryer','oven'].includes(s.type)){const target=s.type==='oven'?4.4:s.type==='fryer'?3.2:3.8;ratio=s.slot?Math.min(1,s.cook/target):0;}s.bar.scale.x=Math.max(.001,clamp(ratio,0,1));}
      if(!['stove','fryer','oven'].includes(s.type)||!s.slot)continue;s.cook+=dt;const target=s.type==='oven'?4.4:s.type==='fryer'?3.2:3.8;if(s.cook>=target&&s.cook<target+5){if(s.slot.isPlate&&!s.slot.baked){s.slot.baked=true;this.refreshPlateVisual(s.slot);this.sfx.cook();}else if(!s.slot.isPlate){const cooked=s.type==='fryer'?'fried':'cooked';if(s.slot.state!==cooked)s.slot.setState(cooked);} }if(s.cook>=target+7){if(s.slot.isPlate){s.slot.components=s.slot.components.map(c=>({...c,state:c.state==='raw'?c.state:'burnt'}));s.slot.baked=false;this.refreshPlateVisual(s.slot);}else if(s.slot.state!=='burnt')s.slot.setState('burnt');}}
  }
  updateItems(dt){for(const i of this.items){if(i.dead||!i.airborne)continue;i.velocity.y-=8.5*dt;i.group.position.addScaledVector(i.velocity,dt);if(i.group.position.y<=.15){i.group.position.y=.15;i.velocity.set(0,0,0);i.airborne=false;}}
    this.items=this.items.filter(i=>!i.dead);
  }
  spawnParty(){const free=this.tables.filter(t=>!t.party&&t.dirty===0);if(!free.length)return;const t=free[Math.floor(Math.random()*free.length)];const size=1+Math.floor(Math.random()*Math.min(3,t.seats.length));const p=new CustomerParty(this,t,size,this.activeMenu,LEVELS[this.levelIndex].patience);t.party=p;this.parties.push(p);}
  walkout(p){this.sfx.bad();this.combo=1;this.lives--;p.forceLeave();this.flash(`Table ${p.table.id+1} walked out! Team life lost.`);this.updateUI();if(this.lives>0)this.openGeometryRescue();else this.finishLevel(true);}
  openGeometryRescue(){this.state='geometry';const q=GEOMETRY_QUESTIONS[Math.floor(Math.random()*GEOMETRY_QUESTIONS.length)];this.currentGeometry=q;document.getElementById('geometry-question').textContent=q.q;const box=document.getElementById('geometry-options');box.innerHTML='';q.a.forEach((a,i)=>{const b=document.createElement('button');b.textContent=a;b.onclick=()=>this.answerGeometry(i,b);box.appendChild(b);});this.ui.geometry.classList.remove('hidden');}
  answerGeometry(i,b){const q=this.currentGeometry;const buttons=[...document.querySelectorAll('#geometry-options button')];buttons.forEach(x=>x.disabled=true);if(i===q.c){b.classList.add('correct');this.lives=Math.min(3,this.lives+1);this.sfx.serve();this.flash('Life restored! Back to the kitchen.');}else{b.classList.add('wrong');buttons[q.c].classList.add('correct');this.sfx.bad();}this.updateUI();setTimeout(()=>{this.ui.geometry.classList.add('hidden');if(this.lives<=0)this.finishLevel(true);else this.state='playing';},1100);}
  onSuccessfulTable(){this.updateUI();}
  updateCustomers(dt){for(const p of this.parties)if(p.state!=='gone')p.update(dt);this.parties=this.parties.filter(p=>p.state!=='gone');}
  updateOrders(){const active=this.parties.filter(p=>p.state==='waiting');this.ui.orders.innerHTML=active.slice(0,6).map(p=>{const pct=clamp(p.patience/p.patienceMax*100,0,100);return `<div class="order-card ${pct<25?'urgent':''}"><div class="top"><span>TABLE ${p.table.id+1}</span><span>${Math.ceil(p.patience)}s</span></div><div class="dishes">${p.orders.map(id=>RECIPES[id].icon).join(' ')}</div><div class="bar"><div class="fill" style="width:${pct}%"></div></div></div>`}).join('');}
  updateUI(){this.ui.timer.textContent=fmtTime(this.timeLeft);this.ui.score.textContent=Math.round(this.score);this.ui.combo.textContent=`x${this.combo}`;this.ui.lives.textContent='❤'.repeat(Math.max(0,this.lives))+'♡'.repeat(Math.max(0,3-this.lives));for(let i=0;i<3;i++){const p=this.players[i];const el=document.getElementById(`p${i+1}-held`);if(el)el.textContent=p?.held?p.held.description():'empty hands';}}
  flash(text){this.ui.message.textContent=text;this.ui.message.classList.remove('hidden');this.messageTimer=2.1;}
  nearestHint(){let best=null;for(const p of this.players){const t=this.nearestInteractable(p.group.position,1.25);if(t){best=this.hintFor(t,p);if(best)break;}}if(best){this.ui.hint.textContent=best;this.ui.hint.classList.remove('hidden');}else this.ui.hint.classList.add('hidden');}
  hintFor(t,p){if(t.type==='loose')return 'Pick up item';if(t.type==='table'){if(t.table.dirty>0&&!p.held)return 'Collect dirty plate';if(t.table.party?.state==='waiting'&&p.held?.isPlate)return `Serve Table ${t.table.id+1}`;return null;}const map={crate:'Take ingredient',plate:'Take clean plate',trash:'Trash held item',counter:'Place / pick up / assemble',prep:'Place ingredient • hold interact to chop',stove:'Cook meat',fryer:'Fry chopped potato',oven:'Bake assembled pizza/toast',sink:'Wash dirty plate'};return map[t.type];}
  updateCamera(dt){if(!this.players.length)return;const c=new THREE.Vector3();for(const p of this.players)c.add(p.group.position);c.multiplyScalar(1/this.players.length);const desired=new THREE.Vector3(c.x+14,16,c.z+16);this.camera.position.lerp(desired,1-Math.exp(-dt*2.4));this.camera.lookAt(c.x,0,c.z);}
  pause(){if(this.state!=='playing')return;this.state='paused';this.ui.pause.classList.remove('hidden');}
  resume(){if(this.state!=='paused')return;this.ui.pause.classList.add('hidden');this.state='playing';}
  showOverlay(which){if(this.state==='playing')this.state='soft';this.ui[which].classList.remove('hidden');}
  closeSoftOverlay(){this.ui.recipes.classList.add('hidden');this.ui.controls.classList.add('hidden');if(this.players.length&&this.state==='soft')this.state='playing';}
  closeAllScreens(){for(const x of ['menu','recipes','controls','pause','result','geometry'])this.ui[x].classList.add('hidden');}
  toMenu(){this.state='menu';this.clearGameplay();this.closeAllScreens();this.ui.menu.classList.remove('hidden');this.ui.hud.classList.add('hidden');this.ui.orders.classList.add('hidden');this.ui.playerHud.classList.add('hidden');this.buildLevelButtons();}
  finishLevel(failed=false){if(this.state==='result')return;this.state='result';let stars=0;const L=LEVELS[this.levelIndex];if(!failed){for(const t of L.thresholds)if(this.score>=t)stars++;}this.progress.stars[this.levelIndex]=Math.max(this.progress.stars[this.levelIndex]||0,stars);localStorage.setItem('robledo_kitchen_rush_progress',JSON.stringify(this.progress));document.getElementById('result-title').textContent=failed?'KITCHEN CLOSED':'DINNER SERVICE COMPLETE';document.getElementById('result-stars').textContent='★'.repeat(stars)+'☆'.repeat(3-stars);document.getElementById('result-stats').innerHTML=`<p><b>Score:</b> ${Math.round(this.score)}<br/><b>Best combo:</b> x${this.combo}<br/><b>Team lives:</b> ${this.lives}</p>`;const next=document.getElementById('next-btn');next.style.display=this.levelIndex<LEVELS.length-1&&stars>0?'block':'none';this.ui.result.classList.remove('hidden');}
  resize(){const w=innerWidth,h=innerHeight;this.renderer.setSize(w,h,false);const aspect=w/h;const view=12.5;this.camera.left=-view*aspect;this.camera.right=view*aspect;this.camera.top=view;this.camera.bottom=-view;this.camera.updateProjectionMatrix();}
  loop(ts){const dt=Math.min(.033,(ts-this.lastTs)/1000||0);this.lastTs=ts;if(this.state==='playing')this.update(dt);if(this.messageTimer>0){this.messageTimer-=dt;if(this.messageTimer<=0)this.ui.message.classList.add('hidden');}this.renderer.render(this.scene,this.camera);requestAnimationFrame(t=>this.loop(t));}
  update(dt){
    for(let i=0;i<this.players.length;i++)this.players[i].update(dt,this.input.state(i));this.updateStations(dt);this.updateItems(dt);this.updateCustomers(dt);this.updateCamera(dt);this.nearestHint();
    this.timeLeft-=dt;this.spawnTimer-=dt;if(this.spawnTimer<=0){this.spawnParty();this.spawnTimer=LEVELS[this.levelIndex].spawnEvery*(.8+Math.random()*.45);}if(this.timeLeft<=0)this.finishLevel(false);this.updateOrders();this.updateUI();this.input.endFrame();
  }
}

new Game();
