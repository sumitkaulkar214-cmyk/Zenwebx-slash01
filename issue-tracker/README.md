# Issue Tracker

A simplified Jira-clone REST API built with FastAPI, SQLAlchemy, and SQLite.

## Prerequisites
- Python 3.11+

## Setup

1. **Clone the repository:**
   ```bash
   # Clone the repository to your local machine
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore the API.
