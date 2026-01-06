var e=globalThis.parcelRequire10c2;(0,e.register)("93qoo",function(r,a){Object.defineProperty(r.exports,"__esModule",{value:!0}),r.exports.default=void 0;var i=t(e("acw62")),o=e("ayMG0");function t(e,r){if("function"==typeof WeakMap)var a=new WeakMap,i=new WeakMap;return(t=function(e,r){if(!r&&e&&e.__esModule)return e;var o,t,l={__proto__:null,default:e};if(null===e||"object"!=typeof e&&"function"!=typeof e)return l;if(o=r?i:a){if(o.has(e))return o.get(e);o.set(e,l)}for(let r in e)"default"!==r&&({}).hasOwnProperty.call(e,r)&&((t=(o=Object.defineProperty)&&Object.getOwnPropertyDescriptor(e,r))&&(t.get||t.set)?o(l,r,t):l[r]=e[r]);return l})(e,r)}r.exports.default=({onFileUpload:e,acceptedTypes:r=".pdf,.txt,.md,.doc,.docx",maxSizeMB:a=10})=>{let[t,l]=(0,i.useState)(!1),[n,s]=(0,i.useState)(!1),[d,p]=(0,i.useState)(null),[c,x]=(0,i.useState)([]),u=async i=>{try{(e=>{let i=r.split(",").map(e=>e.trim().toLowerCase()),o="."+e.name.split(".").pop().toLowerCase();if(!i.includes(o))throw Error(`File type ${o} is not supported. Allowed types: ${r}`);let t=1048576*a;if(e.size>t)throw Error(`File size (${(e.size/1048576).toFixed(2)}MB) exceeds maximum allowed size (${a}MB)`)})(i),s(!0),p(null);let o={id:Date.now().toString(),name:i.name,size:i.size,type:i.type,uploadedAt:new Date().toISOString(),status:"uploaded"};x(e=>[...e,o]),e&&await e(i,o)}catch(e){p(e.message)}finally{s(!1)}},f=(0,i.useCallback)(async e=>{for(let r of(e.preventDefault(),l(!1),Array.from(e.dataTransfer.files)))await u(r)},[]),m=(0,i.useCallback)(e=>{e.preventDefault(),l(!0)},[]),g=(0,i.useCallback)(e=>{e.preventDefault(),l(!1)},[]),h=async e=>{for(let r of Array.from(e.target.files))await u(r);e.target.value=""};return(0,o.jsxs)("div",{className:"file-upload",children:[(0,o.jsxs)("div",{className:"upload-header",children:[(0,o.jsx)("h3",{children:"Document Upload"}),(0,o.jsx)("p",{children:"Upload documents for Q&A (Phase 5 preparation)"})]}),d&&(0,o.jsxs)("div",{className:"error-message",children:[(0,o.jsx)("span",{className:"error-icon",children:"⚠️"}),(0,o.jsx)("span",{children:d}),(0,o.jsx)("button",{onClick:()=>p(null),className:"dismiss-error",children:"×"})]}),(0,o.jsx)("div",{className:`upload-zone ${t?"drag-over":""} ${n?"uploading":""}`,onDrop:f,onDragOver:m,onDragLeave:g,children:(0,o.jsxs)("div",{className:"upload-content",children:[(0,o.jsx)("div",{className:"upload-icon",children:"📁"}),(0,o.jsx)("div",{className:"upload-text",children:n?(0,o.jsxs)("div",{className:"uploading-indicator",children:[(0,o.jsx)("div",{className:"spinner"}),(0,o.jsx)("p",{children:"Uploading..."})]}):(0,o.jsxs)(o.Fragment,{children:[(0,o.jsxs)("p",{children:["Drag and drop files here, or ",(0,o.jsx)("label",{className:"file-input-label",children:"browse"})]}),(0,o.jsxs)("p",{className:"upload-hint",children:["Supported formats: ",r," (max ",a,"MB each)"]}),(0,o.jsx)("input",{type:"file",multiple:!0,accept:r,onChange:h,className:"file-input",id:"file-input"})]})})]})}),c.length>0&&(0,o.jsxs)("div",{className:"uploaded-files",children:[(0,o.jsxs)("h4",{children:["Uploaded Files (",c.length,")"]}),(0,o.jsx)("div",{className:"files-list",children:c.map(e=>(0,o.jsxs)("div",{className:"file-item",children:[(0,o.jsxs)("div",{className:"file-info",children:[(0,o.jsx)("div",{className:"file-name",children:e.name}),(0,o.jsxs)("div",{className:"file-meta",children:[(e=>{if(0===e)return"0 Bytes";let r=Math.floor(Math.log(e)/Math.log(1024));return parseFloat((e/Math.pow(1024,r)).toFixed(2))+" "+["Bytes","KB","MB","GB"][r]})(e.size)," • Uploaded ",new Date(e.uploadedAt).toLocaleTimeString()]})]}),(0,o.jsx)("div",{className:"file-actions",children:(0,o.jsx)("button",{onClick:()=>{var r;return r=e.id,void x(e=>e.filter(e=>e.id!==r))},className:"remove-file",title:"Remove file",children:"✕"})})]},e.id))})]}),(0,o.jsx)("style",{children:`
        .file-upload {
          background: var(--bg-primary);
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px var(--shadow);
          margin: 20px 0;
        }

        .upload-header h3 {
          margin: 0 0 5px 0;
          color: var(--text-primary);
        }

        .upload-header p {
          margin: 0;
          color: var(--text-secondary);
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

        .dismiss-error {
          margin-left: auto;
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: var(--text-primary);
        }

        .upload-zone {
          border: 2px dashed var(--border-color);
          border-radius: 8px;
          padding: 40px 20px;
          text-align: center;
          transition: all 0.3s ease;
          cursor: pointer;
          background: var(--bg-secondary);
        }

        .upload-zone:hover,
        .upload-zone.drag-over {
          border-color: var(--accent);
          background: rgba(0, 123, 255, 0.05);
        }

        .upload-zone.uploading {
          pointer-events: none;
          opacity: 0.7;
        }

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
        }

        .upload-icon {
          font-size: 48px;
          opacity: 0.6;
        }

        .upload-text p {
          margin: 5px 0;
          color: var(--text-primary);
        }

        .file-input-label {
          color: var(--accent);
          cursor: pointer;
          font-weight: 500;
          text-decoration: underline;
        }

        .file-input {
          display: none;
        }

        .upload-hint {
          font-size: 12px;
          color: var(--text-muted) !important;
          margin-top: 5px !important;
        }

        .uploading-indicator {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
        }

        .spinner {
          width: 30px;
          height: 30px;
          border: 3px solid var(--border-color);
          border-top: 3px solid var(--accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          50% { transform: rotate(180deg); }
          100% { transform: rotate(360deg); }
        }

        .uploaded-files {
          margin-top: 20px;
        }

        .uploaded-files h4 {
          margin: 0 0 15px 0;
          color: var(--text-primary);
          font-size: 16px;
        }

        .files-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .file-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: var(--bg-secondary);
          border-radius: 6px;
          border: 1px solid var(--border-color);
        }

        .file-info {
          flex: 1;
        }

        .file-name {
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .file-meta {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .file-actions {
          margin-left: 10px;
        }

        .remove-file {
          background: var(--error);
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          transition: background-color 0.2s ease;
        }

        .remove-file:hover {
          background: #c82333;
        }

        @media (max-width: 768px) {
          .file-upload {
            margin: 10px;
            padding: 15px;
          }

          .upload-zone {
            padding: 30px 15px;
          }

          .file-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
          }

          .file-actions {
            align-self: flex-end;
            margin-left: 0;
          }
        }
      `})]})}});
//# sourceMappingURL=FileUpload.ccc8d81e.js.map
