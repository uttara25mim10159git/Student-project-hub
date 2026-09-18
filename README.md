# Student Project Hub

## 1. Overview
Student Project Hub is a small web application for college students to discover academic projects, showcase their own work, and send collaboration requests.

## 2. Main Features
- Student registration and login
- Student profile and skills
- Create and delete project listings
- Search and filter projects
- Project details with GitHub/demo links
- Collaboration requests
- Simple content-based project recommendations
- SQLite database
- Basic automated tests

## 3. Technologies
- Python
- Flask
- SQLite
- HTML/CSS/Jinja
- Git/GitHub
- Python standard library for the recommendation logic

## 4. Project Structure
`app.py` contains the Flask routes and database setup. `templates/` contains the pages, `static/` contains CSS, `ml/` contains the recommendation logic, and `tests/` contains validation tests.

## 5. How to Run

### Windows
1. Install Python 3.
2. Open Command Prompt in this folder.
3. Create a virtual environment:
   `python -m venv .venv`
4. Activate it:
   `.venv\Scripts\activate`
5. Install dependencies:
   `python -m pip install -r requirements.txt`
6. Start the application:
   `python app.py`
7. Open `http://127.0.0.1:5000/` in your browser.

The SQLite database is created automatically on first run.

## 6. Testing
Run:
`python -m pytest`

## 7. Important Note
This is an academic prototype. For a real deployment, the secret key, database configuration, file uploads, access control, CSRF protection, and production server configuration should be strengthened.

## 8. Future Enhancements
- Institution-specific student verification
- Project file/document upload
- Approval/moderation workflow
- Notifications
- Better recommendation model using TF-IDF/cosine similarity
- Project ratings and bookmarks


## ML component

This version includes a real machine-learning layer:
- **Project domain classifier:** TF-IDF text features + Logistic Regression, trained from `ml/project_dataset.csv`.
- **Similar-project recommender:** TF-IDF vectors + cosine similarity over project title, description, domain and technologies.
- The classifier is trained with `python ml/train_model.py` and saved as `ml/project_classifier.joblib`.

### Install ML dependencies
`python -m pip install -r requirements.txt`

### Train/retrain the classifier
`python ml/train_model.py`

### Run
`python app.py`
Then open `http://127.0.0.1:5000`.
