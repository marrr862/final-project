# User Behavior Analytics Platform

A real-time user behavior analytics platform built with FastAPI, PostgreSQL, Kafka, Spark, Streamlit, Docker and Railway Cloud.

## Features

- User event tracking
- REST API with FastAPI
- PostgreSQL database
- Kafka producer and consumer
- Spark streaming analytics
- Streamlit dashboard
- Fraud detection
- Engagement analytics
- Session analytics
- Recommendation system
- CSV and Excel export
- Cloud deployment on Railway

## Architecture

```text
User
 ↓
FastAPI API
 ↓
PostgreSQL

FastAPI
 ↓
Kafka Producer
 ↓
Kafka Consumer

Kafka
 ↓
Spark Streaming
 ↓
Analytics

Dashboard
 ↓
Railway Cloud API



Technologies
Python
FastAPI
PostgreSQL
SQLAlchemy
Kafka
Spark
Streamlit
Plotly
Docker
Railway
GitHub

Technologies
Python
FastAPI
PostgreSQL
SQLAlchemy
Kafka
Spark
Streamlit
Plotly
Docker
Railway
GitHub

Local Run
docker compose up --build

Open
http://localhost:8000/docs

Dashboard
streamlit run dashboard/app.py

Open
http://localhost:8501

Cloud Deployment(backend is deployed on Railway)
https://web-production-30c3e.up.railway.app/docs

Project Result
The project demonstrates a complete real-time analytics system with event collection, cloud API, database storage, streaming pipeline, fraud detection, recommendations and interactive dashboard visualization.


## 3. commit

```bash
git add .
git commit -m "add README"
git push