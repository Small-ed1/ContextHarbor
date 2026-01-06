var e=globalThis.parcelRequire10c2;(0,e.register)("7y2Ds",function(s,r){Object.defineProperty(s.exports,"__esModule",{value:!0}),s.exports.default=void 0;var a=i(e("acw62")),t=e("ayMG0");function i(e,s){if("function"==typeof WeakMap)var r=new WeakMap,a=new WeakMap;return(i=function(e,s){if(!s&&e&&e.__esModule)return e;var t,i,n={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return n;if(t=s?a:r){if(t.has(e))return t.get(e);t.set(e,n)}for(let s in e)"default"!==s&&({}).hasOwnProperty.call(e,s)&&((i=(t=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,s))&&(i.get||i.set)?t(n,s,i):n[s]=e[s]);return n})(e,s)}s.exports.default=({onResumeSession:e,onDeleteSession:s})=>{let[r,i]=(0,a.useState)([]),[n,o]=(0,a.useState)(!0),[l,d]=(0,a.useState)(null);(0,a.useEffect)(()=>{c()},[]);let c=async()=>{try{o(!0);let e=await fetch("/api/research/sessions");if(!e.ok)throw Error("Failed to load sessions");let s=await e.json();i(s.sessions||[]),d(null)}catch(e){d(e.message)}finally{o(!1)}},p=async s=>{try{let r=await fetch(`/api/research/${s}/resume`,{method:"POST"});if(!r.ok)throw Error("Failed to resume session");await r.json(),e&&e(s),await c()}catch(e){d(`Failed to resume session: ${e.message}`)}},x=async e=>{if(confirm(`Are you sure you want to delete research session ${e}?`))try{if(!(await fetch(`/api/research/${e}`,{method:"DELETE"})).ok)throw Error("Failed to delete session");s&&s(e),await c()}catch(e){d(`Failed to delete session: ${e.message}`)}},u=e=>new Date(e).toLocaleString();return n?(0,t.jsxs)("div",{className:"research-history loading",children:[(0,t.jsx)("div",{className:"spinner"}),(0,t.jsx)("p",{children:"Loading research history..."})]}):(0,t.jsxs)("div",{className:"research-history",children:[(0,t.jsxs)("div",{className:"history-header",children:[(0,t.jsx)("h3",{children:"Research History"}),(0,t.jsx)("button",{onClick:c,className:"refresh-button",children:"↻ Refresh"})]}),l&&(0,t.jsxs)("div",{className:"error-message",children:[(0,t.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,t.jsx)("span",{children:l}),(0,t.jsx)("button",{onClick:()=>d(null),className:"dismiss-error",children:"×"})]}),0===r.length?(0,t.jsxs)("div",{className:"no-sessions",children:[(0,t.jsx)("p",{children:"No saved research sessions found."}),(0,t.jsx)("p",{children:"Completed research will appear here for resuming later."})]}):(0,t.jsx)("div",{className:"sessions-list",children:r.map(e=>(0,t.jsxs)("div",{className:"session-item",children:[(0,t.jsxs)("div",{className:"session-info",children:[(0,t.jsxs)("div",{className:"session-header",children:[(0,t.jsx)("h4",{children:"Research Session"}),(0,t.jsx)("span",{className:`status-badge ${e.status}`,children:e.status})]}),(0,t.jsxs)("div",{className:"session-details",children:[(0,t.jsxs)("div",{className:"detail",children:[(0,t.jsx)("span",{className:"label",children:"ID:"}),(0,t.jsx)("code",{className:"value",children:e.task_id})]}),(0,t.jsxs)("div",{className:"detail",children:[(0,t.jsx)("span",{className:"label",children:"Started:"}),(0,t.jsx)("span",{className:"value",children:e.start_time?u(e.start_time):"Unknown"})]}),(0,t.jsxs)("div",{className:"detail",children:[(0,t.jsx)("span",{className:"label",children:"Last Updated:"}),(0,t.jsx)("span",{className:"value",children:e.last_update?u(e.last_update):"Unknown"})]})]})]}),(0,t.jsxs)("div",{className:"session-actions",children:["running"===e.status&&(0,t.jsx)("button",{onClick:()=>p(e.task_id),className:"resume-button",children:"▶️ Resume"}),(0,t.jsx)("button",{onClick:()=>x(e.task_id),className:"delete-button",children:"🗑️ Delete"})]})]},e.task_id))}),(0,t.jsx)("style",{children:`
        .research-history {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          margin: 20px 0;
        }

        .history-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .history-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .refresh-button {
          padding: 8px 16px;
          background: var(--text-secondary);
          color: var(--bg-primary);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .refresh-button:hover {
          background: var(--text-muted);
        }

        .error-message {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px;
          background: rgba(220, 53, 69, 0.1);
          border: 1px solid var(--error);
          border-radius: 4px;
          color: var(--error);
          margin-bottom: 15px;
        }

        .dismiss-error {
          margin-left: auto;
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: var(--error);
        }

        .no-sessions {
          text-align: center;
          padding: 40px;
          color: var(--text-secondary);
        }

        .no-sessions p {
          margin: 10px 0;
        }

        .sessions-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .session-item {
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 15px;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          flex-wrap: wrap;
          gap: 15px;
          background: var(--bg-primary);
        }

        .session-info {
          flex: 1;
          min-width: 200px;
        }

        .session-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }

        .session-header h4 {
          margin: 0;
          color: var(--text-primary);
        }

        .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
        }

        .status-badge.running {
          background: rgba(40, 167, 69, 0.2);
          color: var(--success);
        }

        .status-badge.stopped {
          background: rgba(255, 193, 7, 0.2);
          color: var(--warning);
        }

        .session-details {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .detail {
          display: flex;
          gap: 8px;
          font-size: 14px;
        }

        .label {
          font-weight: 500;
          color: var(--text-secondary);
          min-width: 70px;
        }

        .value {
          color: var(--text-primary);
        }

        .value code {
          background: var(--bg-tertiary);
          padding: 2px 4px;
          border-radius: 3px;
          font-family: monospace;
          font-size: 12px;
        }

        .session-actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
        }

        .resume-button,
        .delete-button {
          padding: 8px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .resume-button {
          background: var(--success);
          color: white;
        }

        .resume-button:hover {
          background: #218838;
        }

        .delete-button {
          background: var(--error);
          color: white;
        }

        .delete-button:hover {
          background: #c82333;
        }

        .loading {
          text-align: center;
          padding: 40px;
        }

        .spinner {
          width: 30px;
          height: 30px;
          border: 3px solid var(--bg-tertiary);
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
          .session-item {
            flex-direction: column;
          }

          .session-actions {
            align-self: stretch;
            justify-content: space-between;
          }

          .history-header {
            flex-direction: column;
            gap: 10px;
            align-items: flex-start;
          }
        }
      `})]})}});
//# sourceMappingURL=ResearchHistory.9ccf373f.js.map
