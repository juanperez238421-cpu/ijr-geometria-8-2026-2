from pathlib import Path

p = Path('Geometry8_Week3_Class2_ShadedAreas_Senior_V6_FINAL.py')
s = p.read_text(encoding='utf-8')
old = '("ERROR 2 — WRONG ORDER", r"A_{\\text{shaded}}=A_{\\text{whole}}-A_{\\text{missing}}", "For a hole, subtract missing from whole."),'
new = '("ERROR 2 — REVERSED SUBTRACTION", r"A_{\\text{missing}}-A_{\\text{whole}}\\quad\\text{is reversed}", "For a hole: whole minus missing."),'
if old not in s:
    raise SystemExit('Expected V6 error-card line not found; refusing to patch.')
p.write_text(s.replace(old, new), encoding='utf-8')
