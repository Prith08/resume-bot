from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

OUTPUT_DIR = "resumes"
os.makedirs(OUTPUT_DIR, exist_ok=True)


THEMES = {
    "modern": {
        "primary": "#2C3E50",
        "secondary": "#3498DB",
        "accent": "#1ABC9C",
        "text": "#333333",
        "light": "#ECF0F1",
    },
    "professional": {
        "primary": "#1A237E",
        "secondary": "#283593",
        "accent": "#3949AB",
        "text": "#212121",
        "light": "#E8EAF6",
    },
    "creative": {
        "primary": "#E91E63",
        "secondary": "#9C27B0",
        "accent": "#673AB7",
        "text": "#424242",
        "light": "#F3E5F5",
    },
    "executive": {
        "primary": "#263238",
        "secondary": "#37474F",
        "accent": "#455A64",
        "text": "#212121",
        "light": "#ECEFF1",
    },
    "technical": {
        "primary": "#004D40",
        "secondary": "#00695C",
        "accent": "#00897B",
        "text": "#263238",
        "light": "#E0F2F1",
    },
}


def create_styles(template="modern"):
    theme = THEMES.get(template, THEMES["modern"])
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="HeaderName",
        fontSize=24,
        textColor=HexColor(theme["primary"]),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="ContactInfo",
        fontSize=10,
        textColor=HexColor(theme["secondary"]),
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        textColor=HexColor(theme["primary"]),
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="SubSection",
        fontSize=11,
        textColor=HexColor(theme["secondary"]),
        fontName="Helvetica-Bold",
        spaceBefore=6,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10,
        textColor=HexColor(theme["text"]),
        fontName="Helvetica",
        spaceAfter=4,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="BulletText",
        fontSize=10,
        textColor=HexColor(theme["text"]),
        fontName="Helvetica",
        leftIndent=20,
        spaceAfter=2,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name="SkillTag",
        fontSize=9,
        textColor=HexColor(theme["primary"]),
        fontName="Helvetica",
        backColor=HexColor(theme["light"]),
    ))

    return styles


def build_resume(user_data, enhanced_data=None, template="modern", output_filename="resume.pdf"):
    filepath = os.path.join(OUTPUT_DIR, output_filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = create_styles(template)
    theme = THEMES.get(template, THEMES["modern"])
    story = []

    # Header - Name
    story.append(Paragraph(user_data.get("full_name", "Your Name"), styles["HeaderName"]))

    # Contact Info
    contact_parts = []
    if user_data.get("email"):
        contact_parts.append(user_data["email"])
    if user_data.get("phone"):
        contact_parts.append(user_data["phone"])
    if user_data.get("location"):
        contact_parts.append(user_data["location"])
    contact_line = " | ".join(contact_parts)
    story.append(Paragraph(contact_line, styles["ContactInfo"]))

    # Separator
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor(theme["primary"])))
    story.append(Spacer(1, 8))

    # Professional Summary
    summary = enhanced_data.get("summary", "") if enhanced_data else ""
    if not summary:
        summary = user_data.get("career_objective", "")

    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))
        story.append(Paragraph(summary, styles["BodyText2"]))

    # Skills
    skills = enhanced_data.get("skills", user_data.get("skills", [])) if enhanced_data else user_data.get("skills", [])
    if skills:
        story.append(Paragraph("SKILLS", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))

        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                story.append(Paragraph(f"<b>{category}:</b> {', '.join(skill_list)}", styles["BulletText"]))
        elif isinstance(skills, list):
            skill_text = " | ".join(skills)
            story.append(Paragraph(skill_text, styles["BulletText"]))

    # Education
    education = enhanced_data.get("education", user_data.get("education", [])) if enhanced_data else user_data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))

        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree", "")
                school = edu.get("school", edu.get("institution", ""))
                year = edu.get("year", edu.get("graduation_year", ""))
                gpa = edu.get("gpa", "")
                line = f"<b>{degree}</b> - {school}"
                if year:
                    line += f" ({year})"
                story.append(Paragraph(line, styles["SubSection"]))
                if gpa:
                    story.append(Paragraph(f"GPA: {gpa}", styles["BulletText"]))
            else:
                story.append(Paragraph(str(edu), styles["BodyText2"]))

    # Work Experience
    experience = enhanced_data.get("experience", user_data.get("work_experience", [])) if enhanced_data else user_data.get("work_experience", [])
    if experience:
        story.append(Paragraph("WORK EXPERIENCE", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))

        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title", exp.get("position", ""))
                company = exp.get("company", "")
                duration = exp.get("duration", exp.get("period", ""))
                description = exp.get("description", exp.get("responsibilities", []))

                header = f"<b>{title}</b>"
                if company:
                    header += f" at {company}"
                if duration:
                    header += f" ({duration})"
                story.append(Paragraph(header, styles["SubSection"]))

                if isinstance(description, list):
                    for desc in description:
                        story.append(Paragraph(f"• {desc}", styles["BulletText"]))
                elif description:
                    story.append(Paragraph(str(description), styles["BulletText"]))
            else:
                story.append(Paragraph(str(exp), styles["BodyText2"]))

    # Projects
    projects = enhanced_data.get("projects", user_data.get("projects", [])) if enhanced_data else user_data.get("projects", [])
    if projects:
        story.append(Paragraph("PROJECTS", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))

        for project in projects:
            if isinstance(project, dict):
                name = project.get("name", project.get("title", ""))
                desc = project.get("description", "")
                tech = project.get("technologies", project.get("tech_stack", ""))

                line = f"<b>{name}</b>"
                if tech:
                    line += f" | {tech}"
                story.append(Paragraph(line, styles["SubSection"]))
                if desc:
                    story.append(Paragraph(desc, styles["BulletText"]))
            else:
                story.append(Paragraph(str(project), styles["BodyText2"]))

    # Certifications
    certifications = enhanced_data.get("certifications", user_data.get("certifications", [])) if enhanced_data else user_data.get("certifications", [])
    if certifications:
        story.append(Paragraph("CERTIFICATIONS", styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["secondary"])))
        story.append(Spacer(1, 4))

        for cert in certifications:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                issuer = cert.get("issuer", cert.get("organization", ""))
                year = cert.get("year", cert.get("date", ""))
                line = f"• {name}"
                if issuer:
                    line += f" - {issuer}"
                if year:
                    line += f" ({year})"
                story.append(Paragraph(line, styles["BulletText"]))
            else:
                story.append(Paragraph(f"• {cert}", styles["BulletText"]))

    doc.build(story)
    return filepath


def build_cover_letter_pdf(letter_text, output_filename="cover_letter.pdf"):
    filepath = os.path.join(OUTPUT_DIR, output_filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()
    story = []

    for paragraph in letter_text.split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["Normal"]))
            story.append(Spacer(1, 12))

    doc.build(story)
    return filepath
