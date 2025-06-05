import os
import dspy

# Step 1: Configure Azure OpenAI
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

dspy.configure(lm=(
    dspy.LM(
        model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Replace with your actual deployment ID
    )
))

# Step 2: Define Career Advisor Signature & Module
class CareerPathSignature(dspy.Signature):
    current_designation = dspy.InputField(desc="The employee's current job title")
    desired_designation = dspy.InputField(desc="The desired next job title")
    retrieved_skills = dspy.InputField(desc="Relevant skills and growth areas")
    career_suggestion = dspy.OutputField(desc="Suggested growth path to move from current to desired role")

class CareerAdvisor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(CareerPathSignature)

    def forward(self, current_designation, desired_designation, retrieved_skills):
        return self.predict(
            current_designation=current_designation,
            retrieved_skills=retrieved_skills,
            desired_designation=desired_designation
        )

    def enhance_performance_metrics(self, designation, base_metrics, skills):
        prompt = (
            f"Given the designation '{designation}', the following base performance metrics: '{base_metrics}', "
            f"and these relevant skills: '{skills}', suggest improved or more actionable performance metrics for career growth. "
            f"Respond in 2-3 bullet points."
        )
        # Use the globally configured LLM
        return dspy.settings.lm(prompt)

    def enhance_developmental_activities(self, designation, base_activities, skills):
        prompt = (
            f"Given the designation '{designation}', the following base developmental activities: '{base_activities}', "
            f"and these relevant skills: '{skills}', suggest additional or more effective developmental activities for career growth. "
            f"Respond in 2-3 bullet points."
        )
        # Use the globally configured LLM
        return dspy.settings.lm(prompt)
