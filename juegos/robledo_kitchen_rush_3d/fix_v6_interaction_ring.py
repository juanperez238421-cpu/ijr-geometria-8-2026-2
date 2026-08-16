from __future__ import annotations

import re
from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')

replacement = r'''  approachPoint(target){const m=this.member,pos=target?.pos||target?.group?.position;if(!pos||target.type==='storage')return pos;const o=this.game.obstacles.find(x=>x.type===target.type&&Math.abs(x.x-pos.x)<.08&&Math.abs(x.z-pos.z)<.08);if(!o)return pos;const reach=Math.max(o.w/2,o.d/2)+m.radius+.16,candidates=[];for(let i=0;i<32;i++){const a=i*Math.PI/16;candidates.push(new THREE.Vector3(o.x+Math.cos(a)*reach,0,o.z+Math.sin(a)*reach));}let valid=candidates.filter(p=>!this.pathBlocked(p));if(!valid.length)valid=candidates.filter(p=>!this.staticBlocked(p));const pool=valid.length?valid:candidates;pool.sort((a,b)=>a.distanceToSquared(m.group.position)-b.distanceToSquared(m.group.position));return pool[0];}
  planPath(goal){'''

pattern = re.compile(r"  approachPoint\(target\)\{.*?\n  planPath\(goal\)\{", re.S)
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Expected to replace one V6 approachPoint method, replaced {count}')
GAME.write_text(text, encoding='utf-8')
print('Applied 32-point reachable interaction ring around compact V6 fixtures.')
