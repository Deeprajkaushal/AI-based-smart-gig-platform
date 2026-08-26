from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Application, Job, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: str


@router.post("/")
def apply_to_job(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only freelancers can apply
    if current_user.role != "freelancer":
        raise HTTPException(
            status_code=403,
            detail="Only freelancers can apply to jobs"
        )

    # Check job exists
    job = db.query(Job).filter(Job.id == application.job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Check job is still open
    if job.status != "open":
        raise HTTPException(
            status_code=400,
            detail="This job is not open"
        )

    # Check if freelancer already applied
    existing_application = db.query(Application).filter(
        Application.job_id == application.job_id,
        Application.freelancer_id == current_user.id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You have already applied to this job"
        )

    new_application = Application(
        job_id=application.job_id,
        freelancer_id=current_user.id,
        cover_letter=application.cover_letter,
        status="pending"
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return {
        "message": "Application submitted successfully",
        "application_id": new_application.id,
        "job_id": new_application.job_id,
        "freelancer_id": new_application.freelancer_id,
        "status": new_application.status
    }


@router.get("/job/{job_id}")
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Only the client who created the job can see applications
    if current_user.id != job.client_id:
        raise HTTPException(
            status_code=403,
            detail="Only the job owner can view applications"
        )

    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()

    return applications

@router.put("/{application_id}/accept")
def accept_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    job = db.query(Job).filter(
        Job.id == application.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Only the client who owns the job can accept
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the job owner can accept applications"
        )

    application.status = "accepted"

    db.commit()
    db.refresh(application)

    return {
        "message": "Application accepted successfully",
        "application_id": application.id,
        "status": application.status
    }


@router.put("/{application_id}/reject")
def reject_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    job = db.query(Job).filter(
        Job.id == application.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Only the client who owns the job can reject
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the job owner can reject applications"
        )

    application.status = "rejected"

    db.commit()
    db.refresh(application)

    return {
        "message": "Application rejected successfully",
        "application_id": application.id,
        "status": application.status
    }