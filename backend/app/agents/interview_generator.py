import uuid


def generate_interview_questions(resume) -> list[dict]:
    questions = []
    categories = ["Behavioral", "Technical", "AI", "Scenario-based"]

    base_questions = [
        ("Behavioral", "Tell me about a time you improved a cross-functional workflow. What was the measurable outcome?"),
        ("Behavioral", "Describe a situation where you had to standardize processes across multiple teams."),
        ("Technical", "Walk me through how you would design a documentation system for a growing product team."),
        ("Technical", "How do you approach resource allocation when engineering bandwidth is constrained?"),
        ("AI", "You mentioned AI-assisted workflows. Describe the exact prompting strategy you used."),
        ("AI", "How would you evaluate whether an LLM-based solution is appropriate for a given business problem?"),
        ("AI", "Explain the difference between RAG and fine-tuning. When would you choose each?"),
        ("Scenario-based", "Your team needs to reduce documentation lookup time by 50%. How would you approach this?"),
        ("Scenario-based", "A stakeholder wants to 'add AI' to every process. How do you prioritize?"),
        ("Behavioral", "Tell me about a project where data-driven decision making changed an outcome."),
        ("Technical", "How do you measure the success of process documentation?"),
        ("AI", "Describe a workflow you automated. What tools did you use and what were the limitations?"),
        ("AI", "How do you ensure AI-generated content maintains accuracy and brand consistency?"),
        ("Scenario-based", "You have 2 weeks to demonstrate AI value to leadership. What's your plan?"),
        ("Behavioral", "How do you balance speed of delivery with documentation quality?"),
    ]

    for category, q in base_questions:
        questions.append({
            "id": str(uuid.uuid4()),
            "category": category,
            "question": q,
        })

    return questions[:15]
