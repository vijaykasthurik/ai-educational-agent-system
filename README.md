# 🤖 AI Educational Agent System

A professional multi-agent AI system that generates and evaluates educational content using structured LLM workflows.

This project implements an Agent-Based AI Pipeline consisting of a Generator Agent and Reviewer Agent, designed to demonstrate real-world AI orchestration, structured outputs, and UI-driven workflow visualization.

---

## 🚀 Project Overview

This system simulates a real AI content pipeline:

1️⃣ Generator Agent creates educational content based on grade and topic  
2️⃣ Reviewer Agent evaluates the generated content  
3️⃣ If content fails evaluation → automatic refinement pass  
4️⃣ UI visually displays the agent workflow

The architecture focuses on clarity, determinism, and structured AI output.

---

## 🧠 Agent Architecture

### 🔵 Generator Agent

**Responsibility:**

- Generate educational explanation
- Create MCQs aligned with grade level

**Input (Structured JSON):**

{
"grade": 4,
"topic": "Types of angles"
}


**Output:**

{
"explanation": "...",
"mcqs": [
{
"question": "...",
"options": ["A","B","C","D"],
"answer": "B"
}
]
}


---

### 🟣 Reviewer Agent

**Responsibility:**

Evaluate Generator output based on:

- Age appropriateness
- Concept correctness
- Clarity

**Output:**

{
"status": "pass | fail",
"feedback": []
}


---

### 🔁 Refinement Logic

If Reviewer returns:

status = fail


The Generator Agent is re-executed with feedback embedded.

Only one refinement pass is allowed.

---

## 🎨 UI Features

✔ Triggers AI agent pipeline  
✔ Displays Generator Output  
✔ Shows Reviewer Feedback  
✔ Displays Refined Output (if applicable)  
✔ Visual agent workflow (Generator → Reviewer → Refinement)

---

## ⚙️ Tech Stack

- Python (Flask)
- Ollama (Local LLM)
- HTML / CSS / JavaScript
- Agent-based architecture

---

## 🧩 Project Structure

backend/
│
├── app.py
├── generator_agent.py
├── reviewer_agent.py
├── ollama_service.py
│
├── templates/
│ └── index.html
│
└── static/
├── style.css
└── script.js


---

## ▶️ How to Run

### 1️⃣ Install Ollama

ollama pull llama3


---

### 2️⃣ Install Dependencies

pip install -r requirements.txt


---

### 3️⃣ Run Application

cd backend
python app.py


Open:

http://127.0.0.1:5000


---

## 🎯 Key Highlights

- Multi-Agent AI workflow
- Deterministic structured outputs
- Local LLM integration (Ollama)
- Clean separation of responsibilities
- Professional UI workflow visualization

---

## 📌 Purpose

This project demonstrates the design and implementation of a lightweight AI agent system suitable for educational content generation and evaluation pipelines.

---

## 👨‍💻 Author

Vijay Kasthuri K
