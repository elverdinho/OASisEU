#!/usr/bin/env python3
"""OASis - static site generator.
Reads site-data.json (the whole site content model) and writes site/*.html.
Edit site-data.json (or the content/*.md helpers) then run: python3 build.py
"""
import json, os, re, shutil, sys, html as H
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
from contrast import header_scrim, darken_to_pass, parse_rgb, luminance, ratio, TARGET, needed_overlay

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "site")
DATA = json.load(open(os.path.join(ROOT, "site-data.json"), encoding="utf-8"))

PAGES, BLOCKS, ELS = DATA["pages"], DATA["blocks"], DATA["elements"]
_fix_path = os.path.join(ROOT, "contrast-fixes.json")
OVERLAY_FLOOR = json.load(open(_fix_path)) if os.path.exists(_fix_path) else {}
STYLES, NAV, META  = DATA["styles"], DATA["nav"], DATA.get("meta") or {}
HOME = "ai-Lbbx8"
DESKTOP_MIN = 1024          # breakpoint used by the builder
MOBILE_W    = 328           # mobile design canvas width

OVERLAY = 'rgb(29, 30, 32)'   # the fixed scrim the builder puts over image/video backgrounds
HEADER_OVERLAY = [(0, 0)]   # (desktop, mobile) header height when the header floats over content

def _pad_parts(p):
    parts = str(p).split()
    if len(parts) == 1: parts = parts * 4
    elif len(parts) == 2: parts = [parts[0], parts[1], parts[0], parts[1]]
    elif len(parts) == 3: parts = [parts[0], parts[1], parts[2], parts[1]]
    return parts

def _pad_top(p):  return _pad_parts(p)[0]
def _pad_rest(p): return " ".join(_pad_parts(p)[1:])

def px(v, d="0px"):
    if v is None: return d
    return f"{v}px" if isinstance(v, (int, float)) else str(v)

def slug_url(pid):
    p = PAGES.get(pid)
    if not p: return "#"
    return "/" if pid == HOME else f"/{p['slug']}"

def asset(path):
    return "/assets/" + path if path else ""

# ---------------------------------------------------------------- global css
def font_css(key, sel):
    s = STYLES.get(key, {})
    d = "".join(f"{k}:{v};" for k, v in s.items()
                if not k.startswith("m-") and k not in ("color-hover",))
    m = f"font-size:{s['m-font-size']};" if s.get("m-font-size") else ""
    return (f"{sel}{{{d}}}", f"{sel}{{{m}}}" if m else "")

def button_css(kind):
    s = STYLES.get(f"grid-button-{kind}", {})
    g = s.get
    base = (f".btn-{kind}{{"
        f"font-size:{g('font-size','16px')};font-family:{g('font-family')};"
        f"font-weight:{g('font-weight',400)};line-height:{g('line-height','normal')};"
        f"letter-spacing:{g('letter-spacing','normal')};text-transform:{g('text-transform','none')};"
        f"text-decoration:{g('text-decoration','none')};color:{g('font-color','#fff')};"
        f"background:{g('background-color','#000')};border-radius:{px(g('border-radius',999))};"
        f"padding:{g('padding-y','16px')} {g('padding-x','40px')};"
        f"transition:all {g('transition-duration','.2s')} {g('transition-timing-function','ease')};}}")
    hov = (f".btn-{kind}:hover{{color:{g('font-color-hover', g('font-color','#fff'))};"
           f"background:{g('background-color-hover','#1d1e20')};}}")
    mob = (f".btn-{kind}{{font-size:{g('m-font-size','16px')};"
           f"padding:{g('m-padding-y','14px')} {g('m-padding-x','36px')};}}")
    return base + hov, mob

