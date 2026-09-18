# Student Project Hub — Project Report Content

## 1. Introduction
Student Project Hub is a college-oriented web application that organizes student academic projects in one place. It allows students to maintain a profile, publish projects, discover projects by domain or technology, and request to collaborate.

## 2. Problem Statement
Students commonly depend on scattered class groups and personal contacts to find project examples or teammates. This project provides a structured searchable platform for the same purpose.

## 3. Objectives
- Provide a central project catalogue.
- Allow students to publish and manage their own projects.
- Make projects searchable by keywords, domain and difficulty.
- Support basic project collaboration requests.
- Demonstrate a simple content-based recommendation approach.

## 4. Functional Requirements
### FR1 Student account
The system shall allow registration and login.

### FR2 Profile
A logged-in student shall be able to update skills.

### FR3 Project management
A student shall be able to create and delete their own project listing.

### FR4 Project discovery
Users shall be able to search and filter projects.

### FR5 Collaboration
A logged-in student shall be able to send a request to join another project.

### FR6 Recommendation
The system shall display projects with overlapping domain/technology terms.

## 5. Non-Functional Requirements
- Usability: pages should have simple navigation and readable forms.
- Security: passwords are stored using password hashing.
- Reliability: invalid login and duplicate requests are handled without crashing.
- Maintainability: routes, templates, tests and recommendation logic are separated.
- Resource efficiency: SQLite is sufficient for a small academic prototype.
- Error handling: required fields and database uniqueness constraints are checked.

## 6. System Architecture
Browser → Flask routes → application logic → SQLite database.
The recommendation module reads project information and calculates simple similarity based on shared terms.

## 7. Workflow
Register/Login → Dashboard → Create or Explore Project → View Project → Optional Join Request → Recommendation.

## 8. Use Cases
Actors: Student.
Use cases: Register, Login, Manage Profile, Add Project, Delete Own Project, Search Projects, View Project, Request to Join.

## 9. Data Design
Students, Projects and Join Requests are the three main tables.

Relationship:
Student 1 — N Project
Student 1 — N Join Request
Project 1 — N Join Request

## 10. Recommendation Logic
For a selected project, the system creates a set of lowercase terms from its domain and technologies. Candidate projects receive a score equal to the number of shared terms. A small bonus is added when the domain is the same. The highest scoring projects are shown.

## 11. Testing
The test file checks:
- Home page loads.
- Registration works.
- Login works.
- Project discovery page loads.

## 12. Challenges
Potential implementation challenges include managing login sessions, maintaining relationships between projects and students, validating duplicate collaboration requests, and keeping recommendation logic understandable.

## 13. Learnings
The project demonstrates Flask routing, HTML forms, SQLite CRUD operations, sessions, password hashing, modular Python code, testing, and Git-based project organization.

## 14. Future Enhancements
Institutional login verification, moderation, notifications, file uploads, bookmarks, ratings, and a TF-IDF/cosine-similarity recommendation model can be added later.

## 15. References
- Python documentation
- Flask documentation
- SQLite documentation
- Werkzeug documentation
