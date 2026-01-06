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
})({"5JtUO":[function(require,module,exports,__globalThis) {
var global = arguments[3];
var HMR_HOST = null;
var HMR_PORT = null;
var HMR_SERVER_PORT = 40423;
var HMR_SECURE = false;
var HMR_ENV_HASH = "439701173a9199ea";
var HMR_USE_SSE = false;
module.bundle.HMR_BUNDLE_ID = "033a690137baeaf1";
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

},{}],"25UDT":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$ad15 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$ad15.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$ad15.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _documentSelector = require("./DocumentSelector");
var _documentSelectorDefault = parcelHelpers.interopDefault(_documentSelector);
var _documentQA = require("./DocumentQA");
var _documentQADefault = parcelHelpers.interopDefault(_documentQA);
var _s = $RefreshSig$();
const DocumentQATab = ()=>{
    _s();
    const [selectedDocuments, setSelectedDocuments] = (0, _react.useState)([]);
    const [currentView, setCurrentView] = (0, _react.useState)('selector'); // 'selector' or 'qa'
    const handleDocumentSelection = (documents)=>{
        setSelectedDocuments(documents);
        if (documents.length > 0) setCurrentView('qa');
    };
    const handleBackToSelector = ()=>{
        setCurrentView('selector');
    };
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "document-qa-tab",
        children: currentView === 'selector' ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _documentSelectorDefault.default), {
            selectedDocuments: selectedDocuments,
            onSelectionChange: handleDocumentSelection,
            maxSelections: 5
        }, void 0, false, {
            fileName: "src/DocumentQATab.js",
            lineNumber: 23,
            columnNumber: 9
        }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _documentQADefault.default), {
            selectedDocuments: selectedDocuments,
            onBack: handleBackToSelector
        }, void 0, false, {
            fileName: "src/DocumentQATab.js",
            lineNumber: 29,
            columnNumber: 9
        }, undefined)
    }, void 0, false, {
        fileName: "src/DocumentQATab.js",
        lineNumber: 21,
        columnNumber: 5
    }, undefined);
};
_s(DocumentQATab, "W6FHMj/a0pC7SfAwbkmxens9Pzg=");
_c = DocumentQATab;
exports.default = DocumentQATab;
var _c;
$RefreshReg$(_c, "DocumentQATab");

  $parcel$ReactRefreshHelpers$ad15.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","./DocumentSelector":"3OAQj","./DocumentQA":"2WTSW","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"3OAQj":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$f34e = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$f34e.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$f34e.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _skeleton = require("./Skeleton");