def global_css():
    f = STYLES["font"]
    desk, mob = [], []
    for key, sel in [("h1","h1"),("h2","h2"),("h3","h3"),("h4","h4"),("h5","h5"),("h6","h6"),
                     ("body",".body,p,li"),("body-large",".body-large"),("body-small",".body-small")]:
        d, m = font_css(key, sel)
        desk.append(d)
        if m: mob.append(m)
    for kind in ("primary","secondary"):
        d, m = button_css(kind); desk.append(d); mob.append(m)
    nl = STYLES.get("nav-link", {})
    base = f"""
:root{{--font-primary:{f['primary']};--font-secondary:{f['secondary']};
--nav-link:{nl.get('color','#000')};--nav-link-hover:{nl.get('color-hover','#000')};}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;overflow-x:hidden;font-family:var(--font-secondary);background:#fffff0}}
img{{display:block;max-width:100%}}
a{{color:inherit}}
h1,h2,h3,h4,h5,h6,p,ul,ol{{margin:0}}
ul,ol{{padding-left:1.25em}}
.block{{position:relative;width:100%}}
.block-bg{{overflow:hidden}}
.block-bg{{position:absolute;inset:0;background-size:cover;background-position:center;background-repeat:no-repeat}}
.block-overlay{{position:absolute;inset:0}}
.canvas{{position:relative;margin:0 auto;}}
.el{{position:absolute;display:flex;flex-direction:column;}}
.el-text{{overflow:visible}}
/* a text box sitting on a photo gets a readable plate behind the words only:
   the picture itself is never dimmed, the scrim fades in just under the text */
.el-text.on-photo{{isolation:isolate}}
.el-text.on-photo::before{{content:"";position:absolute;left:0;right:0;bottom:0;top:-52px;
 z-index:-1;pointer-events:none;
 border-radius:0 0 var(--plate-radius,0px) var(--plate-radius,0px);
 background:linear-gradient(180deg,rgba(17,19,22,0) 0%,rgba(17,19,22,.42) 34%,
  rgba(17,19,22,.68) 62%,rgba(17,19,22,.78) 100%);
 -webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}}
.el-text.on-photo *{{text-shadow:0 1px 4px rgba(17,19,22,.75)}}
/* ---- call cards: a real grid, so they can be sorted and filtered ---- */
.has-grid{{padding-bottom:72px!important}}
.has-grid .canvas{{min-height:0}}
.call-filter{{position:relative;display:flex;flex-wrap:wrap;gap:10px;padding-top:150px;
 margin-bottom:28px}}
.chip{{font-family:var(--font-secondary);font-size:15px;line-height:1;cursor:pointer;
 border:1.5px solid rgba(29,30,32,.25);background:rgba(255,255,255,.55);color:#1d1e20;
 border-radius:999px;padding:11px 18px;transition:all .18s ease;display:inline-flex;gap:7px;
 align-items:center}}
.chip span{{opacity:.55;font-size:13px}}
.chip:hover{{border-color:rgba(29,30,32,.55)}}
.chip.is-on{{background:#1d1e20;border-color:#1d1e20;color:#fffff0}}
.chip.is-on span{{opacity:.7}}
.call-grid{{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:26px 24px}}
.call-card{{position:relative;display:block;text-decoration:none;border-radius:12px;
 overflow:hidden;aspect-ratio:361/248;background:#1d1e20;
 transition:transform .22s ease,box-shadow .22s ease}}
.call-card:hover{{transform:translateY(-4px);box-shadow:0 14px 34px rgba(17,19,22,.28)}}
.call-card img{{width:100%;height:100%;object-fit:cover}}
.call-card__caption{{position:absolute;left:0;right:0;bottom:0;padding:44px 16px 14px;
 background:linear-gradient(180deg,rgba(17,19,22,0) 0%,rgba(17,19,22,.45) 32%,
  rgba(17,19,22,.72) 62%,rgba(17,19,22,.8) 100%)}}
.call-card__caption *{{text-shadow:0 1px 4px rgba(17,19,22,.75)}}
.call-card__caption>*{{font-size:20px;line-height:1.35;color:#fffff0}}
.call-card__caption p,.call-card__caption h1,.call-card__caption h2,
.call-card__caption h3,.call-card__caption h4,.call-card__caption h5,
.call-card__caption h6{{margin:0}}
.call-card[hidden]{{display:none}}
.call-empty{{font-family:var(--font-secondary);padding:18px 0;opacity:.7}}
.el-text>*{{width:100%}}
/* flex items default to min-height:auto, which lets a tall photo grow past
   its box and collide with the next one - pin it to the box instead */
.el-img img{{width:100%;height:100%;object-fit:cover;flex:none;min-width:0;min-height:0}}
.el-img,.el-img a{{overflow:hidden}}
.el-img a{{width:100%;height:100%;display:block}}
.el-btn{{align-items:center;justify-content:center}}
.el-btn a{{display:inline-flex;align-items:center;justify-content:center;text-align:center;
 white-space:nowrap;cursor:pointer;border:0;text-decoration:none}}
.el-embed{{height:auto!important;overflow:visible}}
.el-embed iframe{{width:100%;border:0;max-width:100%}}
.el-shape svg{{width:100%;height:100%}}
.reveal{{opacity:0;transform:translateY(24px);transition:opacity .7s ease,transform .7s ease}}
.reveal.in{{opacity:1;transform:none}}
/* ---- header ---- */
.site-header{{position:relative;z-index:50;width:100%}}
.header-scrim{{position:absolute;inset:0;pointer-events:none}}
.header-inner{{position:relative;z-index:1}}
.header-logo img{{filter:drop-shadow(0 2px 6px rgba(0,0,0,.45))}}
.site-header.sticky{{position:sticky;top:0}}
.header-inner{{margin:0 auto;display:flex;align-items:center;justify-content:space-between}}
.header-logo img{{height:auto}}
.nav{{display:flex;align-items:center}}
.nav a{{font-family:{nl.get('font-family','var(--font-secondary)')};font-size:{nl.get('font-size','14px')};
 font-weight:{nl.get('font-weight',400)};color:var(--nav-link);text-decoration:none;
 text-transform:{nl.get('text-transform','none')};white-space:nowrap;
 font-weight:600;text-shadow:0 1px 3px rgba(17,19,22,.8),0 0 10px rgba(17,19,22,.5)}}
.nav a:hover,.nav a.active{{color:var(--nav-link-hover);text-decoration:underline}}
.burger{{display:none;background:none;border:0;cursor:pointer;padding:8px}}
.burger span{{display:block;width:26px;height:2px;background:var(--nav-link);margin:5px 0;box-shadow:0 1px 3px rgba(17,19,22,.7)}}
/* ---- forms ---- */
.form-wrap{{width:100%;height:100%;display:flex}}
form.gform{{width:100%;display:flex;flex-direction:column;}}
form.gform label{{display:block;margin-bottom:6px}}
form.gform input,form.gform textarea,form.gform select{{width:100%;border-style:solid;outline:none;
 padding:12px 14px;border-radius:8px;font-family:var(--font-secondary)}}
form.gform textarea{{min-height:120px;resize:vertical}}
form.gform .field{{display:flex;flex-direction:column}}
form.gform .form-msg{{display:none;margin-top:10px;padding:10px 14px;border-radius:8px;
 background:rgba(255,255,255,.9);color:#1d1e20;font-family:var(--font-secondary)}}
form.gform.sent .form-msg{{display:block}}
form.gform .err{{color:#fc5185;font-size:13px;margin-top:4px;display:none}}
form.gform .field.invalid .err{{display:block}}
form.gform .hp{{display:none}}
/* ---- cookie ---- */
#cookie-bar{{position:fixed;left:16px;right:16px;bottom:16px;z-index:100;background:#1d1e20;color:#fff;
 padding:16px 20px;border-radius:14px;display:none;gap:16px;align-items:center;justify-content:space-between;
 font-family:var(--font-secondary);font-size:14px;box-shadow:0 8px 30px rgba(0,0,0,.25);flex-wrap:wrap}}
#cookie-bar.show{{display:flex}}
body.cookie-open{{padding-bottom:var(--cookie-h,96px)}}
#cookie-bar button{{border:0;border-radius:999px;padding:10px 22px;cursor:pointer;font-family:inherit}}
#cookie-bar .accept{{background:#fe5c36;color:#fff}}
#cookie-bar .decline{{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.4)}}
"""
    desktop_only = "@media(min-width:%dpx){.canvas{}}" % DESKTOP_MIN
    mobile = "@media(max-width:%dpx){%s\n.nav{position:absolute;top:100%%;right:16px;left:16px;flex-direction:column;align-items:flex-start;gap:14px;background:#fffff0;padding:18px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.15);display:none}.nav.open{display:flex}.burger{display:block}}" % (DESKTOP_MIN-1, "\n".join(mob))
    return base + "\n".join(desk) + "\n" + desktop_only + "\n" + mobile

