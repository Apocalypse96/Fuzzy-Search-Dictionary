from fastapi import FastAPI, HTTPException, Depends, status, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import json
from rapidfuzz import process, fuzz
import bcrypt
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import re
import string
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("Warning: python-dotenv not installed. Using default/system environment variables.")
    # Define a dummy function to prevent errors
    def load_dotenv():
        pass

# Constants from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "THIS_IS_A_SECRET_KEY_THAT_SHOULD_BE_REPLACED_IN_PRODUCTION")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENABLE_DEBUG_ENDPOINTS = os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() == "true"

# Try to load WordNet; if it fails, provide instructions
try:
    # Check if WordNet is available
    wn.synsets('test')
    print("WordNet loaded successfully!")
except LookupError:
    print("WordNet data not found. Run 'python download_nltk_data.py' to download.")
    # Continue with empty dictionary as fallback
    pass

# Initialize WordNet lemmatizer
lemmatizer = WordNetLemmatizer()

# Enhanced dictionary word cache with frequency information
DICTIONARY_WORDS = set()
DICTIONARY_CACHE = {}
WORD_FREQUENCY = {}  # Store word frequency for better suggestions

# Function to normalize words for better matching
def normalize_word(word: str) -> str:
    """Clean and normalize a word for better matching"""
    # Convert to lowercase and strip whitespace
    word = word.lower().strip()
    # Remove punctuation
    word = word.translate(str.maketrans('', '', string.punctuation))
    # Basic lemmatization (convert to base form)
    try:
        word = lemmatizer.lemmatize(word)
    except:
        pass  # If lemmatization fails, use the original word
    return word

# Enhanced function to get word meaning with fallbacks
def get_word_meaning(word: str) -> Optional[str]:
    """Get word definition with improved matching"""
    original_word = word
    word = word.lower()
    
    # Check if the exact word is in our cache
    if word in DICTIONARY_CACHE:
        # Increment word frequency counter
        WORD_FREQUENCY[word] = WORD_FREQUENCY.get(word, 0) + 1
        return DICTIONARY_CACHE[word]
    
    # Try different word forms
    normalized = normalize_word(word)
    if normalized != word and normalized in DICTIONARY_CACHE:
        WORD_FREQUENCY[normalized] = WORD_FREQUENCY.get(normalized, 0) + 1
        return DICTIONARY_CACHE[normalized]
    
    # Look up word in WordNet
    synsets = wn.synsets(word)
    if not synsets:
        # Try the normalized form if different
        if normalized != word:
            synsets = wn.synsets(normalized)
    
    if not synsets:
        # Try common spelling variations
        variations = generate_common_variations(word)
        for var in variations:
            if var in DICTIONARY_CACHE:
                return DICTIONARY_CACHE[var]
            temp_synsets = wn.synsets(var)
            if temp_synsets:
                synsets = temp_synsets
                break
    
    if synsets:
        # Combine the first few definitions
        definitions = []
        for synset in synsets[:3]:  # Limit to first 3 meanings for brevity
            definition = synset.definition()
            if definition and definition not in definitions:
                definitions.append(definition)
        
        if definitions:
            # Join definitions with semicolons
            meaning = "; ".join(definitions)
            
            # Cache both the original and normalized forms
            DICTIONARY_CACHE[word] = meaning
            if normalized != word:
                DICTIONARY_CACHE[normalized] = meaning
            
            # Add to word list for client-side filtering and update frequency
            DICTIONARY_WORDS.add(word)
            WORD_FREQUENCY[word] = WORD_FREQUENCY.get(word, 0) + 1
            
            return meaning
    
    return None

# Generate common spelling variations for a word
def generate_common_variations(word: str) -> List[str]:
    """Generate common spelling variations to handle typos"""
    variations = []
    
    # Handle doubled letters
    for i in range(len(word) - 1):
        if word[i] == word[i+1]:
            variations.append(word[:i+1] + word[i+2:])  # Remove one duplicate
    
    # Handle missing letters (simple case)
    for i in range(len(word) + 1):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            variations.append(word[:i] + c + word[i:])
    
    # Handle common letter swaps
    for i in range(len(word) - 1):
        swapped = word[:i] + word[i+1] + word[i] + word[i+2:]
        variations.append(swapped)
    
    # Handle common phonetic substitutions
    phonetic_subs = {
        'f': ['ph'], 'ph': ['f'],
        'c': ['k', 's'], 'k': ['c'], 's': ['c'],
        'z': ['s'], 's': ['z'],
        'g': ['j'], 'j': ['g'],
        'i': ['y'], 'y': ['i']
    }
    
    for i, char in enumerate(word):
        if char in phonetic_subs:
            for sub in phonetic_subs[char]:
                variations.append(word[:i] + sub + word[i+1:])
    
    return variations[:10]  # Limit to 10 variations to avoid explosion

