"""Build public/library/gop-2028-race/index.html (EN/IT/RO) in the format of the other Library posts."""
import re

from pathlib import Path
SITE = str(Path(__file__).resolve().parents[2] / 'public')
SLUG = 'gop-2028-race'
src = open(f'{SITE}/library/us-midterms-2026/index.html', encoding='utf-8').read()
base_css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
# keep the shared article styles, drop the map-specific block of the midterms post
base_css = base_css.split('.mapfig{')[0]
nav = re.search(r'(<nav aria-label="Site".*?</nav>)', src, re.S).group(1)
lang_script = re.search(r'(<script>\n\(function \(\) \{\n  var OK.*?</script>)', src, re.S).group(1).replace('midterms-lang', 'gop2028-lang')
analytics = re.search(r'(<!-- Cloudflare Web Analytics -->.*?<!-- End Cloudflare Web Analytics -->)', src, re.S).group(1)

EXTRA_CSS = '''
.c-v{fill:var(--s1);stroke:var(--s1)}.c-r{fill:var(--s2);stroke:var(--s2)}.c-d{fill:var(--muted);stroke:var(--muted)}
.chart .soft{fill-opacity:.35;stroke:none}.chart .solid{stroke:none}
.chart .link{stroke:var(--rule);stroke-width:4;stroke-linecap:round}
.chart .ln{fill:none;stroke-width:3}
.chart .base{stroke:var(--rule);stroke-width:1}
.chart .vlab{font:12px var(--sans);fill:var(--muted)}
.chart .vlab.b{font-weight:600;fill:var(--ink)}
.chart .end{font:600 13px var(--sans)}
.chart .end.c-v,.chart .end.c-r{stroke:none}
.ct{font:600 16px/1.35 var(--sans);margin-bottom:2px}
.cs{font:14px/1.4 var(--sans);color:var(--muted);margin-bottom:6px}
.legend .dot{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--ink);vertical-align:-1px;margin-right:6px}
.legend .dot.soft{opacity:.3}
@media (max-width:600px){.chart .vlab,.chart .end,.chart .lbl{font-size:21px}.chart .ax{font-size:16px}}
'''

def pct(v, l):
    s = f'{v:g}'
    return (s.replace('.', ',') if l != 'en' else s) + '%'

def chart_markets(l, L):
    rows = [('JD Vance', 'v', 45, 31), ('Marco Rubio', 'r', 18, 23), ('Ron DeSantis', 'd', 4.3, 20)]
    x = lambda v: 170 + v / 50 * 560
    g = []
    for i, (n, c, a, b) in enumerate(rows):
        y = 44 + i * 62
        g.append(f'<g><text class="lbl" x="152" y="{y+5}" text-anchor="end">{n}</text>'
                 f'<line class="link" x1="{x(a):.1f}" y1="{y}" x2="{x(b):.1f}" y2="{y}"/>'
                 f'<circle class="c-{c} soft" cx="{x(a):.1f}" cy="{y}" r="9"><title>{n}, {L["d1"]}: {pct(a,l)}</title></circle>'
                 f'<circle class="c-{c} solid" cx="{x(b):.1f}" cy="{y}" r="9"><title>{n}, {L["d2"]}: {pct(b,l)}</title></circle>'
                 f'<text class="vlab" x="{x(a):.1f}" y="{y-17}" text-anchor="middle">{pct(a,l)}</text>'
                 f'<text class="vlab b" x="{x(b):.1f}" y="{y-17}" text-anchor="middle">{pct(b,l)}</text></g>')
    return (f'<figure><div class="ct">{L["c1t"]}</div><div class="cs">{L["c1s"]}</div>'
            f'<div class="legend"><span><i class="dot soft"></i>{L["d1"]}</span><span><i class="dot"></i>{L["d2l"]}</span></div>'
            f'<svg class="chart" viewBox="0 0 760 196" role="img" aria-label="{L["c1t"]}">{"".join(g)}</svg>'
            f'<figcaption>{L["c1c"]}</figcaption></figure>')

