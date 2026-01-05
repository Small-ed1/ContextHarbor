"""
Multi-Agent System Core
Implements overseer LLM coordinating multiple worker LLMs for parallel processing.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from utils.memory_manager import MemoryAction, MemoryAwareMixin, MemoryManager

from ..ollama_client import GenerationRequest, OllamaClient, OllamaConfig


class AgentRole(Enum):
    """Roles that agents can perform."""

    OVERSEER = "overseer"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    SYNTHESIZER = "synthesizer"
    VALIDATOR = "validator"


class AgentState(Enum):
    """States an agent can be in."""

    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    role: AgentRole
    model: str
    max_concurrent_tasks: int = 1
    task_timeout: int = 300  # seconds
    memory_limit_mb: int = 1024
    specialization: Optional[str] = None


@dataclass
class AgentTask:
    """A task assigned to an agent."""

    id: str
    type: str
    description: str
    data: Dict[str, Any]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None


@dataclass
class Agent:
    """An individual AI agent in the multi-agent system."""

    id: str
    config: AgentConfig
    state: AgentState = AgentState.IDLE
    current_task: Optional[AgentTask] = None
    task_history: List[AgentTask] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None

    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle a given task."""
        # Check if agent is specialized for this task type
        if self.config.specialization and task.type not in self.config.specialization:
            return False

        # Check if agent has capacity
        active_tasks = sum(
            1 for t in self.task_history if t.status in ["pending", "running"]
        )
        return active_tasks < self.config.max_concurrent_tasks

    def update_performance(self, task: AgentTask, success: bool, duration: float):
        """Update agent performance metrics."""
        if "tasks_completed" not in self.performance_metrics:
            self.performance_metrics = {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "avg_completion_time": 0.0,
                "success_rate": 0.0,
            }

        metrics = self.performance_metrics
        metrics["tasks_completed"] += 1 if success else 0
        metrics["tasks_failed"] += 0 if success else 1

        # Update average completion time
        total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
        if total_tasks > 0:
            current_avg = metrics["avg_completion_time"]
            metrics["avg_completion_time"] = (
                current_avg * (total_tasks - 1) + duration
            ) / total_tasks
            metrics["success_rate"] = metrics["tasks_completed"] / total_tasks


