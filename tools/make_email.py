#!/usr/bin/env python3
"""Build the Turkish e-mail edition of the bulletin from index.html.

Usage: python3 make_email.py index.html out.html [--logo]
  --logo  include the logo as an inline image (cid:att0). When used, send the
          logo file as the FIRST attachment with inline=true.
Prints the e-mail subject line to stdout.
Table-based layout with inline styles only (works in Outlook desktop and Gmail).
"""
import html, json, re, sys

src, out = sys.argv[1], sys.argv[2]
use_logo = "--logo" in sys.argv[3:]
FULL = "--full" in sys.argv[3:]  # varsayılan: yalnızca günün özeti + pano butonu
URL = "https://peli-tedarik-bulteni.tlnygkr-f22.workers.dev/"
page = open(src, encoding="utf-8").read()
m = re.search(r'<script id="bulletin-data" type="application/json">(.*?)</script>', page, re.S)
D = json.loads(m.group(1))
e = html.escape

# Palette
INK, MUTED, FAINT = "#1B2125", "#5D6672", "#8A929C"
PAPER, CARD, RULE = "#F4F1EA", "#FFFFFF", "#E4DFD5"
BRAND, BRAND_DARK, BRAND_SOFT = "#0E6B5C", "#0B3D36", "#E5F1EE"
SANS = "Arial, Helvetica, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
CATS = {  # label, accent colour
    "geo": ("Jeopolitik", "#B42318"),
    "logistics": ("Lojistik & Navlun", "#0E6B5C"),
    "energy": ("Enerji", "#B7791F"),
    "trade": ("Ticaret Politikası", "#2F5BB7"),
    "turkey": ("Türkiye", "#C8102E"),
    "materials": ("Hammadde", "#6B4E9B"),
}
ARROW = {"up": ("&#9650;", "#B42318"), "down": ("&#9660;", "#0E6B5C"), "flat": ("&#9632;", FAINT)}
ed = D["edition"]


def section(title):
    return (f'<tr><td style="padding:28px 0 10px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td style="font:bold 11px {SANS};letter-spacing:2px;text-transform:uppercase;color:{MUTED};white-space:nowrap;padding-right:12px">{e(title)}</td>'
            f'<td width="100%" style="border-bottom:1px solid {RULE};font-size:1px;line-height:1px">&nbsp;</td></tr></table></td></tr>')


rows = []

# Header band
logo_cell = (f'<td valign="middle" style="padding:0 18px 0 0"><img src="cid:att0" alt="Peli" width="79" height="56" style="display:block;width:79px;height:56px;border:0;border-radius:6px"></td>'
             if use_logo else "")
rows.append(
    f'<tr><td bgcolor="{BRAND_DARK}" style="background:{BRAND_DARK};padding:26px 28px 22px;border-radius:12px 12px 0 0">'
    f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{logo_cell}'
    f'<td valign="middle"><div style="font:bold 11px {SANS};letter-spacing:2px;text-transform:uppercase;color:#9FD3C7">Satın Alma &amp; Tedarik Zinciri</div>'
    f'<div style="font:bold 27px/1.15 {SERIF};color:#FFFFFF;padding-top:4px">Tedarik Zinciri Günlük Bülteni</div></td></tr></table>'
    f'<div style="font:13px {SANS};color:#C9DED9;padding-top:14px"><b style="color:#FFFFFF">{e(ed["date"]["tr"])}</b> &nbsp;&middot;&nbsp; {e(ed["slot"]["tr"])} &nbsp;&middot;&nbsp; {e(ed["generated"]["tr"])}</div>'
    f'</td></tr>')
# Lede
rows.append(
    f'<tr><td bgcolor="{CARD}" style="background:{CARD};padding:22px 28px;border:1px solid {RULE};border-top:0;border-radius:0 0 12px 12px">'
    f'<div style="font:bold 11px {SANS};letter-spacing:2px;text-transform:uppercase;color:{BRAND};padding-bottom:6px">Günün özeti</div>'
    f'<div style="font:18px/1.5 {SERIF};color:{INK}">{e(D["lede"]["tr"])}</div></td></tr>')

