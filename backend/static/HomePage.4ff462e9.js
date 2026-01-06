function e(e,t,a,i){Object.defineProperty(e,t,{get:a,set:i,enumerable:!0,configurable:!0})}var t=globalThis.parcelRequire10c2,a=t.register;a("goKgh",function(a,i){Object.defineProperty(a.exports,"__esModule",{value:!0,configurable:!0}),e(a.exports,"default",()=>n);var r=t("ayMG0"),o=t("acw62");t("kqWnA");var n=({onStartChat:e,onStartResearch:t,selectedModel:a,onModelChange:i,settings:n})=>{let[s,c]=(0,o.useState)(0),[l,p]=(0,o.useState)("");(0,o.useEffect)(()=>{let e=()=>c(window.scrollY);return window.addEventListener("scroll",e),()=>window.removeEventListener("scroll",e)},[]);let d=()=>{l.trim()&&e(l.trim())};return(0,r.jsxs)("div",{className:"home-page",children:[(0,r.jsxs)("section",{className:"hero-section",children:[(0,r.jsxs)("div",{className:"hero-content",children:[(0,r.jsxs)(motion.div,{className:"hero-header",initial:{opacity:0,y:30},animate:{opacity:1,y:0},transition:{duration:.8,ease:"easeOut"},children:[(0,r.jsxs)("h1",{className:"hero-title",children:[(0,r.jsx)("span",{className:"hero-title-main",children:"Welcome to"}),(0,r.jsx)("span",{className:"hero-title-accent",children:"Router Phase 1"})]}),(0,r.jsx)("p",{className:"hero-subtitle",children:"Advanced AI assistant with research capabilities and tool integration"})]}),(0,r.jsxs)(motion.div,{className:"chat-bar",initial:{opacity:0,y:20},animate:{opacity:1,y:0},transition:{duration:.8,delay:.2,ease:"easeOut"},children:[(0,r.jsxs)("div",{className:"model-indicator",children:[(0,r.jsx)("div",{className:"model-icon",children:"🤖"}),(0,r.jsxs)("div",{className:"model-info",children:[(0,r.jsx)("span",{className:"model-label",children:"Active Model"}),(0,r.jsx)("span",{className:"model-name",children:a||"Llama 3.2 (Default)"})]})]}),(0,r.jsxs)("div",{className:"chat-input-container",children:[(0,r.jsx)("textarea",{value:l,onChange:e=>p(e.target.value),onKeyPress:e=>{"Enter"!==e.key||e.shiftKey||(e.preventDefault(),d())},placeholder:"Ask me anything, or start a conversation...",rows:1,className:"chat-input"}),(0,r.jsx)("button",{onClick:d,disabled:!l.trim(),className:"send-button",children:(0,r.jsx)("span",{className:"send-icon",children:"🚀"})})]})]}),(0,r.jsxs)(motion.div,{className:"quick-actions",initial:{opacity:0,y:20},animate:{opacity:1,y:0},transition:{duration:.8,delay:.4,ease:"easeOut"},children:[(0,r.jsxs)("button",{onClick:()=>e("Hello! I'd like to have a conversation."),className:"action-button primary",children:[(0,r.jsx)("div",{className:"button-icon",children:"💬"}),(0,r.jsx)("span",{children:"Start Chat"})]}),(0,r.jsxs)("button",{onClick:t,className:"action-button secondary",children:[(0,r.jsx)("div",{className:"button-icon",children:"🔬"}),(0,r.jsx)("span",{children:"Deep Research"})]}),(0,r.jsxs)("button",{onClick:()=>e("Show me the document library"),className:"action-button tertiary",children:[(0,r.jsx)("div",{className:"button-icon",children:"📚"}),(0,r.jsx)("span",{children:"Document QA"})]})]})]}),(0,r.jsxs)("div",{className:"floating-elements",children:[(0,r.jsx)("div",{className:"floating-circle circle-1"}),(0,r.jsx)("div",{className:"floating-circle circle-2"}),(0,r.jsx)("div",{className:"floating-circle circle-3"})]})]}),(0,r.jsx)(motion.section,{className:"features-section",initial:{opacity:0},whileInView:{opacity:1},transition:{duration:.8},viewport:{once:!0},children:(0,r.jsxs)("div",{className:"features-content",children:[(0,r.jsx)(motion.h2,{className:"section-title",initial:{opacity:0,y:20},whileInView:{opacity:1,y:0},transition:{duration:.6,delay:.2},viewport:{once:!0},children:"Explore Features"}),(0,r.jsx)("div",{className:"features-grid",children:[{icon:"💬",title:"Intelligent Chat",description:"Have natural conversations with AI models. Ask questions, get explanations, and explore ideas."},{icon:"🔬",title:"Deep Research",description:"Conduct comprehensive research with multi-agent systems. Get detailed analysis and insights."},{icon:"📚",title:"Document Q&A",description:"Upload documents and ask questions about their content. Perfect for research papers and manuals."},{icon:"📊",title:"Agent Dashboard",description:"Monitor and manage your AI agents in real-time. See their progress and performance."},{icon:"⚙️",title:"Advanced Settings",description:"Customize your experience with theme preferences, model selection, and advanced options."}].map((e,t)=>(0,r.jsxs)(motion.div,{className:"feature-card",initial:{opacity:0,y:30},whileInView:{opacity:1,y:0},transition:{duration:.6,delay:.1*t,ease:"easeOut"},viewport:{once:!0},whileHover:{y:-8,transition:{duration:.2}},children:[(0,r.jsxs)("div",{className:"feature-icon-wrapper",children:[(0,r.jsx)("div",{className:"feature-icon",children:e.icon}),(0,r.jsx)("div",{className:"feature-glow"})]}),(0,r.jsx)("h3",{className:"feature-title",children:e.title}),(0,r.jsx)("p",{className:"feature-description",children:e.description}),(0,r.jsx)("div",{className:"feature-hover-effect"})]},t))})]})}),(0,r.jsx)(motion.section,{className:"tutorial-section",initial:{opacity:0},whileInView:{opacity:1},transition:{duration:.8},viewport:{once:!0},children:(0,r.jsxs)("div",{className:"tutorial-content",children:[(0,r.jsx)(motion.h2,{className:"section-title",initial:{opacity:0,y:20},whileInView:{opacity:1,y:0},transition:{duration:.6,delay:.2},viewport:{once:!0},children:"Getting Started"}),(0,r.jsx)("div",{className:"tutorial-steps",children:[{number:1,title:"Select Your Model",description:"Choose from various AI models in the sidebar. Each model has different strengths for different tasks.",icon:"🎯"},{number:2,title:"Start a Conversation",description:"Use the chat bar above or navigate to the Chat mode. Ask questions, get explanations, or explore ideas.",icon:"💬"},{number:3,title:"Try Deep Research",description:"For comprehensive analysis, use the Deep Research mode. It uses multiple AI agents to provide thorough insights.",icon:"🔬"},{number:4,title:"Upload Documents",description:"Upload PDFs, documents, or text files and ask questions about their content in the Documents mode.",icon:"📄"}].map((e,t)=>(0,r.jsxs)(motion.div,{className:"tutorial-step",initial:{opacity:0,x:t%2==0?-30:30},whileInView:{opacity:1,x:0},transition:{duration:.6,delay:.1*t,ease:"easeOut"},viewport:{once:!0},children:[(0,r.jsxs)("div",{className:"step-visual",children:[(0,r.jsx)("div",{className:"step-number",children:e.number}),(0,r.jsx)("div",{className:"step-icon",children:e.icon})]}),(0,r.jsxs)("div",{className:"step-content",children:[(0,r.jsx)("h3",{children:e.title}),(0,r.jsx)("p",{children:e.description})]}),(0,r.jsx)("div",{className:"step-connector"})]},t))})]})}),(0,r.jsx)("style",{children:`
        .home-page {
          min-height: 100vh;
          background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
          overflow-x: hidden;
        }

        .hero-section {
          padding: clamp(60px, 12vh, 100px) clamp(20px, 5vw, 24px);
          text-align: center;
          background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
          position: relative;
          overflow: hidden;
        }

        .hero-section::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background:
            radial-gradient(circle at 20% 80%, rgba(74, 144, 226, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(74, 144, 226, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(74, 144, 226, 0.05) 0%, transparent 50%);
        }

        .hero-content {
          max-width: 900px;
          margin: 0 auto;
          position: relative;
          z-index: 1;
        }

        .hero-header {
          margin-bottom: clamp(40px, 8vh, 60px);
        }

        .hero-title {
          font-size: clamp(2.5rem, 10vw, 4rem);
          font-weight: 800;
          margin: 0 0 clamp(16px, 3vh, 20px) 0;
          line-height: 1.1;
        }

        .hero-title-main {
          display: block;
          color: var(--text-primary);
          text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .hero-title-accent {
          display: block;
          background: linear-gradient(135deg, var(--accent), #4dabf7, #74c0fc);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          filter: drop-shadow(0 2px 8px rgba(74, 144, 226, 0.3));
        }

        .hero-subtitle {
          font-size: clamp(1.1rem, 4vw, 1.4rem);
          color: var(--text-secondary);
          margin: 0;
          line-height: 1.6;
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
          opacity: 0.9;
        }

        .chat-bar {
          background: var(--bg-primary);
          border-radius: clamp(20px, 5vw, 28px);
          padding: clamp(24px, 6vw, 32px);
          box-shadow: 0 16px 64px var(--shadow);
          border: 1px solid var(--border-color);
          margin: 0 auto clamp(32px, 6vh, 48px) auto;
          max-width: min(700px, 90vw);
          width: 100%;
          box-sizing: border-box;
          backdrop-filter: blur(20px);
          position: relative;
          overflow: hidden;
        }

        .chat-bar::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, var(--accent), #4dabf7, var(--accent));
          opacity: 0.6;
        }

        .model-indicator {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
          padding: 12px 16px;
          background: var(--bg-tertiary);
          border-radius: 12px;
          border: 1px solid var(--border-color);
        }

        .model-icon {
          font-size: 20px;
          opacity: 0.8;
        }

        .model-info {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 2px;
        }

        .model-label {
          font-size: 11px;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          font-weight: 600;
        }

        .model-name {
          font-size: 14px;
          font-weight: 600;
          color: var(--accent);
        }

        .chat-input-container {
          display: flex;
          gap: 16px;
          align-items: flex-end;
        }

        .chat-input {
          flex: 1;
          padding: clamp(16px, 4vw, 20px);
          border: 2px solid var(--border-color);
          border-radius: clamp(12px, 3vw, 16px);
          background: var(--bg-primary);
          color: var(--text-primary);
          font-size: clamp(16px, 3vw, 18px);
          font-family: inherit;
          resize: none;
          min-height: 24px;
          max-height: 120px;
          transition: all 0.2s ease;
          box-sizing: border-box;
          line-height: 1.5;
        }

        .chat-input:focus {
          outline: none;
          border-color: var(--accent);
          box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.1);
          background: var(--bg-secondary);
        }

        .chat-input::placeholder {
          color: var(--text-secondary);
          opacity: 0.7;
        }

        .send-button {
          width: clamp(56px, 14vw, 64px);
          height: clamp(56px, 14vw, 64px);
          background: linear-gradient(135deg, var(--accent), #4dabf7);
          color: white;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          font-size: clamp(18px, 4vw, 20px);
          transition: all 0.2s ease;
          flex-shrink: 0;
          box-shadow: 0 8px 24px rgba(0, 123, 255, 0.3);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .send-button:hover:not(:disabled) {
          transform: scale(1.1) translateY(-2px);
          box-shadow: 0 12px 32px rgba(0, 123, 255, 0.4);
        }

        .send-button:disabled {
          background: var(--text-secondary);
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .quick-actions {
          display: flex;
          gap: 20px;
          justify-content: center;
          flex-wrap: wrap;
        }

        .action-button {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 16px 24px;
          border-radius: 16px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          border: 2px solid transparent;
          position: relative;
          overflow: hidden;
          min-width: 160px;
          justify-content: center;
        }

        .action-button::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transition: left 0.5s;
        }

        .action-button:hover::before {
          left: 100%;
        }

        .action-button.primary {
          background: linear-gradient(135deg, var(--accent), #4dabf7);
          color: white;
          box-shadow: 0 8px 24px rgba(0, 123, 255, 0.3);
        }

        .action-button.primary:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 32px rgba(0, 123, 255, 0.4);
        }

        .action-button.secondary {
          background: transparent;
          color: var(--accent);
          border-color: var(--accent);
        }

        .action-button.secondary:hover {
          background: var(--accent);
          color: white;
          transform: translateY(-4px);
        }

        .action-button.tertiary {
          background: transparent;
          color: var(--text-primary);
          border-color: var(--border-color);
        }

        .action-button.tertiary:hover {
          background: var(--bg-secondary);
          border-color: var(--accent);
          transform: translateY(-4px);
        }

        .button-icon {
          font-size: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .floating-elements {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          overflow: hidden;
        }

        .floating-circle {
          position: absolute;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(74, 144, 226, 0.1) 0%, transparent 70%);
          animation: float 6s ease-in-out infinite;
        }

        .circle-1 {
          width: 80px;
          height: 80px;
          top: 10%;
          left: 10%;
          animation-delay: 0s;
        }

        .circle-2 {
          width: 60px;
          height: 60px;
          top: 60%;
          right: 15%;
          animation-delay: 2s;
        }

        .circle-3 {
          width: 100px;
          height: 100px;
          bottom: 20%;
          left: 70%;
          animation-delay: 4s;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }

        .features-section,
        .tutorial-section {
          padding: clamp(60px, 12vh, 100px) clamp(20px, 5vw, 24px);
          background: var(--bg-primary);
          position: relative;
        }

        .features-content,
        .tutorial-content {
          max-width: min(1400px, 95vw);
          margin: 0 auto;
        }

        .section-title {
          font-size: clamp(2.2rem, 8vw, 3.5rem);
          font-weight: 800;
          color: var(--text-primary);
          text-align: center;
          margin: 0 0 clamp(40px, 8vh, 80px) 0;
          background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(clamp(280px, 25vw, 320px), 1fr));
          gap: clamp(24px, 5vw, 40px);
        }

        .feature-card {
          background: var(--bg-secondary);
          border-radius: clamp(16px, 4vw, 20px);
          padding: clamp(24px, 6vw, 40px);
          text-align: center;
          transition: all 0.4s ease;
          border: 1px solid var(--border-color);
          position: relative;
          overflow: hidden;
          box-shadow: 0 8px 32px var(--shadow);
        }

        .feature-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, var(--accent), #4dabf7);
          transform: scaleX(0);
          transition: transform 0.3s ease;
        }

        .feature-card:hover::before {
          transform: scaleX(1);
        }

        .feature-card:hover {
          transform: translateY(-12px) scale(1.02);
          box-shadow: 0 20px 64px var(--shadow);
        }

        .feature-icon-wrapper {
          position: relative;
          display: inline-block;
          margin-bottom: clamp(20px, 5vh, 28px);
        }

        .feature-icon {
          font-size: clamp(3rem, 10vw, 4rem);
          position: relative;
          z-index: 1;
          transition: all 0.3s ease;
        }

        .feature-glow {
          position: absolute;
          top: -10px;
          left: -10px;
          right: -10px;
          bottom: -10px;
          background: radial-gradient(circle, rgba(74, 144, 226, 0.2) 0%, transparent 70%);
          border-radius: 50%;
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .feature-card:hover .feature-glow {
          opacity: 1;
        }

        .feature-card:hover .feature-icon {
          transform: scale(1.1);
        }

        .feature-title {
          font-size: clamp(1.3rem, 4vw, 1.5rem);
          font-weight: 700;
          color: var(--text-primary);
          margin: 0 0 clamp(12px, 3vh, 16px) 0;
        }

        .feature-description {
          color: var(--text-secondary);
          line-height: 1.6;
          margin: 0;
          font-size: clamp(0.95rem, 2.5vw, 1.1rem);
        }

        .feature-hover-effect {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(74, 144, 226, 0.05), rgba(116, 192, 252, 0.05));
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .feature-card:hover .feature-hover-effect {
          opacity: 1;
        }

        .tutorial-steps {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(clamp(280px, 30vw, 320px), 1fr));
          gap: clamp(24px, 5vw, 40px);
          max-width: min(1200px, 95vw);
          margin: 0 auto;
        }

        .tutorial-step {
          display: flex;
          gap: clamp(20px, 4vw, 24px);
          align-items: flex-start;
          background: var(--bg-secondary);
          border-radius: clamp(16px, 4vw, 20px);
          padding: clamp(24px, 6vw, 32px);
          border: 1px solid var(--border-color);
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .tutorial-step::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 4px;
          height: 100%;
          background: linear-gradient(180deg, var(--accent), #4dabf7);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .tutorial-step:hover::before {
          opacity: 1;
        }

        .tutorial-step:hover {
          transform: translateX(8px);
          box-shadow: 0 12px 32px var(--shadow);
        }

        .step-visual {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          flex-shrink: 0;
        }

        .step-number {
          width: clamp(50px, 10vw, 60px);
          height: clamp(50px, 10vw, 60px);
          border-radius: 50%;
          background: linear-gradient(135deg, var(--accent), #4dabf7);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: clamp(18px, 4vw, 22px);
          font-weight: 700;
          box-shadow: 0 8px 24px rgba(0, 123, 255, 0.3);
          position: relative;
        }

        .step-number::before {
          content: '';
          position: absolute;
          top: -2px;
          left: -2px;
          right: -2px;
          bottom: -2px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--accent), #4dabf7);
          opacity: 0.3;
          z-index: -1;
        }

        .step-icon {
          font-size: clamp(24px, 6vw, 28px);
          opacity: 0.8;
        }

        .step-content h3 {
          margin: 0 0 clamp(8px, 2vh, 12px) 0;
          color: var(--text-primary);
          font-size: clamp(1.2rem, 4vw, 1.4rem);
          font-weight: 600;
        }

        .step-content p {
          margin: 0;
          color: var(--text-secondary);
          line-height: 1.6;
          font-size: clamp(0.95rem, 2.5vw, 1.05rem);
        }

        .step-connector {
          position: absolute;
          right: -12px;
          top: 50%;
          width: 24px;
          height: 2px;
          background: var(--border-color);
          opacity: 0.5;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .hero-section {
            padding: 50px 20px;
          }

          .hero-title {
            font-size: 2.5rem;
          }

          .hero-subtitle {
            font-size: 1.1rem;
          }

          .chat-bar {
            padding: 24px;
            margin-bottom: 32px;
          }

          .quick-actions {
            flex-direction: column;
            align-items: center;
            gap: 16px;
          }

          .action-button {
            width: 100%;
            max-width: 280px;
            padding: 18px 24px;
          }

          .features-section,
          .tutorial-section {
            padding: 50px 20px;
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: 24px;
          }

          .tutorial-steps {
            grid-template-columns: 1fr;
            gap: 20px;
          }

          .tutorial-step {
            flex-direction: column;
            text-align: center;
            gap: 16px;
          }

          .step-visual {
            flex-direction: row;
            gap: 16px;
          }

          .step-connector {
            display: none;
          }
        }

        @media (max-width: 480px) {
          .hero-section {
            padding: 40px 16px;
          }

          .chat-bar {
            padding: 20px;
            margin-bottom: 24px;
          }

          .model-indicator {
            padding: 10px 12px;
            margin-bottom: 16px;
          }

          .quick-actions {
            gap: 12px;
          }

          .action-button {
            padding: 16px 20px;
            font-size: 15px;
          }

          .features-section,
          .tutorial-section {
            padding: 40px 16px;
          }

          .floating-circle {
            display: none;
          }
        }
      `})]})}}),a("kqWnA",function(a,i){e(a.exports,"default",()=>s);var r,o=t("ayMG0");let n=((r=t("acw62"))&&r.__esModule?r.default:r).memo(({content:e,isEditable:t=!1,onChange:a,placeholder:i="Type your message..."})=>{if(!t){let t=e?e.replace(/```([\s\S]*?)```/g,"<pre><code>$1</code></pre>").replace(/^### (.*$)/gim,"<h3>$1</h3>").replace(/^## (.*$)/gim,"<h2>$1</h2>").replace(/^# (.*$)/gim,"<h1>$1</h1>").replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>").replace(/\*(.*?)\*/g,"<em>$1</em>").replace(/`([^`]+)`/g,"<code>$1</code>").replace(/^\* (.*$)/gim,"<li>$1</li>").replace(/^\d+\. (.*$)/gim,"<li>$1</li>").replace(/\n\n/g,"</p><p>").replace(/\n/g,"<br>").replace(/^---$/gm,"<hr>").replace(/^([^<].*?)(<|$)/gm,"<p>$1</p>$2"):"";return(0,o.jsx)("div",{className:"rich-text-display",dangerouslySetInnerHTML:{__html:t}})}return(0,o.jsx)("textarea",{value:e,onChange:e=>a(e.target.value),placeholder:i,className:"rich-text-editor",rows:4})});n.displayName="RichTextMessage";var s=n});
//# sourceMappingURL=HomePage.4ff462e9.js.map