var _skeletonDefault = parcelHelpers.interopDefault(_skeleton);
var _apiCache = require("./apiCache");
var _virtualizedList = require("./VirtualizedList");
var _virtualizedListDefault = parcelHelpers.interopDefault(_virtualizedList);
var _s = $RefreshSig$();
const DocumentSelector = /*#__PURE__*/ _s((0, _reactDefault.default).memo(_c = _s(({ selectedDocuments, onSelectionChange, maxSelections = 5 })=>{
    _s();
    const [documents, setDocuments] = (0, _react.useState)([]);
    const [loading, setLoading] = (0, _react.useState)(true);
    const [error, setError] = (0, _react.useState)(null);
    const [searchTerm, setSearchTerm] = (0, _react.useState)('');
    const [filterType, setFilterType] = (0, _react.useState)('all');
    (0, _react.useEffect)(()=>{
        loadDocuments();
    }, []);
    const loadDocuments = async ()=>{
        try {
            setLoading(true);
            const data = await (0, _apiCache.cachedFetch)('/api/documents');
            setDocuments(data.documents || []);
            setError(null);
        } catch (err) {
            setError(err.message);
            // Mock data for development
            setDocuments([
                {
                    id: 'doc1',
                    filename: 'research_paper.pdf',
                    title: 'Advances in Machine Learning',
                    type: 'pdf',
                    size: 2457600,
                    uploadedAt: '2024-01-15T10:30:00Z',
                    status: 'processed',
                    chunkCount: 45
                },
                {
                    id: 'doc2',
                    filename: 'user_manual.docx',
                    title: 'System User Manual',
                    type: 'docx',
                    size: 512000,
                    uploadedAt: '2024-01-14T15:20:00Z',
                    status: 'processed',
                    chunkCount: 23
                },
                {
                    id: 'doc3',
                    filename: 'notes.txt',
                    title: 'Meeting Notes',
                    type: 'txt',
                    size: 16384,
                    uploadedAt: '2024-01-13T09:15:00Z',
                    status: 'processed',
                    chunkCount: 8
                }
            ]);
        } finally{
            setLoading(false);
        }
    };
    const handleDocumentToggle = (documentId)=>{
        const newSelection = selectedDocuments.includes(documentId) ? selectedDocuments.filter((id)=>id !== documentId) : [
            ...selectedDocuments,
            documentId
        ];
        if (newSelection.length <= maxSelections) onSelectionChange(newSelection);
    };
    const formatFileSize = (bytes)=>{
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = [
            'Bytes',
            'KB',
            'MB',
            'GB'
        ];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    const formatDate = (dateString)=>{
        const date = new Date(dateString);
        return date.toLocaleDateString([], {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    const filteredDocuments = documents.filter((doc)=>{
        const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) || doc.title && doc.title.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = filterType === 'all' || doc.type === filterType;
        return matchesSearch && matchesType;
    });
    const getStatusColor = (status)=>{
        switch(status){
            case 'processed':
                return '#28a745';
            case 'processing':
                return '#ffc107';
            case 'failed':
                return '#dc3545';
            default:
                return '#6c757d';
        }
    };
    if (loading) return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "document-selector",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "selector-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                        width: "200px",
                        height: "1.5rem"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 112,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                        width: "120px",
                        height: "1rem"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 113,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 111,
                columnNumber: 9
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "selector-controls",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                        width: "100%",
                        height: "2.5rem"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 117,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                        width: "120px",
                        height: "2.5rem"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 118,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 116,
                columnNumber: 9
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "documents-list",
                children: Array.from({
                    length: 4
                }, (_, i)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "document-item",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                width: "20px",
                                height: "20px",
                                variant: "circular",
                                className: "document-checkbox"
                            }, void 0, false, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 124,
                                columnNumber: 15
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "document-info",
                                children: [
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        className: "document-header",
                                        children: [
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                                width: "70%",
                                                height: "1rem"
                                            }, void 0, false, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 127,
                                                columnNumber: 19
                                            }, undefined),
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                className: "document-meta",
                                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                                    width: "50px",
                                                    height: "1rem"
                                                }, void 0, false, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 129,
                                                    columnNumber: 21
                                                }, undefined)
                                            }, void 0, false, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 128,
                                                columnNumber: 19
                                            }, undefined)
                                        ]
                                    }, void 0, true, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 126,
                                        columnNumber: 17
                                    }, undefined),
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeleton.SkeletonText), {
                                        lines: 2,
                                        width: "100%"
                                    }, void 0, false, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 132,
                                        columnNumber: 17
                                    }, undefined),
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                        width: "80px",
                                        height: "0.8rem"
                                    }, void 0, false, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 133,
                                        columnNumber: 17
                                    }, undefined)
                                ]
                            }, void 0, true, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 125,
                                columnNumber: 15
                            }, undefined)
                        ]
                    }, i, true, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 123,
                        columnNumber: 13
                    }, undefined))
            }, void 0, false, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 121,
                columnNumber: 9
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/DocumentSelector.js",
        lineNumber: 110,
        columnNumber: 7
    }, undefined);
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "document-selector",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "selector-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h3", {
                        children: "Select Documents"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 145,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        className: "selection-count",
                        children: [
                            selectedDocuments.length,
                            "/",
                            maxSelections,
                            " selected"
                        ]
                    }, void 0, true, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 146,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 144,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "selector-controls",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "search-bar",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("input", {
                                type: "text",
                                placeholder: "Search documents...",
                                value: searchTerm,
                                onChange: (e)=>setSearchTerm(e.target.value),
                                className: "search-input"
                            }, void 0, false, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 153,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                className: "search-icon",
                                children: "\uD83D\uDD0D"
                            }, void 0, false, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 160,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 152,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "filter-controls",
                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("label", {
                            children: [
                                "Type:",
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("select", {
                                    value: filterType,
                                    onChange: (e)=>setFilterType(e.target.value),
                                    className: "type-filter",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("option", {
                                            value: "all",
                                            children: "All Types"
                                        }, void 0, false, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 171,
                                            columnNumber: 15
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("option", {
                                            value: "pdf",
                                            children: "PDF"
                                        }, void 0, false, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 172,
                                            columnNumber: 15
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("option", {
                                            value: "docx",
                                            children: "Word"
                                        }, void 0, false, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 173,
                                            columnNumber: 15
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("option", {
                                            value: "txt",
                                            children: "Text"
                                        }, void 0, false, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 174,
                                            columnNumber: 15
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentSelector.js",
                                    lineNumber: 166,
                                    columnNumber: 13
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/DocumentSelector.js",
                            lineNumber: 164,
                            columnNumber: 11
                        }, undefined)
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 163,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 151,
                columnNumber: 7
            }, undefined),
            error && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "error-message",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        className: "error-icon",
                        children: "\u26A0\uFE0F"
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 182,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        children: error
                    }, void 0, false, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 183,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 181,
                columnNumber: 9
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "documents-list",
                children: filteredDocuments.length === 0 ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "no-documents",
                    children: [
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                            children: searchTerm || filterType !== 'all' ? 'No documents match your search.' : 'No documents uploaded yet.'
                        }, void 0, false, {
                            fileName: "src/DocumentSelector.js",
                            lineNumber: 190,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                            children: "Upload documents in the Documents tab to get started."
                        }, void 0, false, {
                            fileName: "src/DocumentSelector.js",
                            lineNumber: 191,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/DocumentSelector.js",
                    lineNumber: 189,
                    columnNumber: 11
                }, undefined) : filteredDocuments.length > 20 ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _virtualizedListDefault.default), {
                    items: filteredDocuments,
                    itemHeight: 100,
                    containerHeight: 400,
                    renderItem: (doc, index)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: `document-item ${selectedDocuments.includes(doc.id) ? 'selected' : ''}`,
                            onClick: ()=>handleDocumentToggle(doc.id),
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "document-checkbox",
                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("input", {
                                        type: "checkbox",
                                        checked: selectedDocuments.includes(doc.id),
                                        onChange: ()=>{},
                                        disabled: !selectedDocuments.includes(doc.id) && selectedDocuments.length >= maxSelections
                                    }, void 0, false, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 205,
                                        columnNumber: 19
                                    }, void 0)
                                }, void 0, false, {
                                    fileName: "src/DocumentSelector.js",
                                    lineNumber: 204,
                                    columnNumber: 17
                                }, void 0),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "document-info",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "document-header",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h4", {
                                                    className: "document-title",
                                                    children: doc.title || doc.filename
                                                }, void 0, false, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 215,
                                                    columnNumber: 21
                                                }, void 0),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "document-meta",
                                                    children: [
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "document-type",
                                                            children: doc.type.toUpperCase()
                                                        }, void 0, false, {
                                                            fileName: "src/DocumentSelector.js",
                                                            lineNumber: 219,
                                                            columnNumber: 23
                                                        }, void 0),
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "document-status",
                                                            style: {
                                                                color: getStatusColor(doc.status)
                                                            },
                                                            children: [
                                                                "\u25CF ",
                                                                doc.status
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "src/DocumentSelector.js",
                                                            lineNumber: 220,
                                                            columnNumber: 23
                                                        }, void 0)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 218,
                                                    columnNumber: 21
                                                }, void 0)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 214,
                                            columnNumber: 19
                                        }, void 0),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "document-details",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                    className: "document-filename",
                                                    children: doc.filename
                                                }, void 0, false, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 227,
                                                    columnNumber: 21
                                                }, void 0),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                    className: "document-size",
                                                    children: formatFileSize(doc.size)
                                                }, void 0, false, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 228,
                                                    columnNumber: 21
                                                }, void 0),
                                                doc.chunkCount && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                    className: "document-chunks",
                                                    children: [
                                                        doc.chunkCount,
                                                        " chunks"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/DocumentSelector.js",
                                                    lineNumber: 230,
                                                    columnNumber: 23
                                                }, void 0)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 226,
                                            columnNumber: 19
                                        }, void 0),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "document-date",
                                            children: [
                                                "Uploaded ",
                                                formatDate(doc.uploadedAt)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentSelector.js",
                                            lineNumber: 234,
                                            columnNumber: 19
                                        }, void 0)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentSelector.js",
                                    lineNumber: 213,
                                    columnNumber: 17
                                }, void 0)
                            ]
                        }, doc.id, true, {
                            fileName: "src/DocumentSelector.js",
                            lineNumber: 199,
                            columnNumber: 15
                        }, void 0)
                }, void 0, false, {
                    fileName: "src/DocumentSelector.js",
                    lineNumber: 194,
                    columnNumber: 11
                }, undefined) : filteredDocuments.map((doc)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: `document-item ${selectedDocuments.includes(doc.id) ? 'selected' : ''}`,
                        onClick: ()=>handleDocumentToggle(doc.id),
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "document-checkbox",
                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("input", {
                                    type: "checkbox",
                                    checked: selectedDocuments.includes(doc.id),
                                    onChange: ()=>{},
                                    disabled: !selectedDocuments.includes(doc.id) && selectedDocuments.length >= maxSelections
                                }, void 0, false, {
                                    fileName: "src/DocumentSelector.js",
                                    lineNumber: 249,
                                    columnNumber: 17
                                }, undefined)
                            }, void 0, false, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 248,
                                columnNumber: 15
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "document-info",
                                children: [
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        className: "document-header",
                                        children: [
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h4", {
                                                className: "document-title",
                                                children: doc.title || doc.filename
                                            }, void 0, false, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 259,
                                                columnNumber: 19
                                            }, undefined),
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                className: "document-meta",
                                                children: [
                                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                        className: "document-type",
                                                        children: doc.type.toUpperCase()
                                                    }, void 0, false, {
                                                        fileName: "src/DocumentSelector.js",
                                                        lineNumber: 263,
                                                        columnNumber: 21
                                                    }, undefined),
                                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                        className: "document-status",
                                                        style: {
                                                            color: getStatusColor(doc.status)
                                                        },
                                                        children: [
                                                            "\u25CF ",
                                                            doc.status
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "src/DocumentSelector.js",
                                                        lineNumber: 264,
                                                        columnNumber: 21
                                                    }, undefined)
                                                ]
                                            }, void 0, true, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 262,
                                                columnNumber: 19
                                            }, undefined)
                                        ]
                                    }, void 0, true, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 258,
                                        columnNumber: 17
                                    }, undefined),
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        className: "document-details",
                                        children: [
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                className: "document-filename",
                                                children: doc.filename
                                            }, void 0, false, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 271,
                                                columnNumber: 19
                                            }, undefined),
                                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                className: "document-size",
                                                children: formatFileSize(doc.size)
                                            }, void 0, false, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 272,
                                                columnNumber: 19
                                            }, undefined),
                                            doc.chunkCount && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                className: "document-chunks",
                                                children: [
                                                    doc.chunkCount,
                                                    " chunks"
                                                ]
                                            }, void 0, true, {
                                                fileName: "src/DocumentSelector.js",
                                                lineNumber: 274,
                                                columnNumber: 21
                                            }, undefined)
                                        ]
                                    }, void 0, true, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 270,
                                        columnNumber: 17
                                    }, undefined),
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        className: "document-date",
                                        children: [
                                            "Uploaded ",
                                            formatDate(doc.uploadedAt)
                                        ]
                                    }, void 0, true, {
                                        fileName: "src/DocumentSelector.js",
                                        lineNumber: 278,
                                        columnNumber: 17
                                    }, undefined)
                                ]
                            }, void 0, true, {
                                fileName: "src/DocumentSelector.js",
                                lineNumber: 257,
                                columnNumber: 15
                            }, undefined)
                        ]
                    }, doc.id, true, {
                        fileName: "src/DocumentSelector.js",
                        lineNumber: 243,
                        columnNumber: 13
                    }, undefined))
            }, void 0, false, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 187,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("style", {
                children: `
        .document-selector {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          max-height: 600px;
          display: flex;
          flex-direction: column;
        }

        .selector-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 1px solid var(--border-color);
        }

        .selector-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .selection-count {
          font-size: 14px;
          color: var(--text-secondary);
          background: var(--bg-tertiary);
          padding: 4px 8px;
          border-radius: 12px;
        }

        .selector-controls {
          display: flex;
          gap: 15px;
          margin-bottom: 20px;
          flex-wrap: wrap;
        }

        .search-bar {
          position: relative;
          flex: 1;
          min-width: 250px;
        }

        .search-input {
          width: 100%;
          padding: 10px 40px 10px 15px;
          border: 2px solid var(--border-color);
          border-radius: 6px;
          font-size: 14px;
          background: var(--bg-primary);
          color: var(--text-primary);
        }

        .search-input:focus {
          outline: none;
          border-color: var(--accent);
        }

        .search-icon {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-secondary);
          pointer-events: none;
        }

        .filter-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .filter-controls label {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 14px;
          color: var(--text-secondary);
          white-space: nowrap;
        }

        .type-filter {
          padding: 6px 10px;
          border: 2px solid var(--border-color);
          border-radius: 4px;
          background: var(--bg-primary);
          color: var(--text-primary);
          font-size: 14px;
        }

        .error-message {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px;
          background: rgba(220, 53, 69, 0.1);
          border: 1px solid var(--error);
          border-radius: 4px;
          color: var(--text-primary);
          margin-bottom: 15px;
        }

        .documents-list {
          flex: 1;
          overflow-y: auto;
          border: 1px solid var(--border-color);
          border-radius: 6px;
        }

        .document-item {
          display: flex;
          align-items: flex-start;
          padding: 15px;
          border-bottom: 1px solid var(--border-color);
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .document-item:last-child {
          border-bottom: none;
        }

        .document-item:hover {
          background: var(--bg-secondary);
        }

        .document-item.selected {
          background: rgba(0, 123, 255, 0.1);
          border-left: 3px solid var(--accent);
        }

        .document-checkbox {
          margin-right: 15px;
          margin-top: 2px;
        }

        .document-checkbox input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }

        .document-info {
          flex: 1;
          min-width: 0;
        }

        .document-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 8px;
          gap: 10px;
        }

        .document-title {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary);
          flex: 1;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .document-meta {
          display: flex;
          gap: 12px;
          flex-shrink: 0;
        }

        .document-type {
          background: var(--accent);
          color: white;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          font-weight: 600;
        }

        .document-status {
          font-size: 12px;
          font-weight: 500;
        }

        .document-details {
          display: flex;
          gap: 15px;
          margin-bottom: 6px;
          font-size: 13px;
          color: var(--text-secondary);
        }

        .document-date {
          font-size: 12px;
          color: var(--text-muted);
        }

        .no-documents {
          text-align: center;
          padding: 40px;
          color: var(--text-secondary);
        }

        .no-documents p {
          margin: 10px 0;
        }

        .loading {
          text-align: center;
          padding: 40px;
        }

        .spinner {
          width: 30px;
          height: 30px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid var(--accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 15px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          50% { transform: rotate(180deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .selector-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
          }

          .selector-controls {
            flex-direction: column;
            gap: 10px;
          }

          .search-bar {
            min-width: auto;
          }

          .document-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
          }

          .document-meta {
            width: 100%;
            justify-content: space-between;
          }

          .document-details {
            flex-direction: column;
            gap: 4px;
          }
        }
      `
            }, void 0, false, {
                fileName: "src/DocumentSelector.js",
                lineNumber: 287,
                columnNumber: 7
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/DocumentSelector.js",
        lineNumber: 143,
        columnNumber: 5
    }, undefined);
}, "50NMSmJ+PS/5Zv7PE3e+pC5d3wM=")), "50NMSmJ+PS/5Zv7PE3e+pC5d3wM=");
_c1 = DocumentSelector;
DocumentSelector.displayName = 'DocumentSelector';
exports.default = DocumentSelector;
var _c, _c1;
$RefreshReg$(_c, "DocumentSelector$React.memo");
$RefreshReg$(_c1, "DocumentSelector");

  $parcel$ReactRefreshHelpers$f34e.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","./Skeleton":"kExCx","./apiCache":"hWXFY","./VirtualizedList":"6MMyT","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"kExCx":[function(require,module,exports,__globalThis) {
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
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"6MMyT":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$c363 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$c363.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$c363.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "useDynamicVirtualization", ()=>useDynamicVirtualization);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _s = $RefreshSig$(), _s1 = $RefreshSig$();
const VirtualizedList = ({ items, itemHeight = 60, containerHeight = 400, renderItem, overscan = 5, className = '' })=>{
    _s();
    const [scrollTop, setScrollTop] = (0, _react.useState)(0);
    const [containerHeightState, setContainerHeightState] = (0, _react.useState)(containerHeight);
    const scrollElementRef = (0, _react.useRef)(null);
    const handleScroll = (0, _react.useCallback)((e)=>{
        setScrollTop(e.target.scrollTop);
    }, []);
    // Calculate visible range
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(items.length - 1, Math.ceil((scrollTop + containerHeightState) / itemHeight) + overscan);
    // Calculate total height and offset
    const totalHeight = items.length * itemHeight;
    const offsetY = startIndex * itemHeight;
    // Get visible items
    const visibleItems = items.slice(startIndex, endIndex + 1);
    (0, _react.useEffect)(()=>{
        const updateHeight = ()=>{
            if (scrollElementRef.current) setContainerHeightState(scrollElementRef.current.clientHeight);
        };
        updateHeight();
        window.addEventListener('resize', updateHeight);
        return ()=>window.removeEventListener('resize', updateHeight);
    }, []);
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        ref: scrollElementRef,
        className: `virtualized-list ${className}`,
        style: {
            height: containerHeight,
            overflowY: 'auto',
            position: 'relative'
        },
        onScroll: handleScroll,
        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
            style: {
                height: totalHeight,
                position: 'relative'
            },
            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                style: {
                    transform: `translateY(${offsetY}px)`,
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0
                },
                children: visibleItems.map((item, index)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        style: {
                            height: itemHeight
                        },
                        children: renderItem(item, startIndex + index)
                    }, startIndex + index, false, {
                        fileName: "src/VirtualizedList.js",
                        lineNumber: 67,
                        columnNumber: 13
                    }, undefined))
            }, void 0, false, {
                fileName: "src/VirtualizedList.js",
                lineNumber: 57,
                columnNumber: 9
            }, undefined)
        }, void 0, false, {
            fileName: "src/VirtualizedList.js",
            lineNumber: 56,
            columnNumber: 7
        }, undefined)
    }, void 0, false, {
        fileName: "src/VirtualizedList.js",
        lineNumber: 46,
        columnNumber: 5
    }, undefined);
};
_s(VirtualizedList, "H56c6KGNee+IFcIGWUIkoPQbpLE=");
_c = VirtualizedList;
const useDynamicVirtualization = (items, estimatedItemHeight = 60)=>{
    _s1();
    const [measuredHeights, setMeasuredHeights] = (0, _react.useState)(new Map());
    const [totalHeight, setTotalHeight] = (0, _react.useState)(items.length * estimatedItemHeight);
    const measureItem = (0, _react.useCallback)((index, height)=>{
        setMeasuredHeights((prev)=>{
            const newHeights = new Map(prev);
            const heightChanged = newHeights.get(index) !== height;
            if (heightChanged) {
                newHeights.set(index, height);
                // Recalculate total height
                let newTotal = 0;
                for(let i = 0; i < items.length; i++)newTotal += newHeights.get(i) || estimatedItemHeight;
                setTotalHeight(newTotal);
            }
            return newHeights;
        });
    }, [
        items.length,
        estimatedItemHeight
    ]);
    const getItemHeight = (0, _react.useCallback)((index)=>{
        return measuredHeights.get(index) || estimatedItemHeight;
    }, [
        measuredHeights,
        estimatedItemHeight
    ]);
    const getOffsetForIndex = (0, _react.useCallback)((index)=>{
        let offset = 0;
        for(let i = 0; i < index; i++)offset += getItemHeight(i);
        return offset;
    }, [
        getItemHeight
    ]);
    const getIndexForOffset = (0, _react.useCallback)((offset)=>{
        let currentOffset = 0;
        for(let i = 0; i < items.length; i++){
            const itemHeight = getItemHeight(i);
            if (currentOffset + itemHeight > offset) return i;
            currentOffset += itemHeight;
        }
        return items.length - 1;
    }, [
        items.length,
        getItemHeight
    ]);
    return {
        totalHeight,
        measureItem,
        getItemHeight,
        getOffsetForIndex,
        getIndexForOffset
    };
};
_s1(useDynamicVirtualization, "L+CwGM1LFCLT0wzIkRYkRMgKuRY=");
exports.default = VirtualizedList;
var _c;
$RefreshReg$(_c, "VirtualizedList");

  $parcel$ReactRefreshHelpers$c363.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"2WTSW":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$6ee5 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$6ee5.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$6ee5.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _richTextMessage = require("./RichTextMessage");