def chart_nh(l, L):
    polls = [('UNH', 53, 7), ('St Anselm', 46, 27), ('St Anselm', 37, 30), ('UNH', 36, 26), ('St Anselm', 38, 36), ('St Anselm', 38, 38)]
    xs = lambda i: 74 + i * 112
    y = lambda v: 250 - v / 60 * 210
    out = [f'<line class="base" x1="40" y1="250" x2="660" y2="250"/>']
    for k, (n, c) in enumerate([('JD Vance', 'v'), ('Marco Rubio', 'r')]):
        vals = [p[1 + k] for p in polls]
        pts = ' '.join(f'{xs(i)},{y(v):.1f}' for i, v in enumerate(vals))
        out.append(f'<polyline class="ln c-{c}" style="fill:none" points="{pts}"/>')
        for i, v in enumerate(vals):
            out.append(f'<circle class="c-{c} solid" cx="{xs(i)}" cy="{y(v):.1f}" r="5"><title>{n}, {L["months"][i]} 2026 ({polls[i][0]}): {v}%</title></circle>')
        out.append(f'<text class="vlab b" x="{xs(0)-12}" y="{y(vals[0])+5:.1f}" text-anchor="end">{vals[0]}%</text>')
        ly = y(vals[-1]) - 12 if c == 'v' else y(vals[-1]) + 24
        out.append(f'<text class="end c-{c}" x="{xs(5)+14}" y="{ly:.1f}">{n.split()[-1]} {vals[-1]}%</text>')
    for i, p in enumerate(polls):
        out.append(f'<text class="lbl" x="{xs(i)}" y="274" text-anchor="middle">{L["months"][i]}</text>'
                   f'<text class="ax" x="{xs(i)}" y="292" text-anchor="middle">{p[0]}</text>')
    return (f'<figure><div class="ct">{L["c2t"]}</div><div class="cs">{L["c2s"]}</div>'
            f'<svg class="chart" viewBox="0 0 760 300" role="img" aria-label="{L["c2t"]}">{"".join(out)}</svg>'
            f'<figcaption>{L["c2c"]}</figcaption></figure>')

def org(kind, href, text):
    return f'<a class="org org-{kind}" href="{href}" target="_blank" rel="noopener">{text}</a>'

K = org('fc', 'https://kalshi.com', 'Kalshi')
PM = org('fc', 'https://polymarket.com', 'Polymarket')
PC = org('poll', 'https://www.pollcheck.co.uk/us/primaries/republican/', 'PollCheck')
SA = org('poll', 'https://www.anselm.edu', 'Saint Anselm College')
EM = org('poll', 'https://emersoncollegepolling.com', 'Emerson College')
FOX = org('news', 'https://www.foxnews.com/politics/trump-told-donors-we-need-elect-jd-source-confirms-weighs-vance-rubio-2028.amp', 'Fox News')

SOURCES = '''<ol class="sources">
<li><b>Prediction-market prices, 4 October and 4 November 2026.</b> <a href="https://defirate.com/prediction-markets/republican-presidential-nominee-odds/">DeFi Rate (Kalshi and Polymarket, observed 4 November)</a>; <a href="https://defirate.com/odds/republican-nominee/">DeFi Rate (Kalshi, 4 October)</a>; <a href="https://www.tampafp.com/vp-vances-2028-odds-slip-after-midterm-shellacking-florida-gov-desantis-surges-on-prediction-markets/">Tampa Free Press (Kalshi, 3–4 November; DeSantis interview on SiriusXM)</a>; <a href="https://news.kalshi.com/p/2026-midterms-recap-the-mega-mega-blue-tsunami">Kalshi midterms recap</a>.</li>
<li><b>DeSantis on the midterm result.</b> <a href="https://www.newsweek.com/ron-desantis-issues-dire-prediction-for-gop-after-stunning-midterm-defeat-12666035">Newsweek</a>.</li>
<li><b>Polls.</b> <a href="https://www.pollcheck.co.uk/us/primaries/republican/">PollCheck, national Republican primary average (11 polls, 60 days to 31 October 2026)</a>; <a href="https://www.pollcheck.co.uk/us/primaries/republican/new-hampshire/">PollCheck, New Hampshire polls (University of New Hampshire; Saint Anselm College)</a>; <a href="https://www.abc27.com/news/top-stories/marco-rubio-jd-vance-virtually-tied-in-2028-presidential-primary-poll-emerson-college-polling/amp/">abc27 (Emerson College poll, May 2026)</a>.</li>
<li><b>Trump, Vance and Rubio on 2028.</b> <a href="https://www.foxnews.com/politics/poll-complicates-vance-status-trump-likely-2028-heir-apparent.print">Fox News (Vance–Rubio ticket; Rubio backing Vance)</a>; <a href="https://www.foxnews.com/politics/trump-told-donors-we-need-elect-jd-source-confirms-weighs-vance-rubio-2028.amp">Fox News (Trump’s remark to donors; Vance’s plans after the midterms)</a>; <a href="https://www.jpost.com/american-politics/article-885672">Jerusalem Post (Reuters)</a>; <a href="https://digital-release.cbs42.com/?p=2047668">CBS 42 (endorsement expected after the midterms)</a>; <a href="https://arynews.tv/us-vp-vance-campaigns-hometown-eye-on-2028">ARY News (AFP)</a>; <a href="https://gulfnews.com/amp/story/world%2Famericas%2Fvance-2028-buzz-grows-but-midterms-could-sting-1.500705402">Gulf News (AFP, RNC finance role)</a>.</li>
<li><b>Closeness to Trump as a liability.</b> <a href="https://justthenews.com/nation/states/center-square/poll-vance-widens-lead-2028-republican-presidential-primary-field">The Center Square, via Just the News</a>.</li>
</ol>'''

