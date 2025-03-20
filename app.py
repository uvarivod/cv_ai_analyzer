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
    candidates = analyze_cvs()  # Perform analysis
    json_src = build_JSON(candidates)  # Convert to JSON
    st.session_state.data = json_to_dict(json_src)  # Update data
    st.success("Analysis completed.")  # Display notification

# Dictionary to store selected person
selected_person = None

# Display list of candidates
for index, person in enumerate(st.session_state.data):
    col1, col2 = st.columns([3, 1])  # Two columns: profession and button
    with col1:
        st.markdown(person["profession"])
    with col2:
        if st.button("More Details", key=f"{person['profession']} #{index}"):
            selected_person = person

# Function to display detailed information
def show_person_details(person):
    if person:
        st.subheader(f"Details for {person['profession']}")
        st.markdown(f"**Years of Experience:** {person['years']}")
        st.markdown(f"**Summary:** {person['summary']}")
        st.markdown(f"**Strongest Skills:** {', '.join(person['strongest_skills'])}")
        st.markdown(f"**Challenges:** {', '.join(person['challenges'])}")

# Display details of the selected candidate
if selected_person:
    show_person_details(selected_person)
