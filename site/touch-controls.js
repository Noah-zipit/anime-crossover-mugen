/* Touch controls for Ashar's Anime Crossover MUGEN (WebMUGEN / IKEMEN GO web).
 *
 * One idea, kept small on purpose: the engine already listens on `document`
 * for keydown/keyup and maps KeyboardEvent.code to game keys
 * (ikemen-go-web src/system_js.go, jsCodeToKey). So each on-screen button
 * just dispatches a synthetic KeyboardEvent with the P1 key's code.
 * Nothing in the engine, the wasm, or the character data is modified.
 *
 * P1 layout (save/config.ini [Keys_P1]):
 *   move  W/A/S/D   A/B/C = K/L/;   X/Y/Z = I/O/P   Start = Enter
 */
(function () {
  'use strict';
  if (window.__acmTouch) return;
  window.__acmTouch = true;

  // code = KeyboardEvent.code the engine maps; key = the matching .key value.
  var BTNS = [
    // D-pad (left cluster)
    { cls: 'tc-up', label: '\u25B2', code: 'KeyW', key: 'w' },
    { cls: 'tc-left', label: '\u25C0', code: 'KeyA', key: 'a' },
    { cls: 'tc-right', label: '\u25B6', code: 'KeyD', key: 'd' },
    { cls: 'tc-down', label: '\u25BC', code: 'KeyS', key: 's' },
    // Attacks: top row X Y Z, bottom row A B C (right cluster)
    { row: 'top', label: 'X', code: 'KeyI', key: 'i' },
    { row: 'top', label: 'Y', code: 'KeyO', key: 'o' },
    { row: 'top', label: 'Z', code: 'KeyP', key: 'p' },
    { row: 'bot', label: 'A', code: 'KeyK', key: 'k' },
    { row: 'bot', label: 'B', code: 'KeyL', key: 'l' },
    { row: 'bot', label: 'C', code: 'Semicolon', key: ';' }
  ];

  function dispatch(type, code, key) {
    document.dispatchEvent(new KeyboardEvent(type, {
      code: code, key: key, bubbles: true, cancelable: true
    }));
  }

  function makeButton(def) {
    var b = document.createElement('div');
    b.className = 'tc-btn' + (def.cls ? ' ' + def.cls : '');
    b.textContent = def.label;
    b.setAttribute('role', 'button');
    b.setAttribute('aria-label', def.label);
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
    // Touch-only fallback for browsers without Pointer Events. Attaching
    // both would double-fire on modern browsers (pointer events derive
    // from touch), so this branch only runs where PointerEvent is absent.
    if (!window.PointerEvent) {
      b.addEventListener('touchstart', function (e) { e.preventDefault(); down(e); }, { passive: false });
      b.addEventListener('touchend', function (e) { e.preventDefault(); up(e); }, { passive: false });
      b.addEventListener('touchcancel', function (e) { e.preventDefault(); up(e); }, { passive: false });
    }
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
    atk.appendChild(top);
    atk.appendChild(bot);
    right.appendChild(atk);
    var start = makeButton({ label: 'START', code: 'Enter', key: 'Enter' });
    start.classList.add('tc-start');
    right.appendChild(start);

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