class MultiAgentSystem(MemoryAwareMixin):
    """Core multi-agent system with overseer coordination."""

    def __init__(self, memory_manager: MemoryManager, ollama_config: OllamaConfig):
        super().__init__(memory_manager)
        self.ollama_config = ollama_config
        self.ollama_client = OllamaClient(ollama_config)
        self.logger = logging.getLogger(__name__)

        # Agent management
        self.agents: Dict[str, Agent] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_queue: asyncio.Queue[AgentTask] = asyncio.Queue()

        # System state
        self.is_running = False
        self.overseer_agent: Optional[Agent] = None

        # Performance tracking
        self.system_metrics: Dict[str, Any] = {
            "total_tasks_processed": 0,
            "active_agents": 0,
            "avg_task_completion_time": 0.0,
            "system_efficiency": 0.0,
        }

        # Register memory management callbacks
        self._register_memory_callbacks()

    def _register_memory_callbacks(self):
        """Register callbacks for memory management actions."""
        self.memory_manager.register_callback(
            MemoryAction.REDUCE_AGENTS, self._reduce_agent_count
        )
        self.memory_manager.register_callback(
            MemoryAction.LOWER_MODEL_SIZE, self._lower_model_sizes
        )
        self.memory_manager.register_callback(
            MemoryAction.RESTART_PROCESSES, self._restart_problematic_agents
        )

    async def initialize_system(self, num_workers: int = 3):
        """Initialize the multi-agent system."""
        self.logger.info(f"Initializing multi-agent system with {num_workers} workers")

        # Create overseer agent
        overseer_config = AgentConfig(
            role=AgentRole.OVERSEER,
            model=self.ollama_config.large_model,  # Use most capable model for oversight
            max_concurrent_tasks=5,
            specialization="coordination,planning,task_decomposition",
        )
        self.overseer_agent = Agent(id="overseer", config=overseer_config)
        self.agents["overseer"] = self.overseer_agent

        # Create worker agents
        worker_roles = [AgentRole.RESEARCHER, AgentRole.ANALYST, AgentRole.SYNTHESIZER]
        for i in range(num_workers):
            role = worker_roles[i % len(worker_roles)]
            agent_config = AgentConfig(
                role=role,
                model=self._select_model_for_role(role),
                max_concurrent_tasks=2,
                specialization=self._get_specialization_for_role(role),
            )

            agent = Agent(id=f"worker_{i+1}", config=agent_config)
            self.agents[agent.id] = agent

        self.logger.info(f"Initialized {len(self.agents)} agents")

    def _select_model_for_role(self, role: AgentRole) -> str:
        """Select appropriate model for agent role."""
        role_model_map = {
            AgentRole.RESEARCHER: self.ollama_config.default_model,  # Balanced for research
            AgentRole.ANALYST: self.ollama_config.large_model,  # Complex analysis
            AgentRole.SYNTHESIZER: self.ollama_config.large_model,  # Synthesis requires capability
            AgentRole.VALIDATOR: self.ollama_config.default_model,  # Validation needs accuracy
        }
        return role_model_map.get(role, self.ollama_config.default_model)

    def _get_specialization_for_role(self, role: AgentRole) -> str:
        """Get specialization string for agent role."""
        specializations = {
            AgentRole.RESEARCHER: "web_research,fact_gathering,information_synthesis",
            AgentRole.ANALYST: "data_analysis,pattern_recognition,critical_thinking",
            AgentRole.SYNTHESIZER: "knowledge_integration,recommendation_generation,strategic_planning",
            AgentRole.VALIDATOR: "fact_checking,quality_assessment,consistency_validation",
        }
        return specializations.get(role, "")

    async def start_system(self):
        """Start the multi-agent system."""
        if self.is_running:
            return

        self.is_running = True
        self.logger.info("Starting multi-agent system")

        async with self.ollama_client:
            # Start agent task processors
            agent_tasks = []
            for agent in self.agents.values():
                if agent.id != "overseer":  # Overseer is handled separately
                    task = asyncio.create_task(self._run_agent_loop(agent.id))
                    agent_tasks.append(task)

            # Start overseer coordination
            overseer_task = asyncio.create_task(self._run_overseer_loop())

            # Start task distribution
            distributor_task = asyncio.create_task(self._distribute_tasks())

            # Wait for all tasks
            try:
                await asyncio.gather(overseer_task, distributor_task, *agent_tasks)
            except Exception as e:
                self.logger.error(f"Error in multi-agent system: {e}")
            finally:
                self.is_running = False

    async def submit_task(
        self, task_type: str, description: str, data: Dict[str, Any], priority: int = 1
    ) -> str:
        """Submit a task to the system."""
        task = AgentTask(
            id=str(uuid.uuid4()),
            type=task_type,
            description=description,
            data=data,
            priority=priority,
        )

        await self.task_queue.put(task)
        self.active_tasks[task.id] = task
        self.logger.info(f"Submitted task {task.id}: {task_type}")
        return task.id

    async def _run_overseer_loop(self):
        """Main overseer coordination loop."""
        cleanup_counter = 0

        while self.is_running:
            try:
                # Periodic memory cleanup (every 5 minutes)
                cleanup_counter += 1
                if cleanup_counter >= 30:  # 30 * 10 seconds = 5 minutes
                    await self.perform_memory_cleanup()
                    cleanup_counter = 0

                # Check system status
                system_status = self._assess_system_status()

                # Generate coordination decisions
                if system_status["needs_coordination"]:
                    coordination_plan = await self._generate_coordination_plan(
                        system_status
                    )

                    # Execute coordination actions
                    await self._execute_coordination_plan(coordination_plan)

                # Monitor task progress
                await self._monitor_task_progress()

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error in overseer loop: {e}")
                await asyncio.sleep(5)

    async def _run_agent_loop(self, agent_id: str):
        """Main loop for individual agent."""
        while self.is_running:
            try:
                agent = self.agents.get(agent_id)
                if not agent or agent.state == AgentState.TERMINATED:
                    break

                # Check memory constraints
                if not self.check_memory_before_operation():
                    agent.state = AgentState.IDLE
                    await asyncio.sleep(30)  # Wait for memory situation to improve
                    continue

                # Get next task for this agent
                task = await self._get_next_task_for_agent(agent_id)

                if task:
                    await self._execute_agent_task(agent_id, task)
                else:
                    agent.state = AgentState.IDLE
                    await asyncio.sleep(5)  # Wait for new tasks

            except Exception as e:
                self.logger.error(f"Error in agent {agent_id} loop: {e}")
                agent = self.agents.get(agent_id)
                if agent:
                    agent.state = AgentState.ERROR
                await asyncio.sleep(10)

    async def _distribute_tasks(self):
        """Distribute tasks from queue to appropriate agents."""
        while self.is_running:
            try:
                # Get next task from queue
                task = await self.task_queue.get()

                # Find suitable agent
                assigned_agent = await self._assign_task_to_agent(task)

                if assigned_agent:
                    task.assigned_to = assigned_agent
                    task.status = "assigned"
                    self.logger.info(
                        f"Assigned task {task.id} to agent {assigned_agent}"
                    )
                else:
                    # No suitable agent found, re-queue with lower priority
                    task.priority = max(1, task.priority - 1)
                    await asyncio.sleep(1)  # Brief delay before re-queuing
                    await self.task_queue.put(task)

                self.task_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error in task distribution: {e}")
                await asyncio.sleep(5)

    async def _assign_task_to_agent(self, task: AgentTask) -> Optional[str]:
        """Find the best agent for a task."""
        best_agent = None
        best_score = -1.0

        for agent_id, agent in self.agents.items():
            if agent_id == "overseer":
                continue

            if agent.can_handle_task(task) and agent.state != AgentState.ERROR:
                # Calculate agent suitability score
                score = self._calculate_agent_suitability(agent, task)

                if score > best_score:
                    best_score = score
                    best_agent = agent_id

        return best_agent

    def _calculate_agent_suitability(self, agent: Agent, task: AgentTask) -> float:
        """Calculate how suitable an agent is for a task."""
        score = 0.0

        # Role match
        if agent.config.role.name.lower() in task.type.lower():
            score += 0.4

        # Specialization match
        if agent.config.specialization and any(
            spec in task.type for spec in agent.config.specialization.split(",")
        ):
            score += 0.3

        # Performance history
        if agent.performance_metrics.get("success_rate", 0) > 0.8:
            score += 0.2

        # Current workload (prefer less busy agents)
        active_tasks = sum(
            1 for t in agent.task_history if t.status in ["pending", "running"]
        )
        workload_penalty = active_tasks * 0.1
        score -= min(workload_penalty, 0.3)

        # Priority consideration
        score += task.priority * 0.1

        return max(0.0, score)

    async def _execute_agent_task(self, agent_id: str, task: AgentTask):
        """Execute a task using the specified agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        agent.state = AgentState.WORKING
        agent.current_task = task
        task.status = "running"

        start_time = datetime.now()

        try:
            # Generate prompt for the task
            prompt = await self._generate_task_prompt(agent, task)

            # Execute with Ollama
            request = GenerationRequest(
                prompt=prompt,
                model=agent.config.model,
                max_tokens=2000,
                temperature=0.7,
            )

            async with OllamaClient(self.ollama_config) as client:
                response = await client.generate(request)

            # Process result
            task.result = response.text
            task.status = "completed"
            task.completed_at = datetime.now()

            # Update agent performance
            duration = (datetime.now() - start_time).total_seconds()
            agent.update_performance(task, True, duration)

            self.logger.info(f"Agent {agent_id} completed task {task.id}")

        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = datetime.now()

            # Update agent performance
            duration = (datetime.now() - start_time).total_seconds()
            agent.update_performance(task, False, duration)

            self.logger.error(f"Agent {agent_id} failed task {task.id}: {e}")

        finally:
            agent.state = AgentState.IDLE
            agent.current_task = None
            agent.last_active = datetime.now()

    async def _generate_task_prompt(self, agent: Agent, task: AgentTask) -> str:
        """Generate appropriate prompt for agent task."""
        base_prompt = f"""
