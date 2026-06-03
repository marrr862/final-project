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

API Endpoints
GET /
GET /health
POST /login
GET /protected
POST /events
GET /events
GET /analytics/summary
GET /analytics/users
GET /analytics/pages
GET /analytics/events
GET /analytics/categories
GET /analytics/engagement
GET /fraud/users
GET /recommendations/{user_id}


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


