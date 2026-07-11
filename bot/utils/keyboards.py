from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import RESUME_TEMPLATES, JOB_ROLES


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Create New Resume", callback_data="create_resume")],
        [InlineKeyboardButton("Edit Existing Resume", callback_data="edit_resume")],
        [InlineKeyboardButton("Generate Cover Letter", callback_data="cover_letter")],
        [InlineKeyboardButton("ATS Score Checker", callback_data="ats_checker")],
        [InlineKeyboardButton("Optimize Keywords", callback_data="optimize_keywords")],
        [InlineKeyboardButton("Suggest Skills", callback_data="suggest_skills")],
    ]
    return InlineKeyboardMarkup(keyboard)


def template_keyboard():
    keyboard = []
    for key, name in RESUME_TEMPLATES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"template_{key}")])
    return InlineKeyboardMarkup(keyboard)


def job_role_keyboard():
    keyboard = []
    for key, name in JOB_ROLES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"jobrole_{key}")])
    keyboard.append([InlineKeyboardButton("General (No specific role)", callback_data="jobrole_general")])
    return InlineKeyboardMarkup(keyboard)


def edit_section_keyboard():
    keyboard = [
        [InlineKeyboardButton("Full Name", callback_data="edit_full_name")],
        [InlineKeyboardButton("Email", callback_data="edit_email")],
        [InlineKeyboardButton("Phone", callback_data="edit_phone")],
        [InlineKeyboardButton("Location", callback_data="edit_location")],
        [InlineKeyboardButton("Career Objective", callback_data="edit_career_objective")],
        [InlineKeyboardButton("Education", callback_data="edit_education")],
        [InlineKeyboardButton("Work Experience", callback_data="edit_work_experience")],
        [InlineKeyboardButton("Skills", callback_data="edit_skills")],
        [InlineKeyboardButton("Projects", callback_data="edit_projects")],
        [InlineKeyboardButton("Certifications", callback_data="edit_certifications")],
        [InlineKeyboardButton("Generate AI Summary", callback_data="ai_summary")],
        [InlineKeyboardButton("Improve Grammar", callback_data="improve_grammar")],
        [InlineKeyboardButton("Done - Generate Resume", callback_data="generate_resume")],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirmation_keyboard():
    keyboard = [
        [InlineKeyboardButton("Yes, generate!", callback_data="confirm_generate")],
        [InlineKeyboardButton("No, let me edit", callback_data="edit_resume")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard():
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
