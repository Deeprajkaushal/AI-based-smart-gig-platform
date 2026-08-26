from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Review, Project, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


class ReviewCreate(BaseModel):
    project_id: int
    rating: int
    comment: str


@router.post("/")
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check rating
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    # Find project
    project = db.query(Project).filter(
        Project.id == review.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Only the client can submit a review
    if project.client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the project client can submit a review"
        )

    # Client reviews the freelancer
    reviewee_id = project.freelancer_id

    # Check if client already reviewed this project
    existing_review = db.query(Review).filter(
        Review.project_id == review.project_id,
        Review.reviewer_id == current_user.id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this project"
        )

    # Create review
    new_review = Review(
        project_id=review.project_id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=review.rating,
        comment=review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {
        "message": "Review submitted successfully",
        "review_id": new_review.id,
        "rating": new_review.rating,
        "comment": new_review.comment
    }


@router.get("/project/{project_id}")
def get_project_reviews(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find project
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Only users involved in the project can view its reviews
    if (
        project.client_id != current_user.id
        and project.freelancer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not part of this project"
        )

    # Return reviews
    return db.query(Review).filter(
        Review.project_id == project_id
    ).all()