C = {}
C['en'] = dict(
 weekly='This article will be updated every week with new numbers and relevant developments.',
 eyebrow='Library · Data · 5 November 2026',
 h1='After the midterms, the race to succeed Trump is suddenly open', h1s='Vance vs Rubio, and a late challenger: what the markets and the polls say',
 dek='Two days after Democrats won control of both chambers of Congress, the money riding on the 2028 Republican nomination moved fast. JD Vance is still the favourite, but his lead has narrowed sharply, and Ron DeSantis, written off for most of the year, is back in the conversation.',
 stamp=['About 4 min read', 'Figures as of 4–5 November 2026', 'A source for every figure'],
 orgkey='Links in the text: <span class="k k-news">news organisations</span><span class="k k-poll">pollsters and researchers</span><span class="k k-fc">forecasters and markets</span>',
 alt='Illustration in the style of a wrestling fight card: VANCE vs RUBIO under a 2028 championship belt. Market odds on Kalshi, 4 November: Vance 31%, Rubio 23%. National polls, 60-day average: Vance 39%, Rubio 18%. New Hampshire, Saint Anselm College poll, October: 38% each. Late challenger: Ron DeSantis, from about 5% to 20% on Kalshi the day after the midterms.',
 cap=f'The contest at a glance. Free to share. Odds: {K}, 4 November 2026; polls: {PC} and {SA}.',
 d1='4 Oct 2026', d2='4 Nov 2026', d2l='4 Nov 2026, the day after the midterms',
 c1t='Vance’s lead over Rubio shrank to single digits after the midterms', c1s='Kalshi: implied chance of winning the 2028 Republican nomination',
 c1c=f'Gap between Vance and Rubio: 27 points on 4 October, 8 points on 4 November. Source: {K} prices via DeFi Rate and Tampa Free Press.',
 months=['Feb', 'Mar', 'Jun', 'Jul', 'Aug', 'Oct'],
 c2t='New Hampshire: Rubio has caught up with Vance', c2s='Republican primary polls in New Hampshire, 2026',
 c2c=f'Polls of likely or registered Republican primary voters by the University of New Hampshire (UNH) and {SA}, via {PC}, data to 31 October 2026.',
 body=lambda c1, c2: f'''
<h2>How do you measure a race nobody has entered yet?</h2>
<p>No Republican has formally declared for 2028. Three instruments still give a useful reading:</p>
<ul>
<li><b>Prediction markets</b> such as {K} and {PM}, where traders buy contracts that pay out if a candidate wins. A price of 31 cents means the market puts that candidate’s chances at about 31%.</li>
<li><b>Polls of likely primary voters</b>, which measure today’s preference. This far out, they mostly reflect name recognition.</li>
<li><b>Signals from the party itself</b>: whom Donald Trump blesses, where the big donors go, who actually decides to run.</li>
</ul>
<p>Each measures something different. Read together, they show a contest that has shifted.</p>
<h2>What the markets say</h2>
{c1}
<p>Most of that move happened within 24 hours of the results. On election day, DeSantis was still trading around 5%; by the next evening he was near 20%, while Vance slipped from 35%. {PM} shows a similar picture, with Vance at 31% and Rubio at 19%.</p>
<p>What traders rewarded in DeSantis was distance. He called the outcome a worst-case scenario for Republicans and, in a SiriusXM interview, argued that the confrontation with Iran was pushing up fuel prices and hurting working-class voters. He also called for a ban on stock trading by members of Congress. After a defeat, a Republican willing to criticise the administration looks like an asset to the market.</p>
<div class="callout">A caution: these markets are thin and react to headlines. A one-day jump can fade as fast as it came.</div>
<h2>What the voters say</h2>
<p>Polls tell a slightly different story, and all of them were taken before the midterms. Nationally, Vance still leads clearly: the {PC} average of 11 national polls through 31 October has him at 39%, ahead of Rubio (18%), Donald Trump Jr. (13%) and DeSantis (9%).</p>
<p>New Hampshire, traditionally the first state to hold a Republican primary, is where Rubio’s rise shows most.</p>
{c2}
<p>One national poll pointed the same way: {EM} found the two essentially tied in May. The first polls taken after the midterms will show whether DeSantis’s market surge is shared by actual Republican voters.</p>
<h2>What will decide it</h2>
<ul>
<li><b>Trump’s blessing.</b> Trump has praised both Vance and Rubio and called a joint Vance–Rubio ticket “unstoppable”, without saying who should lead it. {FOX} has also reported, citing a source, that he told donors the party needed to elect Vance. A formal endorsement was widely expected only after the midterms, which makes it the next big signal to watch.</li>
<li><b>Whether Vance runs, and whether Rubio steps aside.</b> Vance has said he would discuss 2028 with his family and with Trump after the midterms. Rubio has said he would back Vance if the vice president runs. While that pledge holds, the rivalry is a question of who goes first, not a head-to-head primary.</li>
<li><b>Closeness to Trump: asset or liability?</b> Before the vote, analysts already warned that heavy losses could make primary voters look for someone with more distance from the president. That is exactly the lane DeSantis has started to claim.</li>
<li><b>Money and machinery.</b> As finance chair of the Republican National Committee, Vance sits at the centre of the party’s donor network, an advantage no rival can match quickly.</li>
</ul>
<h2>Bottom line</h2>
<p>Vance remains the man to beat. But a year ago, markets treated him as close to a one-in-two bet. Today they price him at roughly one in three, and on {K} Rubio and DeSantis together are worth more than he is. The Republican race to succeed Trump has gone from a coronation to a contest, and the next few months of decisions, by Vance, by Rubio and above all by Trump, will settle its shape.</p>
''',
 src='Sources',
 credit='Researched and written with the help of Claude (Anthropic), based on the public sources listed above, and checked by me. Figures as of 5 November 2026. <a href="/#contact">Corrections welcome</a>.',
 foot='Library · 5 November 2026')

