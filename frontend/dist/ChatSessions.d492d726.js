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
})({"ckGvQ":[function(require,module,exports,__globalThis) {
var global = arguments[3];
var HMR_HOST = null;
var HMR_PORT = null;
var HMR_SERVER_PORT = 40423;
var HMR_SECURE = false;
var HMR_ENV_HASH = "439701173a9199ea";
var HMR_USE_SSE = false;
module.bundle.HMR_BUNDLE_ID = "3a113497d492d726";
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

},{}],"CRv5J":[function(require,module,exports,__globalThis) {
var $parcel$ReactRefreshHelpers$7475 = require("@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js");
$parcel$ReactRefreshHelpers$7475.init();
var prevRefreshReg = globalThis.$RefreshReg$;
var prevRefreshSig = globalThis.$RefreshSig$;
$parcel$ReactRefreshHelpers$7475.prelude(module);

try {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
var _jsxDevRuntime = require("react/jsx-dev-runtime");
var _react = require("react");
var _reactDefault = parcelHelpers.interopDefault(_react);
var _skeleton = require("./Skeleton");
var _skeletonDefault = parcelHelpers.interopDefault(_skeleton);
var _apiCache = require("./apiCache");
var _s = $RefreshSig$();
const ChatSessions = /*#__PURE__*/ _s((0, _reactDefault.default).memo(_c = _s(({ onSessionSelect, currentSessionId })=>{
    _s();
    const [sessions, setSessions] = (0, _react.useState)([]);
    const [loading, setLoading] = (0, _react.useState)(true);
    const [error, setError] = (0, _react.useState)(null);
    const [showArchived, setShowArchived] = (0, _react.useState)(false);
    (0, _react.useEffect)(()=>{
        loadSessions();
    }, [
        showArchived
    ]);
    const loadSessions = async ()=>{
        try {
            setLoading(true);
            const data = await (0, _apiCache.cachedFetch)('/api/chats');
            setSessions(data || []);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally{
            setLoading(false);
        }
    };
    const createNewSession = async ()=>{
        try {
            const response = await fetch('/api/chats', {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to create session');
            const data = await response.json();
            onSessionSelect && onSessionSelect(data.id);
            await loadSessions(); // Refresh the list
        } catch (err) {
            setError(`Failed to create session: ${err.message}`);
        }
    };
    const archiveSession = async (sessionId)=>{
        if (!confirm(`Are you sure you want to archive this session?`)) return;
        try {
            const response = await fetch(`/api/chats/${sessionId}/archive`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to archive session');
            await loadSessions(); // Refresh the list
        } catch (err) {
            setError(`Failed to archive session: ${err.message}`);
        }
    };
    const deleteSession = async (sessionId)=>{
        if (!confirm(`Are you sure you want to permanently delete this session? This action cannot be undone.`)) return;
        try {
            const response = await fetch(`/api/chats/${sessionId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete session');
            await loadSessions(); // Refresh the list
        } catch (err) {
            setError(`Failed to delete session: ${err.message}`);
        }
    };
    const formatDate = (dateString)=>{
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = diffMs / 3600000;
        if (diffHours < 24) return date.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
        else if (diffHours < 168) return date.toLocaleDateString([], {
            weekday: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
        else return date.toLocaleDateString();
    };
    const getSessionPreview = (session)=>{
        if (session.summary) return session.summary;
        if (session.messages && session.messages.length > 0) {
            const lastMessage = session.messages[session.messages.length - 1];
            return lastMessage.content ? lastMessage.content.substring(0, 100) + '...' : 'Empty message';
        }
        return 'New conversation';
    };
    const filteredSessions = sessions.filter((session)=>showArchived || !session.archived);
    if (loading) return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "chat-sessions",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "sessions-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                        width: "150px",
                        height: "1.2rem"
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 115,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "header-actions",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                width: "100px",
                                height: "2rem"
                            }, void 0, false, {
                                fileName: "src/ChatSessions.js",
                                lineNumber: 117,
                                columnNumber: 13
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                width: "100px",
                                height: "2rem"
                            }, void 0, false, {
                                fileName: "src/ChatSessions.js",
                                lineNumber: 118,
                                columnNumber: 13
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 116,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/ChatSessions.js",
                lineNumber: 114,
                columnNumber: 9
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "sessions-list",
                children: Array.from({
                    length: 3
                }, (_, i)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "session-item",
                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "document-info",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "session-title-row",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                            width: "80%",
                                            height: "1rem"
                                        }, void 0, false, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 127,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "session-actions",
                                            children: [
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                                    width: "24px",
                                                    height: "24px",
                                                    variant: "circular"
                                                }, void 0, false, {
                                                    fileName: "src/ChatSessions.js",
                                                    lineNumber: 129,
                                                    columnNumber: 21
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                                    width: "24px",
                                                    height: "24px",
                                                    variant: "circular"
                                                }, void 0, false, {
                                                    fileName: "src/ChatSessions.js",
                                                    lineNumber: 130,
                                                    columnNumber: 21
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 128,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 126,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeleton.SkeletonText), {
                                    lines: 2,
                                    width: "100%"
                                }, void 0, false, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 133,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "session-meta",
                                    children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)((0, _skeletonDefault.default), {
                                        width: "60px",
                                        height: "0.8rem"
                                    }, void 0, false, {
                                        fileName: "src/ChatSessions.js",
                                        lineNumber: 135,
                                        columnNumber: 19
                                    }, undefined)
                                }, void 0, false, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 134,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/ChatSessions.js",
                            lineNumber: 125,
                            columnNumber: 15
                        }, undefined)
                    }, i, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 124,
                        columnNumber: 13
                    }, undefined))
            }, void 0, false, {
                fileName: "src/ChatSessions.js",
                lineNumber: 122,
                columnNumber: 9
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/ChatSessions.js",
        lineNumber: 113,
        columnNumber: 7
    }, undefined);
    return /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
        className: "chat-sessions",
        children: [
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "sessions-header",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h3", {
                        children: "Chat Sessions"
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 148,
                        columnNumber: 9
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: "header-actions",
                        children: [
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("label", {
                                className: "archive-toggle",
                                children: [
                                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("input", {
                                        type: "checkbox",
                                        checked: showArchived,
                                        onChange: (e)=>setShowArchived(e.target.checked)
                                    }, void 0, false, {
                                        fileName: "src/ChatSessions.js",
                                        lineNumber: 151,
                                        columnNumber: 13
                                    }, undefined),
                                    "Show archived"
                                ]
                            }, void 0, true, {
                                fileName: "src/ChatSessions.js",
                                lineNumber: 150,
                                columnNumber: 11
                            }, undefined),
                            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                onClick: createNewSession,
                                className: "new-session-button",
                                children: "+ New Chat"
                            }, void 0, false, {
                                fileName: "src/ChatSessions.js",
                                lineNumber: 158,
                                columnNumber: 11
                            }, undefined)
                        ]
                    }, void 0, true, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 149,
                        columnNumber: 9
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/ChatSessions.js",
                lineNumber: 147,
                columnNumber: 7
            }, undefined),
            error && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "error-message",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        className: "error-icon",
                        children: "\u26A0\uFE0F"
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 166,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                        children: error
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 167,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                        onClick: ()=>setError(null),
                        className: "dismiss-error",
                        children: "\xd7"
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 168,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/ChatSessions.js",
                lineNumber: 165,
                columnNumber: 9
            }, undefined),
            filteredSessions.length === 0 ? /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "no-sessions",
                children: [
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                        children: showArchived ? 'No archived sessions found.' : 'No chat sessions found.'
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 174,
                        columnNumber: 11
                    }, undefined),
                    /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                        children: "Start a new conversation to see it here."
                    }, void 0, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 175,
                        columnNumber: 11
                    }, undefined)
                ]
            }, void 0, true, {
                fileName: "src/ChatSessions.js",
                lineNumber: 173,
                columnNumber: 9
            }, undefined) : /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                className: "sessions-list",
                children: filteredSessions.map((session)=>/*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                        className: `session-item ${session.id === currentSessionId ? 'active' : ''} ${session.archived ? 'archived' : ''}`,
                        onClick: ()=>onSessionSelect && onSessionSelect(session.id),
                        children: /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                            className: "session-content",
                            children: [
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "session-title-row",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("h4", {
                                            className: "session-title",
                                            children: session.title || 'Untitled Chat'
                                        }, void 0, false, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 187,
                                            columnNumber: 19
                                        }, undefined),
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                            className: "session-actions",
                                            children: [
                                                !session.archived && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                                    onClick: (e)=>{
                                                        e.stopPropagation();
                                                        archiveSession(session.id);
                                                    },
                                                    className: "archive-button",
                                                    title: "Archive session",
                                                    children: "\uD83D\uDCC1"
                                                }, void 0, false, {
                                                    fileName: "src/ChatSessions.js",
                                                    lineNumber: 192,
                                                    columnNumber: 23
                                                }, undefined),
                                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("button", {
                                                    onClick: (e)=>{
                                                        e.stopPropagation();
                                                        deleteSession(session.id);
                                                    },
                                                    className: "delete-button",
                                                    title: "Delete session",
                                                    children: "\uD83D\uDDD1\uFE0F"
                                                }, void 0, false, {
                                                    fileName: "src/ChatSessions.js",
                                                    lineNumber: 203,
                                                    columnNumber: 21
                                                }, undefined)
                                            ]
                                        }, void 0, true, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 190,
                                            columnNumber: 19
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 186,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("p", {
                                    className: "session-preview",
                                    children: getSessionPreview(session)
                                }, void 0, false, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 216,
                                    columnNumber: 17
                                }, undefined),
                                /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("div", {
                                    className: "session-meta",
                                    children: [
                                        /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                            className: "session-date",
                                            children: formatDate(session.created_at)
                                        }, void 0, false, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 221,
                                            columnNumber: 19
                                        }, undefined),
                                        session.archived && /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("span", {
                                            className: "archived-badge",
                                            children: "Archived"
                                        }, void 0, false, {
                                            fileName: "src/ChatSessions.js",
                                            lineNumber: 225,
                                            columnNumber: 21
                                        }, undefined)
                                    ]
                                }, void 0, true, {
                                    fileName: "src/ChatSessions.js",
                                    lineNumber: 220,
                                    columnNumber: 17
                                }, undefined)
                            ]
                        }, void 0, true, {
                            fileName: "src/ChatSessions.js",
                            lineNumber: 185,
                            columnNumber: 15
                        }, undefined)
                    }, session.id, false, {
                        fileName: "src/ChatSessions.js",
                        lineNumber: 180,
                        columnNumber: 13
                    }, undefined))
            }, void 0, false, {
                fileName: "src/ChatSessions.js",
                lineNumber: 178,
                columnNumber: 9
            }, undefined),
            /*#__PURE__*/ (0, _jsxDevRuntime.jsxDEV)("style", {
                children: `
        .chat-sessions {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          margin: 20px 0;
        }

        .sessions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          flex-wrap: wrap;
          gap: 15px;
        }

        .sessions-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .archive-toggle {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 14px;
          color: var(--text-secondary);
          cursor: pointer;
        }

        .archive-toggle input[type="checkbox"] {
          margin: 0;
        }

        .new-session-button {
          padding: 8px 16px;
          background: var(--accent);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        }

        .new-session-button:hover {
          background: #0056b3;
        }

        .error-message {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px;
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
          color: #721c24;
          margin-bottom: 15px;
        }

        .dismiss-error {
          margin-left: auto;
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: #721c24;
        }

        .no-sessions {
          text-align: center;
          padding: 40px;
          color: #666;
        }

        .no-sessions p {
          margin: 10px 0;
        }

        .sessions-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .session-item {
          border: 1px solid #e9ecef;
          border-radius: 6px;
          padding: 15px;
          cursor: pointer;
          transition: all 0.2s ease;
          background: #f8f9fa;
        }

        .session-item:hover {
          box-shadow: 0 2px 8px var(--shadow);
        }

        .session-item.selected {
          border-color: var(--accent);
        }

        .session-item.active {
          border-color: #007bff;
          background: #e7f3ff;
        }

        .session-item.archived {
          opacity: 0.7;
          border-style: dashed;
        }

        .session-content {
          width: 100%;
        }

        .session-title-row {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 8px;
        }

        .session-title {
          margin: 0 0 8px 0;
          color: var(--text-primary);
        }

        .session-actions {
          display: flex;
          gap: 5px;
          opacity: 0;
          transition: opacity 0.2s ease;
        }

        .session-item:hover .session-actions {
          opacity: 1;
        }

        .archive-button,
        .delete-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
          border-radius: 3px;
          font-size: 14px;
          transition: background-color 0.2s ease;
        }

        .archive-button:hover {
          background: #e9ecef;
        }

        .delete-button:hover {
          background: #f8d7da;
        }

        .session-preview {
          margin: 0 0 8px 0;
          color: #666;
          font-size: 14px;
          line-height: 1.4;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .session-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 12px;
        }

        .session-date {
          color: #999;
        }

        .archived-badge {
          background: #ffc107;
          color: #856404;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          font-weight: 500;
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
          .sessions-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .header-actions {
            width: 100%;
            justify-content: space-between;
          }

          .session-title-row {
            flex-direction: column;
            gap: 10px;
          }

          .session-actions {
            opacity: 1;
            justify-content: flex-end;
          }

          .session-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
          }
        }
      `
            }, void 0, false, {
                fileName: "src/ChatSessions.js",
                lineNumber: 234,
                columnNumber: 7
            }, undefined)
        ]
    }, void 0, true, {
        fileName: "src/ChatSessions.js",
        lineNumber: 146,
        columnNumber: 5
    }, undefined);
}, "Nt6eALEbVaVH6vXZVNb2kYmSk9I=")), "Nt6eALEbVaVH6vXZVNb2kYmSk9I=");
_c1 = ChatSessions;
ChatSessions.displayName = 'ChatSessions';
exports.default = ChatSessions;
var _c, _c1;
$RefreshReg$(_c, "ChatSessions$React.memo");
$RefreshReg$(_c1, "ChatSessions");

  $parcel$ReactRefreshHelpers$7475.postlude(module);
} finally {
  globalThis.$RefreshReg$ = prevRefreshReg;
  globalThis.$RefreshSig$ = prevRefreshSig;
}
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","./Skeleton":"kExCx","./apiCache":"hWXFY","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}],"kExCx":[function(require,module,exports,__globalThis) {
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
},{"react/jsx-dev-runtime":"dVPUn","react":"jMk1U","@parcel/transformer-js/src/esmodule-helpers.js":"jnFvT","@parcel/transformer-react-refresh-wrap/lib/helpers/helpers.js":"7h6Pi"}]},["ckGvQ"], null, "parcelRequire10c2", {})

//# sourceMappingURL=ChatSessions.d492d726.js.map
