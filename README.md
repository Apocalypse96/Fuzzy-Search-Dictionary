# Secure Fuzzy Search Dictionary




A secure dictionary application with fuzzy search capabilities. Users must log in to access the dictionary. When searching for words, the system finds exact matches or suggests the closest matching words.

## Features

- Session-based authentication using HTTP-only cookies
- Protected routes requiring authentication
- Fuzzy search dictionary using RapidFuzz algorithm
- Recent search history stored in localStorage
- Clean UI with Tailwind CSS

## Tech Stack

- **Frontend**: React, React Router, Context API, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Authentication**: JWT with HTTP-only cookies
- **Search Algorithm**: RapidFuzz for fuzzy matching

## Getting Started

### Backend

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Install dependencies:
[Screencast from 2025-03-24 15-22-45.webm](https://github.com/user-attachments/assets/3301a27c-d6a0-4b09-9c86-8941f8fe3b77)

   ```
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to the frontend directory:

   ```
   cd frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Usage

1. Access the application at http://localhost:3000
2. Login with the test credentials:
   - Username: `admin`
   - Password: `password`
3. Search for words in the dictionary
4. Click on suggestions to find the right word

## API Endpoints

- `POST /token` - Login and get access token
- `POST /logout` - Logout and clear session
- `GET /validate-session` - Validate user session
- `POST /search` - Search for word in dictionary
