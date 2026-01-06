var e=globalThis.parcelRequire10c2;(0,e.register)("lqMdl",function(r,a){Object.defineProperty(r.exports,"__esModule",{value:!0}),r.exports.default=void 0;var t=o(e("acw62")),s=e("ayMG0");function o(e,r){if("function"==typeof WeakMap)var a=new WeakMap,t=new WeakMap;return(o=function(e,r){if(!r&&e&&e.__esModule)return e;var s,o,n={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return n;if(s=r?t:a){if(s.has(e))return s.get(e);s.set(e,n)}for(let r in e)"default"!==r&&({}).hasOwnProperty.call(e,r)&&((o=(s=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,r))&&(o.get||o.set)?s(n,r,o):n[r]=e[r]);return n})(e,r)}let n=t.default.memo(({onStartResearch:e,onStopResearch:r,currentTask:a,isResearching:o})=>{let[n,i]=(0,t.useState)(""),[l,c]=(0,t.useState)("standard"),[d,p]=(0,t.useState)(!1),u=async r=>{if(r.preventDefault(),n.trim()){p(!0);try{await e(n.trim(),l),i("")}catch(e){console.error("Failed to start research:",e)}finally{p(!1)}}},x=async()=>{if(a&&r)try{await r(a)}catch(e){console.error("Failed to stop research:",e)}};return(0,s.jsxs)("div",{className:"research-controls",children:[(0,s.jsxs)("div",{className:"controls-header",children:[(0,s.jsx)("h3",{children:"Research Controls"}),a&&(0,s.jsxs)("div",{className:"current-session",children:[(0,s.jsx)("span",{className:"session-label",children:"Active Session:"}),(0,s.jsx)("code",{className:"session-id",children:a})]})]}),o?(0,s.jsxs)("div",{className:"active-research",children:[(0,s.jsxs)("div",{className:"status-message",children:[(0,s.jsx)("span",{className:"status-icon",children:"⚡"}),(0,s.jsx)("span",{children:"Research in progress..."})]}),(0,s.jsxs)("button",{onClick:x,className:"stop-button",children:[(0,s.jsx)("span",{className:"icon",children:"⏹️"}),"Stop Research"]})]}):(0,s.jsxs)("form",{onSubmit:u,className:"research-form",children:[(0,s.jsxs)("div",{className:"form-group",children:[(0,s.jsx)("label",{htmlFor:"topic",children:"Research Topic"}),(0,s.jsx)("input",{type:"text",id:"topic",value:n,onChange:e=>i(e.target.value),placeholder:"Enter your research topic...",required:!0,disabled:d})]}),(0,s.jsxs)("div",{className:"form-group",children:[(0,s.jsx)("label",{htmlFor:"depth",children:"Research Depth"}),(0,s.jsxs)("select",{id:"depth",value:l,onChange:e=>c(e.target.value),disabled:d,children:[(0,s.jsx)("option",{value:"quick",children:"Quick (Fast results, basic analysis)"}),(0,s.jsx)("option",{value:"standard",children:"Standard (Balanced depth and speed)"}),(0,s.jsx)("option",{value:"deep",children:"Deep (Comprehensive analysis, slower)"})]})]}),(0,s.jsx)("button",{type:"submit",className:"start-button",disabled:!n.trim()||d,children:d?(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)("span",{className:"spinner"}),"Starting Research..."]}):(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)("span",{className:"icon",children:"🔍"}),"Start Research"]})})]}),(0,s.jsx)("style",{children:`
        .research-controls {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          margin: 20px 0;
        }

        .controls-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          flex-wrap: wrap;
          gap: 10px;
        }

        .controls-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .current-session {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }

        .session-label {
          color: var(--text-secondary);
        }

        .session-id {
          background: var(--bg-tertiary);
          padding: 2px 6px;
          border-radius: 4px;
          font-family: monospace;
          font-size: 12px;
          color: var(--accent);
        }

        .research-form {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-group label {
          font-weight: 500;
          color: var(--text-primary);
          font-size: 14px;
        }

        .form-group input,
        .form-group select {
          padding: 10px 12px;
          border: 2px solid var(--border-color);
          border-radius: 6px;
          font-size: 16px;
          transition: border-color 0.2s ease;
          background: var(--bg-primary);
          color: var(--text-primary);
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: var(--accent);
          box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }

        .form-group input:disabled,
        .form-group select:disabled {
          background: var(--bg-tertiary);
          cursor: not-allowed;
        }

        .start-button,
        .stop-button {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          align-self: flex-start;
        }

        .start-button {
          background: var(--accent);
          color: white;
        }

        .start-button:hover:not(:disabled) {
          background: #0056b3;
          transform: translateY(-1px);
        }

        .start-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
          transform: none;
        }

        .stop-button {
          background: var(--error);
          color: white;
        }

        .stop-button:hover {
          background: #c82333;
          transform: translateY(-1px);
        }

        .active-research {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
          padding: 20px;
          background: var(--bg-tertiary);
          border-radius: 8px;
        }

        .status-message {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 500;
          color: var(--accent);
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #ffffff;
          border-top: 2px solid transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          50% { transform: rotate(180deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .controls-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .research-form {
            gap: 12px;
          }

          .start-button {
            align-self: stretch;
          }
        }
      `})]})});n.displayName="ResearchControls",r.exports.default=n});
//# sourceMappingURL=ResearchControls.730bf045.js.map
