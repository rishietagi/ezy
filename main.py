import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
import os
from google.api_core import exceptions
from dotenv import load_dotenv
import time

import streamlit as st
from database import insert_user, validate_user, get_user_by_email
import hashlib



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup():
    st.subheader("Sign Up")
    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if first and last and phone and email and password:
            hashed_pwd = hash_password(password)
            success = insert_user(first, last, phone, email, hashed_pwd)
            if success:
                st.success("Account created successfully.")
                st.session_state.page = "login"
            else:
                st.error("Account creation failed. Email might already be registered.")
        else:
            st.warning("Please fill all fields.")

    st.markdown("Already have an account? [Login here](#)")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()


def login():
    st.subheader("Login")
    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hashed_pwd = hash_password(password)
        if validate_user(email, hashed_pwd):
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.user_email = email

            # Fetch user details for profile icon
            user_record = get_user_by_email(email)
            if user_record:
                st.session_state.user = {
                    "first_name": user_record[0],
                    "last_name": user_record[1],
                    "phone": user_record[2],
                    "email": user_record[3]
                }

            st.session_state.page = "main"
            st.rerun()  # <-- Important to refresh page view
        else:
            st.error("Invalid credentials.")

    st.markdown("Don't have an account? [Sign up here](#)")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()


def logout():
    for key in ["logged_in", "user_email", "user", "page"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out successfully.")
    st.session_state.page = "login"
    st.experimental_rerun()




load_dotenv()

# Configure the Gemini AI model
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def analyze_medical_report(content, content_type):
    prompt = "Analyze this medical report concisely. Provide key findings, diagnoses, and recommendations:"
    
    for attempt in range(MAX_RETRIES):
        try:
            if content_type == "image":
                response = model.generate_content([prompt, content])
            else:  # text
                # Gemini 1.5 Flash can handle larger inputs, so we'll send the full text
                response = model.generate_content(f"{prompt}\n\n{content}")
            
            return response.text
        except exceptions.GoogleAPIError as e:
            if attempt < MAX_RETRIES - 1:
                st.warning(f"An error occurred. Retrying in {RETRY_DELAY} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                st.error(f"Failed to analyze the report after {MAX_RETRIES} attempts. Error: {str(e)}")
                return fallback_analysis(content, content_type)

def fallback_analysis(content, content_type):
    st.warning("Using fallback analysis method due to API issues.")
    if content_type == "image":
        return "Unable to analyze the image due to API issues. Please try again later or consult a medical professional for accurate interpretation."
    else:  # text
        word_count = len(content.split())
        return f"""
        Fallback Analysis:
        1. Document Type: Text-based medical report
        2. Word Count: Approximately {word_count} words
        3. Content: The document appears to contain medical information, but detailed analysis is unavailable due to technical issues.
        4. Recommendation: Please review the document manually or consult with a healthcare professional for accurate interpretation.
        5. Note: This is a simplified analysis due to temporary unavailability of the AI service. For a comprehensive analysis, please try again later.
        """

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text
def back_button_to_url(url):
    col1, col2 = st.columns([1, 9])  # Creates a narrow left column
    with col1:
        st.markdown(
            f"""
            <a href="{url}" target="_self" style="text-decoration: none;">
                <button style="
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    padding: 8px 16px;
                    cursor: pointer;
                ">⬅️ Back</button>
            </a>
            """,
            unsafe_allow_html=True,
        )
def main():
    back_button_to_url("http://localhost:5173/")

    if "user" in st.session_state:
        with st.sidebar.expander("👤 My Profile", expanded=False):
            st.markdown(f"**Name:** {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Phone:** {st.session_state.user['phone']}")
            if st.button("Logout"):
                logout()


    st.title("SmartScan Reports: Simple Medical Report Analyzer")
    st.write("Upload a medical report (image or PDF) for analysis")

    file_type = st.radio("Select file type:", ("Image", "PDF"))

    if file_type == "Image":
        uploaded_file = st.file_uploader("Choose a medical report image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            image = Image.open(tmp_file_path)
            st.image(image, caption="Uploaded Medical Report", use_column_width=True)

            if st.button("Analyze Image Report"):
                with st.spinner("Analyzing the medical report image..."):
                    analysis = analyze_medical_report(image, "image")
                    st.subheader("Analysis Results:")
                    st.write(analysis)

            os.unlink(tmp_file_path)

    else:  # PDF
        uploaded_file = st.file_uploader("Choose a medical report PDF", type=["pdf"])
        if uploaded_file is not None:
            st.write("PDF uploaded successfully")

            if st.button("Analyze PDF Report"):
                with st.spinner("Analyzing the medical report PDF..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    with open(tmp_file_path, 'rb') as pdf_file:
                        pdf_text = extract_text_from_pdf(pdf_file)

                    analysis = analyze_medical_report(pdf_text, "text")
                    st.subheader("Analysis Results:")
                    st.write(analysis)

                    os.unlink(tmp_file_path)

if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "signup":
        signup()
    elif st.session_state.page == "login":
        login()
    elif st.session_state.page == "main" and st.session_state.get("logged_in", False):
        main()
    else:
        st.warning("You're not logged in. Redirecting to login page...")
        st.session_state.page = "login"