C['it'] = dict(
 weekly='Questo articolo sarà aggiornato ogni settimana con nuovi dati e gli sviluppi più rilevanti.',
 eyebrow='Library · Dati · 5 novembre 2026',
 h1='Dopo il voto di metà mandato, la corsa alla successione di Trump si è improvvisamente aperta', h1s='Vance contro Rubio, e uno sfidante dell’ultima ora: cosa dicono i mercati e i sondaggi',
 dek='Due giorni dopo che i democratici hanno ottenuto il controllo di entrambe le camere del Congresso, le scommesse sulla nomination repubblicana del 2028 si sono mosse in fretta. JD Vance resta il favorito, ma il suo vantaggio si è ridotto di molto, e Ron DeSantis, dato per spacciato per gran parte dell’anno, è tornato in partita.',
 stamp=['Circa 4 minuti di lettura', 'Dati al 4–5 novembre 2026', 'Una fonte per ogni dato'],
 orgkey='Link nel testo: <span class="k k-news">organi d’informazione</span><span class="k k-poll">istituti di sondaggio e ricerca</span><span class="k k-fc">modelli di previsione e mercati</span>',
 alt='Illustrazione nello stile di un manifesto di wrestling: VANCE contro RUBIO sotto una cintura da campione con la scritta 2028. Quote su Kalshi al 4 novembre: Vance 31%, Rubio 23%. Sondaggi nazionali, media a 60 giorni: Vance 39%, Rubio 18%. New Hampshire, sondaggio del Saint Anselm College di ottobre: 38% ciascuno. Lo sfidante: Ron DeSantis, da circa il 5% al 20% su Kalshi il giorno dopo il voto.',
 cap=f'La sfida in sintesi. Libera da condividere. Quote: {K}, 4 novembre 2026; sondaggi: {PC} e {SA}.',
 d1='4 ott 2026', d2='4 nov 2026', d2l='4 nov 2026, il giorno dopo il voto',
 c1t='Dopo il voto, il vantaggio di Vance su Rubio è sceso sotto i dieci punti', c1s='Kalshi: probabilità implicita di ottenere la nomination repubblicana del 2028',
 c1c=f'Distacco tra Vance e Rubio: 27 punti al 4 ottobre, 8 punti al 4 novembre. Fonte: prezzi di {K} tramite DeFi Rate e Tampa Free Press.',
 months=['feb', 'mar', 'giu', 'lug', 'ago', 'ott'],
 c2t='New Hampshire: Rubio ha raggiunto Vance', c2s='Sondaggi sulle primarie repubblicane in New Hampshire, 2026',
 c2c=f'Sondaggi tra probabili elettori o elettori registrati delle primarie repubblicane, realizzati dalla University of New Hampshire (UNH) e dal {SA}, tramite {PC}, dati al 31 ottobre 2026.',
 body=lambda c1, c2: f'''
<h2>Come si misura una corsa in cui nessuno è ancora sceso in campo?</h2>
<p>Nessun repubblicano ha ancora annunciato formalmente la propria candidatura per il 2028. Tre strumenti offrono comunque una lettura utile:</p>
<ul>
<li><b>I mercati di previsione</b>, come {K} e {PM}, dove si comprano contratti che pagano se un candidato vince. Un prezzo di 31 centesimi significa che il mercato gli attribuisce circa il 31% di probabilità.</li>
<li><b>I sondaggi tra i probabili elettori delle primarie</b>, che misurano le preferenze di oggi. A questa distanza dal voto riflettono soprattutto la notorietà dei nomi.</li>
<li><b>I segnali che arrivano dal partito</b>: chi riceve la benedizione di Donald Trump, dove vanno i grandi finanziatori, chi decide davvero di candidarsi.</li>
</ul>
<p>Ognuno misura una cosa diversa. Letti insieme, mostrano una sfida che è cambiata.</p>
<h2>Cosa dicono i mercati</h2>
{c1}
<p>Gran parte di questo spostamento è avvenuta nelle 24 ore successive ai risultati. Il giorno del voto DeSantis era ancora intorno al 5%; la sera dopo era vicino al 20%, mentre Vance scendeva dal 35%. {PM} mostra un quadro simile, con Vance al 31% e Rubio al 19%.</p>
<p>In DeSantis gli investitori hanno premiato la distanza dall’amministrazione. Ha definito il risultato lo scenario peggiore per i repubblicani e, in un’intervista a SiriusXM, ha sostenuto che lo scontro con l’Iran sta facendo salire i prezzi del carburante e colpisce gli elettori della classe lavoratrice. Ha anche chiesto di vietare ai membri del Congresso di comprare e vendere azioni. Dopo una sconfitta, un repubblicano disposto a criticare l’amministrazione appare al mercato come un punto di forza.</p>
<div class="callout">Una cautela: su questi mercati gli scambi sono pochi e i prezzi reagiscono ai titoli dei giornali. Un balzo di un giorno può svanire con la stessa rapidità.</div>
<h2>Cosa dicono gli elettori</h2>
<p>I sondaggi raccontano una storia un po’ diversa, e sono stati tutti realizzati prima del voto. A livello nazionale Vance resta nettamente in testa: la media {PC} di 11 sondaggi nazionali fino al 31 ottobre lo dà al 39%, davanti a Rubio (18%), Donald Trump Jr. (13%) e DeSantis (9%).</p>
<p>È in New Hampshire, tradizionalmente il primo stato a tenere le primarie repubblicane, che la rimonta di Rubio si vede di più.</p>
{c2}
<p>Anche un sondaggio nazionale andava nella stessa direzione: a maggio {EM} aveva trovato i due praticamente alla pari. I primi sondaggi dopo il voto diranno se l’impennata di DeSantis sui mercati è condivisa anche dagli elettori repubblicani.</p>
<h2>Cosa deciderà la corsa</h2>
<ul>
<li><b>La benedizione di Trump.</b> Trump ha elogiato sia Vance sia Rubio e ha definito “inarrestabile” un ticket Vance–Rubio, senza dire chi dei due dovrebbe guidarlo. {FOX} ha anche riferito, citando una fonte, che avrebbe detto ai finanziatori che il partito deve eleggere Vance. Un appoggio formale era atteso solo dopo il voto di metà mandato: è il prossimo grande segnale da seguire.</li>
<li><b>Se Vance si candida, e se Rubio si fa da parte.</b> Vance ha detto che dopo il voto avrebbe discusso del 2028 con la sua famiglia e con Trump. Rubio ha detto che sosterrebbe Vance se il vicepresidente si candidasse. Finché quell’impegno regge, la rivalità tra i due è una questione di chi parte per primo, non uno scontro diretto alle primarie.</li>
<li><b>La vicinanza a Trump: risorsa o zavorra?</b> Già prima del voto alcuni analisti avvertivano che una sconfitta pesante avrebbe potuto spingere gli elettori delle primarie verso qualcuno più distante dal presidente. È proprio lo spazio che DeSantis ha cominciato a occupare.</li>
<li><b>Soldi e organizzazione.</b> Come responsabile finanziario del Comitato nazionale repubblicano, Vance è al centro della rete dei finanziatori del partito, un vantaggio che nessun rivale può colmare in fretta.</li>
</ul>
<h2>In sintesi</h2>
<p>Vance resta l’uomo da battere. Un anno fa, però, i mercati gli davano quasi una possibilità su due. Oggi gliene danno circa una su tre, e su {K} Rubio e DeSantis insieme valgono più di lui. La corsa per succedere a Trump è passata da un’incoronazione a una vera sfida, e le decisioni dei prossimi mesi, di Vance, di Rubio e soprattutto di Trump, ne definiranno la forma.</p>
''',
 src='Fonti',
 credit='Ricerca e testo realizzati con l’aiuto di Claude (Anthropic), sulla base delle fonti pubbliche elencate sopra, e verificati da me. Dati aggiornati al 5 novembre 2026. <a href="/#contact">Correzioni benvenute</a>.',
 foot='Library · 5 novembre 2026')

