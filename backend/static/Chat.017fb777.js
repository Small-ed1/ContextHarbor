function e(e,a,t,s){Object.defineProperty(e,a,{get:t,set:s,enumerable:!0,configurable:!0})}var a=globalThis.parcelRequire10c2,t=a.register;t("g3Ulu",function(t,s){Object.defineProperty(t.exports,"__esModule",{value:!0,configurable:!0}),e(t.exports,"default",()=>l);var r=a("ayMG0"),i=a("acw62"),n=a("kqWnA"),o=a("lW6gq");a("gC2yi");var l=({sessionId:e,onBack:a,onToggleResearch:t,selectedModel:s})=>{let[l,c]=(0,i.useState)([]),[p,d]=(0,i.useState)(""),[x,m]=(0,i.useState)(!1),[g,h]=(0,i.useState)(null),[u,b]=(0,i.useState)(!1),v=(0,i.useRef)(null);(0,i.useRef)(null),(0,i.useEffect)(()=>{f()},[e]),(0,i.useEffect)(()=>{w()},[l]);let f=async()=>{if(e)try{m(!0);let a=await fetch(`/api/chats/${e}`);if(a.ok){let e=await a.json();c(e.messages||[]),h(null)}else h("Failed to load chat session")}catch(e){h(`Error loading chat: ${e.message}`)}finally{m(!1)}},w=()=>{v.current?.scrollIntoView({behavior:"smooth"})},y=e=>new Date(e).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"}),j=async()=>{if(!p.trim()||x)return;let e={id:Date.now(),type:"user",content:p.trim(),timestamp:new Date};c(a=>[...a,e]),d(""),m(!0),h(null);try{let a=await fetch("/api/v1/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:e.content,mode:u?"research":"chat",project:"default",model:s||void 0,history:l.slice(-10).map(e=>({type:e.type,content:e.content}))})});if(a.ok){let e=await a.json(),t={id:Date.now()+1,type:"ai",content:e.response,timestamp:new Date};c(e=>[...e,t])}else throw Error(`API error: ${a.status}`)}catch(e){h(`Failed to send message: ${e.message}`),m(!1)}finally{m(!1)}};return(0,r.jsxs)("div",{className:"chat-interface",children:[(0,r.jsxs)("div",{className:"chat-header",children:[(0,r.jsx)("button",{onClick:a,className:"back-button",children:"← Back to Sessions"}),(0,r.jsxs)("div",{className:"chat-info",children:[(0,r.jsx)("h3",{children:"Chat Session"}),(0,r.jsxs)("p",{children:["Session ID: ",e]}),s&&(0,r.jsxs)("p",{children:["Model: ",s]})]}),(0,r.jsx)("div",{className:"chat-controls",children:(0,r.jsxs)("label",{className:"research-toggle",children:[(0,r.jsx)("input",{type:"checkbox",checked:u,onChange:e=>b(e.target.checked)}),(0,r.jsx)("span",{className:"toggle-label",children:"Deep Research Mode"})]})})]}),(0,r.jsxs)("div",{className:"chat-container",children:[(0,r.jsx)("div",{className:"messages-area",children:0!==l.length||x?(0,r.jsxs)(r.Fragment,{children:[l.map(e=>(0,r.jsx)("div",{children:"user"===e.type?(0,r.jsxs)("div",{className:"message user-message",children:[(0,r.jsxs)("div",{className:"message-content",children:[(0,r.jsx)("div",{className:"message-text",children:e.content}),(0,r.jsx)("div",{className:"message-tail"})]}),(0,r.jsxs)("div",{className:"message-meta",children:[(0,r.jsx)("span",{className:"timestamp",children:y(e.timestamp)}),(0,r.jsx)("span",{className:"message-status",children:"✓"})]})]}):(0,r.jsxs)("div",{className:"message ai-message",children:[(0,r.jsxs)("div",{className:"message-header",children:[(0,r.jsx)("div",{className:"ai-avatar",children:(0,r.jsx)("div",{className:"avatar-gradient",children:(0,r.jsx)("span",{className:"avatar-icon",children:"🤖"})})}),(0,r.jsxs)("div",{className:"ai-info",children:[(0,r.jsx)("span",{className:"ai-name",children:"AI Assistant"}),(0,r.jsx)("span",{className:"model-badge",children:s||"Llama 3.2"})]})]}),(0,r.jsxs)("div",{className:"message-content",children:[(0,r.jsx)("div",{className:"answer-text",children:(0,r.jsx)(n.default,{content:e.content})}),(0,r.jsx)("div",{className:"message-tail"})]}),(0,r.jsxs)("div",{className:"message-meta",children:[(0,r.jsx)("span",{className:"timestamp",children:y(e.timestamp)}),(0,r.jsxs)("div",{className:"message-actions",children:[(0,r.jsx)("button",{className:"action-btn",title:"Copy message",children:"📋"}),(0,r.jsx)("button",{className:"action-btn",title:"Regenerate",children:"🔄"})]})]})]})},e.id)),x&&(0,r.jsxs)("div",{className:"message ai-message typing",children:[(0,r.jsxs)("div",{className:"message-header",children:[(0,r.jsx)("div",{className:"ai-avatar",children:(0,r.jsx)("div",{className:"avatar-gradient",children:(0,r.jsx)("span",{className:"avatar-icon",children:"🤖"})})}),(0,r.jsxs)("div",{className:"ai-info",children:[(0,r.jsx)("span",{className:"ai-name",children:"AI Assistant"}),(0,r.jsxs)("span",{className:"typing-indicator",children:[(0,r.jsx)("span",{}),(0,r.jsx)("span",{}),(0,r.jsx)("span",{})]})]})]}),(0,r.jsx)("div",{className:"message-content",children:(0,r.jsxs)("div",{className:"typing-placeholder",children:[(0,r.jsxs)("div",{className:"typing-dots",children:[(0,r.jsx)("span",{}),(0,r.jsx)("span",{}),(0,r.jsx)("span",{})]}),(0,r.jsx)("span",{className:"typing-text",children:"AI is thinking..."})]})})]}),g&&(0,r.jsx)("div",{className:"error-message",children:(0,r.jsxs)("span",{children:["⚠️ ",g]})}),(0,r.jsx)("div",{ref:v})]}):(0,r.jsxs)("div",{className:"welcome-message",children:[(0,r.jsxs)("div",{className:"welcome-illustration",children:[(0,r.jsx)("div",{className:"welcome-glow"}),(0,r.jsx)("div",{className:"welcome-icon",children:"🚀"})]}),(0,r.jsx)("h4",{children:"Welcome to your AI Chat!"}),(0,r.jsx)("p",{children:"I'm here to help with questions, research, creative tasks, and more. What would you like to explore today?"}),(0,r.jsxs)("div",{className:"suggestion-chips",children:[(0,r.jsx)("button",{className:"chip",onClick:()=>d("Explain quantum computing in simple terms"),children:"💡 Explain quantum computing"}),(0,r.jsx)("button",{className:"chip",onClick:()=>d("Write a creative story about space exploration"),children:"📖 Write a story"}),(0,r.jsx)("button",{className:"chip",onClick:()=>d("Help me debug this code"),children:"🐛 Debug code"}),(0,r.jsx)("button",{className:"chip",onClick:()=>b(!0),children:"🔬 Research mode"})]})]})}),(0,r.jsx)("div",{className:"input-area",children:(0,r.jsxs)("div",{className:"message-input-container",children:[(0,r.jsx)(o.default,{onSendMessage:e=>{d(e),j()},placeholder:u?"Ask a research question...":"Type your message..."}),(0,r.jsx)("div",{className:"input-actions",children:(0,r.jsx)("button",{className:`mode-toggle ${u?"active":""}`,onClick:()=>b(!u),title:u?"Switch to chat mode":"Switch to research mode",disabled:x,children:u?"🔬":"💬"})}),u&&(0,r.jsxs)("div",{className:"research-notice",children:[(0,r.jsx)("span",{className:"notice-icon",children:"🔬"}),(0,r.jsx)("span",{className:"notice-text",children:"Research mode enabled - This may take longer for comprehensive analysis"})]})]})})]}),(0,r.jsx)("style",{children:`
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
       `})]})}}),t("kqWnA",function(t,s){e(t.exports,"default",()=>o);var r,i=a("ayMG0");let n=((r=a("acw62"))&&r.__esModule?r.default:r).memo(({content:e,isEditable:a=!1,onChange:t,placeholder:s="Type your message..."})=>{if(!a){let a=e?e.replace(/```([\s\S]*?)```/g,"<pre><code>$1</code></pre>").replace(/^### (.*$)/gim,"<h3>$1</h3>").replace(/^## (.*$)/gim,"<h2>$1</h2>").replace(/^# (.*$)/gim,"<h1>$1</h1>").replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>").replace(/\*(.*?)\*/g,"<em>$1</em>").replace(/`([^`]+)`/g,"<code>$1</code>").replace(/^\* (.*$)/gim,"<li>$1</li>").replace(/^\d+\. (.*$)/gim,"<li>$1</li>").replace(/\n\n/g,"</p><p>").replace(/\n/g,"<br>").replace(/^---$/gm,"<hr>").replace(/^([^<].*?)(<|$)/gm,"<p>$1</p>$2"):"";return(0,i.jsx)("div",{className:"rich-text-display",dangerouslySetInnerHTML:{__html:a}})}return(0,i.jsx)("textarea",{value:e,onChange:e=>t(e.target.value),placeholder:s,className:"rich-text-editor",rows:4})});n.displayName="RichTextMessage";var o=n}),t("lW6gq",function(t,s){e(t.exports,"default",()=>n);var r=a("ayMG0"),i=a("acw62"),n=({onSendMessage:e,placeholder:a="Type your message..."})=>{let[t,s]=(0,i.useState)("");return(0,r.jsxs)("form",{onSubmit:a=>{a.preventDefault(),t.trim()&&(e(t.trim()),s(""))},className:"chat-input-form",children:[(0,r.jsx)("textarea",{value:t,onChange:e=>s(e.target.value),placeholder:a,className:"chat-textarea",rows:3}),(0,r.jsx)("button",{type:"submit",className:"send-button",children:"Send"})]})}}),t("gC2yi",function(t,s){e(t.exports,"SkeletonText",()=>n),e(t.exports,"default",()=>o);var r=a("ayMG0");a("acw62");let i=({width:e="100%",height:a="1rem",className:t="",variant:s="text",animation:i="pulse"})=>{let n={text:"skeleton-text",rectangular:"skeleton-rectangular",circular:"skeleton-circular",avatar:"skeleton-avatar"},o={pulse:"skeleton-pulse",wave:"skeleton-wave"},l=["skeleton",n[s]||n.text,o[i]||o.pulse,t].filter(Boolean).join(" ");return(0,r.jsx)("div",{className:l,style:{width:e,height:a}})},n=({lines:e=1,width:a="100%",...t})=>(0,r.jsx)("div",{className:"skeleton-text-block",children:Array.from({length:e},(s,n)=>(0,r.jsx)(i,{width:n===e-1?"60%":a,height:"1rem",variant:"text",...t},n))});var o=i});
//# sourceMappingURL=Chat.017fb777.js.map
