from __future__ import annotations

import re
from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')

# Autonomous staff remain fully physical, but move at roughly a human dash pace and receive a
# modest AI work-efficiency multiplier. This keeps support bots useful without skipping stations.
old_ctor = "this.held=null;this.radius=.43;this.speed=4.55*ROLE_META[role].move;this.facing="
new_ctor = "this.held=null;this.radius=.43;this.speed=(human?4.55:6.6)*ROLE_META[role].move;this.facing="
if old_ctor not in text:
    raise SystemExit('Could not apply V6 autonomous movement-speed tuning')
text = text.replace(old_ctor, new_ctor, 1)
old_work = "  workMultiplier(type){const r=ROLE_META[this.role];if(type==='prep')return r.prep;if(['stove','fryer','oven'].includes(type))return r.cook;if(type==='sink')return r.wash;return 1;}"
new_work = "  workMultiplier(type){const r=ROLE_META[this.role],ai=this.human?1:1.45;let base=1;if(type==='prep')base=r.prep;else if(['stove','fryer','oven'].includes(type))base=r.cook;else if(type==='sink')base=r.wash;return base*ai;}"
if old_work not in text:
    raise SystemExit('Could not apply V6 autonomous work-efficiency tuning')
text = text.replace(old_work, new_work, 1)

