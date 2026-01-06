"""
Research Orchestration System
Coordinates adaptive research strategies with multi-agent coordination and iterative refinement.
"""

import asyncio
import json
import logging
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

try:
    from ...utils.context_manager import ContextManager, ContextWindowStrategy
    from ...utils.memory_manager import (MemoryAction, MemoryAwareMixin,
                                          MemoryManager)
    from .multi_agent_system import AgentRole, MultiAgentSystem
    from .iterative_research import IterativeResearchTool
    from .web_scraper import WebScraper, ScrapingConfig
    from ..ollama_client import OllamaClient, OllamaConfig
except ImportError:
    # Fallback for when imports fail
    ContextManager = None
    ContextWindowStrategy = None
    MemoryManager = None  # type: ignore
    MemoryAwareMixin = None  # type: ignore
    MultiAgentSystem = None  # type: ignore
    AgentRole = None  # type: ignore
    IterativeResearchTool = None  # type: ignore
    WebScraper = None  # type: ignore
    ScrapingConfig = None  # type: ignore
    OllamaClient = None  # type: ignore
    OllamaConfig = None  # type: ignore


class ResearchStrategy(Enum):
    """Research strategy types."""

    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    HYBRID = "hybrid"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    EXPLORATORY = "exploratory"


class ResearchPhase(Enum):
    """Phases of the research process."""

    PLANNING = "planning"
    INITIAL_RESEARCH = "initial_research"
    DEEP_DIVE = "deep_dive"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    ITERATION = "iteration"
    COMPLETION = "completion"


