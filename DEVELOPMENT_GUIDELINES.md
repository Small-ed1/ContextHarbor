# Router Phase 1 Development Guidelines

## Core Development Workflow

### 1. Change Management
- **Server Restart**: After EVERY change (frontend, backend, or configuration), restart all servers using `./restart_servers.sh all`
- **Backend-Frontend Sync**: Every backend change MUST have an accompanying frontend change to maintain feature parity
- **Testing**: Run full test suite after EVERY change using `npm test` (frontend) and `python -m pytest` (backend)
- **Error Hunting**: Perform thorough error checking and debugging after each change

### 2. Quality Assurance
- **Code Standards**: Follow existing conventions (mypy, black, eslint)
- **Performance**: Monitor RAM usage (current limit: 15.3 GiB) and optimize as needed
- **Security**: Audit tool permissions and sandboxing after changes

### 3. Version Control
- **Commits**: After each MAJOR change deemed successful by user testing:
  - Create descriptive commit message
  - Push to remote repository
  - Tag major releases
- **Branching**: Use feature branches for development, merge to main after testing

### 4. Deployment
- **Dual Deployment**: Support both PyInstaller executable and pip installation
- **Auto-Updates**: Implement automatic update checking for tools and algorithms
- **Backup**: Maintain local SQLite backups with WAL mode

### 5. Monitoring & Limits
- **Resource Awareness**: Respect current 15.3 GiB RAM limit with adaptive compression
- **Progress Tracking**: All operations must show current status, completion, and controls
- **Time Limits**: Configurable research time limits (5min - 30 days) with soft controls

### 6. Integration Requirements
- **Primary**: Ollama and Kiwix integration with auto-detection
- **Extensible**: Tool architecture for additional integrations
- **Local-First**: All storage and processing remains local

### 7. User Experience
- **Web UI Primary**: Full-featured interface for all operations
- **CLI Secondary**: Rich TUI with feature parity (no animations)
- **Authentication**: Username/password with encrypted token bypass

### 8. Research Engine
- **Multi-Agent**: Overseeing agent controls time allocation and processes
- **Iterative Pipeline**: Query decomposition → execution → synthesis
- **RAG Maintenance**: Weekly automated content analysis and trimming

## Emergency Procedures
- **Rollback**: Use git to revert problematic changes
- **Resource Limits**: Automatic shutdown at 15.5 GiB RAM usage
- **Data Recovery**: SQLite WAL for transaction safety

## Testing Checklist
- [ ] All servers restart successfully
- [ ] Frontend/backend synchronization verified
- [ ] Full test suite passes
- [ ] Error logs clean
- [ ] RAM usage within limits
- [ ] Authentication works
- [ ] Tool permissions functional
- [ ] Research engine operational

# Detailed Implementation Plan Layout

## Phase 1: Infrastructure Foundation (Weeks 1-2)
**Goal:** Establish core systems and storage.

### Week 1: Database & Authentication
**Tasks:**
1. SQLite Schema Implementation
   - Create migration scripts for all tables
   - Implement FTS5 for text search
   - Set up vector storage for embeddings
   - Enable WAL mode for concurrency
2. User Management System
   - Implement bcrypt password hashing
   - Create JWT token system
   - Add encrypted bypass tokens
   - Build user profile storage
3. Auto-Configuration Framework
   - Ollama model detection (/api/tags)
   - Hardware profiling (RAM, CPU)
   - First-run setup wizard
   - Configuration validation

**Deliverables:**
- Functional SQLite database with migrations
- User authentication endpoints
- Auto-config script
- Basic CLI skeleton

**Testing:**
- Database CRUD operations
- Authentication flow
- Configuration persistence
- CLI basic commands

### Week 2: RAG & Storage Integration
**Tasks:**
1. Embedding Service Setup
   - Integrate sentence-transformers or Ollama embeddings
   - Implement vector storage in SQLite BLOBs
   - Create similarity search functions
   - Set up FTS5 fallback
