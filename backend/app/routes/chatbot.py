from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import User


router = APIRouter(
    prefix="/chatbot",
    tags=["AI Chatbot"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chatbot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    message = request.message.lower()

    if "job" in message:
        response = (
            "You can browse available jobs and apply for jobs "
            "that match your skills."
        )

    elif "application" in message:
        response = (
            "You can view your applications and track their status "
            "from the Applications section."
        )

    elif "profile" in message:
        response = (
            "Keep your freelancer profile and skills updated so "
            "clients and the AI recommendation system can find you."
        )

    elif "project" in message:
        response = (
            "Projects are created after a client accepts a freelancer's "
            "application."
        )

    else:
        response = (
            "I can help you with jobs, applications, profiles, "
            "projects, and using the Smart Gig Platform."
        )

    return {
        "user_id": current_user.id,
        "message": request.message,
        "response": response
    }