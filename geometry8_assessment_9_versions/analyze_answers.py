#!/usr/bin/env python3
"""Create CSV and HTML summaries from geometry8_results.sqlite3."""
import argparse,csv,html,json,sqlite3
from collections import defaultdict
from pathlib import Path
from statistics import mean,median

def rows_from_db(path):
    con=sqlite3.connect(path);con.row_factory=sqlite3.Row
    try:return [dict(r) for r in con.execute("SELECT * FROM submissions ORDER BY id")]
    finally:con.close()
def write_csv(path,rows,fields):
    with path.open("w",newline="",encoding="utf-8-sig") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--db",type=Path,default=Path("geometry8_results.sqlite3"));ap.add_argument("--out",type=Path,default=Path("analysis_output"));a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    data=rows_from_db(a.db) if a.db.exists() else [];versions=defaultdict(list);questions=defaultdict(list);students=[]
    for r in data:
        versions[r["version"]].append(float(r["score"]));correct=json.loads(r["correct_json"])
        students.append({"id":r["id"],"student":r["student"],"student_code":r["student_code"],"group":r["group_name"],"pc":r["pc"],"version":r["version"],"score":r["score"],"percent":round(100*float(r["score"])/12,2)})
        for i,v in enumerate(correct,1):questions[(r["version"],i)].append(1 if v else 0)
    vr=[{"version":v,"submissions":len(s),"mean":round(mean(s),2),"median":round(median(s),2),"minimum":min(s),"maximum":max(s)} for v,s in sorted(versions.items())]
    qr=[{"version":v,"question":q,"responses":len(x),"correct":sum(x),"accuracy_percent":round(100*sum(x)/len(x),2)} for (v,q),x in sorted(questions.items())]
    write_csv(a.out/"student_scores.csv",students,["id","student","student_code","group","pc","version","score","percent"])
    write_csv(a.out/"version_analysis.csv",vr,["version","submissions","mean","median","minimum","maximum"])
    write_csv(a.out/"question_analysis.csv",qr,["version","question","responses","correct","accuracy_percent"])
    def table(rows,fields):
        return "<table><tr>"+"".join(f"<th>{html.escape(f)}</th>" for f in fields)+"</tr>"+"".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(f,'')))}</td>" for f in fields)+"</tr>" for r in rows)+"</table>"
    report=f"<!doctype html><meta charset='utf-8'><style>body{{font-family:Arial;margin:25px}}table{{border-collapse:collapse;width:100%;margin-bottom:24px}}th,td{{border:1px solid #ccc;padding:7px}}th{{background:#eaf3f8}}</style><h1>Geometry 8 Analysis</h1><h2>Versions</h2>{table(vr,['version','submissions','mean','median','minimum','maximum'])}<h2>Questions</h2>{table(qr,['version','question','responses','correct','accuracy_percent'])}<h2>Students</h2>{table(students,['id','student','group','pc','version','score','percent'])}"
    (a.out/"analysis_report.html").write_text(report,encoding="utf-8");print(f"Analyzed {len(data)} submissions -> {a.out}")
if __name__=="__main__":main()
