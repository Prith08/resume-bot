import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "resume_bot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            career_objective TEXT,
            education TEXT,
            work_experience TEXT,
            skills TEXT,
            projects TEXT,
            certifications TEXT,
            selected_template TEXT DEFAULT 'modern',
            job_role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            template TEXT,
            job_role TEXT,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cover_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_title TEXT,
            company TEXT,
            letter_text TEXT,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


def save_user_data(user_id, username, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (user_id, username, full_name, email, phone, location, career_objective,
         education, work_experience, skills, projects, certifications,
         selected_template, job_role, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, username,
        data.get("full_name", ""),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("location", ""),
        data.get("career_objective", ""),
        json.dumps(data.get("education", [])),
        json.dumps(data.get("work_experience", [])),
        json.dumps(data.get("skills", [])),
        json.dumps(data.get("projects", [])),
        json.dumps(data.get("certifications", [])),
        data.get("selected_template", "modern"),
        data.get("job_role", ""),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_user_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "email": row["email"],
        "phone": row["phone"],
        "location": row["location"],
        "career_objective": row["career_objective"],
        "education": json.loads(row["education"]) if row["education"] else [],
        "work_experience": json.loads(row["work_experience"]) if row["work_experience"] else [],
        "skills": json.loads(row["skills"]) if row["skills"] else [],
        "projects": json.loads(row["projects"]) if row["projects"] else [],
        "certifications": json.loads(row["certifications"]) if row["certifications"] else [],
        "selected_template": row["selected_template"],
        "job_role": row["job_role"],
    }


def save_resume_record(user_id, template, job_role, pdf_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resumes (user_id, template, job_role, pdf_path)
        VALUES (?, ?, ?, ?)
    """, (user_id, template, job_role, pdf_path))

    conn.commit()
    conn.close()


def save_cover_letter(user_id, job_title, company, letter_text, pdf_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cover_letters (user_id, job_title, company, letter_text, pdf_path)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, job_title, company, letter_text, pdf_path))

    conn.commit()
    conn.close()
