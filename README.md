# 🛡️ Autonomous Fraud Investigation System

An AI-powered system that not only detects fraud but **investigates relationships between entities using Graph Intelligence, AI Agents, and RAG-based reasoning**.

> ⚡ Unlike traditional fraud detection systems that only score transactions, this system **analyzes networks, explains decisions, and simulates real-world fintech investigation workflows**.

---

## 🚀 Features

- 🧠 **AI-Based Fraud Detection**
  - Risk scoring using intelligent rules + ML-style logic
- 🌐 **Graph Intelligence (Neo4j)**
  - Detects hidden relationships between users, devices, and transactions
- 🔍 **Relationship-Based Fraud Analysis**
  - Identifies fraud rings, shared devices, suspicious clusters
- 📊 **Interactive Dashboard**
  - Real-time visualization of fraud insights
- 🤖 **AI Investigation Agent**
  - Explains *why* a transaction is fraudulent
- 📚 **RAG (Retrieval-Augmented Generation)**
  - Uses past fraud cases to improve reasoning
- 🔗 **Automation Ready (n8n)**
  - Extendable to real-world alerting workflows

---

## 🧠 Problem Statement

Traditional fraud detection systems:
- Work on **isolated transactions**
- Generate **high false positives**
- Lack **explainability**

Modern systems are shifting toward:
- Graph-based fraud detection
- AI-driven investigation pipelines
- Explainable decision systems :contentReference[oaicite:0]{index=0}

👉 This project simulates that **next-generation fraud investigation system**.

---

## 🏗️ System Architecture
```bash
Frontend (Next.js Dashboard)
↓
Backend (FastAPI)
↓
PostgreSQL (Transactions DB)
↓
Neo4j (Graph Intelligence)
↓
RAG + AI Agents
↓
(Optional) n8n Automation
```

---

## 📊 Workflow

1. User submits transaction / user_id
2. Backend calculates fraud risk score
3. Graph DB analyzes relationships
4. RAG retrieves similar fraud cases
5. AI Agent generates explanation
6. Frontend displays:
   - Risk Score
   - Graph Intelligence
   - Investigation Report

---

## 🖥️ Tech Stack

### 🔹 Backend
- FastAPI
- Python
- SQLAlchemy

### 🔹 Frontend
- Next.js 15
- TypeScript
- Tailwind CSS

### 🔹 Databases
- PostgreSQL (Relational Data)
- Neo4j (Graph Data)

### 🔹 AI Layer
- RAG (Custom embeddings)
- AI Agents (Explainability + reasoning)

### 🔹 DevOps
- Docker & Docker Compose

---

## ⚙️ Installation & Setup

### 🔹 Prerequisites
- Docker Desktop
- Git

---

### 🔹 Run the project

```bash
git clone https://github.com/sathwik27-ai/Autonomous_Fraud_Investigation.git
cd Autonomous_Fraud_Investigation
docker compose up --build
```
🔹 Access Applications
🌐 Frontend → http://localhost:3000
⚙️ Backend API → http://localhost:8000/docs
🧠 Neo4j → http://localhost:7474
🔁 n8n → http://localhost:5678

📈 Impact
Detects fraud beyond rule-based systems
Uses graph relationships instead of isolated data
Reduces false positives using network intelligence
Simulates real fintech fraud investigation pipelines

Modern fraud systems increasingly rely on:

Graph analysis
AI reasoning
Real-time pipelines

🔥 Key Highlight
💡 “This system doesn’t just detect fraud — it investigates it.”

🧪 Example Use Case
User A makes transaction
System detects:
Same device used by 3 accounts
Suspicious transfer pattern
Graph reveals fraud ring
AI explains:
👉 “Linked to known fraudulent cluster”
🧩 Future Improvements
Real-time streaming (Kafka)
Advanced ML models (XGBoost / DL)
Cloud deployment (AWS/GCP)
Real payment gateway integration
Production-grade monitoring
👨‍💻 Contributors
~Sathwik
~Rochita
⭐ Final Note

This project demonstrates:

Full-stack engineering
AI + Graph integration
Real-world fintech system design

👉 Designed to showcase industry-level system thinking, not just coding.
