"""
Export endpoints for downloading research reports
GET /api/ideas/{idea_id}/export/pdf - Download idea as PDF
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from supabase import create_client
import io

from app.core.config import settings
from app.core.auth import get_current_user
from app.services.pdf_generator import generate_research_pdf

logger = logging.getLogger(__name__)
router = APIRouter()


def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


@router.get("/api/ideas/{idea_id}/export/pdf")
async def export_pdf(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Export idea as PDF report.

    Returns PDF file for download.
    """

    logger.info(f"User {user['id']} exporting idea {idea_id} as PDF")

    supabase = get_supabase()

    try:
        # Retrieve idea from database
        response = supabase.table("ideas")\
            .select("*")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        idea = response.data

        # Generate PDF
        pdf_bytes = generate_research_pdf(idea)

        # Create file-like object
        pdf_stream = io.BytesIO(pdf_bytes)

        # Sanitize filename
        filename = idea.get("title", "research-report").replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        filename = f"{filename}.pdf"

        logger.info(f"PDF exported successfully: {filename}")

        # Return as file download
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting PDF: {str(e)}")
