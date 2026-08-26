from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Milestone, Project, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"]
)


class MilestoneCreate(BaseModel):
    project_id: int
    title: str
    description: str


@router.post("/")
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == milestone.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Only project client can create milestones
    if project.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the client can create milestones"
        )

    new_milestone = Milestone(
        project_id=milestone.project_id,
        title=milestone.title,
        description=milestone.description,
        status="pending"
    )

    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)

    return {
        "message": "Milestone created successfully",
        "milestone_id": new_milestone.id,
        "project_id": new_milestone.project_id,
        "title": new_milestone.title,
        "status": new_milestone.status
    }


@router.get("/project/{project_id}")
def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if (
        project.client_id != current_user.id
        and project.freelancer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not part of this project"
        )

    return db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).all()


@router.put("/{milestone_id}/complete")
def complete_milestone(
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

    if project.freelancer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the freelancer can complete a milestone"
        )

    milestone.status = "completed"

    db.commit()
    db.refresh(milestone)

    return {
        "message": "Milestone completed successfully",
        "milestone_id": milestone.id,
        "status": milestone.status
    }