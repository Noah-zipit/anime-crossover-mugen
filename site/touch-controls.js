/* Touch controls for Cursed Clash (IKEMEN GO web).
 *
 * One idea, kept small on purpose: the engine already listens on `document`
 * for keydown/keyup and maps KeyboardEvent.code to game keys
 * (ikemen-go-web src/system_js.go, jsCodeToKey). So each on-screen button
 * just dispatches a synthetic KeyboardEvent with the P1 key's code.
 * Nothing in the engine, the wasm, or the character data is modified.
 *
 * P1 layout (save/config.ini [Keys_P1]):
 *   move  W/A/S/D   A/B/C = K/L/;   X/Y/Z = I/O/P   Start = Enter   Pause = Esc
 * Labels are the real move names: X/Y/Z = light/medium/heavy PUNCH,
 * A/B/C = light/medium/heavy KICK. Start (Enter) is also every kept
 * character's power-charge command ("s"), so the one button is labelled
 * CHARGE with START underneath it.
 */
(function () {
  'use strict';
  if (window.__ccTouch) return;
  window.__ccTouch = true;

  // Punch / kick / charge icons are the lite PNGs (neon graphics extracted
  // from the other-AI zip's glass-tile icons; the tiles' checkerboard
  // background was baked in, so only the neon graphic is used). Pause and
  // Moves stay inline SVG (no PNG was supplied for them).
  var IMG = {
    fist: 'touch/icons/punch.png',
    boot: 'touch/icons/kick.png',
    bolt: 'touch/icons/charge.png'
  };
  var SVG = {
    list: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="4.4" cy="6" r="1.5" fill="currentColor"/><circle cx="4.4" cy="12" r="1.5" fill="currentColor"/><circle cx="4.4" cy="18" r="1.5" fill="currentColor"/><rect x="8.4" y="4.8" width="11.2" height="2.4" rx="1.2" fill="currentColor"/><rect x="8.4" y="10.8" width="11.2" height="2.4" rx="1.2" fill="currentColor"/><rect x="8.4" y="16.8" width="11.2" height="2.4" rx="1.2" fill="currentColor"/></svg>'
  };

  // code = KeyboardEvent.code the engine maps; key = the matching .key value.
  // label = [line 1, line 2] shown under the icon (plain text, never inside the icon).
  var BTNS = [
    // D-pad (left cluster): direction triangles only, as before.
    { cls: 'tc-up', label: '\u25B2', code: 'KeyW', key: 'w', icon: null },
    { cls: 'tc-left', label: '\u25C0', code: 'KeyA', key: 'a', icon: null },
    { cls: 'tc-right', label: '\u25B6', code: 'KeyD', key: 'd', icon: null },
    { cls: 'tc-down', label: '\u25BC', code: 'KeyS', key: 's', icon: null },
    // Attacks: top row punches (X/Y/Z), bottom row kicks (A/B/C).
    { row: 'top', kind: 'punch', icon: 'fist', lines: ['LIGHT', 'PUNCH'], code: 'KeyI', key: 'i' },
    { row: 'top', kind: 'punch', icon: 'fist', lines: ['MED', 'PUNCH'], code: 'KeyO', key: 'o' },
    { row: 'top', kind: 'punch', icon: 'fist', lines: ['HEAVY', 'PUNCH'], code: 'KeyP', key: 'p' },
    { row: 'bot', kind: 'kick', icon: 'boot', lines: ['LIGHT', 'KICK'], code: 'KeyK', key: 'k' },
    { row: 'bot', kind: 'kick', icon: 'boot', lines: ['MED', 'KICK'], code: 'KeyL', key: 'l' },
    { row: 'bot', kind: 'kick', icon: 'boot', lines: ['HEAVY', 'KICK'], code: 'Semicolon', key: ';' },
    // Utility row: CHARGE is Enter (Start) = every kept character's power charge.
    { row: 'util', kind: 'charge', icon: 'bolt', lines: ['CHARGE', 'START'], code: 'Enter', key: 'Enter' }
    // PAUSE is NOT in the cluster any more (2026-11-17: it sits in the top
    // bar next to MOVES / TOUCH). It still sends the same Escape keydown/
    // keyup as before; the engine behaviour (Escape quits mid-fight) is
    // unchanged, only the button moved.
  ];

  function dispatch(type, code, key) {
    document.dispatchEvent(new KeyboardEvent(type, {
      code: code, key: key, bubbles: true, cancelable: true
    }));
  }

  function makeButton(def) {
    var b = document.createElement('div');
    b.className = 'tc-btn' + (def.cls ? ' ' + def.cls : '') + (def.kind ? ' tc-' + def.kind : '');
    if (def.icon) {
      var ic = document.createElement('span');
      ic.className = 'tc-ic';
      if (IMG[def.icon]) {
        var im = document.createElement('img');
        im.src = IMG[def.icon];
        im.alt = '';
        im.draggable = false;
        ic.appendChild(im);
      } else {
        ic.innerHTML = SVG[def.icon];
      }
      b.appendChild(ic);
    }
    if (def.lines) {
      var lb = document.createElement('span');
      lb.className = 'tc-label';
      def.lines.forEach(function (ln, i) {
        if (i) lb.appendChild(document.createElement('br'));
        lb.appendChild(document.createTextNode(ln));
      });
      b.appendChild(lb);
    } else {
      b.textContent = def.label;
    }
    b.setAttribute('role', 'button');
    b.setAttribute('aria-label', def.lines ? def.lines.join(' ') : def.label);
    var pointers = new Set();
    function down(e) {
      e.preventDefault();
      if (e.pointerId !== undefined) {
        if (pointers.has(e.pointerId)) return;
        pointers.add(e.pointerId);
        try { b.setPointerCapture(e.pointerId); } catch (err) { /* no capture */ }
      }
      b.classList.add('pressed');
      dispatch('keydown', def.code, def.key);
    }
    function up(e) {
      e.preventDefault();
      if (e.pointerId !== undefined) {
        pointers.delete(e.pointerId);
        if (pointers.size > 0) return; // another finger still holds it
      }
      b.classList.remove('pressed');
      dispatch('keyup', def.code, def.key);
    }
    b.addEventListener('pointerdown', down);
    b.addEventListener('pointerup', up);
    b.addEventListener('pointercancel', up);
    if (!window.PointerEvent) {
      b.addEventListener('touchstart', function (e) { e.preventDefault(); down(e); }, { passive: false });
      b.addEventListener('touchend', function (e) { e.preventDefault(); up(e); }, { passive: false });
      b.addEventListener('touchcancel', function (e) { e.preventDefault(); up(e); }, { passive: false });
    }
    b.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    return b;
  }

  function makeMovesButton() {
    var b = document.createElement('div');
    b.className = 'tc-btn tc-moves';
    var ic = document.createElement('span');
    ic.className = 'tc-ic';
    ic.innerHTML = SVG.list;
    b.appendChild(ic);
    var lb = document.createElement('span');
    lb.className = 'tc-label';
    lb.textContent = 'MOVES';
    b.appendChild(lb);
    b.setAttribute('role', 'button');
    b.setAttribute('aria-label', 'Open move list');
    b.addEventListener('click', function (e) {
      e.preventDefault();
      if (window.__ccMovesToggle) window.__ccMovesToggle();
    });
    b.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    return b;
  }

  function build() {
    var root = document.createElement('div');
    root.id = 'tc-root';

    var dpad = document.createElement('div');
    dpad.className = 'tc-cluster tc-dpad';
    BTNS.slice(0, 4).forEach(function (def) { dpad.appendChild(makeButton(def)); });

    var right = document.createElement('div');
    right.className = 'tc-cluster';
    var atk = document.createElement('div');
    atk.className = 'tc-atk';
    var top = document.createElement('div');
    top.className = 'tc-row top';
    BTNS.slice(4, 7).forEach(function (def) { top.appendChild(makeButton(def)); });
    var bot = document.createElement('div');
    bot.className = 'tc-row bot';
    BTNS.slice(7, 10).forEach(function (def) { bot.appendChild(makeButton(def)); });
    var util = document.createElement('div');
    util.className = 'tc-row util';
    BTNS.slice(10, 11).forEach(function (def) { util.appendChild(makeButton(def)); });
    util.appendChild(makeMovesButton());
    atk.appendChild(top);
    atk.appendChild(bot);
    atk.appendChild(util);
    right.appendChild(atk);

    root.appendChild(dpad);
    root.appendChild(right);
    document.body.appendChild(root);

    var toggle = document.createElement('button');
    toggle.id = 'tc-toggle';
    toggle.type = 'button';
    toggle.textContent = 'TOUCH';
    toggle.title = 'Show / hide touch controls';
    toggle.setAttribute('aria-label', 'Show or hide touch controls');
    document.body.appendChild(toggle);

    // PAUSE lives in the top bar now, not in the fight cluster. Same key as
    // before (Escape down on press, up on release); the engine still quits
    // mid-fight on it, only the button moved. It is a plain text button
    // like MOVES / TOUCH, no letters inside an icon.
    var pauseBtn = document.createElement('button');
    pauseBtn.id = 'tc-pause-btn';
    pauseBtn.type = 'button';
    pauseBtn.textContent = 'PAUSE';
    pauseBtn.title = 'Pause (Esc)';
    pauseBtn.setAttribute('aria-label', 'Pause');
    pauseBtn.addEventListener('mousedown', function (e) { e.preventDefault(); });
    pauseBtn.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      pauseBtn.classList.add('pressed');
      dispatch('keydown', 'Escape', 'Escape');
    });
    var pauseUp = function (e) {
      if (e) e.preventDefault();
      pauseBtn.classList.remove('pressed');
      dispatch('keyup', 'Escape', 'Escape');
    };
    pauseBtn.addEventListener('pointerup', pauseUp);
    pauseBtn.addEventListener('pointercancel', pauseUp);
    pauseBtn.addEventListener('click', function () { pauseBtn.blur(); });
    document.body.appendChild(pauseBtn);

    // FULLSCREEN in the top bar: Fullscreen API on the document element,
    // toggle on second tap. Works on Android Chrome. On change, the canvas
    // is refit to the new viewport.
    var fsBtn = document.createElement('button');
    fsBtn.id = 'tc-fs-btn';
    fsBtn.type = 'button';
    fsBtn.textContent = 'FULLSCREEN';
    fsBtn.title = 'Toggle fullscreen';
    fsBtn.setAttribute('aria-label', 'Toggle fullscreen');
    fsBtn.addEventListener('mousedown', function (e) { e.preventDefault(); });
    fsBtn.addEventListener('click', function () {
      try {
        if (document.fullscreenElement) { document.exitFullscreen(); }
        else {
          var el = document.documentElement;
          if (el.requestFullscreen) el.requestFullscreen();
          else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        }
      } catch (e) { /* fullscreen unavailable here */ }
      fsBtn.blur();
    });
    document.body.appendChild(fsBtn);
    document.addEventListener('fullscreenchange', function () {
      fsBtn.classList.toggle('on', !!document.fullscreenElement);
      var canvas = document.querySelector('body > canvas');
      if (canvas && window.ikemenGameOnlyUI) window.ikemenGameOnlyUI.fit(canvas);
      else if (canvas && window.ikemenFitCanvas) window.ikemenFitCanvas();
    });

    var KEY = 'acm-touch-visible';
    function isTouchDevice() {
      return (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) ||
        ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    }
    function apply(visible) {
      root.classList.toggle('hidden', !visible);
      toggle.classList.toggle('off', !visible);
      try { localStorage.setItem(KEY, visible ? '1' : '0'); } catch (e) { /* private mode */ }
    }
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
    apply(saved !== null ? saved === '1' : isTouchDevice());
    toggle.addEventListener('click', function () {
      apply(root.classList.contains('hidden'));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
