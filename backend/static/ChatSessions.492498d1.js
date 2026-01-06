var e=globalThis.parcelRequire10c2,s=e.register;s("7nx9Q",function(s,t){Object.defineProperty(s.exports,"__esModule",{value:!0}),s.exports.default=void 0;var i=o(e("acw62")),a=o(e("gC2yi")),r=e("2zAJi"),n=e("ayMG0");function o(e,s){if("function"==typeof WeakMap)var t=new WeakMap,i=new WeakMap;return(o=function(e,s){if(!s&&e&&e.__esModule)return e;var a,r,n={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return n;if(a=s?i:t){if(a.has(e))return a.get(e);a.set(e,n)}for(let s in e)"default"!==s&&({}).hasOwnProperty.call(e,s)&&((r=(a=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,s))&&(r.get||r.set)?a(n,s,r):n[s]=e[s]);return n})(e,s)}let l=i.default.memo(({onSessionSelect:e,currentSessionId:s})=>{let[t,o]=(0,i.useState)([]),[l,c]=(0,i.useState)(!0),[d,h]=(0,i.useState)(null),[x,p]=(0,i.useState)(!1);(0,i.useEffect)(()=>{m()},[x]);let m=async()=>{try{c(!0);let e=await (0,r.cachedFetch)("/api/chats");o(e||[]),h(null)}catch(e){h(e.message)}finally{c(!1)}},u=async()=>{try{let s=await fetch("/api/chats",{method:"POST"});if(!s.ok)throw Error("Failed to create session");let t=await s.json();e&&e(t.id),await m()}catch(e){h(`Failed to create session: ${e.message}`)}},g=async e=>{if(confirm("Are you sure you want to archive this session?"))try{if(!(await fetch(`/api/chats/${e}/archive`,{method:"POST"})).ok)throw Error("Failed to archive session");await m()}catch(e){h(`Failed to archive session: ${e.message}`)}},f=async e=>{if(confirm("Are you sure you want to permanently delete this session? This action cannot be undone."))try{if(!(await fetch(`/api/chats/${e}`,{method:"DELETE"})).ok)throw Error("Failed to delete session");await m()}catch(e){h(`Failed to delete session: ${e.message}`)}},v=t.filter(e=>x||!e.archived);return l?(0,n.jsxs)("div",{className:"chat-sessions",children:[(0,n.jsxs)("div",{className:"sessions-header",children:[(0,n.jsx)(a.default,{width:"150px",height:"1.2rem"}),(0,n.jsxs)("div",{className:"header-actions",children:[(0,n.jsx)(a.default,{width:"100px",height:"2rem"}),(0,n.jsx)(a.default,{width:"100px",height:"2rem"})]})]}),(0,n.jsx)("div",{className:"sessions-list",children:Array.from({length:3},(e,s)=>(0,n.jsx)("div",{className:"session-item",children:(0,n.jsxs)("div",{className:"document-info",children:[(0,n.jsxs)("div",{className:"session-title-row",children:[(0,n.jsx)(a.default,{width:"80%",height:"1rem"}),(0,n.jsxs)("div",{className:"session-actions",children:[(0,n.jsx)(a.default,{width:"24px",height:"24px",variant:"circular"}),(0,n.jsx)(a.default,{width:"24px",height:"24px",variant:"circular"})]})]}),(0,n.jsx)(a.SkeletonText,{lines:2,width:"100%"}),(0,n.jsx)("div",{className:"session-meta",children:(0,n.jsx)(a.default,{width:"60px",height:"0.8rem"})})]})},s))})]}):(0,n.jsxs)("div",{className:"chat-sessions",children:[(0,n.jsxs)("div",{className:"sessions-header",children:[(0,n.jsx)("h3",{children:"Chat Sessions"}),(0,n.jsxs)("div",{className:"header-actions",children:[(0,n.jsxs)("label",{className:"archive-toggle",children:[(0,n.jsx)("input",{type:"checkbox",checked:x,onChange:e=>p(e.target.checked)}),"Show archived"]}),(0,n.jsx)("button",{onClick:u,className:"new-session-button",children:"+ New Chat"})]})]}),d&&(0,n.jsxs)("div",{className:"error-message",children:[(0,n.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,n.jsx)("span",{children:d}),(0,n.jsx)("button",{onClick:()=>h(null),className:"dismiss-error",children:"×"})]}),0===v.length?(0,n.jsxs)("div",{className:"no-sessions",children:[(0,n.jsx)("p",{children:x?"No archived sessions found.":"No chat sessions found."}),(0,n.jsx)("p",{children:"Start a new conversation to see it here."})]}):(0,n.jsx)("div",{className:"sessions-list",children:v.map(t=>(0,n.jsx)("div",{className:`session-item ${t.id===s?"active":""} ${t.archived?"archived":""}`,onClick:()=>e&&e(t.id),children:(0,n.jsxs)("div",{className:"session-content",children:[(0,n.jsxs)("div",{className:"session-title-row",children:[(0,n.jsx)("h4",{className:"session-title",children:t.title||"Untitled Chat"}),(0,n.jsxs)("div",{className:"session-actions",children:[!t.archived&&(0,n.jsx)("button",{onClick:e=>{e.stopPropagation(),g(t.id)},className:"archive-button",title:"Archive session",children:"📁"}),(0,n.jsx)("button",{onClick:e=>{e.stopPropagation(),f(t.id)},className:"delete-button",title:"Delete session",children:"🗑️"})]})]}),(0,n.jsx)("p",{className:"session-preview",children:(e=>{if(e.summary)return e.summary;if(e.messages&&e.messages.length>0){let s=e.messages[e.messages.length-1];return s.content?s.content.substring(0,100)+"...":"Empty message"}return"New conversation"})(t)}),(0,n.jsxs)("div",{className:"session-meta",children:[(0,n.jsx)("span",{className:"session-date",children:(e=>{if(!e)return"Unknown";let s=new Date(e),t=(new Date-s)/36e5;return t<24?s.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"}):t<168?s.toLocaleDateString([],{weekday:"short",hour:"2-digit",minute:"2-digit"}):s.toLocaleDateString()})(t.created_at)}),t.archived&&(0,n.jsx)("span",{className:"archived-badge",children:"Archived"})]})]})},t.id))}),(0,n.jsx)("style",{children:`
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
      `})]})});l.displayName="ChatSessions",s.exports.default=l}),s("gC2yi",function(s,t){Object.defineProperty(s.exports,"__esModule",{value:!0}),s.exports.default=s.exports.SkeletonText=s.exports.SkeletonTable=s.exports.SkeletonCard=s.exports.SkeletonButton=s.exports.SkeletonAvatar=void 0,(i=e("acw62"))&&i.__esModule;var i,a=e("ayMG0");let r=({width:e="100%",height:s="1rem",className:t="",variant:i="text",animation:r="pulse"})=>{let n={text:"skeleton-text",rectangular:"skeleton-rectangular",circular:"skeleton-circular",avatar:"skeleton-avatar"},o={pulse:"skeleton-pulse",wave:"skeleton-wave"},l=["skeleton",n[i]||n.text,o[r]||o.pulse,t].filter(Boolean).join(" ");return(0,a.jsx)("div",{className:l,style:{width:e,height:s}})};s.exports.SkeletonText=({lines:e=1,width:s="100%",...t})=>(0,a.jsx)("div",{className:"skeleton-text-block",children:Array.from({length:e},(i,n)=>(0,a.jsx)(r,{width:n===e-1?"60%":s,height:"1rem",variant:"text",...t},n))}),s.exports.SkeletonCard=({height:e="200px",...s})=>(0,a.jsxs)("div",{className:"skeleton-card",children:[(0,a.jsx)(r,{height:"2rem",width:"80%",className:"skeleton-card-title",...s}),(0,a.jsx)(r,{height:e,variant:"rectangular",className:"skeleton-card-content",...s}),(0,a.jsxs)("div",{className:"skeleton-card-footer",children:[(0,a.jsx)(r,{width:"40%",height:"0.8rem",...s}),(0,a.jsx)(r,{width:"30%",height:"0.8rem",...s})]})]}),s.exports.SkeletonTable=({rows:e=5,columns:s=4,...t})=>(0,a.jsxs)("div",{className:"skeleton-table",children:[(0,a.jsx)("div",{className:"skeleton-table-header",children:Array.from({length:s},(e,s)=>(0,a.jsx)(r,{height:"1.2rem",width:"100%",...t},s))}),Array.from({length:e},(e,i)=>(0,a.jsx)("div",{className:"skeleton-table-row",children:Array.from({length:s},(e,s)=>(0,a.jsx)(r,{height:"1rem",width:"100%",...t},s))},i))]}),s.exports.SkeletonAvatar=({size:e="40px",...s})=>(0,a.jsx)(r,{width:e,height:e,variant:"circular",...s}),s.exports.SkeletonButton=({width:e="120px",...s})=>(0,a.jsx)(r,{width:e,height:"2.5rem",variant:"rectangular",className:"skeleton-button",...s}),s.exports.default=r});
//# sourceMappingURL=ChatSessions.492498d1.js.map