2. Knowledge Management
   - Content chunking and storage
   - Metadata tracking (sources, timestamps)
   - Weekly maintenance job skeleton
   - Import/export functionality
3. File System Integration
   - Local storage structure
   - Backup procedures
   - Migration from existing JSON

**Deliverables:**
- RAG retrieval system
- Knowledge base API endpoints
- Backup/restore functionality
- Migration scripts

**Testing:**
- Embedding generation and storage
- Similarity search accuracy
- Knowledge import/export
- Backup integrity

## Phase 2: Web UI Enhancement (Weeks 3-5)
**Goal:** Complete chat and research interface.

### Week 3: Chat Management Interface
**Tasks:**
1. Chat CRUD Operations
   - Create/delete/rename/archive functions
   - Drag-and-drop reordering
   - Bulk operations (export/import)
2. Message Management
   - Real-time message sync
   - Token counting and limits
   - Message threading
3. Search & Filtering
   - Full-text search across chats
   - Date/content filters
   - Summary generation

**Deliverables:**
- Complete chat sidebar
- Message persistence
- Search functionality

**Testing:**
- Chat operations (CRUD)
- Message sync
- Search accuracy

### Week 4: Research Dashboard
**Tasks:**
1. Progress Visualization
   - Real-time progress bars
   - Time allocation display
   - Agent status monitoring
2. Research Controls
   - Start/pause/resume controls
   - Parameter adjustment
   - Result preview
3. Agent Management
   - Agent status dashboard
   - Manual intervention options
   - Resource monitoring

**Deliverables:**
- Research progress UI
- Agent monitoring panels
- Control interfaces

**Testing:**
- Research session lifecycle
- Progress accuracy
- Agent communication

### Week 5: Settings & RAG Interface
**Tasks:**
1. Settings Panel
   - Time limit configuration
   - Model preferences
   - Tool permissions matrix
2. RAG Management
   - Knowledge browser
   - Content addition interface
   - Maintenance controls
3. Integration Testing
   - End-to-end workflows
   - Performance monitoring

**Deliverables:**
- Complete settings UI
- RAG management interface
- Integration test suite

**Testing:**
- Settings persistence
- RAG operations
- Full workflow testing

## Phase 3: CLI Synchronization (Weeks 6-7)
**Goal:** Feature-complete CLI interface.

### Week 6: Core CLI Commands
**Tasks:**
1. Authentication CLI
   - Login/logout commands
   - Token management
   - Session handling
2. Chat CLI
   - Interactive chat mode
   - Chat management commands
   - Message history
3. Basic Tool Commands
   - Tool listing and status
   - Permission management
   - Execution with prompts

**Deliverables:**
- CLI authentication
- Chat interface
- Tool management commands

**Testing:**
- CLI login flow
- Chat operations
- Tool execution

### Week 7: Advanced CLI Features
**Tasks:**
1. Research CLI
   - Research session management
   - Progress monitoring
   - Result handling
2. RAG CLI
   - Knowledge management commands
   - Search and retrieval
   - Maintenance triggers
3. Rich Interface
   - Progress bars and spinners
   - Syntax highlighting
   - Interactive prompts

**Deliverables:**
- Research CLI commands
- RAG CLI interface
- Rich TUI components

**Testing:**
- Research workflows
- RAG operations
- CLI performance

## Phase 4: Research Engine (Weeks 8-10)
**Goal:** Time-aware multi-agent system.

### Week 8: Overseer Agent
**Tasks:**
1. Time Management
   - Dynamic allocation logic
   - Soft limit enforcement
   - Resource monitoring
2. Process Control
   - Agent lifecycle management
   - Priority scheduling
   - Quality assessment

**Deliverables:**
- Time allocation system
- Agent control framework

**Testing:**
- Time management logic
- Agent coordination

### Week 9: Research Pipeline
**Tasks:**
1. Query Decomposition
   - Iterative breakdown logic
   - Sub-task generation
   - Dependency management
2. Multi-Agent Execution
   - Parallel processing
   - Result aggregation
   - Error handling