C['ro'] = dict(
 weekly='Articolul va fi actualizat în fiecare săptămână cu cifre noi și informațiile relevante.',
 eyebrow='Library · Date · 5 noiembrie 2026',
 h1='După alegerile de la jumătatea mandatului, cursa pentru succesiunea lui Trump s-a deschis brusc', h1s='Vance contra Rubio și un rival de ultim moment: ce spun piețele și sondajele',
 dek='La două zile după ce democrații au câștigat controlul ambelor camere ale Congresului, pariurile pe candidatura republicană pentru 2028 s-au mișcat rapid. JD Vance rămâne favoritul, dar avansul lui s-a redus puternic, iar Ron DeSantis, considerat ieșit din joc aproape tot anul, a revenit în discuție.',
 stamp=['Circa 4 minute de citit', 'Date la 4–5 noiembrie 2026', 'Cifre din surse de încredere'],
 orgkey='Linkuri în text: <span class="k k-news">organizații de presă</span><span class="k k-poll">institute de sondare și cercetare</span><span class="k k-fc">prognoze și piețe de pariuri</span>',
 alt='Ilustrație în stilul unui afiș de wrestling: VANCE contra RUBIO sub o centură de campion cu inscripția 2028. Cote pe Kalshi la 4 noiembrie: Vance 31%, Rubio 23%. Sondaje naționale, medie pe 60 de zile: Vance 39%, Rubio 18%. New Hampshire, sondajul Saint Anselm College din octombrie: câte 38%. Intră în ring: Ron DeSantis, de la circa 5% la 20% pe Kalshi a doua zi după vot.',
 cap=f'Confruntarea pe scurt. Se poate distribui liber. Cote: {K}, 4 noiembrie 2026; sondaje: {PC} și {SA}.',
 d1='4 oct. 2026', d2='4 nov. 2026', d2l='4 nov. 2026, a doua zi după vot',
 c1t='După vot, avansul lui Vance față de Rubio a coborât sub zece puncte', c1s='Kalshi: șansa implicită de a obține candidatura republicană pentru 2028',
 c1c=f'Diferența dintre Vance și Rubio: 27 de puncte la 4 octombrie, 8 puncte la 4 noiembrie. Sursa: prețurile {K}, prin DeFi Rate și Tampa Free Press.',
 months=['feb.', 'mar.', 'iun.', 'iul.', 'aug.', 'oct.'],
 c2t='New Hampshire: Rubio l-a ajuns din urmă pe Vance', c2s='Sondaje pentru primarele republicane din New Hampshire, 2026',
 c2c=f'Sondaje printre probabilii votanți sau alegătorii înregistrați la primarele republicane, realizate de University of New Hampshire (UNH) și {SA}, prin {PC}, date la 31 octombrie 2026.',
 body=lambda c1, c2: f'''
<h2>Cum măsori o cursă în care nu a intrat încă nimeni?</h2>
<p>Niciun republican nu și-a anunțat oficial candidatura pentru 2028. Trei instrumente oferă totuși o imagine utilă:</p>
<ul>
<li><b>Piețele de predicții</b>, precum {K} și {PM}, unde se cumpără contracte care plătesc dacă un candidat câștigă. Un preț de 31 de cenți înseamnă că piața îi dă candidatului circa 31% șanse.</li>
<li><b>Sondajele printre probabilii votanți din primare</b>, care măsoară preferințele de azi. La această distanță de vot, ele arată mai ales cât de cunoscute sunt numele.</li>
<li><b>Semnalele din partid</b>: pe cine sprijină Donald Trump, încotro se îndreaptă marii finanțatori, cine decide efectiv să candideze.</li>
</ul>
<p>Fiecare măsoară altceva. Citite împreună, arată o competiție care s-a schimbat.</p>
<h2>Ce spun piețele</h2>
{c1}
<p>Cea mai mare parte a acestei mișcări s-a produs în 24 de ore de la rezultate. În ziua votului, DeSantis era încă în jur de 5%; a doua zi seara ajunsese aproape de 20%, iar Vance cobora de la 35%. {PM} arată o imagine asemănătoare, cu Vance la 31% și Rubio la 19%.</p>
<p>La DeSantis, investitorii au răsplătit distanța față de administrație. El a numit rezultatul cel mai rău scenariu pentru republicani și, într-un interviu la SiriusXM, a susținut că confruntarea cu Iranul scumpește carburanții și îi lovește pe alegătorii din clasa muncitoare. A cerut și interzicerea tranzacțiilor cu acțiuni pentru membrii Congresului. După o înfrângere, un republican dispus să critice administrația pare pentru piață un atu.</p>
<div class="callout">O precauție: pe aceste piețe se tranzacționează puțin, iar prețurile reacționează la titlurile din presă. Un salt de o zi poate dispărea la fel de repede.</div>
<h2>Ce spun alegătorii</h2>
<p>Sondajele spun o poveste puțin diferită și toate au fost făcute înainte de vot. La nivel național, Vance conduce încă detașat: media {PC} a 11 sondaje naționale până la 31 octombrie îl plasează la 39%, înaintea lui Rubio (18%), Donald Trump Jr. (13%) și DeSantis (9%).</p>
<p>În New Hampshire, statul care ține de obicei primele primare republicane, ascensiunea lui Rubio se vede cel mai bine.</p>
{c2}
<p>Și un sondaj național arăta în aceeași direcție: în mai, {EM} îi găsea pe cei doi practic la egalitate. Primele sondaje de după vot vor arăta dacă saltul lui DeSantis pe piețe este împărtășit și de alegătorii republicani.</p>
<h2>Ce va decide cursa</h2>
<ul>
<li><b>Sprijinul lui Trump.</b> Trump i-a lăudat atât pe Vance, cât și pe Rubio și a numit un tandem Vance–Rubio „de neoprit”, fără să spună cine ar trebui să fie în frunte. {FOX} a relatat și că, potrivit unei surse, le-ar fi spus finanțatorilor că partidul trebuie să-l aleagă pe Vance. Un sprijin oficial era așteptat abia după alegeri, așa că acesta e următorul semnal important de urmărit.</li>
<li><b>Dacă Vance candidează și dacă Rubio se dă la o parte.</b> Vance a spus că va discuta despre 2028 cu familia și cu Trump după alegeri. Rubio a spus că l-ar susține pe Vance dacă vicepreședintele candidează. Cât timp acest angajament rămâne valabil, rivalitatea dintre ei e o chestiune de cine pornește primul, nu o confruntare directă în primare.</li>
<li><b>Apropierea de Trump: atu sau povară?</b> Încă dinainte de vot, unii analiști avertizau că o înfrângere grea i-ar putea face pe alegătorii din primare să caute pe cineva mai distanțat de președinte. Exact acest spațiu a început să-l ocupe DeSantis.</li>
<li><b>Bani și organizare.</b> Ca responsabil cu finanțele Comitetului Național Republican, Vance se află în centrul rețelei de finanțatori a partidului, un avantaj pe care niciun rival nu-l poate recupera repede.</li>
</ul>
<h2>Concluzia</h2>
<p>Vance rămâne omul de învins. Acum un an însă, piețele îi dădeau aproape o șansă din două. Azi îi dau circa una din trei, iar pe {K} Rubio și DeSantis valorează împreună mai mult decât el. Cursa pentru succesiunea lui Trump a trecut de la o încoronare la o competiție adevărată, iar deciziile din lunile următoare, ale lui Vance, ale lui Rubio și mai ales ale lui Trump, îi vor da forma.</p>
''',
 src='Surse',
 credit='Documentat și scris cu ajutorul Claude (Anthropic), pe baza surselor publice de mai sus, și verificat de mine. Cifre valabile la 5 noiembrie 2026. <a href="/#contact">Corecturile sunt binevenite</a>.',
 foot='Library · 5 noiembrie 2026')

