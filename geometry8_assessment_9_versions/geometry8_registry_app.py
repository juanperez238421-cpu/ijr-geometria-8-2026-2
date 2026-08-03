#!/usr/bin/env python3
"""Offline Geometry 8 response registry for nine equivalent paper versions.

Standard library only. Run:
    python geometry8_registry_app.py --host 0.0.0.0 --port 5000
"""
from __future__ import annotations
import argparse,csv,html,io,json,math,sqlite3,urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

PC_MAP={f"PC-{i:02d}":chr(64+i) for i in range(1,10)}
KEYS={
"A":[True,False,True,False,True,False,6.9,11.5,15,15,12,9.0],
"B":[False,True,False,True,False,True,6.7,14.7,17,12,9,10.0],
"C":[True,True,False,False,True,False,7.0,10.3,20,24,15,12.0],
"D":[False,False,True,True,False,True,10.6,18.1,29,24,21,11.9],
"E":[True,False,False,True,True,False,6.7,11.9,25,35,12,12.0],
"F":[False,True,True,False,False,True,9.9,6.0,26,20,28,14.4],
"G":[True,True,True,False,False,False,8.7,12.0,37,21,12,12.0],
"H":[False,False,False,True,True,True,7.0,15.2,61,40,21,15.3],
"I":[True,False,True,False,False,True,9.8,6.9,53,56,30,12.0],
}
TOL=[0]*6+[.15,.15,.01,.01,.01,.15]
TOPICS=["Trig ratios","Trig ratios","Pythagoras","Pythagoras","Thales","Geometric mean","Sine","Cosine","Pythagoras","Pythagoras","Thales","Similarity"]
CSS="""body{font-family:Arial,sans-serif;margin:0;background:#f4f7f9;color:#20252a}header{background:#173b57;color:white;padding:18px}.wrap{max-width:1050px;margin:20px auto;padding:0 14px}.card{background:white;border:1px solid #d7dee3;border-radius:10px;padding:17px;margin-bottom:15px}.btn,button{display:inline-block;background:#2878a6;color:white;border:0;border-radius:7px;padding:10px 14px;text-decoration:none;font-weight:bold;cursor:pointer;margin-right:6px}input,select{width:100%;padding:9px;border:1px solid #b7c4cc;border-radius:6px;box-sizing:border-box}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.field{margin-bottom:12px}.q{border-top:1px solid #d7dee3;padding:10px 0}.q input[type=radio]{width:auto}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #d7dee3;text-align:left}th{background:#eaf3f8}.score{font-size:36px;color:#173b57;font-weight:bold}.ok{color:#147245}.bad{color:#a12d2d}.small{color:#687780;font-size:12px}"""

