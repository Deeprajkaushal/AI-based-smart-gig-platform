from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import User


router = APIRouter(
    prefix="/disputes",
    tags=["AI Dispute Assistant"]
)


class DisputeRequest(BaseModel):
    project_id: int
    issue: str
    client_statement: str
    freelancer_statement: str


@router.post("/analyze")
def analyze_dispute(
    dispute: DisputeRequest,
    current_user: User = Depends(get_current_user)
):

    issue = dispute.issue.lower()
    client_statement = dispute.client_statement.lower()
    freelancer_statement = dispute.freelancer_statement.lower()

    combined_text = (
        issue
        + " "
        + client_statement
        + " "
        + freelancer_statement
    )

    # Basic MVP dispute analysis
    if "late" in combined_text or "delay" in combined_text:
        recommendation = (
            "The dispute appears to involve a delivery delay. "
            "Review the agreed milestone deadline and submitted work. "
            "If the work was completed after the agreed deadline, "
            "consider a partial resolution or revised deadline."
        )

        dispute_type = "delivery_delay"

    elif "quality" in combined_text or "poor" in combined_text:
        recommendation = (
            "The dispute appears to involve work quality. "
            "Compare the submitted work against the original job "
            "requirements and milestone criteria. Consider requesting "
            "reasonable revisions before making a final decision."
        )

        dispute_type = "quality_issue"

    elif "payment" in combined_text or "money" in combined_text:
        recommendation = (
            "The dispute appears to involve payment. "
            "Review the agreed project budget, completed milestones, "
            "and work submitted before reaching a resolution."
        )

        dispute_type = "payment_issue"

    else:
        recommendation = (
            "The dispute requires manual review. "
            "Compare the original job requirements, project milestones, "
            "submitted work, and both parties' statements."
        )

        dispute_type = "general_dispute"

    return {
        "project_id": dispute.project_id,
        "dispute_type": dispute_type,
        "recommendation": recommendation,
        "status": "under_review"
    }