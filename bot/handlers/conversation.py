from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from bot.database.db import save_user_data, get_user_data, save_resume_record
from bot.services.pdf_service import build_resume
from bot.services.ai_service import (
    generate_resume_content, generate_summary, improve_grammar,
    suggest_skills, generate_cover_letter, check_ats_score,
    optimize_keywords, AI_AVAILABLE
)
from bot.utils.keyboards import (
    main_menu_keyboard, template_keyboard, job_role_keyboard,
    edit_section_keyboard, back_keyboard
)
from config import (
    WAITING_FULL_NAME, WAITING_EMAIL, WAITING_PHONE, WAITING_LOCATION,
    WAITING_OBJECTIVE, WAITING_EDUCATION, WAITING_EXPERIENCE,
    WAITING_SKILLS, WAITING_PROJECTS, WAITING_CERTIFICATIONS,
    WAITING_TEMPLATE, WAITING_JOB_ROLE, WAITING_EDIT_SECTION,
    WAITING_COVER_LETTER_JOB, WAITING_COVER_LETTER_COMPANY,
    WAITING_ATS_JOB_DESCRIPTION
)


user_data_store = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Welcome to Resume Bot, {user.first_name}!\n\n"
        "I'll help you create a professional ATS-optimized resume.",
        reply_markup=main_menu_keyboard()
    )


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    user_id = update.effective_user.id

    if action == "create_resume":
        user_data_store.pop(user_id, None)
        await query.edit_message_text("What is your full name?")
        return WAITING_FULL_NAME

    elif action == "edit_resume":
        existing = get_user_data(user_id)
        if not existing:
            await query.edit_message_text(
                "No existing resume found. Start by creating one!",
                reply_markup=back_keyboard()
            )
            return ConversationHandler.END

        user_data_store[user_id] = existing
        await query.edit_message_text(
            "Select a section to edit:",
            reply_markup=edit_section_keyboard()
        )
        return WAITING_EDIT_SECTION

    elif action == "cover_letter":
        existing = get_user_data(user_id)
        if not existing:
            await query.edit_message_text(
                "Create a resume first before generating a cover letter.",
                reply_markup=back_keyboard()
            )
            return ConversationHandler.END

        user_data_store[user_id] = existing
        await query.edit_message_text("What is the job title you're applying for?")
        return WAITING_COVER_LETTER_JOB

    elif action == "ats_checker":
        existing = get_user_data(user_id)
        if not existing:
            await query.edit_message_text(
                "Create a resume first to check ATS score.",
                reply_markup=back_keyboard()
            )
            return ConversationHandler.END

        user_data_store[user_id] = existing
        context.user_data["action_type"] = "ats_check"
        await query.edit_message_text(
            "Paste the job description to check your ATS score:"
        )
        return WAITING_ATS_JOB_DESCRIPTION

    elif action == "optimize_keywords":
        existing = get_user_data(user_id)
        if not existing:
            await query.edit_message_text(
                "Create a resume first to optimize keywords.",
                reply_markup=back_keyboard()
            )
            return ConversationHandler.END

        context.user_data["action_type"] = "optimize_keywords"
        user_data_store[user_id] = existing
        await query.edit_message_text(
            "Paste the job description to optimize your resume keywords:"
        )
        return WAITING_ATS_JOB_DESCRIPTION

    elif action == "suggest_skills":
        context.user_data["action_type"] = "suggest_skills"
        await query.edit_message_text(
            "Select your job role:",
            reply_markup=job_role_keyboard()
        )
        return WAITING_JOB_ROLE

    elif action == "main_menu":
        await query.edit_message_text(
            "What would you like to do?",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END


async def collect_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data_store:
        user_data_store[user_id] = {}
    user_data_store[user_id]["full_name"] = update.message.text.strip()
    await update.message.reply_text("Great! Now, what is your email address?")
    return WAITING_EMAIL


async def collect_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email = update.message.text.strip()
    if "@" not in email or "." not in email:
        await update.message.reply_text("Please enter a valid email address (e.g., name@example.com):")
        return WAITING_EMAIL
    user_data_store[user_id]["email"] = email
    await update.message.reply_text("What is your phone number?")
    return WAITING_PHONE


async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["phone"] = update.message.text.strip()
    await update.message.reply_text("Where are you located? (City, Country)")
    return WAITING_LOCATION


async def collect_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["location"] = update.message.text.strip()
    await update.message.reply_text(
        "What is your career objective? (A brief 2-3 sentence summary)"
    )
    return WAITING_OBJECTIVE


async def collect_objective(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id]["career_objective"] = update.message.text.strip()
    await update.message.reply_text(
        "Enter your education details (one entry per line):\n\n"
        "Format: Degree | Institution | Year | GPA (optional)\n"
        "Example: B.Sc. Computer Science | MIT | 2024 | 3.8\n\n"
        "Enter each education on a new line. Send /skip if none."
    )
    return WAITING_EDUCATION


async def collect_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "/cancel":
        return await cancel(update, context)
    if text == "/skip":
        user_data_store[user_id]["education"] = []
    else:
        entries = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                parts = [p.strip() for p in line.split("|")]
                entry = {
                    "degree": parts[0] if len(parts) > 0 else "",
                    "school": parts[1] if len(parts) > 1 else "",
                    "year": parts[2] if len(parts) > 2 else "",
                    "gpa": parts[3] if len(parts) > 3 else "",
                }
                entries.append(entry)
        user_data_store[user_id]["education"] = entries

    await update.message.reply_text(
        "Enter your work experience (one entry per block):\n\n"
        "Format:\n"
        "Job Title | Company | Duration\n"
        "- Responsibility 1\n"
        "- Responsibility 2\n\n"
        "Separate multiple jobs with ---\n"
        "Send /skip if none."
    )
    return WAITING_EXPERIENCE


async def collect_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "/cancel":
        return await cancel(update, context)
    if text == "/skip":
        user_data_store[user_id]["work_experience"] = []
    else:
        entries = []
        blocks = text.split("---")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            header = lines[0].strip()
            parts = [p.strip() for p in header.split("|")]
            entry = {
                "title": parts[0] if len(parts) > 0 else "",
                "company": parts[1] if len(parts) > 1 else "",
                "duration": parts[2] if len(parts) > 2 else "",
                "description": []
            }
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("-"):
                    entry["description"].append(line[1:].strip())
            entries.append(entry)
        user_data_store[user_id]["work_experience"] = entries

    await update.message.reply_text(
        "Enter your skills (comma-separated):\n"
        "Example: Python, JavaScript, SQL, Project Management, Team Leadership\n"
        "Send /skip if none."
    )
    return WAITING_SKILLS


async def collect_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "/cancel":
        return await cancel(update, context)
    if text == "/skip":
        user_data_store[user_id]["skills"] = []
    else:
        user_data_store[user_id]["skills"] = [s.strip() for s in text.split(",")]

    await update.message.reply_text(
        "Enter your projects (one per block):\n\n"
        "Format:\n"
        "Project Name | Technologies\n"
        "Description of the project\n\n"
        "Separate multiple projects with ---\n"
        "Send /skip if none."
    )
    return WAITING_PROJECTS


async def collect_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "/cancel":
        return await cancel(update, context)
    if text == "/skip":
        user_data_store[user_id]["projects"] = []
    else:
        entries = []
        blocks = text.split("---")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            header = lines[0].strip()
            parts = [p.strip() for p in header.split("|")]
            entry = {
                "name": parts[0] if len(parts) > 0 else "",
                "technologies": parts[1] if len(parts) > 1 else "",
                "description": ""
            }
            if len(lines) > 1:
                entry["description"] = "\n".join(lines[1:]).strip()
            entries.append(entry)
        user_data_store[user_id]["projects"] = entries

    await update.message.reply_text(
        "Enter your certifications (one per line):\n\n"
        "Format: Certification Name | Issuer | Year\n"
        "Example: AWS Solutions Architect | Amazon | 2024\n"
        "Send /skip if none."
    )
    return WAITING_CERTIFICATIONS


async def collect_certifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "/cancel":
        return await cancel(update, context)
    if text == "/skip":
        user_data_store[user_id]["certifications"] = []
    else:
        entries = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                parts = [p.strip() for p in line.split("|")]
                entry = {
                    "name": parts[0] if len(parts) > 0 else "",
                    "issuer": parts[1] if len(parts) > 1 else "",
                    "year": parts[2] if len(parts) > 2 else "",
                }
                entries.append(entry)
        user_data_store[user_id]["certifications"] = entries

    save_user_data(user_id, update.effective_user.username or "", user_data_store[user_id])

    await update.message.reply_text(
        "Excellent! Now select a job role for optimization:",
        reply_markup=job_role_keyboard()
    )
    return WAITING_JOB_ROLE


async def handle_job_role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action_type = context.user_data.get("action_type", "create_resume")
    role_key = query.data.replace("jobrole_", "")
    user_id = update.effective_user.id

    if action_type == "suggest_skills":
        await query.edit_message_text("Generating skill suggestions...")
        skills = suggest_skills(role_key)

        if isinstance(skills, list):
            await query.edit_message_text(
                f"Suggested skills for your role:\n\n{', '.join(skills)}\n\n"
                "Use these to update your resume!",
                reply_markup=back_keyboard()
            )
        else:
            await query.edit_message_text(
                "Error generating skills. Please try again.",
                reply_markup=back_keyboard()
            )
        return ConversationHandler.END

    role_name = role_key if role_key == "general" else role_key

    if user_id in user_data_store:
        user_data_store[user_id]["job_role"] = role_name

    context.user_data["action_type"] = "create_resume"
    await query.edit_message_text(
        "Now choose a resume template:",
        reply_markup=template_keyboard()
    )
    return WAITING_TEMPLATE


async def handle_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    template = query.data.replace("template_", "")

    if user_id in user_data_store:
        user_data_store[user_id]["selected_template"] = template
        save_user_data(user_id, update.effective_user.username or "", user_data_store[user_id])

    if AI_AVAILABLE:
        await query.edit_message_text("Generating AI-enhanced resume content...")
    else:
        await query.edit_message_text("Generating resume (add OPENAI_API_KEY to .env for AI enhancements)...")

    enhanced = generate_resume_content(
        user_data_store.get(user_id, {}),
        user_data_store.get(user_id, {}).get("job_role")
    )

    await query.edit_message_text("Generating PDF resume...")

    output_file = f"resume_{user_id}.pdf"
    pdf_path = build_resume(
        user_data_store[user_id],
        enhanced_data=enhanced,
        template=template,
        output_filename=output_file
    )

    save_resume_record(user_id, template, user_data_store[user_id].get("job_role", ""), pdf_path)

    with open(pdf_path, "rb") as f:
        await query.message.reply_document(
            document=f,
            filename="Resume.pdf",
            caption="Your professional resume is ready!",
        )

    await query.message.reply_text(
        "What would you like to do next?",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


async def handle_edit_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    section = query.data
    section_map = {
        "edit_full_name": ("full_name", "What is your updated full name?"),
        "edit_email": ("email", "What is your updated email?"),
        "edit_phone": ("phone", "What is your updated phone number?"),
        "edit_location": ("location", "What is your updated location?"),
        "edit_career_objective": ("career_objective", "What is your updated career objective?"),
        "edit_education": ("education", "Enter updated education details:"),
        "edit_work_experience": ("work_experience", "Enter updated work experience:"),
        "edit_skills": ("skills", "Enter updated skills (comma-separated):"),
        "edit_projects": ("projects", "Enter updated project details:"),
        "edit_certifications": ("certifications", "Enter updated certifications:"),
    }

    if section == "ai_summary":
        msg = "Generating professional summary..." if AI_AVAILABLE else "Using your provided objective (add OPENAI_API_KEY for AI-generated summary)..."
        await query.edit_message_text(msg)
        summary = generate_summary(
            user_data_store.get(user_id, {}),
            user_data_store.get(user_id, {}).get("job_role")
        )
        if user_id in user_data_store:
            user_data_store[user_id]["career_objective"] = summary
            save_user_data(user_id, update.effective_user.username or "", user_data_store[user_id])
        await query.edit_message_text(
            f"Generated Summary:\n\n{summary}\n\n"
            "You can edit this or continue.",
            reply_markup=edit_section_keyboard()
        )
        return WAITING_EDIT_SECTION

    elif section == "improve_grammar":
        await query.edit_message_text("Send the text you want to improve (e.g., your career objective or experience):")
        context.user_data["awaiting_grammar_improve"] = True
        return WAITING_EDIT_SECTION

    elif section == "generate_resume":
        await query.edit_message_text(
            "Select template:",
            reply_markup=template_keyboard()
        )
        return WAITING_TEMPLATE

    if section in section_map:
        field_name, prompt = section_map[section]
        context.user_data["editing_field"] = field_name

        if field_name in ["education", "work_experience", "projects", "certifications", "skills"]:
            current = user_data_store.get(user_id, {}).get(field_name, [])
            if current:
                await query.edit_message_text(
                    f"{prompt}\n\nCurrent value: {current}",
                    reply_markup=None
                )
            else:
                await query.edit_message_text(prompt, reply_markup=None)
        else:
            current = user_data_store.get(user_id, {}).get(field_name, "Not set")
            await query.edit_message_text(
                f"{prompt}\n\nCurrent: {current}",
                reply_markup=None
            )

    return WAITING_EDIT_SECTION


async def handle_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    field = context.user_data.get("editing_field")

    if context.user_data.get("awaiting_grammar_improve"):
        await update.message.reply_text("Improving grammar...")
        improved = improve_grammar(update.message.text.strip())
        if user_id in user_data_store:
            user_data_store[user_id]["career_objective"] = improved
            save_user_data(user_id, update.effective_user.username or "", user_data_store[user_id])
        await update.message.reply_text(
            f"Improved text:\n\n{improved}\n\nSaved to career objective.",
            reply_markup=edit_section_keyboard()
        )
        context.user_data["awaiting_grammar_improve"] = False
        return WAITING_EDIT_SECTION

    if field and user_id in user_data_store:
        text = update.message.text.strip()
        if field == "skills":
            user_data_store[user_id][field] = [s.strip() for s in text.split(",")]
        elif field in ("education", "work_experience", "projects", "certifications"):
            user_data_store[user_id][field] = text
        else:
            user_data_store[user_id][field] = text
        save_user_data(user_id, update.effective_user.username or "", user_data_store[user_id])

    await update.message.reply_text(
        "Updated! What else would you like to edit?",
        reply_markup=edit_section_keyboard()
    )
    return WAITING_EDIT_SECTION


async def handle_ats_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    job_description = update.message.text.strip()
    action_type = context.user_data.get("action_type", "ats_check")

    user_data = user_data_store.get(user_id, {})
    resume_text = f"""
{user_data.get('full_name', '')}
{user_data.get('email', '')} | {user_data.get('phone', '')} | {user_data.get('location', '')}

Objective: {user_data.get('career_objective', '')}

Skills: {', '.join(user_data.get('skills', []))}

Education: {user_data.get('education', [])}

Experience: {user_data.get('work_experience', [])}

Projects: {user_data.get('projects', [])}

Certifications: {user_data.get('certifications', [])}
"""

    if action_type == "optimize_keywords":
        await update.message.reply_text("Optimizing keywords for your resume...")
        result = optimize_keywords(resume_text, job_description)
        if "error" in result:
            await update.message.reply_text(f"Error: {result['error']}")
        else:
            keywords_added = result.get("keywords_added", [])
            recommendations = result.get("recommendations", [])
            response = "Keyword Optimization Complete\n\n"
            if keywords_added:
                response += "Keywords to Add:\n" + ", ".join(keywords_added) + "\n\n"
            if recommendations:
                response += "Recommendations:\n" + "\n".join(f"- {r}" for r in recommendations)
            await update.message.reply_text(response, reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("Analyzing resume against job description...")
        result = check_ats_score(resume_text, job_description)
        if "error" in result:
            await update.message.reply_text(f"Error: {result['error']}")
        else:
            score = result.get("score", 0)
            matched = result.get("matched_keywords", [])
            missing = result.get("missing_keywords", [])
            suggestions = result.get("suggestions", [])
            strengths = result.get("strengths", [])

            response = f"ATS Score: {score}/100\n\n"
            if strengths:
                response += "Strengths:\n" + "\n".join(f"- {s}" for s in strengths) + "\n\n"
            if matched:
                response += "Matched Keywords:\n" + ", ".join(matched) + "\n\n"
            if missing:
                response += "Missing Keywords:\n" + ", ".join(missing) + "\n\n"
            if suggestions:
                response += "Suggestions:\n" + "\n".join(f"- {s}" for s in suggestions)

            await update.message.reply_text(response, reply_markup=main_menu_keyboard())

    return ConversationHandler.END


async def handle_cover_letter_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cover_letter_job"] = update.message.text.strip()
    await update.message.reply_text("What is the company name?")
    return WAITING_COVER_LETTER_COMPANY


async def handle_cover_letter_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    company = update.message.text.strip()
    job_title = context.user_data.get("cover_letter_job", "")

    await update.message.reply_text("Generating cover letter...")

    user_data = user_data_store.get(user_id, {})
    letter = generate_cover_letter(user_data, job_title, company)

    await update.message.reply_text(
        f"Cover Letter for {job_title} at {company}\n\n{letter}",
        reply_markup=back_keyboard()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Cancelled. Come back anytime!",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


def get_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(main_menu_callback, pattern="^(create_resume|edit_resume|cover_letter|ats_checker|optimize_keywords|suggest_skills|main_menu)$"),
        ],
        states={
            WAITING_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_full_name)],
            WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            WAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            WAITING_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_location)],
            WAITING_OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_objective)],
            WAITING_EDUCATION: [MessageHandler(filters.TEXT, collect_education)],
            WAITING_EXPERIENCE: [MessageHandler(filters.TEXT, collect_experience)],
            WAITING_SKILLS: [MessageHandler(filters.TEXT, collect_skills)],
            WAITING_PROJECTS: [MessageHandler(filters.TEXT, collect_projects)],
            WAITING_CERTIFICATIONS: [MessageHandler(filters.TEXT, collect_certifications)],
            WAITING_JOB_ROLE: [CallbackQueryHandler(handle_job_role_callback, pattern="^jobrole_")],
            WAITING_TEMPLATE: [CallbackQueryHandler(handle_template_selection, pattern="^template_")],
            WAITING_EDIT_SECTION: [
                CallbackQueryHandler(handle_edit_section),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_text),
            ],
            WAITING_COVER_LETTER_JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cover_letter_job)],
            WAITING_COVER_LETTER_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cover_letter_company)],
            WAITING_ATS_JOB_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ats_action)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
