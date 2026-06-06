import streamlit as st
from openai import OpenAI
import datetime

st.set_page_config(
    page_title="Agentic Healthcare Assistant using Streamlit MBA",
    page_icon="🩺",
    layout="wide"
)

with st.sidebar:
    st.header("Configuration")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Your key is used only during this session."
    )

if not api_key:
    st.warning("Enter your OpenAI API key in the sidebar.")
    st.stop()

client = OpenAI(api_key=api_key)

if "patients_db" not in st.session_state:
    st.session_state.patients_db = {}

if "appointments_db" not in st.session_state:
    st.session_state.appointments_db = []

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []


def add_log(message):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.agent_logs.append(f"[{time_now}] {message}")


def add_patient_record(patient_name, age, condition, history):
    if not patient_name:
        return "Please enter the patient name."
    if not condition:
        return "Please enter the medical condition."
    if not history:
        return "Please enter the medical history."

    st.session_state.patients_db[patient_name.lower()] = {
        "name": patient_name,
        "age": age,
        "condition": condition,
        "history": history
    }

    add_log(f"Patient record added or updated for {patient_name}")
    return f"Patient record saved successfully for {patient_name}."


def get_patient_history(patient_name):
    if not patient_name:
        return "Please enter the patient name."

    patient = st.session_state.patients_db.get(patient_name.lower())

    if not patient:
        add_log(f"No patient record found for {patient_name}")
        return "No patient record found. Please add the patient record first."

    add_log(f"Retrieved medical history for {patient_name}")

    return f"""
Patient Name: {patient['name']}
Age: {patient['age']}
Condition: {patient['condition']}
Medical History: {patient['history']}
"""


def summarize_patient_history(patient_name):
    if not patient_name:
        return "Please enter the patient name."

    patient = st.session_state.patients_db.get(patient_name.lower())

    if not patient:
        add_log(f"No record found for summary request: {patient_name}")
        return "No patient record found. Please add the patient record first."

    prompt = f"""
You are a safe healthcare assistant.

Summarize this patient's medical history in simple language.

Patient Name: {patient['name']}
Age: {patient['age']}
Condition: {patient['condition']}
Medical History: {patient['history']}

Rules:
- Keep the summary simple.
- Do not give a final medical diagnosis.
- Do not prescribe medicine.
- Mention that the patient should consult a qualified doctor.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a safe healthcare assistant. Do not provide diagnosis or prescriptions."},
                {"role": "user", "content": prompt}
            ]
        )

        add_log(f"Generated patient summary for {patient_name}")
        return response.choices[0].message.content

    except Exception as e:
        add_log(f"Summary error: {str(e)}")
        return f"Error while generating summary: {str(e)}"


def book_appointment(patient_name, doctor_type, preferred_date):
    if not patient_name:
        return "Please enter the patient name."

    appointment = {
        "patient_name": patient_name,
        "doctor_type": doctor_type,
        "date": str(preferred_date),
        "status": "Booked"
    }

    st.session_state.appointments_db.append(appointment)
    add_log(f"Appointment booked for {patient_name} with {doctor_type} on {preferred_date}")

    return f"""
Appointment booked successfully.

Patient Name: {patient_name}
Doctor Type: {doctor_type}
Preferred Date: {preferred_date}
Status: Booked
"""


def show_appointments():
    if len(st.session_state.appointments_db) == 0:
        return "No appointments booked yet."

    result = ""

    for index, appointment in enumerate(st.session_state.appointments_db, start=1):
        result += f"""
Appointment {index}
Patient Name: {appointment['patient_name']}
Doctor Type: {appointment['doctor_type']}
Date: {appointment['date']}
Status: {appointment['status']}

"""

    add_log("Displayed appointment list")
    return result


def disease_information(disease_name):
    if not disease_name:
        return "Please enter the disease name or medical topic."

    prompt = f"""
Explain this medical topic in simple language:

Topic: {disease_name}

Include:
1. What it is
2. Common symptoms
3. General treatment options
4. When to consult a doctor

Safety rules:
- Do not provide personal diagnosis.
- Do not prescribe medicine.
- Do not replace a doctor.
- Tell the user to consult a qualified doctor.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You provide general educational healthcare information only."},
                {"role": "user", "content": prompt}
            ]
        )

        add_log(f"Generated disease information for {disease_name}")
        return response.choices[0].message.content

    except Exception as e:
        add_log(f"Disease information error: {str(e)}")
        return f"Error while generating disease information: {str(e)}"


