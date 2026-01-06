var e=globalThis.parcelRequire10c2,t=e.register;t("cc46N",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.default=void 0;var s=l(e("acw62")),r=o(e("lH95N")),n=o(e("luNHW")),i=e("ayMG0");function o(e){return e&&e.__esModule?e:{default:e}}function l(e,t){if("function"==typeof WeakMap)var a=new WeakMap,s=new WeakMap;return(l=function(e,t){if(!t&&e&&e.__esModule)return e;var r,n,i={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return i;if(r=t?s:a){if(r.has(e))return r.get(e);r.set(e,i)}for(let t in e)"default"!==t&&({}).hasOwnProperty.call(e,t)&&((n=(r=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,t))&&(n.get||n.set)?r(i,t,n):i[t]=e[t]);return i})(e,t)}t.exports.default=()=>{let[e,t]=(0,s.useState)([]),[a,o]=(0,s.useState)("selector");return(0,i.jsx)("div",{className:"document-qa-tab",children:"selector"===a?(0,i.jsx)(r.default,{selectedDocuments:e,onSelectionChange:e=>{t(e),e.length>0&&o("qa")},maxSelections:5}):(0,i.jsx)(n.default,{selectedDocuments:e,onBack:()=>{o("selector")}})})}}),t("lH95N",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.default=void 0;var s,r=c(e("acw62")),n=c(e("gC2yi")),i=e("2zAJi"),o=(s=e("6feOA"))&&s.__esModule?s:{default:s},l=e("ayMG0");function c(e,t){if("function"==typeof WeakMap)var a=new WeakMap,s=new WeakMap;return(c=function(e,t){if(!t&&e&&e.__esModule)return e;var r,n,i={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return i;if(r=t?s:a){if(r.has(e))return r.get(e);r.set(e,i)}for(let t in e)"default"!==t&&({}).hasOwnProperty.call(e,t)&&((n=(r=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,t))&&(n.get||n.set)?r(i,t,n):i[t]=e[t]);return i})(e,t)}let d=r.default.memo(({selectedDocuments:e,onSelectionChange:t,maxSelections:a=5})=>{let[s,c]=(0,r.useState)([]),[d,p]=(0,r.useState)(!0),[m,u]=(0,r.useState)(null),[x,h]=(0,r.useState)(""),[g,f]=(0,r.useState)("all");(0,r.useEffect)(()=>{v()},[]);let v=async()=>{try{p(!0);let e=await (0,i.cachedFetch)("/api/documents");c(e.documents||[]),u(null)}catch(e){u(e.message),c([{id:"doc1",filename:"research_paper.pdf",title:"Advances in Machine Learning",type:"pdf",size:2457600,uploadedAt:"2024-01-15T10:30:00Z",status:"processed",chunkCount:45},{id:"doc2",filename:"user_manual.docx",title:"System User Manual",type:"docx",size:512e3,uploadedAt:"2024-01-14T15:20:00Z",status:"processed",chunkCount:23},{id:"doc3",filename:"notes.txt",title:"Meeting Notes",type:"txt",size:16384,uploadedAt:"2024-01-13T09:15:00Z",status:"processed",chunkCount:8}])}finally{p(!1)}},y=s=>{let r=e.includes(s)?e.filter(e=>e!==s):[...e,s];r.length<=a&&t(r)},b=e=>{if(0===e)return"0 Bytes";let t=Math.floor(Math.log(e)/Math.log(1024));return parseFloat((e/Math.pow(1024,t)).toFixed(2))+" "+["Bytes","KB","MB","GB"][t]},j=e=>new Date(e).toLocaleDateString([],{year:"numeric",month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"}),w=s.filter(e=>{let t=e.filename.toLowerCase().includes(x.toLowerCase())||e.title&&e.title.toLowerCase().includes(x.toLowerCase()),a="all"===g||e.type===g;return t&&a}),N=e=>{switch(e){case"processed":return"#28a745";case"processing":return"#ffc107";case"failed":return"#dc3545";default:return"#6c757d"}};return d?(0,l.jsxs)("div",{className:"document-selector",children:[(0,l.jsxs)("div",{className:"selector-header",children:[(0,l.jsx)(n.default,{width:"200px",height:"1.5rem"}),(0,l.jsx)(n.default,{width:"120px",height:"1rem"})]}),(0,l.jsxs)("div",{className:"selector-controls",children:[(0,l.jsx)(n.default,{width:"100%",height:"2.5rem"}),(0,l.jsx)(n.default,{width:"120px",height:"2.5rem"})]}),(0,l.jsx)("div",{className:"documents-list",children:Array.from({length:4},(e,t)=>(0,l.jsxs)("div",{className:"document-item",children:[(0,l.jsx)(n.default,{width:"20px",height:"20px",variant:"circular",className:"document-checkbox"}),(0,l.jsxs)("div",{className:"document-info",children:[(0,l.jsxs)("div",{className:"document-header",children:[(0,l.jsx)(n.default,{width:"70%",height:"1rem"}),(0,l.jsx)("div",{className:"document-meta",children:(0,l.jsx)(n.default,{width:"50px",height:"1rem"})})]}),(0,l.jsx)(n.SkeletonText,{lines:2,width:"100%"}),(0,l.jsx)(n.default,{width:"80px",height:"0.8rem"})]})]},t))})]}):(0,l.jsxs)("div",{className:"document-selector",children:[(0,l.jsxs)("div",{className:"selector-header",children:[(0,l.jsx)("h3",{children:"Select Documents"}),(0,l.jsxs)("span",{className:"selection-count",children:[e.length,"/",a," selected"]})]}),(0,l.jsxs)("div",{className:"selector-controls",children:[(0,l.jsxs)("div",{className:"search-bar",children:[(0,l.jsx)("input",{type:"text",placeholder:"Search documents...",value:x,onChange:e=>h(e.target.value),className:"search-input"}),(0,l.jsx)("span",{className:"search-icon",children:"🔍"})]}),(0,l.jsx)("div",{className:"filter-controls",children:(0,l.jsxs)("label",{children:["Type:",(0,l.jsxs)("select",{value:g,onChange:e=>f(e.target.value),className:"type-filter",children:[(0,l.jsx)("option",{value:"all",children:"All Types"}),(0,l.jsx)("option",{value:"pdf",children:"PDF"}),(0,l.jsx)("option",{value:"docx",children:"Word"}),(0,l.jsx)("option",{value:"txt",children:"Text"})]})]})})]}),m&&(0,l.jsxs)("div",{className:"error-message",children:[(0,l.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,l.jsx)("span",{children:m})]}),(0,l.jsx)("div",{className:"documents-list",children:0===w.length?(0,l.jsxs)("div",{className:"no-documents",children:[(0,l.jsx)("p",{children:x||"all"!==g?"No documents match your search.":"No documents uploaded yet."}),(0,l.jsx)("p",{children:"Upload documents in the Documents tab to get started."})]}):w.length>20?(0,l.jsx)(o.default,{items:w,itemHeight:100,containerHeight:400,renderItem:(t,s)=>(0,l.jsxs)("div",{className:`document-item ${e.includes(t.id)?"selected":""}`,onClick:()=>y(t.id),children:[(0,l.jsx)("div",{className:"document-checkbox",children:(0,l.jsx)("input",{type:"checkbox",checked:e.includes(t.id),onChange:()=>{},disabled:!e.includes(t.id)&&e.length>=a})}),(0,l.jsxs)("div",{className:"document-info",children:[(0,l.jsxs)("div",{className:"document-header",children:[(0,l.jsx)("h4",{className:"document-title",children:t.title||t.filename}),(0,l.jsxs)("div",{className:"document-meta",children:[(0,l.jsx)("span",{className:"document-type",children:t.type.toUpperCase()}),(0,l.jsxs)("span",{className:"document-status",style:{color:N(t.status)},children:["● ",t.status]})]})]}),(0,l.jsxs)("div",{className:"document-details",children:[(0,l.jsx)("span",{className:"document-filename",children:t.filename}),(0,l.jsx)("span",{className:"document-size",children:b(t.size)}),t.chunkCount&&(0,l.jsxs)("span",{className:"document-chunks",children:[t.chunkCount," chunks"]})]}),(0,l.jsxs)("div",{className:"document-date",children:["Uploaded ",j(t.uploadedAt)]})]})]},t.id)}):w.map(t=>(0,l.jsxs)("div",{className:`document-item ${e.includes(t.id)?"selected":""}`,onClick:()=>y(t.id),children:[(0,l.jsx)("div",{className:"document-checkbox",children:(0,l.jsx)("input",{type:"checkbox",checked:e.includes(t.id),onChange:()=>{},disabled:!e.includes(t.id)&&e.length>=a})}),(0,l.jsxs)("div",{className:"document-info",children:[(0,l.jsxs)("div",{className:"document-header",children:[(0,l.jsx)("h4",{className:"document-title",children:t.title||t.filename}),(0,l.jsxs)("div",{className:"document-meta",children:[(0,l.jsx)("span",{className:"document-type",children:t.type.toUpperCase()}),(0,l.jsxs)("span",{className:"document-status",style:{color:N(t.status)},children:["● ",t.status]})]})]}),(0,l.jsxs)("div",{className:"document-details",children:[(0,l.jsx)("span",{className:"document-filename",children:t.filename}),(0,l.jsx)("span",{className:"document-size",children:b(t.size)}),t.chunkCount&&(0,l.jsxs)("span",{className:"document-chunks",children:[t.chunkCount," chunks"]})]}),(0,l.jsxs)("div",{className:"document-date",children:["Uploaded ",j(t.uploadedAt)]})]})]},t.id))}),(0,l.jsx)("style",{children:`
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
      `})]})});d.displayName="DocumentSelector",t.exports.default=d}),t("gC2yi",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.default=t.exports.SkeletonText=t.exports.SkeletonTable=t.exports.SkeletonCard=t.exports.SkeletonButton=t.exports.SkeletonAvatar=void 0,(s=e("acw62"))&&s.__esModule;var s,r=e("ayMG0");let n=({width:e="100%",height:t="1rem",className:a="",variant:s="text",animation:n="pulse"})=>{let i={text:"skeleton-text",rectangular:"skeleton-rectangular",circular:"skeleton-circular",avatar:"skeleton-avatar"},o={pulse:"skeleton-pulse",wave:"skeleton-wave"},l=["skeleton",i[s]||i.text,o[n]||o.pulse,a].filter(Boolean).join(" ");return(0,r.jsx)("div",{className:l,style:{width:e,height:t}})};t.exports.SkeletonText=({lines:e=1,width:t="100%",...a})=>(0,r.jsx)("div",{className:"skeleton-text-block",children:Array.from({length:e},(s,i)=>(0,r.jsx)(n,{width:i===e-1?"60%":t,height:"1rem",variant:"text",...a},i))}),t.exports.SkeletonCard=({height:e="200px",...t})=>(0,r.jsxs)("div",{className:"skeleton-card",children:[(0,r.jsx)(n,{height:"2rem",width:"80%",className:"skeleton-card-title",...t}),(0,r.jsx)(n,{height:e,variant:"rectangular",className:"skeleton-card-content",...t}),(0,r.jsxs)("div",{className:"skeleton-card-footer",children:[(0,r.jsx)(n,{width:"40%",height:"0.8rem",...t}),(0,r.jsx)(n,{width:"30%",height:"0.8rem",...t})]})]}),t.exports.SkeletonTable=({rows:e=5,columns:t=4,...a})=>(0,r.jsxs)("div",{className:"skeleton-table",children:[(0,r.jsx)("div",{className:"skeleton-table-header",children:Array.from({length:t},(e,t)=>(0,r.jsx)(n,{height:"1.2rem",width:"100%",...a},t))}),Array.from({length:e},(e,s)=>(0,r.jsx)("div",{className:"skeleton-table-row",children:Array.from({length:t},(e,t)=>(0,r.jsx)(n,{height:"1rem",width:"100%",...a},t))},s))]}),t.exports.SkeletonAvatar=({size:e="40px",...t})=>(0,r.jsx)(n,{width:e,height:e,variant:"circular",...t}),t.exports.SkeletonButton=({width:e="120px",...t})=>(0,r.jsx)(n,{width:e,height:"2.5rem",variant:"rectangular",className:"skeleton-button",...t}),t.exports.default=n}),t("6feOA",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.useDynamicVirtualization=t.exports.default=void 0;var s=n(e("acw62")),r=e("ayMG0");function n(e,t){if("function"==typeof WeakMap)var a=new WeakMap,s=new WeakMap;return(n=function(e,t){if(!t&&e&&e.__esModule)return e;var r,n,i={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return i;if(r=t?s:a){if(r.has(e))return r.get(e);r.set(e,i)}for(let t in e)"default"!==t&&({}).hasOwnProperty.call(e,t)&&((n=(r=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,t))&&(n.get||n.set)?r(i,t,n):i[t]=e[t]);return i})(e,t)}t.exports.useDynamicVirtualization=(e,t=60)=>{let[a,r]=(0,s.useState)(new Map),[n,i]=(0,s.useState)(e.length*t),o=(0,s.useCallback)((a,s)=>{r(r=>{let n=new Map(r);if(n.get(a)!==s){n.set(a,s);let r=0;for(let a=0;a<e.length;a++)r+=n.get(a)||t;i(r)}return n})},[e.length,t]),l=(0,s.useCallback)(e=>a.get(e)||t,[a,t]),c=(0,s.useCallback)(e=>{let t=0;for(let a=0;a<e;a++)t+=l(a);return t},[l]),d=(0,s.useCallback)(t=>{let a=0;for(let s=0;s<e.length;s++){let e=l(s);if(a+e>t)return s;a+=e}return e.length-1},[e.length,l]);return{totalHeight:n,measureItem:o,getItemHeight:l,getOffsetForIndex:c,getIndexForOffset:d}},t.exports.default=({items:e,itemHeight:t=60,containerHeight:a=400,renderItem:n,overscan:i=5,className:o=""})=>{let[l,c]=(0,s.useState)(0),[d,p]=(0,s.useState)(a),m=(0,s.useRef)(null),u=(0,s.useCallback)(e=>{c(e.target.scrollTop)},[]),x=Math.max(0,Math.floor(l/t)-i),h=Math.min(e.length-1,Math.ceil((l+d)/t)+i),g=e.length*t,f=x*t,v=e.slice(x,h+1);return(0,s.useEffect)(()=>{let e=()=>{m.current&&p(m.current.clientHeight)};return e(),window.addEventListener("resize",e),()=>window.removeEventListener("resize",e)},[]),(0,r.jsx)("div",{ref:m,className:`virtualized-list ${o}`,style:{height:a,overflowY:"auto",position:"relative"},onScroll:u,children:(0,r.jsx)("div",{style:{height:g,position:"relative"},children:(0,r.jsx)("div",{style:{transform:`translateY(${f}px)`,position:"absolute",top:0,left:0,right:0},children:v.map((e,a)=>(0,r.jsx)("div",{style:{height:t},children:n(e,x+a)},x+a))})})})}}),t("luNHW",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.default=void 0;var s,r=o(e("acw62")),n=(s=e("kqWnA"))&&s.__esModule?s:{default:s},i=e("ayMG0");function o(e,t){if("function"==typeof WeakMap)var a=new WeakMap,s=new WeakMap;return(o=function(e,t){if(!t&&e&&e.__esModule)return e;var r,n,i={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return i;if(r=t?s:a){if(r.has(e))return r.get(e);r.set(e,i)}for(let t in e)"default"!==t&&({}).hasOwnProperty.call(e,t)&&((n=(r=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,t))&&(n.get||n.set)?r(i,t,n):i[t]=e[t]);return i})(e,t)}t.exports.default=({selectedDocuments:e,onBack:t})=>{let[a,s]=(0,r.useState)([]),[o,l]=(0,r.useState)(""),[c,d]=(0,r.useState)(!1),[p,m]=(0,r.useState)(null),u=(0,r.useRef)(null);(0,r.useEffect)(()=>{u.current?.scrollIntoView({behavior:"smooth"})},[a]);let x=async t=>{if(t.preventDefault(),!o.trim()||c)return;let a=o.trim();l("");let r={id:Date.now().toString(),type:"user",content:a,timestamp:new Date};s(e=>[...e,r]),d(!0),m(null);try{let t=await fetch("/api/qa/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:a,document_ids:e,max_results:5})});if(!t.ok)throw Error("Failed to get answer");let r=await t.json(),n={id:(Date.now()+1).toString(),type:"ai",content:r.answer,sources:r.sources||[],confidence:r.confidence,timestamp:new Date};s(e=>[...e,n])}catch(t){m(t.message),setTimeout(()=>{let t=`Based on the ${e.length} selected document(s), here's what I found regarding "${a}":

This is a placeholder response. In the full implementation, this would contain actual answers extracted from the uploaded documents using vector similarity search and LLM synthesis.

Key points from the documents:
\u{2022} Point 1 from document analysis
\u{2022} Point 2 with source citations
\u{2022} Point 3 with confidence scoring

Sources: ${e.join(", ")}`,r={id:(Date.now()+1).toString(),type:"ai",content:t,sources:e.map(e=>({id:e,relevance:.85})),confidence:.78,timestamp:new Date};s(e=>[...e,r]),m(null)},2e3)}finally{d(!1)}},h=e=>e.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});return(0,i.jsxs)("div",{className:"document-qa",children:[(0,i.jsxs)("div",{className:"qa-header",children:[(0,i.jsx)("button",{onClick:t,className:"back-button",children:"← Back to Document Selection"}),(0,i.jsxs)("div",{className:"qa-info",children:[(0,i.jsx)("h3",{children:"Document Q&A"}),(0,i.jsxs)("p",{children:["Ask questions about your ",e.length," selected document(s)"]})]})]}),(0,i.jsxs)("div",{className:"chat-container",children:[(0,i.jsx)("div",{className:"messages-area",children:0===a.length?c?(0,i.jsxs)("div",{className:"loading-messages",children:[(0,i.jsxs)("div",{className:"message ai-message",children:[(0,i.jsxs)("div",{className:"message-header",children:[(0,i.jsx)(Skeleton,{width:"120px",height:"1rem"}),(0,i.jsx)(Skeleton,{width:"80px",height:"1rem"})]}),(0,i.jsx)("div",{className:"message-content",children:(0,i.jsx)(SkeletonText,{lines:3,width:"100%"})})]}),(0,i.jsx)("div",{className:"message user-message",children:(0,i.jsx)("div",{className:"message-content",children:(0,i.jsx)(SkeletonText,{lines:2,width:"80%"})})})]}):(0,i.jsxs)("div",{className:"welcome-message",children:[(0,i.jsx)("div",{className:"welcome-icon",children:"📚"}),(0,i.jsx)("h4",{children:"Welcome to Document Q&A"}),(0,i.jsx)("p",{children:"Ask me anything about your uploaded documents. I'll search through the content and provide relevant answers with source citations."}),(0,i.jsxs)("div",{className:"example-questions",children:[(0,i.jsx)("p",{children:(0,i.jsx)("strong",{children:"Example questions:"})}),(0,i.jsxs)("ul",{children:[(0,i.jsx)("li",{children:'"What are the main findings in this research paper?"'}),(0,i.jsx)("li",{children:'"Summarize the key points from chapter 3"'}),(0,i.jsx)("li",{children:'"What does the document say about machine learning?"'})]})]})]}):(0,i.jsxs)(i.Fragment,{children:[a.map(e=>(0,i.jsx)("div",{children:"user"===e.type?(0,i.jsxs)("div",{className:"message user-message",children:[(0,i.jsx)("div",{className:"message-content",children:(0,i.jsx)("p",{children:e.content})}),(0,i.jsx)("div",{className:"message-meta",children:(0,i.jsx)("span",{className:"timestamp",children:h(e.timestamp)})})]}):(0,i.jsxs)("div",{className:"message ai-message",children:[(0,i.jsxs)("div",{className:"message-header",children:[(0,i.jsx)("div",{className:"ai-avatar",children:"🤖"}),(0,i.jsxs)("div",{className:"ai-info",children:[(0,i.jsx)("span",{className:"ai-name",children:"Document Assistant"}),e.confidence&&(0,i.jsxs)("span",{className:"confidence-score",children:["Confidence: ",(100*e.confidence).toFixed(0),"%"]})]})]}),(0,i.jsxs)("div",{className:"message-content",children:[(0,i.jsx)("div",{className:"answer-text",children:(0,i.jsx)(n.default,{content:e.content})}),e.sources&&e.sources.length>0&&(0,i.jsxs)("div",{className:"sources-section",children:[(0,i.jsx)("h5",{children:"Sources:"}),(0,i.jsx)("div",{className:"sources-list",children:e.sources.map((e,t)=>(0,i.jsxs)("div",{className:"source-item",children:[(0,i.jsx)("span",{className:"source-id",children:e.id}),e.relevance&&(0,i.jsxs)("span",{className:"source-relevance",children:[(100*e.relevance).toFixed(0),"% relevant"]})]},t))})]})]}),(0,i.jsx)("div",{className:"message-meta",children:(0,i.jsx)("span",{className:"timestamp",children:h(e.timestamp)})})]})},e.id)),c&&(0,i.jsxs)("div",{className:"message ai-message loading",children:[(0,i.jsxs)("div",{className:"message-header",children:[(0,i.jsx)("div",{className:"ai-avatar",children:"🤖"}),(0,i.jsxs)("div",{className:"ai-info",children:[(0,i.jsx)("span",{className:"ai-name",children:"Document Assistant"}),(0,i.jsx)("span",{className:"loading-text",children:"Searching documents..."})]})]}),(0,i.jsx)("div",{className:"message-content",children:(0,i.jsx)("div",{className:"loading-indicator",children:(0,i.jsxs)("div",{className:"typing-dots",children:[(0,i.jsx)("span",{}),(0,i.jsx)("span",{}),(0,i.jsx)("span",{})]})})})]}),(0,i.jsx)("div",{ref:u})]})}),p&&(0,i.jsxs)("div",{className:"error-banner",children:[(0,i.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,i.jsx)("span",{children:p}),(0,i.jsx)("button",{onClick:()=>m(null),className:"dismiss-error",children:"×"})]}),(0,i.jsxs)("form",{onSubmit:x,className:"query-form",children:[(0,i.jsxs)("div",{className:"query-input-container",children:[(0,i.jsx)("textarea",{value:o,onChange:e=>l(e.target.value),placeholder:"Ask a question about your documents...",className:"query-input",rows:1,disabled:c,onKeyDown:e=>{"Enter"!==e.key||e.shiftKey||(e.preventDefault(),x(e))}}),(0,i.jsx)("button",{type:"submit",className:"submit-button",disabled:!o.trim()||c,children:c?(0,i.jsx)("div",{className:"spinner"}):(0,i.jsx)("span",{className:"send-icon",children:"➤"})})]}),(0,i.jsx)("div",{className:"query-help",children:"Press Enter to send, Shift+Enter for new line"})]})]}),(0,i.jsx)("style",{children:`
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
      `})]})}}),t("kqWnA",function(t,a){Object.defineProperty(t.exports,"__esModule",{value:!0}),t.exports.default=void 0;var s,r=(s=e("acw62"))&&s.__esModule?s:{default:s},n=e("ayMG0");let i=r.default.memo(({content:e,isEditable:t=!1,onChange:a,placeholder:s="Type your message..."})=>{if(!t){let t=e?e.replace(/```([\s\S]*?)```/g,"<pre><code>$1</code></pre>").replace(/^### (.*$)/gim,"<h3>$1</h3>").replace(/^## (.*$)/gim,"<h2>$1</h2>").replace(/^# (.*$)/gim,"<h1>$1</h1>").replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>").replace(/\*(.*?)\*/g,"<em>$1</em>").replace(/`([^`]+)`/g,"<code>$1</code>").replace(/^\* (.*$)/gim,"<li>$1</li>").replace(/^\d+\. (.*$)/gim,"<li>$1</li>").replace(/\n\n/g,"</p><p>").replace(/\n/g,"<br>").replace(/^---$/gm,"<hr>").replace(/^([^<].*?)(<|$)/gm,"<p>$1</p>$2"):"";return(0,n.jsx)("div",{className:"rich-text-display",dangerouslySetInnerHTML:{__html:t}})}return(0,n.jsx)("textarea",{value:e,onChange:e=>a(e.target.value),placeholder:s,className:"rich-text-editor",rows:4})});i.displayName="RichTextMessage",t.exports.default=i});
//# sourceMappingURL=DocumentQATab.31ff680c.js.map