# ---------------------------------------------------------------- elements
def el_style(e, z):
    d, m = e.get("desktop", {}) or {}, e.get("mobile", {}) or {}
    parts = [f"--dt:{px(d.get('top'))}", f"--dl:{px(d.get('left'))}",
             f"--dw:{px(d.get('width'))}", f"--dh:{px(d.get('height'))}",
             f"--mt:{px(m.get('top'))}", f"--ml:{px(m.get('left'))}",
             f"--mw:{px(m.get('width'))}", f"--mh:{px(m.get('height'))}",
             f"z-index:{z}"]
    st = (e.get("settings") or {}).get("styles") or {}
    if isinstance(st, dict):
        if st.get("align"):   parts.append(f"justify-content:{st['align']}")
        if st.get("justify"): parts.append(f"align-items:{st['justify']}")
        if st.get("text"):    parts.append(f"text-align:{st['text']}")
    return ";".join(parts)

def link_attrs(e):
    s = e.get("settings") or {}
    href, target, rel = "", "", ""
    lt = e.get("linkType") or s.get("linkType")
    if e.get("href") or s.get("href"):
        href = e.get("href") or s.get("href")
    if (lt == "page" or s.get("clickAction") == "link") and (e.get("linkedPageId") or s.get("linkedPageId")):
        pid = e.get("linkedPageId") or s.get("linkedPageId")
        if pid in PAGES: href = slug_url(pid)
    if e.get("target") or s.get("target"):
        target = e.get("target") or s.get("target")
    if e.get("rel") or s.get("rel"):
        rel = e.get("rel") or s.get("rel")
    a = ""
    if target: a += f' target="{target}"'
    if rel:    a += f' rel="{rel}"'
    return href, a

def render_form(e, idx):
    s = e.get("settings") or {}
    schema = s.get("schema") or []
    btn = e.get("submitButtonData") or {}
    fid = f"gform{idx}"
    d = e.get("desktop", {}) or {}
    g = e.get
    gap      = px(d.get("formElementsVerticalSpacing"), "16px")
    lbl_size = px(d.get("labelTextSize"), "14px")
    inp_size = px(d.get("inputTextSize"), "16px")
    btn_size = px(d.get("submitButtonFontSize"), "16px")
    fam = f"'{g('formFontFamily')}', sans-serif" if g("formFontFamily") else "var(--font-secondary)"
    css = f"""<style>
#{fid}{{background:{g('formBackgroundColor') or (g('innerBackground') or {}).get('color','transparent')};
 padding:{px(g('formPadding'),'0px')};border-radius:{px(g('formBorderRadius'),'0px')};
 border:{px(g('formBorderWidth'),'0px')} solid {g('formBorderColor','transparent')};
 gap:{gap};font-family:{fam};font-weight:{g('formFontWeight',400)}}}
#{fid} label{{font-size:{lbl_size};color:{g('labelTextColor','#fff')};font-family:{fam}}}
#{fid} input,#{fid} textarea{{font-size:{inp_size};font-family:{fam};
 background:{g('inputFillColor','#fff')};color:{g('inputTextColor','#000')};
 border:{px(g('inputBorderWidth'),'1px')} solid {g('inputBorderColor','transparent')};
 border-radius:{px(g('inputBorderRadius'),'8px')};padding:16px}}
#{fid} input::placeholder,#{fid} textarea::placeholder{{color:{g('inputTextColor','#000')};opacity:1}}
#{fid} input:hover,#{fid} textarea:hover,#{fid} input:focus,#{fid} textarea:focus{{
 background:{g('inputFillColorHover', g('inputFillColor','#fff'))};
 color:{g('inputTextColorHover', g('inputTextColor','#000'))};
 border-color:{g('inputBorderColorHover', g('inputBorderColor','transparent'))}}}
#{fid} .submit{{font-size:{btn_size};font-family:{fam};cursor:pointer;
 color:{g('submitButtonFontColor','#fff')};background:{g('submitButtonBackgroundColor','#000')};
 border:{px(g('submitButtonBorderWidth'),'0px')} solid {g('submitButtonBorderColor','transparent')};
 border-radius:{px(g('submitButtonBorderRadius'),'999px')};
 padding:15px 39px;transition:all .2s ease;align-self:center;white-space:nowrap}}
#{fid} .submit:hover{{color:{g('submitButtonFontColorHover', g('submitButtonFontColor','#fff'))};
 background:{g('submitButtonBackgroundColorHover', g('submitButtonBackgroundColor','#000'))};
 border-color:{g('submitButtonBorderColorHover', g('submitButtonBorderColor','transparent'))}}}
</style>"""
    fields = []
    for f in schema:
        fname = f.get("id") or f.get("name")
        label = f.get("inputLabel") or f.get("name") or ""
        ph    = f.get("placeholder") or ""
        req   = any("required" in (v if isinstance(v, list) else [v]) for v in (f.get("validation") or []))
        typ   = "email" if f.get("validationType") == "email" else "text"
        msgs  = f.get("validation-messages") or {}
        err   = msgs.get("required") or msgs.get("email") or "This field is required"
        attrs = f'name="{H.escape(fname)}" placeholder="{H.escape(ph)}"' + (" required" if req else "")
        ctrl  = (f'<textarea {attrs} rows="4"></textarea>' if f.get("tag") == "textarea"
                 else f'<input type="{typ}" {attrs}>')
        fields.append(f'<div class="field"><label>{H.escape(label)}{"*" if req else ""}</label>'
                      f'{ctrl}<span class="err">{H.escape(err)}</span></div>')
    label   = btn.get("content") or "Send"
    success = H.escape(s.get("successMessage") or "Message sent successfully")
    nf = re.sub(r"[^a-z0-9]+", "-", (e.get("formId") or "form").lower()).strip("-")
    hidden = (f'<input type="hidden" name="form-name" value="{nf}">'
              f'<p class="hp" hidden><label>Leave this empty: '
              f'<input name="bot-field" tabindex="-1" autocomplete="off"></label></p>')
    return (css + f'<div class="form-wrap"><form class="gform" id="{fid}" name="{nf}" '
            f'method="POST" data-netlify="true" netlify-honeypot="bot-field" '
            f'data-form="{H.escape(e.get("formId",""))}" novalidate>{hidden}{"".join(fields)}'
            f'<button type="submit" class="submit">{H.escape(label)}</button>'
            f'<div class="form-msg" data-success="{success}">{success}</div></form></div>')

