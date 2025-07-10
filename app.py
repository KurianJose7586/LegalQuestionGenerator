import streamlit as st
import PyPDF2
import pdfplumber
import os
from groq import Groq
from io import StringIO
import re

# --- CONFIG ---
MAX_TOKENS = 15000
APP_TITLE = "Legal Question Generator"

# --- STREAMLIT SETUP ---
st.set_page_config(page_title=APP_TITLE, layout="centered", page_icon="📜")
st.title(APP_TITLE)
st.caption("Generate scenario-based MCQs from Indian constitutional law case briefs")

# --- UTILS ---
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def clean_text(text):
    return ' '.join(text.split())

def truncate_text(text, max_chars=MAX_TOKENS):
    return text[:max_chars]

def build_prompt(extracted_text, n_questions):
    return f'''
You are a highly trained legal tutor. Your job is to generate multiple choice questions from the following legal content. Use only scenario-based MCQs — questions based on hypothetical legal facts.

Instructions:
- Present a real-world scenario (2–4 lines).
- Ask a legal reasoning question about it.
- Provide 4 answer options, only one correct.
- After the options, write:
Correct Answer: [A/B/C/D]
Explanation: [1–2 sentence legal reasoning + case law]

Use Indian constitutional law cases, especially Article 21 topics like:
- Right to life, liberty, fair procedure, privacy, shelter
- D.K. Basu, Maneka Gandhi, Olga Tellis, Puttaswamy, etc.

Text: {extracted_text}
Generate {n_questions} MCQs from the above text.
'''

# --- GROQ API ---
def get_groq_api_key():
    return st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY")

def call_groq_api(prompt, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7):
    api_key = get_groq_api_key()
    if not api_key:
        st.error("Please set your GROQ_API_KEY in Streamlit secrets or environment variables.")
        return None
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=2048,
        stream=False
    )
    content = None
    if response and response.choices and response.choices[0].message and response.choices[0].message.content:
        content = response.choices[0].message.content.strip()
    return content

# --- PARSING ---
def parse_mcqs(raw_output):
    mcqs = []
    blocks = re.split(r'\n?\*?\*?\d+\.\*?\*?\n?', raw_output)
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        lines = block.split('\n')
        scenario = []
        options = []
        answer = ""
        explanation = ""
        state = "scenario"
        for line in lines:
            l = line.strip()
            if re.match(r"^[A-D][\).]", l):
                state = "options"
                options.append(l)
            elif l.startswith("Correct Answer:"):
                answer = l.replace("Correct Answer:", "").strip()
                state = "answer"
            elif l.startswith("Explanation:"):
                explanation = l.replace("Explanation:", "").strip()
                state = "explanation"
            elif state == "scenario":
                scenario.append(l)
            elif state == "options":
                options.append(l)
        if options and answer:
            mcqs.append({
                "scenario": " ".join(scenario),
                "options": options,
                "answer": answer,
                "explanation": explanation
            })
    return mcqs

# --- FORM ---
with st.form("pdf_form"):
    pdf_file = st.file_uploader("Upload a legal case brief (PDF)", type=["pdf"])
    n_questions = st.slider("How many questions?", 5, 30, 10)
    submitted = st.form_submit_button("Generate MCQs")

if pdf_file and submitted:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(pdf_file)
        text = clean_text(text)
        text = truncate_text(text)
    if not text or len(text) < 100:
        st.error("Failed to extract sufficient text from the PDF.")
    else:
        st.success("PDF text extracted successfully!")
        prompt = build_prompt(text, n_questions)
        with st.spinner("Generating MCQs using Groq API..."):
            try:
                output = call_groq_api(prompt)
            except Exception as e:
                st.error(f"Groq API error: {e}")
                output = None

        if output:
            st.success("MCQs generated!")
            mcqs = parse_mcqs(output)

            if not mcqs:
                st.warning("Could not parse MCQs. Showing raw output:")
                st.code(output)
            else:
                st.markdown(f"### {len(mcqs)} MCQs Generated:")
                for i, mcq in enumerate(mcqs, 1):
                    with st.expander(f"Question {i}"):
                        st.markdown(f"**Scenario:** {mcq['scenario']}")
                        st.markdown("\n".join(mcq['options']))
                        st.markdown(f"**Correct Answer:** {mcq['answer']}")
                        st.markdown(f"**Explanation:** {mcq['explanation']}")

                # --- Export ---
                def mcqs_to_md(mcqs):
                    out = StringIO()
                    for i, mcq in enumerate(mcqs, 1):
                        out.write(f"### Q{i}: {mcq['scenario']}\n")
                        for opt in mcq['options']:
                            out.write(f"{opt}\n")
                        out.write(f"**Correct Answer:** {mcq['answer']}\n")
                        out.write(f"**Explanation:** {mcq['explanation']}\n\n")
                    return out.getvalue()

                md = mcqs_to_md(mcqs)
                st.download_button("Download MCQs (Markdown)", md, file_name="mcqs.md", mime="text/markdown", key="download_md")
                st.download_button("Download MCQs (Text)", md, file_name="mcqs.txt", mime="text/plain", key="download_txt")
        else:
            st.error("Failed to generate MCQs. Please try again.")
else:
    st.info("Upload a PDF and select the number of questions to begin.")