class ResearchPriority(Enum):
    """Priority levels for research topics."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ResearchTopic:
    """A research topic with metadata."""

    id: str
    title: str
    description: str
    priority: ResearchPriority = ResearchPriority.MEDIUM
    depth_level: int = 1
    parent_topic: Optional[str] = None
    subtopics: List[str] = field(default_factory=list)
    status: str = "pending"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    estimated_complexity: int = 1  # 1-10 scale


@dataclass
class ResearchPlan:
    """A research plan with strategy and topics."""

    id: str
    title: str
    strategy: ResearchStrategy
    topics: Dict[str, ResearchTopic] = field(default_factory=dict)
    current_phase: ResearchPhase = ResearchPhase.PLANNING
    max_depth: int = 3
    breadth_limit: int = 5
    iteration_limit: int = 3
    time_budget_hours: Optional[float] = None
    quality_threshold: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ResearchProgress:
    """Tracks research progress and metrics."""

    total_topics: int = 0
    completed_topics: int = 0
    active_topics: int = 0
    findings_count: int = 0
    sources_count: int = 0
    average_confidence: float = 0.0
    time_spent_hours: float = 0.0
    current_depth: int = 1
    strategy_adaptations: int = 0
    quality_score: float = 0.0


class ResearchOrchestrator:
    """
    Orchestrates adaptive research strategies using multi-agent coordination.
    Supports breadth-first, depth-first, and hybrid approaches with iterative refinement.
    """

    def __init__(self, multi_agent_system, context_manager, memory_manager):
        self.multi_agent_system = multi_agent_system
        self.context_manager = context_manager
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)

        # Initialize iterative research tool for real research
        self.iterative_research_tool = None
        if memory_manager:
            try:
                ollama_config = OllamaConfig()  # type: ignore
                ollama_client = OllamaClient(ollama_config)  # type: ignore
                scraping_config = ScrapingConfig()  # type: ignore
                web_scraper = WebScraper(scraping_config, memory_manager)  # type: ignore
                self.iterative_research_tool = IterativeResearchTool(  # type: ignore
                    ollama_client, web_scraper, memory_manager
                )
                self.logger.info("IterativeResearchTool initialized for real research")
            except Exception as e:
                self.logger.warning(f"Failed to initialize IterativeResearchTool: {e}")
                self.iterative_research_tool = None

        # Research state
        self.active_plans: Dict[str, ResearchPlan] = {}
        self.research_progress: Dict[str, ResearchProgress] = {}

        # Strategy configurations
        self.strategy_configs = {
            ResearchStrategy.BREADTH_FIRST: {
                "max_concurrent_topics": 5,
                "depth_increment": 1,
                "quality_threshold": 0.6,
                "exploration_bias": 0.8,
            },
            ResearchStrategy.DEPTH_FIRST: {
                "max_concurrent_topics": 2,
                "depth_increment": 2,
                "quality_threshold": 0.8,
                "exploration_bias": 0.3,
            },
            ResearchStrategy.HYBRID: {
                "max_concurrent_topics": 3,
                "depth_increment": 1,
                "quality_threshold": 0.7,
                "exploration_bias": 0.5,
            },
            ResearchStrategy.ITERATIVE_REFINEMENT: {
                "max_concurrent_topics": 2,
                "depth_increment": 1,
                "quality_threshold": 0.9,
                "exploration_bias": 0.2,
            },
            ResearchStrategy.EXPLORATORY: {
                "max_concurrent_topics": 4,
                "depth_increment": 1,
                "quality_threshold": 0.5,
                "exploration_bias": 0.9,
            },
        }

        # Performance tracking
        self.orchestration_metrics = {
            "total_plans_executed": 0,
            "average_completion_time": 0.0,
            "strategy_success_rates": {},
            "topic_discovery_rate": 0.0,
        }

    async def create_research_plan(
        self,
        title: str,
        description: str,
        strategy: ResearchStrategy = ResearchStrategy.HYBRID,
        initial_topics: Optional[List[str]] = None,
        time_budget_hours: Optional[float] = None,
    ) -> str:
        """Create a new research plan."""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = ResearchPlan(
            id=plan_id,
            title=title,
            strategy=strategy,
            time_budget_hours=time_budget_hours,
        )

        # Create initial topics
        if initial_topics:
            for topic_title in initial_topics:
                topic_id = f"topic_{len(plan.topics) + 1}"
                topic = ResearchTopic(
                    id=topic_id,
                    title=topic_title,
                    description=f"Research topic: {topic_title}",
                    priority=ResearchPriority.HIGH,
                )
                plan.topics[topic_id] = topic

        # Create context session for this research (skip if context_manager is None)
        if self.context_manager:
            session_id = await self.context_manager.create_session(
                title=f"Research: {title}",
                description=description,
                metadata={"plan_id": plan_id, "strategy": strategy.value},
            )

        self.active_plans[plan_id] = plan
        self.research_progress[plan_id] = ResearchProgress()

        self.logger.info(
            f"Created research plan: {plan_id} - {title} ({strategy.value})"
        )
        return plan_id

    async def create_section_based_research_plan(
        self,
        title: str,
        description: str,
        sections: List[Dict[str, Any]],
        time_budget_hours: Optional[float] = None,
    ) -> str:
        """Create a research plan with predefined sections determined at start."""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = ResearchPlan(
            id=plan_id,
            title=title,
            strategy=ResearchStrategy.HYBRID,  # Best for section-based research
            time_budget_hours=time_budget_hours,
        )

        # Create topics from sections
        for i, section in enumerate(sections):
            topic_id = f"section_{i+1}"
            topic = ResearchTopic(
                id=topic_id,
                title=section["title"],
                description=section["description"],
                priority=ResearchPriority.HIGH,
                depth_level=1,
                estimated_complexity=section.get("estimated_days", 1)
                * 2,  # Convert days to complexity
            )
            plan.topics[topic_id] = topic

            # Add subsections as subtopics
            for j, subsection in enumerate(section.get("subsections", [])):
                subtopic_id = f"subsection_{i+1}_{j+1}"
                subtopic = ResearchTopic(
                    id=subtopic_id,
                    title=subsection,
                    description=f"Subsection of {section['title']}: {subsection}",
                    priority=ResearchPriority.MEDIUM,
                    depth_level=2,
                    parent_topic=topic_id,
                    estimated_complexity=1,
                )
                plan.topics[subtopic_id] = subtopic
                topic.subtopics.append(subtopic_id)

        # Create context session for this research (skip if context_manager is None)
        if self.context_manager:
            session_id = await self.context_manager.create_session(
                title=f"Section-based Research: {title}",
                description=f"{description} - {len(sections)} sections defined at start",
                metadata={
                    "plan_id": plan_id,
                    "strategy": "section_based",
                    "sections_count": len(sections),
                },
            )

        self.active_plans[plan_id] = plan
        self.research_progress[plan_id] = ResearchProgress()

        self.logger.info(
            f"Created section-based research plan: {plan_id} - {title} ({len(sections)} sections)"
        )
        return plan_id

    async def execute_research_plan(self, plan_id: str) -> bool:
        """Execute a research plan using adaptive strategies."""
        if plan_id not in self.active_plans:
            raise ValueError(f"Research plan {plan_id} not found")

        plan = self.active_plans[plan_id]
        progress = self.research_progress[plan_id]

        plan.started_at = datetime.now()
        plan.current_phase = ResearchPhase.INITIAL_RESEARCH

        self.logger.info(f"Starting research plan: {plan_id}")

        try:
            # Phase 1: Initial research breadth
            await self._execute_initial_research(plan, progress)

            # Phase 2: Deep dive based on strategy
            await self._execute_deep_dive(plan, progress)

            # Phase 3: Synthesis and validation
            await self._execute_synthesis_and_validation(plan, progress)

            # Phase 4: Iterative refinement if needed
            await self._execute_iterative_refinement(plan, progress)

            plan.current_phase = ResearchPhase.COMPLETION
            plan.completed_at = datetime.now()

            # Update metrics
            self._update_orchestration_metrics(plan, progress)

            self.logger.info(f"Completed research plan: {plan_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error executing research plan {plan_id}: {e}")
            plan.current_phase = ResearchPhase.VALIDATION  # Mark as failed but complete
            return False

    async def _execute_initial_research(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute initial breadth-first research phase."""
        self.logger.info(f"Starting initial research phase for plan {plan.id}")

        # Get high-priority topics
        initial_topics = [
            t for t in plan.topics.values() if t.priority == ResearchPriority.HIGH
        ]

        # Execute parallel research tasks
        config = self.strategy_configs[plan.strategy]
        max_concurrent = config["max_concurrent_topics"]

        # Process topics in batches
        for i in range(0, len(initial_topics), max_concurrent):
            batch = initial_topics[i : i + max_concurrent]
            await self._research_topic_batch(plan, batch, depth=1, progress=progress)

        plan.current_phase = ResearchPhase.DEEP_DIVE

    async def _execute_deep_dive(self, plan: ResearchPlan, progress: ResearchProgress):
        """Execute deep dive phase based on research strategy."""
        self.logger.info(f"Starting deep dive phase for plan {plan.id}")

        config = self.strategy_configs[plan.strategy]

        if plan.strategy == ResearchStrategy.BREADTH_FIRST:
            await self._execute_breadth_first_dive(plan, progress)
        elif plan.strategy == ResearchStrategy.DEPTH_FIRST:
            await self._execute_depth_first_dive(plan, progress)
        elif plan.strategy == ResearchStrategy.HYBRID:
            await self._execute_hybrid_dive(plan, progress)
        elif plan.strategy == ResearchStrategy.EXPLORATORY:
            await self._execute_exploratory_dive(plan, progress)
        else:  # ITERATIVE_REFINEMENT
            await self._execute_iterative_dive(plan, progress)

    async def _execute_breadth_first_dive(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute breadth-first research strategy."""
        current_depth = 2
        max_depth = plan.max_depth

        while current_depth <= max_depth:
            # Get topics at current depth level
            depth_topics = [
                t for t in plan.topics.values() if t.depth_level == current_depth - 1
            ]

            if not depth_topics:
                break

            # Generate subtopics for each topic
            new_topics = []
            for topic in depth_topics:
                if topic.confidence_score >= 0.6:  # Only expand high-confidence topics
                    subtopics = await self._generate_subtopics(topic, plan)
                    new_topics.extend(subtopics)

            # Research new topics
            if new_topics:
                await self._research_topic_batch(
                    plan, new_topics, depth=current_depth, progress=progress
                )

            current_depth += 1
            progress.current_depth = current_depth

    async def _execute_depth_first_dive(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute depth-first research strategy."""
        # Find highest priority topic
        topics_by_priority = sorted(
            plan.topics.values(),
            key=lambda x: (x.priority.value, x.confidence_score),
            reverse=True,
        )

        for topic in topics_by_priority[:3]:  # Focus on top 3 topics
            await self._deep_research_topic(topic, plan, progress)

    async def _execute_hybrid_dive(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute hybrid research strategy."""
        # Combine breadth and depth approaches
        await self._execute_breadth_first_dive(plan, progress)

        # Then do deep dives on most promising topics
        promising_topics = sorted(
            plan.topics.values(), key=lambda x: x.confidence_score, reverse=True
        )[:2]

        for topic in promising_topics:
            await self._deep_research_topic(topic, plan, progress)

    async def _execute_exploratory_dive(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute exploratory research strategy."""
        # Generate many subtopics and research broadly
        all_topics = list(plan.topics.values())

        for topic in all_topics:
            if (
                len(plan.topics) < plan.breadth_limit * 2
            ):  # Don't exceed breadth limit too much
                subtopics = await self._generate_subtopics(topic, plan)
                # Research subtopics immediately
                await self._research_topic_batch(
                    plan, subtopics, depth=topic.depth_level + 1, progress=progress
                )

    async def _execute_iterative_dive(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute iterative refinement strategy."""
        iteration = 0
        max_iterations = plan.iteration_limit

        while iteration < max_iterations:
            # Identify knowledge gaps
            gaps = await self._identify_knowledge_gaps(plan)

            if not gaps:
                break

            # Research gaps
            gap_topics = []
            for gap in gaps[:3]:  # Focus on top 3 gaps
                topic = ResearchTopic(
                    id=f"iter_{iteration}_{len(plan.topics)}",
                    title=gap["title"],
                    description=gap["description"],
                    priority=ResearchPriority.HIGH,
                    depth_level=iteration + 2,
                )
                plan.topics[topic.id] = topic
                gap_topics.append(topic)

            await self._research_topic_batch(
                plan, gap_topics, depth=iteration + 2, progress=progress
            )
            iteration += 1

    async def _execute_synthesis_and_validation(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute synthesis and validation phase."""
        plan.current_phase = ResearchPhase.SYNTHESIS

        # Synthesize findings
        synthesis_task = await self.multi_agent_system.submit_task(
            task_type="synthesis",
            description=f"Synthesize findings from research plan: {plan.title}",
            data={
                "plan_id": plan.id,
                "topics": [t.__dict__ for t in plan.topics.values()],
                "strategy": plan.strategy.value,
            },
        )

        # Wait for synthesis
        await asyncio.sleep(5)  # Allow time for processing

        # Validation
        plan.current_phase = ResearchPhase.VALIDATION
        validation_task = await self.multi_agent_system.submit_task(
            task_type="validation",
            description=f"Validate research findings for plan: {plan.title}",
            data={
                "plan_id": plan.id,
                "findings": [t.findings for t in plan.topics.values()],
                "sources": [t.sources for t in plan.topics.values()],
            },
        )

    async def _execute_iterative_refinement(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Execute iterative refinement if quality threshold not met."""
        if progress.quality_score >= plan.quality_threshold:
            return

        plan.current_phase = ResearchPhase.ITERATION

        # Identify areas needing refinement
        refinement_areas = await self._identify_refinement_areas(plan)

        if refinement_areas:
            refinement_topics = []
            for area in refinement_areas[:2]:  # Limit refinement scope
                topic = ResearchTopic(
                    id=f"refine_{len(plan.topics)}",
                    title=f"Refinement: {area['title']}",
                    description=area["description"],
                    priority=ResearchPriority.HIGH,
                )
                plan.topics[topic.id] = topic
                refinement_topics.append(topic)

            await self._research_topic_batch(
                plan, refinement_topics, depth=plan.max_depth, progress=progress
            )

    async def _research_topic_batch(
        self,
        plan: ResearchPlan,
        topics: List[ResearchTopic],
        depth: int,
        progress: ResearchProgress,
    ):
        """Research a batch of topics in parallel."""
        tasks = []

        for topic in topics:
            topic.status = "researching"
            task = self.multi_agent_system.submit_task(
                task_type="research",
                description=f"Research topic: {topic.title} (depth {depth})",
                data={
                    "topic": topic.__dict__,
                    "plan_id": plan.id,
                    "depth": depth,
                    "strategy": plan.strategy.value,
                },
            )
            tasks.append((topic, task))

        # Wait for all tasks in batch to complete
        for topic, task_future in tasks:
            try:
                if self.iterative_research_tool:
                    # Use real research with IterativeResearchTool
                    self.logger.info(f"Starting real research on topic: {topic.title}")
                    research_result = await self.iterative_research_tool.research_topic(
                        query=topic.title,
                        model="llama3.2:3b",
                        max_iterations=2,
                        search_limit=3,
                        deep_research=False
                    )

                    # Parse research result into findings
                    findings = [{
                        "id": f"finding_{topic.id}_1",
                        "content": research_result,
                        "source": "web_research",
                        "confidence": 0.8,
                        "timestamp": datetime.now().isoformat(),
                    }]
                else:
                    # Fallback to simulation
                    self.logger.info(f"Using simulation for topic: {topic.title}")
                    findings = await self._simulate_research_findings(topic, depth)

                topic.findings.extend(findings)
                topic.confidence_score = min(0.9, topic.confidence_score + 0.2)
                topic.status = "completed"
                topic.last_updated = datetime.now()

                # Add to context
                findings_text = "\n".join([f["content"] for f in findings])
                if self.context_manager:
                    await self.context_manager.add_context(
                        content=findings_text,
                        window_id="research",
                        topic=topic.title,
                        importance=topic.confidence_score,
                    )

                progress.completed_topics += 1
                progress.findings_count += len(findings)

            except Exception as e:
                self.logger.error(f"Error researching topic {topic.id}: {e}")
                topic.status = "failed"

    async def _deep_research_topic(
        self, topic: ResearchTopic, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Perform deep research on a single topic."""
        try:
            if self.iterative_research_tool:
                # Use real deep research
                self.logger.info(f"Starting deep research on topic: {topic.title}")
                research_result = await self.iterative_research_tool.research_topic(
                    query=topic.title,
                    model="llama3.2:3b",
                    max_iterations=3,
                    search_limit=5,
                    deep_research=True
                )

                # Parse research result into findings
                deep_findings = [{
                    "id": f"deep_finding_{topic.id}_1",
                    "content": research_result,
                    "source": "deep_web_research",
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat(),
                }]
            else:
                # Fallback to simulation
                self.logger.info(f"Using deep simulation for topic: {topic.title}")
                deep_findings = await self._simulate_research_findings(
                    topic, topic.depth_level + 2, detailed=True
                )

            topic.findings.extend(deep_findings)
            topic.confidence_score = min(0.95, topic.confidence_score + 0.3)

            # Generate subtopics
            subtopics = await self._generate_subtopics(topic, plan)
            for subtopic in subtopics:
                plan.topics[subtopic.id] = subtopic
                topic.subtopics.append(subtopic.id)

        except Exception as e:
            self.logger.error(f"Error in deep research for topic {topic.id}: {e}")
            # Fallback to simulation on error
            deep_findings = await self._simulate_research_findings(
                topic, topic.depth_level + 2, detailed=True
            )
            topic.findings.extend(deep_findings)
            topic.confidence_score = min(0.95, topic.confidence_score + 0.2)

    async def _generate_subtopics(
        self, parent_topic: ResearchTopic, plan: ResearchPlan
    ) -> List[ResearchTopic]:
        """Generate subtopics for a parent topic."""
        # Submit subtopic generation task
        task = await self.multi_agent_system.submit_task(
            task_type="generate_subtopics",
            description=f"Generate subtopics for: {parent_topic.title}",
            data={
                "parent_topic": parent_topic.__dict__,
                "existing_topics": len(plan.topics),
                "breadth_limit": plan.breadth_limit,
            },
        )

        # Simulate subtopic generation
        await asyncio.sleep(2)

        # Generate mock subtopics
        subtopics = []
        for i in range(min(3, plan.breadth_limit - len(plan.topics))):
            subtopic = ResearchTopic(
                id=f"sub_{parent_topic.id}_{i}",
                title=f"{parent_topic.title} - Aspect {i+1}",
                description=f"Subtopic of {parent_topic.title}",
                priority=ResearchPriority.MEDIUM,
                depth_level=parent_topic.depth_level + 1,
                parent_topic=parent_topic.id,
            )
            subtopics.append(subtopic)

        return subtopics

    async def _identify_knowledge_gaps(
        self, plan: ResearchPlan
    ) -> List[Dict[str, Any]]:
        """Identify knowledge gaps in the research."""
        # Submit gap analysis task
        task = await self.multi_agent_system.submit_task(
            task_type="gap_analysis",
            description="Identify knowledge gaps in research findings",
            data={
                "topics": [t.__dict__ for t in plan.topics.values()],
                "findings": [t.findings for t in plan.topics.values()],
            },
        )

        # Simulate gap identification
        await asyncio.sleep(2)

        # Return mock gaps
        return [
            {
                "title": "Implementation Details",
                "description": "Missing practical implementation details and examples",
            },
            {
                "title": "Comparative Analysis",
                "description": "Need comparison with alternative approaches",
            },
        ]

    async def _identify_refinement_areas(
        self, plan: ResearchPlan
    ) -> List[Dict[str, Any]]:
        """Identify areas needing refinement."""
        # Submit refinement analysis task
        task = await self.multi_agent_system.submit_task(
            task_type="refinement_analysis",
            description="Identify areas needing research refinement",
            data={
                "plan": plan.__dict__,
                "progress": self.research_progress[plan.id].__dict__,
            },
        )

        # Simulate refinement identification
        await asyncio.sleep(2)

        return [
            {
                "title": "Quality Enhancement",
                "description": "Improve quality of findings through additional validation",
            }
        ]

    async def _simulate_research_findings(
        self, topic: ResearchTopic, depth: int, detailed: bool = False
    ) -> List[Dict[str, Any]]:
        """Simulate research findings (in practice, this would come from agents)."""
        num_findings = 3 if not detailed else 5

        findings = []
        for i in range(num_findings):
            finding = {
                "id": f"finding_{topic.id}_{i}",
                "content": f"Research finding {i+1} for topic '{topic.title}' at depth {depth}",
                "source": f"Source {i+1}",
                "confidence": 0.7 + (depth * 0.1),
                "timestamp": datetime.now().isoformat(),
            }
            findings.append(finding)

        return findings

    def _update_orchestration_metrics(
        self, plan: ResearchPlan, progress: ResearchProgress
    ):
        """Update orchestration performance metrics."""
        self.orchestration_metrics["total_plans_executed"] += 1

        if plan.completed_at and plan.started_at:
            completion_time = (
                plan.completed_at - plan.started_at
            ).total_seconds() / 3600
            current_avg = self.orchestration_metrics["average_completion_time"]
            total_plans = self.orchestration_metrics["total_plans_executed"]

            self.orchestration_metrics["average_completion_time"] = (
                current_avg * (total_plans - 1) + completion_time
            ) / total_plans

        # Update strategy success rates
        strategy = plan.strategy.value
        if strategy not in self.orchestration_metrics["strategy_success_rates"]:
            self.orchestration_metrics["strategy_success_rates"][strategy] = {
                "success": 0,
                "total": 0,
            }

        self.orchestration_metrics["strategy_success_rates"][strategy]["total"] += 1
        if progress.quality_score >= plan.quality_threshold:
            self.orchestration_metrics["strategy_success_rates"][strategy][
                "success"
            ] += 1

    async def get_research_status(self, plan_id: str) -> Dict[str, Any]:
        """Get comprehensive research status."""
        if plan_id not in self.active_plans:
            return {"error": "Plan not found"}

        plan = self.active_plans[plan_id]
        progress = self.research_progress[plan_id]

        return {
            "plan": {
                "id": plan.id,
                "title": plan.title,
                "strategy": plan.strategy.value,
                "phase": plan.current_phase.value,
                "created_at": plan.created_at.isoformat(),
                "started_at": plan.started_at.isoformat() if plan.started_at else None,
                "completed_at": plan.completed_at.isoformat()
                if plan.completed_at
                else None,
            },
            "progress": {
                "total_topics": len(plan.topics),
                "completed_topics": progress.completed_topics,
                "active_topics": progress.active_topics,
                "findings_count": progress.findings_count,
                "average_confidence": progress.average_confidence,
                "quality_score": progress.quality_score,
                "current_depth": progress.current_depth,
            },
            "topics": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority.value,
                    "depth_level": t.depth_level,
                    "confidence_score": t.confidence_score,
                    "findings_count": len(t.findings),
                }
                for t in plan.topics.values()
            ],
        }

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics."""
        return self.orchestration_metrics.copy()
