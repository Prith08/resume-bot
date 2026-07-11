import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///resume_bot.db")

RESUME_TEMPLATES = {
    "modern": "Modern - Clean & Minimal",
    "professional": "Professional - Corporate Style",
    "creative": "Creative - Bold & Colorful",
    "executive": "Executive - Executive Level",
    "technical": "Technical - Developer Focused",
}

JOB_ROLES = {
    "software_engineer": "Software Engineer",
    "network_engineer": "Network Engineer",
    "data_analyst": "Data Analyst",
    "accountant": "Accountant",
    "teacher": "Teacher",
}

# Conversation states
(
    WAITING_FULL_NAME,
    WAITING_EMAIL,
    WAITING_PHONE,
    WAITING_LOCATION,
    WAITING_OBJECTIVE,
    WAITING_EDUCATION,
    WAITING_EXPERIENCE,
    WAITING_SKILLS,
    WAITING_PROJECTS,
    WAITING_CERTIFICATIONS,
    WAITING_TEMPLATE,
    WAITING_JOB_ROLE,
    WAITING_EDIT_SECTION,
    WAITING_COVER_LETTER_JOB,
    WAITING_COVER_LETTER_COMPANY,
    WAITING_ATS_JOB_DESCRIPTION,
) = range(16)
