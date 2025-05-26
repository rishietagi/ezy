import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
import os
from google.api_core import exceptions
from dotenv import load_dotenv
import time

from database import insert_user, validate_user, get_user_by_email
import hashlib


# ---------- CSS Styling ----------
st.markdown("""
    <style>
        /* Global font and background */
        body, .stApp {
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: 'Segoe UI', sans-serif;
        }
        /* Title */
        .main-title {
            font-size: 2.8em;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 10px;
        }
        /* Subtitle */
        .subtext {
            font-size: 1.1em;
            color: #cbd5e1;
            margin-bottom: 30px;
        }
        /* Upload Section */
        .upload-box {
            background-color: #1e293b;
            padding: 25px;
            border-radius: 10px;
        }
        /* Buttons */
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        }
        /* Radio buttons */
        .stRadio > label {
            font-weight: bold;
            color: #f1f5f9;
        }
        /* Sidebar profile */
        .sidebar-title {
            font-weight: 700;
            font-size: 1.2em;
            color: #f1f5f9;
        }
    </style>
""", unsafe_allow_html=True)


# ---------- Authentication Helpers ----------
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
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .st-emotion-cache-1avcm0n {padding: 0;}  /* Removes unnecessary top padding */
    </style>
""", unsafe_allow_html=True)
    st.subheader("Login")
    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hashed_pwd = hash_password(password)
        if validate_user(email, hashed_pwd):
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.user_email = email

            user_record = get_user_by_email(email)
            if user_record:
                st.session_state.user = {
                    "first_name": user_record[0],
                    "last_name": user_record[1],
                    "phone": user_record[2],
                    "email": user_record[3]
                }

            st.session_state.page = "main"
            st.rerun()
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


# ---------- Gemini Setup ----------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

MAX_RETRIES = 3
RETRY_DELAY = 2


def analyze_medical_report(content, content_type):
    prompt = "Analyze this medical report concisely. Provide key findings, diagnoses, and recommendations:"
    
    for attempt in range(MAX_RETRIES):
        try:
            if content_type == "image":
                response = model.generate_content([prompt, content])
            else:
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
    else:
        word_count = len(content.split())
        return f"""
        Fallback Analysis:
        1. Document Type: Text-based medical report
        2. Word Count: Approximately {word_count} words
        3. Content: The document appears to contain medical information, but detailed analysis is unavailable due to technical issues.
        4. Recommendation: Please review the document manually or consult with a healthcare professional.
        5. Note: This is a simplified fallback response.
        """


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# def back_button_to_url(url):
#     col1, col2 = st.columns([1, 9])
#     with col1:
#         st.markdown(
#             f"""
#             <a href="{url}" target="_self" style="text-decoration: none;">
#                 <button style="
#                     background-color: #2563eb;
#                     color: white;
#                     border: none;
#                     border-radius: 5px;
#                     font-size: 16px;
#                     padding: 8px 16px;
#                     cursor: pointer;
#                 ">⬅️ Back</button>
#             </a>
#             """,
#             unsafe_allow_html=True,
#         )


# ---------- Main App ----------
def main():
    
    # back_button_to_url("http://localhost:5173/")


    hide_streamlit_style = """
        <style>
        /* Hide Streamlit header, footer, and hamburger menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


    if "user" in st.session_state:
        profile_info = f"""
        <div class="profile-container">
            <div class="profile-icon">👤</div>
            <div class="profile-details">
                <strong>{st.session_state.user['first_name']} {st.session_state.user['last_name']}</strong><br>
                {st.session_state.user['email']}<br>
                {st.session_state.user['phone']}<br>
                <form action="" method="post">
                    <input type="submit" value="Logout" class="logout-btn" onclick="window.location.reload();">
                </form>
            </div>
        </div>

        <style>
            .profile-container {{
                position: fixed;
                top: 20px;
                left: 20px;  /* changed from right to left */
                z-index: 9999;
                font-family: Arial, sans-serif;
            }}
            .profile-icon {{
                font-size: 30px;
                cursor: pointer;
                background-color: #3498db;
                color: white;
                border-radius: 50%;
                width: 45px;
                height: 45px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            }}
            .profile-details {{
                display: none;
                position: absolute;
                top: 50px;
                left: 0;  /* align details under icon */
                background-color: blue;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
                width: 220px;
                transition: all 0.3s ease;
            }}
            .profile-container:hover .profile-details {{
                display: block;
            }}
            .logout-btn {{
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                margin-top: 8px;
                border-radius: 5px;
                cursor: pointer;
            }}
        </style>
        """
        st.markdown(profile_info, unsafe_allow_html=True)

    st.markdown("""
    <style>
    body {
        background-color: #0F172A;
        color: white;
    }

    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: -140px;
        margin-bottom: 50px;
    }

    .title-text {
        font-size:  3rem;
        font-weight: bold;
        color: #ffffff;
    }

    .subtitle-text {
        font-size: 1.4rem;
        font-weight: 300;
        color: #cbd5e1;
    }

    .stRadio > div {
        display: flex;
        justify-content: center;
        padding-top: 10px;
    }

    .upload-box {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        max-width: 600px;
        margin: 0 auto;
    }

    .upload-box .stFileUploader, .upload-box .stButton {
        margin-top: 20px;
        text-align: center;
    }

    .stFileUploader > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .stButton button {
        background-color: #3b82f6;
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-weight: 500;
        border: none;
        margin-top: 10px;
        transition: background-color 0.3s ease;
    }

    .stButton button:hover {
        background-color: #2563eb;
    }

    .stFileUploader label {
        color: #ffffff;
        font-weight: 500;
    }

    .stRadio label {
        color: #ffffff;
        font-weight: 500;
    }

    .stMarkdown h4 {
        text-align: center;
        margin-top: 40px;
        margin-bottom: 10px;
        font-weight: 600;
    }

    /* Optional: Improve spinner visibility */
    .stSpinner {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="title-container">
        <div class="title-text">SmartScan Reports</div>
        <div class="subtitle-text">AI driven Medical Report Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("#### Upload a medical report (image or PDF) for analysis")

    with st.container():
        # st.markdown('<div class="upload-box">', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)


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
