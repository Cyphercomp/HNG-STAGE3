Insighta Labs+ - Profile Intelligence System
📌 Project Overview
Insighta Labs+ is a production-ready, multi-interface profile management system designed for Stage 3 requirements. It features a robust Django REST API, a Python-based CLI, and an Analyst Web Portal. The system implements secure GitHub OAuth2 with PKCE, Role-Based Access Control (RBAC), and Natural Language (NL) search capabilities.

🏗 System Architecture
The project is decoupled into three primary components:

Backend (Django REST Framework): The core engine handling data persistence, security, and the NLP parsing logic.

CLI (Python/Click/Rich): A powerful terminal tool for automated intelligence gathering, using PKCE for secure authentication.

Web Portal (JavaScript): A dashboard for human analysts to visualize data and perform exports using secure HTTP-only cookies.

🔐 Security & Authentication
GitHub OAuth2 with PKCE: Proof Key for Code Exchange (PKCE) is implemented to secure the authentication flow for public clients (CLI).

JWT Lifecycle: Access tokens (3 mins) and Refresh tokens (5 mins) with mandatory rotation.

RBAC: Roles are divided into admin (Full CRUD) and analyst (Read-Only + Export).

Rate Limiting: Anonymous users are limited to 10 requests/minute on authentication endpoints to prevent brute-force attacks.

🧠 Natural Language Parsing Logic
The system implements a custom filter backend using PostgreSQL Full-Text Search (FTS). It translates natural language strings into database queries:

Gender detection: Identifies "male", "female", "men", "women".

Nationality detection: Maps country names/codes (e.g., "Nigeria", "RW").

Age groups: Handles keywords like "young" (<30) and "senior" (>60).

🚀 Installation & Setup

cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

🛠 API Endpoints
GET /auth/github: Initiates OAuth flow.

POST /auth/github/callback: Finalizes authentication (State & PKCE validation).

GET /api/profiles/: List/Search profiles (Requires X-API-Version: 1).

GET /api/profiles/export: Download timestamped CSV.

🤝 Conventional Commits
This project follows strict conventional commit standards:

feat(scope): New features.

fix(scope): Bug fixes.

docs(scope): Documentation updates.