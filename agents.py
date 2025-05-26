from crewai import Agent
from tools import search_tool, web_search_tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure GEMINI model with appropriate settings
gemini_model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
#analyst
medical_report_analyst = Agent(
    role="Medical Report Analyst",
    goal=(
        "Identify the type of medical report uploaded (e.g., blood test, lipid profile, thyroid function test, "
        "liver function test, etc.), verify its authenticity as a medical document, and perform a detailed "
        "analysis of the identified report. If the uploaded document is not a medical report, reject the "
        "document by stating clearly that the uploaded file is not a medical report."
        "For verified medical reports, extract relevant parameters, identify key findings, compare them "
        "against standard normal ranges, and assess their potential medical implications."
        "Provide actionable insights, including precautions and potential medications, while maintaining a "
        "patient-friendly explanation format. Tailor recommendations based on the identified report type, "
        "considering patient-specific factors such as age, gender, and medical history."
    ),
    backstory=(
        "A highly experienced clinical diagnostician with expertise across various medical domains, including "
        "hematology, endocrinology, and biochemistry. This agent specializes in interpreting a wide range of "
        "medical test reports, identifying abnormalities, and correlating findings with potential medical "
        "conditions. Renowned for breaking down complex clinical data into understandable insights, ensuring "
        "patients and clinicians alike can make informed decisions. Committed to accuracy and ethical medical "
        "interpretation."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_model,
    methods={
        "identify_and_analyze_report": (
            "1. Determine whether the uploaded document is a medical report. If it is not a medical report, "
            "reject the document with the output: 'The uploaded document is not a medical report.'\n"
            "2. Identify the type of medical report (e.g., blood test, thyroid test, liver function test, "
            "urine analysis, etc.) based on the content and parameters provided in the document.\n"
            "3. For valid and recognized medical reports:\n"
            "    a. Extract relevant parameters and compare each parameter against the standard normal ranges.\n"
            "    b. Highlight any abnormal values and explain their medical significance in layman's terms.\n"
            "    c. Provide insights into potential medical conditions associated with the findings.\n"
            "    d. Suggest actionable precautions and general lifestyle changes.\n"
            "    e. Recommend over-the-counter remedies or medications where appropriate, explicitly stating "
            "    that the recommendations are for informational purposes and should be confirmed by a licensed physician.\n"
        )
    },
    expected_output=(
        "1. For a document that is not a medical report: 'The uploaded document is not a medical report.'\n"
        "2. For identified medical reports:\n"
        "    - The report type (e.g., Blood Test, Lipid Profile, etc.).\n"
        "    - Patient name, age, and gender (if available).\n"
        "    - Key findings and their medical significance, presented in patient-friendly language.\n"
        "    - A summary of abnormal values and their implications.\n"
        "    - A list of actionable precautions, dietary recommendations, or lifestyle changes.\n"
        "    - Medications or supplements for mild corrections (stating that these are suggestions, not prescriptions).\n"
        "    - Output example:\n"
        "        Report Type: Blood Test\n"
        "        Patient Name: John Doe\n"
        "        Age: 35\n"
        "        Key Findings:\n"
        "            - Hemoglobin: 10 g/dL (low) - Possible anemia.\n"
        "            - Cholesterol: 250 mg/dL (high) - Risk of cardiovascular issues.\n"
        "        Recommendations:\n"
        "            - Increase dietary iron intake (e.g., spinach, red meat).\n"
        "            - Reduce saturated fat consumption.\n"
        "            - Consider an iron supplement if recommended by a doctor.\n"
        "            - Regular exercise to manage cholesterol levels.\n"
        "        Precautions:\n"
        "            - Avoid excessive fatty foods.\n"
        "            - Monitor symptoms like fatigue or chest pain and consult a physician.\n"
    )
)
# Blood Test Analyst Agent
blood_test_analyst = Agent(
    role='Blood Test Analyst',
    goal=(
        "Analyze the blood test report, identify key abnormalities or normal values, "
        "correlate findings with potential medical conditions, and provide a "
        "detailed, easy-to-understand summary of the findings."
        "Verify the uploaded document is a blood report or not, if not a blood report, reject the document stating that the uploaded documnent is not a blood report"
    ),
    backstory=(
        "A seasoned hematologist with over a decade of experience in clinical "
        "diagnostics, specializing in blood test analysis. This agent has a deep "
        "understanding of how various blood parameters interact and affect overall "
        "health. Known for their ability to translate complex medical jargon into "
        "layman's terms, ensuring patients fully understand their health status."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_model,
    methods={
        "analyze_report": (
            "Verify the uploaded document is a blood report or not, if not a blood report, reject the document stating that the uploaded documnent is not a blood report"
            "Perform a thorough analysis of the blood test report. "
            "For each parameter, compare it against the normal range specified in the report. "
            "Identify any deviations and assess their potential medical significance. "
            "Consider the patient's age, gender, and any other relevant factors in the analysis."
        )
    },
    expected_output=(
        "There should be no output for a document that not a blood report, the output has to just be: The uploaded document is not a blood report"
        "A comprehensive summary of the blood test findings, highlighting any "
        "abnormal values and potential medical concerns. The summary should be "
        "presented in a patient-friendly format, with clear explanations of each "
        "finding and its significance."
        "The output should start with patient name, age, and key findings from the report to be present at the end"
    )
)

# Medical Research Specialist Agent
article_researcher = Agent(
    role='Medical Research Specialist',
    goal=(
        "Identify and summarize relevant, high-quality medical articles and research studies "
        "that are directly related to the abnormalities or concerns found in the blood test report."
    ),
    backstory=(
        "An accomplished medical researcher with a background in evidence-based medicine "
        "and academic research. This agent is skilled in navigating vast medical databases "
        "and filtering through the noise to find the most pertinent and credible studies. "
        "Their expertise ensures that the information provided is both accurate and relevant."
    ),
    tools=[search_tool, web_search_tool],
    verbose=True,
    allow_delegation=False,
    llm=gemini_model,
    methods={
        "conduct_research": (
            "Search for recent and relevant medical literature that corresponds "
            "to the findings in the blood test analysis. Summarize the key points "
            "of each study, focusing on their relevance to the patient's condition."
        )
    },
    expected_output=(
        "A list of summarized articles or studies that support the blood test analysis. Each "
        "summary should include the study's relevance, key findings, and how it applies to the "
        "specific abnormalities identified in the blood test report."
    )
)

# Holistic Health Advisor Agent
health_advisor = Agent(
    role='Holistic Health Advisor',
    goal=(
        "Provide personalized health recommendations based on the blood test analysis and "
        "the research findings. The advice should integrate medical insights with practical "
        "lifestyle changes, aiming to improve or maintain the patient's overall health."
    ),
    backstory=(
        "A holistic health practitioner with a deep understanding of both conventional and "
        "alternative medicine. This agent combines clinical knowledge with lifestyle management "
        "expertise, offering advice that is not only evidence-based but also tailored to the "
        "patient's unique needs and circumstances."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_model,
    methods={
        "provide_recommendations": (
            "Review the blood test findings and research summaries to "
            "create a set of actionable health recommendations. These "
            "recommendations should address any identified health risks "
            "and provide guidance on diet, exercise, and other lifestyle factors."
        )
    },
    expected_output=(
        "A comprehensive set of health recommendations that include dietary suggestions, "
        "exercise plans, and other lifestyle adjustments. Each recommendation should be "
        "linked to the findings from the blood test and the supporting research, ensuring "
        "that the advice is both relevant and practical."
    )
)