You are an AI agent specializing in {agent.config.role.value}.
Your task: {task.description}

Task Data: {json.dumps(task.data, indent=2)}

Please provide a comprehensive response focusing on your area of expertise.
"""

        # Add role-specific instructions
        if agent.config.role == AgentRole.RESEARCHER:
            base_prompt += "\nFocus on gathering accurate, relevant information and citing sources."
        elif agent.config.role == AgentRole.ANALYST:
            base_prompt += "\nAnalyze the information critically and identify key insights and patterns."
        elif agent.config.role == AgentRole.SYNTHESIZER:
            base_prompt += (
                "\nSynthesize information into coherent recommendations and strategies."
            )

        return base_prompt

    async def _get_next_task_for_agent(self, agent_id: str) -> Optional[AgentTask]:
        """Get the next appropriate task for an agent."""
        # This is a simplified implementation
        # In practice, you'd have a more sophisticated task assignment system
        for task in self.active_tasks.values():
            if task.assigned_to == agent_id and task.status == "assigned":
                return task
        return None

    def _assess_system_status(self) -> Dict[str, Any]:
        """Assess overall system status."""
        total_agents = len(self.agents)
        active_agents = sum(
            1 for a in self.agents.values() if a.state == AgentState.WORKING
        )
        pending_tasks = sum(
            1 for t in self.active_tasks.values() if t.status == "pending"
        )

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": total_agents - active_agents,
            "pending_tasks": pending_tasks,
            "system_load": active_agents / max(total_agents, 1),
            "needs_coordination": pending_tasks > active_agents * 2,
        }

    async def _generate_coordination_plan(
        self, system_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a coordination plan using the overseer."""
        if self.overseer_agent is None:
            return {
                "recommendations": "Overseer agent not initialized",
                "actions": []
            }

        status_summary = f"""
System Status:
- Total Agents: {system_status['total_agents']}
- Active Agents: {system_status['active_agents']}
- Pending Tasks: {system_status['pending_tasks']}
- System Load: {system_status['system_load']:.2f}

Please analyze this status and provide coordination recommendations.
"""

        request = GenerationRequest(
            prompt=status_summary,
            system_prompt="You are an expert system coordinator. Analyze the current system status and provide specific recommendations for task distribution, agent management, and system optimization.",
            model=self.overseer_agent.config.model,
            max_tokens=1000,
        )

        async with OllamaClient(self.ollama_config) as client:
            response = await client.generate(request)

        # Parse coordination plan (simplified)
        return {
            "recommendations": response.text,
            "actions": self._parse_coordination_actions(response.text),
        }

    def _parse_coordination_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse coordination actions from overseer response."""
        # Simplified parsing - in practice, you'd use more sophisticated NLP
        actions = []
        if "spawn agent" in response_text.lower():
            actions.append({"type": "spawn_agent", "count": 1})
        if "reduce load" in response_text.lower():
            actions.append({"type": "reduce_load"})
        return actions

    async def _execute_coordination_plan(self, plan: Dict[str, Any]):
        """Execute the coordination plan."""
        for action in plan.get("actions", []):
            if action["type"] == "spawn_agent":
                await self._spawn_additional_agent()
            elif action["type"] == "reduce_load":
                await self._reduce_system_load()

    async def _monitor_task_progress(self):
        """Monitor overall task progress and system efficiency."""
        completed_tasks = sum(
            1 for t in self.active_tasks.values() if t.status == "completed"
        )
        total_tasks = len(self.active_tasks)

        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            self.system_metrics["system_efficiency"] = completion_rate

    async def _spawn_additional_agent(self):
        """Spawn an additional agent if resources allow."""
        if not self.check_memory_before_operation():
            self.logger.warning(
                "Cannot spawn additional agent due to memory constraints"
            )
            return

        agent_count = len([a for a in self.agents.keys() if a.startswith("worker_")])
        new_agent_id = f"worker_{agent_count + 1}"

        # Create new agent with conservative settings
        agent_config = AgentConfig(
            role=AgentRole.RESEARCHER,  # Default to researcher
            model=self.ollama_config.small_model,  # Use smaller model
            max_concurrent_tasks=1,
            specialization="general_assistance",
        )

        agent = Agent(id=new_agent_id, config=agent_config)
        self.agents[new_agent_id] = agent

        # Start agent loop
        asyncio.create_task(self._run_agent_loop(new_agent_id))
        self.logger.info(f"Spawned additional agent: {new_agent_id}")

    async def _reduce_system_load(self):
        """Reduce system load by pausing non-critical tasks."""
        # Implementation would pause lower-priority tasks
        self.logger.info("Reducing system load by pausing non-critical tasks")

    # Memory management callbacks
    async def _reduce_agent_count(self, memory_stats):
        """Reduce the number of active agents."""
        worker_agents = [
            aid
            for aid, a in self.agents.items()
            if aid.startswith("worker_") and a.state != AgentState.TERMINATED
        ]

        if len(worker_agents) > 1:
            # Terminate the least efficient agent
            agent_to_terminate = min(
                worker_agents,
                key=lambda x: self.agents[x].performance_metrics.get("success_rate", 0),
            )
            self.agents[agent_to_terminate].state = AgentState.TERMINATED
            self.logger.info(
                f"Terminated agent {agent_to_terminate} due to memory constraints"
            )

    async def _lower_model_sizes(self, memory_stats):
        """Switch agents to smaller models."""
        for agent in self.agents.values():
            if agent.config.model == self.ollama_config.large_model:
                agent.config.model = self.ollama_config.default_model
                self.logger.info(f"Switched agent {agent.id} to smaller model")

    async def _restart_problematic_agents(self, memory_stats):
        """Restart agents that are in error state."""
        for agent in self.agents.values():
            if agent.state == AgentState.ERROR:
                agent.state = AgentState.IDLE
                agent.current_task = None
                self.logger.info(f"Restarted problematic agent {agent.id}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(
                1 for a in self.agents.values() if a.state == AgentState.WORKING
            ),
            "idle_agents": sum(
                1 for a in self.agents.values() if a.state == AgentState.IDLE
            ),
            "error_agents": sum(
                1 for a in self.agents.values() if a.state == AgentState.ERROR
            ),
            "total_tasks": len(self.active_tasks),
            "pending_tasks": sum(
                1 for t in self.active_tasks.values() if t.status == "pending"
            ),
            "running_tasks": sum(
                1 for t in self.active_tasks.values() if t.status == "running"
            ),
            "completed_tasks": sum(
                1 for t in self.active_tasks.values() if t.status == "completed"
            ),
            "failed_tasks": sum(
                1 for t in self.active_tasks.values() if t.status == "failed"
            ),
            "system_metrics": self.system_metrics,
            "memory_stats": self.memory_manager.get_memory_report(),
        }

    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks to prevent memory leaks."""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Clean up active_tasks
        tasks_to_remove = []
        for task_id, task in self.active_tasks.items():
            if task.completed_at and task.completed_at < cutoff_time:
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.active_tasks[task_id]
            self.logger.debug(f"Cleaned up old task: {task_id}")

        # Clean up agent task histories (keep only recent tasks)
        for agent in self.agents.values():
            if len(agent.task_history) > 100:  # Keep max 100 tasks per agent
                # Keep most recent tasks
                agent.task_history.sort(key=lambda t: t.created_at, reverse=True)
                agent.task_history = agent.task_history[:50]  # Keep 50 most recent
                self.logger.debug(f"Trimmed task history for agent {agent.id}")

    async def cleanup_inactive_agents(self, max_idle_hours: int = 48):
        """Remove agents that have been idle for too long."""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_idle_hours)
        agents_to_remove = []

        for agent_id, agent in self.agents.items():
            if agent_id == "overseer":
                continue  # Don't remove overseer

            if (agent.state == AgentState.IDLE and
                agent.last_active and agent.last_active < cutoff_time):
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            del self.agents[agent_id]
            self.logger.info(f"Cleaned up inactive agent: {agent_id}")

    async def perform_memory_cleanup(self):
        """Perform comprehensive memory cleanup."""
        await self.cleanup_completed_tasks()
        await self.cleanup_inactive_agents()

        # Force garbage collection
        import gc
        collected = gc.collect()
        self.logger.debug(f"Garbage collection freed {collected} objects")
