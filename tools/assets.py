import json,os,re,subprocess,sys
d=json.load(open("site-data.json"))
SITE="mxBMqQrL4JTa2LLe"
paths=set()
def add(p):
    if p and isinstance(p,str) and not p.startswith("http"): paths.add(p)
for e in d["elements"].values():
    s=e.get("settings",{})
    if isinstance(s,dict): add(s.get("path"))
    b=e.get("background")
    if isinstance(b,dict): add(b.get("path"))
for b in d["blocks"].values():
    bg=b.get("background")
    if isinstance(bg,dict): add(bg.get("path"))
    st=b.get("settings",{})
    if isinstance(st,dict): add(st.get("logoImagePath"))
add((d.get("meta") or {}).get("faviconPath"))
add((d.get("meta") or {}).get("ogImagePath"))
os.makedirs("site/assets",exist_ok=True)
ok=fail=skip=0
for p in sorted(paths):
    out=os.path.join("site/assets",p)
    if os.path.exists(out) and os.path.getsize(out)>0: skip+=1; continue
    url=f"https://assets.zyrosite.com/{SITE}/{p}"
    r=subprocess.run(["curl","-sL","--max-time","60","-A","Mozilla/5.0",url,"-o",out,"-w","%{http_code}"],capture_output=True,text=True)
    if r.stdout.strip()=="200" and os.path.getsize(out)>0: ok+=1
    else: fail+=1; print("FAIL",r.stdout.strip(),p)
print(f"assets total={len(paths)} downloaded={ok} skipped={skip} failed={fail}")