**Deliverables:**
- Decomposition engine
- Execution framework

**Testing:**
- Pipeline execution
- Result quality
- Error recovery

### Week 10: Synthesis & Persistence
**Tasks:**
1. Result Synthesis
   - Citation integration
   - Content consolidation
   - Final output generation
2. Session Persistence
   - State serialization
   - Resume capability
   - Result caching

**Deliverables:**
- Synthesis engine
- Persistence layer

**Testing:**
- Synthesis accuracy
- Session recovery
- Performance benchmarks

## Phase 5: Tool Ecosystem (Weeks 11-12)
**Goal:** Complete tool suite with permissions.

### Week 11: Core Tools
**Tasks:**
1. System Tools
   - Terminal access with sandboxing
   - File operations with restrictions
   - Process monitoring
2. Web Tools
   - Search integration
   - Content scraping
   - API access

**Deliverables:**
- System tool implementations
- Web tool suite

**Testing:**
- Tool execution safety
- Permission enforcement
- Performance impact

### Week 12: Advanced Tools & Permissions
**Tasks:**
1. AI Tools
   - Model management
   - Embedding generation
   - Analysis utilities
2. Knowledge Tools
   - Kiwix integration
   - RAG retrieval
   - Document processing
3. Permission Framework
   - Hierarchical permissions
   - Audit logging
   - Dynamic prompts

**Deliverables:**
- AI and knowledge tools
- Complete permission system

**Testing:**
- Tool integration
- Permission accuracy
- Audit functionality

## Phase 6: Automation & Production (Weeks 13-14)
**Goal:** Production-ready system.

### Week 13: Automation Features
**Tasks:**
1. Update Management
   - Automatic tool updates
   - Algorithm versioning
   - Dependency management
2. Maintenance Automation
   - Weekly RAG analysis
   - Database optimization
   - Health monitoring

**Deliverables:**
- Update system
- Maintenance scheduler

**Testing:**
- Update reliability
- Maintenance effectiveness

### Week 14: Final Polish & Deployment
**Tasks:**
1. Packaging
   - PyInstaller executable
   - Pip package structure
   - Installation scripts
2. Documentation
   - User guides
   - API documentation
   - Troubleshooting
3. Final Testing
   - End-to-end validation
   - Performance optimization
   - Security audit

**Deliverables:**
- Deployment packages
- Complete documentation
- Production-ready system

**Testing:**
- Installation verification
- Full system testing
- Performance validation

## Risk Assessment & Mitigation

### High-Risk Areas
1. RAM Limitations: Current 15.3 GiB constraint requires careful memory management
2. Multi-Agent Complexity: Research orchestration needs robust error handling
3. Dual Interface Sync: Web/CLI consistency requires careful state management

### Mitigation Strategies
1. Memory Management: Implement aggressive compression and monitoring
2. Testing: Comprehensive integration tests for all workflows
3. Monitoring: Real-time resource tracking with automatic adjustments

## Success Metrics

### Technical Metrics
- Performance: Research completion within allocated time ±10%
- Reliability: 99% uptime with graceful error recovery
- Security: Zero permission bypasses, clean audit logs

### User Experience Metrics
- Usability: Web UI tasks completed in <5 clicks, CLI commands <3 keystrokes
- Response Time: Chat responses <2 seconds, research progress updates <5 seconds
- Accuracy: RAG retrieval precision >85%, research quality scores >8/10

## Final Questions
1. Timeline: Is the 14-week timeline acceptable, or should we prioritize certain phases?
2. Scope: Are there any features from the plan you'd like to deprioritize or add?
3. Resources: Any specific tools, libraries, or external dependencies we should prepare for?
4. Validation: What user testing scenarios are most critical for the first implementation?
5. Maintenance: How should we handle ongoing development after initial release?

This detailed plan provides a complete roadmap for building the dual-interface AI assistant. The guidelines file ensures consistent development practices, while the phased approach allows for iterative validation and risk management. Ready to begin implementation once you approve the plan and answer any final questions.