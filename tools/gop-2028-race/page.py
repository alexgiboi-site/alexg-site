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
    rows = [('JD Vance', 'v', 37, 31), ('Marco Rubio', 'r', 17, 25), ('Ron DeSantis', 'd', 16, 16)]
    x = lambda v: 170 + v / 50 * 560
    g = []
    for i, (n, c, a, b) in enumerate(rows):
        y = 44 + i * 62
        # when the two readings are close, push the labels apart so they never overlap
        ya = y - 17
        if abs(a - b) < 4:
            # readings almost equal: new value above the dots, previous value below them
            (xa, ta), (xb, tb), ya = (x(a), 'middle'), (x(b), 'middle'), y + 30
        elif abs(a - b) < 10:
            (xa, ta), (xb, tb) = ((x(a) + 6, 'end'), (x(b) - 6, 'start')) if a < b else ((x(a) - 6, 'start'), (x(b) + 6, 'end'))
        else:
            (xa, ta), (xb, tb) = (x(a), 'middle'), (x(b), 'middle')
        g.append(f'<g><text class="lbl" x="152" y="{y+5}" text-anchor="end">{n}</text>'
                 f'<line class="link" x1="{x(a):.1f}" y1="{y}" x2="{x(b):.1f}" y2="{y}"/>'
                 f'<circle class="c-{c} soft" cx="{x(a):.1f}" cy="{y}" r="9"><title>{n}, {L["d1"]}: {pct(a,l)}</title></circle>'
                 f'<circle class="c-{c} solid" cx="{x(b):.1f}" cy="{y}" r="9"><title>{n}, {L["d2"]}: {pct(b,l)}</title></circle>'
                 f'<text class="vlab" x="{xa:.1f}" y="{ya}" text-anchor="{ta}">{pct(a,l)}</text>'
                 f'<text class="vlab b" x="{xb:.1f}" y="{y-17}" text-anchor="{tb}">{pct(b,l)}</text></g>')
    return (f'<figure><div class="ct">{L["c1t"]}</div><div class="cs">{L["c1s"]}</div>'
            f'<div class="legend"><span><i class="dot soft"></i>{L["d1"]}</span><span><i class="dot"></i>{L["d2l"]}</span></div>'
            f'<svg class="chart" viewBox="0 0 760 206" role="img" aria-label="{L["c1t"]}">{"".join(g)}</svg>'
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
USAT = org('news', 'https://www.usatoday.com/story/news/politics/2026/11/16/cygnal-2028-presidential-primary-poll/92811750007/', 'USA Today')
YG = org('poll', 'https://yougov.com/en-us/articles/55977-jd-vance-kamala-harris-top-lists-preferred-2028-presidential-candidates-november-9-11-2026-economist-yougov-poll', 'YouGov')
EM2 = org('poll', 'https://emersoncollegepolling.com/national-poll-rubio-leads-2028-gop-nomination-contest-ossoff-rises-among-democrats/', 'Emerson College')
USAT2 = org('news', 'https://www.yahoo.com/news/politics/articles/jd-vance-behind-marco-rubio-192147261.html', 'USA Today')
NW = org('news', 'https://newsweek.com/jd-vance-dealt-2028-blow-against-marco-rubio-in-post-midterm-poll-12741514', 'Newsweek')
AX = org('news', 'https://axios.com/2026/11/19/republicans-israel-poll-2028-primary-states', 'Axios')
VIN = org('news', 'https://vinnews.com/2026/11/23/rubio-holds-double-digit-lead-over-vance-in-early-state-2028-gop-primary-poll/', 'VIN News')
AP = org('news', 'https://www.pbs.org/newshour/politics/trump-auditions-potential-successors-as-rubio-and-vance-join-him-for-white-house-briefing', 'AP')
FOX2 = org('news', 'https://www.foxnews.com/politics/trump-says-vance-rubio-doing-fantastically-ahead-2028-republican-presidential-primary', 'Fox News')
FOX = org('news', 'https://www.foxnews.com/politics/trump-told-donors-we-need-elect-jd-source-confirms-weighs-vance-rubio-2028.amp', 'Fox News')

SOURCES = '''<ol class="sources">
<li><b>Prediction-market prices, 4 October, 4, 9, 16 and 23 November 2026.</b> <a href="https://defirate.com/odds/republican-nominee/">DeFi Rate (Kalshi and Polymarket, observed 23 November, 5:20 am ET; previous readings 16 November, 7:39 pm ET, and 9 November, 1:14 pm ET)</a>; <a href="https://kalshiview.com/markets/2028-republican-presidential-nominee/">KalshiView (Kalshi snapshot, 22 November: Vance 30%, Rubio 24%, DeSantis 16%)</a>; <a href="https://newsweek.com/jd-vance-dealt-2028-blow-against-marco-rubio-in-post-midterm-poll-12741514">Newsweek (Kalshi and Polymarket, 19 November)</a>; <a href="https://www.newsweek.com/college-republicans-snub-vance-and-rubio-for-surprise-2028-pick-12712777">Newsweek (Kalshi and Polymarket, 13 November; College Republican straw polls)</a>; <a href="https://www.newsweek.com/trump-asked-who-should-succeed-him-what-he-said-12685327">Newsweek (Kalshi and Polymarket, 8 November)</a>; <a href="https://defirate.com/prediction-markets/republican-presidential-nominee-odds/">DeFi Rate (Kalshi and Polymarket, 4 October)</a>; <a href="https://www.tampafp.com/vp-vances-2028-odds-slip-after-midterm-shellacking-florida-gov-desantis-surges-on-prediction-markets/">Tampa Free Press (Kalshi, 3–4 November; DeSantis interview on SiriusXM)</a>; <a href="https://news.kalshi.com/p/2026-midterms-recap-the-mega-mega-blue-tsunami">Kalshi midterms recap</a>.</li>
<li><b>Trump on his successor.</b> <a href="https://www.newsweek.com/trump-asked-who-should-succeed-him-what-he-said-12685327">Newsweek (CBS, 60 Minutes, aired 8 November 2026)</a>; <a href="https://www.pbs.org/newshour/politics/trump-auditions-potential-successors-as-rubio-and-vance-join-him-for-white-house-briefing">AP via PBS NewsHour, 21 November 2026 (White House briefing of 20 November)</a>; <a href="https://www.foxnews.com/politics/trump-says-vance-rubio-doing-fantastically-ahead-2028-republican-presidential-primary">Fox News (interview, 21 November 2026)</a>; <a href="https://www.ibtimes.co.uk/trump-praises-aoc-declines-2028-endorsement-1833805">IBTimes UK, 21 November 2026</a>.</li>
<li><b>Vance undecided on 2028.</b> <a href="https://www.nj.com/politics/2026/11/jd-vance-hits-roadblock-over-possible-2028-presidential-bid.html">NJ.com, 9 November 2026, citing The Wall Street Journal</a>; <a href="https://www.yahoo.com/news/politics/articles/vance-won-t-decision-2028-032509201.html">Mediaite via Yahoo News, 16 November 2026, citing Axios (decision after the new year)</a>; <a href="https://newsweek.com/jd-vance-dealt-2028-blow-against-marco-rubio-in-post-midterm-poll-12741514">Newsweek, 19 November 2026 (Vance: “We’ll figure it out sometime next year”)</a>; <a href="https://www.foxnews.com/politics/gop-midterm-bloodbath-exposes-cracks-vances-2028-white-house-ambitions">Fox News, 14 November 2026 (reaction to Vance’s post-election remarks)</a>.</li>
<li><b>New national polls after the midterms.</b> <a href="https://yougov.com/en-us/articles/55977-jd-vance-kamala-harris-top-lists-preferred-2028-presidential-candidates-november-9-11-2026-economist-yougov-poll">YouGov (Economist/YouGov poll, 9–11 November 2026, published 13 November)</a>; <a href="https://www.usatoday.com/story/news/politics/2026/11/16/cygnal-2028-presidential-primary-poll/92811750007/">USA Today (Cygnal poll, 4–5 November 2026, published 16 November)</a>; <a href="https://emersoncollegepolling.com/national-poll-rubio-leads-2028-gop-nomination-contest-ossoff-rises-among-democrats/">Emerson College Polling (national poll, 14–16 November 2026, released 19 November)</a>; <a href="https://www.yahoo.com/news/politics/articles/jd-vance-behind-marco-rubio-192147261.html">USA Today via Yahoo News, 19 November 2026 (Emerson results)</a>; <a href="https://newsweek.com/jd-vance-dealt-2028-blow-against-marco-rubio-in-post-midterm-poll-12741514">Newsweek, 19 November 2026 (Emerson; Echelon Insights, 12–16 November)</a>; <a href="https://townhall.com/news/dmitri-bolt/2026/11/20/a-new-poll-puts-this-republican-in-the-lead-for-2028-n2686806">Townhall, 20 November 2026 (Emerson results with a list of names; RealClearPolitics average)</a>.</li>
<li><b>Early-state poll (OnMessage for CAM Action, 7–10 November 2026).</b> <a href="https://axios.com/2026/11/19/republicans-israel-poll-2028-primary-states">Axios, 19 November 2026 (sponsor, dates, sample)</a>; <a href="https://vinnews.com/2026/11/23/rubio-holds-double-digit-lead-over-vance-in-early-state-2028-gop-primary-poll/">VIN News, 23 November 2026 (primary figures, overall and by state)</a>.</li>
<li><b>DeSantis on the midterm result.</b> <a href="https://www.newsweek.com/ron-desantis-issues-dire-prediction-for-gop-after-stunning-midterm-defeat-12666035">Newsweek</a>.</li>
<li><b>Polls.</b> <a href="https://www.pollcheck.co.uk/us/primaries/republican/">PollCheck, national Republican primary average (11 polls, 60 days to 31 October 2026; could not be rechecked on 17 or 24 November)</a>; <a href="https://www.pollcheck.co.uk/us/primaries/republican/new-hampshire/">PollCheck, New Hampshire polls (University of New Hampshire; Saint Anselm College)</a>; <a href="https://www.abc27.com/news/top-stories/marco-rubio-jd-vance-virtually-tied-in-2028-presidential-primary-poll-emerson-college-polling/amp/">abc27 (Emerson College poll, May 2026)</a>; <a href="https://www.realclearpolling.com/polls/president/republican-primary/2028/national">RealClearPolling, national polls and average (checked 10 November 2026)</a>; <a href="https://www.realclearpolling.com/polls/president/republican-primary/2028/new-hampshire">RealClearPolling, New Hampshire polls (checked 10 November 2026)</a>.</li>
<li><b>Trump, Vance and Rubio on 2028.</b> <a href="https://www.foxnews.com/politics/poll-complicates-vance-status-trump-likely-2028-heir-apparent.print">Fox News (Vance–Rubio ticket; Rubio backing Vance)</a>; <a href="https://www.foxnews.com/politics/trump-told-donors-we-need-elect-jd-source-confirms-weighs-vance-rubio-2028.amp">Fox News (Trump’s remark to donors; Vance’s plans after the midterms)</a>; <a href="https://www.jpost.com/american-politics/article-885672">Jerusalem Post (Reuters)</a>; <a href="https://digital-release.cbs42.com/?p=2047668">CBS 42 (endorsement expected after the midterms)</a>; <a href="https://arynews.tv/us-vp-vance-campaigns-hometown-eye-on-2028">ARY News (AFP)</a>; <a href="https://gulfnews.com/amp/story/world%2Famericas%2Fvance-2028-buzz-grows-but-midterms-could-sting-1.500705402">Gulf News (AFP, RNC finance role)</a>.</li>
<li><b>Closeness to Trump as a liability.</b> <a href="https://justthenews.com/nation/states/center-square/poll-vance-widens-lead-2028-republican-presidential-primary-field">The Center Square, via Just the News</a>.</li>
</ol>'''

C = {}
C['en'] = dict(
 weekly='This article will be updated every week with new numbers and relevant developments. Last updated: 24 November 2026.',
 eyebrow='Library · Data · 5 November 2026',
 h1='After the midterms, the race to succeed Trump is suddenly open', h1s='Vance vs Rubio, and a late challenger: what the markets and the polls say',
 dek='Two days after Democrats won control of both chambers of Congress, the money riding on the 2028 Republican nomination moved fast. JD Vance is still the favourite, but his lead has narrowed sharply, and Ron DeSantis, written off for most of the year, is back in the conversation.',
 stamp=['About 6 min read', 'Figures as of 23 November 2026', 'A source for every figure'],
 orgkey='Links in the text: <span class="k k-news">news organisations</span><span class="k k-poll">pollsters and researchers</span><span class="k k-fc">forecasters and markets</span>',
 alt='Illustration in the style of a wrestling fight card: VANCE vs RUBIO under a 2028 championship belt. Market odds on Kalshi, 23 November: Vance 31%, Rubio 25%. National polls, average to 31 October: Vance 39%, Rubio 18%. New Hampshire, Saint Anselm College poll, October: 38% each. Late challenger: Ron DeSantis, from about 5% before the midterms to 16% on Kalshi.',
 cap=f'The contest at a glance. Free to share. Odds: {K}, 23 November 2026; polls: {PC} and {SA}.',
 d1='16 Nov 2026', d2='23 Nov 2026', d2l='23 Nov 2026, latest reading',
 c1t='In a week, Rubio has cut Vance’s market lead to six points', c1s='Kalshi: implied chance of winning the 2028 Republican nomination',
 c1c=f'Gap between Vance and Rubio: 27 points on 4 October, 8 points on 4 November, 13 points on 9 November, 20 points on 16 November, 6 points on 23 November. Source: {K} prices via DeFi Rate and Tampa Free Press.',
 months=['Feb', 'Mar', 'Jun', 'Jul', 'Aug', 'Oct'],
 c2t='New Hampshire: Rubio has caught up with Vance', c2s='Republican primary polls in New Hampshire, 2026',
 c2c=f'Polls of likely or registered Republican primary voters by the University of New Hampshire (UNH) and {SA}, via {PC}, data to 31 October 2026. No newer standalone New Hampshire poll had been published by 24 November.',
 body=lambda c1, c2: f'''
<h2>What’s new this week</h2>
<div class="callout"><b>Update of 24 November.</b> Rubio has closed much of the gap on the markets. On {K}, between 16 and 23 November he rose from 17% to 25%, while Vance fell from 37% to 31%; DeSantis held at 16%. A national {EM2} poll (14–16 November) put Rubio ahead of Vance, by 36% to 20% when voters were asked without a list of names and by 44% to 24% with one, according to {USAT2}; an Echelon Insights poll (12–16 November) still had Vance ahead, 40% to 26%, according to {NW}. A poll of 1,000 Republicans in Iowa, New Hampshire, Nevada and South Carolina, taken by OnMessage on 7–10 November for the political arm of the Combat Antisemitism Movement ({AX}), had Rubio at 47% and Vance at 28%, according to {VIN}. At a White House briefing on 20 November, Trump again declined to choose between the two, {AP} reported. Vance said he had not made a decision and would “figure it out sometime next year”, according to Newsweek.</div>
<h2>How do you measure a race nobody has entered yet?</h2>
<p>No Republican has formally declared for 2028. Three instruments still give a useful reading:</p>
<ul>
<li><b>Prediction markets</b> such as {K} and {PM}, where traders buy contracts that pay out if a candidate wins. A price of 34 cents means the market puts that candidate’s chances at about 34%.</li>
<li><b>Polls of likely primary voters</b>, which measure today’s preference. This far out, they mostly reflect name recognition.</li>
<li><b>Signals from the party itself</b>: whom Donald Trump blesses, where the big donors go, who actually decides to run.</li>
</ul>
<p>Each measures something different. Read together, they show a contest that has shifted.</p>
<h2>What the markets say</h2>
{c1}
<p>The big move came within 24 hours of the results. On election day, DeSantis was still trading around 5%; by the next evening he was near 20%, while Vance slipped from 35% to 31%. A month earlier, on 4 October, Kalshi had Vance at 45% and Rubio at 18%. In the days that followed, prices settled somewhat: by 9 November Vance was back at 34%, Rubio at 21% and DeSantis at 17%. On 16 November, Vance stood at 37%, Rubio at 17% and DeSantis at 16%. The following week Rubio climbed: by 23 November Kalshi had Vance at 31%, Rubio at 25% and DeSantis still at 16%, about three times his pre-election price. On {PM} the gap was wider, with Vance at about 29%, Rubio at 19% and DeSantis at 16% (DeFi Rate, 23 November). No other name traded at 5% or more on either market; the next, the commentator Tucker Carlson, was at 4.6% on Polymarket and 3.1% on Kalshi.</p>
<p>What traders rewarded in DeSantis was distance. He called the outcome a worst-case scenario for Republicans and, in a SiriusXM interview, argued that the confrontation with Iran was pushing up fuel prices and hurting working-class voters. He also called for a ban on stock trading by members of Congress. After a defeat, a Republican willing to criticise the administration looks like an asset to the market.</p>
<div class="callout">A caution: these markets are thin and react to headlines. A one-day jump can fade as fast as it came.</div>
<h2>What the voters say</h2>
<p>Polls tell a slightly different story. Before the midterms, Vance led clearly nationally: the {PC} average of 11 national polls through 31 October has him at 39%, ahead of Rubio (18%), Donald Trump Jr. (13%) and DeSantis (9%). The PollCheck average could not be rechecked for this update, so these are still the figures from 31 October. RealClearPolling’s average, with polls up to 1 November, had Vance at 38%, Rubio at 26% and DeSantis at 8%. The last national poll before the vote, by AtlasIntel (31 October–1 November), put Rubio ahead, 46% to 33%; the other national polls in RealClearPolling’s list since late August show Vance ahead by 12 to 22 points (RealClearPolling, checked 10 November). Once the post-election polls were added, the RealClearPolitics average showed Rubio narrowly ahead, by 35.4% to 34%, with DeSantis at 10.2%, according to Townhall (20 November).</p>
<p>The polls taken after the vote point in different directions. In an Economist/{YG} poll of 9–11 November, which asked intended Republican primary voters an open question about whom they would vote for, 40% named Vance, 33% Rubio, 14% DeSantis and 9% Donald Trump. An Echelon Insights poll of 12–16 November had Vance at 40%, Rubio at 26% and DeSantis at 12% ({NW}). Other surveys put Rubio in front. A Cygnal survey of 3,000 midterm voters on 4–5 November, reported by {USAT}, found Rubio ahead of Vance by more than three points, with DeSantis a distant third; the published report gives no exact Republican figures. The {EM2} poll of 14–16 November, of 1,000 registered voters including 418 who intend to vote in the Republican primary, found Rubio at 36% and Vance at 20% on an open question, with DeSantis, Donald Trump and Thomas Massie at about 7% each; given a list of names, 44% chose Rubio, 24% Vance, 9% DeSantis and 6% Donald Trump Jr. ({USAT2}).</p>
<p>New Hampshire, traditionally the first state to hold a Republican primary, is where Rubio’s rise shows most.</p>
{c2}
<p>One national poll pointed the same way: {EM} found the two essentially tied in May. No standalone New Hampshire poll has been published since October. In the four-state OnMessage poll, which interviewed about 250 Republicans in each state, Rubio led in New Hampshire by 44% to 25%, according to {VIN}; a sample that small has a much wider margin of error than the full poll, and the survey was commissioned by an advocacy group.</p>
<h2>What will decide it</h2>
<ul>
<li><b>Trump’s blessing.</b> Trump has praised both Vance and Rubio and called a joint Vance–Rubio ticket “unstoppable”, without saying who should lead it. {FOX} has also reported, citing a source, that he told donors the party needed to elect Vance. A formal endorsement was widely expected only after the midterms. Asked about it on CBS’s <i>60 Minutes</i>, aired on 8 November, Trump said “Probably, not necessarily”, spoke of a “tremendous bench” and said “I may or may not get involved”, according to Newsweek. At a White House briefing on 20 November, with Vance and Rubio beside him, he again declined to say which would make the better president and joked that his chief of staff, Stephen Miller, “was better than these two guys”, according to {AP}. The next day, in an interview with {FOX2}, he said “the two of them are doing fantastically”.</li>
<li><b>Whether Vance runs, and whether Rubio steps aside.</b> Vance has said he would discuss 2028 with his family and with Trump after the midterms. According to The Wall Street Journal, as reported by NJ.com on 9 November, he has told associates he has not decided, and some people close to him doubt that a Republican can win in 2028. Axios reported on 15 November that he will not make a final decision until after the new year. Fox News reported that his post-election comment linking the party’s losses to the war with Iran drew criticism from some Republicans; asked about it on 20 November, Trump called the statement “fine” and “accurate”, according to AP. On 19 November, Newsweek quoted Vance as saying: “So I haven’t made a decision. We’ll figure it out sometime next year.” Rubio has said he would back Vance if the vice president runs. While that pledge holds, the rivalry is a question of who goes first, not a head-to-head primary.</li>
<li><b>Closeness to Trump: asset or liability?</b> Before the vote, analysts already warned that heavy losses could make primary voters look for someone with more distance from the president. That is exactly the lane DeSantis has started to claim.</li>
<li><b>Money and machinery.</b> As finance chair of the Republican National Committee, Vance sits at the centre of the party’s donor network, an advantage no rival can match quickly.</li>
</ul>
<h2>Bottom line</h2>
<p>Vance remains the markets’ favourite, but only just. A year ago, markets treated him as close to a one-in-two bet. Today {K} prices him at about three in ten, six points ahead of Rubio, and several polls taken since the midterms put Rubio in front, while others still show Vance leading. The Republican race to succeed Trump has gone from a coronation to a contest, and the next few months of decisions, by Vance, by Rubio and above all by Trump, will settle its shape.</p>
''',
 src='Sources',
 credit='Researched and written with the help of Claude (Anthropic), based on the public sources listed above, and checked by me. Figures as of 23 November 2026; last updated 24 November 2026. <a href="/#contact">Corrections welcome</a>.',
 foot='Library · 5 November 2026')

C['it'] = dict(
 weekly='Questo articolo sarà aggiornato ogni settimana con nuovi dati e gli sviluppi più rilevanti. Ultimo aggiornamento: 24 novembre 2026.',
 eyebrow='Library · Dati · 5 novembre 2026',
 h1='Dopo il voto di metà mandato, la corsa alla successione di Trump si è improvvisamente aperta', h1s='Vance contro Rubio, e uno sfidante dell’ultima ora: cosa dicono i mercati e i sondaggi',
 dek='Due giorni dopo che i democratici hanno ottenuto il controllo di entrambe le camere del Congresso, le scommesse sulla nomination repubblicana del 2028 si sono mosse in fretta. JD Vance resta il favorito, ma il suo vantaggio si è ridotto di molto, e Ron DeSantis, dato per spacciato per gran parte dell’anno, è tornato in partita.',
 stamp=['Circa 6 minuti di lettura', 'Dati al 23 novembre 2026', 'Una fonte per ogni dato'],
 orgkey='Link nel testo: <span class="k k-news">organi d’informazione</span><span class="k k-poll">istituti di sondaggio e ricerca</span><span class="k k-fc">modelli di previsione e mercati</span>',
 alt='Illustrazione nello stile di un manifesto di wrestling: VANCE contro RUBIO sotto una cintura da campione con la scritta 2028. Quote su Kalshi al 23 novembre: Vance 31%, Rubio 25%. Sondaggi nazionali, media al 31 ottobre: Vance 39%, Rubio 18%. New Hampshire, sondaggio del Saint Anselm College di ottobre: 38% ciascuno. Lo sfidante: Ron DeSantis, da circa il 5% prima del voto al 16% su Kalshi.',
 cap=f'La sfida in sintesi. Libera da condividere. Quote: {K}, 23 novembre 2026; sondaggi: {PC} e {SA}.',
 d1='16 nov 2026', d2='23 nov 2026', d2l='23 nov 2026, ultimo dato',
 c1t='In una settimana Rubio ha ridotto a sei punti il vantaggio di Vance sui mercati', c1s='Kalshi: probabilità implicita di ottenere la nomination repubblicana del 2028',
 c1c=f'Distacco tra Vance e Rubio: 27 punti al 4 ottobre, 8 al 4 novembre, 13 al 9 novembre, 20 al 16 novembre, 6 al 23 novembre. Fonte: prezzi di {K} tramite DeFi Rate e Tampa Free Press.',
 months=['feb', 'mar', 'giu', 'lug', 'ago', 'ott'],
 c2t='New Hampshire: Rubio ha raggiunto Vance', c2s='Sondaggi sulle primarie repubblicane in New Hampshire, 2026',
 c2c=f'Sondaggi tra probabili elettori o elettori registrati delle primarie repubblicane, realizzati dalla University of New Hampshire (UNH) e dal {SA}, tramite {PC}, dati al 31 ottobre 2026. Al 24 novembre non era stato pubblicato alcun sondaggio più recente dedicato al solo New Hampshire.',
 body=lambda c1, c2: f'''
<h2>Le novità della settimana</h2>
<div class="callout"><b>Aggiornamento del 24 novembre.</b> Sui mercati Rubio ha recuperato gran parte dello svantaggio. Su {K}, tra il 16 e il 23 novembre è salito dal 17% al 25%, mentre Vance è sceso dal 37% al 31%; DeSantis è rimasto al 16%. Un sondaggio nazionale di {EM2} (14-16 novembre) mette Rubio davanti a Vance: 36% a 20% quando agli intervistati non si propone alcun nome, 44% a 24% con un elenco di candidati, riferisce {USAT2}. Per Echelon Insights (12-16 novembre) è invece ancora avanti Vance, 40% a 26%, secondo {NW}. In un sondaggio su 1.000 repubblicani di Iowa, New Hampshire, Nevada e Carolina del Sud, realizzato da OnMessage dal 7 al 10 novembre per il braccio politico del Combat Antisemitism Movement ({AX}), Rubio è al 47% e Vance al 28%, secondo {VIN}. Al briefing della Casa Bianca del 20 novembre Trump ha di nuovo evitato di scegliere tra i due, riferisce {AP}. Vance ha detto di non aver ancora deciso e che ci penserà “in qualche momento l’anno prossimo”, scrive Newsweek.</div>
<h2>Come si misura una corsa in cui nessuno è ancora sceso in campo?</h2>
<p>Nessun repubblicano ha ancora annunciato formalmente la propria candidatura per il 2028. Tre strumenti offrono comunque una lettura utile:</p>
<ul>
<li><b>I mercati di previsione</b>, come {K} e {PM}, dove si comprano contratti che pagano se un candidato vince. Un prezzo di 34 centesimi significa che il mercato gli attribuisce circa il 34% di probabilità.</li>
<li><b>I sondaggi tra i probabili elettori delle primarie</b>, che misurano le preferenze di oggi. A questa distanza dal voto riflettono soprattutto la notorietà dei nomi.</li>
<li><b>I segnali che arrivano dal partito</b>: chi riceve la benedizione di Donald Trump, dove vanno i grandi finanziatori, chi decide davvero di candidarsi.</li>
</ul>
<p>Ognuno misura una cosa diversa. Letti insieme, mostrano una sfida che è cambiata.</p>
<h2>Cosa dicono i mercati</h2>
{c1}
<p>Lo scossone è arrivato nelle 24 ore successive ai risultati. Il giorno del voto DeSantis era ancora intorno al 5%; la sera dopo era vicino al 20%, mentre Vance scendeva dal 35% al 31%. Un mese prima, il 4 ottobre, Kalshi dava Vance al 45% e Rubio al 18%. Nei giorni seguenti i prezzi si sono in parte assestati: al 9 novembre Vance era tornato al 34%, Rubio era al 21% e DeSantis al 17%. Il 16 novembre Vance era al 37%, Rubio al 17% e DeSantis al 16%. Nella settimana successiva Rubio è salito: al 23 novembre Kalshi dava Vance al 31%, Rubio al 25% e DeSantis ancora al 16%, circa il triplo del suo valore prima del voto. Su {PM} il distacco era più ampio, con Vance intorno al 29%, Rubio al 19% e DeSantis al 16% (DeFi Rate, 23 novembre). Nessun altro nome arrivava al 5% su nessuno dei due mercati: il successivo, il commentatore Tucker Carlson, era al 4,6% su Polymarket e al 3,1% su Kalshi.</p>
<p>In DeSantis gli investitori hanno premiato la distanza dall’amministrazione. Ha definito il risultato lo scenario peggiore per i repubblicani e, in un’intervista a SiriusXM, ha sostenuto che lo scontro con l’Iran sta facendo salire i prezzi del carburante e colpisce gli elettori della classe lavoratrice. Ha anche chiesto di vietare ai membri del Congresso di comprare e vendere azioni. Dopo una sconfitta, un repubblicano disposto a criticare l’amministrazione appare al mercato come un punto di forza.</p>
<div class="callout">Una cautela: su questi mercati gli scambi sono pochi e i prezzi reagiscono ai titoli dei giornali. Un balzo di un giorno può svanire con la stessa rapidità.</div>
<h2>Cosa dicono gli elettori</h2>
<p>I sondaggi raccontano una storia un po’ diversa. Prima del voto Vance era nettamente in testa a livello nazionale: la media {PC} di 11 sondaggi nazionali fino al 31 ottobre lo dà al 39%, davanti a Rubio (18%), Donald Trump Jr. (13%) e DeSantis (9%). Per questo aggiornamento non è stato possibile ricontrollare la media PollCheck: i dati sono ancora quelli al 31 ottobre. La media di RealClearPolling, con i sondaggi fino al 1° novembre, dava Vance al 38%, Rubio al 26% e DeSantis all’8%. L’ultimo sondaggio nazionale prima del voto, di AtlasIntel (31 ottobre–1° novembre), metteva invece Rubio in testa, 46% a 33%; gli altri sondaggi nazionali raccolti da RealClearPolling da fine agosto danno Vance avanti di 12-22 punti (RealClearPolling, verificato il 10 novembre). Con l’aggiunta dei sondaggi successivi al voto, la media di RealClearPolitics vedeva Rubio di poco avanti, 35,4% contro il 34% di Vance, con DeSantis al 10,2%, secondo Townhall (20 novembre).</p>
<p>I sondaggi successivi al voto vanno in direzioni diverse. In quello Economist/{YG} del 9-11 novembre, che chiedeva ai probabili elettori delle primarie repubblicane di indicare liberamente per chi avrebbero votato, il 40% ha fatto il nome di Vance, il 33% quello di Rubio, il 14% DeSantis e il 9% Donald Trump. Un sondaggio di Echelon Insights del 12-16 novembre dà Vance al 40%, Rubio al 26% e DeSantis al 12% ({NW}). Altre rilevazioni mettono invece Rubio in testa. Un’indagine di Cygnal su 3.000 elettori delle elezioni di metà mandato, condotta il 4-5 novembre e riportata da {USAT}, dà invece Rubio avanti di oltre tre punti su Vance, con DeSantis staccato al terzo posto; l’articolo non riporta le percentuali esatte dei repubblicani. Il sondaggio {EM2} del 14-16 novembre, su 1.000 elettori registrati, di cui 418 intenzionati a votare alle primarie repubblicane, trova Rubio al 36% e Vance al 20% con una domanda aperta, con DeSantis, Donald Trump e Thomas Massie intorno al 7% ciascuno; davanti a un elenco di nomi, il 44% sceglie Rubio, il 24% Vance, il 9% DeSantis e il 6% Donald Trump Jr. ({USAT2}).</p>
<p>È in New Hampshire, tradizionalmente il primo stato a tenere le primarie repubblicane, che la rimonta di Rubio si vede di più.</p>
{c2}
<p>Anche un sondaggio nazionale andava nella stessa direzione: a maggio {EM} aveva trovato i due praticamente alla pari. Da ottobre non è uscito alcun sondaggio dedicato al solo New Hampshire. Nel sondaggio OnMessage sui quattro stati, con circa 250 repubblicani intervistati in ciascuno, in New Hampshire Rubio è avanti 44% a 25%, secondo {VIN}; con un campione così ridotto il margine d’errore è molto più ampio di quello del sondaggio complessivo, e l’indagine è stata commissionata da un gruppo di pressione.</p>
<h2>Cosa deciderà la corsa</h2>
<ul>
<li><b>La benedizione di Trump.</b> Trump ha elogiato sia Vance sia Rubio e ha definito “inarrestabile” un ticket Vance–Rubio, senza dire chi dei due dovrebbe guidarlo. {FOX} ha anche riferito, citando una fonte, che avrebbe detto ai finanziatori che il partito deve eleggere Vance. Un appoggio formale era atteso solo dopo il voto di metà mandato. Interpellato a <i>60 Minutes</i> della CBS, in onda l’8 novembre, Trump ha risposto “Probabilmente, non necessariamente”, ha parlato di una “panchina formidabile” e ha detto “Potrei intervenire o no”, riferisce Newsweek. Al briefing del 20 novembre alla Casa Bianca, con Vance e Rubio al suo fianco, ha di nuovo evitato di dire quale dei due sarebbe un presidente migliore e ha scherzato sul fatto che il suo capo di gabinetto, Stephen Miller, “era meglio di questi due”, riferisce {AP}. Il giorno dopo, in un’intervista a {FOX2}, ha detto che “stanno andando entrambi alla grande”.</li>
<li><b>Se Vance si candida, e se Rubio si fa da parte.</b> Vance ha detto che dopo il voto avrebbe discusso del 2028 con la sua famiglia e con Trump. Secondo il Wall Street Journal, ripreso da NJ.com il 9 novembre, ai suoi collaboratori ha detto di non aver ancora deciso, e alcune persone a lui vicine dubitano che un repubblicano possa vincere nel 2028. Il 15 novembre Axios ha riferito che non prenderà una decisione definitiva prima del nuovo anno. Secondo Fox News, il suo commento del dopo-voto, che legava le sconfitte del partito alla guerra con l’Iran, è stato criticato da alcuni repubblicani; interpellato il 20 novembre, Trump ha detto che quella dichiarazione “va bene” ed è “corretta”, secondo AP. Il 19 novembre Newsweek lo ha citato così: “Non ho ancora deciso. Ci penseremo in qualche momento l’anno prossimo”. Rubio ha detto che sosterrebbe Vance se il vicepresidente si candidasse. Finché quell’impegno regge, la rivalità tra i due è una questione di chi parte per primo, non uno scontro diretto alle primarie.</li>
<li><b>La vicinanza a Trump: risorsa o zavorra?</b> Già prima del voto alcuni analisti avvertivano che una sconfitta pesante avrebbe potuto spingere gli elettori delle primarie verso qualcuno più distante dal presidente. È proprio lo spazio che DeSantis ha cominciato a occupare.</li>
<li><b>Soldi e organizzazione.</b> Come responsabile finanziario del Comitato nazionale repubblicano, Vance è al centro della rete dei finanziatori del partito, un vantaggio che nessun rivale può colmare in fretta.</li>
</ul>
<h2>In sintesi</h2>
<p>Vance resta il favorito dei mercati, ma di poco. Un anno fa i mercati gli davano quasi una possibilità su due. Oggi {K} gliene dà circa tre su dieci, sei punti più di Rubio, e diversi sondaggi successivi al voto mettono Rubio in testa, mentre altri vedono ancora avanti Vance. La corsa per succedere a Trump è passata da un’incoronazione a una vera sfida, e le decisioni dei prossimi mesi, di Vance, di Rubio e soprattutto di Trump, ne definiranno la forma.</p>
''',
 src='Fonti',
 credit='Ricerca e testo realizzati con l’aiuto di Claude (Anthropic), sulla base delle fonti pubbliche elencate sopra, e verificati da me. Dati aggiornati al 23 novembre 2026; ultimo aggiornamento 24 novembre 2026. <a href="/#contact">Correzioni benvenute</a>.',
 foot='Library · 5 novembre 2026')

C['ro'] = dict(
 weekly='Articolul va fi actualizat în fiecare săptămână cu cifre noi și informațiile relevante. Ultima actualizare: 24 noiembrie 2026.',
 eyebrow='Library · Date · 5 noiembrie 2026',
 h1='După alegerile de la jumătatea mandatului, cursa pentru succesiunea lui Trump s-a deschis brusc', h1s='Vance contra Rubio și un rival de ultim moment: ce spun piețele și sondajele',
 dek='La două zile după ce democrații au câștigat controlul ambelor camere ale Congresului, pariurile pe candidatura republicană pentru 2028 s-au mișcat rapid. JD Vance rămâne favoritul, dar avansul lui s-a redus puternic, iar Ron DeSantis, considerat ieșit din joc aproape tot anul, a revenit în discuție.',
 stamp=['Circa 6 minute de citit', 'Date la 23 noiembrie 2026', 'Cifre din surse de încredere'],
 orgkey='Linkuri în text: <span class="k k-news">organizații de presă</span><span class="k k-poll">institute de sondare și cercetare</span><span class="k k-fc">prognoze și piețe de pariuri</span>',
 alt='Ilustrație în stilul unui afiș de wrestling: VANCE contra RUBIO sub o centură de campion cu inscripția 2028. Cote pe Kalshi la 23 noiembrie: Vance 31%, Rubio 25%. Sondaje naționale, media la 31 octombrie: Vance 39%, Rubio 18%. New Hampshire, sondajul Saint Anselm College din octombrie: câte 38%. Intră în ring: Ron DeSantis, de la circa 5% înainte de vot la 16% pe Kalshi.',
 cap=f'Confruntarea pe scurt. Se poate distribui liber. Cote: {K}, 23 noiembrie 2026; sondaje: {PC} și {SA}.',
 d1='16 nov. 2026', d2='23 nov. 2026', d2l='23 nov. 2026, cea mai recentă cotă',
 c1t='Într-o săptămână, Rubio a redus la șase puncte avansul lui Vance pe piețe', c1s='Kalshi: șansa implicită de a obține candidatura republicană pentru 2028',
 c1c=f'Diferența dintre Vance și Rubio: 27 de puncte la 4 octombrie, 8 la 4 noiembrie, 13 la 9 noiembrie, 20 la 16 noiembrie, 6 la 23 noiembrie. Sursa: prețurile {K}, prin DeFi Rate și Tampa Free Press.',
 months=['feb.', 'mar.', 'iun.', 'iul.', 'aug.', 'oct.'],
 c2t='New Hampshire: Rubio l-a ajuns din urmă pe Vance', c2s='Sondaje pentru primarele republicane din New Hampshire, 2026',
 c2c=f'Sondaje printre probabilii votanți sau alegătorii înregistrați la primarele republicane, realizate de University of New Hampshire (UNH) și {SA}, prin {PC}, date la 31 octombrie 2026. Până la 24 noiembrie nu fusese publicat niciun sondaj mai recent dedicat doar New Hampshire.',
 body=lambda c1, c2: f'''
<h2>Ce s-a schimbat săptămâna aceasta</h2>
<div class="callout"><b>Actualizare din 24 noiembrie.</b> Pe piețe, Rubio a recuperat o mare parte din diferență. Pe {K}, între 16 și 23 noiembrie a urcat de la 17% la 25%, iar Vance a coborât de la 37% la 31%; DeSantis a rămas la 16%. Un sondaj național {EM2} (14–16 noiembrie) îl plasează pe Rubio înaintea lui Vance: 36% la 20% când respondenților nu li se propune niciun nume și 44% la 24% când primesc o listă, potrivit {USAT2}. În sondajul Echelon Insights (12–16 noiembrie), Vance conduce încă, cu 40% la 26%, potrivit {NW}. Un sondaj pe 1.000 de republicani din Iowa, New Hampshire, Nevada și Carolina de Sud, realizat de OnMessage în 7–10 noiembrie pentru brațul politic al Combat Antisemitism Movement ({AX}), îi dă lui Rubio 47% și lui Vance 28%, potrivit {VIN}. La briefingul de la Casa Albă din 20 noiembrie, Trump a evitat din nou să aleagă între cei doi, relatează {AP}. Vance a spus că nu a luat încă o decizie și că „vom vedea cândva anul viitor”, scrie Newsweek.</div>
<h2>Cum măsori o cursă în care nu a intrat încă nimeni?</h2>
<p>Niciun republican nu și-a anunțat oficial candidatura pentru 2028. Trei instrumente oferă totuși o imagine utilă:</p>
<ul>
<li><b>Piețele de predicții</b>, precum {K} și {PM}, unde se cumpără contracte care plătesc dacă un candidat câștigă. Un preț de 34 de cenți înseamnă că piața îi dă candidatului circa 34% șanse.</li>
<li><b>Sondajele printre probabilii votanți din primare</b>, care măsoară preferințele de azi. La această distanță de vot, ele arată mai ales cât de cunoscute sunt numele.</li>
<li><b>Semnalele din partid</b>: pe cine sprijină Donald Trump, încotro se îndreaptă marii finanțatori, cine decide efectiv să candideze.</li>
</ul>
<p>Fiecare măsoară altceva. Citite împreună, arată o competiție care s-a schimbat.</p>
<h2>Ce spun piețele</h2>
{c1}
<p>Saltul s-a produs în 24 de ore de la rezultate. În ziua votului, DeSantis era încă în jur de 5%; a doua zi seara ajunsese aproape de 20%, iar Vance cobora de la 35% la 31%. Cu o lună înainte, la 4 octombrie, Kalshi îl dădea pe Vance la 45% și pe Rubio la 18%. În zilele următoare prețurile s-au mai așezat: la 9 noiembrie Vance revenise la 34%, Rubio era la 21%, iar DeSantis la 17%. Pe 16 noiembrie, Vance era la 37%, Rubio la 17%, iar DeSantis la 16%. În săptămâna următoare Rubio a urcat: pe 23 noiembrie Kalshi îl dădea pe Vance la 31%, pe Rubio la 25% și pe DeSantis tot la 16%, de circa trei ori peste nivelul de dinainte de vot. Pe {PM} diferența era mai mare: Vance în jur de 29%, Rubio la 19%, DeSantis la 16% (DeFi Rate, 23 noiembrie). Niciun alt nume nu ajungea la 5% pe vreuna dintre piețe; următorul, comentatorul Tucker Carlson, era la 4,6% pe Polymarket și la 3,1% pe Kalshi.</p>
<p>La DeSantis, investitorii au răsplătit distanța față de administrație. El a numit rezultatul cel mai rău scenariu pentru republicani și, într-un interviu la SiriusXM, a susținut că confruntarea cu Iranul scumpește carburanții și îi lovește pe alegătorii din clasa muncitoare. A cerut și interzicerea tranzacțiilor cu acțiuni pentru membrii Congresului. După o înfrângere, un republican dispus să critice administrația pare pentru piață un atu.</p>
<div class="callout">O precauție: pe aceste piețe se tranzacționează puțin, iar prețurile reacționează la titlurile din presă. Un salt de o zi poate dispărea la fel de repede.</div>
<h2>Ce spun alegătorii</h2>
<p>Sondajele spun o poveste puțin diferită. Înainte de vot, Vance conducea detașat la nivel național: media {PC} a 11 sondaje naționale până la 31 octombrie îl plasează la 39%, înaintea lui Rubio (18%), Donald Trump Jr. (13%) și DeSantis (9%). Media PollCheck nu a putut fi reverificată pentru această actualizare, așa că cifrele sunt tot cele de la 31 octombrie. Media RealClearPolling, cu sondajele până la 1 noiembrie, îl dădea pe Vance la 38%, pe Rubio la 26% și pe DeSantis la 8%. Ultimul sondaj național dinainte de vot, realizat de AtlasIntel (31 octombrie–1 noiembrie), îl plasa însă pe Rubio în frunte, cu 46% față de 33%; celelalte sondaje naționale din lista RealClearPolling de la sfârșitul lui august încoace îl arată pe Vance în avans cu 12–22 de puncte (RealClearPolling, verificat pe 10 noiembrie). După adăugarea sondajelor de după vot, media RealClearPolitics îl arăta pe Rubio ușor în față, cu 35,4% față de 34% pentru Vance, iar pe DeSantis la 10,2%, potrivit Townhall (20 noiembrie).</p>
<p>Sondajele de după vot arată în direcții diferite. În sondajul Economist/{YG} din 9–11 noiembrie, care i-a lăsat pe probabilii votanți din primarele republicane să spună liber pe cine ar vota, 40% l-au numit pe Vance, 33% pe Rubio, 14% pe DeSantis și 9% pe Donald Trump. Un sondaj Echelon Insights din 12–16 noiembrie îl dă pe Vance la 40%, pe Rubio la 26% și pe DeSantis la 12% ({NW}). Alte sondaje îl pun însă pe Rubio în frunte. Un sondaj Cygnal pe 3.000 de alegători de la jumătatea mandatului, realizat pe 4–5 noiembrie și relatat de {USAT}, îl plasează în schimb pe Rubio cu peste trei puncte înaintea lui Vance, cu DeSantis pe un îndepărtat loc trei; articolul nu dă procentele exacte pentru republicani. Sondajul {EM2} din 14–16 noiembrie, pe 1.000 de alegători înregistrați, dintre care 418 intenționează să voteze în primarele republicane, îl găsește pe Rubio la 36% și pe Vance la 20% la o întrebare deschisă, cu DeSantis, Donald Trump și Thomas Massie la circa 7% fiecare; când primesc o listă de nume, 44% îl aleg pe Rubio, 24% pe Vance, 9% pe DeSantis și 6% pe Donald Trump Jr. ({USAT2}).</p>
<p>În New Hampshire, statul care ține de obicei primele primare republicane, ascensiunea lui Rubio se vede cel mai bine.</p>
{c2}
<p>Și un sondaj național arăta în aceeași direcție: în mai, {EM} îi găsea pe cei doi practic la egalitate. Din octombrie nu a mai fost publicat niciun sondaj dedicat doar New Hampshire. În sondajul OnMessage din cele patru state, cu circa 250 de republicani intervievați în fiecare, Rubio conduce în New Hampshire cu 44% la 25%, potrivit {VIN}; un eșantion atât de mic are o marjă de eroare mult mai mare decât sondajul în ansamblu, iar studiul a fost comandat de o organizație de advocacy.</p>
<h2>Ce va decide cursa</h2>
<ul>
<li><b>Sprijinul lui Trump.</b> Trump i-a lăudat atât pe Vance, cât și pe Rubio și a numit un tandem Vance–Rubio „de neoprit”, fără să spună cine ar trebui să fie în frunte. {FOX} a relatat și că, potrivit unei surse, le-ar fi spus finanțatorilor că partidul trebuie să-l aleagă pe Vance. Un sprijin oficial era așteptat abia după alegeri. Întrebat despre asta la <i>60 Minutes</i> (CBS), emisiune difuzată pe 8 noiembrie, Trump a răspuns „Probabil, nu neapărat”, a vorbit despre o „rezervă extraordinară” de nume și a spus „S-ar putea să mă implic sau nu”, potrivit Newsweek. La briefingul de la Casa Albă din 20 noiembrie, cu Vance și Rubio alături, a evitat din nou să spună care dintre ei ar fi un președinte mai bun și a glumit că șeful său de cabinet, Stephen Miller, „a fost mai bun decât ăștia doi”, relatează {AP}. A doua zi, într-un interviu la {FOX2}, a spus că „amândoi se descurcă fantastic”.</li>
<li><b>Dacă Vance candidează și dacă Rubio se dă la o parte.</b> Vance a spus că va discuta despre 2028 cu familia și cu Trump după alegeri. Potrivit Wall Street Journal, citat de NJ.com pe 9 noiembrie, el le-a spus apropiaților că nu a decis încă, iar unii dintre cei din jurul lui se îndoiesc că un republican poate câștiga în 2028. Pe 15 noiembrie, Axios a relatat că nu va lua o decizie finală înainte de Anul Nou. Potrivit Fox News, comentariul lui de după alegeri, care lega înfrângerile partidului de războiul cu Iranul, a fost criticat de unii republicani; întrebat pe 20 noiembrie, Trump a spus că declarația a fost „în regulă” și „corectă”, potrivit AP. Pe 19 noiembrie, Newsweek l-a citat pe Vance spunând: „Nu am luat încă o decizie. Vom vedea cândva anul viitor.” Rubio a spus că l-ar susține pe Vance dacă vicepreședintele candidează. Cât timp acest angajament rămâne valabil, rivalitatea dintre ei e o chestiune de cine pornește primul, nu o confruntare directă în primare.</li>
<li><b>Apropierea de Trump: atu sau povară?</b> Încă dinainte de vot, unii analiști avertizau că o înfrângere grea i-ar putea face pe alegătorii din primare să caute pe cineva mai distanțat de președinte. Exact acest spațiu a început să-l ocupe DeSantis.</li>
<li><b>Bani și organizare.</b> Ca responsabil cu finanțele Comitetului Național Republican, Vance se află în centrul rețelei de finanțatori a partidului, un avantaj pe care niciun rival nu-l poate recupera repede.</li>
</ul>
<h2>Concluzia</h2>
<p>Vance rămâne favoritul piețelor, dar la limită. Acum un an, piețele îi dădeau aproape o șansă din două. Azi {K} îi dă circa trei din zece, cu șase puncte peste Rubio, iar mai multe sondaje de după alegeri îl plasează pe Rubio în frunte, deși altele îl arată încă pe Vance înainte. Cursa pentru succesiunea lui Trump a trecut de la o încoronare la o competiție adevărată, iar deciziile din lunile următoare, ale lui Vance, ale lui Rubio și mai ales ale lui Trump, îi vor da forma.</p>
''',
 src='Surse',
 credit='Documentat și scris cu ajutorul Claude (Anthropic), pe baza surselor publice de mai sus, și verificat de mine. Cifre valabile la 23 noiembrie 2026; ultima actualizare: 24 noiembrie 2026. <a href="/#contact">Corecturile sunt binevenite</a>.',
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
