from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import FreelancerProfile, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/freelancers",
    tags=["Freelancers"]
)


class FreelancerProfileCreate(BaseModel):
    bio: str
    experience_years: int
    hourly_rate: float


@router.post("/profile")
def create_profile(
    profile: FreelancerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "freelancer":
        raise HTTPException(
            status_code=403,
            detail="Only freelancers can create freelancer profiles"
        )

    existing_profile = db.query(FreelancerProfile).filter(
        FreelancerProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Freelancer profile already exists"
        )

    new_profile = FreelancerProfile(
        user_id=current_user.id,
        bio=profile.bio,
        experience_years=profile.experience_years,
        hourly_rate=profile.hourly_rate
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "message": "Freelancer profile created successfully",
        "profile_id": new_profile.id,
        "bio": new_profile.bio,
        "experience_years": new_profile.experience_years,
        "hourly_rate": new_profile.hourly_rate
    }


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    profile = db.query(FreelancerProfile).filter(
        FreelancerProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Freelancer profile not found"
        )

    return profile