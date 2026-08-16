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
GAME.write_text(text, encoding='utf-8')
print('Applied V6 human-equivalent fixture reach plus dynamic service-point re-routing.')
