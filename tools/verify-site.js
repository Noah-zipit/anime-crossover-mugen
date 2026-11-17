#!/usr/bin/env node
// Headless-Chromium smoke test for the deployed Anime Crossover MUGEN site.
// Drives the Playwright-cached headless shell over CDP using Node's built-in
// WebSocket (no extra packages). Connects DIRECTLY to the page target's own
// websocket (flattened browser sessions proved unreliable here).
// Collects console errors, failed requests, boot-log text, canvas presence,
// touch-overlay wiring, and a screenshot.
//
// Usage: node verify-site.js <url> [out-prefix]
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME = path.join(process.env.HOME, '.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell');
const url = process.argv[2];
const outPrefix = process.argv[3] || '/tmp/verify';
if (!url) { console.error('usage: node verify-site.js <url> [out-prefix]'); process.exit(2); }
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const withTimeout = (p, ms, what) => Promise.race([p, sleep(ms).then(() => { throw new Error('TIMEOUT: ' + what); })]);

(async () => {
  const port = 9333;
  const chrome = spawn(CHROME, [
    '--headless', '--no-sandbox', '--disable-gpu',
    `--remote-debugging-port=${port}`,
    '--user-data-dir=/tmp/chrome-verify-profile',
    '--window-size=1280,800', '--mute-audio', 'about:blank',
  ], { stdio: 'ignore' });
  const report = { url, consoleErrors: [], failedRequests: [], exceptions: [], checks: {} };
  try {
    let list;
    for (let i = 0; i < 40; i++) {
      try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); break; }
      catch { await sleep(250); }
    }
    if (!list) throw new Error('chrome did not start CDP');
    let page = list.find(t => t.type === 'page');
    if (!page) throw new Error('no page target');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await withTimeout(new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; }), 10000, 'ws open');
    let id = 0;
    const pending = new Map();
    const events = [];
    const send = (method, params) => new Promise((res, rej) => {
      const mid = ++id;
      pending.set(mid, { res, rej });
      ws.send(JSON.stringify({ id: mid, method, params: params || {} }));
      setTimeout(() => { if (pending.has(mid)) { pending.delete(mid); rej(new Error('TIMEOUT ' + method)); } }, 30000);
    });
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) {
        const { res, rej } = pending.get(m.id); pending.delete(m.id);
        if (m.error) rej(new Error(JSON.stringify(m.error))); else res(m.result || {});
      } else if (m.method) events.push(m);
    };
    await withTimeout(send('Runtime.enable'), 15000, 'Runtime.enable');
    await withTimeout(send('Log.enable'), 15000, 'Log.enable');
    await withTimeout(send('Network.enable'), 15000, 'Network.enable');
    await withTimeout(send('Page.enable'), 15000, 'Page.enable');
    await withTimeout(send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false }), 15000, 'metrics');
    await withTimeout(send('Page.navigate', { url }), 15000, 'navigate');
    const t0 = Date.now();
    let bootText = '';
    for (let i = 0; i < 24; i++) {
      await sleep(5000);
      try {
        const r = await send('Runtime.evaluate', { expression: `(function(){
          var b = document.getElementById('boot');
          var c = document.querySelector('body > canvas');
          return JSON.stringify({ boot: b ? b.textContent.slice(-600) : null,
            canvas: !!c, cw: c ? c.width : 0, ch: c ? c.height : 0,
            panics: window.__panics || [], touch: !!document.getElementById('tc-root'),
            title: document.title });
        })()`, returnByValue: true });
        const v = JSON.parse(r.result.value);
        bootText = v.boot || '';
        report.checks = v;
        if (v.canvas && /VFS ready/i.test(bootText)) break;
      } catch (e) { report.checks.evalError = e.message; }
    }
    report.bootTail = bootText;
    report.waitMs = Date.now() - t0;
    const tw = await send('Runtime.evaluate', { expression: `(function(){
      window.__tcSeen = [];
      document.addEventListener('keydown', function(e){ window.__tcSeen.push(e.code); });
      document.addEventListener('keyup', function(e){ window.__tcSeen.push('up:'+e.code); });
      var btns = document.querySelectorAll('#tc-root .tc-btn');
      if (!btns.length) return 'no-buttons';
      var b = btns[0];
      b.dispatchEvent(new PointerEvent('pointerdown', {pointerId: 1, bubbles: true}));
      b.dispatchEvent(new PointerEvent('pointerup', {pointerId: 1, bubbles: true}));
      return 'pressed:' + b.textContent + ' seen:' + window.__tcSeen.join(',');
    })()`, returnByValue: true });
    report.touchTest = (tw.result && tw.result.value) || String(tw);
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    if (shot.data) fs.writeFileSync(outPrefix + '.png', Buffer.from(shot.data, 'base64'));
    for (const e of events) {
      if (e.method === 'Runtime.exceptionThrown') report.exceptions.push(JSON.stringify(e.params.exceptionDetails).slice(0, 500));
      if (e.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(e.params.type)) {
        report.consoleErrors.push(e.params.type + ': ' + e.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 300));
      }
      if (e.method === 'Log.entryAdded' && e.params.entry.level === 'error') {
        report.consoleErrors.push('log: ' + (e.params.entry.text || '') + ' ' + (e.params.entry.url || ''));
      }
      if (e.method === 'Network.loadingFailed') report.failedRequests.push(e.params.errorText || 'loadingFailed');
      if (e.method === 'Network.responseReceived' && e.params.response.status >= 400) {
        report.failedRequests.push(e.params.response.status + ' ' + e.params.response.url);
      }
    }
    ws.close();
  } finally {
    chrome.kill();
  }
  report.consoleErrors = report.consoleErrors.slice(0, 20);
  report.failedRequests = [...new Set(report.failedRequests)].slice(0, 20);
  report.exceptions = report.exceptions.slice(0, 10);
  console.log(JSON.stringify(report, null, 2));
})().catch(e => { console.error('VERIFY FAILED:', e.message); process.exit(1); });
