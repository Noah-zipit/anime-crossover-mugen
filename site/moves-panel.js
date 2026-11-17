/* Cursed Clash move-list panel (the on-page command list).
 *
 * The data comes from moves-data.js, generated from the four characters'
 * own movelist.dat files (themselves written from each character's .cmd by
 * the Studio command-list writer). Nothing here is invented: every move and
 * input is the character's own. The engine's pause-menu Command List shows
 * the same list in-game; this panel is the always-reachable copy.
 *
 * Notation: arrows = directions (hold), + = at the same time as the last
 * direction, LP/MP/HP = light/medium/heavy punch (X/Y/Z),
 * LK/MK/HK = light/medium/heavy kick (A/B/C).
 */
(function () {
  'use strict';
  if (window.__ccMoves) return;
  window.__ccMoves = true;

  var ARROWS = { U: '\u2191', UF: '\u2197', F: '\u2192', DF: '\u2198', D: '\u2193', DB: '\u2199', B: '\u2190', UB: '\u2196' };
  var BTN_CLASS = { LP: 'lp', MP: 'mp', HP: 'hp', LK: 'lk', MK: 'mk', HK: 'hk', START: 'start' };

  function chip(tok) {
    var s = document.createElement('span');
    if (tok.t === 'dir') { s.className = 'cc-chip cc-dir'; s.textContent = ARROWS[tok.v] || tok.v; }
    else if (tok.t === 'plus') { s.className = 'cc-chip cc-plus'; s.textContent = '+'; }
    else if (tok.t === 'air') { s.className = 'cc-chip cc-air'; s.textContent = 'AIR'; }
    else if (tok.t === 'dots') { s.className = 'cc-chip cc-plus'; s.textContent = '\u2026'; }
    else if (tok.t === 'btn') { s.className = 'cc-chip cc-btn ' + (BTN_CLASS[tok.v] || ''); s.textContent = tok.v; }
    return s;
  }

  function render(charKey) {
    var data = (window.CURSED_CLASH_MOVES || {})[charKey];
    var body = document.getElementById('cc-moves-body');
    if (!body) return;
    body.textContent = '';
    if (!data) { body.textContent = 'No move list for this character.'; return; }
    data.sections.forEach(function (sec) {
      var h = document.createElement('div');
      h.className = 'cc-sec';
      h.textContent = sec.title;
      body.appendChild(h);
      sec.rows.forEach(function (row) {
        var r = document.createElement('div');
        r.className = 'cc-row';
        var n = document.createElement('span');
        n.className = 'cc-name';
        n.textContent = row.name;
        r.appendChild(n);
        var inp = document.createElement('span');
        inp.className = 'cc-input';
        row.input.forEach(function (tok) { inp.appendChild(chip(tok)); });
        r.appendChild(inp);
        body.appendChild(r);
      });
    });
  }

  function build() {
    var data = window.CURSED_CLASH_MOVES || {};
    var keys = Object.keys(data);
    if (!keys.length) return;

    var panel = document.createElement('div');
    panel.id = 'cc-moves';
    panel.className = 'hidden';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Move list');

    var head = document.createElement('div');
    head.className = 'cc-head';
    var title = document.createElement('span');
    title.className = 'cc-title';
    title.textContent = 'MOVES';
    head.appendChild(title);
    var close = document.createElement('button');
    close.className = 'cc-close';
    close.type = 'button';
    close.textContent = '\u2715';
    close.setAttribute('aria-label', 'Close move list');
    close.addEventListener('click', function () { panel.classList.add('hidden'); });
    head.appendChild(close);
    panel.appendChild(head);

    var tabs = document.createElement('div');
    tabs.className = 'cc-tabs';
    var current = keys[0];
    keys.forEach(function (k) {
      var b = document.createElement('button');
      b.className = 'cc-tab' + (k === current ? ' active' : '');
      b.type = 'button';
      // Portrait thumbnail (AI art from the other-AI zip). The engine reads
      // select portraits from each character's SFF, not from loose files, so
      // these thumbnails only show here in the panel - they do not change the
      // in-game select portraits.
      var im = document.createElement('img');
      im.className = 'cc-tab-img';
      im.src = 'portraits/' + k + '.png';
      im.alt = '';
      im.draggable = false;
      b.appendChild(im);
      b.appendChild(document.createTextNode(data[k].display));
      b.addEventListener('click', function () {
        current = k;
        tabs.querySelectorAll('.cc-tab').forEach(function (t) { t.classList.remove('active'); });
        b.classList.add('active');
        render(k);
      });
      tabs.appendChild(b);
    });
    panel.appendChild(tabs);

    var body = document.createElement('div');
    body.id = 'cc-moves-body';
    body.className = 'cc-body';
    panel.appendChild(body);
    document.body.appendChild(panel);
    render(current);

    var barBtn = document.createElement('button');
    barBtn.id = 'cc-moves-btn';
    barBtn.type = 'button';
    barBtn.textContent = 'MOVES';
    barBtn.title = 'Open the move list';
    barBtn.setAttribute('aria-label', 'Open the move list');
    barBtn.addEventListener('click', function () { panel.classList.toggle('hidden'); });
    document.body.appendChild(barBtn);

    window.__ccMovesToggle = function () { panel.classList.toggle('hidden'); };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
