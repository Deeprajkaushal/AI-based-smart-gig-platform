from fastapi import FastAPI

from app.database import engine, Base
from app import models

from app.routes import (
    users,
    jobs,
    freelancers,
    applications,
    projects,
    milestones,
    submissions,
    reviews,
    skills,
    recommendations,
    chatbot,
    disputes
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Based Smart Gig Platform API",
    description="Backend API for the AI Based Smart Gig Platform",
    version="1.0.0"
)


# User routes
app.include_router(users.router)

# Job routes
app.include_router(jobs.router)

# Freelancer routes
app.include_router(freelancers.router)

# Application routes
app.include_router(applications.router)

# Project routes
app.include_router(projects.router)

# Milestone routes
app.include_router(milestones.router)

# Work submission routes
app.include_router(submissions.router)

# Review and rating routes
app.include_router(reviews.router)

# Freelancer skills
app.include_router(skills.router)

# AI freelancer recommendations
app.include_router(recommendations.router)

# AI chatbot
app.include_router(chatbot.router)

# AI dispute assistant
app.include_router(disputes.router)


@app.get("/")
def root():
    return {
        "message": "AI Based Smart Gig Platform API is running"
    }