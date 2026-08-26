from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, Application, Job, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/from-application/{application_id}")
def create_project_from_application(
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

    # Only the client who owns the job can create the project
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the job owner can create the project"
        )

    # Application must be accepted
    if application.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Application must be accepted first"
        )

    existing_project = db.query(Project).filter(
        Project.job_id == job.id
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project already exists for this job"
        )

    new_project = Project(
    job_id=job.id,
    client_id=job.client_id,
    freelancer_id=application.freelancer_id,
    title=job.title,
    description=job.description,
    status="active"
)

    db.add(new_project)

    # Close the job after selecting a freelancer
    job.status = "closed"

    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project created successfully",
        "project_id": new_project.id,
        "job_id": new_project.job_id,
        "client_id": new_project.client_id,
        "freelancer_id": new_project.freelancer_id,
        "status": new_project.status
    }


@router.get("/")
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    projects = db.query(Project).filter(
        (Project.client_id == current_user.id) |
        (Project.freelancer_id == current_user.id)
    ).all()

    return projects