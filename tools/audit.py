"""Measure the real contrast of every text box against the pixels behind it.

Writes contrast-fixes.json: for each block whose own text sits on a background
photo and fails, the extra scrim the block needs. build.py folds that back in,
so the fix comes from what is actually rendered, not from a guess.
"""
import json, os, re, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contrast import luminance, ratio, _composite, SCRIM, TARGET

CAP = 0.60          # never dim a photo further than this
data = json.load(open("_shots/audit.json"))
fails, fixes = [], {}

for page, boxes in data.items():
    fp = f"_shots/bg-{page}.png"
    if not os.path.exists(fp): continue
    im = Image.open(fp).convert("RGB")
    W, H = im.size
    for b in boxes:
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        if w < 4 or h < 4 or y + h > H: continue
        region = im.crop((max(0, x), max(0, y), min(W, x + w), min(H, y + h)))
        rw, rh = region.size
        if rw < 2 or rh < 2: continue
        sx, sy = max(1, rw // 40), max(1, rh // 14)
        px = [region.getpixel((i, j)) for j in range(0, rh, sy) for i in range(0, rw, sx)]
        col = tuple(int(v) for v in re.findall(r"\d+", b["color"])[:3])
        lt = luminance(col)
        # a text box can be much larger than its words and can span other elements,
        # so judge the 15th percentile of the area rather than the single worst pixel
        rs = sorted(ratio(lt, luminance(p)) for p in px)
        worst = rs[int(len(rs) * 0.15)]
        large = b["size"] >= 24 or (b["size"] >= 18.66 and int(b["weight"]) >= 700)
        need = 3.0 if large else 4.5
        if worst >= need: continue
        fails.append((round(worst, 2), need, page, b["t"], b["size"], b.get("bgkind"), b.get("block")))
        if b.get("bgkind") in ("image", "video") and b.get("block") and not b["plate"]:
            def pct(alpha):
                v = sorted(ratio(lt, luminance(_composite(p, SCRIM, alpha))) for p in px)
                return v[int(len(v) * 0.15)]
            if pct(CAP) < need:
                best = CAP
            else:
                lo, hi = 0.0, CAP
                for _ in range(16):
                    mid = (lo + hi) / 2
                    if pct(mid) >= need: hi = mid
                    else: lo = mid
                best = round(hi, 3)
            fixes[b["block"]] = max(fixes.get(b["block"], 0), best)

json.dump(fixes, open("contrast-fixes.json", "w"), indent=1, sort_keys=True)
fails.sort()
print(f"{len(fails)} text box(es) below threshold; {len(fixes)} block(s) need a deeper scrim\n")
for f in fails[:24]:
    print(f"  {f[0]:5} (need {f[1]})  {f[2][:24]:26} {f[3][:38]:40} {f[4]:.0f}px  bg={f[5]}")
