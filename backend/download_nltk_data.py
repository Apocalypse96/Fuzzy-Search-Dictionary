import nltk
import os
import sys

def download_wordnet():
    """Download WordNet data for NLTK."""
    print("Downloading WordNet data...")
    try:
        nltk.download('wordnet')
        nltk.download('omw-1.4')  # Open Multilingual WordNet
        print("WordNet data downloaded successfully!")
        return True
    except Exception as e:
        print(f"Error downloading WordNet data: {e}")
        return False

if __name__ == "__main__":
    success = download_wordnet()
    sys.exit(0 if success else 1)
