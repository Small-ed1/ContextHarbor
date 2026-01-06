// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles

(function (
  modules,
  entry,
  mainEntry,
  parcelRequireName,
  externals,
  distDir,
  publicUrl,
  devServer
) {
  /* eslint-disable no-undef */
  var globalObject =
    typeof globalThis !== 'undefined'
      ? globalThis
      : typeof self !== 'undefined'
      ? self
      : typeof window !== 'undefined'
      ? window
      : typeof global !== 'undefined'
      ? global
      : {};
  /* eslint-enable no-undef */

  // Save the require from previous bundle to this closure if any
  var previousRequire =
    typeof globalObject[parcelRequireName] === 'function' &&
    globalObject[parcelRequireName];

  var importMap = previousRequire.i || {};
  var cache = previousRequire.cache || {};
  // Do not use `require` to prevent Webpack from trying to bundle this call
  var nodeRequire =
    typeof module !== 'undefined' &&
    typeof module.require === 'function' &&
    module.require.bind(module);

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        if (externals[name]) {
          return externals[name];
        }
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire =
          typeof globalObject[parcelRequireName] === 'function' &&
          globalObject[parcelRequireName];
        if (!jumped && currentRequire) {
          return currentRequire(name, true);
        }

        // If there are other bundles on this page the require from the
        // previous one is saved to 'previousRequire'. Repeat this as
        // many times as there are bundles until the module is found or
        // we exhaust the require chain.
        if (previousRequire) {
          return previousRequire(name, true);
        }

        // Try the node require function if it exists.
        if (nodeRequire && typeof name === 'string') {
          return nodeRequire(name);
        }

        var err = new Error("Cannot find module '" + name + "'");
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;
      localRequire.cache = {};

      var module = (cache[name] = new newRequire.Module(name));

      modules[name][0].call(
        module.exports,
        localRequire,
        module,
        module.exports,
        globalObject
      );
    }

    return cache[name].exports;

    function localRequire(x) {
      var res = localRequire.resolve(x);
      if (res === false) {
        return {};
      }
      // Synthesize a module to follow re-exports.
      if (Array.isArray(res)) {
        var m = {__esModule: true};
        res.forEach(function (v) {
          var key = v[0];
          var id = v[1];
          var exp = v[2] || v[0];
          var x = newRequire(id);
          if (key === '*') {
            Object.keys(x).forEach(function (key) {
              if (
                key === 'default' ||
                key === '__esModule' ||
                Object.prototype.hasOwnProperty.call(m, key)
              ) {
                return;
              }

              Object.defineProperty(m, key, {
                enumerable: true,
                get: function () {
                  return x[key];
                },
              });
            });
          } else if (exp === '*') {
            Object.defineProperty(m, key, {
              enumerable: true,
              value: x,
            });
          } else {
            Object.defineProperty(m, key, {
              enumerable: true,
              get: function () {
                if (exp === 'default') {
                  return x.__esModule ? x.default : x;
                }
                return x[exp];
              },
            });
          }
        });
        return m;
      }
      return newRequire(res);
    }

    function resolve(x) {
      var id = modules[name][1][x];
      return id != null ? id : x;
    }
  }

  function Module(moduleName) {
    this.id = moduleName;
    this.bundle = newRequire;
    this.require = nodeRequire;
    this.exports = {};
  }

  newRequire.isParcelRequire = true;
  newRequire.Module = Module;
  newRequire.modules = modules;
  newRequire.cache = cache;
  newRequire.parent = previousRequire;
  newRequire.distDir = distDir;
  newRequire.publicUrl = publicUrl;
  newRequire.devServer = devServer;
  newRequire.i = importMap;
  newRequire.register = function (id, exports) {
    modules[id] = [
      function (require, module) {
        module.exports = exports;
      },
      {},
    ];
  };

  // Only insert newRequire.load when it is actually used.
  // The code in this file is linted against ES5, so dynamic import is not allowed.
  // INSERT_LOAD_HERE

  Object.defineProperty(newRequire, 'root', {
    get: function () {
      return globalObject[parcelRequireName];
    },
  });

  globalObject[parcelRequireName] = newRequire;

  for (var i = 0; i < entry.length; i++) {
    newRequire(entry[i]);
  }

  if (mainEntry) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(mainEntry);

    // CommonJS
    if (typeof exports === 'object' && typeof module !== 'undefined') {
      module.exports = mainExports;

      // RequireJS
    } else if (typeof define === 'function' && define.amd) {
      define(function () {
        return mainExports;
      });
    }
  }
})({"jLuuR":[function(require,module,exports,__globalThis) {
var global = arguments[3];
var HMR_HOST = null;
var HMR_PORT = null;
var HMR_SERVER_PORT = 40423;
var HMR_SECURE = false;
var HMR_ENV_HASH = "439701173a9199ea";
var HMR_USE_SSE = false;
module.bundle.HMR_BUNDLE_ID = "56d3df0137796bd9";
"use strict";
/* global HMR_HOST, HMR_PORT, HMR_SERVER_PORT, HMR_ENV_HASH, HMR_SECURE, HMR_USE_SSE, chrome, browser, __parcel__import__, __parcel__importScripts__, ServiceWorkerGlobalScope */ /*::
import type {
  HMRAsset,
  HMRMessage,
} from '@parcel/reporter-dev-server/src/HMRServer.js';
interface ParcelRequire {
  (string): mixed;
  cache: {|[string]: ParcelModule|};
  hotData: {|[string]: mixed|};
  Module: any;
  parent: ?ParcelRequire;
  isParcelRequire: true;
  modules: {|[string]: [Function, {|[string]: string|}]|};
  HMR_BUNDLE_ID: string;
  root: ParcelRequire;
}
interface ParcelModule {
  hot: {|
    data: mixed,
    accept(cb: (Function) => void): void,
    dispose(cb: (mixed) => void): void,
    // accept(deps: Array<string> | string, cb: (Function) => void): void,
    // decline(): void,
    _acceptCallbacks: Array<(Function) => void>,
    _disposeCallbacks: Array<(mixed) => void>,
  |};
}
interface ExtensionContext {
  runtime: {|
    reload(): void,
    getURL(url: string): string;
    getManifest(): {manifest_version: number, ...};
  |};
}
declare var module: {bundle: ParcelRequire, ...};
declare var HMR_HOST: string;
declare var HMR_PORT: string;
declare var HMR_SERVER_PORT: string;
declare var HMR_ENV_HASH: string;
declare var HMR_SECURE: boolean;
declare var HMR_USE_SSE: boolean;
declare var chrome: ExtensionContext;
declare var browser: ExtensionContext;
declare var __parcel__import__: (string) => Promise<void>;
declare var __parcel__importScripts__: (string) => Promise<void>;
declare var globalThis: typeof self;
declare var ServiceWorkerGlobalScope: Object;
*/ var OVERLAY_ID = '__parcel__error__overlay__';
var OldModule = module.bundle.Module;
function Module(moduleName) {
    OldModule.call(this, moduleName);
    this.hot = {
        data: module.bundle.hotData[moduleName],
        _acceptCallbacks: [],
        _disposeCallbacks: [],
        accept: function(fn) {
            this._acceptCallbacks.push(fn || function() {});
        },
        dispose: function(fn) {
            this._disposeCallbacks.push(fn);
        }
    };
    module.bundle.hotData[moduleName] = undefined;
}
module.bundle.Module = Module;
module.bundle.hotData = {};
var checkedAssets /*: {|[string]: boolean|} */ , disposedAssets /*: {|[string]: boolean|} */ , assetsToDispose /*: Array<[ParcelRequire, string]> */ , assetsToAccept /*: Array<[ParcelRequire, string]> */ , bundleNotFound = false;
function getHostname() {
    return HMR_HOST || (typeof location !== 'undefined' && location.protocol.indexOf('http') === 0 ? location.hostname : 'localhost');
}
function getPort() {
    return HMR_PORT || (typeof location !== 'undefined' ? location.port : HMR_SERVER_PORT);
}
// eslint-disable-next-line no-redeclare
let WebSocket = globalThis.WebSocket;
if (!WebSocket && typeof module.bundle.root === 'function') try {
    // eslint-disable-next-line no-global-assign
    WebSocket = module.bundle.root('ws');
} catch  {
// ignore.
}
var hostname = getHostname();
var port = getPort();
var protocol = HMR_SECURE || typeof location !== 'undefined' && location.protocol === 'https:' && ![
    'localhost',
    '127.0.0.1',
    '0.0.0.0'
].includes(hostname) ? 'wss' : 'ws';
// eslint-disable-next-line no-redeclare
var parent = module.bundle.parent;
if (!parent || !parent.isParcelRequire) {
    // Web extension context
    var extCtx = typeof browser === 'undefined' ? typeof chrome === 'undefined' ? null : chrome : browser;
    // Safari doesn't support sourceURL in error stacks.
    // eval may also be disabled via CSP, so do a quick check.
    var supportsSourceURL = false;
    try {
        (0, eval)('throw new Error("test"); //# sourceURL=test.js');
    } catch (err) {
        supportsSourceURL = err.stack.includes('test.js');
    }
    var ws;
    if (HMR_USE_SSE) ws = new EventSource('/__parcel_hmr');
    else try {
        // If we're running in the dev server's node runner, listen for messages on the parent port.
        let { workerData, parentPort } = module.bundle.root('node:worker_threads') /*: any*/ ;
        if (workerData !== null && workerData !== void 0 && workerData.__parcel) {
            parentPort.on('message', async (message)=>{
                try {
                    await handleMessage(message);
                    parentPort.postMessage('updated');
                } catch  {
                    parentPort.postMessage('restart');
                }
            });
            // After the bundle has finished running, notify the dev server that the HMR update is complete.
            queueMicrotask(()=>parentPort.postMessage('ready'));
        }
    } catch  {
        if (typeof WebSocket !== 'undefined') try {
            ws = new WebSocket(protocol + '://' + hostname + (port ? ':' + port : '') + '/');
        } catch (err) {
            // Ignore cloudflare workers error.
            if (err.message && !err.message.includes('Disallowed operation called within global scope')) console.error(err.message);
        }
    }
    if (ws) {
        // $FlowFixMe
        ws.onmessage = async function(event /*: {data: string, ...} */ ) {
            var data /*: HMRMessage */  = JSON.parse(event.data);
            await handleMessage(data);
        };
        if (ws instanceof WebSocket) {
            ws.onerror = function(e) {
                if (e.message) console.error(e.message);
            };
            ws.onclose = function() {
                console.warn("[parcel] \uD83D\uDEA8 Connection to the HMR server was lost");
            };
        }
    }
}
async function handleMessage(data /*: HMRMessage */ ) {
    checkedAssets = {} /*: {|[string]: boolean|} */ ;
    disposedAssets = {} /*: {|[string]: boolean|} */ ;
    assetsToAccept = [];
    assetsToDispose = [];
    bundleNotFound = false;
    if (data.type === 'reload') fullReload();
    else if (data.type === 'update') {
        // Remove error overlay if there is one
        if (typeof document !== 'undefined') removeErrorOverlay();
        let assets = data.assets;
        // Handle HMR Update
        let handled = assets.every((asset)=>{
            return asset.type === 'css' || asset.type === 'js' && hmrAcceptCheck(module.bundle.root, asset.id, asset.depsByBundle);
        });
        // Dispatch a custom event in case a bundle was not found. This might mean
        // an asset on the server changed and we should reload the page. This event
        // gives the client an opportunity to refresh without losing state
        // (e.g. via React Server Components). If e.preventDefault() is not called,
        // we will trigger a full page reload.
        if (handled && bundleNotFound && assets.some((a)=>a.envHash !== HMR_ENV_HASH) && typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') handled = !window.dispatchEvent(new CustomEvent('parcelhmrreload', {
            cancelable: true
        }));
        if (handled) {
            console.clear();
            // Dispatch custom event so other runtimes (e.g React Refresh) are aware.
            if (typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') window.dispatchEvent(new CustomEvent('parcelhmraccept'));
            await hmrApplyUpdates(assets);
            hmrDisposeQueue();
            // Run accept callbacks. This will also re-execute other disposed assets in topological order.
            let processedAssets = {};
            for(let i = 0; i < assetsToAccept.length; i++){
                let id = assetsToAccept[i][1];
                if (!processedAssets[id]) {
                    hmrAccept(assetsToAccept[i][0], id);
                    processedAssets[id] = true;
                }
            }
        } else fullReload();
    }
    if (data.type === 'error') {
        // Log parcel errors to console
        for (let ansiDiagnostic of data.diagnostics.ansi){
            let stack = ansiDiagnostic.codeframe ? ansiDiagnostic.codeframe : ansiDiagnostic.stack;
            console.error("\uD83D\uDEA8 [parcel]: " + ansiDiagnostic.message + '\n' + stack + '\n\n' + ansiDiagnostic.hints.join('\n'));
        }
        if (typeof document !== 'undefined') {
            // Render the fancy html overlay
            removeErrorOverlay();
            var overlay = createErrorOverlay(data.diagnostics.html);
            // $FlowFixMe
            document.body.appendChild(overlay);
        }
    }
}
function removeErrorOverlay() {
    var overlay = document.getElementById(OVERLAY_ID);
    if (overlay) {
        overlay.remove();
        console.log("[parcel] \u2728 Error resolved");
    }
}
function createErrorOverlay(diagnostics) {
    var overlay = document.createElement('div');
    overlay.id = OVERLAY_ID;
    let errorHTML = '<div style="background: black; opacity: 0.85; font-size: 16px; color: white; position: fixed; height: 100%; width: 100%; top: 0px; left: 0px; padding: 30px; font-family: Menlo, Consolas, monospace; z-index: 9999;">';
    for (let diagnostic of diagnostics){
        let stack = diagnostic.frames.length ? diagnostic.frames.reduce((p, frame)=>{
            return `${p}
<a href="${protocol === 'wss' ? 'https' : 'http'}://${hostname}:${port}/__parcel_launch_editor?file=${encodeURIComponent(frame.location)}" style="text-decoration: underline; color: #888" onclick="fetch(this.href); return false">${frame.location}</a>
${frame.code}`;
        }, '') : diagnostic.stack;
        errorHTML += `
      <div>
        <div style="font-size: 18px; font-weight: bold; margin-top: 20px;">
          \u{1F6A8} ${diagnostic.message}
        </div>
        <pre>${stack}</pre>
        <div>
          ${diagnostic.hints.map((hint)=>"<div>\uD83D\uDCA1 " + hint + '</div>').join('')}
        </div>
        ${diagnostic.documentation ? `<div>\u{1F4DD} <a style="color: violet" href="${diagnostic.documentation}" target="_blank">Learn more</a></div>` : ''}
      </div>
    `;
    }
    errorHTML += '</div>';
    overlay.innerHTML = errorHTML;
    return overlay;
}
function fullReload() {
    if (typeof location !== 'undefined' && 'reload' in location) location.reload();
    else if (typeof extCtx !== 'undefined' && extCtx && extCtx.runtime && extCtx.runtime.reload) extCtx.runtime.reload();
    else try {
        let { workerData, parentPort } = module.bundle.root('node:worker_threads') /*: any*/ ;
        if (workerData !== null && workerData !== void 0 && workerData.__parcel) parentPort.postMessage('restart');
    } catch (err) {
        console.error("[parcel] \u26A0\uFE0F An HMR update was not accepted. Please restart the process.");
    }
}
function getParents(bundle, id) /*: Array<[ParcelRequire, string]> */ {
    var modules = bundle.modules;
    if (!modules) return [];
    var parents = [];
    var k, d, dep;
    for(k in modules)for(d in modules[k][1]){
        dep = modules[k][1][d];
        if (dep === id || Array.isArray(dep) && dep[dep.length - 1] === id) parents.push([
            bundle,
            k
        ]);
    }
    if (bundle.parent) parents = parents.concat(getParents(bundle.parent, id));
    return parents;
}
function updateLink(link) {
    var href = link.getAttribute('href');
    if (!href) return;
    var newLink = link.cloneNode();
    newLink.onload = function() {
        if (link.parentNode !== null) // $FlowFixMe
        link.parentNode.removeChild(link);
    };
    newLink.setAttribute('href', // $FlowFixMe
    href.split('?')[0] + '?' + Date.now());
    // $FlowFixMe
    link.parentNode.insertBefore(newLink, link.nextSibling);
}
var cssTimeout = null;
function reloadCSS() {
    if (cssTimeout || typeof document === 'undefined') return;
    cssTimeout = setTimeout(function() {
        var links = document.querySelectorAll('link[rel="stylesheet"]');
        for(var i = 0; i < links.length; i++){
            // $FlowFixMe[incompatible-type]
            var href /*: string */  = links[i].getAttribute('href');
            var hostname = getHostname();
            var servedFromHMRServer = hostname === 'localhost' ? new RegExp('^(https?:\\/\\/(0.0.0.0|127.0.0.1)|localhost):' + getPort()).test(href) : href.indexOf(hostname + ':' + getPort());
            var absolute = /^https?:\/\//i.test(href) && href.indexOf(location.origin) !== 0 && !servedFromHMRServer;
            if (!absolute) updateLink(links[i]);
        }
        cssTimeout = null;
    }, 50);
}
function hmrDownload(asset) {
    if (asset.type === 'js') {
        if (typeof document !== 'undefined') {
            let script = document.createElement('script');
            script.src = asset.url + '?t=' + Date.now();
            if (asset.outputFormat === 'esmodule') script.type = 'module';
            return new Promise((resolve, reject)=>{
                var _document$head;
                script.onload = ()=>resolve(script);
                script.onerror = reject;
                (_document$head = document.head) === null || _document$head === void 0 || _document$head.appendChild(script);
            });
        } else if (typeof importScripts === 'function') {
            // Worker scripts
            if (asset.outputFormat === 'esmodule') return import(asset.url + '?t=' + Date.now());
            else return new Promise((resolve, reject)=>{
                try {
                    importScripts(asset.url + '?t=' + Date.now());
                    resolve();
                } catch (err) {
                    reject(err);
                }
            });
        }
    }
}
async function hmrApplyUpdates(assets) {
    global.parcelHotUpdate = Object.create(null);
    let scriptsToRemove;
    try {
        // If sourceURL comments aren't supported in eval, we need to load
        // the update from the dev server over HTTP so that stack traces
        // are correct in errors/logs. This is much slower than eval, so
        // we only do it if needed (currently just Safari).
        // https://bugs.webkit.org/show_bug.cgi?id=137297
        // This path is also taken if a CSP disallows eval.
        if (!supportsSourceURL) {
            let promises = assets.map((asset)=>{
                var _hmrDownload;
                return (_hmrDownload = hmrDownload(asset)) === null || _hmrDownload === void 0 ? void 0 : _hmrDownload.catch((err)=>{
                    // Web extension fix
                    if (extCtx && extCtx.runtime && extCtx.runtime.getManifest().manifest_version == 3 && typeof ServiceWorkerGlobalScope != 'undefined' && global instanceof ServiceWorkerGlobalScope) {
                        extCtx.runtime.reload();
                        return;
                    }
                    throw err;
                });
            });
            scriptsToRemove = await Promise.all(promises);
        }
        assets.forEach(function(asset) {
            hmrApply(module.bundle.root, asset);
        });
    } finally{
        delete global.parcelHotUpdate;
        if (scriptsToRemove) scriptsToRemove.forEach((script)=>{
            if (script) {
                var _document$head2;
                (_document$head2 = document.head) === null || _document$head2 === void 0 || _document$head2.removeChild(script);
            }
        });
    }
}
function hmrApply(bundle /*: ParcelRequire */ , asset /*:  HMRAsset */ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (asset.type === 'css') reloadCSS();
    else if (asset.type === 'js') {
        let deps = asset.depsByBundle[bundle.HMR_BUNDLE_ID];
        if (deps) {
            if (modules[asset.id]) {
                // Remove dependencies that are removed and will become orphaned.
                // This is necessary so that if the asset is added back again, the cache is gone, and we prevent a full page reload.
                let oldDeps = modules[asset.id][1];
                for(let dep in oldDeps)if (!deps[dep] || deps[dep] !== oldDeps[dep]) {
                    let id = oldDeps[dep];
                    let parents = getParents(module.bundle.root, id);
                    if (parents.length === 1) hmrDelete(module.bundle.root, id);
                }
            }
            if (supportsSourceURL) // Global eval. We would use `new Function` here but browser
            // support for source maps is better with eval.
            (0, eval)(asset.output);
            // $FlowFixMe
            let fn = global.parcelHotUpdate[asset.id];
            modules[asset.id] = [
                fn,
                deps
            ];
        }
        // Always traverse to the parent bundle, even if we already replaced the asset in this bundle.
        // This is required in case modules are duplicated. We need to ensure all instances have the updated code.
        if (bundle.parent) hmrApply(bundle.parent, asset);
    }
}
function hmrDelete(bundle, id) {
    let modules = bundle.modules;
    if (!modules) return;
    if (modules[id]) {
        // Collect dependencies that will become orphaned when this module is deleted.
        let deps = modules[id][1];
        let orphans = [];
        for(let dep in deps){
            let parents = getParents(module.bundle.root, deps[dep]);
            if (parents.length === 1) orphans.push(deps[dep]);
        }
        // Delete the module. This must be done before deleting dependencies in case of circular dependencies.
        delete modules[id];
        delete bundle.cache[id];
        // Now delete the orphans.
        orphans.forEach((id)=>{
            hmrDelete(module.bundle.root, id);
        });
    } else if (bundle.parent) hmrDelete(bundle.parent, id);
}
function hmrAcceptCheck(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    checkedAssets = {};
    if (hmrAcceptCheckOne(bundle, id, depsByBundle)) return true;
    // Traverse parents breadth first. All possible ancestries must accept the HMR update, or we'll reload.
    let parents = getParents(module.bundle.root, id);
    let accepted = false;
    while(parents.length > 0){
        let v = parents.shift();
        let a = hmrAcceptCheckOne(v[0], v[1], null);
        if (a) // If this parent accepts, stop traversing upward, but still consider siblings.
        accepted = true;
        else if (a !== null) {
            // Otherwise, queue the parents in the next level upward.
            let p = getParents(module.bundle.root, v[1]);
            if (p.length === 0) {
                // If there are no parents, then we've reached an entry without accepting. Reload.
                accepted = false;
                break;
            }
            parents.push(...p);
        }
    }
    return accepted;
}
function hmrAcceptCheckOne(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (depsByBundle && !depsByBundle[bundle.HMR_BUNDLE_ID]) {
        // If we reached the root bundle without finding where the asset should go,
        // there's nothing to do. Mark as "accepted" so we don't reload the page.
        if (!bundle.parent) {
            bundleNotFound = true;
            return true;
        }
        return hmrAcceptCheckOne(bundle.parent, id, depsByBundle);
    }
    if (checkedAssets[id]) return null;
    checkedAssets[id] = true;
    var cached = bundle.cache[id];
    if (!cached) return true;
    assetsToDispose.push([
        bundle,
        id
    ]);
    if (cached && cached.hot && cached.hot._acceptCallbacks.length) {
        assetsToAccept.push([
            bundle,
            id
        ]);
        return true;
    }
    return false;
}
function hmrDisposeQueue() {
    // Dispose all old assets.
    for(let i = 0; i < assetsToDispose.length; i++){
        let id = assetsToDispose[i][1];
        if (!disposedAssets[id]) {
            hmrDispose(assetsToDispose[i][0], id);
            disposedAssets[id] = true;
        }
    }
    assetsToDispose = [];
}
function hmrDispose(bundle /*: ParcelRequire */ , id /*: string */ ) {
    var cached = bundle.cache[id];
    bundle.hotData[id] = {};
    if (cached && cached.hot) cached.hot.data = bundle.hotData[id];
    if (cached && cached.hot && cached.hot._disposeCallbacks.length) cached.hot._disposeCallbacks.forEach(function(cb) {
        cb(bundle.hotData[id]);
    });
    delete bundle.cache[id];
}
function hmrAccept(bundle /*: ParcelRequire */ , id /*: string */ ) {
    // Execute the module.
    bundle(id);
    // Run the accept callbacks in the new version of the module.
    var cached = bundle.cache[id];
    if (cached && cached.hot && cached.hot._acceptCallbacks.length) {
        let assetsToAlsoAccept = [];
        cached.hot._acceptCallbacks.forEach(function(cb) {
            let additionalAssets = cb(function() {
                return getParents(module.bundle.root, id);
            });
            if (Array.isArray(additionalAssets) && additionalAssets.length) assetsToAlsoAccept.push(...additionalAssets);
        });
        if (assetsToAlsoAccept.length) {
            let handled = assetsToAlsoAccept.every(function(a) {
                return hmrAcceptCheck(a[0], a[1]);
            });
            if (!handled) return fullReload();
            hmrDisposeQueue();
        }
    }
}

},{}],"4pvfB":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$c654 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$c654.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$c654.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _richTextMessage = require("./RichTextMessage");
var _richTextMessageDefault = parcelHelpers.interopDefault(_richTextMessage);
var _chatMessageInput = require("./ChatMessageInput");
var _chatMessageInputDefault = parcelHelpers.interopDefault(_chatMessageInput);
var _skeleton = require("./Skeleton");
var _skeletonDefault = parcelHelpers.interopDefault(_skeleton);
var _s = $RefreshSig$();
const Chat = ({ sessionId, onBack, onToggleResearch, selectedModel })=>{
    _s();
    const [messages, setMessages] = (0, _react.useState)([]);
    const [currentMessage, setCurrentMessage] = (0, _react.useState)('');
    const [isLoading, setIsLoading] = (0, _react.useState)(false);
    const [error, setError] = (0, _react.useState)(null);
    const [researchMode, setResearchMode] = (0, _react.useState)(false);
    const messagesEndRef = (0, _react.useRef)(null);
    const inputRef = (0, _react.useRef)(null);
    (0, _react.useEffect)(()=>{
        loadChatSession();
    }, [
        sessionId
    ]);
    (0, _react.useEffect)(()=>{
        scrollToBottom();
    }, [
        messages
    ]);
    const loadChatSession = async ()=>{
        if (!sessionId) return;
        try {
            setIsLoading(true);
            const response = await fetch(`/api/chats/${sessionId}`);
            if (response.ok) {
                const chatData = await response.json();
                setMessages(chatData.messages || []);
                setError(null);
            } else setError('Failed to load chat session');
        } catch (err) {
            setError(`Error loading chat: ${err.message}`);
        } finally{
            setIsLoading(false);
        }
    };
    const scrollToBottom = ()=>{
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    };
    const formatTimestamp = (timestamp)=>{
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    const sendMessage = async ()=>{
        if (!currentMessage.trim() || isLoading) return;
        const userMessage = {
            id: Date.now(),
            type: 'user',
            content: currentMessage.trim(),
            timestamp: new Date()
        };
        setMessages((prev)=>[
                ...prev,
                userMessage
            ]);
        setCurrentMessage('');
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    mode: researchMode ? 'research' : 'chat',
                    project: 'default',
                    model: selectedModel || undefined,
                    history: messages.slice(-10).map((m)=>({
                            type: m.type,
                            content: m.content
                        }))
                })
            });
            if (response.ok) {
                const data = await response.json();
                const aiMessage = {
                    id: Date.now() + 1,
                    type: 'ai',
                    content: data.response,
                    timestamp: new Date()
                };
                setMessages((prev)=>[
                        ...prev,
                        aiMessage
                    ]);
            } else throw new Error(`API error: ${response.status}`);
        } catch (err) {
            setError(`Failed to send message: ${err.message}`);
            setIsLoading(false);
        } finally{
            setIsLoading(false);
        }
    };
    const handleKeyPress = (e)=>{
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };
    const renderMessage = (message)=>{
        if (message.type === 'user') return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
            className: "message user-message",
            children: [
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-content",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "message-text",
                            children: message.content
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 119,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "message-tail"
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 122,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/Chat.js",
                    lineNumber: 118,
                    columnNumber: 11
                }, undefined),
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-meta",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                            className: "timestamp",
                            children: formatTimestamp(message.timestamp)
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 125,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                            className: "message-status",
                            children: "\u2713"
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 126,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/Chat.js",
                    lineNumber: 124,
                    columnNumber: 11
                }, undefined)
            ]
        }, void 0, true, {
            fileName: "src/Chat.js",
            lineNumber: 115,
            columnNumber: 9
        }, undefined);
        else return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
            className: "message ai-message",
            children: [
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-header",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "ai-avatar",
                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "avatar-gradient",
                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "avatar-icon",
                                    children: "\uD83E\uDD16"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 138,
                                    columnNumber: 17
                                }, undefined)
                            }, void 0, false, {
                                fileName: "src/Chat.js",
                                lineNumber: 137,
                                columnNumber: 15
                            }, undefined)
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 136,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "ai-info",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "ai-name",
                                    children: "AI Assistant"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 142,
                                    columnNumber: 15
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "model-badge",
                                    children: selectedModel || 'Llama 3.2'
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 143,
                                    columnNumber: 15
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/Chat.js",
                            lineNumber: 141,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/Chat.js",
                    lineNumber: 135,
                    columnNumber: 11
                }, undefined),
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-content",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "answer-text",
                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _richTextMessageDefault.default), {
                                content: message.content
                            }, void 0, false, {
                                fileName: "src/Chat.js",
                                lineNumber: 149,
                                columnNumber: 15
                            }, undefined)
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 148,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "message-tail"
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 151,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/Chat.js",
                    lineNumber: 147,
                    columnNumber: 11
                }, undefined),
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-meta",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                            className: "timestamp",
                            children: formatTimestamp(message.timestamp)
                        }, void 0, false, {
                            fileName: "src/Chat.js",
                            lineNumber: 155,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "message-actions",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                    className: "action-btn",
                                    title: "Copy message",
                                    children: "\uD83D\uDCCB"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 157,
                                    columnNumber: 15
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                    className: "action-btn",
                                    title: "Regenerate",
                                    children: "\uD83D\uDD04"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 158,
                                    columnNumber: 15
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/Chat.js",
                            lineNumber: 156,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/Chat.js",
                    lineNumber: 154,
                    columnNumber: 11
                }, undefined)
            ]
        }, void 0, true, {
            fileName: "src/Chat.js",
            lineNumber: 132,
            columnNumber: 9
        }, undefined);
    };
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "chat-interface",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "chat-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                        onClick: onBack,
                        className: "back-button",
                        children: "\u2190 Back to Sessions"
                    }, void 0, false, {
                        fileName: "src/Chat.js",
                        lineNumber: 169,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "chat-info",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h3", {
                                children: "Chat Session"
                            }, void 0, false, {
                                fileName: "src/Chat.js",
                                lineNumber: 173,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                children: [
                                    "Session ID: ",
                                    sessionId
                                ]
                            }, void 0, true, {
                                fileName: "src/Chat.js",
                                lineNumber: 174,
                                columnNumber: 11
                            }, undefined),
                            selectedModel && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                children: [
                                    "Model: ",
                                    selectedModel
                                ]
                            }, void 0, true, {
                                fileName: "src/Chat.js",
                                lineNumber: 175,
                                columnNumber: 29
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/Chat.js",
                        lineNumber: 172,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "chat-controls",
                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("label", {
                            className: "research-toggle",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("input", {
                                    type: "checkbox",
                                    checked: researchMode,
                                    onChange: (e)=>setResearchMode(e.target.checked)
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 179,
                                    columnNumber: 13
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "toggle-label",
                                    children: "Deep Research Mode"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 184,
                                    columnNumber: 13
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/Chat.js",
                            lineNumber: 178,
                            columnNumber: 11
                        }, undefined)
                    }, void 0, false, {
                        fileName: "src/Chat.js",
                        lineNumber: 177,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/Chat.js",
                lineNumber: 168,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "chat-container",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "messages-area",
                        children: messages.length === 0 && !isLoading ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "welcome-message",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "welcome-illustration",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "welcome-glow"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 196,
                                            columnNumber: 18
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "welcome-icon",
                                            children: "\uD83D\uDE80"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 197,
                                            columnNumber: 18
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 195,
                                    columnNumber: 16
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h4", {
                                    children: "Welcome to your AI Chat!"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 199,
                                    columnNumber: 16
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                    children: "I'm here to help with questions, research, creative tasks, and more. What would you like to explore today?"
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 200,
                                    columnNumber: 16
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "suggestion-chips",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                            className: "chip",
                                            onClick: ()=>setCurrentMessage("Explain quantum computing in simple terms"),
                                            children: "\uD83D\uDCA1 Explain quantum computing"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 202,
                                            columnNumber: 18
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                            className: "chip",
                                            onClick: ()=>setCurrentMessage("Write a creative story about space exploration"),
                                            children: "\uD83D\uDCD6 Write a story"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 205,
                                            columnNumber: 18
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                            className: "chip",
                                            onClick: ()=>setCurrentMessage("Help me debug this code"),
                                            children: "\uD83D\uDC1B Debug code"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 208,
                                            columnNumber: 18
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                            className: "chip",
                                            onClick: ()=>setResearchMode(true),
                                            children: "\uD83D\uDD2C Research mode"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 211,
                                            columnNumber: 18
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 201,
                                    columnNumber: 16
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/Chat.js",
                            lineNumber: 192,
                            columnNumber: 15
                        }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _jsxDevRuntime.Fragment), {
                            children: [
                                messages.map((message)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        children: renderMessage(message)
                                    }, message.id, false, {
                                        fileName: "src/Chat.js",
                                        lineNumber: 219,
                                        columnNumber: 17
                                    }, undefined)),
                                isLoading && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "message ai-message typing",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-header",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "ai-avatar",
                                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                        className: "avatar-gradient",
                                                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "avatar-icon",
                                                            children: "\uD83E\uDD16"
                                                        }, void 0, false, {
                                                            fileName: "src/Chat.js",
                                                            lineNumber: 231,
                                                            columnNumber: 26
                                                        }, undefined)
                                                    }, void 0, false, {
                                                        fileName: "src/Chat.js",
                                                        lineNumber: 230,
                                                        columnNumber: 24
                                                    }, undefined)
                                                }, void 0, false, {
                                                    fileName: "src/Chat.js",
                                                    lineNumber: 229,
                                                    columnNumber: 22
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "ai-info",
                                                    children: [
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "ai-name",
                                                            children: "AI Assistant"
                                                        }, void 0, false, {
                                                            fileName: "src/Chat.js",
                                                            lineNumber: 235,
                                                            columnNumber: 24
                                                        }, undefined),
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "typing-indicator",
                                                            children: [
                                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                    fileName: "src/Chat.js",
                                                                    lineNumber: 237,
                                                                    columnNumber: 26
                                                                }, undefined),
                                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                    fileName: "src/Chat.js",
                                                                    lineNumber: 238,
                                                                    columnNumber: 26
                                                                }, undefined),
                                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                    fileName: "src/Chat.js",
                                                                    lineNumber: 239,
                                                                    columnNumber: 26
                                                                }, undefined)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "src/Chat.js",
                                                            lineNumber: 236,
                                                            columnNumber: 24
                                                        }, undefined)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/Chat.js",
                                                    lineNumber: 234,
                                                    columnNumber: 22
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 228,
                                            columnNumber: 20
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-content",
                                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                className: "typing-placeholder",
                                                children: [
                                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                        className: "typing-dots",
                                                        children: [
                                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                fileName: "src/Chat.js",
                                                                lineNumber: 246,
                                                                columnNumber: 26
                                                            }, undefined),
                                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                fileName: "src/Chat.js",
                                                                lineNumber: 247,
                                                                columnNumber: 26
                                                            }, undefined),
                                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                                fileName: "src/Chat.js",
                                                                lineNumber: 248,
                                                                columnNumber: 26
                                                            }, undefined)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "src/Chat.js",
                                                        lineNumber: 245,
                                                        columnNumber: 24
                                                    }, undefined),
                                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                        className: "typing-text",
                                                        children: "AI is thinking..."
                                                    }, void 0, false, {
                                                        fileName: "src/Chat.js",
                                                        lineNumber: 250,
                                                        columnNumber: 24
                                                    }, undefined)
                                                ]
                                            }, void 0, true, {
                                                fileName: "src/Chat.js",
                                                lineNumber: 244,
                                                columnNumber: 22
                                            }, undefined)
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 243,
                                            columnNumber: 20
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 225,
                                    columnNumber: 19
                                }, undefined),
                                error && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "error-message",
                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                        children: [
                                            "\u26A0\uFE0F ",
                                            error
                                        ]
                                    }, void 0, true, {
                                        fileName: "src/Chat.js",
                                        lineNumber: 258,
                                        columnNumber: 19
                                    }, undefined)
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 257,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    ref: messagesEndRef
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 262,
                                    columnNumber: 15
                                }, undefined)
                            ]
                        }, void 0, true)
                    }, void 0, false, {
                        fileName: "src/Chat.js",
                        lineNumber: 190,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "input-area",
                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "message-input-container",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _chatMessageInputDefault.default), {
                                    onSendMessage: (message)=>{
                                        // For now, treat as plain text. Later can parse HTML if needed
                                        setCurrentMessage(message);
                                        sendMessage();
                                    },
                                    placeholder: researchMode ? "Ask a research question..." : "Type your message..."
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 269,
                                    columnNumber: 15
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "input-actions",
                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                        className: `mode-toggle ${researchMode ? 'active' : ''}`,
                                        onClick: ()=>setResearchMode(!researchMode),
                                        title: researchMode ? 'Switch to chat mode' : 'Switch to research mode',
                                        disabled: isLoading,
                                        children: researchMode ? "\uD83D\uDD2C" : "\uD83D\uDCAC"
                                    }, void 0, false, {
                                        fileName: "src/Chat.js",
                                        lineNumber: 278,
                                        columnNumber: 17
                                    }, undefined)
                                }, void 0, false, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 277,
                                    columnNumber: 15
                                }, undefined),
                                researchMode && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "research-notice",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                            className: "notice-icon",
                                            children: "\uD83D\uDD2C"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 289,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                            className: "notice-text",
                                            children: "Research mode enabled - This may take longer for comprehensive analysis"
                                        }, void 0, false, {
                                            fileName: "src/Chat.js",
                                            lineNumber: 290,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/Chat.js",
                                    lineNumber: 288,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/Chat.js",
                            lineNumber: 268,
                            columnNumber: 13
                        }, undefined)
                    }, void 0, false, {
                        fileName: "src/Chat.js",
                        lineNumber: 267,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/Chat.js",
                lineNumber: 189,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("style", {
                children: `
         .chat-interface {
           height: 100%;
           display: flex;
           flex-direction: column;
           background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
         }

         .chat-header {
           display: flex;
           align-items: center;
           gap: clamp(15px, 3vw, 20px);
           padding: clamp(15px, 3vw, 20px);
           border-bottom: 1px solid var(--border-color);
           background: var(--bg-primary);
           backdrop-filter: blur(10px);
           box-shadow: 0 2px 20px var(--shadow);
           flex-wrap: wrap;
         }

         .back-button {
           padding: clamp(8px, 2vw, 10px) clamp(16px, 3vw, 20px);
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           border: none;
           border-radius: clamp(8px, 2vw, 12px);
           cursor: pointer;
           font-size: clamp(12px, 2.5vw, 14px);
           font-weight: 600;
           white-space: nowrap;
           transition: all 0.2s ease;
           box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
         }

         .back-button:hover {
           transform: translateY(-2px);
           box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
         }

         .chat-info h3 {
           margin: 0;
           color: var(--text-primary);
           font-size: clamp(18px, 3vw, 20px);
           font-weight: 600;
           background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           background-clip: text;
         }

         .chat-info p {
           margin: clamp(4px, 1vh, 6px) 0 0 0;
           color: var(--text-secondary);
           font-size: clamp(12px, 2.5vw, 14px);
         }

         .chat-controls {
           margin-left: auto;
           display: flex;
           align-items: center;
           gap: 15px;
         }

         .research-toggle {
           display: flex;
           align-items: center;
           gap: clamp(8px, 2vw, 10px);
           cursor: pointer;
           font-size: clamp(12px, 2.5vw, 14px);
           color: var(--text-secondary);
           padding: 8px 12px;
           border-radius: 20px;
           transition: all 0.2s ease;
           background: var(--bg-tertiary);
         }

         .research-toggle:hover {
           background: var(--bg-secondary);
         }

         .research-toggle input[type="checkbox"] {
           width: clamp(16px, 3vw, 18px);
           height: clamp(16px, 3vw, 18px);
           accent-color: var(--accent);
         }

         .toggle-label {
           font-weight: 500;
         }

         .chat-container {
           flex: 1;
           display: flex;
           flex-direction: column;
           overflow: hidden;
         }

         .messages-area {
           flex: 1;
           overflow-y: auto;
           padding: clamp(20px, 3vw, 24px);
           display: flex;
           flex-direction: column;
           gap: clamp(20px, 3vh, 24px);
           scroll-behavior: smooth;
         }

         .messages-area::-webkit-scrollbar {
           width: 6px;
         }

         .messages-area::-webkit-scrollbar-track {
           background: var(--bg-tertiary);
           border-radius: 3px;
         }

         .messages-area::-webkit-scrollbar-thumb {
           background: var(--border-color);
           border-radius: 3px;
         }

         .messages-area::-webkit-scrollbar-thumb:hover {
           background: var(--text-muted);
         }

         .welcome-message {
           text-align: center;
           padding: clamp(60px, 20vh, 80px) clamp(20px, 5vw, 24px);
           color: var(--text-secondary);
           max-width: 600px;
           margin: 0 auto;
         }

         .welcome-illustration {
           position: relative;
           display: inline-block;
           margin-bottom: clamp(24px, 6vh, 32px);
         }

         .welcome-glow {
           position: absolute;
           top: -10px;
           left: -10px;
           right: -10px;
           bottom: -10px;
           background: radial-gradient(circle, rgba(74, 144, 226, 0.3) 0%, transparent 70%);
           border-radius: 50%;
           animation: pulse 2s ease-in-out infinite;
         }

         .welcome-icon {
           font-size: clamp(48px, 12vw, 64px);
           position: relative;
           z-index: 1;
           animation: float 3s ease-in-out infinite;
         }

         @keyframes pulse {
           0%, 100% { transform: scale(1); opacity: 0.7; }
           50% { transform: scale(1.1); opacity: 1; }
         }

         @keyframes float {
           0%, 100% { transform: translateY(0px); }
           50% { transform: translateY(-10px); }
         }

         .welcome-message h4 {
           margin: 0 0 clamp(12px, 3vh, 16px) 0;
           color: var(--text-primary);
           font-size: clamp(24px, 5vw, 28px);
           font-weight: 600;
         }

         .welcome-message p {
           margin: 0 0 clamp(24px, 6vh, 32px) 0;
           font-size: clamp(16px, 3vw, 18px);
           line-height: 1.6;
         }

         .suggestion-chips {
           display: flex;
           flex-wrap: wrap;
           gap: 12px;
           justify-content: center;
         }

         .chip {
           padding: 10px 16px;
           background: var(--bg-primary);
           border: 1px solid var(--border-color);
           border-radius: 20px;
           color: var(--text-primary);
           font-size: 14px;
           cursor: pointer;
           transition: all 0.2s ease;
           white-space: nowrap;
           box-shadow: 0 2px 8px var(--shadow);
         }

         .chip:hover {
           transform: translateY(-2px);
           box-shadow: 0 4px 16px var(--shadow);
           border-color: var(--accent);
         }

         .message {
           display: flex;
           flex-direction: column;
           gap: clamp(8px, 2vh, 10px);
           max-width: min(85%, 700px);
           width: 100%;
           position: relative;
         }

         .user-message {
           align-self: flex-end;
           align-items: flex-end;
         }

         .ai-message {
           align-self: flex-start;
           align-items: flex-start;
         }

         .message-header {
           display: flex;
           align-items: center;
           gap: clamp(10px, 2vw, 12px);
           margin-bottom: 4px;
         }

         .ai-avatar {
           position: relative;
         }

         .avatar-gradient {
           width: clamp(36px, 7vw, 40px);
           height: clamp(36px, 7vw, 40px);
           border-radius: 50%;
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           display: flex;
           align-items: center;
           justify-content: center;
           box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
           transition: all 0.2s ease;
         }

         .avatar-gradient:hover {
           transform: scale(1.1);
         }

         .avatar-icon {
           font-size: clamp(16px, 3vw, 18px);
           filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
         }

         .ai-name {
           font-weight: 600;
           color: var(--text-primary);
           font-size: clamp(15px, 2.5vw, 16px);
         }

         .model-badge {
           font-size: 11px;
           color: var(--text-muted);
           background: var(--bg-tertiary);
           padding: 2px 6px;
           border-radius: 8px;
           margin-left: 8px;
           font-weight: 500;
         }

         .typing-indicator {
           display: flex;
           gap: 2px;
           margin-left: 8px;
         }

         .typing-indicator span {
           width: 4px;
           height: 4px;
           border-radius: 50%;
           background: var(--accent);
           animation: typing 1.4s ease-in-out infinite;
         }

         .typing-indicator span:nth-child(1) { animation-delay: 0s; }
         .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
         .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

         @keyframes typing {
           0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
           30% { transform: scale(1); opacity: 1; }
         }

         .message-content {
           position: relative;
           padding: clamp(16px, 3vw, 20px);
           border-radius: clamp(16px, 4vw, 20px);
           background: var(--bg-primary);
           border: 1px solid var(--border-color);
           box-shadow: 0 4px 20px var(--shadow);
           word-wrap: break-word;
           overflow-wrap: break-word;
           transition: all 0.2s ease;
         }

         .user-message .message-content {
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           border: none;
           box-shadow: 0 4px 20px rgba(0, 123, 255, 0.3);
         }

         .message-tail {
           position: absolute;
           width: 0;
           height: 0;
           border: 8px solid transparent;
         }

         .user-message .message-tail {
           right: -8px;
           bottom: 16px;
           border-left-color: #4dabf7;
           border-right: none;
         }

         .ai-message .message-tail {
           left: -8px;
           bottom: 16px;
           border-right-color: var(--bg-primary);
           border-left: none;
         }

         .message-text {
           line-height: 1.6;
           font-size: clamp(15px, 2.5vw, 16px);
           white-space: pre-wrap;
         }

         .answer-text {
           line-height: 1.7;
           font-size: clamp(15px, 2.5vw, 16px);
         }

         .typing-placeholder {
           display: flex;
           align-items: center;
           gap: 12px;
           color: var(--text-secondary);
           font-style: italic;
         }

         .typing-dots {
           display: flex;
           gap: 4px;
         }

         .typing-dots span {
           width: 6px;
           height: 6px;
           border-radius: 50%;
           background: var(--accent);
           animation: typing-dots 1.4s ease-in-out infinite;
         }

         .typing-dots span:nth-child(1) { animation-delay: 0s; }
         .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
         .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

         @keyframes typing-dots {
           0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
           30% { transform: scale(1.2); opacity: 1; }
         }

         .typing-text {
           font-size: 14px;
         }

         .message-meta {
           display: flex;
           align-items: center;
           justify-content: space-between;
           font-size: clamp(11px, 2vw, 12px);
           color: var(--text-muted);
           padding: 0 clamp(4px, 1vw, 6px);
           margin-top: 4px;
         }

         .user-message .message-meta {
           justify-content: flex-end;
         }

         .message-status {
           margin-left: 8px;
           color: #28a745;
           font-weight: bold;
         }

         .message-actions {
           display: flex;
           gap: 6px;
         }

         .action-btn {
           background: none;
           border: none;
           color: var(--text-muted);
           cursor: pointer;
           padding: 4px;
           border-radius: 4px;
           font-size: 12px;
           transition: all 0.2s ease;
           opacity: 0.7;
         }

         .action-btn:hover {
           background: var(--bg-tertiary);
           opacity: 1;
           transform: scale(1.1);
         }

         .error-message {
           padding: 16px;
           background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
           border: 1px solid var(--error);
           border-radius: 12px;
           color: var(--error);
           text-align: center;
           box-shadow: 0 4px 16px rgba(220, 53, 69, 0.1);
           backdrop-filter: blur(10px);
         }

         .input-area {
           padding: clamp(20px, 3vw, 24px);
           border-top: 1px solid var(--border-color);
           background: var(--bg-primary);
           backdrop-filter: blur(10px);
           box-shadow: 0 -4px 20px var(--shadow);
         }

         .message-input-container {
           max-width: 900px;
           margin: 0 auto;
         }

         .input-wrapper {
           display: flex;
           align-items: flex-end;
           gap: 12px;
           background: var(--bg-secondary);
           border: 2px solid var(--border-color);
           border-radius: 24px;
           padding: 4px;
           transition: all 0.2s ease;
           box-shadow: 0 4px 16px var(--shadow);
         }

         .input-wrapper:focus-within {
           border-color: var(--accent);
           box-shadow: 0 4px 24px rgba(0, 123, 255, 0.2);
         }

         .message-input {
           flex: 1;
           padding: 16px 20px;
           border: none;
           background: transparent;
           color: var(--text-primary);
           font-size: 16px;
           font-family: inherit;
           resize: none;
           min-height: 20px;
           max-height: 120px;
           line-height: 1.5;
           outline: none;
         }

         .message-input::placeholder {
           color: var(--text-secondary);
         }

         .message-input:disabled {
           opacity: 0.6;
           cursor: not-allowed;
         }

         .input-actions {
           display: flex;
           align-items: center;
           gap: 8px;
           padding-right: 8px;
         }

         .mode-toggle {
           width: 40px;
           height: 40px;
           border: none;
           border-radius: 50%;
           background: var(--bg-tertiary);
           color: var(--text-secondary);
           cursor: pointer;
           display: flex;
           align-items: center;
           justify-content: center;
           font-size: 18px;
           transition: all 0.2s ease;
         }

         .mode-toggle:hover:not(:disabled) {
           background: var(--bg-primary);
           transform: scale(1.1);
         }

         .mode-toggle.active {
           background: var(--accent);
           color: white;
           box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
         }

         .mode-toggle:disabled {
           opacity: 0.5;
           cursor: not-allowed;
         }

         .send-button {
           width: 48px;
           height: 48px;
           border: none;
           border-radius: 50%;
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           cursor: pointer;
           display: flex;
           align-items: center;
           justify-content: center;
           font-size: 18px;
           transition: all 0.2s ease;
           box-shadow: 0 4px 16px rgba(0, 123, 255, 0.3);
         }

         .send-button:hover:not(:disabled) {
           transform: scale(1.1);
           box-shadow: 0 6px 24px rgba(0, 123, 255, 0.4);
         }

         .send-button:disabled {
           background: var(--text-secondary);
           cursor: not-allowed;
           transform: none;
           box-shadow: none;
         }

         .send-spinner {
           width: 20px;
           height: 20px;
           border: 2px solid rgba(255, 255, 255, 0.3);
           border-top: 2px solid white;
           border-radius: 50%;
           animation: spin 1s linear infinite;
         }

         @keyframes spin {
           0% { transform: rotate(0deg); }
           50% { transform: rotate(180deg); }
           100% { transform: rotate(360deg); }
         }

         .research-notice {
           display: flex;
           align-items: center;
           gap: 8px;
           margin-top: 12px;
           padding: 10px 16px;
           background: rgba(255, 193, 7, 0.1);
           border: 1px solid var(--warning);
           border-radius: 12px;
           color: var(--text-primary);
           font-size: 14px;
         }

         .notice-icon {
           font-size: 16px;
         }

         .notice-text {
           flex: 1;
         }

         /* Responsive Design */
         @media (max-width: 768px) {
           .chat-header {
             flex-direction: column;
             gap: 16px;
             align-items: stretch;
             padding: 16px;
           }

           .chat-controls {
             margin-left: 0;
             justify-content: center;
           }

           .messages-area {
             padding: 16px;
             gap: 16px;
           }

           .message {
             max-width: 100%;
           }

           .message-content {
             padding: 14px;
           }

           .input-area {
             padding: 16px;
           }

           .input-wrapper {
             flex-direction: column;
             gap: 8px;
             border-radius: 16px;
           }

           .input-actions {
             justify-content: space-between;
             padding: 8px 16px 0 16px;
           }

           .message-input {
             padding: 12px 16px;
           }

           .suggestion-chips {
             flex-direction: column;
             align-items: center;
           }

           .chip {
             width: 100%;
             max-width: 280px;
             justify-content: center;
           }
         }

         @media (max-width: 480px) {
           .welcome-message {
             padding: 40px 16px;
           }

           .welcome-icon {
             font-size: 48px;
           }

           .suggestion-chips {
             gap: 8px;
           }

           .chip {
             padding: 8px 12px;
             font-size: 13px;
           }

           .research-notice {
             flex-direction: column;
             text-align: center;
             gap: 6px;
           }
         }
       `
            }, void 0, false, {
                fileName: "src/Chat.js",
                lineNumber: 297,
                columnNumber: 8
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/Chat.js",
        lineNumber: 167,
        columnNumber: 5
    }, undefined);
};
_s(Chat, "SA2M2dven9SBPXCJLPwH+Fb3DD0=");
_c = Chat;
exports.default = Chat;
var _c;
$RefreshReg$(_c, "Chat");

  $parcel$ReactRefreshHelpers$c654.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","./RichTextMessage":"flq1Y","./ChatMessageInput":"khw0j","./Skeleton":"kExCx","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"flq1Y":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$e60f = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$e60f.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$e60f.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
const RichTextMessage = /*#__PURE__*/ (0, _reactDefault.default).memo(_c = ({ content, isEditable = false, onChange, placeholder = "Type your message..." })=>{
    // Convert markdown-like syntax to HTML for display
    const convertMarkdownToHtml = (text)=>{
        if (!text) return '';
        return text// Code blocks (must come first)
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')// Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>').replace(/^## (.*$)/gim, '<h2>$1</h2>').replace(/^# (.*$)/gim, '<h1>$1</h1>')// Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')// Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')// Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')// Lists (convert to proper HTML)
        .replace(/^\* (.*$)/gim, '<li>$1</li>').replace(/^\d+\. (.*$)/gim, '<li>$1</li>')// Line breaks
        .replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>')// Horizontal rules
        .replace(/^---$/gm, '<hr>')// Wrap in paragraphs if not already wrapped
        .replace(/^([^<].*?)(<|$)/gm, '<p>$1</p>$2');
    };
    // For display mode, convert markdown and render as HTML
    if (!isEditable) {
        const htmlContent = convertMarkdownToHtml(content);
        return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
            className: "rich-text-display",
            dangerouslySetInnerHTML: {
                __html: htmlContent
            }
        }, void 0, false, {
            fileName: "src/RichTextMessage.js",
            lineNumber: 42,
            columnNumber: 7
        }, undefined);
    }
    // For editing mode, use simple textarea for now
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("textarea", {
        value: content,
        onChange: (e)=>onChange(e.target.value),
        placeholder: placeholder,
        className: "rich-text-editor",
        rows: 4
    }, void 0, false, {
        fileName: "src/RichTextMessage.js",
        lineNumber: 51,
        columnNumber: 5
    }, undefined);
});
_c1 = RichTextMessage;
RichTextMessage.displayName = 'RichTextMessage';
exports.default = RichTextMessage;
var _c, _c1;
$RefreshReg$(_c, "RichTextMessage$React.memo");
$RefreshReg$(_c1, "RichTextMessage");

  $parcel$ReactRefreshHelpers$e60f.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"khw0j":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$6b0b = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$6b0b.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$6b0b.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _s = $RefreshSig$();
const ChatMessageInput = ({ onSendMessage, placeholder = "Type your message..." })=>{
    _s();
    const [content, setContent] = (0, _react.useState)('');
    const editorRef = (0, _react.useRef)(null);
    const handleInput = (0, _react.useCallback)(()=>{
        if (editorRef.current) setContent(editorRef.current.innerHTML);
    }, []);
    const handleKeyDown = (0, _react.useCallback)((e)=>{
        if (e.ctrlKey || e.metaKey) switch(e.key){
            case 'b':
                e.preventDefault();
                execCommand('bold');
                break;
            case 'i':
                e.preventDefault();
                execCommand('italic');
                break;
            case 'u':
                e.preventDefault();
                execCommand('underline');
                break;
            case 'k':
                e.preventDefault();
                insertLink();
                break;
            default:
                break;
        }
    }, []);
    const handlePaste = (0, _react.useCallback)((e)=>{
        e.preventDefault();
        const text = e.clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
    }, []);
    const handleSubmit = (e)=>{
        e.preventDefault();
        const text = editorRef.current ? editorRef.current.textContent.trim() : '';
        if (text) {
            onSendMessage(text);
            if (editorRef.current) editorRef.current.innerHTML = '';
            setContent('');
        }
    };
    const execCommand = (command, value = null)=>{
        document.execCommand(command, false, value);
        editorRef.current?.focus();
    };
    const isCommandActive = (command)=>{
        return document.queryCommandState(command);
    };
    const insertCode = ()=>{
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const codeElement = document.createElement('code');
            codeElement.textContent = selection.toString() || 'code';
            range.deleteContents();
            range.insertNode(codeElement);
            setContent(editorRef.current.innerHTML);
        }
        editorRef.current?.focus();
    };
    const insertLink = ()=>{
        const url = prompt('Enter URL:');
        if (url) execCommand('createLink', url);
    };
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("form", {
        onSubmit: handleSubmit,
        className: "chat-input-form",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "rich-text-toolbar",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "toolbar-group",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('bold'),
                                title: "Bold",
                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("strong", {
                                    children: "B"
                                }, void 0, false, {
                                    fileName: "src/ChatMessageInput.js",
                                    lineNumber: 89,
                                    columnNumber: 82
                                }, undefined)
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 89,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('italic'),
                                title: "Italic",
                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("em", {
                                    children: "I"
                                }, void 0, false, {
                                    fileName: "src/ChatMessageInput.js",
                                    lineNumber: 90,
                                    columnNumber: 86
                                }, undefined)
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 90,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('underline'),
                                title: "Underline",
                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("u", {
                                    children: "U"
                                }, void 0, false, {
                                    fileName: "src/ChatMessageInput.js",
                                    lineNumber: 91,
                                    columnNumber: 92
                                }, undefined)
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 91,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatMessageInput.js",
                        lineNumber: 88,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "toolbar-group",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('formatBlock', 'h1'),
                                title: "Heading 1",
                                children: "H1"
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 94,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('formatBlock', 'h2'),
                                title: "Heading 2",
                                children: "H2"
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 95,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('formatBlock', 'blockquote'),
                                title: "Quote",
                                children: '"'
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 96,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatMessageInput.js",
                        lineNumber: 93,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "toolbar-group",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: insertCode,
                                title: "Code",
                                children: "` `"
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 99,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: insertLink,
                                title: "Link",
                                children: "\uD83D\uDD17"
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 100,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatMessageInput.js",
                        lineNumber: 98,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "toolbar-group",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('insertUnorderedList'),
                                title: "Bullet List",
                                children: "\u2022"
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 103,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                type: "button",
                                onClick: ()=>execCommand('insertOrderedList'),
                                title: "Numbered List",
                                children: "1."
                            }, void 0, false, {
                                fileName: "src/ChatMessageInput.js",
                                lineNumber: 104,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatMessageInput.js",
                        lineNumber: 102,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/ChatMessageInput.js",
                lineNumber: 87,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                ref: editorRef,
                contentEditable: true,
                className: "rich-text-editor",
                onInput: handleInput,
                onKeyDown: handleKeyDown,
                onPaste: handlePaste,
                "data-placeholder": placeholder,
                suppressContentEditableWarning: true
            }, void 0, false, {
                fileName: "src/ChatMessageInput.js",
                lineNumber: 107,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                type: "submit",
                className: "send-button",
                children: "Send"
            }, void 0, false, {
                fileName: "src/ChatMessageInput.js",
                lineNumber: 117,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("style", {
                jsx: true,
                children: `
        .rich-text-toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 8px;
          padding: 8px;
          background: var(--bg-secondary, #f8f9fa);
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 6px;
        }
        .toolbar-group {
          display: flex;
          gap: 2px;
          border-right: 1px solid var(--border-color, #dee2e6);
          padding-right: 8px;
        }
        .toolbar-group:last-child {
          border-right: none;
          padding-right: 0;
        }
        .rich-text-toolbar button {
          padding: 6px 10px;
          border: 1px solid var(--border-color, #dee2e6);
          background: var(--bg-primary, white);
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          color: var(--text-primary, #212529);
          transition: all 0.2s ease;
        }
        .rich-text-toolbar button:hover {
          background: var(--accent, #007bff);
          color: white;
          border-color: var(--accent, #007bff);
        }
        .rich-text-toolbar button:active {
          transform: scale(0.95);
        }
        .rich-text-editor {
          min-height: 80px;
          padding: 12px;
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 6px;
          outline: none;
          overflow-y: auto;
          background: var(--bg-primary, white);
          color: var(--text-primary, #212529);
          line-height: 1.5;
          font-family: inherit;
        }
        .rich-text-editor:focus {
          border-color: var(--accent, #007bff);
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        .rich-text-editor:empty:before {
          content: attr(data-placeholder);
          color: var(--text-secondary, #6c757d);
          pointer-events: none;
        }
        .send-button {
          margin-top: 12px;
          padding: 10px 20px;
          background: linear-gradient(135deg, var(--accent, #007bff), #0056b3);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        .send-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }
        .send-button:active {
          transform: translateY(0);
        }
      `
            }, void 0, false, {
                fileName: "src/ChatMessageInput.js",
                lineNumber: 120,
                columnNumber: 7
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/ChatMessageInput.js",
        lineNumber: 86,
        columnNumber: 5
    }, undefined);
};
_s(ChatMessageInput, "h0+X2NILzBYf7L9zdwZgtGLapzE=");
_c = ChatMessageInput;
exports.default = ChatMessageInput;
var _c;
$RefreshReg$(_c, "ChatMessageInput");

  $parcel$ReactRefreshHelpers$6b0b.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"kExCx":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$5663 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$5663.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$5663.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "SkeletonText", ()=>SkeletonText);