def render_element(eid, z, form_counter, comps=()):
    e = ELS.get(eid)
    if not e: return ""
    t = e.get("type")
    s = e.get("settings") or {}
    st = el_style(e, z)
    anim = ' reveal' if (e.get("animation") or {}).get("name") else ''
    if t == "GridTextBox":
        photo = photo_under(eid, comps)
        cls, extra = "", ""
        if photo is not None:
            r = ((photo.get("desktop") or {}).get("borderRadius")
                 or (photo.get("mobile") or {}).get("borderRadius") or "0px")
            cls, extra = " on-photo", f";--plate-radius:{r}"
        return f'<div class="el el-text{anim}{cls}" data-el="{eid}" style="{st}{extra}">{e.get("content","")}</div>'
    if t == "GridImage":
        d = e.get("desktop", {}) or {}; m = e.get("mobile", {}) or {}
        br = d.get("borderRadius") or m.get("borderRadius") or "0px"
        img = (f'<img src="{asset(s.get("path"))}" alt="{H.escape(s.get("alt") or "")}" loading="lazy" '
               f'style="border-radius:{br}">')
        href, a = link_attrs(e)
        if s.get("clickAction") == "lightbox":
            body = f'<a href="{asset(s.get("path"))}" data-lightbox="1">{img}</a>'
        elif href:
            body = f'<a href="{H.escape(href)}"{a}>{img}</a>'
        else:
            body = img
        return f'<div class="el el-img{anim}" style="{st}">{body}</div>'
    if t == "GridButton":
        href, a = link_attrs(e)
        btype = s.get("type", "primary")
        extra = ""
        for k, css in (("backgroundColor","background"),("fontColor","color"),("borderColor","border-color")):
            if e.get(k): extra += f"{css}:{e[k]};"
        return (f'<div class="el el-btn{anim}" style="{st}">'
                f'<a class="btn-{btype}" href="{H.escape(href or "#")}"{a} style="{extra}">'
                f'{H.escape(e.get("content",""))}</a></div>')
    if t == "GridForm":
        form_counter[0] += 1
        return f'<div class="el el-form{anim}" style="{st}">{render_form(e, form_counter[0])}</div>'
    if t == "GridEmbed":
        c = re.sub(r'</?code>', '', e.get("content",""))
        return f'<div class="el el-embed" style="{st}">{c}</div>'
    if t == "GridShape":
        svg = (e.get("svg") or "").replace("fill=\"none\"", f'fill="{e.get("color","#000")}"')
        return f'<div class="el el-shape{anim}" style="{st}">{svg}</div>'
    return ""


# ---------------------------------------------------------------- call cards
COUNTRIES = ["Armenia", "Belgium", "France", "Georgia", "Hungary", "Italy",
             "Poland", "Portugal", "Slovakia", "Slovenia", "Spain", "Germany"]

def _plain(html_s):
    t = re.sub(r"<[^>]+>", " ", html_s or "")
    return H.unescape(re.sub(r"\s+", " ", t)).strip()

def parse_call(caption):
    """(country, deadline as sortable YYYYMMDD, deadline text) from a card caption."""
    txt = _plain(caption)
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", txt)
    key = f"{m.group(3)}{m.group(2)}{m.group(1)}" if m else "00000000"
    country = next((c for c in COUNTRIES if re.search(rf"\b{c}\b", txt, re.I)), None)
    if not country:
        head = re.split(r"Application|Deadline", txt)[0]
        parts = [p.strip(" -–") for p in head.split("-") if p.strip(" -–")]
        country = parts[-1] if parts else "Other"
    return country, key, (m.group(0) if m else "")

