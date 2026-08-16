from __future__ import annotations

from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')

needle = "const goal=this.navGoal||raw,goalDist=m.group.position.distanceTo(goal);"
replacement = "if(target.type!=='storage'&&this.navGoal&&this.pathBlocked(this.navGoal)){const alt=this.approachPoint(target);if(alt&&alt.distanceToSquared(this.navGoal)>.04){this.navGoal=alt.clone();this.navMode='direct';this.navPath=[];this.navProbeTime=0;this.navProbeDist=m.group.position.distanceTo(this.navGoal);this.navPathProbeTime=0;this.avoidSign*=-1;}}const goal=this.navGoal||raw,goalDist=m.group.position.distanceTo(goal);"

if needle not in text:
    raise SystemExit('Could not find V6 navigation goal segment for dynamic service-point correction')
text = text.replace(needle, replacement, 1)
GAME.write_text(text, encoding='utf-8')
print('Applied V6 dynamic service-point re-routing when another crew member occupies the target approach point.')
