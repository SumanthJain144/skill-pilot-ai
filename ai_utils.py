import os
import dspy
from openai import AzureOpenAI

# Step 1: Configure Azure OpenAI (reuse logic from career_advisor.py)
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

dspy.configure(lm=(
    dspy.LM(
        model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
))

LEVELS = ['Entry', 'Mid', 'Senior', 'Expert']

SYSTEM_PROMPT = """
You are an expert career advisor for software engineers. Given a user's self-assessed skill levels for a specific designation, deduce their current level (Entry, Mid, Senior, Expert) and recommend a career path to the next level. Use the provided skills and certifications from the competency framework. If the user is already at Expert, suggest exploring other designations or upskilling in trending areas.
"""

def assess_and_recommend(
    designation: str,
    skills_dict,
    user_skill_ratings,
    certifications
):
    """
    Uses dspy LLM (Azure OpenAI) to assess the user's level and recommend a career path.
    Returns (verdict, recommendation).
    """
    # Prepare the prompt
    skill_ratings_str = "\n".join([f"{skill}: {level}" for skill, level in user_skill_ratings.items()])
    certs_str = ", ".join(certifications)
    prompt = f"""
Designation: {designation}
User Skill Ratings:\n{skill_ratings_str}
Available Certifications: {certs_str}

1. What is the user's current level (Entry, Mid, Senior, Expert)?
2. What is the recommended career path to reach the next level? Summarise the skills to focus in table and certifications to pursue.
If already at Expert, suggest upskilling or exploring other designations.
"""
    response = dspy.settings.lm(SYSTEM_PROMPT + "\n" + prompt)
    # Ensure response is a string (dspy may return a list)
    if isinstance(response, list):
        response = "\n".join(str(r) for r in response)
    lines = response.strip().split('\n')
    verdict = lines[0] if lines else ""
    recommendation = "\n".join(lines[1:]) if len(lines) > 1 else ""
    return verdict, recommendation