# Multi-method fuzzy search with weighted scoring
def advanced_fuzzy_match(word: str, candidates: List[str], limit: int = 5) -> List[Tuple[str, float]]:
    """Use multiple fuzzy matching methods with weighted scoring"""
    if not word or not candidates:
        return []
    
    word = word.lower()
    
    # Different matchers with weights
    matchers = [
        (fuzz.ratio, 1.0),                 # Basic similarity
        (fuzz.partial_ratio, 0.9),         # Good for substrings
        (fuzz.token_sort_ratio, 0.8),      # Good for word order differences
        (fuzz.token_set_ratio, 0.7),       # Good for additional/missing words
    ]
    
    # Calculate scores using different methods
    candidate_scores = {}
    for candidate in candidates:
        candidate_lower = candidate.lower()
        
        # Skip exact match, it would be caught earlier
        if candidate_lower == word:
            continue
            
        weighted_score = 0
        for matcher, weight in matchers:
            score = matcher(word, candidate_lower)
            weighted_score += score * weight
            
        # Normalize the score
        final_score = weighted_score / sum(weight for _, weight in matchers)
        
        # Boost score based on word frequency if available
        freq_boost = min(WORD_FREQUENCY.get(candidate_lower, 0) * 0.5, 10)
        final_score += freq_boost
        
        candidate_scores[candidate] = final_score
    
    # Get top N results above threshold
    threshold = 60  # Minimum score to consider
    results = [(c, s) for c, s in candidate_scores.items() if s > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results[:limit]

# Enhanced search dictionary function
def search_dictionary(word: str) -> Dict:
    """Enhanced search function with better typo handling"""
    # Try to standardize the word first
    original_word = word
    word = word.lower().strip()
    
    # Check for exact match first
    meaning = get_word_meaning(word)
    if meaning:
        return {
            "exact_match": True,
            "word": word,
            "meaning": meaning
        }
    
    # If not exact, try normalized form
    normalized = normalize_word(word)
    if normalized != word:
        meaning = get_word_meaning(normalized)
        if meaning:
            return {
                "exact_match": True,
                "word": normalized,
                "meaning": meaning,
                "normalized_from": word
            }
    
    # No exact match, try advanced fuzzy matching
    suggestions = []
    
    # First try against our cached dictionary
    if DICTIONARY_WORDS:
        # Use advanced fuzzy matching with multiple algorithms
        matches = advanced_fuzzy_match(word, list(DICTIONARY_WORDS), limit=5)
        if matches:
            suggestions = [match[0] for match in matches]
    
    # If we don't have enough good suggestions, use WordNet
    if len(suggestions) < 3:
        # Try to find similar words in WordNet
        all_words = set()
        
        # First try with the original word
        synsets = wn.synsets(word)
        
        # If no synsets found, try with normalized word
        if not synsets and normalized != word:
            synsets = wn.synsets(normalized)
        
        # Collect lemmas from synsets
        for synset in synsets:
            all_words.update([lemma.name().lower() for lemma in synset.lemmas()])
            
            # Also check hypernyms and hyponyms for related words
            for hypernym in synset.hypernyms()[:2]:  # Limit to 2 hypernyms
                all_words.update([lemma.name().lower() for lemma in hypernym.lemmas()])
            
            for hyponym in synset.hyponyms()[:2]:  # Limit to 2 hyponyms
                all_words.update([lemma.name().lower() for lemma in hyponym.lemmas()])
        
        # If we found related words, try fuzzy matching against them
        if all_words:
            # Filter out multi-word phrases (contain underscore)
            single_words = [w for w in all_words if '_' not in w]
            
            if single_words:
                wordnet_matches = advanced_fuzzy_match(word, list(single_words), limit=3)
                wordnet_suggestions = [match[0] for match in wordnet_matches]
                
                # Add these to our suggestions, avoiding duplicates
                for suggestion in wordnet_suggestions:
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
    
    # If still no good suggestions, try common spelling variations
    if len(suggestions) < 3:
        variations = generate_common_variations(word)
        for var in variations:
            if get_word_meaning(var) and var not in suggestions:
                suggestions.append(var)
            if len(suggestions) >= 5:  # Limit to 5 total suggestions
                break
    
    # Return results
    if suggestions:
        return {
            "exact_match": False,
            "suggestions": suggestions[:5]  # Limit to 5 suggestions
        }
    
    return {
        "exact_match": False,
        "suggestions": []
    }

# Load some common words to populate the initial word list
def load_common_words():
    common_words = [
        "hello", "world", "python", "react", "javascript", "computer", "programming",
        "algorithm", "database", "interface", "security", "network", "internet",
        "authentication", "authorization", "dictionary", "language", "keyboard",
        "mouse", "screen", "software", "hardware", "function", "variable", "class",
        "object", "method", "property", "syntax", "semantics", "compiler", "interpreter",
        "browser", "server", "client", "request", "response", "protocol", "cookie",
        "session", "token", "api", "rest", "graphql", "json", "xml", "html", "css"
    ]
    
    for word in common_words:
        meaning = get_word_meaning(word)
        if meaning:
            DICTIONARY_WORDS.add(word)
            WORD_FREQUENCY[word] = 1  # Initialize frequency

# Initialize common words
load_common_words()

# Generate a new hash for "password" using direct bcrypt, not passlib
def generate_password_hash():
    password = "password"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

# Create a fresh hash compatible with the current bcrypt version
admin_password_hash = generate_password_hash()

# Mock user database with freshly generated hash
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": admin_password_hash,  # Freshly generated hash for "password"
    }
}

