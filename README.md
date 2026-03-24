# Codara - Python Learning Platform

A full-stack web application for learning Python through structured practice with real code execution.

## Tech Stack

- **Frontend**: React + Vite + Monaco Editor
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (running locally or cloud instance)

## Project Structure

```
codara/
├── backend/           # FastAPI backend
│   ├── main.py       # Application entry point
│   ├── routes.py     # API endpoints
│   ├── models.py     # Pydantic models
│   ├── database.py   # MongoDB connection
│   ├── executor.py   # Code execution engine
│   ├── seed_data.py  # Sample level data
│   └── requirements.txt
│
└── frontend/         # React frontend
    ├── src/
    │   ├── pages/    # Home, Levels, Practice, Dashboard
    │   ├── components/
    │   ├── api.js    # API service
    │   └── index.css
    └── package.json
```

## Setup Instructions

### 1. Start MongoDB

Make sure MongoDB is running:
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas cloud
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/levels` | Get all 5 array levels |
| GET | `/levels/{id}` | Get specific level details |
| POST | `/execute` | Execute user code with test cases |
| POST | `/submit` | Submit solution and track progress |
| GET | `/progress` | Get user progress stats |
| GET | `/daily-task` | Get daily challenge based on performance |
| GET | `/attempts` | Get recent attempts |

## Features

1. **Level-based Learning**: 5 array problems with increasing difficulty
2. **Monaco Editor**: Professional code editing experience
3. **Real Code Execution**: Code runs in sandboxed subprocess with timeout
4. **Test Case Evaluation**: Each solution tested against multiple test cases
5. **Progress Tracking**: Stats stored in MongoDB
6. **Daily Tasks**: Personalized challenges based on weak areas

## Sample Levels

1. **Array Basics** (Easy) - Sum all elements
2. **Find Maximum** (Easy) - Find the largest element
3. **Array Reversal** (Medium) - Reverse an array
4. **Two Sum** (Medium) - Find indices that sum to target
5. **Remove Duplicates** (Hard) - Remove duplicates from sorted array

## Environment Variables

Backend supports these environment variables (optional):

```
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=codara
```

## Running in Production

```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Serve the dist folder
```
