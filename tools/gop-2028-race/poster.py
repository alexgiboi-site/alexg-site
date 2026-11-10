"""Render the Vance vs Rubio fight-card poster in EN/IT/RO, desktop and mobile, plus a share card."""
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

from pathlib import Path
OUT = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[2] / 'public/library/gop-2028-race')

T = {
 'en': dict(
  kicker='THE 2028 REPUBLICAN NOMINATION · AFTER THE MIDTERMS',
  vrole='JD Vance · Vice President · Ohio', rrole='Marco Rubio · Secretary of State · Florida',
  rows=[('34%', 'MARKET ODDS · KALSHI, 9 NOV', '21%'),
        ('39%', 'NATIONAL POLLS · 60-DAY AVERAGE', '18%'),
        ('38%', 'NEW HAMPSHIRE · ST ANSELM, OCT', '38%')],
  tag='LATE CHALLENGER', badge='from about 5% before the midterms to 17% on Kalshi',
  foot='Odds: Kalshi via DeFi Rate, 9 Nov 2026 · National polls: PollCheck 60-day average to 31 Oct 2026 · New Hampshire: Saint Anselm College, 19–20 Oct 2026 · alexgiboi.com/library'),
 'it': dict(
  kicker='LA NOMINATION REPUBBLICANA DEL 2028 · DOPO IL VOTO DI METÀ MANDATO',
  vrole='JD Vance · vicepresidente · Ohio', rrole='Marco Rubio · segretario di Stato · Florida',
  rows=[('34%', 'MERCATI DI PREVISIONE · KALSHI, 9 NOV', '21%'),
        ('39%', 'SONDAGGI NAZIONALI · MEDIA A 60 GIORNI', '18%'),
        ('38%', 'NEW HAMPSHIRE · ST ANSELM, OTT', '38%')],
  tag='LO SFIDANTE', badge='da circa il 5% prima del voto al 17% su Kalshi',
  foot='Quote: Kalshi tramite DeFi Rate, 9 nov 2026 · Sondaggi nazionali: media PollCheck a 60 giorni al 31 ott 2026 · New Hampshire: Saint Anselm College, 19–20 ott 2026 · alexgiboi.com/library'),
 'ro': dict(
  kicker='CANDIDATURA REPUBLICANĂ PENTRU 2028 · DUPĂ ALEGERILE DE LA JUMĂTATEA MANDATULUI',
  vrole='JD Vance · vicepreședinte · Ohio', rrole='Marco Rubio · secretar de stat · Florida',
  rows=[('34%', 'PIEȚE DE PREDICȚII · KALSHI, 9 NOI', '21%'),
        ('39%', 'SONDAJE NAȚIONALE · MEDIE PE 60 DE ZILE', '18%'),
        ('38%', 'NEW HAMPSHIRE · ST ANSELM, OCT', '38%')],
  tag='INTRĂ ÎN RING', badge='de la circa 5% înainte de vot la 17% pe Kalshi',
  foot='Cote: Kalshi, prin DeFi Rate, 9 nov. 2026 · Sondaje naționale: media PollCheck pe 60 de zile, la 31 oct. 2026 · New Hampshire: Saint Anselm College, 19–20 oct. 2026 · alexgiboi.com/library'),
}

BLUE, ORANGE, GROUND, GREY = '#7CC4E8', '#F5A25D', '#0D1B2A', '#A9B4C2'

BELT = '''<svg aria-hidden="true" width="{w}" height="{h}" viewBox="0 0 380 120">
<rect x="0" y="38" width="380" height="44" rx="14" fill="#B8901F" stroke="#6E540E" stroke-width="3"/>
<circle cx="78" cy="60" r="26" fill="#E5C55A" stroke="#6E540E" stroke-width="3"/>
<circle cx="302" cy="60" r="26" fill="#E5C55A" stroke="#6E540E" stroke-width="3"/>
<ellipse cx="190" cy="60" rx="78" ry="56" fill="#E9CC66" stroke="#6E540E" stroke-width="4"/>
<ellipse cx="190" cy="60" rx="62" ry="42" fill="none" stroke="#6E540E" stroke-width="2"/>
<text x="190" y="75" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="38" fill="#0D1B2A">2028</text>
</svg>'''

