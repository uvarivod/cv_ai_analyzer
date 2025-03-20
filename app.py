import streamlit as st
from utils import build_JSON, json_to_dict

# Initialize data in session_state
if "data" not in st.session_state:
    st.session_state.data = []

# Application title
st.title("Professional Profiles")

# "Analyze" button
if st.button("Run Analysis"):
    from backend import analyze_cvs
    candidates = analyze_cvs()  # Analyze the data
    json_src = build_JSON(candidates)  # Convert to JSON format
    st.session_state.data = json_to_dict(json_src)  # Update stored data
    st.success("Analysis completed.")  # Display success message

# Variable to store the selected person
selected_person = None

# Display list of candidates
for person in st.session_state.data:
    col1, col2 = st.columns([3, 1])  # Two columns: profession and button
    with col1:
        st.markdown(person["profession"])
    with col2:
        if st.button("More details", key=person["profession"]):
            selected_person = person

def show_person_details(person):
    """
    Displays detailed information about a selected candidate.

    Args:
        person (dict): The selected person's details, including profession, experience, summary, skills, and challenges.

    Returns:
        None
    """
    if person:
        st.subheader(f"Details for {person['profession']}:")
        st.markdown(f"**Summary:** {person['summary']}", unsafe_allow_html=True)
        st.markdown(f"**Years of experience:** {person['years']}", unsafe_allow_html=True)
        st.markdown(f"**Strongest skills:** {', '.join(person['strongest_skills'])}", unsafe_allow_html=True)
        st.markdown(f"**Key challenges:** {', '.join(person['challenges'])}", unsafe_allow_html=True)


# Display detailed information for the selected candidate
if selected_person:
    show_person_details(selected_person)
