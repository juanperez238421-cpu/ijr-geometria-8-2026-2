from __future__ import annotations

from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')

# Bots should be able to operate a fixture from the same practical interaction envelope as a
# human player. This matters in a compact starter kitchen where the only cardinal approach point
# can temporarily be occupied by another crew member. The bot still has to physically reach the
# fixture; this only prevents it from insisting on one exact service coordinate after it is
# already close enough to interact.
near_start = "near(target,dt){const m=this.member,raw=target?.pos||target?.group?.position;if(!raw)return false;"
near_replacement = "near(target,dt){const m=this.member,raw=target?.pos||target?.group?.position;if(!raw)return false;const interactionReach=target.type==='storage'?.9:target.type==='table'?1.48:1.5;if(m.group.position.distanceTo(raw)<=interactionReach){m.animate(dt,false);return true;}"
if near_start not in text:
    raise SystemExit('Could not find V6 near() start for interaction-reach correction')
text = text.replace(near_start, near_replacement, 1)

# If a still-distant bot has an approach point that becomes occupied while it is en route, pick a
# different valid side and reset the local route instead of waiting behind the other crew member.
needle = "const goal=this.navGoal||raw,goalDist=m.group.position.distanceTo(goal);"
replacement = "if(target.type!=='storage'&&this.navGoal&&this.pathBlocked(this.navGoal)){const alt=this.approachPoint(target);if(alt&&alt.distanceToSquared(this.navGoal)>.04){this.navGoal=alt.clone();this.navMode='direct';this.navPath=[];this.navProbeTime=0;this.navProbeDist=m.group.position.distanceTo(this.navGoal);this.navPathProbeTime=0;this.avoidSign*=-1;}}const goal=this.navGoal||raw,goalDist=m.group.position.distanceTo(goal);"
if needle not in text:
    raise SystemExit('Could not find V6 navigation goal segment for dynamic service-point correction')
text = text.replace(needle, replacement, 1)

# A professional service bot must not finish a task and remain parked at a critical fixture.
# In V6, idle autonomous crew walk to a free standby point in the open dining area. This prevents
# a waiter that just returned a clean plate from blocking the rack for a second bot, and also
# reduces kitchen congestion during normal service. Standby motion uses the same production near()
# and hybrid direct/A* navigation as every other physical bot action.
idle = "if(!this.task){m.animate(dt,false);return;}"
idle_replacement = "if(!this.task){const b=g.currentBounds(),bias=ROLE_META[m.role]?.botBias,candidates=bias==='service'?[new THREE.Vector3(Math.min(3.4,b.xMax-1),0,b.zMax-1.15),new THREE.Vector3(1.4,0,b.zMax-1.0),new THREE.Vector3(3.6,0,1.6)]:bias==='prep'?[new THREE.Vector3(-1.2,0,b.zMax-1.0),new THREE.Vector3(.4,0,b.zMax-1.1),new THREE.Vector3(-1.4,0,1.8)]:[new THREE.Vector3(1.2,0,b.zMax-1.0),new THREE.Vector3(0,0,b.zMax-1.0),new THREE.Vector3(1.5,0,1.8)];const free=candidates.find(p=>!this.pathBlocked(p))||candidates.find(p=>!this.staticBlocked(p))||candidates[0];if(!this.idleTarget||this.idleTarget.pos.distanceToSquared(free)>.04)this.idleTarget={type:'storage',pos:free.clone()};if(!this.near(this.idleTarget,dt))return;m.animate(dt,false);return;}"
if idle not in text:
    raise SystemExit('Could not find V6 idle BotBrain block for standby correction')
text = text.replace(idle, idle_replacement, 1)

GAME.write_text(text, encoding='utf-8')
print('Applied V6 fixture reach, dynamic service-point re-routing and idle crew standby behavior.')