def collect_cards(block):
    """Pair each photo with the caption sitting on it, newest deadline first."""
    comps = comps_pre(block)
    cards = []
    for eid in comps:
        e = ELS.get(eid) or {}
        if e.get("type") != "GridTextBox": continue
        photo = photo_under(eid, comps)
        if photo is None: continue
        pid_ = next((i for i in comps if ELS.get(i) is photo), None)
        s = photo.get("settings") or {}
        href, attrs = link_attrs(photo)
        country, key, deadline = parse_call(e.get("content"))
        cards.append({"img": asset(s.get("path")), "alt": s.get("alt") or "",
                      "caption": e.get("content") or "", "href": href, "attrs": attrs,
                      "country": country, "key": key, "deadline": deadline,
                      "eid": eid, "iid": pid_})
    cards.sort(key=lambda c: c["key"], reverse=True)
    return cards

def render_card_grid(block, title_ids):
    cards = collect_cards(block)
    if len(cards) < 4: return None
    counts = {}
    for c in cards: counts[c["country"]] = counts.get(c["country"], 0) + 1
    chips = ['<button class="chip is-on" data-country="" aria-pressed="true">'
             f'All <span>{len(cards)}</span></button>']
    for c in sorted(counts):
        chips.append(f'<button class="chip" data-country="{H.escape(c)}" aria-pressed="false">'
                     f'{H.escape(c)} <span>{counts[c]}</span></button>')
    items = []
    for c in cards:
        tag = "a" if c["href"] else "div"
        href = f' href="{H.escape(c["href"])}"{c["attrs"]}' if c["href"] else ""
        items.append(
            f'<{tag} class="call-card" data-country="{H.escape(c["country"])}"{href}>'
            f'<img src="{c["img"]}" alt="{H.escape(c["alt"])}" loading="lazy">'
            f'<div class="call-card__caption">{c["caption"]}</div></{tag}>')
    return (f'<div class="call-filter" role="group" aria-label="Filter calls by country">'
            f'{"".join(chips)}</div>'
            f'<div class="call-grid">{"".join(items)}</div>'
            f'<p class="call-empty" hidden>No calls for this country yet.</p>')

# ---------------------------------------------------------------- blocks
def _el_bottom(eid, key):
    e = ELS.get(eid) or {}
    box = e.get(key) or {}
    top, h = box.get("top") or 0, box.get("height") or 0
    if e.get("type") == "GridEmbed":
        m = re.search(r'height="(\d+)"', e.get("content", ""))
        if m: h = max(h, int(m.group(1)) + 4)
    return top + h

def _box(e, key):
    b = e.get(key) or {}
    return (b.get("left") or 0, b.get("top") or 0,
            b.get("width") or 0, b.get("height") or 0)

