/* alexgiboi.com — share bar for Library posts.
   Markup: <div class="share" data-share></div> (add data-share="end" for the closing bar).
   Plain links only: no third-party scripts, no trackers, no counters.
   Phones with a share sheet get one Share button plus Copy link; other screens get
   LinkedIn, X, Bluesky, WhatsApp, Email and Copy link. Labels follow the page language (EN/IT/RO). */
(function () {
  var bars = document.querySelectorAll('[data-share]');
  if (!bars.length) return;

  var STR = {
    en: { label: 'Share', share: 'Share', more: 'More', email: 'Email', copy: 'Copy link', copied: 'Link copied', fail: 'Copy this link:', via: 'Share on' },
    it: { label: 'Condividi', share: 'Condividi', more: 'Altro', email: 'Email', copy: 'Copia link', copied: 'Link copiato', fail: 'Copia questo link:', via: 'Condividi su' },
    ro: { label: 'Distribuie', share: 'Distribuie', more: 'Mai mult', email: 'E-mail', copy: 'Copiază linkul', copied: 'Link copiat', fail: 'Copiază acest link:', via: 'Distribuie pe' }
  };
  var ICON = {
    share: '<path d="M12 15V3M7.5 7.5 12 3l4.5 4.5"/><path d="M8 11H6a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-2"/>',
    link: '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3.2-3.2a4.5 4.5 0 0 0-6.4-6.4L12 5.6"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3.2 3.2a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2"/>',
    check: '<path d="M4.5 12.5 9.5 17.5 19.5 6.5"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3.5 6 8.5 7 8.5-7"/>'
  };
  var NETWORKS = [
    { id: 'linkedin', name: 'LinkedIn', href: function (u) { return 'https://www.linkedin.com/sharing/share-offsite/?url=' + enc(u); } },
    { id: 'x', name: 'X', href: function (u, t) { return 'https://x.com/intent/post?url=' + enc(u) + '&text=' + enc(t); } },
    { id: 'bluesky', name: 'Bluesky', href: function (u, t) { return 'https://bsky.app/intent/compose?text=' + enc(t + ' ' + u); } },
    { id: 'whatsapp', name: 'WhatsApp', href: function (u, t) { return 'https://wa.me/?text=' + enc(t + ' ' + u); } }
  ];

  function enc(s) { return encodeURIComponent(s); }
  function meta(sel) { var m = document.querySelector(sel); return m ? (m.getAttribute('content') || m.getAttribute('href') || '').trim() : ''; }
  function lang() { var l = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase(); return STR[l] ? l : 'en'; }
  function title() { return meta('meta[property="og:title"]') || document.title; }
  function desc() { return meta('meta[property="og:description"]') || meta('meta[name="description"]'); }
  // The clean public address, plus the current #hash so a chosen country or language travels with the link.
  function url() {
    var base = meta('link[rel="canonical"]') || (location.origin + location.pathname);
    var h = location.hash && location.hash.length > 1 ? location.hash : '';
    return base.split('#')[0] + h;
  }
  function svg(name) { return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + ICON[name] + '</svg>'; }

  var canNative = typeof navigator.share === 'function';
  var narrow = window.matchMedia ? window.matchMedia('(max-width: 640px)') : { matches: false };

  function render(bar) {
    var S = STR[lang()];
    var compact = canNative && narrow.matches;
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', S.label);
    if (bar.getAttribute('data-share') === 'end') bar.classList.add('share-end');
    var html = '<span class="share-label" aria-hidden="true">' + S.label + '</span>';
    if (compact) {
      html += '<button type="button" class="share-btn is-primary" data-act="native">' + svg('share') + '<span>' + S.share + '</span></button>';
    } else {
      NETWORKS.forEach(function (n) {
        html += '<a class="share-btn" data-net="' + n.id + '" href="#" target="_blank" rel="noopener noreferrer" aria-label="' + S.via + ' ' + n.name + '">' + n.name + '</a>';
      });
      html += '<a class="share-btn" data-net="email" href="#">' + svg('mail') + '<span>' + S.email + '</span></a>';
    }
    html += '<button type="button" class="share-btn" data-act="copy">' + svg('link') + '<span>' + S.copy + '</span></button>';
    if (canNative && !compact) html += '<button type="button" class="share-btn" data-act="native">' + svg('share') + '<span>' + S.more + '</span></button>';
    html += '<span class="share-status" role="status" aria-live="polite"></span>';
    bar.innerHTML = html;
    refresh(bar);
  }

  // Links are rebuilt from the current address each time, so they always match what the reader sees.
  function refresh(bar) {
    var u = url(), t = title();
    bar.querySelectorAll('[data-net]').forEach(function (a) {
      var id = a.getAttribute('data-net');
      if (id === 'email') {
        var d = desc();
        a.href = 'mailto:?subject=' + enc(t) + '&body=' + enc((d ? d + '\n\n' : '') + u);
      } else {
        NETWORKS.forEach(function (n) { if (n.id === id) a.href = n.href(u, t); });
      }
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, no) {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var done = false; try { done = document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
      done ? ok() : no();
    });
  }

  function onClick(e) {
    var btn = e.target.closest('.share-btn');
    if (!btn) return;
    var bar = btn.closest('[data-share]');
    var S = STR[lang()];
    if (btn.hasAttribute('data-net')) { refresh(bar); return; }
    var act = btn.getAttribute('data-act');
    if (act === 'native') {
      navigator.share({ title: title(), url: url() }).catch(function () {});
    } else if (act === 'copy') {
      var u = url();
      copyText(u).then(function () {
        var label = btn.querySelector('span');
        btn.classList.add('is-done');
        btn.querySelector('svg').innerHTML = ICON.check;
        label.textContent = S.copied;
        bar.querySelector('.share-status').textContent = S.copied;
        clearTimeout(btn._t);
        btn._t = setTimeout(function () {
          btn.classList.remove('is-done');
          btn.querySelector('svg').innerHTML = ICON.link;
          label.textContent = STR[lang()].copy;
          bar.querySelector('.share-status').textContent = '';
        }, 2200);
      }, function () { window.prompt(S.fail, u); });
    }
  }

  function renderAll() { bars.forEach(render); }
  bars.forEach(function (bar) {
    bar.addEventListener('click', onClick);
    // Some pages change the #hash without a hashchange event, so refresh again just before use.
    bar.addEventListener('pointerover', function () { refresh(bar); });
    bar.addEventListener('focusin', function () { refresh(bar); });
  });
  renderAll();
  window.addEventListener('hashchange', function () { bars.forEach(refresh); });
  if (narrow.addEventListener) narrow.addEventListener('change', renderAll);
  // Pages with a language switch (EN / IT / RO) relabel the bar when the language changes.
  if (window.MutationObserver) new MutationObserver(renderAll).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
