# 📜 Legal Question Generator

A Streamlit app that reads Indian constitutional law case briefs (PDFs) and generates scenario-based multiple choice questions (MCQs) using an LLM via the Groq API.

This project explores **agentic AI**—systems that perform multi-step tasks independently—and applies it to **legal education**.

---

## 🧠 What It Does

- 📂 Upload a legal case brief (PDF)
- 🤖 Extracts and cleans the text
- 🔍 Sends a structured prompt to a Groq-hosted LLaMA model
- ❓ Generates MCQs focused on **Article 21** themes (e.g., life, liberty, privacy)
- ✅ Displays correct answers with legal reasoning
- 📥 Export results in Markdown or plain text

---

## 🛠 Tech Stack

- Python + Streamlit  
- `pdfplumber` + `PyPDF2` for PDF parsing  
- Groq API with LLaMA-4  
- Simple regex-based output parser

---

## 🚀 Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/legal-question-generator.git
   cd legal-question-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Groq API key:  
   Set it as an environment variable or add to `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_api_key_here"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

---

## 📌 Notes

- Currently optimized for Indian constitutional law content  
- Focuses on **Article 21** cases like *Maneka Gandhi*, *Puttaswamy*, *D.K. Basu*, etc.  
- Not production-ready — built for experimentation and learning

---

## 🧪 Why This?

To practice building small agentic AI tools that chain together:
- PDF extraction → prompt engineering → model response → structured output → user interaction

---

## 📄 License

MIT License