def pane(l):
    L = C[l]
    hidden = '' if l == 'en' else ' hidden'
    load = 'fetchpriority="high"' if l == 'en' else 'loading="lazy"'
    stamp = ''.join(f'<span>{s}</span>' for s in L['stamp'])
    hero = (f'<figure class="hero"><a href="hero-{l}.webp"><picture><source media="(max-width:600px)" srcset="hero-m-{l}.webp" width="1000" height="1250">'
            f'<img src="hero-{l}.webp" width="1600" height="800" alt="{L["alt"]}" {load}></picture></a><figcaption>{L["cap"]}</figcaption></figure>')
    return f'''<div class="pane" data-pane="{l}" lang="{l}"{hidden}>
<header class="head">
<span class="eyebrow">{L["eyebrow"]}</span>
<h1>{L["h1"]} <span>{L["h1s"]}</span></h1>
<p class="dek">{L["dek"]}</p>
<div class="stamp">{stamp}</div>
<div class="orgkey">{L["orgkey"]}</div>
<div class="updated">{L["weekly"]}</div>
</header>
{hero}
<article>{L["body"](chart_markets(l, L), chart_nh(l, L))}
<h2>{L["src"]}</h2>
{SOURCES}
<p class="credit">{L["credit"]}</p>
</article>
<footer>{L["foot"]}</footer>
</div>
'''

