from sqlalchemy import Column, BigInteger, String, Text, Numeric, DateTime, Integer, ForeignKey
from datetime import datetime

from app.database import Base


# 1. USERS
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. FREELANCER PROFILES
class FreelancerProfile(Base):
    __tablename__ = "freelancer_profiles"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    hourly_rate = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)


# 3. JOBS
class Job(Base):
    __tablename__ = "jobs"

    id = Column(BigInteger, primary_key=True, index=True)
    client_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Numeric(10, 2))
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


# 4. APPLICATIONS
class Application(Base):
    __tablename__ = "applications"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )
    freelancer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    cover_letter = Column(Text)
    proposed_rate = Column(Numeric(10, 2))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


# 5. PROJECTS
class Project(Base):
    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    client_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    freelancer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)


# 6. MILESTONES
class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(BigInteger, primary_key=True, index=True)
    project_id = Column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


# 7. SUBMISSIONS
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(BigInteger, primary_key=True, index=True)
    milestone_id = Column(
        BigInteger,
        ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False
    )
    freelancer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    submission_text = Column(Text)
    file_url = Column(Text)
    status = Column(String(20), default="submitted")
    submitted_at = Column(DateTime, default=datetime.utcnow)


# 8. REVIEWS
class Review(Base):
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True, index=True)
    project_id = Column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    reviewer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    reviewee_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# 9. AI RECOMMENDATIONS
class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )
    freelancer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    match_score = Column(Numeric(5, 2))
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# 10. CHATBOT CONVERSATIONS
class ChatbotConversation(Base):
    __tablename__ = "chatbot_conversations"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 11. DISPUTES
class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(BigInteger, primary_key=True, index=True)
    project_id = Column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    raised_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    description = Column(Text, nullable=False)
    ai_analysis = Column(Text)
    status = Column(String(20), default="open")
    resolution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 12. FREELANCER SKILLS
class Skill(Base):
    __tablename__ = "skills"

    id = Column(BigInteger, primary_key=True, index=True)
    freelancer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    skill_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)