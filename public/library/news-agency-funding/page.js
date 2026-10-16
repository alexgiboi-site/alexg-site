
/* ---------- calculations ---------- */
dash.calc('fkpis', {
  title: 'Structure headline counts',
  description: 'Active agencies by structure (public / state, private, not determined), share of national agencies that are public or state, and evidence coverage.',
  inputs: ['funding_agencies', 'funding_changes'],
  fn: (funding_agencies, funding_changes) => {
    const act = funding_agencies.filter(r => r.status === 'Active');
    const n = (c) => act.filter(r => r.structure === c).length;
    const nat = act.filter(r => String(r.kind).startsWith('National'));
    const natPS = nat.filter(r => r.structure === 'Public / State').length;
    return [{
      total: funding_agencies.length,
      active: act.length,
      ps: n('Public / State'),
      private: n('Private'),
      undetermined: n('Not determined'),
      inferred: act.filter(r => r.structure === 'Public / State' && r.structure_basis === 'Inferred from ownership').length,
      national: nat.length,
      national_ps_share: nat.length ? natPS / nat.length : null,
      ev_official: funding_agencies.filter(r => r.evidence === 'Official source').length,
      ev_independent: funding_agencies.filter(r => r.evidence === 'Independent source').length,
      ev_none: funding_agencies.filter(r => r.evidence === 'Not confirmed').length,
      changed: funding_agencies.filter(r => Number(r.changes) > 0).length,
      changes: funding_changes.length
    }];
  }
});

dash.calc('fund_by_region', {
  title: 'Structure by region',
  description: 'Active agencies counted by region and structure.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const act = funding_agencies.filter(r => r.status === 'Active');
    return [...new Set(act.map(r => r.region))].map(region => {
      const rs = act.filter(r => r.region === region);
      const c = (k) => rs.filter(r => r.structure === k).length;
      return {region, total: rs.length, ps: c('Public / State'), private: c('Private'), undetermined: c('Not determined')};
    }).sort((a, b) => b.total - a.total);
  }
});

dash.calc('fund_by_kind', {
  title: 'Structure by kind',
  description: 'Active agencies counted by kind of agency and structure.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const act = funding_agencies.filter(r => r.status === 'Active');
    return [...new Set(act.map(r => r.kind))].map(kind => {
      const rs = act.filter(r => r.kind === kind);
      const c = (k) => rs.filter(r => r.structure === k).length;
      return {kind, total: rs.length, ps: c('Public / State'), private: c('Private'), undetermined: c('Not determined')};
    }).sort((a, b) => b.total - a.total);
  }
});

dash.calc('own_matrix', {
  title: 'Ownership type by region',
  description: 'Active agencies counted by region and ownership type, with an all-regions total row.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const keys = {'Government body': 'gov', 'State-owned company or statutory body': 'soc', 'State-owned, legal form not confirmed': 'sonc',
      'Public-law institution (no owner)': 'pli', 'Party-owned': 'party', 'Intergovernmental / association': 'igo',
      'Private: media-owned': 'media', 'Private: commercial': 'comm', 'Non-profit / philanthropic': 'np', 'Religious': 'rel', 'Unknown': 'unk'};
    const act = funding_agencies.filter(r => r.status === 'Active');
    const row = (region, rs) => {
      const o = {region, total: rs.length};
      for (const k of Object.values(keys)) o[k] = 0;
      for (const r of rs) o[keys[r.ownership_type] || 'unk'] += 1;
      return o;
    };
    const out = [...new Set(act.map(r => r.region))].map(g => row(g, act.filter(r => r.region === g))).sort((a, b) => b.total - a.total);
    out.push(row('All regions', act));
    return out;
  }
});

dash.calc('appoint_counts', {
  title: 'Appointing body',
  description: 'Active public / state agencies counted by the body that appoints, elects or approves their management.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const order = ['Parliament', 'Government nominee, voted in by parliament', 'Independent board or council', 'Government or cabinet', 'Head of state', 'Ministry or government department', 'Ruling party or other state organ', 'Not documented'];
    const act = funding_agencies.filter(r => r.status === 'Active' && r.structure === 'Public / State');
    return order.map(appointed_by => {
      const rs = act.filter(r => r.appointed_by === appointed_by);
      return {appointed_by, total: rs.length, ps: rs.length};
    }).filter(r => r.total > 0);
  }
});

dash.calc('chg_kpis', {
  title: 'Change headline counts',
  description: 'Logged changes and agencies affected, by direction group, overall and since 2020.',
  inputs: ['funding_changes'],
  fn: (funding_changes) => {
    const grp = {'Toward state': 'state', 'More public money': 'up', 'Less public money': 'down', 'Toward independence': 'indep', 'Toward non-profit': 'indep',
      'Toward private': 'priv', 'Private to private': 'priv', 'Restructuring': 'restr', 'Relaunch': 'restr', 'Closure': 'close', 'Closure risk': 'close'};
    const c = (rs, g) => rs.filter(r => grp[r.direction] === g).length;
    const s20 = funding_changes.filter(r => Number(r.year) >= 2020);
    return [{
      changes: funding_changes.length,
      agencies: new Set(funding_changes.map(r => r.id)).size,
      sourced: funding_changes.filter(r => r.verification !== 'Not confirmed').length,
      unconfirmed: funding_changes.filter(r => r.verification === 'Not confirmed').length,
      since2020: s20.length,
      state: c(funding_changes, 'state'), private: c(funding_changes, 'priv'), closure: c(funding_changes, 'close'),
      s20_state: c(s20, 'state'), s20_up: c(s20, 'up'), s20_down: c(s20, 'down'), s20_priv: c(s20, 'priv'), s20_close: c(s20, 'close'),
      earliest: Math.min(...funding_changes.map(r => Number(r.year)))
    }];
  }
});

dash.calc('chg_by_region', {
  title: 'Change direction by region',
  description: 'Logged changes counted by region and direction group, all years.',
  inputs: ['funding_changes'],
  fn: (funding_changes) => {
    const grp = {'Toward state': 'state', 'More public money': 'money_up', 'Less public money': 'money_down', 'Toward independence': 'indep', 'Toward non-profit': 'indep',
      'Toward private': 'private', 'Private to private': 'private', 'Restructuring': 'restruct', 'Relaunch': 'restruct', 'Closure': 'closure', 'Closure risk': 'closure'};
    return [...new Set(funding_changes.map(r => r.region))].map(region => {
      const rs = funding_changes.filter(r => r.region === region);
      const o = {region, total: rs.length, state: 0, money_up: 0, money_down: 0, indep: 0, private: 0, restruct: 0, closure: 0};
      for (const r of rs) o[grp[r.direction] || 'restruct'] += 1;
      return o;
    }).sort((a, b) => b.total - a.total);
  }
});

dash.calc('cat_counts', {
  title: 'Structure definitions',
  description: 'Each structure with its definition, the number of active agencies in it, and how many have a documented appointment rule.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const defs = [
      ['Public / State', 'Owned, founded or mainly funded by the state, with or without its own commercial revenue. Ranges from ministry departments and state institutions under full state control to public-service bodies whose management is approved by or answers to parliament; see who appoints the management.'],
      ['Private', 'Owned by media companies or cooperatives, commercial owners, non-profits or religious bodies, and financed mainly from its own commercial income.'],
      ['Not determined', 'Owner could not be established, the agency could not be confirmed to exist, or it fits neither group (e.g. party-owned).']];
    const act = funding_agencies.filter(r => r.status === 'Active');
    return defs.map(([category, definition]) => ({category, definition,
      active: act.filter(r => r.structure === category).length,
      documented: category === 'Public / State' ? act.filter(r => r.structure === category && r.structure_basis === 'Documented').length : null}));
  }
});

dash.calc('own_counts', {
  title: 'Ownership type definitions',
  description: 'Each ownership type with its definition and the number of active agencies of that type.',
  inputs: ['funding_agencies'],
  fn: (funding_agencies) => {
    const defs = [
      ['Government body', 'A unit of a ministry, presidency or other state organ, without its own legal personality.'],
      ['State-owned company or statutory body', 'A separate legal entity (state company, public establishment, statutory institution) owned or founded by the state.'],
      ['State-owned, legal form not confirmed', 'State-owned or state-run, but whether it is a ministry unit or a separate entity was not established.'],
      ['Public-law institution (no owner)', 'Autonomous public-law body with no shareholder.'],
      ['Party-owned', 'Owned by a political party or movement.'],
      ['Intergovernmental / association', 'Set up by several governments or a regional association.'],
      ['Private: media-owned', 'Owned by newspapers, broadcasters or a media cooperative.'],
      ['Private: commercial', 'Privately owned company not mainly owned by its media clients.'],
      ['Non-profit / philanthropic', 'Foundation, association or not-for-profit company.'],
      ['Religious', 'Owned by a church or religious body.'],
      ['Unknown', 'Owner not determined.']];
    const act = funding_agencies.filter(r => r.status === 'Active');
    return defs.map(([ownership_type, definition]) => ({ownership_type, definition, active: act.filter(r => r.ownership_type === ownership_type).length}));
  }
});

dash.calc('source_list', {
  title: 'Sources cited',
  description: 'Websites cited, with how many agencies and logged changes cite each.',
  inputs: ['funding_agencies', 'funding_changes'],
  fn: (funding_agencies, funding_changes) => {
    const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } };
    const m = new Map();
    const add = (u, k, hh) => { const h = hh || host(u); if (!h) return; if (!m.has(h)) m.set(h, {domain: h, agencies: 0, events: 0, example: u}); m.get(h)[k] += 1; };
    funding_agencies.forEach(r => [...new Set(String(r.sources || '').split(/\s*;\s*|\s+/).map(host).filter(Boolean))].forEach(h => add('https://' + h + '/', 'agencies', h)));
    funding_changes.forEach(r => add(r.source, 'events'));
    return [...m.values()].sort((a, b) => (b.agencies + b.events) - (a.agencies + a.events) || a.domain.localeCompare(b.domain));
  }
});