parcelHelpers.export(exports, "SkeletonCard", ()=>SkeletonCard);
parcelHelpers.export(exports, "SkeletonTable", ()=>SkeletonTable);
parcelHelpers.export(exports, "SkeletonAvatar", ()=>SkeletonAvatar);
parcelHelpers.export(exports, "SkeletonButton", ()=>SkeletonButton);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
const Skeleton = ({ width = '100%', height = '1rem', className = '', variant = 'text', animation = 'pulse' })=>{
    const baseClasses = 'skeleton';
    const variantClasses = {
        text: 'skeleton-text',
        rectangular: 'skeleton-rectangular',
        circular: 'skeleton-circular',
        avatar: 'skeleton-avatar'
    };
    const animationClasses = {
        pulse: 'skeleton-pulse',
        wave: 'skeleton-wave'
    };
    const classes = [
        baseClasses,
        variantClasses[variant] || variantClasses.text,
        animationClasses[animation] || animationClasses.pulse,
        className
    ].filter(Boolean).join(' ');
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: classes,
        style: {
            width,
            height
        }
    }, void 0, false, {
        fileName: "src/Skeleton.js",
        lineNumber: 32,
        columnNumber: 5
    }, undefined);
};
_c = Skeleton;
const SkeletonText = ({ lines = 1, width = '100%', ...props })=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "skeleton-text-block",
        children: Array.from({
            length: lines
        }, (_, i)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                width: i === lines - 1 ? '60%' : width,
                height: "1rem",
                variant: "text",
                ...props
            }, i, false, {
                fileName: "src/Skeleton.js",
                lineNumber: 43,
                columnNumber: 7
            }, undefined))
    }, void 0, false, {
        fileName: "src/Skeleton.js",
        lineNumber: 41,
        columnNumber: 3
    }, undefined);
