from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Submission, Milestone, Project, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)


class SubmissionCreate(BaseModel):
    milestone_id: int
    work_description: str
    work_link: str | None = None


@router.post("/")
def submit_work(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    milestone = db.query(Milestone).filter(
        Milestone.id == submission.milestone_id
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    project = db.query(Project).filter(
        Project.id == milestone.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Only the freelancer assigned to the project can submit work
    if project.freelancer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned freelancer can submit work"
        )

    new_submission = Submission(
    milestone_id=submission.milestone_id,
    freelancer_id=current_user.id,
    submission_text=submission.work_description,
    file_url=submission.work_link,
    status="submitted"
)

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return {
        "message": "Work submitted successfully",
        "submission_id": new_submission.id,
        "milestone_id": new_submission.milestone_id,
        "status": new_submission.status
    }


@router.get("/milestone/{milestone_id}")
def get_milestone_submission(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    project = db.query(Project).filter(
        Project.id == milestone.project_id
    ).first()

    if (
        project.client_id != current_user.id
        and project.freelancer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not part of this project"
        )

    return db.query(Submission).filter(
        Submission.milestone_id == milestone_id
    ).all()