/* ---------- constants for drawing ---------- */
const FUND = ['Public / State', 'Private', 'Not determined'];
const FUND_KEY = {'Public / State': 'ps', 'Private': 'private', 'Not determined': 'undetermined'};
const FUND_LABEL = {'Public / State': 'Public / State', 'Private': 'Private', 'Not determined': 'Not determined'};
const fundColor = (c) => ({'Public / State': dash.colors[0], 'Private': dash.colors[2]}[c] || 'var(--cds-chart-muted)');
const OWN_COLS = [['gov', 0], ['soc', 0], ['sonc', 0], ['pli', 1], ['party', 4], ['igo', 1], ['media', 2], ['comm', 2], ['np', 2], ['rel', 2], ['unk', -1]];
const GROUPS = [
  {k: 'state', label: 'More state control', dirs: ['Toward state'], def: 'The state raised its stake, took direct control, or moved the agency under a more political body.'},
  {k: 'money_up', label: 'More public money', dirs: ['More public money'], def: 'A new or larger state grant, subsidy, capital increase or public-service contract.'},
  {k: 'money_down', label: 'Less public money', dirs: ['Less public money'], def: 'A state grant or contract cut, or payments suspended.'},
  {k: 'indep', label: 'More independence or non-profit', dirs: ['Toward independence', 'Toward non-profit'], def: 'From government department to autonomous public-law body, or from commercial owners to not-for-profit.'},
  {k: 'private', label: 'Privatised or new private owner', dirs: ['Toward private', 'Private to private'], def: 'A state agency privatised, or a private agency sold to another private owner.'},
  {k: 'restruct', label: 'Restructured, merged or relaunched', dirs: ['Restructuring', 'Relaunch'], def: 'A change of legal form, supervising body, a merger or a relaunch without a clear move toward the state or private owners.'},
  {k: 'closure', label: 'Closed or at risk', dirs: ['Closure', 'Closure risk'], def: 'Stopped operating, or closure of the news service announced.'}
];
const grpColor = (k) => ({state: dash.colors[0], money_up: dash.colors[3], money_down: dash.colors[5], indep: dash.colors[1], private: dash.colors[2], restruct: dash.colors[4], closure: 'var(--cds-chart-status-critical)'}[k] || 'var(--cds-chart-muted)');
const groupOf = (dir) => (GROUPS.find(g => g.dirs.includes(dir)) || GROUPS[5]).k;
const fmt = d3.format(',');
const pct0 = d3.format('.0%');
const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } };
const S = {page: 'funding', sort: 'country', dir: 1, csort: 'year', cdir: -1, traj: null, hashDone: false, inited: false, cinited: false};

function failed(el) { el.replaceChildren(); const d = document.createElement('div'); d.className = 'failed'; d.textContent = 'Failed to load'; el.appendChild(d); }
function clearChart(el, st) { el.classList.toggle('dash-skeleton', st === 'loading'); if (st === 'error') failed(el); else el.replaceChildren(); }

function fillMarks(scope) {
  scope.querySelectorAll('[data-source][data-field][data-row]').forEach(el => {
    const d = dash.data(el.dataset.source);
    const row = d.status === 'ok' && Array.isArray(d.data) ? d.data[Number(el.dataset.row)] : null;
    if (row) {
      const v = row[el.dataset.field];
      el.classList.remove('dash-skeleton');
      el.textContent = (v == null || v === '') ? '—' : el.dataset.fmt === 'pct' ? pct0(v) : typeof v === 'number' ? fmt(v) : String(v);
    } else {
      if (d.status !== 'loading') el.classList.remove('dash-skeleton');
      el.textContent = '—';
    }
  });
  scope.querySelectorAll('i[data-fc]').forEach(i => { i.style.background = fundColor(i.dataset.fc); });
  scope.querySelectorAll('i[data-grp]').forEach(i => { i.style.background = grpColor(i.dataset.grp); });
}

function makeTip(el) { const t = document.createElement('div'); t.className = 'tip'; el.appendChild(t); return d3.select(t); }
function showTip(el, tip, ev, lines) {
  const [mx, my] = d3.pointer(ev, el);
  tip.style('display', 'block').html('');
  lines.forEach(l => { const d = tip.append('div'); if (l.k) d.attr('class', 'k'); if (l.color) d.append('i').attr('class', 'sw').style('background', l.color); d.append('span').text(l.text); });
  const tw = tip.node().offsetWidth, th = tip.node().offsetHeight;
  let left = mx + 12; if (left + tw > el.clientWidth - 4) left = mx - tw - 12; left = Math.max(0, left);
  let top = my + 14; if (top + th > el.clientHeight - 2) top = Math.max(0, my - th - 10);
  tip.style('left', left + 'px').style('top', top + 'px');
}
function legend(el, items) {
  el.replaceChildren();
  items.forEach(it => { const s = document.createElement('span'); s.style.display = 'inline-flex'; s.style.alignItems = 'center'; const i = document.createElement('i'); i.className = 'sw'; i.style.background = it.color; s.appendChild(i); s.appendChild(document.createTextNode(it.label)); el.appendChild(s); });
}
function fitText(node, text, maxW) {
  node.text(text);
  if (node.node().getComputedTextLength() <= maxW) return;
  let t = text;
  while (t.length > 3 && node.node().getComputedTextLength() > maxW) { t = t.slice(0, -1); node.text(t + '…'); }
}