_c1 = SkeletonText;
const SkeletonCard = ({ height = '200px', ...props })=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "skeleton-card",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                height: "2rem",
                width: "80%",
                className: "skeleton-card-title",
                ...props
            }, void 0, false, {
                fileName: "src/Skeleton.js",
                lineNumber: 56,
                columnNumber: 5
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                height: height,
                variant: "rectangular",
                className: "skeleton-card-content",
                ...props
            }, void 0, false, {
                fileName: "src/Skeleton.js",
                lineNumber: 57,
                columnNumber: 5
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "skeleton-card-footer",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                        width: "40%",
                        height: "0.8rem",
                        ...props
                    }, void 0, false, {
                        fileName: "src/Skeleton.js",
                        lineNumber: 59,
                        columnNumber: 7
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                        width: "30%",
                        height: "0.8rem",
                        ...props
                    }, void 0, false, {
                        fileName: "src/Skeleton.js",
                        lineNumber: 60,
                        columnNumber: 7
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/Skeleton.js",
                lineNumber: 58,
                columnNumber: 5
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/Skeleton.js",
        lineNumber: 55,
        columnNumber: 3
    }, undefined);
_c2 = SkeletonCard;
const SkeletonTable = ({ rows = 5, columns = 4, ...props })=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "skeleton-table",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "skeleton-table-header",
                children: Array.from({
                    length: columns
                }, (_, i)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                        height: "1.2rem",
                        width: "100%",
                        ...props
                    }, i, false, {
                        fileName: "src/Skeleton.js",
                        lineNumber: 70,
                        columnNumber: 9
                    }, undefined))
            }, void 0, false, {
                fileName: "src/Skeleton.js",
                lineNumber: 68,
                columnNumber: 5
            }, undefined),
            Array.from({
                length: rows
            }, (_, rowIndex)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "skeleton-table-row",
                    children: Array.from({
                        length: columns
                    }, (_, colIndex)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                            height: "1rem",
                            width: "100%",
                            ...props
                        }, colIndex, false, {
                            fileName: "src/Skeleton.js",
                            lineNumber: 77,
                            columnNumber: 11
                        }, undefined))
                }, rowIndex, false, {
                    fileName: "src/Skeleton.js",
                    lineNumber: 75,
                    columnNumber: 7
                }, undefined))
        ]
    }, void 0, true, {
        fileName: "src/Skeleton.js",
        lineNumber: 66,
        columnNumber: 3
    }, undefined);
