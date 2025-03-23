import json
from main import search_dictionary, load_common_words

# Initialize the dictionary
load_common_words()

def test_fuzzy_search():
    """Test the fuzzy search with various typos and edge cases"""
    test_cases = [
        # Common typos
        ("pyhton", "python"),  # Letters swapped
        ("javscript", "javascript"),  # Missing letter
        ("programmming", "programming"),  # Extra letter
        ("algorythm", "algorithm"),  # Phonetic substitution
        ("datbase", "database"),  # Missing letter
        ("intrface", "interface"),  # Missing letter
        ("sekurity", "security"),  # Phonetic substitution
        ("networc", "network"),  # Phonetic substitution
        
        # Edge cases
        ("PYTHON", "python"),  # Capitalization
        ("  javascript  ", "javascript"),  # Extra whitespace
        ("data-base", "database"),  # With punctuation
        
        # More complex cases
        ("computr progrm", "computer"),  # Multiple errors
        ("authntication", "authentication"),  # Multiple missing letters
        ("algorythem", "algorithm")  # Phonetic + extra letter
    ]
    
    results = {}
    
    print("\n=== FUZZY SEARCH TEST RESULTS ===\n")
    print(f"{'INPUT':<20} | {'EXACT MATCH':<12} | {'RESULT/SUGGESTIONS':<40}")
    print("-" * 75)
    
    for test_input, expected in test_cases:
        result = search_dictionary(test_input)
        
        # Format result for display
        if result["exact_match"]:
            result_str = f"{result['word']} - {result['meaning'][:30]}..."
            success = result["word"] == expected
        else:
            suggestions_str = ", ".join(result["suggestions"][:3])
            result_str = f"Suggestions: {suggestions_str}"
            success = expected in result["suggestions"]
        
        status = "✅" if success else "❌"
        print(f"{test_input:<20} | {str(result['exact_match']):<12} | {result_str:<40} {status}")
        
        # Store results for analysis
        results[test_input] = {
            "expected": expected,
            "result": result,
            "success": success
        }
    
    # Summary
    success_count = sum(1 for r in results.values() if r["success"])
    print("\n=== SUMMARY ===")
    print(f"Total tests: {len(test_cases)}")
    print(f"Successful matches: {success_count}")
    print(f"Success rate: {success_count / len(test_cases) * 100:.1f}%")

if __name__ == "__main__":
    test_fuzzy_search()