/* Horizontal stacked bars; keys = [{k, label, color, value}] */
function stackedBars(el, rows, labelField, keys, onPick) {
  el.replaceChildren();
  const W = Math.max(280, el.clientWidth);
  const barH = 20, gap = 9, top = 2;
  const H = top + rows.length * (barH + gap);
  el.style.minHeight = H + 'px';
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img');
  const probe = svg.append('text').attr('font-size', 12).style('font-family', 'var(--font-anthropic-sans)');
  let lw = 0; rows.forEach(r => { probe.text(r[labelField]); lw = Math.max(lw, probe.node().getComputedTextLength()); });
  probe.text(fmt(d3.max(rows, r => r.total) || 0)); const numW = probe.node().getComputedTextLength() + 10; probe.remove();
  const left = Math.min(lw, W * 0.42) + 10;
  const x = d3.scaleLinear([0, d3.max(rows, r => r.total) || 1], [left, W - numW]);
  const tip = makeTip(el);
  rows.forEach((r, i) => {
    const y = top + i * (barH + gap);
    const g = svg.append('g');
    const lab = g.append('text').attr('x', left - 8).attr('y', y + barH / 2).attr('dy', '0.35em').attr('text-anchor', 'end')
      .attr('font-size', 12).attr('fill', 'var(--color-fg)').style('font-family', 'var(--font-anthropic-sans)');
    fitText(lab, String(r[labelField]), left - 10);
    if (lab.text() !== String(r[labelField])) lab.append('title').text(r[labelField]);
    let x0 = left;
    keys.forEach(kk => {
      const v = r[kk.k]; if (!v) return;
      const w = x(v) - x(0);
      g.append('rect').attr('x', x0).attr('y', y).attr('width', Math.max(1, w - 1.5)).attr('height', barH).attr('rx', 3)
        .style('fill', kk.color).style('cursor', onPick ? 'pointer' : null)
        .on('mousemove', (ev) => showTip(el, tip, ev, [{text: r[labelField], k: true}, {text: `${kk.label}: ${fmt(v)} of ${fmt(r.total)} (${pct0(v / r.total)})`, color: kk.color}]))
        .on('mouseleave', () => tip.style('display', 'none'))
        .on('click', () => onPick && onPick(r, kk));
      x0 += w;
    });
    g.append('text').attr('x', x0 + 6).attr('y', y + barH / 2).attr('dy', '0.35em').attr('font-size', 12)
      .attr('fill', 'var(--color-fg-muted)').style('font-family', 'var(--font-anthropic-sans)').style('font-variant-numeric', 'tabular-nums').text(fmt(r.total));
  });
}

/* ---------- page 1 ---------- */
function drawMatrix(rows) {
  const tb = d3.select('#own-table tbody'); tb.selectAll('tr').remove();
  const body = rows.filter(r => r.region !== 'All regions');
  const max = d3.max(body, r => d3.max(OWN_COLS, ([k]) => r[k])) || 1;
  rows.forEach(r => {
    const isTot = r.region === 'All regions';
    const tr = tb.append('tr').attr('data-key', r.region).attr('class', isTot ? 'tot' : null);
    tr.append('td').text(r.region);
    OWN_COLS.forEach(([k, ci]) => {
      const v = r[k];
      const td = tr.append('td').attr('class', 'cell' + (v ? '' : ' zero')).text(fmt(v));
      if (v && !isTot) {
        const base = ci < 0 ? 'var(--cds-chart-muted)' : dash.colors[ci];
        td.style('background', `color-mix(in srgb, ${base} ${Math.round(10 + 55 * v / max)}%, transparent)`);
      }
    });
    tr.append('td').attr('class', 'num').text(fmt(r.total));
  });
}