CSS = f'''
*{{box-sizing:border-box}} body{{margin:0}}
.p{{position:relative;overflow:hidden;background:{GROUND};color:#F4F6F8;font-family:Inter,sans-serif}}
.abs{{position:absolute;left:0;right:0}}
.k{{text-align:center;font-weight:600;color:{GREY};margin:0 auto}}
.name{{font-family:"Inter Display";font-weight:900;line-height:1;letter-spacing:-0.02em}}
.vs{{border:3px solid #F4F6F8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:"Inter Display";font-weight:900}}
.role{{color:{GREY}}}
.row{{display:grid;align-items:center;border-top:1px solid #2B3A4E;padding-top:4px}}
.num{{font-family:"Inter Display";font-weight:800}}
.lab{{text-align:center;font-weight:600;color:{GREY};line-height:1.5}}
.badge{{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;background:{GROUND};border:2px solid #F4F6F8;border-radius:40px}}
.tag{{font-weight:800;color:{GROUND};background:#F4F6F8;border-radius:6px;padding:4px 10px}}
.ds{{font-family:"Inter Display";font-weight:900}}
.bt{{color:#D3DAE3}}
.foot{{text-align:center;color:{GREY};margin:0 auto}}
'''

def ropes(w, top, posts_h, pad=70):
    y = [top + 40, top + 85, top + 130]
    lines = ''.join(f'<line x1="{pad+26}" y1="{v}" x2="{w-pad-26}" y2="{v}" stroke="#F4F6F8" stroke-opacity="0.22" stroke-width="7"/>' for v in y)
    return (f'<svg aria-hidden="true" class="abs" style="top:0" width="{w}" height="{top+posts_h+40}">'
            f'<rect x="{pad}" y="{top}" width="26" height="{posts_h}" rx="6" fill="#2B3A4E"/>'
            f'<rect x="{w-pad-26}" y="{top}" width="26" height="{posts_h}" rx="6" fill="#2B3A4E"/>{lines}'
            f'<rect x="{pad-8}" y="{top+30}" width="42" height="110" rx="8" fill="{BLUE}" fill-opacity="0.85"/>'
            f'<rect x="{w-pad-34}" y="{top+30}" width="42" height="110" rx="8" fill="{ORANGE}" fill-opacity="0.85"/></svg>')

def tape(t, top, left, width, mid, numsz, labsz, ls, br=False):
    rows = ''.join(
        f'<div class="row" style="grid-template-columns:1fr {mid}px 1fr">'
        f'<div class="num" style="text-align:right;font-size:{numsz}px;color:{BLUE}">{a}</div>'
        f'<div class="lab" style="font-size:{labsz}px;letter-spacing:{ls}px">{l.replace(" · ", "<br>") if br else l}</div>'
        f'<div class="num" style="text-align:left;font-size:{numsz}px;color:{ORANGE}">{b}</div></div>'
        for a, l, b in t['rows'])
    return f'<div style="position:absolute;top:{top}px;left:{left}px;width:{width}px;display:flex;flex-direction:column;gap:2px">{rows}</div>'

def badge(t, top, size, txt, wrap_w=None):
    w = f'max-width:{wrap_w}px;' if wrap_w else ''
    return (f'<div class="abs" style="top:{top}px;display:flex;justify-content:center">'
            f'<div class="badge" style="{w}gap:8px 16px;padding:12px 30px">'
            f'<span class="tag" style="font-size:{size-4}px;letter-spacing:3px">{t["tag"]}</span>'
            f'<span class="ds" style="font-size:{size+10}px">RON DESANTIS</span>'
            f'<span class="bt" style="font-size:{txt}px">{t["badge"]}</span></div></div>')

