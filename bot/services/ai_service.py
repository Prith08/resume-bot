import json
from config import OPENAI_API_KEY

AI_AVAILABLE = bool(OPENAI_API_KEY) and OPENAI_API_KEY != "your_openai_api_key_here"

client = None
if AI_AVAILABLE:
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)


def _build_basic_summary(user_data, job_role=None):
    name = user_data.get("full_name", "")
    skills = ", ".join(user_data.get("skills", [])) or "relevant skills"
    return f"Experienced professional with expertise in {skills}. Dedicated to delivering high-quality results and driving organizational success."


def _build_basic_skills(user_data, job_role=None):
    return user_data.get("skills", [])


def generate_resume_content(user_data, job_role=None):
    if not AI_AVAILABLE:
        return {
            "summary": _build_basic_summary(user_data, job_role),
            "skills": user_data.get("skills", []),
            "education": user_data.get("education", []),
            "experience": user_data.get("work_experience", []),
            "projects": user_data.get("projects", []),
            "certifications": user_data.get("certifications", []),
        }

    system_prompt = """You are a professional resume writer. Generate polished, ATS-friendly resume content.
Return the response as a JSON object with these fields:
- summary: professional summary (2-3 sentences)
- skills: categorized skills list
- education: formatted education details
- experience: improved work experience descriptions with action verbs
- projects: enhanced project descriptions
- certifications: formatted certifications

Make the content professional, concise, and achievement-focused."""

    user_prompt = f"""Create resume content for:
Name: {user_data.get('full_name')}
Career Objective: {user_data.get('career_objective')}
Education: {json.dumps(user_data.get('education', []))}
Work Experience: {json.dumps(user_data.get('work_experience', []))}
Skills: {json.dumps(user_data.get('skills', []))}
Projects: {json.dumps(user_data.get('projects', []))}
Certifications: {json.dumps(user_data.get('certifications', []))}
Job Role: {job_role or 'General Professional'}

Improve all content with strong action verbs, quantified achievements, and ATS keywords."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "summary": _build_basic_summary(user_data, job_role),
            "skills": user_data.get("skills", []),
            "education": user_data.get("education", []),
            "experience": user_data.get("work_experience", []),
            "projects": user_data.get("projects", []),
            "certifications": user_data.get("certifications", []),
        }


def generate_summary(user_data, job_role=None):
    if not AI_AVAILABLE:
        return _build_basic_summary(user_data, job_role)

    prompt = f"""Write a professional resume summary (2-3 sentences) for:
Name: {user_data.get('full_name')}
Objective: {user_data.get('career_objective')}
Skills: {', '.join(user_data.get('skills', []))}
Experience: {json.dumps(user_data.get('work_experience', []))}
Job Role: {job_role or 'General'}
Make it compelling and tailored to the role."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return _build_basic_summary(user_data, job_role)


def improve_grammar(text):
    if not AI_AVAILABLE:
        return text

    prompt = f"""Fix grammar, spelling, and improve wording for this resume text:
"{text}"
Return the improved version only. Keep it professional and concise."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert editor. Fix grammar and improve wording."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception:
        return text


def suggest_skills(job_role):
    if not AI_AVAILABLE:
        fallback = {
            "software_engineer": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "Docker", "AWS", "REST APIs", "System Design", "Problem Solving", "Teamwork", "Agile"],
            "network_engineer": ["TCP/IP", "DNS", "DHCP", "Routing", "Switching", "Firewalls", "VPN", "Cisco IOS", "Network Security", "Wireshark", "Troubleshooting", "SDN"],
            "data_analyst": ["SQL", "Python", "R", "Excel", "Tableau", "Power BI", "Statistics", "Data Cleaning", "Data Visualization", "Pandas", "Business Intelligence"],
            "accountant": ["GAAP", "Financial Reporting", "QuickBooks", "Excel", "Tax Preparation", "Auditing", "Reconciliation", "Accounts Payable", "Accounts Receivable", "SAP"],
            "teacher": ["Lesson Planning", "Classroom Management", "Curriculum Development", "Assessment", "Differentiated Instruction", "Educational Technology", "Communication", "Patience", "Creativity"],
        }.get(job_role, ["Communication", "Problem Solving", "Teamwork", "Time Management", "Leadership", "Microsoft Office", "Analytical Skills"])
        return fallback

    prompt = f"""List 15-20 relevant technical and soft skills for a {job_role} position.
Return as a JSON array of strings. Include both hard and soft skills.
Example: ["Python", "SQL", "Problem Solving", "Team Leadership"]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a career advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("skills", result) if isinstance(result, dict) else result
    except Exception:
        return ["Communication", "Problem Solving", "Teamwork", "Time Management"]


def generate_cover_letter(user_data, job_title, company):
    name = user_data.get("full_name", "")
    email = user_data.get("email", "")
    skills = ", ".join(user_data.get("skills", []))
    phone = user_data.get("phone", "")

    if not AI_AVAILABLE:
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With my background and skills in {skills}, I am confident in my ability to contribute to your team.

Throughout my career, I have developed strong expertise in my field. My experience includes {user_data.get('work_experience', [])}.

I would welcome the opportunity to discuss how my skills align with {company}'s goals. Thank you for considering my application.

Best regards,
{name}
{email} | {phone}"""

    prompt = f"""Write a professional cover letter for {name} applying for {job_title} at {company}.

Background:
- Email: {email}
- Phone: {phone}
- Skills: {skills}
- Experience: {json.dumps(user_data.get('work_experience', []))}
- Education: {json.dumps(user_data.get('education', []))}

Make it specific to the role and company. Use professional formatting."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With my background and skills in {skills}, I am confident in my ability to contribute to your team.

I would welcome the opportunity to discuss how my skills align with {company}'s goals.

Best regards,
{name}
{email} | {phone}"""


def check_ats_score(resume_text, job_description):
    if not AI_AVAILABLE:
        return {
            "score": 50,
            "matched_keywords": ["resume_submitted"],
            "missing_keywords": [],
            "suggestions": ["Add an OpenAI API key to .env for AI-powered ATS analysis"],
            "strengths": ["Resume submitted for review"]
        }

    prompt = f"""Analyze this resume against the job description and provide an ATS score.

Resume:
{resume_text}

Job Description:
{job_description}

Return JSON with:
- score: integer 0-100
- matched_keywords: list of matched keywords
- missing_keywords: list of missing important keywords
- suggestions: list of improvement suggestions
- strengths: list of resume strengths"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an ATS optimization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"error": "ATS analysis unavailable. Check your OpenAI API key."}


def optimize_keywords(resume_text, job_description):
    if not AI_AVAILABLE:
        return {
            "keywords_added": [],
            "recommendations": ["Add an OpenAI API key to .env for AI-powered keyword optimization"]
        }

    prompt = f"""Optimize this resume for ATS by suggesting keyword improvements.

Resume:
{resume_text}

Job Description:
{job_description}

Return JSON with:
- optimized_resume: improved resume text with keywords naturally integrated
- keywords_added: list of keywords added
- recommendations: list of optimization tips"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an ATS optimization specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"error": "Keyword optimization unavailable. Check your OpenAI API key."}