var _richTextMessageDefault = parcelHelpers.interopDefault(_richTextMessage);
var _s = $RefreshSig$();
const DocumentQA = ({ selectedDocuments, onBack })=>{
    _s();
    const [messages, setMessages] = (0, _react.useState)([]);
    const [currentQuery, setCurrentQuery] = (0, _react.useState)('');
    const [isLoading, setIsLoading] = (0, _react.useState)(false);
    const [error, setError] = (0, _react.useState)(null);
    const messagesEndRef = (0, _react.useRef)(null);
    const scrollToBottom = ()=>{
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    };
    (0, _react.useEffect)(()=>{
        scrollToBottom();
    }, [
        messages
    ]);
    const handleSubmit = async (e)=>{
        e.preventDefault();
        if (!currentQuery.trim() || isLoading) return;
        const query = currentQuery.trim();
        setCurrentQuery('');
        // Add user message
        const userMessage = {
            id: Date.now().toString(),
            type: 'user',
            content: query,
            timestamp: new Date()
        };
        setMessages((prev)=>[
                ...prev,
                userMessage
            ]);
        setIsLoading(true);
        setError(null);
        try {
            // TODO: Replace with actual API call
            const response = await fetch('/api/qa/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    document_ids: selectedDocuments,
                    max_results: 5
                })
            });
            if (!response.ok) throw new Error('Failed to get answer');
            const data = await response.json();
            // Add AI response
            const aiMessage = {
                id: (Date.now() + 1).toString(),
                type: 'ai',
                content: data.answer,
                sources: data.sources || [],
                confidence: data.confidence,
                timestamp: new Date()
            };
            setMessages((prev)=>[
                    ...prev,
                    aiMessage
                ]);
        } catch (err) {
            setError(err.message);
            // Mock response for development
            setTimeout(()=>{
                const mockAnswer = `Based on the ${selectedDocuments.length} selected document(s), here's what I found regarding "${query}":

This is a placeholder response. In the full implementation, this would contain actual answers extracted from the uploaded documents using vector similarity search and LLM synthesis.

Key points from the documents:
\u{2022} Point 1 from document analysis
\u{2022} Point 2 with source citations
\u{2022} Point 3 with confidence scoring

Sources: ${selectedDocuments.join(', ')}`;
                const aiMessage = {
                    id: (Date.now() + 1).toString(),
                    type: 'ai',
                    content: mockAnswer,
                    sources: selectedDocuments.map((id)=>({
                            id,
                            relevance: 0.85
                        })),
                    confidence: 0.78,
                    timestamp: new Date()
                };
                setMessages((prev)=>[
                        ...prev,
                        aiMessage
                    ]);
                setError(null);
            }, 2000);
        } finally{
            setIsLoading(false);
        }
    };
    const formatTimestamp = (timestamp)=>{
        return timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    const renderMessage = (message)=>{
        if (message.type === 'user') return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
            className: "message user-message",
            children: [
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-content",
                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                        children: message.content
                    }, void 0, false, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 113,
                        columnNumber: 13
                    }, undefined)
                }, void 0, false, {
                    fileName: "src/DocumentQA.js",
                    lineNumber: 112,
                    columnNumber: 11
                }, undefined),
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-meta",
                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        className: "timestamp",
                        children: formatTimestamp(message.timestamp)
                    }, void 0, false, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 116,
                        columnNumber: 13
                    }, undefined)
                }, void 0, false, {
                    fileName: "src/DocumentQA.js",
                    lineNumber: 115,
                    columnNumber: 11
                }, undefined)
            ]
        }, void 0, true, {
            fileName: "src/DocumentQA.js",
            lineNumber: 111,
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
                            children: "\uD83E\uDD16"
                        }, void 0, false, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 124,
                            columnNumber: 13
                        }, undefined),
                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "ai-info",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "ai-name",
                                    children: "Document Assistant"
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 126,
                                    columnNumber: 15
                                }, undefined),
                                message.confidence && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                    className: "confidence-score",
                                    children: [
                                        "Confidence: ",
                                        (message.confidence * 100).toFixed(0),
                                        "%"
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 128,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 125,
                            columnNumber: 13
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/DocumentQA.js",
                    lineNumber: 123,
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
                                fileName: "src/DocumentQA.js",
                                lineNumber: 137,
                                columnNumber: 16
                            }, undefined)
                        }, void 0, false, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 136,
                            columnNumber: 14
                        }, undefined),
                        message.sources && message.sources.length > 0 && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "sources-section",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h5", {
                                    children: "Sources:"
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 142,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "sources-list",
                                    children: message.sources.map((source, index)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "source-item",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                    className: "source-id",
                                                    children: source.id
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 146,
                                                    columnNumber: 23
                                                }, undefined),
                                                source.relevance && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                    className: "source-relevance",
                                                    children: [
                                                        (source.relevance * 100).toFixed(0),
                                                        "% relevant"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 148,
                                                    columnNumber: 25
                                                }, undefined)
                                            ]
                                        }, index, true, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 145,
                                            columnNumber: 21
                                        }, undefined))
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 143,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 141,
                            columnNumber: 15
                        }, undefined)
                    ]
                }, void 0, true, {
                    fileName: "src/DocumentQA.js",
                    lineNumber: 135,
                    columnNumber: 12
                }, undefined),
                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                    className: "message-meta",
                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        className: "timestamp",
                        children: formatTimestamp(message.timestamp)
                    }, void 0, false, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 160,
                        columnNumber: 13
                    }, undefined)
                }, void 0, false, {
                    fileName: "src/DocumentQA.js",
                    lineNumber: 159,
                    columnNumber: 11
                }, undefined)
            ]
        }, void 0, true, {
            fileName: "src/DocumentQA.js",
            lineNumber: 122,
            columnNumber: 9
        }, undefined);
    };
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "document-qa",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "qa-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                        onClick: onBack,
                        className: "back-button",
                        children: "\u2190 Back to Document Selection"
                    }, void 0, false, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 170,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "qa-info",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h3", {
                                children: "Document Q&A"
                            }, void 0, false, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 174,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                children: [
                                    "Ask questions about your ",
                                    selectedDocuments.length,
                                    " selected document(s)"
                                ]
                            }, void 0, true, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 175,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 173,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentQA.js",
                lineNumber: 169,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "chat-container",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "messages-area",
                        children: messages.length === 0 ? isLoading ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "loading-messages",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "message ai-message",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-header",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                                                    width: "120px",
                                                    height: "1rem"
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 186,
                                                    columnNumber: 21
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(Skeleton, {
                                                    width: "80px",
                                                    height: "1rem"
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 187,
                                                    columnNumber: 21
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 185,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-content",
                                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(SkeletonText, {
                                                lines: 3,
                                                width: "100%"
                                            }, void 0, false, {
                                                fileName: "src/DocumentQA.js",
                                                lineNumber: 190,
                                                columnNumber: 21
                                            }, undefined)
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 189,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 184,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "message user-message",
                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        className: "message-content",
                                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)(SkeletonText, {
                                            lines: 2,
                                            width: "80%"
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 195,
                                            columnNumber: 21
                                        }, undefined)
                                    }, void 0, false, {
                                        fileName: "src/DocumentQA.js",
                                        lineNumber: 194,
                                        columnNumber: 19
                                    }, undefined)
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 193,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 183,
                            columnNumber: 15
                        }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "welcome-message",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "welcome-icon",
                                    children: "\uD83D\uDCDA"
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 201,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h4", {
                                    children: "Welcome to Document Q&A"
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 202,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                    children: "Ask me anything about your uploaded documents. I'll search through the content and provide relevant answers with source citations."
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 203,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "example-questions",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("strong", {
                                                children: "Example questions:"
                                            }, void 0, false, {
                                                fileName: "src/DocumentQA.js",
                                                lineNumber: 205,
                                                columnNumber: 22
                                            }, undefined)
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 205,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("ul", {
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("li", {
                                                    children: '"What are the main findings in this research paper?"'
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 207,
                                                    columnNumber: 21
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("li", {
                                                    children: '"Summarize the key points from chapter 3"'
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 208,
                                                    columnNumber: 21
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("li", {
                                                    children: '"What does the document say about machine learning?"'
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 209,
                                                    columnNumber: 21
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 206,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 204,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/DocumentQA.js",
                            lineNumber: 200,
                            columnNumber: 15
                        }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _jsxDevRuntime.Fragment), {
                            children: [
                                messages.map((message)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                        children: renderMessage(message)
                                    }, message.id, false, {
                                        fileName: "src/DocumentQA.js",
                                        lineNumber: 217,
                                        columnNumber: 17
                                    }, undefined)),
                                isLoading && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "message ai-message loading",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-header",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "ai-avatar",
                                                    children: "\uD83E\uDD16"
                                                }, void 0, false, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 225,
                                                    columnNumber: 21
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "ai-info",
                                                    children: [
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "ai-name",
                                                            children: "Document Assistant"
                                                        }, void 0, false, {
                                                            fileName: "src/DocumentQA.js",
                                                            lineNumber: 227,
                                                            columnNumber: 23
                                                        }, undefined),
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                                            className: "loading-text",
                                                            children: "Searching documents..."
                                                        }, void 0, false, {
                                                            fileName: "src/DocumentQA.js",
                                                            lineNumber: 228,
                                                            columnNumber: 23
                                                        }, undefined)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 226,
                                                    columnNumber: 21
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 224,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "message-content",
                                            children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                className: "loading-indicator",
                                                children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                                    className: "typing-dots",
                                                    children: [
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                            fileName: "src/DocumentQA.js",
                                                            lineNumber: 234,
                                                            columnNumber: 25
                                                        }, undefined),
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                            fileName: "src/DocumentQA.js",
                                                            lineNumber: 235,
                                                            columnNumber: 25
                                                        }, undefined),
                                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {}, void 0, false, {
                                                            fileName: "src/DocumentQA.js",
                                                            lineNumber: 236,
                                                            columnNumber: 25
                                                        }, undefined)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "src/DocumentQA.js",
                                                    lineNumber: 233,
                                                    columnNumber: 23
                                                }, undefined)
                                            }, void 0, false, {
                                                fileName: "src/DocumentQA.js",
                                                lineNumber: 232,
                                                columnNumber: 21
                                            }, undefined)
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 231,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 223,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    ref: messagesEndRef
                                }, void 0, false, {
                                    fileName: "src/DocumentQA.js",
                                    lineNumber: 243,
                                    columnNumber: 15
                                }, undefined)
                            ]
                        }, void 0, true)
                    }, void 0, false, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 180,
                        columnNumber: 9
                    }, undefined),
                    error && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "error-banner",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                className: "error-icon",
                                children: "\u26A0\uFE0F"
                            }, void 0, false, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 250,
                                columnNumber: 13
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                children: error
                            }, void 0, false, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 251,
                                columnNumber: 13
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                onClick: ()=>setError(null),
                                className: "dismiss-error",
                                children: "\xd7"
                            }, void 0, false, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 252,
                                columnNumber: 13
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 249,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("form", {
                        onSubmit: handleSubmit,
                        className: "query-form",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "query-input-container",
                                children: [
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("textarea", {
                                        value: currentQuery,
                                        onChange: (e)=>setCurrentQuery(e.target.value),
                                        placeholder: "Ask a question about your documents...",
                                        className: "query-input",
                                        rows: 1,
                                        disabled: isLoading,
                                        onKeyDown: (e)=>{
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSubmit(e);
                                            }
                                        }
                                    }, void 0, false, {
                                        fileName: "src/DocumentQA.js",
                                        lineNumber: 258,
                                        columnNumber: 13
                                    }, undefined),
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                        type: "submit",
                                        className: "submit-button",
                                        disabled: !currentQuery.trim() || isLoading,
                                        children: isLoading ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "spinner"
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 278,
                                            columnNumber: 17
                                        }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                            className: "send-icon",
                                            children: "\u27A4"
                                        }, void 0, false, {
                                            fileName: "src/DocumentQA.js",
                                            lineNumber: 280,
                                            columnNumber: 17
                                        }, undefined)
                                    }, void 0, false, {
                                        fileName: "src/DocumentQA.js",
                                        lineNumber: 272,
                                        columnNumber: 13
                                    }, undefined)
                                ]
                            }, void 0, true, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 257,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                className: "query-help",
                                children: "Press Enter to send, Shift+Enter for new line"
                            }, void 0, false, {
                                fileName: "src/DocumentQA.js",
                                lineNumber: 284,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/DocumentQA.js",
                        lineNumber: 256,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/DocumentQA.js",
                lineNumber: 179,
                columnNumber: 7
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("style", {
                children: `
        .document-qa {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: var(--bg-primary);
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 10px var(--shadow);
        }

        .qa-header {
          display: flex;
          align-items: center;
          gap: 20px;
          padding: 20px;
          border-bottom: 1px solid var(--border-color);
          background: var(--bg-secondary);
        }

        .back-button {
          padding: 8px 16px;
          background: var(--accent);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s ease;
        }

        .back-button:hover {
          background: #0056b3;
        }

        .qa-info h3 {
          margin: 0 0 5px 0;
          color: var(--text-primary);
        }

        .qa-info p {
          margin: 0;
          color: var(--text-secondary);
          font-size: 14px;
        }

        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }

        .messages-area {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .welcome-message {
          text-align: center;
          padding: 40px 20px;
          color: var(--text-secondary);
        }

        .welcome-icon {
          font-size: 48px;
          margin-bottom: 20px;
        }

        .welcome-message h4 {
          color: var(--text-primary);
          margin-bottom: 15px;
        }

        .example-questions {
          margin-top: 20px;
          text-align: left;
          max-width: 400px;
          margin-left: auto;
          margin-right: auto;
        }

        .example-questions ul {
          margin: 10px 0 0 0;
          padding-left: 20px;
        }

        .example-questions li {
          margin: 5px 0;
          font-size: 14px;
        }

        .message {
          max-width: 80%;
          animation: fadeIn 0.3s ease-in;
        }

        .user-message {
          align-self: flex-end;
          background: var(--accent);
          color: white;
          border-radius: 18px 18px 4px 18px;
          margin-left: auto;
        }

        .ai-message {
          align-self: flex-start;
          background: var(--bg-secondary);
          border: 1px solid var(--border-color);
          border-radius: 18px 18px 18px 4px;
          color: var(--text-primary);
        }

        .message-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid var(--border-color);
        }

        .ai-avatar {
          width: 32px;
          height: 32px;
          background: var(--accent);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
        }

        .ai-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .ai-name {
          font-weight: 600;
          color: var(--text-primary);
        }

        .confidence-score {
          font-size: 12px;
          color: var(--success);
          font-weight: 500;
        }

        .loading-text {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .message-content {
          line-height: 1.6;
        }

        .user-message .message-content {
          padding: 12px 16px;
        }

        .ai-message .message-content {
          padding: 0;
        }

        .answer-text p {
          margin: 8px 0;
        }

        .answer-text p:first-child {
          margin-top: 0;
        }

        .answer-text p:last-child {
          margin-bottom: 0;
        }

        .sources-section {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border-color);
        }

        .sources-section h5 {
          margin: 0 0 8px 0;
          color: var(--text-primary);
          font-size: 14px;
        }

        .sources-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .source-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 6px 10px;
          background: var(--bg-tertiary);
          border-radius: 4px;
          font-size: 13px;
        }

        .source-id {
          font-family: monospace;
          color: var(--accent);
        }

        .source-relevance {
          color: var(--text-secondary);
          font-size: 12px;
        }

        .message-meta {
          margin-top: 8px;
          text-align: right;
        }

        .user-message .message-meta {
          text-align: right;
        }

        .ai-message .message-meta {
          text-align: left;
        }

        .timestamp {
          font-size: 11px;
          color: var(--text-muted);
        }

        .loading-indicator {
          display: flex;
          align-items: center;
          padding: 20px;
        }

        .typing-dots {
          display: flex;
          gap: 4px;
        }

        .typing-dots span {
          width: 8px;
          height: 8px;
          background: var(--text-secondary);
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }

        .typing-dots span:nth-child(1) { animation-delay: 0s; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        .error-banner {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          background: rgba(220, 53, 69, 0.1);
          border-top: 1px solid var(--error);
          color: var(--text-primary);
        }

        .dismiss-error {
          margin-left: auto;
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: var(--error);
        }

        .query-form {
          border-top: 1px solid var(--border-color);
          background: var(--bg-primary);
        }

        .query-input-container {
          display: flex;
          align-items: flex-end;
          gap: 12px;
          padding: 20px;
        }

        .query-input {
          flex: 1;
          padding: 12px 16px;
          border: 2px solid var(--border-color);
          border-radius: 8px;
          font-size: 16px;
          font-family: inherit;
          background: var(--bg-primary);
          color: var(--text-primary);
          resize: none;
          min-height: 20px;
          max-height: 120px;
          overflow-y: auto;
        }

        .query-input:focus {
          outline: none;
          border-color: var(--accent);
        }

        .query-input:disabled {
          background: var(--bg-secondary);
          cursor: not-allowed;
        }

        .submit-button {
          padding: 12px 16px;
          background: var(--accent);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 48px;
          height: 48px;
          transition: background-color 0.2s ease;
        }

        .submit-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .submit-button:disabled {
          background: var(--text-muted);
          cursor: not-allowed;
        }

        .send-icon {
          font-size: 18px;
          transform: rotate(0deg);
          transition: transform 0.2s ease;
        }

        .submit-button:not(:disabled) .send-icon {
          transform: rotate(0deg);
        }

        .query-help {
          padding: 0 20px 12px;
          font-size: 12px;
          color: var(--text-secondary);
          text-align: center;
        }

        .spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes typing {
          0%, 60%, 100% { opacity: 0.4; transform: scale(1); }
          30% { opacity: 1; transform: scale(1.2); }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          50% { transform: rotate(180deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .qa-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
          }

          .messages-area {
            padding: 15px;
          }

          .message {
            max-width: 90%;
          }

          .query-input-container {
            padding: 15px;
            gap: 8px;
          }

          .query-input {
            font-size: 16px; /* Prevents zoom on iOS */
          }

          .submit-button {
            min-width: 44px;
            height: 44px;
          }
        }
      `
            }, void 0, false, {
                fileName: "src/DocumentQA.js",
                lineNumber: 290,
                columnNumber: 7
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/DocumentQA.js",
        lineNumber: 168,
        columnNumber: 5
    }, undefined);
};
_s(DocumentQA, "xHEh9HhdI3y8YaHj+RH4ipHHjBk=");
_c = DocumentQA;
exports.default = DocumentQA;
var _c;
$RefreshReg$(_c, "DocumentQA");

  $parcel$ReactRefreshHelpers$6ee5.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","./RichTextMessage":"flq1Y","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"flq1Y":[function(require,module,exports,__globalThis) {
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
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}]},["5JtUO"], null, "parcelRequire10c2", {})

//# sourceMappingURL=DocumentQATab.37baeaf1.js.map
