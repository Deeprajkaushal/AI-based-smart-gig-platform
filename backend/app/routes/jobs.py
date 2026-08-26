from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Job, User
from app.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreate(BaseModel):
    title: str
    description: str
    budget: float


@router.post("/")
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "client":
        raise HTTPException(
            status_code=403,
            detail="Only clients can post jobs"
        )

    new_job = Job(
        client_id=current_user.id,
        title=job.title,
        description=job.description,
        budget=job.budget
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "message": "Job created successfully",
        "job_id": new_job.id,
        "title": new_job.title,
        "description": new_job.description,
        "budget": new_job.budget,
        "status": new_job.status
    }


@router.get("/")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs