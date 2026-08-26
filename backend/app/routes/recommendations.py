from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, Skill, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/recommendations",
    tags=["AI Recommendations"]
)


@router.get("/job/{job_id}")
def recommend_freelancers(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Only the client who created the job can request recommendations
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the job owner can view recommendations"
        )

    # Extract skills from the job description
    job_text = (
        f"{job.title} {job.description}"
    ).lower()

    # Basic skill dictionary for the MVP
    known_skills = [
        "python",
        "java",
        "javascript",
        "react",
        "fastapi",
        "sql",
        "postgresql",
        "machine learning",
        "data science",
        "html",
        "css",
        "tailwind",
        "node.js",
        "c++",
        "git",
        "docker"
    ]

    required_skills = [
        skill for skill in known_skills
        if skill in job_text
    ]

    if not required_skills:
        return {
            "job_id": job.id,
            "message": "No recognized skills found in the job description",
            "recommendations": []
        }

    freelancers = db.query(User).filter(
        User.role == "freelancer"
    ).all()

    recommendations = []

    for freelancer in freelancers:

        freelancer_skills = db.query(Skill).filter(
            Skill.freelancer_id == freelancer.id
        ).all()

        freelancer_skill_names = [
            skill.skill_name.lower()
            for skill in freelancer_skills
        ]

        matched_skills = [
            skill
            for skill in required_skills
            if skill in freelancer_skill_names
        ]

        match_percentage = (
            len(matched_skills) / len(required_skills)
        ) * 100

        if match_percentage > 0:

            recommendations.append({
                "freelancer_id": freelancer.id,
                "freelancer_name": freelancer.name,
                "match_percentage": round(
                    match_percentage,
                    2
                ),
                "matched_skills": matched_skills,
                "required_skills": required_skills
            })

    # Highest matching freelancers first
    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return {
        "job_id": job.id,
        "required_skills": required_skills,
        "recommendations": recommendations
    }