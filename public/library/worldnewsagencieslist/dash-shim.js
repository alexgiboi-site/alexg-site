// Minimal stand-in for the dashboard runtime: loads the two CSV files and runs the page's calculations.
(function () {
  var files = { funding_agencies: 'funding_agencies.csv', funding_changes: 'funding_changes.csv' };
  var store = {}, calcs = {}, order = [], cbs = [];
  Object.keys(files).forEach(function (id) { store[id] = { status: 'loading', data: [], columns: [], meta: [] }; });
  function wrapRes(r) { r.rows = r.data; return r; }
  function runCalcs() {
    order.forEach(function (id) {
      var c = calcs[id];
      var ins = c.inputs.map(function (i) { return store[i]; });
      if (ins.every(function (x) { return x && x.status === 'ok'; })) {
        try { var out = c.fn.apply(null, ins.map(function (x) { return x.data; })); store[id] = { status: 'ok', data: out, columns: out && out[0] ? Object.keys(out[0]) : [], meta: [] }; }
        catch (e) { console.error(id, e); store[id] = { status: 'error', data: [], columns: [], meta: [], message: String(e) }; }
      } else if (ins.some(function (x) { return x && x.status === 'error'; })) {
        store[id] = { status: 'error', data: [], columns: [], meta: [] };
      } else { store[id] = { status: 'loading', data: [], columns: [], meta: [] }; }
    });
  }
  function fire() { runCalcs(); cbs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); fillMarks(); }
  function fillMarks() {
    document.querySelectorAll('[data-dash-filled]').forEach(function () {});
  }
  window.dash = {
    colors: ['#1F5FA6', '#E08A2E', '#2A9D8F', '#8E6BBF', '#C2546A', '#6E8B3D', '#A0673B', '#5C6B7A'],
    data: function (id) { var r = store[id] || { status: 'missing', data: [], columns: [], meta: [] }; return wrapRes(Object.assign({ refreshing: false }, r)); },
    onData: function (f) { cbs.push(f); try { f(); } catch (e) { console.error(e); } },
    calc: function (id, def) { calcs[id] = def; order.push(id); store[id] = { status: 'loading', data: [], columns: [], meta: [] }; },
    loader: function () {},
    setLink: function (p) { try { history.replaceState(null, '', '#' + p); } catch (e) {} },
    params: function () { return {}; }, setParams: function () {}, resetParams: function () {}, refresh: function () {}
  };
  var pending = Object.keys(files).length;
  Object.keys(files).forEach(function (id) {
    d3.csv(files[id]).then(function (rows) {
      store[id] = { status: 'ok', data: Array.from(rows), columns: rows.columns, meta: [] };
    }).catch(function (e) {
      store[id] = { status: 'error', data: [], columns: [], meta: [], message: String(e) };
    }).then(function () { if (--pending === 0) fire(); });
  });
  var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(fire, 150); });
})();