# Risk barometer
LEVEL = {"green": ("Düşük", "#1E7B4F", "#E3F2EA"), "amber": ("Orta", "#9A5B00", "#FFF0D2"), "red": ("Yüksek", "#B42318", "#FBE4E1")}
TREND = {"up": "&#8599; artıyor", "down": "&#8600; azalıyor", "flat": "&#8594; sabit"}
if D.get("risk"):
    rows.append(section("Risk barometresi"))
    cells = []
    for r in D["risk"]:
        lv, fg, bg = LEVEL.get(r.get("level"), LEVEL["amber"])
        cells.append(
            f'<td width="20%" valign="top" style="padding:3px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE};border-top:4px solid {fg};border-radius:8px;padding:10px 10px 11px">'
            f'<div style="font:bold 12px {SANS};color:{INK}">{e(r["area"]["tr"])}</div>'
            f'<div style="padding:6px 0 4px"><span style="display:inline-block;font:bold 11px {SANS};color:{fg};background:{bg};border-radius:999px;padding:2px 9px">{lv}</span></div>'
            f'<div style="font:11px {SANS};color:{MUTED}">{TREND.get(r.get("trend"), TREND["flat"])}</div>'
            f'<div style="font:11px/1.4 {SANS};color:{FAINT};padding-top:4px">{e(r.get("note", {}).get("tr", ""))}</div>'
            f'</td></tr></table></td>')
    rows.append(f'<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{"".join(cells)}</tr></table></td></tr>')

# What it means for us — actions
TAG = {"today": ("BUGÜN", "#FFFFFF", "#B42318"), "week": ("BU HAFTA", "#FFFFFF", "#B7791F"), "watch": ("İZLE", "#FFFFFF", "#2F5BB7")}
A = D.get("actions") or {}
if A.get("abroad") or A.get("domestic"):
    rows.append(section("Bizim için ne anlama geliyor"))
    for key, title in (("abroad", "Yurt dışı alımlar"), ("domestic", "Yurt içi alımlar")):
        items = A.get(key) or []
        if not items:
            continue
        lis = ""
        for it in items:
            tg, fg, bg = TAG.get(it.get("tag"), TAG["watch"])
            ref = (f' <span style="font:11px {SANS};color:{FAINT};white-space:nowrap">&middot; Haber {int(it["ref"]) + 1:02d}</span>'
                   if isinstance(it.get("ref"), int) else "")
            lis += (f'<tr><td valign="top" width="84" style="padding:9px 10px 9px 0;border-top:1px solid {RULE}">'
                    f'<span style="display:inline-block;font:bold 10px {SANS};letter-spacing:.8px;color:{fg};background:{bg};border-radius:4px;padding:3px 7px;white-space:nowrap">{tg}</span></td>'
                    f'<td valign="top" style="padding:9px 0;border-top:1px solid {RULE};font:14px/1.5 {SANS};color:{INK}">{e(it["tr"])}{ref}</td></tr>')
        rows.append(
            f'<tr><td style="padding:0 0 10px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE};border-radius:10px;padding:14px 18px 8px">'
            f'<div style="font:bold 16px {SERIF};color:{BRAND_DARK};padding-bottom:8px">{title}</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{lis}</table></td></tr></table></td></tr>')

# Figures
def tile_grid(items):
    cells = []
    for f in items:
        sym, col = ARROW.get(f.get("dir"), ARROW["flat"])
        cells.append(
            f'<td width="33%" valign="top" style="padding:4px"><a href="{e(f.get("url", URL))}" style="text-decoration:none;color:{INK}">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE};border-radius:10px;padding:12px 14px">'
            f'<div style="font:12px {SANS};color:{MUTED}">{e(f["label"]["tr"])}</div>'
            f'<div style="font:bold 22px {SANS};color:{INK};padding:3px 0 2px">{e(f["value"]["tr"])}</div>'
            f'<div style="font:12px {SANS};color:{col}">{sym} {e(f["change"]["tr"])}</div>'
            f'<div style="font:11px {SANS};color:{FAINT};padding-top:2px">{e(f["asof"]["tr"])}</div>'
            f'</td></tr></table></a></td>')
    while len(cells) % 3:
        cells.append('<td width="33%" style="padding:4px"></td>')
    grid = "".join("<tr>" + "".join(cells[i:i + 3]) + "</tr>" for i in range(0, len(cells), 3))
    return f'<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{grid}</table></td></tr>'


rows.append(section("Göstergeler"))
rows.append(tile_grid(D.get("figures", [])))
if D.get("metals"):
    rows.append(section("Metal ve hurda fiyatları"))
    rows.append(tile_grid(D["metals"]))

