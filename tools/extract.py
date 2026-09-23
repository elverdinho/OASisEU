import re,json,html,os,glob

MIR="_mirror"
def unwrap(v):
    if isinstance(v,list) and len(v)==2 and isinstance(v[0],int):
        t,val=v
        if t==1: return [unwrap(x) for x in val]
        return unwrap(val)
    if isinstance(v,dict): return {k:unwrap(x) for k,x in v.items()}
    if isinstance(v,list): return [unwrap(x) for x in v]
    return v

merged={"pages":{},"blocks":{},"elements":{},"nav":None,"styles":None,"forms":{},"meta":None,"homePageId":None}
files=sorted(glob.glob(os.path.join(MIR,"*.html")))
for f in files:
    src=open(f).read()
    m=re.search(r'props="(\{&quot;pageData.*?)"\s+ssr',src,re.S)
    if not m:
        print("SKIP",f); continue
    d=unwrap(json.loads(html.unescape(m.group(1))))["pageData"]
    for pid,p in d.get("pages",{}).items():
        old=merged["pages"].get(pid)
        if old is None or (not old.get("blocks") and p.get("blocks")):
            merged["pages"][pid]=p
    merged["blocks"].update(d.get("blocks",{}))
    merged["elements"].update(d.get("elements",{}))
    merged["forms"].update(d.get("forms",{}))
    merged["nav"]=merged["nav"] or d.get("nav")
    merged["styles"]=merged["styles"] or d.get("styles")
    merged["meta"]=merged["meta"] or d.get("meta")
    merged["homePageId"]=merged["homePageId"] or d.get("homePageId")
json.dump(merged,open("site-data.json","w"),indent=1,ensure_ascii=False)
print("files",len(files),"pages",len(merged["pages"]),"blocks",len(merged["blocks"]),"elements",len(merged["elements"]))
print("\nelement types:")
from collections import Counter
print(Counter(e.get("type") for e in merged["elements"].values()))
print("\nblock types:")
print(Counter(b.get("type")+"/"+str(b.get("slot","")) for b in merged["blocks"].values()))