TITLE = 'After the midterms, the race to succeed Trump is suddenly open'
DESC = 'Vance vs Rubio, and a late challenger: what prediction markets and polls say about the 2028 Republican nomination after the 2026 midterms. A source for every figure. In English, Italian and Romanian.'
URL = f'https://alexgiboi.com/library/{SLUG}/'

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{DESC}">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Ion-Alexandru Giboi">
<meta property="og:image" content="{URL}share-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Vance vs Rubio: the 2028 Republican nomination after the midterms, on alexgiboi.com">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/share.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<title>{TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>{base_css}{EXTRA_CSS}</style>
</head>
<body>
{nav}

<div class="wrap">
<div class="langbar">
  <div class="share" data-share></div>
  <div class="lang" role="group" aria-label="Limba / Lingua / Language">
    <button type="button" id="btn-ro" data-lang="ro" aria-pressed="false">RO</button>
    <button type="button" id="btn-it" data-lang="it" aria-pressed="false">IT</button>
    <button type="button" id="btn-en" data-lang="en" aria-pressed="true">EN</button>
  </div>
</div>
{pane("en")}{pane("it")}{pane("ro")}<div class="share share-end" data-share="end"></div>
</div>
{lang_script}
<script src="/assets/share.js" defer></script>
{analytics}
</body>
</html>
'''
open(f'{SITE}/library/{SLUG}/index.html', 'w', encoding='utf-8').write(html)
print('written', len(html))