print(f"Generated admin password hash: {admin_password_hash}")

# App initialization
app = FastAPI(title="Secure Fuzzy Dictionary API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # React app address from .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modified password verification using direct bcrypt, not passlib context
def verify_password(plain_password, hashed_password):
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

# Rest of the authentication code
def get_password_hash(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

# Keep existing PassLib context for compatibility with other functions
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class SearchRequest(BaseModel):
    word: str

class SearchResponse(BaseModel):
    exact_match: bool
    word: Optional[str] = None
    meaning: Optional[str] = None
    suggestions: Optional[List[str]] = None

# Authentication functions
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # Use our direct bcrypt verification instead of pwd_context
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Modified to accept tokens from cookies or Authorization header
async def get_current_user_from_cookie_or_header(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(default=None)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from cookie if not in header
    if not token and access_token:
        token = access_token
    
    # If still no token, check request cookies directly
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(USERS_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Standard OAuth2 user dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(USERS_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(USERS_DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set HTTP-only cookie with the token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",  # Protects against CSRF in modern browsers
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@app.get("/user", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Updated search endpoint with enhanced error handling
@app.post("/search", response_model=SearchResponse)
async def search_word(
    search_req: SearchRequest, 
    current_user: User = Depends(get_current_user_from_cookie_or_header)
):
    try:
        result = search_dictionary(search_req.word)
        return result
    except Exception as e:
        print(f"Error processing search: {e}")
        # Return a fallback response instead of crashing
        return {
            "exact_match": False,
            "suggestions": []
        }

# For cookie-based authentication
@app.get("/validate-session")
async def validate_session(access_token: str = Cookie(None)):
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            return {"is_authenticated": True, "username": username}
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    raise HTTPException(status_code=401, detail="Not authenticated")

# Only include debug endpoint if enabled
if ENABLE_DEBUG_ENDPOINTS:
    # Debug endpoint for troubleshooting
    @app.get("/debug-auth")
    async def debug_auth(request: Request):
        """Debug endpoint to check token presence in different locations"""
        auth_header = request.headers.get("Authorization")
        cookies = request.cookies
        
        result = {
            "auth_header_present": auth_header is not None,
            "cookies": {k: "PRESENT" for k in cookies.keys()},
            "access_token_cookie": cookies.get("access_token") is not None
        }
        
        if cookies.get("access_token"):
            try:
                payload = jwt.decode(cookies.get("access_token"), SECRET_KEY, algorithms=[ALGORITHM])
                result["token_decode_success"] = True
                result["username"] = payload.get("sub")
                result["token_expiry"] = payload.get("exp")
            except Exception as e:
                result["token_decode_success"] = False
                result["decode_error"] = str(e)
        
        return result

# Updated endpoint to return dictionary words from WordNet
@app.get("/dictionary-words")
async def get_dictionary_words(current_user: User = Depends(get_current_user_from_cookie_or_header)):
    """Return a list of all dictionary words for client-side filtering"""
    # Return current dictionary words (this will grow as users search)
    word_list = list(DICTIONARY_WORDS)
    
    # If we have too few words, add some common ones
    if len(word_list) < 20:
        # Add more words from WordNet's common synsets
        common_synsets = wn.all_synsets()
        sample_words = []
        for synset in list(common_synsets)[:50]:  # First 50 synsets
            lemmas = synset.lemmas()
            if lemmas:
                sample_words.append(lemmas[0].name())
        
        word_list.extend(sample_words)
        word_list = list(set(word_list))  # Remove duplicates
    
    return {"words": word_list[:1000]}  # Limit to 1000 words max

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("BACKEND_HOST", "0.0.0.0"), 
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=DEBUG
    )