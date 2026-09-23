import os,re,sys,json,time,subprocess,urllib.parse as up

BASE="https://theoasisproject.eu"
OUT="/Users/lorenzo/Projects/oasis-project/_mirror"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def get(url):
    r=subprocess.run(["curl","-sL","--max-time","45","-A",UA,url],capture_output=True)
    if r.returncode!=0: raise RuntimeError("curl %s"%r.returncode)
    return r.stdout,""

seen=set(); queue=["/"]; pages={}
while queue:
    path=queue.pop(0)
    if path in seen: continue
    seen.add(path)
    url=BASE+path
    try:
        body,ct=get(url)
    except Exception as e:
        print("ERR",path,e); continue
    html=body.decode("utf-8","replace")
    pages[path]=html
    print("PAGE",path,len(html))
    for m in re.finditer(r'href="([^"]+)"',html):
        h=m.group(1)
        if h.startswith("//") or h.startswith("mailto:") or h.startswith("tel:"): continue
        if h.startswith("http"):
            if not h.startswith(BASE): continue
            h=h[len(BASE):] or "/"
        if not h.startswith("/"): continue
        h=h.split("#")[0].split("?")[0]
        if not h: h="/"
        if re.search(r'\.(css|js|png|jpg|jpeg|webp|svg|ico|pdf|zip|woff2?)$',h,re.I): continue
        if h not in seen and h not in queue: queue.append(h)
    time.sleep(0.15)

os.makedirs(OUT,exist_ok=True)
for p,h in pages.items():
    fn=("index" if p=="/" else p.strip("/").replace("/","__"))+".html"
    open(os.path.join(OUT,fn),"w").write(h)
json.dump(sorted(pages.keys()),open(os.path.join(OUT,"_pages.json"),"w"),indent=1)
print("\nTOTAL PAGES",len(pages))
for p in sorted(pages): print(" ",p)