def db(path):
    con=sqlite3.connect(path);con.row_factory=sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY,submitted_at TEXT,student TEXT,student_code TEXT,group_name TEXT,pc TEXT,version TEXT,answers_json TEXT,correct_json TEXT,score REAL)""")
    return con

def parse_bool(v):
    v=v.strip().lower()
    if v in {"true","t","1","v","verdadero"}:return True
    if v in {"false","f","0","falso"}:return False
    return None

def grade(version,answers):
    expected=KEYS[version];correct=[]
    for i,(raw,key) in enumerate(zip(answers,expected)):
        if i<6: ok=parse_bool(raw) is key
        else:
            try: ok=abs(float(raw.replace(",","."))-float(key))<=TOL[i]+1e-12
            except ValueError: ok=False
        correct.append(ok)
    return sum(correct),correct

def esc(v):return html.escape(str(v or ""),quote=True)
def page(title,body):
    nav='<p><a class="btn" href="/">Dashboard</a><a class="btn" href="/new">Register answers</a><a class="btn" href="/export.csv">Export CSV</a></p>'
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{esc(title)}</title><style>{CSS}</style></head><body><header><h1>Geometry 8 - Nine-PC Registry</h1></header><main class="wrap">{nav}{body}</main></body></html>'.encode()

class Handler(BaseHTTPRequestHandler):
    def send_data(self,data,ctype="text/html; charset=utf-8",status=200,filename=None):
        self.send_response(status);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(data)))
        if filename:self.send_header("Content-Disposition",f'attachment; filename="{filename}"')
        self.end_headers();self.wfile.write(data)
    def post(self):
        n=int(self.headers.get("Content-Length","0"));return urllib.parse.parse_qs(self.rfile.read(n).decode(),keep_blank_values=True)
    def do_GET(self):
        route=urllib.parse.urlparse(self.path).path
        if route=="/":return self.dashboard()
        if route=="/new":return self.form()
        if route=="/export.csv":return self.export()
        self.send_data(page("Not found",'<div class="card">Not found</div>'),status=404)
    def do_POST(self):
        if urllib.parse.urlparse(self.path).path!="/submit":return self.send_data(b"Not found",status=404)
        f=self.post();get=lambda k:f.get(k,[""])[0].strip()
        student=get("student");pc=get("pc");version=get("version").upper();answers=[get(f"q{i}") for i in range(1,13)]
        if not student or pc not in PC_MAP or version!=PC_MAP[pc] or any(a=="" for a in answers):
            return self.send_data(page("Invalid",'<div class="card"><h2>Invalid submission</h2><p>Check student, PC/version and all 12 answers.</p></div>'),status=400)
        score,correct=grade(version,answers)
        with db(self.server.db_path) as con:
            con.execute("INSERT INTO submissions(submitted_at,student,student_code,group_name,pc,version,answers_json,correct_json,score) VALUES(?,?,?,?,?,?,?,?,?)",(datetime.now().isoformat(timespec="seconds"),student,get("student_code"),get("group_name"),pc,version,json.dumps(answers),json.dumps(correct),score))
        rows=''.join(f'<tr><td>{i}</td><td>{esc(a)}</td><td>{esc(KEYS[version][i-1])}</td><td class="{"ok" if correct[i-1] else "bad"}">{"Correct" if correct[i-1] else "Incorrect"}</td></tr>' for i,a in enumerate(answers,1))
        self.send_data(page("Saved",f'<div class="card"><h2>Saved: {esc(student)}</h2><div class="score">{score}/12</div><table><tr><th>Q</th><th>Answer</th><th>Expected</th><th>Status</th></tr>{rows}</table></div>'))
    def dashboard(self):
        with db(self.server.db_path) as con:rows=con.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 100").fetchall()
        body=''.join(f'<tr><td>{r["id"]}</td><td>{esc(r["student"])}</td><td>{esc(r["group_name"])}</td><td>{r["pc"]}</td><td>{r["version"]}</td><td><b>{r["score"]:.0f}/12</b></td><td>{r["submitted_at"]}</td></tr>' for r in rows) or '<tr><td colspan="7">No submissions yet.</td></tr>'
        mapping=' '.join(f'<span class="btn">{pc} = {v}</span>' for pc,v in PC_MAP.items())
        self.send_data(page("Dashboard",f'<div class="card"><h2>PC assignment</h2>{mapping}</div><div class="card"><h2>Submissions</h2><table><tr><th>ID</th><th>Student</th><th>Group</th><th>PC</th><th>Version</th><th>Score</th><th>Time</th></tr>{body}</table></div>'))
    def form(self):
        opts=''.join(f'<option value="{pc}" data-v="{v}">{pc} - Version {v}</option>' for pc,v in PC_MAP.items())
        qs=[]
        for i in range(1,13):
            control=f'<label><input type="radio" name="q{i}" value="true" required> TRUE</label> &nbsp; <label><input type="radio" name="q{i}" value="false" required> FALSE</label>' if i<=6 else f'<input name="q{i}" required placeholder="Final numerical answer">'
            qs.append(f'<div class="q"><b>Question {i}</b> <span class="small">{TOPICS[i-1]}</span><br>{control}</div>')
        self.send_data(page("Register",f'''<div class="card"><h2>Register answers</h2><form method="post" action="/submit"><div class="grid"><div class="field"><b>Student</b><input name="student" required></div><div class="field"><b>Student code</b><input name="student_code"></div><div class="field"><b>Group</b><input name="group_name"></div><div class="field"><b>Computer</b><select name="pc" id="pc">{opts}</select><input type="hidden" name="version" id="version" value="A"><p class="small">Version <b id="label">A</b></p></div></div>{''.join(qs)}<button>Score and save</button></form></div><script>const p=document.getElementById('pc'),v=document.getElementById('version'),l=document.getElementById('label');function s(){{v.value=p.options[p.selectedIndex].dataset.v;l.textContent=v.value}}p.onchange=s;s()</script>'''))
    def export(self):
        with db(self.server.db_path) as con:rows=con.execute("SELECT * FROM submissions ORDER BY id").fetchall()
        out=io.StringIO();fields=["id","submitted_at","student","student_code","group_name","pc","version","score"]+[f"q{i}_answer" for i in range(1,13)]+[f"q{i}_correct" for i in range(1,13)]
        w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
        for r in rows:
            d={k:r[k] for k in fields if k in r.keys()};ans=json.loads(r["answers_json"]);cor=json.loads(r["correct_json"])
            for i in range(12):d[f"q{i+1}_answer"]=ans[i];d[f"q{i+1}_correct"]=int(cor[i])
            w.writerow(d)
        self.send_data(out.getvalue().encode("utf-8-sig"),"text/csv",filename="geometry8_results.csv")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=5000);ap.add_argument("--db",type=Path,default=Path("geometry8_results.sqlite3"));args=ap.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),Handler);server.db_path=args.db.resolve();print(f"Open http://127.0.0.1:{args.port}")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=="__main__":main()