_c3 = SkeletonTable;
const SkeletonAvatar = ({ size = '40px', ...props })=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
        width: size,
        height: size,
        variant: "circular",
        ...props
    }, void 0, false, {
        fileName: "src/Skeleton.js",
        lineNumber: 90,
        columnNumber: 3
    }, undefined);
_c4 = SkeletonAvatar;
const SkeletonButton = ({ width = '120px', ...props })=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
        width: width,
        height: "2.5rem",
        variant: "rectangular",
        className: "skeleton-button",
        ...props
    }, void 0, false, {
        fileName: "src/Skeleton.js",
        lineNumber: 99,
        columnNumber: 3
    }, undefined);
_c5 = SkeletonButton;
exports.default = Skeleton;
var _c, _c1, _c2, _c3, _c4, _c5;
$RefreshReg$(_c, "Skeleton");
$RefreshReg$(_c1, "SkeletonText");
$RefreshReg$(_c2, "SkeletonCard");
$RefreshReg$(_c3, "SkeletonTable");
$RefreshReg$(_c4, "SkeletonAvatar");
$RefreshReg$(_c5, "SkeletonButton");

  $parcel$ReactRefreshHelpers$5663.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}]},["jLuuR"], null, "parcelRequire10c2", {})

//# sourceMappingURL=Chat.37796bd9.js.map
