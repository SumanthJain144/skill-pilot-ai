from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from competency_data import CompetencyData
from ai_utils import assess_and_recommend

# Load competency data
competency_data = CompetencyData("competency-data.csv")

st.set_page_config(page_title="Career Growth Advisor", layout="wide", initial_sidebar_state="expanded")


# Add a custom CSS for styling and animations
st.markdown("""
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .welcome-animation {
        animation: fadeIn 1.2s ease-out forwards;
        margin-bottom: 2rem;
        text-align: center;
    }
    .welcome-image {
        max-width: 180px;
        margin: 0 auto;
        display: block;
    }
    .welcome-text {
        font-size: 1.8rem;
        margin-top: 1rem;
        color: #2c3e50;
        font-weight: 500;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Create a sidebar for user profile selections
with st.sidebar:
    # Add logo at the top of sidebar, centered
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("logo.png", width=400, use_container_width=True)
    st.header("Your Career Profile")
    
    # Step 1: User selects current competency in sidebar
    competencies = competency_data.get_competencies()
    current_competency = st.selectbox("Select your current competency:", competencies)
    
    # Step 2: User selects designation filtered by competency in sidebar
    if current_competency:
        # Only show designations that are not empty and not duplicated
        designations = competency_data.get_designations(current_competency)
        designations = [d for d in designations if d and d.strip()]
        # Remove duplicates while preserving order
        seen = set()
        filtered_designations = []
        for d in designations:
            if d not in seen:
                filtered_designations.append(d)
                seen.add(d)
        current_designation = st.selectbox("Select your current designation:", filtered_designations)
    else:
        current_designation = None
        
    # Add a divider
    st.divider()
    
    # Add some helpful information in the sidebar
    st.markdown("""
    ### How to use:
    1. Select your competency
    2. Choose your designation
    3. Rate your skills
    4. Get personalized recommendations
    """)

# Show welcome animation only when nothing is selected
if not (current_competency and current_designation):
    # Create custom CSS for an animated GIF-like effect
    st.markdown("""
    <style>
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            50% { transform: scale(1.05); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
            100% { transform: scale(1); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        }
        
        @keyframes shine {
            0% { background-position: -100% 0; }
            100% { background-position: 200% 0; }
        }
        
        .welcome-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .animated-image-container {
            position: relative;
            animation: float 6s ease-in-out infinite;
            margin-bottom: 2rem;
        }
        
        .animated-image {
            width: 280px;
            height: 280px;
            object-fit: contain;
            animation: pulse 3s infinite ease-in-out;
            border-radius: 50%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .glow {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(66,153,225,0.2) 0%, rgba(66,153,225,0) 70%);
            animation: pulse 3s infinite ease-in-out;
            z-index: -1;
        }
        
        .welcome-title {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1.5rem 0;
            text-align: center;
            color: #2c3e50;
            animation: fadeIn 1.5s;
        }
        
        .welcome-subtitle {
            font-size: 1.3rem;
            text-align: center;
            color: #7f8c8d;
            animation: fadeIn 2s;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the welcome container with animated elements using Streamlit's native components
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Add the image with animation class applied via HTML
            st.markdown("""
            <div class="animated-image-container" style="text-align: center;">
                <div class="glow"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Use Streamlit's native image component for better loading
            st.image("welcome.png", width=700)
            
            # Add the welcome text
            st.markdown("""
            <h4 class="welcome-subtitle">Start by selecting your competency from the left panel</h4>
            """, unsafe_allow_html=True)
    
# Display the current selection in the main area
if current_competency and current_designation:
    # Create header with title
    st.title("Skill Graph & Career Path Recommmender")
    st.write(f"**Selected Profile:** {current_designation} in {current_competency}")
    st.divider()

# Step 3: Generate quiz with categorical levels for all skills from all levels
user_skill_ratings = {}
skill_levels = ['Skills: Novice', 'Skills: Basic', 'Skills: Intermediate', 'Skills: Advanced', 'Skills: Expert']
proficiency_labels = ['Novice', 'Basic', 'Intermediate', 'Advanced', 'Expert']

# Only show quiz if both dropdowns have a selection and the designation is not empty
if current_competency and current_designation:
    skills_dict = competency_data.get_skills_for_designation(current_competency, current_designation)
    certifications = competency_data.get_certifications_for_designation(current_competency, current_designation)
    if any(skills_dict.values()):
        st.subheader("Select your proficiency level for each skill:")
        
        # Create tabs for different skill levels
        # First, get non-empty skill levels
        available_levels = [level for level in skill_levels if skills_dict.get(level, [])]
        
        # Create tabs with formatted tab labels
        tabs = st.tabs([level.replace('Skills: ', '') for level in available_levels])
        
        # Populate each tab with its skills
        for i, level in enumerate(available_levels):
            with tabs[i]:
                skills = skills_dict.get(level, [])
                if skills:
                    for skill in skills:
                        user_skill_ratings[skill] = st.radio(
                            skill,
                            proficiency_labels,
                            horizontal=True,
                            key=f"{level}_{skill}_{current_competency}_{current_designation}"
                        )
        # Radar chart visualization of skill ratings
        import plotly.graph_objects as go
        if user_skill_ratings:
            categories = list(user_skill_ratings.keys())
            values = [proficiency_labels.index(user_skill_ratings[cat]) + 1 for cat in categories]
            fig = go.Figure(
                data=[
                    go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        name='Your Skill Profile',
                        marker=dict(color='rgba(0,123,255,0.7)')
                    )
                ]
            )
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
                showlegend=False,
                title="Your Skill Profile (Radar Chart)"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Track previous selection to reset results when changed
        if 'prev_competency' not in st.session_state:
            st.session_state['prev_competency'] = current_competency
        if 'prev_designation' not in st.session_state:
            st.session_state['prev_designation'] = current_designation
            
        # Reset results if competency or designation has changed
        if (st.session_state.get('prev_competency') != current_competency or 
            st.session_state.get('prev_designation') != current_designation):
            if 'verdict' in st.session_state:
                del st.session_state['verdict']
            if 'recommendation' in st.session_state:
                del st.session_state['recommendation']
            st.session_state['prev_competency'] = current_competency
            st.session_state['prev_designation'] = current_designation
        
        # Define a function to reset state
        def reset_results():
            if 'verdict' in st.session_state:
                del st.session_state['verdict']
            if 'recommendation' in st.session_state:
                del st.session_state['recommendation']
        
        # Step 4: Assessment and Recommendation
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Get Assessment & Career Path"):
                with st.spinner("Assessing your level and generating recommendations..."):
                    verdict, recommendation = assess_and_recommend(
                        designation=current_designation,
                        skills_dict=skills_dict,
                        user_skill_ratings=user_skill_ratings,
                        certifications=certifications
                    )
                # Store results in session state to persist after download
                st.session_state['verdict'] = verdict
                st.session_state['recommendation'] = recommendation
                
        with col2:
            st.button("Reset Results", on_click=reset_results)

        # Display results if present in session state
        if 'verdict' in st.session_state and 'recommendation' in st.session_state:
            import re
            # Try to extract a concise heading from the verdict
            heading = None
            match = re.search(
                r"((?:Based on (?:your|the) skill profile|Given this skill profile)[^\n\.!?]*[\.!?])",
                st.session_state['verdict'], re.IGNORECASE)
            if match:
                heading = match.group(1).strip()
            else:
                # Fallback: use the first line of the verdict
                heading = st.session_state['verdict'].splitlines()[0].strip()
            
            st.markdown(f"{heading}")
            st.markdown(f"**Career Path Recommendation:**\n{st.session_state['recommendation']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            import io
            report = io.StringIO()
            report.write(f"Assessment: {st.session_state['verdict']}\n\n")
            report.write(f"Career Path Recommendation:\n{st.session_state['recommendation']}\n")
            st.download_button(
                label="Download This Career Path",
                data=report.getvalue(),
                file_name="career_path_recommendation.txt",
                mime="text/plain"
            )
    else:
        st.info("No skills found for this designation.")

# Step 4 and onward will be implemented after AI integration and further steps
# This sets up the new flow: dropdowns and dynamic quiz generation based on CSV