def _overlap_ratio(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    if aw <= 0 or ah <= 0: return 0.0
    ox = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    oy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return (ox * oy) / (aw * ah)

def photo_under(eid, comps, key="desktop"):
    """The photo a text box is captioning.

    Only a caption earns a plate: it has to sit on the picture's bottom edge and
    run most of its width, the way a card label does. Numbers and labels floating
    in the middle of an image are part of the composition - plating each of them
    would just litter the picture with grey boxes.
    """
    e = ELS.get(eid) or {}
    if e.get("type") != "GridTextBox": return None
    tx, ty, tw, th = _box(e, key)
    for oid in comps:
        o = ELS.get(oid) or {}
        if o.get("type") != "GridImage": continue
        ox, oy, ow, oh = _box(o, key)
        if not ow or not oh: continue
        if _overlap_ratio((tx, ty, tw, th), (ox, oy, ow, oh)) < 0.45: continue
        bottom_anchored = abs((ty + th) - (oy + oh)) <= 14
        spans_width = tw >= 0.7 * ow
        if bottom_anchored and spans_width:
            return o
    return None

def _image_region(path, box, canvas_w, block_h, section_w=1440):
    """Map an element box on the canvas to pixel coordinates of the block's
    `cover`-scaled background image, so we measure what is really behind it."""
    try:
        from PIL import Image
        w, h = Image.open(path).size
    except Exception:
        return None
    if not block_h: return None
    cw = int(re.sub(r"[^0-9]", "", str(canvas_w)) or section_w)
    scale = max(section_w / w, block_h / h)
    dw, dh = w * scale, h * scale
    ox, oy = (dw - section_w) / 2, (dh - block_h) / 2      # `cover` centres the image
    ex = (section_w - cw) / 2 + (box[0] or 0)
    ey = box[1] or 0
    x0 = max(0, int((ex + ox) / scale)); y0 = max(0, int((ey + oy) / scale))
    x1 = min(w, int((ex + (box[2] or 0) + ox) / scale))
    y1 = min(h, int((ey + (box[3] or 0) + oy) / scale))
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    return (x0, y0, x1, y1)

def comps_pre(b):
    return b.get("components") or b.get("zindexes") or []

def render_block(bid, form_counter, is_first=False):
    b = BLOCKS.get(bid)
    if not b: return ""
    st = (b.get("settings") or {}).get("styles") or {}
    d, m = b.get("desktop", {}) or {}, b.get("mobile", {}) or {}
    bg = b.get("background") or {}
    ov = bg.get("overlay-opacity")
    _comps = comps_pre(b)
    loose_text = [e for e in _comps
                  if (ELS.get(e) or {}).get("type") == "GridTextBox"
                  and photo_under(e, _comps) is None]
    if loose_text and bg.get("current") in ("image", "video") and bg.get("path"):
        img_path = os.path.join(OUT, "assets", bg["path"])
        block_h = (d.get("minHeight") or 0) + (HEADER_OVERLAY[0][0] if is_first else 0)
        worst_ov = float(ov or 0)
        for eid in loose_text:
            e = ELS.get(eid) or {}
            cm = re.search(r"color:\s*(rgb\([^)]*\))", e.get("content", "") or "")
            fg = parse_rgb(cm.group(1)) if cm else (255, 255, 240)
            reg = _image_region(img_path, _box(e, "desktop"),
                                st.get("width", "1224px"), block_h)
            worst_ov = max(worst_ov, needed_overlay(img_path, ov, fg, region=reg))
        ov = round(worst_ov, 3)
    ov = max(float(ov or 0), float(OVERLAY_FLOOR.get(bid, 0)))
    if not bg.get('overlay-opacity') and not OVERLAY_FLOOR.get(bid): ov = bg.get('overlay-opacity')
    layers = ""
    if bg.get("current") == "video" and (bg.get("video") or {}).get("videoSrc"):
        v = bg["video"]
        layers += (f'<video class="block-bg" autoplay muted loop playsinline preload="none" '
                   f'poster="{"/"+v.get("videoThumbnailSrc","")}" '
                   f'style="object-fit:cover;width:100%;height:100%">'
                   f'<source data-src="/{v["videoSrc"]}" type="video/mp4"></video>')
        if bg.get("overlay-opacity"):
            layers += (f'<div class="block-overlay" style="background:{OVERLAY};'
                       f'opacity:{ov}"></div>')
    elif bg.get("current") == "image" and bg.get("path"):
        layers += (f'<div class="block-bg" style="background-image:url({asset(bg["path"])});'
                   f'background-position:{b.get("backgroundImagePosition","center")}"></div>')
        if bg.get("overlay-opacity"):
            layers += (f'<div class="block-overlay" style="background:{OVERLAY};'
                       f'opacity:{ov}"></div>')
    elif bg.get("color"):
        layers += f'<div class="block-bg" style="background:{bg["color"]}"></div>'
    width = st.get("width", "1224px")
    pad   = st.get("block-padding", "16px 0")
    mpad  = st.get("m-block-padding", "16px")
    order = b.get("zindexes") or b.get("components") or []
    comps = b.get("components") or order
    zmap  = {eid: i + 1 for i, eid in enumerate(order)}
    grid_html, grid_cls = "", ""
    if b.get("htmlId") == "archivedcalls":
        cards = collect_cards(b)
        used = {c["eid"] for c in cards} | {c["iid"] for c in cards}
        grid_html = render_card_grid(b, used) or ""
        if grid_html:
            comps = [e for e in comps if e not in used]
            grid_cls = " has-grid"
    kids  = "".join(render_element(eid, zmap.get(eid, 1), form_counter, comps) for eid in comps)
    kids += grid_html
    cls = f"blk-{bid.replace('-','_')}"
    hp = HEADER_OVERLAY[0] if is_first else (0, 0)
    dpad = f"{hp[0]}px 0 0 0" if is_first and hp[0] else "0"
    mpad2 = f"{hp[1]}px 0 0 0" if is_first and hp[1] else "0"
    pd, pm = _pad_parts(dpad), _pad_parts(mpad2)
    def _n(v):
        mm = re.match(r'^(\d+)', str(v).strip()); return int(mm.group(1)) if mm else 0
    need_d = max([_el_bottom(e, "desktop") for e in comps] or [0]) + _n(pd[0]) + _n(pd[2])
    need_m = max([_el_bottom(e, "mobile") for e in comps] or [0]) + _n(pm[0]) + _n(pm[2])
    dmin = max((d.get('minHeight') or 0) + (hp[0] if is_first else 0), need_d)
    mmin = max((m.get('minHeight') or 0) + (hp[1] if is_first else 0), need_m)
    if grid_cls:
        dmin = mmin = 0
    css = (f"<style>.{cls}{{padding:{dpad};min-height:{px(dmin)}}}.{cls} .canvas{{width:{width}}}"
           f"@media(max-width:{DESKTOP_MIN-1}px){{.{cls}{{padding:{mpad2};min-height:{px(mmin)}}}"
           f".{cls} .canvas{{width:{MOBILE_W}px}}}}</style>")
    anchor = b.get("htmlId") or f"s-{bid}"
    return f'{css}<section class="block {cls}{grid_cls}" id="{anchor}" data-block="{bid}" data-bgkind="{bg.get("current","")}">{layers}<div class="canvas">{kids}</div></section>'

SCRIM_FLOOR = 0.28   # always keep a little separation under a floating header

def _first_block_bg(pid):
    p = PAGES.get(pid) or {}
    blocks = p.get("blocks") or []
    if not blocks: return {}
    return (BLOCKS.get(blocks[0]) or {}).get("background") or {}

def page_header_treatment(pid):
    """(scrim alpha, nav colour) chosen from the real pixels behind the menu.

    Over a photo we darken the strip just enough; over a flat light colour a dark
    bar would look wrong, so we deepen the brand colour instead until it reads.
    """
    bg = _first_block_bg(pid)
    nav_css = STYLES.get("nav-link", {}).get("color", "rgb(0,0,0)")
    nav = parse_rgb(nav_css)
    if bg.get("current") in ("image", "video"):
        path = os.path.join(OUT, "assets", bg["path"]) if bg.get("path") else None
        need = header_scrim(path, bg.get("overlay-opacity"), nav)
        return round(max(need, SCRIM_FLOOR), 3), nav_css
    # flat colour behind the header
    base = parse_rgb(bg.get("color") or "rgb(255,255,255)")
    if ratio(luminance(nav), luminance(base)) >= TARGET:
        return 0.0, nav_css
    fixed, _ = darken_to_pass(nav, base)
    return 0.0, "rgb(%d, %d, %d)" % fixed

def render_header(active_pid):
    b = next((x for x in BLOCKS.values() if x.get("slot") == "header"), None)
    if not b: return ""
    s = b.get("settings") or {}
    st = s.get("styles") or {}
    bg = b.get("background") or {}
    d, m = b.get("desktop", {}) or {}, b.get("mobile", {}) or {}
    links = []
    for n in NAV:
        if n.get("isHidden"): continue
        pid = n.get("linkedPageId")
        p = PAGES.get(pid)
        if not p: continue
        cls = " active" if pid == active_pid else ""
        links.append(f'<a class="{cls.strip()}" href="{slug_url(pid)}">{H.escape(p.get("name",""))}</a>')
    logo = s.get("logoImagePath")
    ar = b.get("logoAspectRatio") or 1
    sticky = " sticky" if s.get("isSticky") else ""
    transparent = bool(bg.get("isTransparent"))
    bgc = "transparent" if transparent else bg.get("color", "transparent")
    if transparent and not s.get("isSticky"):
        HEADER_OVERLAY[0] = (d.get("height") or 0, m.get("height") or 0)
    css = f"""<style>
.site-header{{background:{bgc};{'position:absolute;top:0;left:0;right:0;' if transparent and not s.get('isSticky') else ''}}}
.header-inner{{max-width:{st.get('width','1240px')};padding:{st.get('padding','18px 16px')};
 min-height:{px(d.get('height'))};position:relative}}
.header-logo img{{width:{st.get('logo-width','270px')}}}
.nav{{gap:{st.get('link-spacing','32px')}}}
@media(max-width:{DESKTOP_MIN-1}px){{
.header-inner{{padding:{st.get('m-padding','0 16px')};min-height:{px(m.get('height'))}}}
.header-logo img{{width:{st.get('m-logo-width','140px')}}}
.nav{{gap:{st.get('m-link-spacing','20px')}}}
.nav a{{font-size:{STYLES.get('nav-link',{}).get('m-font-size','16px')}}}}}
</style>"""
    scrim, nav_colour = page_header_treatment(active_pid) if transparent else (0.0, STYLES.get("nav-link", {}).get("color", "rgb(0,0,0)"))
    # hold the full strength across the band where the logo and links sit,
    # then fade out so the header still melts into the page below
    scrim_el = (f'<div class="header-scrim" style="background:linear-gradient(180deg,'
                f'rgba(17,19,22,{scrim}) 0%,rgba(17,19,22,{scrim}) 74%,'
                f'rgba(17,19,22,{round(scrim*0.45,3)}) 90%,rgba(17,19,22,0) 100%)"></div>') if scrim else ""
    css += f"<style>.site-header{{--nav-link:{nav_colour};--nav-link-hover:{nav_colour}}}</style>"
    return (css + f'<header class="site-header{sticky}">{scrim_el}<div class="header-inner">'
            f'<a class="header-logo" href="/"><img src="{asset(logo)}" alt="OASis" '
            f'style="aspect-ratio:{ar}"></a>'
            f'<button class="burger" aria-label="Menu" onclick="document.querySelector(\'.nav\').classList.toggle(\'open\')">'
            f'<span></span><span></span><span></span></button>'
            f'<nav class="nav">{"".join(links)}</nav></div></header>')

def render_footer(form_counter):
    bid = next((k for k, v in BLOCKS.items() if v.get("slot") == "footer"), None)
    return f'<footer>{render_block(bid, form_counter)}</footer>' if bid else ""

# ---------------------------------------------------------------- page
JS = """
document.addEventListener('DOMContentLoaded',function(){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.08,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  document.querySelectorAll('form.gform').forEach(function(f){
    f.addEventListener('submit',function(ev){
      ev.preventDefault();var ok=true;
      f.querySelectorAll('.field').forEach(function(fd){
        var c=fd.querySelector('input,textarea');if(!c)return;
        var bad=(c.hasAttribute('required')&&!c.value.trim())||(c.type==='email'&&c.value&&!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(c.value));
        fd.classList.toggle('invalid',bad);if(bad)ok=false;});
      if(!ok)return;
      var fd=new FormData(f);
      fd.append('_page',location.pathname);
      var body=new URLSearchParams(fd).toString();
      var btn=f.querySelector('.submit'); if(btn){btn.disabled=true;btn.style.opacity=.6;}
      fetch(location.pathname,{method:'POST',
            headers:{'Content-Type':'application/x-www-form-urlencoded'},body:body})
        .then(function(r){if(!r.ok)throw 0;f.classList.add('sent');f.reset();})
        .catch(function(){f.classList.add('sent');f.reset();})
        .then(function(){if(btn){btn.disabled=false;btn.style.opacity=1;}});
    });
  });
  // background videos are decorative: fetch them only once their block is near
  var vids=document.querySelectorAll('video.block-bg');
  if(vids.length){
    var vio=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting)return;
        var v=e.target,s=v.querySelector('source[data-src]');
        if(s){s.src=s.dataset.src;s.removeAttribute('data-src');v.load();
              var pr=v.play();if(pr&&pr.catch)pr.catch(function(){});}
        vio.unobserve(v);
      });},{rootMargin:'400px 0px'});
    vids.forEach(function(v){vio.observe(v);});
  }
  document.querySelectorAll('.call-filter').forEach(function(bar){
    var grid=bar.parentElement.querySelector('.call-grid');
    var empty=bar.parentElement.querySelector('.call-empty');
    bar.addEventListener('click',function(ev){
      var btn=ev.target.closest('.chip'); if(!btn)return;
      var want=btn.dataset.country||'';
      bar.querySelectorAll('.chip').forEach(function(c){
        var on=c===btn; c.classList.toggle('is-on',on); c.setAttribute('aria-pressed',on);});
      var shown=0;
      grid.querySelectorAll('.call-card').forEach(function(card){
        var ok=!want||card.dataset.country===want;
        card.hidden=!ok; if(ok)shown++;});
      if(empty)empty.hidden=shown>0;
      try{history.replaceState(null,'',want?'?country='+encodeURIComponent(want):location.pathname+location.hash);}catch(e){}
    });
    var pre=new URLSearchParams(location.search).get('country');
    if(pre){var t=bar.querySelector('.chip[data-country="'+CSS.escape(pre)+'"]'); if(t)t.click();}
  });
  document.querySelectorAll('[data-lightbox]').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();
      var o=document.createElement('div');
      o.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:center;justify-content:center;padding:24px;cursor:zoom-out';
      var i=document.createElement('img');i.src=a.href;i.style.cssText='max-width:100%;max-height:100%;object-fit:contain';
      o.appendChild(i);o.onclick=function(){o.remove()};document.body.appendChild(o);});
  });
  var bar=document.getElementById('cookie-bar');
  function fitCookieBar(){
    if(!bar||!bar.classList.contains('show'))return;
    document.documentElement.style.setProperty('--cookie-h',(bar.offsetHeight+32)+'px');
  }
  try{ if(!localStorage.getItem('oasis-cookie')){bar.classList.add('show');document.body.classList.add('cookie-open');fitCookieBar();} }catch(e){}
  addEventListener('resize',fitCookieBar);
  document.querySelectorAll('#cookie-bar button').forEach(function(b){
    b.addEventListener('click',function(){try{localStorage.setItem('oasis-cookie',b.className)}catch(e){}
      bar.classList.remove('show');document.body.classList.remove('cookie-open');});
  });
});
"""

COOKIE = (f'<div id="cookie-bar"><span>{H.escape(DATA.get("cookieBannerDisclaimer") or "We use cookies to improve your experience on our website.")}</span>'
          f'<span style="display:flex;gap:10px"><button class="decline">{H.escape(DATA.get("cookieBannerDeclineText") or "Decline")}</button>'
          f'<button class="accept">{H.escape(DATA.get("cookieBannerAcceptText") or "Accept")}</button></span></div>')

def render_page(pid):
    p = PAGES[pid]
    meta = p.get("meta") or {}
    title = meta.get("title") or p.get("name") or "OASis"
    desc  = meta.get("description") or ""
    kw    = ", ".join(meta.get("keywords") or [])
    fav   = asset(META.get("faviconPath"))
    og    = asset(META.get("ogImagePath"))
    fc = [0]
    hdr = render_header(pid)          # sets HEADER_OVERLAY
    blks = p.get("blocks") or []
    body = "".join(render_block(b, fc, is_first=(i == 0)) for i, b in enumerate(blks))
    canonical = "https://theoasisproject.eu/" + ("" if pid == HOME else p["slug"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<meta name="keywords" content="{H.escape(kw)}">
<link rel="canonical" href="{H.escape(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:image" content="{og}">
<meta property="og:url" content="{H.escape(canonical)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{fav}">
<link rel="apple-touch-icon" href="{fav}">
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
{hdr}
<main>{body}</main>
{render_footer([100])}
{COOKIE}
<script>{JS}</script>
</body>
</html>
"""

def main():
    os.makedirs(OUT, exist_ok=True)
    css = global_css()
    # element positioning must come after the per-block <style> tags -> keep in styles.css
    css += f"""
@media(min-width:{DESKTOP_MIN}px){{
.el{{top:var(--dt);left:var(--dl);width:var(--dw);height:var(--dh)}}
.el-text{{height:auto;min-height:var(--dh)}}
.el-text [style*="--fontSizeDesktop"],.call-card__caption [style*="--fontSizeDesktop"]{{font-size:var(--fontSizeDesktop)}}
.el-text [style*="--lineHeightDesktop"],.call-card__caption [style*="--lineHeightDesktop"]{{line-height:var(--lineHeightDesktop)}}
}}
@media(max-width:{DESKTOP_MIN-1}px){{
.el{{top:var(--mt);left:var(--ml);width:var(--mw);height:var(--mh)}}
.el-text{{height:auto;min-height:var(--mh)}}
.el-text [style*="--fontSizeMobile"],.call-card__caption [style*="--fontSizeMobile"]{{font-size:var(--fontSizeMobile)}}
.el-text [style*="--lineHeightMobile"],.call-card__caption [style*="--lineHeightMobile"]{{line-height:var(--lineHeightMobile)}}
}}
@media(max-width:1100px){{.call-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:700px){{
.call-grid{{grid-template-columns:1fr;gap:16px}}
.call-filter{{padding-top:92px;gap:8px;margin-bottom:20px}}
.chip{{font-size:14px;padding:9px 14px}}
.call-card__caption{{padding:40px 14px 12px}}
.call-card__caption>*{{font-size:17px}}
.has-grid{{padding-bottom:48px!important}}
}}
"""
    open(os.path.join(OUT, "styles.css"), "w", encoding="utf-8").write(css)
    n = 0
    for pid, p in PAGES.items():
        if not p.get("blocks"): continue
        fn = "index.html" if pid == HOME else f"{p['slug']}.html"
        open(os.path.join(OUT, fn), "w", encoding="utf-8").write(render_page(pid))
        n += 1
    # 404 + sitemap
    urls = "".join(f"<url><loc>https://theoasisproject.eu/{'' if pid==HOME else PAGES[pid]['slug']}</loc></url>"
                   for pid in PAGES if PAGES[pid].get("blocks"))
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(
        "User-agent: *\nAllow: /\nSitemap: https://theoasisproject.eu/sitemap.xml\n")
    print(f"built {n} pages -> {OUT}")

if __name__ == "__main__":
    main()
