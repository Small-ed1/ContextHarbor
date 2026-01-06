var e=globalThis.parcelRequire10c2;(0,e.register)("5x4ke",function(r,s){Object.defineProperty(r.exports,"__esModule",{value:!0}),r.exports.default=void 0;var a=i(e("acw62")),t=e("ayMG0");function i(e,r){if("function"==typeof WeakMap)var s=new WeakMap,a=new WeakMap;return(i=function(e,r){if(!r&&e&&e.__esModule)return e;var t,i,n={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return n;if(t=r?a:s){if(t.has(e))return t.get(e);t.set(e,n)}for(let r in e)"default"!==r&&({}).hasOwnProperty.call(e,r)&&((i=(t=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,r))&&(i.get||i.set)?t(n,r,i):n[r]=e[r]);return n})(e,r)}r.exports.default=({taskId:e,onComplete:r,onError:s})=>{let[i,n]=(0,a.useState)(null),[o,l]=(0,a.useState)(!1),[d,c]=(0,a.useState)(null);if((0,a.useEffect)(()=>{if(!e)return;let a=new EventSource(`/api/research/${e}/progress`);return a.onopen=()=>{l(!0),c(null)},a.onmessage=e=>{try{let t=JSON.parse(e.data);if(t.error){c(t.error),s&&s(t.error);return}if("heartbeat"===t.type)return;n(t),"completed"===t.status&&(r&&r(t),a.close())}catch(e){console.error("Error parsing progress data:",e),c("Failed to parse progress data")}},a.onerror=e=>{console.error("EventSource error:",e),l(!1),c("Connection lost"),s&&s("Connection lost")},()=>{a.close(),l(!1)}},[e,r,s]),!i)return(0,t.jsxs)("div",{className:"research-progress loading",children:[(0,t.jsx)("div",{className:"progress-spinner"}),(0,t.jsx)("p",{children:"Connecting to research session..."})]});let p=Math.round(i.progress||0);return(0,t.jsxs)("div",{className:"research-progress",children:[(0,t.jsxs)("div",{className:"progress-header",children:[(0,t.jsx)("h3",{children:"Research Progress"}),(0,t.jsxs)("div",{className:`status-indicator ${i.status}`,children:[(0,t.jsx)("span",{className:`status-dot ${i.status}`}),"running"===i.status?"Running":"completed"===i.status?"Completed":"Error"]})]}),(0,t.jsxs)("div",{className:"progress-bar-container",children:[(0,t.jsx)("div",{className:"progress-bar",children:(0,t.jsx)("div",{className:"progress-fill",style:{width:`${p}%`}})}),(0,t.jsxs)("span",{className:"progress-text",children:[p,"%"]})]}),(0,t.jsxs)("div",{className:"progress-details",children:[(0,t.jsxs)("div",{className:"detail-row",children:[(0,t.jsx)("span",{className:"label",children:"Phase:"}),(0,t.jsx)("span",{className:"value",children:i.phase||"Initializing"})]}),(0,t.jsxs)("div",{className:"detail-row",children:[(0,t.jsx)("span",{className:"label",children:"Topics:"}),(0,t.jsxs)("span",{className:"value",children:[i.topics_completed||0," / ",i.total_topics||0]})]}),(0,t.jsxs)("div",{className:"detail-row",children:[(0,t.jsx)("span",{className:"label",children:"Findings:"}),(0,t.jsx)("span",{className:"value",children:i.findings_count||0})]}),i.start_time&&(0,t.jsxs)("div",{className:"detail-row",children:[(0,t.jsx)("span",{className:"label",children:"Started:"}),(0,t.jsx)("span",{className:"value",children:new Date(i.start_time).toLocaleTimeString()})]})]}),d&&(0,t.jsxs)("div",{className:"progress-error",children:[(0,t.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,t.jsx)("span",{className:"error-message",children:d})]}),(0,t.jsx)("style",{children:`
        .research-progress {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          margin: 20px 0;
        }

        .progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .progress-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .status-dot.running {
          background: var(--accent);
          animation: pulse 2s infinite;
        }

        .status-dot.completed {
          background: var(--success);
        }

        .status-dot.error {
          background: var(--error);
        }

        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }

        .progress-bar-container {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 20px;
        }

        .progress-bar {
          flex: 1;
          height: 20px;
          background: var(--bg-tertiary);
          border-radius: 10px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--accent), #0056b3);
          transition: width 0.3s ease;
        }

        .progress-text {
          font-weight: 600;
          color: var(--accent);
          min-width: 45px;
        }

        .progress-details {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px 20px;
          margin-bottom: 15px;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .label {
          font-weight: 500;
          color: var(--text-secondary);
        }

        .value {
          font-weight: 600;
          color: var(--text-primary);
        }

        .progress-error {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px;
          background: rgba(220, 53, 69, 0.1);
          border: 1px solid var(--error);
          border-radius: 4px;
          color: var(--error);
        }

        .loading {
          text-align: center;
          padding: 40px;
        }

        .progress-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--bg-tertiary);
          border-top: 4px solid var(--accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .progress-details {
            grid-template-columns: 1fr;
          }

          .progress-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
          }
        }
      `})]})}});
//# sourceMappingURL=ResearchProgress.bdbebb10.js.map