def healthcare_agent(user_query, patient_name):
    if not user_query:
        return "Please enter your query."

    query = user_query.lower()
    add_log(f"User query received: {user_query}")

    if "history" in query or "record" in query or "details" in query:
        return get_patient_history(patient_name)

    elif "summarize" in query or "summary" in query:
        return summarize_patient_history(patient_name)

    elif "appointment" in query or "book" in query or "doctor" in query:
        return "Please use the Book Appointment page to book a doctor appointment."

    elif "disease" in query or "symptom" in query or "treatment" in query or "medicine" in query:
        return disease_information(user_query)

    else:
        prompt = f"""
User asked: {user_query}

Respond as a helpful healthcare assistant.

Rules:
- Keep the answer simple.
- Do not give a final medical diagnosis.
- Do not prescribe medicine.
- Suggest consulting a qualified doctor if needed.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a safe healthcare assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            add_log("Generated general healthcare response")
            return response.choices[0].message.content

        except Exception as e:
            add_log(f"General response error: {str(e)}")
            return f"Error while generating response: {str(e)}"


def show_logs():
    if len(st.session_state.agent_logs) == 0:
        return "No logs yet."

    return "\\n".join(st.session_state.agent_logs)


def show_evaluation_metrics():
    return f"""
Simple Evaluation Metrics

Total Patient Records: {len(st.session_state.patients_db)}
Total Appointments Booked: {len(st.session_state.appointments_db)}
Total Agent Actions Logged: {len(st.session_state.agent_logs)}

Available Tools:
- Healthcare agent router
- Patient record tool
- Patient history retrieval tool
- AI summary tool
- Appointment booking tool
- Appointment viewer
- Disease information tool
- Agent logs
- Evaluation metrics
"""


st.title("Agentic Healthcare Assistant using Gradio MBA")

st.write("This Streamlit version deploys the same capstone concept tested first in Gradio.")

st.warning("Educational project only. This app does not provide medical diagnosis, prescriptions, or treatment decisions.")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Chat with Healthcare Agent",
        "Add Patient Record",
        "View Patient History",
        "Summarize Patient History",
        "Book Appointment",
        "View Appointments",
        "Disease Information",
        "Agent Logs",
        "Evaluation Metrics"
    ]
)

if page == "Chat with Healthcare Agent":
    st.header("Chat with Healthcare Agent")
    user_query = st.text_area("Healthcare query")
    patient_name = st.text_input("Patient name")

    if st.button("Ask Agent"):
        result = healthcare_agent(user_query, patient_name)
        st.text_area("Agent response", result, height=300)

elif page == "Add Patient Record":
    st.header("Add Patient Record")
    patient_name = st.text_input("Patient name")
    age = st.number_input("Age", min_value=0, max_value=130, value=70)
    condition = st.text_input("Medical condition")
    history = st.text_area("Medical history")

    if st.button("Save Patient Record"):
        result = add_patient_record(patient_name, age, condition, history)
        st.success(result)

elif page == "View Patient History":
    st.header("View Patient History")
    patient_name = st.text_input("Patient name")

    if st.button("Get Patient History"):
        result = get_patient_history(patient_name)
        st.text_area("Patient history", result, height=250)

elif page == "Summarize Patient History":
    st.header("Summarize Patient History")
    patient_name = st.text_input("Patient name")

    if st.button("Summarize History"):
        result = summarize_patient_history(patient_name)
        st.text_area("Patient summary", result, height=300)

elif page == "Book Appointment":
    st.header("Book Appointment")
    patient_name = st.text_input("Patient name")

    doctor_type = st.selectbox(
        "Doctor type",
        [
            "General Physician",
            "Cardiologist",
            "Nephrologist",
            "Neurologist",
            "Dermatologist",
            "Orthopedic Doctor",
            "Pediatrician",
            "ENT Specialist"
        ]
    )

    preferred_date = st.date_input("Preferred date")

    if st.button("Book Appointment"):
        result = book_appointment(patient_name, doctor_type, preferred_date)
        st.success(result)

elif page == "View Appointments":
    st.header("View Appointments")

    if st.button("Show Appointments"):
        result = show_appointments()
        st.text_area("Appointments", result, height=300)

elif page == "Disease Information":
    st.header("Disease Information")
    disease_name = st.text_input("Disease or medical topic")

    if st.button("Get Disease Information"):
        result = disease_information(disease_name)
        st.text_area("Disease information", result, height=350)

elif page == "Agent Logs":
    st.header("Agent Logs")

    if st.button("Show Logs"):
        result = show_logs()
        st.text_area("Logs", result, height=350)

elif page == "Evaluation Metrics":
    st.header("Evaluation Metrics")

    if st.button("Show Evaluation Metrics"):
        result = show_evaluation_metrics()
        st.text_area("Evaluation metrics", result, height=300)
