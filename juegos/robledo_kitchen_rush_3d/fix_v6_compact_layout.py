from pathlib import Path

GAME = Path(__file__).resolve().parent / 'src/game.js'
text = GAME.read_text(encoding='utf-8')
replacements = {
    "add('plate',-b.xMax+1.15,backZ);add('sink',-b.xMax+2.85,backZ);add('trash',-b.xMax+4.55,backZ);add('grocery',b.xMax-3.15,backZ);":
    "add('plate',-b.xMax+1.45,backZ);add('sink',-b.xMax+3.4,backZ);add('trash',-b.xMax+5.2,backZ);add('grocery',Math.min(b.xMax-3.35,3.2),backZ);",
    "const workZ=Math.min(-1.55,b.zMin+3.6),workXs=[-b.xMax+1.4,-b.xMax+3.2,-b.xMax+5.0,-b.xMax+6.8].filter(x=>x<b.xMax-1);":
    "const workZ=Math.min(-1.45,b.zMin+4.0),workXs=[-b.xMax+2.0,-b.xMax+4.0,-b.xMax+6.0,-b.xMax+8.0].filter(x=>x<b.xMax-1);",
    "add('counter',Math.min(b.xMax-1.25,2.8),workZ);":
    "add('counter',Math.min(b.xMax-1.25,.8),workZ);",
}
for old,new in replacements.items():
    if old not in text:
        raise SystemExit(f'Could not find compact-layout source segment: {old[:70]}')
    text = text.replace(old,new,1)
GAME.write_text(text,encoding='utf-8')
print('Applied V6 compact kitchen layout: wider station access, central counter and closer grocery wall.')