def desktop(t, W=1600, H=800):
    return f'''<div class="p" style="width:{W}px;height:{H}px">
{ropes(W, H-215, 180)}
<div class="abs" style="top:30px"><div class="k" style="font-size:17px;letter-spacing:5px;max-width:1500px">{t["kicker"]}</div></div>
<div class="abs" style="top:58px;display:flex;justify-content:center">{BELT.format(w=320, h=101)}</div>
<div class="abs" style="top:168px;display:grid;grid-template-columns:1fr 150px 1fr;align-items:center">
 <div class="name" style="text-align:right;font-size:148px;color:{BLUE}">VANCE</div>
 <div style="display:flex;justify-content:center"><div class="vs" style="width:88px;height:88px;font-size:36px">VS</div></div>
 <div class="name" style="text-align:left;font-size:148px;color:{ORANGE}">RUBIO</div></div>
<div class="abs role" style="top:330px;display:grid;grid-template-columns:1fr 150px 1fr;font-size:19px">
 <div style="text-align:right">{t["vrole"]}</div><div></div><div>{t["rrole"]}</div></div>
{tape(t, 372, 230, W-460, 520, 46, 14, 3)}
{badge(t, H-180, 18, 18)}
<div class="abs" style="top:{H-34}px"><div class="foot" style="font-size:13px;max-width:1500px">{t["foot"]}</div></div>
</div>'''

def mobile(t, W=1000, H=1250):
    def role(r, align):
        n, rest = r.split(' · ', 1)
        return f'<div class="role" style="text-align:{align};font-size:22px;line-height:1.4"><div style="color:#F4F6F8;font-weight:600">{n}</div><div>{rest}</div></div>'
    return f'''<div class="p" style="width:{W}px;height:{H}px">
{ropes(W, 870, 200, 40)}
<div class="abs" style="top:40px"><div class="k" style="font-size:20px;letter-spacing:4px;max-width:880px;line-height:1.5">{t["kicker"]}</div></div>
<div class="abs" style="top:128px;display:flex;justify-content:center">{BELT.format(w=380, h=120)}</div>
<div class="abs" style="top:300px;display:grid;grid-template-columns:1fr 96px 1fr;align-items:center;padding:0 24px">
 <div class="name" style="text-align:right;font-size:112px;color:{BLUE}">VANCE</div>
 <div style="display:flex;justify-content:center"><div class="vs" style="width:72px;height:72px;font-size:28px">VS</div></div>
 <div class="name" style="text-align:left;font-size:112px;color:{ORANGE}">RUBIO</div></div>
<div class="abs" style="top:432px;display:grid;grid-template-columns:1fr 96px 1fr;padding:0 24px">
 {role(t["vrole"], "right")}<div></div>{role(t["rrole"], "left")}</div>
{tape(t, 540, 40, W-80, 400, 70, 17, 2, True)}
{badge(t, 900, 22, 22, 900)}
<div class="abs" style="top:1148px"><div class="foot" style="font-size:16px;max-width:900px;line-height:1.5">{t["foot"]}</div></div>
</div>'''

def render(page, html, w, h, path, size=None, fmt='WEBP'):
    page.set_viewport_size({'width': w, 'height': h})
    page.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{html}</body></html>')
    page.wait_for_timeout(150)
    page.screenshot(path='/tmp/_p.png', clip={'x': 0, 'y': 0, 'width': w, 'height': h})
    im = Image.open('/tmp/_p.png').convert('RGB')
    if size:
        im = im.resize(size, Image.LANCZOS)
    if fmt == 'WEBP':
        im.save(path, 'WEBP', quality=88, method=6)
    else:
        im.save(path, 'JPEG', quality=88, optimize=True, progressive=True)
    # overflow report
    over = page.evaluate("""[...document.querySelectorAll('div,span')].filter(e=>e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='hidden').map(e=>e.textContent.trim().slice(0,30))""")
    if over: print('OVERFLOW', path, over)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg = b.new_page()
    for l, t in T.items():
        render(pg, desktop(t), 1600, 800, f'{OUT}/hero-{l}.webp')
        render(pg, mobile(t), 1000, 1250, f'{OUT}/hero-m-{l}.webp')
    # share card: 1600x840 layout scaled to 1200x630
    render(pg, desktop(T['en'], 1600, 840), 1600, 840, f'{OUT}/share-card.jpg', (1200, 630), 'JPEG')
    b.close()
print('done')
