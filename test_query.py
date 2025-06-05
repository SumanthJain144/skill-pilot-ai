import os
import dspy
from groq import Groq
from vector_store import DesignationVectorStore
import streamlit
from career_advisor import CareerAdvisor  # Use the refactored class

# Manually configure LLM (Groq)
from groq import Groq  # Assuming this is how you import Groq

# Step 1: Manually configure Groq LLM
groq_api_key = os.getenv("GROQ_API_KEY")

dspy.configure(lm=(
    dspy.LM(
        model="groq/llama3-70b-8192",
        api_key=groq_api_key
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
        # Use LLM to generate enhancement
        return dspy.LM()(prompt)

    def enhance_developmental_activities(self, designation, base_activities, skills):
        prompt = (
            f"Given the designation '{designation}', the following base developmental activities: '{base_activities}', "
            f"and these relevant skills: '{skills}', suggest additional or more effective developmental activities for career growth. "
            f"Respond in 2-3 bullet points."
        )
        # Use LLM to generate enhancement
        return dspy.LM()(prompt)