replacement = r'''  staticBlocked(pos){const m=this.member,g=this.game,b=g.currentBounds();if(pos.x<-b.xMax+.5||pos.x>b.xMax-.5||pos.z<b.zMin+.5||pos.z>b.zMax-.5)return true;for(const o of g.obstacles)if(Math.abs(pos.x-o.x)<o.w/2+m.radius+.06&&Math.abs(pos.z-o.z)<o.d/2+m.radius+.06)return true;return false;}
  pathBlocked(pos){if(this.staticBlocked(pos))return true;const m=this.member;for(const other of this.game.players){if(other===m)continue;if(Math.hypot(pos.x-other.group.position.x,pos.z-other.group.position.z)<m.radius+other.radius+.16)return true;}return false;}
  approachPoint(target){const m=this.member,pos=target?.pos||target?.group?.position;if(!pos||target.type==='storage')return pos;const o=this.game.obstacles.find(x=>x.type===target.type&&Math.abs(x.x-pos.x)<.08&&Math.abs(x.z-pos.z)<.08);if(!o)return pos;const pad=m.radius+.24,candidates=[new THREE.Vector3(o.x,0,o.z-o.d/2-pad),new THREE.Vector3(o.x+o.w/2+pad,0,o.z),new THREE.Vector3(o.x,0,o.z+o.d/2+pad),new THREE.Vector3(o.x-o.w/2-pad,0,o.z)];let valid=candidates.filter(p=>!this.pathBlocked(p));if(!valid.length)valid=candidates.filter(p=>!this.staticBlocked(p));const pool=valid.length?valid:candidates;pool.sort((a,b)=>a.distanceToSquared(m.group.position)-b.distanceToSquared(m.group.position));return pool[0];}
  planPath(goal){const m=this.member,start=m.group.position.clone(),step=.38,gx=Math.round((goal.x-start.x)/step),gz=Math.round((goal.z-start.z)/step),key=(x,z)=>`${x},${z}`,dirs=[[1,0],[-1,0],[0,1],[0,-1]],open=new Map(),came=new Map(),cost=new Map(),nodes=new Map(),startKey=key(0,0);open.set(startKey,{x:0,z:0,f:Math.abs(gx)+Math.abs(gz)});cost.set(startKey,0);nodes.set(startKey,{x:0,z:0});let endKey=null;for(let iter=0;iter<3200&&open.size;iter++){let ck=null,cur=null;for(const[k,n]of open)if(!cur||n.f<cur.f){ck=k;cur=n;}open.delete(ck);if(Math.abs(cur.x-gx)+Math.abs(cur.z-gz)<=1){endKey=ck;break;}for(const[dX,dZ]of dirs){const nx=cur.x+dX,nz=cur.z+dZ,nk=key(nx,nz),p=new THREE.Vector3(start.x+nx*step,0,start.z+nz*step);if(this.pathBlocked(p))continue;const nc=(cost.get(ck)||0)+1;if(nc>=(cost.get(nk)??Infinity))continue;cost.set(nk,nc);came.set(nk,ck);nodes.set(nk,{x:nx,z:nz});open.set(nk,{x:nx,z:nz,f:nc+Math.abs(gx-nx)+Math.abs(gz-nz)});}}if(!endKey)return[];const rev=[];for(let k=endKey;k&&k!==startKey;k=came.get(k)){const n=nodes.get(k);if(!n)break;rev.push(new THREE.Vector3(start.x+n.x*step,0,start.z+n.z*step));}rev.reverse();rev.push(goal.clone());return rev;}
  moveToward(point,dt,scale=.9){const m=this.member,g=this.game,v=new THREE.Vector3(point.x-m.group.position.x,0,point.z-m.group.position.z);if(v.length()<.001)return false;v.normalize();m.facing.copy(v);m.group.rotation.y=Math.atan2(v.x,v.z);const before=m.group.position.clone();g.moveCrew(m,v.clone().multiplyScalar(m.speed*scale*dt));let moved=before.distanceToSquared(m.group.position)>1e-7;if(!moved){const side=new THREE.Vector3(-v.z,0,v.x).multiplyScalar(this.avoidSign);g.moveCrew(m,side.clone().multiplyScalar(m.speed*.68*dt));moved=before.distanceToSquared(m.group.position)>1e-7;if(!moved){this.avoidSign*=-1;g.moveCrew(m,side.multiplyScalar(-m.speed*.68*dt));moved=before.distanceToSquared(m.group.position)>1e-7;}}return moved;}
  near(target,dt){const m=this.member,raw=target?.pos||target?.group?.position;if(!raw)return false;if(this.navTarget!==target){this.navTarget=target;this.navGoal=(this.approachPoint(target)||raw).clone();this.navMode='direct';this.navPath=[];this.navProbeTime=0;this.navProbeDist=m.group.position.distanceTo(this.navGoal);this.navPathStall=0;}const goal=this.navGoal||raw,goalDist=m.group.position.distanceTo(goal);if(goalDist<.28){m.animate(dt,false);return true;}
    if(this.navMode!=='path'){this.moveToward(goal,dt,.9);const after=m.group.position.distanceTo(goal);this.navProbeTime=(this.navProbeTime||0)+dt;if(this.navProbeTime>=.45){const improvement=(this.navProbeDist??after)-after;if(improvement<.14){this.navPath=this.planPath(goal);if(this.navPath.length){this.navMode='path';this.navPathStall=0;this.navPathProbe=after;this.navPathProbeTime=0;}else this.avoidSign*=-1;}this.navProbeDist=after;this.navProbeTime=0;}m.animate(dt,true,.95);return false;}
    while(this.navPath.length&&m.group.position.distanceTo(this.navPath[0])<.2)this.navPath.shift();if(!this.navPath.length){this.navMode='direct';this.navProbeDist=m.group.position.distanceTo(goal);this.navProbeTime=0;m.animate(dt,true,.95);return false;}const wp=this.navPath[0];this.moveToward(wp,dt,.9);while(this.navPath.length&&m.group.position.distanceTo(this.navPath[0])<.2)this.navPath.shift();const after=m.group.position.distanceTo(goal);this.navPathProbeTime=(this.navPathProbeTime||0)+dt;if(this.navPathProbeTime>=.65){const improvement=(this.navPathProbe??after)-after;if(improvement<.08){const retry=this.planPath(goal);if(retry.length)this.navPath=retry;else{this.navMode='direct';this.avoidSign*=-1;this.navProbeDist=after;this.navProbeTime=0;}}this.navPathProbe=after;this.navPathProbeTime=0;}m.animate(dt,true,.95);return false;}
  update(dt){'''

pattern = re.compile(r"  approachPoint\(target\)\{.*?\n  update\(dt\)\{", re.S)
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Expected to replace one V6 BotBrain navigation block, replaced {count}')
GAME.write_text(text, encoding='utf-8')
print('Applied V6 hybrid navigation with unoccupied service-point selection and AI staff tuning.')
