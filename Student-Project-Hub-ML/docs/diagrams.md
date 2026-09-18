# Diagram Guide

These Mermaid diagrams can be pasted into a Mermaid-compatible editor or drawn manually for the report.

## System Architecture
```mermaid
flowchart LR
A[Student Browser] --> B[Flask Application]
B --> C[Authentication]
B --> D[Project Management]
B --> E[Search and Filters]
B --> F[Recommendation Module]
C --> G[(SQLite Database)]
D --> G
E --> G
F --> G
```

## Workflow
```mermaid
flowchart TD
A[Open Hub] --> B{Logged in?}
B -- No --> C[Register / Login]
B -- Yes --> D[Dashboard]
C --> D
D --> E{Choose action}
E --> F[Create Project]
E --> G[Explore Projects]
E --> H[Update Profile]
G --> I[View Project]
I --> J[Request to Join]
I --> K[View Similar Projects]
F --> L[(Database)]
J --> L
H --> L
```

## Use Case
```mermaid
flowchart LR
S((Student))
S --> A[Register/Login]
S --> B[Manage Profile]
S --> C[Create Project]
S --> D[Search Projects]
S --> E[View Project]
S --> F[Request to Join]
S --> G[View Recommendations]
```

## Class/Component
```mermaid
classDiagram
class Student {
  id
  name
  email
  branch
  year
  skills
}
class Project {
  id
  title
  description
  domain
  technologies
  difficulty
  team_size
  status
}
class JoinRequest {
  id
  project_id
  student_id
  message
  status
}
Student "1" --> "*" Project : owns
Student "1" --> "*" JoinRequest : sends
Project "1" --> "*" JoinRequest : receives
```

## Sequence: Add Project
```mermaid
sequenceDiagram
participant U as Student
participant B as Browser
participant F as Flask
participant DB as SQLite
U->>B: Fill project form
B->>F: POST /project/new
F->>DB: INSERT project
DB-->>F: Success
F-->>B: Redirect to dashboard
B-->>U: Project displayed
```

## ER Diagram
```mermaid
erDiagram
STUDENT ||--o{ PROJECT : owns
STUDENT ||--o{ JOIN_REQUEST : sends
PROJECT ||--o{ JOIN_REQUEST : receives
STUDENT {
 int id PK
 string name
 string email
 string password
 string branch
 int year
 string skills
}
PROJECT {
 int id PK
 string title
 string description
 string domain
 string technologies
 string difficulty
 int team_size
 string github_link
 string demo_link
 string status
 int owner_id FK
}
JOIN_REQUEST {
 int id PK
 int project_id FK
 int student_id FK
 string message
 string status
}
```
