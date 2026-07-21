RESTful API for the SkillBridge freelance marketplace platform.

## Features

- User authentication with JWT
- Gig management (create, read, update, delete)
- Order management
- Reviews and ratings
- Password reset flow
- Role-based access control (freelancer vs client)
- PostgreSQL database (SQLite for development)

## Tech Stack

- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-Migrate 4.0.5
- Flask-CORS 4.0.1
- Flask-JWT-Extended 4.6.0
- PostgreSQL (production)
- SQLite (development)
- Gunicorn 21.2.0

## Database Models

| Model | Description |
|-------|-------------|
| User | User accounts with roles (freelancer/client) |
| Gig | Service listings created by freelancers |
| Order | Client orders with status tracking |
| Review | Client reviews and ratings |
| Tag | Categories for gigs |

### Model Relationships
- One User has many Gigs
- One User has many Orders
- One Gig has many Orders
- Many Gigs have many Tags

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/password-reset/request` | Request password reset |
| POST | `/api/auth/password-reset/confirm` | Confirm password reset |
| GET | `/api/gigs` | List all gigs |
| GET | `/api/gigs/<id>` | Get a single gig |

### Protected Endpoints

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/auth/me` | Get current user | Any |
| POST | `/api/gigs` | Create a gig | Freelancer |
| PUT | `/api/gigs/<id>` | Update a gig | Freelancer (owner) |
| DELETE | `/api/gigs/<id>` | Delete a gig | Freelancer (owner) |
| GET | `/api/orders` | Get user orders | Any |
| POST | `/api/orders` | Create an order | Client |
| PUT | `/api/orders/<id>` | Update order status | Client (owner) |
| DELETE | `/api/orders/<id>` | Cancel an order | Client (owner) |
| PUT | `/api/users/<id>` | Update user profile | User (owner) |
| DELETE | `/api/users/<id>` | Delete user | User (owner) |

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip
- PostgreSQL (optional for production)

### Installation

```bash
# Clone the repository
git clone https://github.com/olivermooz-117/skrill_bridge_backend.git
cd skrill_bridge_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# Set DATABASE_URL, SECRET_KEY, etc.

# Run the application
python run.py

# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_auth.py

Deployment

Live url
Backend API: https://skrill-bridge-backend.onrender.com