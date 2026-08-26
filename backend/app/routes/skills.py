from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Skill, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


class SkillCreate(BaseModel):
    skill_name: str


@router.post("/")
def add_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "freelancer":
        raise HTTPException(
            status_code=403,
            detail="Only freelancers can add skills"
        )

    existing_skill = db.query(Skill).filter(
        Skill.freelancer_id == current_user.id,
        Skill.skill_name == skill.skill_name
    ).first()

    if existing_skill:
        raise HTTPException(
            status_code=400,
            detail="Skill already exists"
        )

    new_skill = Skill(
        freelancer_id=current_user.id,
        skill_name=skill.skill_name
    )

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    return {
        "message": "Skill added successfully",
        "skill_id": new_skill.id,
        "skill_name": new_skill.skill_name
    }


@router.get("/my")
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "freelancer":
        raise HTTPException(
            status_code=403,
            detail="Only freelancers can view freelancer skills"
        )

    return db.query(Skill).filter(
        Skill.freelancer_id == current_user.id
    ).all()


@router.delete("/{skill_id}")
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.freelancer_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    db.delete(skill)
    db.commit()

    return {
        "message": "Skill deleted successfully"
    }