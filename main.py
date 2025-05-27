import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
import os
from google.api_core import exceptions
from dotenv import load_dotenv
import time
from datetime import datetime
from database import insert_user, validate_user, get_user_by_email, log_login_time, get_login_history, save_report, get_user_reports, get_report_by_id
import time
import hashlib
from streamlit_lottie import st_lottie
import requests


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
        .st-lottie {
            display: flex;
            justify-content: center;
            align-items: center;
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


def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# def show_overlay_animation(container, lottie_url, duration=2):
#     anim_data = load_lottie_url(lottie_url)
#     if anim_data is None:
#         st.warning("Animation failed to load.")
#         return

#     with container:
#         st.markdown("""
#             <style>
#             .overlay-lottie {
#                 position: fixed;
#                 top: 0;
#                 left: 0;
#                 width: 100vw;
#                 height: 100vh;
#                 background-color: rgba(15, 23, 42, 0.95);
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 z-index: 9999;
#             }
#             </style>
#         """, unsafe_allow_html=True)

#         st.markdown('<div class="overlay-lottie">', unsafe_allow_html=True)
#         st_lottie(anim_data, height=300, key="lottie-transition")
#         st.markdown('</div>', unsafe_allow_html=True)

#     time.sleep(duration)
#     container.empty()


def show_fullscreen_animation(lottie_url, duration=2):
    # Clear all widgets
    st.empty()

    # Display full-page animation
    lottie_json = load_lottie_url(lottie_url)
    st.markdown("""
        <style>
        .fullscreen-lottie {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="fullscreen-lottie">', unsafe_allow_html=True)
    st_lottie(lottie_json, speed=1, height=400, key="full_anim")
    st.markdown('</div>', unsafe_allow_html=True)

    time.sleep(duration)

# def fake_page_transition(message="Loading..."):
#     placeholder = st.empty()
#     with placeholder.container():
#         st.markdown(f"<h4 style='text-align:center;'>{message}</h4>", unsafe_allow_html=True)
#         st.progress(0)
#         for percent_complete in range(100):
#             time.sleep(0.005)
#             st.progress(percent_complete + 1)
#     placeholder.empty()

    
# ---------- Authentication Helpers ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup():
    hide_streamlit_style = """
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .signup-container {
            max-width: 300px;
            margin: 0 auto;
            background-color: #44576D;
            padding: 10px;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .signup-title {
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .stTextInput > div > div,
        .stNumberInput > div > div,
        .stSelectbox > div > div {
            background-color: #334155;
            color: white;
            border-radius: 8px;
        }
        .stTextInput input,
        .stNumberInput input {
            background-color: #334155;
            color: white;
        }
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-weight: 500;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2563eb;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.markdown('''
    <div class="signup-container">
        <div class="signup-title">Sign Up</div>
    </div>
    ''', unsafe_allow_html=True)

    animation_placeholder = st.empty()

    with st.container():
        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email ID")
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        password = st.text_input("Password", type="password")

        if st.button("Create Account", key="create"):
            if first and last and phone and email and password and age and gender:
                hashed_pwd = hash_password(password)
                success = insert_user(first, last, phone, email, hashed_pwd, age, gender)
                if success:
                    st.success("Account created successfully.")
                    st.session_state.page = "login"
                else:
                    st.error("Account creation failed. Email might already be registered.")
            else:
                st.warning("Please fill all fields.")


    if st.button("Go to Login", key="go_login"):
        with st.spinner("Redirecting to Login..."):
            anim = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_usmfx6bp.json")
            st_lottie(anim, speed=1, height=200)
            time.sleep(1.5)  # allow animation to play
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
        user = validate_user(email, hashed_pwd)

        if user:
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.user_email = email

            user_id = user[0]  # Assuming first field is user ID
            log_login_time(user_id)  # ✅ Log login time

            st.session_state.user_id = user_id  # Store for use in profile page
            st.session_state.user = {
                "first_name": user[1],
                "last_name": user[2],
                "phone": user[3],
                "email": user[4]
            }

            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("Invalid credentials.")

    if st.button("Go to SignUp", key="go_signup"):
        with st.spinner("Redirecting to Signup..."):
            anim = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_usmfx6bp.json")
            st_lottie(anim, speed=1, height=200)
            time.sleep(1.5)  # allow animation to play
        st.session_state.page = "signup"
        st.rerun()




def logout():
    for key in ["logged_in", "user_email", "user", "page"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out successfully.")
    # fake_page_transition("Logging You Out...")
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
    hide_streamlit_style = """
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.markdown("""
        <div class="header-title">
            <h1>SmartScan Reports</h1>
            <p class="subtitle">AI driven Medical Report Analyzer</p>
        </div>
    """, unsafe_allow_html=True)

    if "user" in st.session_state:
        user = st.session_state.user
        user_record = get_user_by_email(user['email'])
        user_id = user_record[4]
        login_history = get_login_history(user_id)

        profile_info = f"""
        <div class="profile-wrapper">
            <div class="profile-icon">👤</div>
            <div class="profile-info">
                <strong>{user['first_name']} {user['last_name']}</strong><br>
                {user['email']}<br>
                {user['phone']}<br>
                <form action="" method="post">
                    <input type="submit" value="Logout" class="logout-btn" onclick="window.location.reload();">
                </form>
                <hr style="margin: 10px 0;">
                <div class="sessions">
                    <strong>Previous Sessions</strong><br>
                    {"<br>".join(f"Session {i + 1}: {entry[0].strftime('%Y-%m-%d %H:%M:%S')}" for i, entry in enumerate(login_history)) if login_history else "No previous login sessions found."}
                </div>
            </div>
        </div>
        """
        st.markdown(profile_info, unsafe_allow_html=True)

    # ----- Style Section -----
    st.markdown("""
    <style>
    body {
        background-color: #0F172A;
        color: white;
    }

    /* Profile box top-left */
    .profile-wrapper {
        position: fixed;
        top: 20px;
        left: 20px;
        background-color: #1e293b;
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        width: 250px;
        z-index: 1000;
    }

    .profile-icon {
        font-size: 36px;
        margin-bottom: 10px;
        text-align: center;
    }

    .logout-btn {
        background-color: #e74c3c;
        color: white;
        border: none;
        padding: 6px 12px;
        margin-top: 8px;
        border-radius: 6px;
        cursor: pointer;
        width: 100%;
    }

    .sessions {
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-top: 10px;
    }

    /* Centered title */
    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        top: 20px;
        margin-top: 0px;
        margin-bottom: 50px;
    }

    .title-text {
        font-size:  3rem;
        font-weight: bold;
        color: #ffffff;
    }
    .header-title {
        position: relative;
        top: 20px;
        text-align: center;
        margin-top: 0;
        margin-bottom: 30px;
        z-index: 0;
    }

    .header-title h1 {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        margin: 0;
    }

    .header-title .subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        color: #cbd5e1;
        margin-top: 10px;
    }

    .subtitle-text {
        font-size: 1.4rem;
        font-weight: 300;
        color: #cbd5e1;
    }

    /* Upload & file controls */
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

    .stFileUploader label,
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

    .stSpinner {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)





    st.write("#### Upload a medical report (image or PDF) for analysis")

    with st.container():
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

                        filename = uploaded_file.name
                        report_content = "Image file analyzed "
                        save_report(user_id, filename, report_content, analysis)

                        st.subheader("Analysis Results:")
                        st.write(analysis)
                        st.success("Report analysis saved to history.")

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

                        filename = uploaded_file.name
                        report_content = pdf_text
                        save_report(user_id, filename, report_content, analysis)

                        st.subheader("Analysis Results:")
                        st.write(analysis)
                        st.success("Report analysis saved to history.")

                        os.unlink(tmp_file_path)

        st.markdown('</div>', unsafe_allow_html=True)


        st.markdown("---")
        st.subheader("Previous Analysis of Reports")

        report_sessions = get_user_reports(user_id)

        if report_sessions:
            selected = st.selectbox(
                "Select a previous report:",
                options=report_sessions,
                format_func=lambda r: f"{r['filename']} ({r['created_at'].strftime('%Y-%m-%d %H:%M')})"
            )

            if selected:
                report_details = get_report_by_id(selected['id'])

                # Metadata section
                st.markdown(
                    f"""
                    <div style="font-size: 0.9rem; color: #ccc; margin-bottom: 0.5rem;">
                        <b>Filename:</b> {report_details['filename']}<br>
                        <b>Uploaded:</b> {report_details['created_at'].strftime('%Y-%m-%d %H:%M')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Report content block
                st.subheader("Report Content")
                st.code(
                    report_details['report_content'] or "[Image file analysed, no text content available]",
                    language='text'
                )

                # Analysis result block
                st.subheader("Analysis Result")
                st.write(report_details['analysis'])

        else:
            st.info("No previous reports found.")




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
