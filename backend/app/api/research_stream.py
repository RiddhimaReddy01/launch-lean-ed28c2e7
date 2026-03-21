"""
Streaming Research Endpoint
Returns results as each module completes (SSE - Server-Sent Events)

Usage:
  const eventSource = new EventSource('/api/research-stream?idea=...')
  eventSource.onmessage = (e) => {
    const {stage, data, progress} = JSON.parse(e.data)
    // Update UI as data arrives
  }
"""

import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.models import DecomposeRequest, DecomposeResponse
from app.api.decompose import decompose_idea
from app.api.discover import discover_insights
from app.api.analyze import analyze_section
from app.api.setup import generate_setup
from app.api.validate import generate_validation

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/research-stream")
async def research_stream(idea: str):
    """
    Stream research results as they complete.

    Frontend receives updates like:
    {"stage": "decompose", "status": "loading"}
    {"stage": "decompose", "status": "complete", "data": {...}}
    {"stage": "discover", "status": "loading"}
    {"stage": "discover", "status": "complete", "data": {...}}
    """

    if not idea or len(idea.split()) < 3:
        raise HTTPException(status_code=400, detail="Idea must be at least 3 words")

    async def generate():
        try:
            # Stage 1: Decompose (required by all others)
            yield format_sse("decompose", "loading", None, 0)

            try:
                decompose_req = DecomposeRequest(idea=idea)
                decompose_result = await decompose_idea(decompose_req, user=None)
                yield format_sse("decompose", "complete", decompose_result, 20)
            except Exception as e:
                logger.error(f"Decompose failed: {e}")
                yield format_sse("decompose", "error", {"error": str(e)}, 0)
                return

            # Stage 2-5: Run in parallel after decompose completes
            tasks = [
                ("discover", discover_insights(decompose_result)),
                ("analyze", analyze_section(
                    "opportunity",
                    None,
                    decompose_result,
                    undefined=None
                )),
                ("setup", generate_setup(None, decompose_result, None)),
                ("validate", generate_validation(None, decompose_result, None, None))
            ]

            # Yield loading states for all
            for stage, _ in tasks:
                yield format_sse(stage, "loading", None, 20)

            # Run all in parallel and stream results as they complete
            results = {}
            for stage, task in tasks:
                try:
                    result = await task
                    results[stage] = result
                    progress = 20 + (60 // len(tasks))
                    yield format_sse(stage, "complete", result, progress)
                except Exception as e:
                    logger.error(f"{stage} failed: {e}")
                    yield format_sse(stage, "error", {"error": str(e)}, 20)

            # Final status
            yield format_sse("research", "complete", results, 100)

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield format_sse("error", "error", {"error": str(e)}, 0)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


def format_sse(stage: str, status: str, data: any, progress: int) -> str:
    """Format Server-Sent Event"""
    event = {
        "stage": stage,
        "status": status,
        "progress": progress,
        "data": data
    }
    return f"data: {json.dumps(event)}\n\n"


@router.post("/api/research-batch")
async def research_batch(request: DecomposeRequest):
    """
    Batch endpoint: Run all 5 modules in parallel.
    Returns all results at once (but faster than sequential).

    This is for clients that can't handle streaming (like curl).
    """

    if not request.idea or len(request.idea.split()) < 3:
        raise HTTPException(status_code=400, detail="Idea must be at least 3 words")

    try:
        # Stage 1: Decompose
        decompose_result = await decompose_idea(request, user=None)

        # Stage 2-5: Parallel
        discover_task = asyncio.create_task(
            discover_insights(decompose_result)
        )
        analyze_task = asyncio.create_task(
            analyze_section("opportunity", None, decompose_result, None)
        )
        setup_task = asyncio.create_task(
            generate_setup(None, decompose_result, None)
        )
        validate_task = asyncio.create_task(
            generate_validation(None, decompose_result, None, None)
        )

        # Wait for all
        discover_result, analyze_result, setup_result, validate_result = await asyncio.gather(
            discover_task,
            analyze_task,
            setup_task,
            validate_task,
            return_exceptions=True
        )

        return {
            "decompose": decompose_result,
            "discover": discover_result if not isinstance(discover_result, Exception) else None,
            "analyze": analyze_result if not isinstance(analyze_result, Exception) else None,
            "setup": setup_result if not isinstance(setup_result, Exception) else None,
            "validate": validate_result if not isinstance(validate_result, Exception) else None
        }

    except Exception as e:
        logger.error(f"Batch research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
