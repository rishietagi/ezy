from crewai import Task
from agents import blood_test_analyst, article_researcher, health_advisor

# Define tasks
analyze_blood_test_task = Task(
    description='''
    You will be analyzing the following blood test report:
    "{text}"

    Instructions:
    1. Review each test result in the report.
    2. Identify the test name, the value, and the normal range.
    3. Compare the test value to the normal range:
        - If the value is within the normal range, note that it is normal.
        - If the value is outside the normal range, highlight it and explain the potential implications.
    4. Provide a comprehensive summary including:
        - An overview of all test results.
        - A detailed analysis of any abnormal values.
        - Potential implications of the abnormal results.
        - Suggestions for further investigation if needed.
    ''',
    expected_output='A comprehensive summary of the blood test results, highlighting abnormal values with explanations and potential implications.',
    agent=blood_test_analyst,
)

find_articles_task = Task(
    description='''
    Following the analysis of the blood test report, perform the following tasks:
    1. Identify key health concerns or issues highlighted by the abnormal values in the blood test report.
    2. Search the web for 3-5 recent, high-quality medical articles that are directly related to each identified health concern.
    3. For each selected article, provide:
        - The full title and author(s) of the article.
        - A concise summary of the main findings or recommendations.
        - A clear explanation of how the article's findings relate to the blood test results.
    ''',
    expected_output='A list of 3-5 carefully selected medical articles with summaries and relevance to the blood test results.',
    agent=article_researcher,
    context=[analyze_blood_test_task]
)

provide_recommendations_task = Task(
    description='''
    Based on the detailed analysis of the blood test report and the relevant articles, provide comprehensive health recommendations:
    1. Summarize the key findings from the blood test report and articles.
    2. Identify the main health concerns highlighted by the test results and articles.
    3. Recommend any additional tests or follow-ups that may be necessary for further evaluation.
    4. Offer actionable lifestyle advice aimed at improving overall health, considering the specific findings of the blood test.
    5. Include links to the referenced articles or additional trusted resources for further reading.
    ''',
    expected_output='A set of prioritized health recommendations, including a summary of findings, suggestions, and lifestyle advice.',
    agent=health_advisor,
    context=[analyze_blood_test_task, find_articles_task]
)
#general purpose
identify_and_analyze_report_task = Task(
    description='''
    You will be identifying and analyzing the uploaded report document:
   "{text}"

    Instructions:
    1. Verify if the uploaded document belongs to the medical field. 
        - If it is not a medical document, immediately reject it with the response: 
          "The uploaded document is not a medical report."
    2. If the document is a medical report, identify the type of report (e.g., Blood Test, Lipid Profile, Thyroid Function Test, etc.).
    3. For recognized medical reports:
        - Extract the relevant parameters, values, and any reference ranges provided in the document.
        - Compare each parameter's value to its reference range:
            - If the value is within the normal range, note it as normal.
            - If the value is outside the normal range, highlight it and explain the potential medical implications.
        - Provide actionable insights specific to the identified report type, such as:
            - Health precautions or dietary adjustments.
            - Potential medications or supplements (with a disclaimer to consult a licensed physician).
            - Recommendations for further testing or clinical evaluations if required.
        - Tailor insights based on patient details (e.g., age, gender, or medical history) if available.
    4. Summarize the findings in a structured, patient-friendly format.
    ''',
    expected_output='''
    1. For non-medical documents: "The uploaded document is not a medical report."
    2. For identified medical reports:
        - Report type (e.g., Blood Test, Lipid Profile, etc.).
        - Key findings, including normal and abnormal values.
        - Detailed implications of abnormal results with potential health risks explained.
        - Actionable recommendations, including precautions, lifestyle changes, and additional tests if needed.
        - The output should start with the patient’s name (if available), age, and identified report type.
    ''',
    agent=medical_report_analyst,
)

find_relevant_articles_task = Task(
    description='''
    Following the identification and analysis of the medical report, perform the following tasks:
    1. Based on the findings, identify key health concerns or issues associated with abnormal values.
    2. Search the web for 3-5 high-quality, recent medical articles related to each identified health concern.
    3. For each selected article, provide:
        - The full title and author(s) of the article.
        - A brief summary of the main findings or recommendations.
        - A clear explanation of how the article’s findings correlate with the test results and identified health concerns.
    4. Ensure the articles come from reliable medical sources (e.g., PubMed, WHO, or trusted medical journals).
    ''',
    expected_output='A list of 3-5 relevant, high-quality medical articles with summaries and their relevance to the identified health concerns from the report.',
    agent=article_researcher,
    context=[identify_and_analyze_report_task]
)

provide_actionable_recommendations_task = Task(
    description='''
    Based on the analysis of the medical report and insights from the relevant articles, provide comprehensive recommendations:
    1. Summarize the key findings from the report analysis and articles.
    2. Highlight the main health concerns and risks identified.
    3. Recommend additional tests, clinical evaluations, or follow-ups to address the findings.
    4. Provide detailed lifestyle advice, including:
        - Dietary recommendations tailored to the findings.
        - Exercise or wellness routines for overall health improvement.
    5. Suggest potential supplements or medications for minor corrections (with a disclaimer to consult a licensed medical professional).
    6. Provide links to referenced articles and additional trusted resources for further reading.
    ''',
    expected_output='A structured set of recommendations that include a summary of findings, health risks, actionable lifestyle changes, and any necessary follow-ups.',
    agent=health_advisor,
    context=[identify_and_analyze_report_task, find_relevant_articles_task]
)
