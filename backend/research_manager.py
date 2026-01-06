import asyncio
import json
import logging
from typing import Any, AsyncGenerator


async def start_research(topic: str, depth: str) -> str:
    """Start a research session."""
    import logging

    from utils.research_session_manager import research_session_manager

    logger = logging.getLogger(__name__)
    logger.info(f"Starting research on topic: {topic} with depth: {depth}")
    task_id = await research_session_manager.start_research(topic, depth)
    logger.info(f"Research started with task_id: {task_id}")
    return task_id


async def get_research_status(task_id: str) -> dict[str, Any]:
    """Get the status of a research session."""
    import logging

    from utils.research_session_manager import research_session_manager

    logger = logging.getLogger(__name__)
    status = await research_session_manager.get_status(task_id)
    if status is None:
        logger.warning(f"Research session not found: {task_id}")
        return {"error": "Research session not found", "status": "not_found"}
    logger.debug(f"Research status for {task_id}: {status.get('status')}")
    return status


async def stop_research(task_id: str) -> dict[str, Any]:
    from utils.research_session_manager import research_session_manager

    result = await research_session_manager.stop_research(task_id)
    return result


async def list_research_sessions() -> dict[str, Any]:
    from utils.research_session_manager import research_session_manager

    sessions = research_session_manager.list_saved_sessions()
    return {"sessions": list(sessions.values())}


async def resume_research_session(task_id: str) -> dict[str, Any]:
    from utils.research_session_manager import research_session_manager

    session = await research_session_manager.resume_session(task_id)
    if session:
        return {
            "task_id": task_id,
            "status": "resumed",
            "message": "Research session resumed",
        }
    else:
        return {"error": "Failed to resume session"}


def delete_research_session(task_id: str) -> dict[str, Any]:
    from utils.research_session_manager import research_session_manager

    research_session_manager.delete_session(task_id)
    return {"task_id": task_id, "status": "deleted"}


def get_agent_status() -> dict[str, Any]:
    try:
        from utils.research_session_manager import research_session_manager

        all_agents = []

        # Get agents from all active sessions
        for session in research_session_manager.sessions.values():
            if session.multi_agent_system:
                try:
                    # Get system status which includes agent information
                    status = session.multi_agent_system.get_system_status()
                    # Extract agent information
                    agents_info = []
                    for agent_id, agent in session.multi_agent_system.agents.items():
                        agents_info.append(
                            {
                                "id": agent.id,
                                "role": agent.config.role.value,
                                "model": agent.config.model,
                                "status": agent.state.value,
                                "current_task": agent.current_task.type
                                if agent.current_task
                                else None,
                                "performance_metrics": agent.performance_metrics,
                                "last_active": agent.last_active.isoformat()
                                if agent.last_active
                                else None,
                            }
                        )
                    all_agents.extend(agents_info)
                except Exception as e:
                    logging.error(
                        f"Error getting agent status for session {session.task_id}: {e}"
                    )

        return {"agents": all_agents}
    except Exception as e:
        return {"error": f"Failed to get agent status: {str(e)}"}


async def research_progress(task_id: str) -> AsyncGenerator[str, None]:
    from utils.research_session_manager import research_session_manager

    async def generate():
        try:
            queue = await research_session_manager.subscribe_progress(task_id)

            while True:
                try:
                    # Wait for progress update
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Format as SSE
                    data = json.dumps(update)
                    yield f"data: {data}\n\n"

                    # Check if research is complete
                    if update.get("status") == "completed":
                        break

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield 'data: {"type": "heartbeat"}\n\n'
                    continue

        except Exception as e:
            error_data = json.dumps({"error": str(e), "status": "error"})
            yield f"data: {error_data}\n\n"

    async for item in generate():
        yield item
