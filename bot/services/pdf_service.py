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
        fontSize=26,
        textColor=HexColor(theme["primary"]),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name="ContactInfo",
        fontSize=10,
        textColor=HexColor(theme["text"]),
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=12,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="ContactLink",
        fontSize=10,
        textColor=HexColor(theme["secondary"]),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=13,
        textColor=HexColor(theme["primary"]),
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=4,
        leading=16,
    ))

    styles.add(ParagraphStyle(
        name="SubSection",
        fontSize=11,
        textColor=HexColor(theme["secondary"]),
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=2,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10,
        textColor=HexColor(theme["text"]),
        fontName="Helvetica",
        spaceAfter=4,
        leading=15,
    ))

    styles.add(ParagraphStyle(
        name="BulletText",
        fontSize=10,
        textColor=HexColor(theme["text"]),
        fontName="Helvetica",
        leftIndent=20,
        spaceAfter=2,
        leading=14,
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

    story.append(Spacer(1, 6))

    story.append(Paragraph(user_data.get("full_name", "Your Name"), styles["HeaderName"]))

    contact_parts = []
    if user_data.get("email"):
        contact_parts.append(f'<font color="{theme["secondary"]}">{user_data["email"]}</font>')
    if user_data.get("phone"):
        contact_parts.append(f'<font color="{theme["secondary"]}">{user_data["phone"]}</font>')
    if user_data.get("location"):
        contact_parts.append(user_data["location"])

    if contact_parts:
        contact_line = "  •  ".join(contact_parts)
        story.append(Paragraph(contact_line, styles["ContactInfo"]))

    story.append(HRFlowable(width="70%", thickness=2, color=HexColor(theme["primary"]), spaceAfter=4))
    story.append(Spacer(1, 6))

    def add_section(title):
        story.append(Paragraph(title, styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor(theme["light"])))
        story.append(Spacer(1, 4))

    summary = enhanced_data.get("summary", "") if enhanced_data else ""
    if not summary:
        summary = user_data.get("career_objective", "")
    if summary:
        add_section("PROFESSIONAL SUMMARY")
        story.append(Paragraph(summary, styles["BodyText2"]))

    skills = enhanced_data.get("skills", user_data.get("skills", [])) if enhanced_data else user_data.get("skills", [])
    if skills:
        add_section("SKILLS")
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                story.append(Paragraph(f"<b>{category}:</b>  {', '.join(skill_list)}", styles["BodyText2"]))
        elif isinstance(skills, list):
            cols = 2
            mid = (len(skills) + 1) // 2
            left = skills[:mid]
            right = skills[mid:]
            skill_data = []
            for i in range(max(len(left), len(right))):
                l = left[i] if i < len(left) else ""
                r = right[i] if i < len(right) else ""
                skill_data.append((l, r))
            t = Table(skill_data, colWidths=[doc.width/2.2, doc.width/2.2])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (-1, -1), HexColor(theme["text"])),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)

    education = enhanced_data.get("education", user_data.get("education", [])) if enhanced_data else user_data.get("education", [])
    if education:
        add_section("EDUCATION")
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree", "")
                school = edu.get("school", edu.get("institution", ""))
                year = edu.get("year", edu.get("graduation_year", ""))
                gpa = edu.get("gpa", "")
                line = f"<b>{degree}</b>"
                if school:
                    line += f"  —  {school}"
                if year:
                    line += f"  ({year})"
                story.append(Paragraph(line, styles["SubSection"]))
                if gpa:
                    story.append(Paragraph(f"GPA: {gpa}", styles["BulletText"]))
            else:
                story.append(Paragraph(str(edu), styles["BodyText2"]))

    experience = enhanced_data.get("experience", user_data.get("work_experience", [])) if enhanced_data else user_data.get("work_experience", [])
    if experience:
        add_section("WORK EXPERIENCE")
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title", exp.get("position", ""))
                company = exp.get("company", "")
                duration = exp.get("duration", exp.get("period", ""))
                description = exp.get("description", exp.get("responsibilities", []))

                header = f"<b>{title}</b>"
                if company:
                    header += f"  —  {company}"
                if duration:
                    header += f"  ({duration})"
                story.append(Paragraph(header, styles["SubSection"]))

                if isinstance(description, list):
                    for desc in description:
                        story.append(Paragraph(f"•  {desc}", styles["BulletText"]))
                elif description:
                    story.append(Paragraph(f"•  {description}", styles["BulletText"]))
            else:
                story.append(Paragraph(str(exp), styles["BodyText2"]))

    projects = enhanced_data.get("projects", user_data.get("projects", [])) if enhanced_data else user_data.get("projects", [])
    if projects:
        add_section("PROJECTS")
        for project in projects:
            if isinstance(project, dict):
                name = project.get("name", project.get("title", ""))
                desc = project.get("description", "")
                tech = project.get("technologies", project.get("tech_stack", ""))
                line = f"<b>{name}</b>"
                if tech:
                    line += f"  —  {tech}"
                story.append(Paragraph(line, styles["SubSection"]))
                if desc:
                    story.append(Paragraph(desc, styles["BulletText"]))
            else:
                story.append(Paragraph(str(project), styles["BodyText2"]))

    certifications = enhanced_data.get("certifications", user_data.get("certifications", [])) if enhanced_data else user_data.get("certifications", [])
    if certifications:
        add_section("CERTIFICATIONS")
        for cert in certifications:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                issuer = cert.get("issuer", cert.get("organization", ""))
                year = cert.get("year", cert.get("date", ""))
                line = f"•  {name}"
                if issuer:
                    line += f"  —  {issuer}"
                if year:
                    line += f"  ({year})"
                story.append(Paragraph(line, styles["BulletText"]))
            else:
                story.append(Paragraph(f"•  {cert}", styles["BulletText"]))

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