# Calendar
rows.append(section("Yaklaşan tarihler"))
cal = "".join(
    f'<tr><td valign="top" style="padding:10px 14px;border-bottom:1px solid {RULE};white-space:nowrap">'
    f'<span style="display:inline-block;font:bold 12px {SANS};color:{BRAND_DARK};background:{BRAND_SOFT};border-radius:6px;padding:4px 9px">{e(c["date"]["tr"])}</span></td>'
    f'<td style="padding:10px 14px 10px 0;border-bottom:1px solid {RULE};font:14px/1.5 {SANS};color:{INK}">{e(c["text"]["tr"])}</td></tr>'
    for c in D.get("calendar", []))
rows.append(f'<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE};border-radius:10px">{cal}</table></td></tr>')

# Stories
rows.append(section("Öne çıkanlar"))
for i, s in enumerate(D.get("stories", []), 1):
    t = s["tr"]
    label, col = CATS.get(s.get("cat"), (s.get("cat", ""), BRAND))
    pri = (f' &nbsp;<span style="display:inline-block;font:bold 10px {SANS};letter-spacing:1px;color:#FFFFFF;background:#B42318;border-radius:999px;padding:2px 8px">ÖNCELİKLİ</span>'
           if s.get("priority") else "")
    srcs = " &nbsp;&middot;&nbsp; ".join(f'<a href="{e(x["url"])}" style="color:{BRAND};text-decoration:none">{e(x["name"])}</a>' for x in s.get("sources", []))
    rows.append(
        f'<tr><td style="padding:0 0 12px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
        f'<td width="5" bgcolor="{col}" style="background:{col};border-radius:10px 0 0 10px;font-size:1px">&nbsp;</td>'
        f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE};border-left:0;border-radius:0 10px 10px 0;padding:18px 20px">'
        f'<div style="font:bold 11px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:{col}">{i:02d} &nbsp;{e(label)}{pri}</div>'
        f'<div style="font:bold 19px/1.3 {SERIF};color:{INK};padding:6px 0 8px">{e(t["title"])}</div>'
        f'<div style="font:14px/1.6 {SANS};color:#2E363C">{e(t["summary"])}</div>'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px"><tr>'
        f'<td bgcolor="{BRAND_SOFT}" style="background:{BRAND_SOFT};border-radius:8px;padding:11px 14px;font:14px/1.5 {SANS};color:{INK}">'
        f'<div style="font:bold 11px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:{BRAND};padding-bottom:3px">&#8594; Bizim için ne anlama geliyor</div>{e(t["impact"])}</td></tr></table>'
        f'<div style="font:12px {SANS};color:{FAINT};padding-top:10px">Kaynaklar: {srcs}</div>'
        f'</td></tr></table></td></tr>')

# Özet e-posta: başlık + günün özeti, ardından doğrudan pano butonu
if not FULL:
    rows = rows[:2]

# Button + footer
rows.append(
    f'<tr><td align="center" style="padding:24px 0 8px"><table role="presentation" cellpadding="0" cellspacing="0"><tr>'
    f'<td bgcolor="{BRAND_DARK}" style="background:{BRAND_DARK};border-radius:8px">'
    f'<a href="{URL}" style="display:inline-block;background:{BRAND_DARK};color:#FFFFFF;border:1px solid {BRAND_DARK};'
    f'font:bold 16px {SANS};text-decoration:none;padding:14px 34px;border-radius:8px">Bülten panosuna git &rarr;</a></td></tr></table></td></tr>')
rows.append(
    f'<tr><td align="center" style="padding:14px 10px 0;font:12px/1.6 {SANS};color:{FAINT}">'
    f'Hafta içi her gün 08:00 ve 17:00\'da otomatik hazırlanır. Kamuya açık kaynaklardan derlenir; kritik rakamları karar öncesinde kaynağından teyit edin.</td></tr>')

doc = (f'<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>'
       f'<body style="margin:0;padding:0;background:{PAPER}">'
       f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{PAPER}" style="background:{PAPER}"><tr><td align="center" style="padding:24px 12px">'
       f'<table role="presentation" width="640" cellpadding="0" cellspacing="0" style="width:100%;max-width:640px">'
       + "".join(rows) +
       '</table></td></tr></table></body></html>')
open(out, "w", encoding="utf-8").write(doc)
print(f'Tedarik Zinciri Bülteni · {ed["date"]["tr"]} · {ed["slot"]["tr"]}')
