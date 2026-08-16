from __future__ import annotations

import re
from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')

# Reachable service ring: sample around the whole interaction envelope instead of forcing only
# four cardinal approach points in the deliberately compact starter restaurant.
replacement = r'''  approachPoint(target){const m=this.member,pos=target?.pos||target?.group?.position;if(!pos||target.type==='storage')return pos;const o=this.game.obstacles.find(x=>x.type===target.type&&Math.abs(x.x-pos.x)<.08&&Math.abs(x.z-pos.z)<.08);if(!o)return pos;const reach=Math.max(o.w/2,o.d/2)+m.radius+.16,candidates=[];for(let i=0;i<32;i++){const a=i*Math.PI/16;candidates.push(new THREE.Vector3(o.x+Math.cos(a)*reach,0,o.z+Math.sin(a)*reach));}let valid=candidates.filter(p=>!this.pathBlocked(p));if(!valid.length)valid=candidates.filter(p=>!this.staticBlocked(p));const pool=valid.length?valid:candidates;pool.sort((a,b)=>a.distanceToSquared(m.group.position)-b.distanceToSquared(m.group.position));return pool[0];}
  planPath(goal){'''
pattern = re.compile(r"  approachPoint\(target\)\{.*?\n  planPath\(goal\)\{", re.S)
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Expected to replace one V6 approachPoint method, replaced {count}')

# Senior layout correction: V5/V6 had an assembly counter unnecessarily far across the room and
# the first prep/stove pair was tight to the left wall. Keep the restaurant small, but make the
# recommended kitchen an actual compact production line with wider access and shorter routes.
layout_replacements = {
    "add('plate',-b.xMax+1.15,backZ);add('sink',-b.xMax+2.85,backZ);add('trash',-b.xMax+4.55,backZ);add('grocery',b.xMax-3.15,backZ);":
    "add('plate',-b.xMax+1.45,backZ);add('sink',-b.xMax+3.4,backZ);add('trash',-b.xMax+5.2,backZ);add('grocery',Math.min(b.xMax-3.35,3.2),backZ);",
    "const workZ=Math.min(-1.55,b.zMin+3.6),workXs=[-b.xMax+1.4,-b.xMax+3.2,-b.xMax+5.0,-b.xMax+6.8].filter(x=>x<b.xMax-1);":
    "const workZ=Math.min(-1.45,b.zMin+4.0),workXs=[-b.xMax+2.0,-b.xMax+4.0,-b.xMax+6.0,-b.xMax+8.0].filter(x=>x<b.xMax-1);",
    "add('counter',Math.min(b.xMax-1.25,2.8),workZ);":
    "add('counter',Math.min(b.xMax-1.25,.8),workZ);",
}
for old,new in layout_replacements.items():
    if old not in text:
        raise SystemExit(f'Could not find compact-layout source segment: {old[:70]}')
    text = text.replace(old,new,1)

GAME.write_text(text, encoding='utf-8')
print('Applied V6 reachable interaction ring and compact physical production-line layout.')
