import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Configure the Generative AI API with your provided API key
genai.configure(api_key="AIzaSyDiKGPo8SeNlAqbb7QqXujtrzIt0o-4Oyo")

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert the PDF to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode(),  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def calculate_ats_score(response_text):
    """
    Parses the response text from the AI model to extract and display the ATS score.
    Assumes the AI response contains a percentage value.
    """
    try:
        # Extract percentage from the response text
        score = next((int(word.strip('%')) for word in response_text.split() if '%' in word), None)
        return score
    except Exception:
        return None

# Streamlit App

st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Add custom CSS for header, buttons, and background
st.markdown(
    """
    <style>
    /* Add background image */
    body {
        background-image: url('https://source.unsplash.com/1600x900/?coding,abstract');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    /* Style for the header */
    .centered-header {
        color: green; /* Green color */
        text-shadow: 3px 3px 6px black;
        font-family: 'Verdana', sans-serif;
        font-size: 36px;
        text-align: center;
        margin-bottom: 20px;
    }
    .header-underline {
        width: 50%;
        margin: 0 auto 20px;
        border-bottom: 3px solid white;
    }
    /* Style for buttons */
    .stButton > button {
        background-color: white; /* White button color */
        color: black;
        border: none;
        padding: 10px 20px;
        text-align: center;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: green; /* Green on hover */
        color: white; /* White text on hover */
    }
    /* Style for file uploader button */
    .stFileUploader label div {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        background-color: white;
        color: black;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        cursor: pointer;
    }
    .stFileUploader label div:hover {
        background-color: green; /* Green shade on hover */
        color: white; /* White text on hover */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header with centered text and underline
st.markdown("<h1 class='centered-header'>ATS TRACKING SYSTEM - BY VIVEK DESHMUKH</h1>", unsafe_allow_html=True)
st.markdown("<div class='header-underline'></div>", unsafe_allow_html=True)

# Text area and file uploader
input_text = st.text_area("ADD JOB DESCRIPTION HERE:", key="input")
uploaded_file = st.file_uploader("UPLOAD YOUR RESUME IN THE PDF FORMAT:", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Buttons
submit1 = st.button("TELL ME ABOUT THE RESUME")
submit3 = st.button("PERCENTAGE MATCH")
ats_score_button = st.button("SHOW ATS SCORE")

# Input prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage, then keywords missing, and lastly final thoughts.
"""

# Button actions
if submit1: 
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.write("PLEASE UPLOAD THE RESUME")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.write("PLEASE UPLOAD THE RESUME")

elif ats_score_button:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        ats_score = calculate_ats_score(response)
        if ats_score is not None:
            st.subheader(f"ATS Score: {ats_score}%")
            if ats_score > 75:
                st.success("Your resume matches well with the job description!")
            elif ats_score > 50:
                st.warning("Your resume has a moderate match. Consider improving it.")
            else:
                st.error("Your resume has a low match. Significant improvements are needed.")
        else:
            st.write("Unable to calculate ATS score. Please check the input.")
    else:
        st.write("PLEASE UPLOAD THE RESUME")