const ACOLS = ['agency', 'acronym', 'country', 'region', 'kind', 'size', 'structure', 'ownership_type', 'owner', 'appointed_by', 'mixed_ownership', 'last_change', 'evidence', 'status', 'sources'];
const ANARROW = new Set(['acronym', 'region', 'kind', 'size', 'ownership_type', 'owner', 'appointed_by', 'mixed_ownership', 'last_change', 'evidence', 'status', 'sources']);
const FORDER = {'Public / State': 0, 'Private': 1, 'Not determined': 2};
const SORDER = {XL: 0, L: 1, M: 2, S: 3};
function addOpts(sel, vals, label) { vals.forEach(v => { const o = document.createElement('option'); o.value = v; o.textContent = label ? label(v) : v; sel.appendChild(o); }); }
function initAgencyControls(rows) {
  if (S.inited) return; S.inited = true;
  addOpts(document.getElementById('f-region'), [...new Set(rows.map(r => r.region))].sort());
  addOpts(document.getElementById('f-fund'), FUND, v => FUND_LABEL[v]);
  addOpts(document.getElementById('f-appt'), ['Parliament', 'Government nominee, voted in by parliament', 'Independent board or council', 'Government or cabinet', 'Head of state', 'Ministry or government department', 'Ruling party or other state organ', 'Not documented']);
  addOpts(document.getElementById('f-own'), [...new Set(rows.map(r => r.ownership_type))].sort());
  addOpts(document.getElementById('f-kind'), [...new Set(rows.map(r => r.kind))].sort());
  const ids = ['q', 'f-region', 'f-fund', 'f-appt', 'f-own', 'f-kind', 'f-size', 'f-chg', 'f-ev', 'f-status'];
  ids.forEach(id => document.getElementById(id).addEventListener('input', drawAgencyTable));
  document.getElementById('f-reset').addEventListener('click', () => { ids.forEach(id => { document.getElementById(id).value = ''; }); drawAgencyTable(); });
  document.querySelectorAll('#agency-table th button').forEach(b => b.addEventListener('click', () => {
    if (S.sort === b.dataset.sort) S.dir *= -1; else { S.sort = b.dataset.sort; S.dir = b.dataset.sort === 'last_change_year' ? -1 : 1; }
    drawAgencyTable();
  }));
  document.querySelector('#agency-table tbody').addEventListener('click', (ev) => {
    const tr = ev.target.closest('tr.clickable'); if (!tr) return;
    openHistory(tr.dataset.key);
  });
}
function drawAgencyTable() {
  const d = dash.data('funding_agencies');
  const tb = d3.select('#agency-table tbody'); tb.selectAll('tr').remove();
  if (d.status !== 'ok') { document.getElementById('row-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
  const v = (id) => document.getElementById(id).value;
  const q = v('q').trim().toLowerCase();
  let out = d.data.filter(r => (!v('f-region') || r.region === v('f-region')) && (!v('f-fund') || r.structure === v('f-fund')) && (!v('f-appt') || r.appointed_by === v('f-appt')) &&
    (!v('f-own') || r.ownership_type === v('f-own')) && (!v('f-kind') || r.kind === v('f-kind')) && (!v('f-size') || r.size === v('f-size')) &&
    (!v('f-chg') || (v('f-chg') === 'yes' ? Number(r.changes) > 0 : !(Number(r.changes) > 0))) &&
    (!v('f-ev') || r.evidence === v('f-ev')) &&
    (!v('f-status') || r.status === v('f-status')) &&
    (!q || [r.agency, r.acronym, r.country, r.owner, r.legal_form, r.ownership_type, r.mixed_ownership, r.last_change, r.governance, r.appointed_by, r.notes, r.alliances].join(' ').toLowerCase().includes(q)));
  const k = S.sort;
  const val = (r) => k === 'structure' ? FORDER[r[k]] ?? 9 : k === 'size' ? SORDER[r.size] ?? 9
    : k === 'last_change_year' ? (r[k] === '' ? 0 : Number(r[k])) : String(r[k] || '').toLowerCase();
  out.sort((a, b) => { const va = val(a), vb = val(b); return (va < vb ? -1 : va > vb ? 1 : String(a.agency).localeCompare(String(b.agency))) * S.dir; });
  document.getElementById('row-count').textContent = `${fmt(out.length)} of ${fmt(d.data.length)} agencies shown`;
  out.forEach(r => {
    const tr = tb.append('tr').attr('data-key', r.id).attr('class', Number(r.changes) > 0 ? 'clickable' : null);
    ACOLS.forEach(col => {
      const td = tr.append('td');
      const cls = [];
      if (ANARROW.has(col)) cls.push('hide-narrow');
      if (col === 'last_change' || col === 'owner' || col === 'appointed_by') cls.push('wrap');
      if (cls.length) td.attr('class', cls.join(' '));
      if (col === 'structure') { const s = td.append('span').attr('class', 'cat'); s.append('i').attr('class', 'sw').style('background', fundColor(r[col])); s.append('span').text(r[col]); }
      else if (col === 'appointed_by') { td.text(r.appointed_by || ''); const t = [r.governance, r.structure_basis === 'Inferred from ownership' ? 'Inferred from government ownership' : '', r.smm_class ? 'State Media Monitor: ' + r.smm_class : ''].filter(Boolean).join(' — '); if (t) td.attr('title', t); }
      else if (col === 'sources') { String(r.sources || '').split(/\s*;\s*/).filter(u => /^https?:\/\//.test(u)).forEach((u, i) => { if (i) td.append('span').text(' · '); td.append('a').attr('href', u).attr('target', '_blank').attr('rel', 'noopener noreferrer').text(host(u)); }); }
      else if (col === 'owner') { td.text(r.owner || ''); if (r.legal_form || r.notes) td.attr('title', [r.legal_form, r.notes].filter(Boolean).join(' — ')); }
      else td.text(r[col] || '');
    });
  });
  document.querySelectorAll('#agency-table th').forEach(th => {
    const b = th.querySelector('button'); if (!b) return;
    th.setAttribute('aria-sort', b.dataset.sort === S.sort ? (S.dir === 1 ? 'ascending' : 'descending') : 'none');
  });
}
function pickAgencies(field, value, fund) {
  document.getElementById('f-region').value = field === 'region' ? value : '';
  document.getElementById('f-kind').value = field === 'kind' ? value : '';
  document.getElementById('f-appt').value = field === 'appointed_by' ? value : '';
  document.getElementById('f-fund').value = fund;
  document.getElementById('f-status').value = '';
  drawAgencyTable();
  document.getElementById('agencies-card').scrollIntoView({behavior: 'smooth', block: 'start'});
}

function drawFunding() {
  const sec = document.getElementById('funding');
  fillMarks(sec);
  const fkeys = FUND.map(c => ({k: FUND_KEY[c], label: FUND_LABEL[c], color: fundColor(c), cat: c}));
  legend(document.getElementById('region-legend'), fkeys);
  legend(document.getElementById('kind-legend'), fkeys);
  const reg = dash.data('fund_by_region'), regEl = document.getElementById('region-chart');
  if (reg.status === 'ok') { regEl.classList.remove('dash-skeleton'); stackedBars(regEl, reg.data, 'region', fkeys, (r, kk) => pickAgencies('region', r.region, kk.cat)); } else clearChart(regEl, reg.status);
  const kind = dash.data('fund_by_kind'), kindEl = document.getElementById('kind-chart');
  if (kind.status === 'ok') { kindEl.classList.remove('dash-skeleton'); stackedBars(kindEl, kind.data, 'kind', fkeys, (r, kk) => pickAgencies('kind', r.kind, kk.cat)); } else clearChart(kindEl, kind.status);
  const akeys = fkeys.slice(0, 1);
  document.getElementById('appoint-legend').replaceChildren();
  const ap = dash.data('appoint_counts'), apEl = document.getElementById('appoint-chart');
  if (ap.status === 'ok') { apEl.classList.remove('dash-skeleton'); stackedBars(apEl, ap.data, 'appointed_by', akeys, (r, kk) => pickAgencies('appointed_by', r.appointed_by, kk.cat)); } else clearChart(apEl, ap.status);
  const mx = dash.data('own_matrix');
  if (mx.status === 'ok') drawMatrix(mx.data); else d3.select('#own-table tbody').selectAll('tr').remove();
  const ag = dash.data('funding_agencies');
  if (ag.status === 'ok') initAgencyControls(ag.data);
  drawAgencyTable();
}

/* ---------- page 2 ---------- */
function drawTimeline(el, rows) {
  el.replaceChildren();
  const W = Math.max(300, el.clientWidth);
  const Y0 = 1988, Y1 = 2027;
  const shown = rows.filter(r => Number(r.year) >= Y0);
  const earlier = rows.filter(r => Number(r.year) < Y0);
  const r0 = W < 520 ? 4 : 5.5, step = r0 * 2 + 2;
  const lanes = GROUPS.map(g => {
    const items = shown.filter(r => g.dirs.includes(r.direction));
    const by = d3.group(items, r => Number(r.year));
    return Object.assign({}, g, {items, by, max: Math.max(1, d3.max([...by.values()], v => v.length) || 1)});
  });
  const labelH = 18, pad = 10;
  let y = 0; lanes.forEach(l => { l.top = y; l.h = labelH + l.max * step + pad; y += l.h; });
  const axisH = 24, H = y + axisH;
  el.style.minHeight = H + 'px';
  const x = d3.scaleLinear([Y0 - 0.5, Y1 + 0.5], [6, W - 8]);
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img');
  // 2020+ band
  svg.append('rect').attr('x', x(2019.5)).attr('y', 0).attr('width', x(Y1 + 0.5) - x(2019.5)).attr('height', y).style('fill', 'var(--cds-chart-grid)').style('opacity', .5);
  const tip = makeTip(el);
  lanes.forEach(l => {
    const c = grpColor(l.k);
    const g = svg.append('g');
    g.append('line').attr('x1', 6).attr('x2', W - 8).attr('y1', l.top + l.h - 0.5).attr('y2', l.top + l.h - 0.5).attr('stroke', 'var(--cds-chart-grid)');
    g.append('circle').attr('cx', 11).attr('cy', l.top + 10).attr('r', 4).style('fill', c);
    g.append('text').attr('x', 20).attr('y', l.top + 10).attr('dy', '0.35em').attr('font-size', 12).attr('fill', 'var(--color-fg)')
      .style('font-family', 'var(--font-anthropic-sans)').text(`${l.label} · ${fmt(l.items.length + earlier.filter(r => l.dirs.includes(r.direction)).length)}`);
    for (const [yr, items] of l.by) {
      items.forEach((it, i) => {
        g.append('circle').attr('cx', x(yr)).attr('cy', l.top + labelH + r0 + 1 + i * step).attr('r', r0)
          .style('fill', c).style('stroke', 'var(--color-panel)').style('stroke-width', 1).style('cursor', 'pointer')
          .on('mousemove', function (ev) { d3.select(this).style('stroke', 'var(--color-fg)'); showTip(el, tip, ev, [
            {text: `${it.date} · ${it.agency} (${it.country})`, k: true},
            {text: `${it.direction}: ${it.change_type}`, color: c},
            {text: `${it.from_state || '–'} → ${it.to_state || '–'}`},
            {text: it.verification}]); })
          .on('mouseleave', function () { d3.select(this).style('stroke', 'var(--color-panel)'); tip.style('display', 'none'); })
          .on('click', () => openHistory(it.id));
      });
    }
  });
  const every = W < 520 ? 10 : 5;
  const ticks = d3.range(1990, Y1 + 1, every);
  const ax = svg.append('g').attr('transform', `translate(0,${y})`)
    .call(d3.axisBottom(x).tickValues(ticks).tickFormat(d3.format('d')).tickSizeOuter(0));
  ax.attr('font-size', null).attr('font-family', null);
  ax.selectAll('text').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)').style('font-family', 'var(--font-anthropic-sans)');
  ax.selectAll('line,path').attr('stroke', 'var(--cds-chart-axis)');
  const note = document.getElementById('timeline-note');
  note.textContent = 'Each dot is one logged change, by year and direction (shaded: 2020 onwards). Hover for details; click a dot to open that agency\'s history below.' +
    (earlier.length ? ` ${fmt(earlier.length)} earlier change${earlier.length > 1 ? 's' : ''} (before ${Y0}) ${earlier.length > 1 ? 'are' : 'is'} counted in the lane totals and listed in the change log.` : '');
}

function initTraj(changes, agencies) {
  const sel = document.getElementById('traj-sel');
  if (!sel.options.length) {
    const byId = new Map(agencies.map(a => [String(a.id), a]));
    const ids = [...new Set(changes.map(c => String(c.id)))].filter(id => byId.has(id))
      .sort((a, b) => byId.get(a).agency.localeCompare(byId.get(b).agency));
    ids.forEach(id => { const a = byId.get(id); const n = changes.filter(c => String(c.id) === id).length; sel.appendChild(new Option(`${a.agency} (${a.country}) · ${n}`, id)); });
    const lusa = agencies.find(a => a.acronym === 'Lusa');
    S.traj = S.traj || (lusa && ids.includes(String(lusa.id)) ? String(lusa.id) : ids[0]);
    sel.addEventListener('change', () => { S.traj = sel.value; drawTraj(); });
  }
  sel.value = S.traj;
}
function drawTraj() {
  const ch = dash.data('funding_changes'), ag = dash.data('funding_agencies');
  const tb = d3.select('#traj-table tbody'); tb.selectAll('tr').remove();
  if (ch.status !== 'ok' || ag.status !== 'ok' || !S.traj) return;
  const a = ag.data.find(r => String(r.id) === String(S.traj)); if (!a) return;
  document.getElementById('traj-name').textContent = `${a.agency} · ${a.country}`;
  ['traj-cat', 'traj-own', 'traj-gov'].forEach(id => document.getElementById(id).setAttribute('data-where', `id=${encodeURIComponent(a.id)}`));
  document.getElementById('traj-cat').textContent = a.structure;
  document.getElementById('traj-own').textContent = a.ownership_type;
  document.getElementById('traj-gov-wrap').hidden = !a.governance;
  document.getElementById('traj-gov').textContent = a.governance || '—';
  ch.data.filter(r => String(r.id) === String(S.traj)).sort((p, q) => Number(p.year) - Number(q.year) || Number(p.event) - Number(q.event)).forEach(r => {
    const tr = tb.append('tr').attr('data-key', r.event);
    tr.append('td').text(r.date);
    const s = tr.append('td').append('span').attr('class', 'cat'); s.append('i').attr('class', 'dot').style('background', grpColor(groupOf(r.direction))); s.append('span').text(r.direction);
    tr.append('td').attr('class', 'wrap').text(r.from_state);
    tr.append('td').attr('class', 'wrap').text(r.to_state);
    tr.append('td').attr('class', 'wrap hide-narrow').text(r.description);
  });
}
function openHistory(id) {
  S.traj = String(id);
  if (S.page !== 'changes') showPage('changes'); else { const sel = document.getElementById('traj-sel'); if (sel.options.length) sel.value = S.traj; drawTraj(); }
  document.getElementById('history-card').scrollIntoView({behavior: 'smooth', block: 'start'});
}

function initChangeControls(rows) {
  if (S.cinited) return; S.cinited = true;
  addOpts(document.getElementById('c-region'), [...new Set(rows.map(r => r.region))].sort());
  addOpts(document.getElementById('c-grp'), GROUPS.map(g => g.k), k => GROUPS.find(g => g.k === k).label);
  addOpts(document.getElementById('c-type'), [...new Set(rows.map(r => r.change_type))].sort());
  const ids = ['cq', 'c-region', 'c-grp', 'c-type', 'c-period', 'c-ver'];
  ids.forEach(id => document.getElementById(id).addEventListener('input', drawChangeTable));
  document.getElementById('c-reset').addEventListener('click', () => { ids.forEach(id => { document.getElementById(id).value = ''; }); drawChangeTable(); });
  document.querySelectorAll('#chg-table th button').forEach(b => b.addEventListener('click', () => {
    if (S.csort === b.dataset.sort) S.cdir *= -1; else { S.csort = b.dataset.sort; S.cdir = b.dataset.sort === 'year' ? -1 : 1; }
    drawChangeTable();
  }));
}
function drawChangeTable() {
  const d = dash.data('funding_changes');
  const tb = d3.select('#chg-table tbody'); tb.selectAll('tr').remove();
  if (d.status !== 'ok') { document.getElementById('chg-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
  const v = (id) => document.getElementById(id).value;
  const q = v('cq').trim().toLowerCase();
  const per = v('c-period');
  const inPer = (y) => !per || (per === '2020' ? y >= 2020 : per === '2010' ? y >= 2010 && y < 2020 : per === '2000' ? y >= 2000 && y < 2010 : y < 2000);
  let out = d.data.filter(r => (!v('c-region') || r.region === v('c-region')) && (!v('c-grp') || groupOf(r.direction) === v('c-grp')) &&
    (!v('c-type') || r.change_type === v('c-type')) && (!v('c-ver') || r.verification === v('c-ver')) && inPer(Number(r.year)) &&
    (!q || [r.agency, r.acronym, r.country, r.description, r.from_state, r.to_state, r.change_type, r.direction].join(' ').toLowerCase().includes(q)));
  const k = S.csort;
  const val = (r) => k === 'year' ? Number(r.year) : String(r[k] || '').toLowerCase();
  out.sort((a, b) => { const va = val(a), vb = val(b); return (va < vb ? -1 : va > vb ? 1 : (Number(b.event) - Number(a.event)) * (k === 'year' ? 1 : -1)) * S.cdir; });
  document.getElementById('chg-count').textContent = `${fmt(out.length)} of ${fmt(d.data.length)} changes shown`;
  out.forEach(r => {
    const tr = tb.append('tr').attr('data-key', r.event);
    tr.append('td').attr('class', 'num').text(r.year);
    tr.append('td').attr('class', 'hide-narrow').text(r.date);
    tr.append('td').attr('title', r.agency).text(r.acronym);
    tr.append('td').attr('class', 'hide-narrow').text(r.country);
    const s = tr.append('td').append('span').attr('class', 'cat'); s.append('i').attr('class', 'dot').style('background', grpColor(groupOf(r.direction))); s.append('span').text(r.direction);
    tr.append('td').attr('class', 'hide-narrow').text(r.change_type);
    tr.append('td').attr('class', 'wrap').text(r.from_state);
    tr.append('td').attr('class', 'wrap').text(r.to_state);
    tr.append('td').attr('class', 'wrap hide-narrow').text(r.description);
    tr.append('td').attr('class', 'hide-narrow').text(r.verification);
    const sc = tr.append('td').attr('class', 'hide-narrow');
    if (/^https?:\/\//.test(r.source || '')) sc.append('a').attr('href', r.source).attr('target', '_blank').attr('rel', 'noopener noreferrer').text(host(r.source));
    else sc.text(r.source || '');
  });
  document.querySelectorAll('#chg-table th').forEach(th => {
    const b = th.querySelector('button'); if (!b) return;
    th.setAttribute('aria-sort', b.dataset.sort === S.csort ? (S.cdir === 1 ? 'ascending' : 'descending') : 'none');
  });
}

function drawChanges() {
  const sec = document.getElementById('changes');
  fillMarks(sec);
  const ch = dash.data('funding_changes'), ag = dash.data('funding_agencies');
  const tl = document.getElementById('timeline-chart');
  if (ch.status === 'ok') { tl.classList.remove('dash-skeleton'); drawTimeline(tl, ch.data); } else clearChart(tl, ch.status);
  if (ch.status === 'ok' && ag.status === 'ok') { initTraj(ch.data, ag.data); drawTraj(); }
  const gk = GROUPS.map(g => ({k: g.k, label: g.label, color: grpColor(g.k)}));
  legend(document.getElementById('chg-region-legend'), gk);
  const cr = dash.data('chg_by_region'), crEl = document.getElementById('chg-region-chart');
  if (cr.status === 'ok') { crEl.classList.remove('dash-skeleton'); stackedBars(crEl, cr.data, 'region', gk, (r, kk) => {
    document.getElementById('c-region').value = r.region; document.getElementById('c-grp').value = kk.k; drawChangeTable();
    document.getElementById('log-card').scrollIntoView({behavior: 'smooth', block: 'start'}); }); }
  else clearChart(crEl, cr.status);
  if (ch.status === 'ok') initChangeControls(ch.data);
  drawChangeTable();
}

/* ---------- page 3 ---------- */
function drawDefs() {
  const sec = document.getElementById('definitions');
  fillMarks(sec);
  const cc = dash.data('cat_counts'), tc = d3.select('#cat-table tbody'); tc.selectAll('tr').remove();
  if (cc.status === 'ok') cc.data.forEach(r => {
    const tr = tc.append('tr').attr('data-key', r.category);
    const s = tr.append('td').append('span').attr('class', 'cat'); s.append('i').attr('class', 'sw').style('background', fundColor(r.category)); s.append('span').text(r.category);
    tr.append('td').attr('class', 'wrap').text(r.definition);
    tr.append('td').attr('class', 'num').text(fmt(r.active));
    tr.append('td').attr('class', 'num hide-narrow').text(r.documented == null ? '–' : fmt(r.documented));
  });
  const oc = dash.data('own_counts'), to = d3.select('#owncount-table tbody'); to.selectAll('tr').remove();
  if (oc.status === 'ok') oc.data.forEach(r => {
    const tr = to.append('tr').attr('data-key', r.ownership_type);
    tr.append('td').text(r.ownership_type);
    tr.append('td').attr('class', 'wrap').text(r.definition);
    tr.append('td').attr('class', 'num').text(fmt(r.active));
  });
  const dl = d3.select('#dir-list'); dl.selectAll('li').remove();
  GROUPS.forEach(g => { const li = dl.append('li'); li.append('i').attr('class', 'dot').style('background', grpColor(g.k)); li.append('strong').text(g.label + ': '); li.append('span').text(`${g.def} (${g.dirs.join(', ')})`); });
  const sl = dash.data('source_list'), ts = d3.select('#src-table tbody'); ts.selectAll('tr').remove();
  if (sl.status === 'ok') sl.data.forEach(r => {
    const tr = ts.append('tr').attr('data-key', r.domain);
    tr.append('td').append('a').attr('href', r.example).attr('target', '_blank').attr('rel', 'noopener noreferrer').text(r.domain);
    tr.append('td').attr('class', 'num').text(fmt(r.agencies));
    tr.append('td').attr('class', 'num').text(fmt(r.events));
  });
}

/* ---------- pages and links ---------- */
function showPage(p, link = true) {
  S.page = p;
  document.querySelectorAll('#dash-root .ff section.page').forEach(s => { s.hidden = s.id !== p; });
  document.querySelectorAll('#dash-root .ff .tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.page === p ? 'true' : 'false'));
  if (link) dash.setLink(p);
  drawCurrent();
}
document.querySelectorAll('#dash-root .ff .tabs button').forEach(b => b.addEventListener('click', () => showPage(b.dataset.page)));
function drawCurrent() { if (S.page === 'changes') drawChanges(); else if (S.page === 'definitions') drawDefs(); else drawFunding(); }
function handleHash() {
  if (S.hashDone) return; S.hashDone = true;
  const h = decodeURIComponent(location.hash.slice(1)); if (!h) return;
  const el = document.getElementById(h); if (!el) return;
  const sec = el.closest('section.page'); if (!sec) return;
  if (sec.id !== S.page) showPage(sec.id, false);
  if (el !== sec) el.scrollIntoView();
}
dash.onData(() => {
  drawCurrent();
  if (dash.data('funding_agencies').status === 'ok' && dash.data('funding_changes').status === 'ok') handleHash();
});
