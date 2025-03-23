import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import {
  MagnifyingGlassIcon,
  ArrowRightIcon,
  BookOpenIcon,
  ClockIcon,
  ArrowLeftOnRectangleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/solid";
import { FaLightbulb } from "react-icons/fa";

// Add debounce utility function
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

const Dictionary = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [recentSearches, setRecentSearches] = useState([]);
  const [suggestions, setSuggestions] = useState([]); // For real-time suggestions
  const [typingTimeout, setTypingTimeout] = useState(0);
  const [cachedWords, setCachedWords] = useState([]); // For client-side filtering
  const [isLoadingCache, setIsLoadingCache] = useState(true); // Track initial loading

  const { user, logout, searchWord } = useAuth();
  const navigate = useNavigate();
  const searchInputRef = useRef(null);

  // Load dictionary words for client-side filtering
  useEffect(() => {
    const fetchDictionaryWords = async () => {
      try {
        // Fetch a list of all words from the backend
        const response = await axios.get(
          "http://localhost:8000/dictionary-words",
          {
            withCredentials: true,
          }
        );
        setCachedWords(response.data.words || []);
      } catch (err) {
        console.error("Failed to load dictionary words cache:", err);
        // If fetch fails, we'll fall back to backend search
        setCachedWords([]);
      } finally {
        setIsLoadingCache(false);
      }
    };

    fetchDictionaryWords();
  }, []);

  // Load recent searches from localStorage
  useEffect(() => {
    const savedSearches = localStorage.getItem("recentSearches");
    if (savedSearches) {
      try {
        setRecentSearches(JSON.parse(savedSearches));
      } catch (e) {
        console.error("Error parsing recent searches:", e);
      }
    }
  }, []);

  // Save recent searches to localStorage
  const saveSearch = (word, isExactMatch, meaning = null) => {
    const search = {
      word,
      timestamp: new Date().toISOString(),
      isExactMatch,
      meaning: isExactMatch ? meaning : null,
    };

    const updatedSearches = [
      search,
      ...recentSearches.filter((s) => s.word !== word),
    ].slice(0, 5);
    setRecentSearches(updatedSearches);
    localStorage.setItem("recentSearches", JSON.stringify(updatedSearches));
  };

  // Client-side filtering function
  const filterWordsByPrefix = (prefix) => {
    if (!prefix || prefix.length < 2 || cachedWords.length === 0) return [];

    const lowerPrefix = prefix.toLowerCase();
    return cachedWords
      .filter((word) => word.toLowerCase().startsWith(lowerPrefix))
      .slice(0, 5); // Limit to 5 suggestions
  };

  // Enhanced fetch suggestions - first client-side, then API if needed
  const fetchSuggestions = useCallback(
    async (term) => {
      if (!term || term.length < 2) {
        setSuggestions([]);
        return;
      }

      // First, try client-side filtering
      const clientSideSuggestions = filterWordsByPrefix(term);

      if (clientSideSuggestions.length > 0) {
        // If we have enough client-side suggestions, use them
        setSuggestions(clientSideSuggestions);
      } else {
        // Otherwise, fall back to backend API for fuzzy search
        try {
          const data = await searchWord(term);

          // If exact match, no need for suggestions
          if (data.exact_match) {
            setSuggestions([]);
            return;
          }

          // Set suggestions from the API response
          if (data.suggestions && data.suggestions.length > 0) {
            setSuggestions(data.suggestions);
          } else {
            setSuggestions([]);
          }
        } catch (err) {
          console.error("Error fetching suggestions:", err);
          setSuggestions([]);
        }
      }
    },
    [searchWord, cachedWords, filterWordsByPrefix] // Added filterWordsByPrefix to dependencies
  );

  // Fix: use inline function in useCallback instead of pre-defined debounce
  // Debounced version of fetchSuggestions
  const debouncedFetchSuggestions = useCallback(
    (term) => {
      // Inline implementation of debounce instead of external function reference
      if (typingTimeout) {
        clearTimeout(typingTimeout);
      }

      const timeoutId = setTimeout(() => {
        fetchSuggestions(term);
      }, 200);

      setTypingTimeout(timeoutId);
    },
    [fetchSuggestions, typingTimeout]
  );

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    // Use our debounced function
    debouncedFetchSuggestions(value);
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion) => {
    setSearchTerm(suggestion);
    setSuggestions([]); // Clear suggestions
    handleSearch(null, suggestion); // Perform search with the selected suggestion
  };

  const handleSearch = async (e, overrideSearchTerm = null) => {
    if (e) e.preventDefault();
    const termToSearch = overrideSearchTerm || searchTerm.trim();
    if (!termToSearch) return;

    setIsLoading(true);
    setError("");
    setSuggestions([]); // Clear suggestions when performing a full search

    try {
      const data = await searchWord(termToSearch);
      setResult(data);

      // Save to recent searches if it's an exact match
      if (data.exact_match) {
        saveSearch(data.word, true, data.meaning);
      }
    } catch (err) {
      setError("Error searching for word. Please try again.");
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleSuggestionClick = (word) => {
    setSearchTerm(word);
    handleSearch(null, word);
  };

  return (
    <div className="min-h-screen bg-comic-bg text-comic-text flex flex-col">
      <header className="bg-comic-card shadow-md border-b border-comic-border">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BookOpenIcon className="h-8 w-8 text-comic-primary" />
            <h1 className="comic-title text-3xl">Fuzzy Dictionary</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="speech-bubble">
              <span className="text-comic-accent">@{user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="btn-comic flex items-center justify-center"
            >
              <ArrowLeftOnRectangleIcon className="h-5 w-5 mr-1.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl w-full mx-auto py-6 sm:px-6 lg:px-8 flex-grow">
        <div className="px-4 py-6 sm:px-0">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card-comic"
          >
            {isLoadingCache && (
              <div className="flex items-center text-comic-accent mb-4">
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-comic-accent mr-2"></div>
                <span>Loading dictionary data...</span>
              </div>
            )}

            <div className="relative mb-10">
              <form onSubmit={handleSearch} className="mb-2">
                <div className="flex flex-col sm:flex-row gap-2">
                  <div className="flex-grow relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <MagnifyingGlassIcon
                        className="h-5 w-5 text-comic-muted"
                        aria-hidden="true"
                      />
                    </div>
                    <input
                      type="text"
                      ref={searchInputRef}
                      value={searchTerm}
                      onChange={handleInputChange}
                      placeholder="Enter a word to search"
                      className="input-comic pl-10 w-full"
                      autoComplete="off"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading || !searchTerm.trim()}
                    className={`btn-comic flex items-center justify-center px-6 ${
                      isLoading || !searchTerm.trim()
                        ? "opacity-50 cursor-not-allowed"
                        : ""
                    }`}
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-black mr-2"></div>
                        <span>Searching</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        <span>Search</span>
                        <ArrowRightIcon
                          className="h-4 w-4 ml-2"
                          aria-hidden="true"
                        />
                      </div>
                    )}
                  </button>
                </div>
              </form>

              {/* Real-time suggestions dropdown with comic styling */}
              <AnimatePresence>
                {suggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute z-50 w-full bg-comic-highlight border-2 border-comic-border rounded-md shadow-lg mt-1"
                  >
                    <ul className="py-1 max-h-60 overflow-y-auto">
                      {suggestions.map((suggestion, index) => (
                        <motion.li
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <button
                            type="button"
                            onClick={() => handleSuggestionSelect(suggestion)}
                            className="block w-full text-left px-4 py-2 text-comic-text hover:bg-comic-card hover:text-comic-primary transition-colors"
                          >
                            <span className="font-comic font-bold">
                              {suggestion}
                            </span>
                          </button>
                        </motion.li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="p-4 mb-4 bg-red-900/20 border-l-4 border-comic-primary text-comic-primary flex items-start"
              >
                <ExclamationTriangleIcon
                  className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5"
                  aria-hidden="true"
                />
                <span>{error}</span>
              </motion.div>
            )}

            <AnimatePresence mode="wait">
              {result && (
                <motion.div
                  key={result.word || "suggestions"}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
                  className="border-2 border-comic-border rounded-lg overflow-hidden bg-comic-highlight"
                >
                  {result.exact_match ? (
                    <div className="p-6">
                      <div className="flex items-center mb-4">
                        <BookOpenIcon className="h-6 w-6 text-comic-secondary mr-2" />
                        <h3 className="text-xl font-comic font-bold text-comic-secondary">
                          Word Found!
                        </h3>
                      </div>
                      <div className="speech-bubble bg-comic-card">
                        <span className="font-comic text-xl font-bold text-comic-primary">
                          {result.word}
                        </span>
                        <div className="mt-2 text-comic-text font-comic">
                          {result.meaning}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6">
                      <div className="flex items-center mb-4">
                        <FaLightbulb className="h-5 w-5 text-comic-accent mr-2" />
                        <h3 className="text-xl font-comic font-bold text-comic-accent">
                          Word not found. Did you mean:
                        </h3>
                      </div>
                      <ul className="space-y-2 pl-4">
                        {result.suggestions &&
                          result.suggestions.map((suggestion, index) => (
                            <motion.li
                              key={index}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.1 }}
                              className="flex items-center"
                            >
                              <ArrowRightIcon className="h-4 w-4 text-comic-accent mr-2" />
                              <button
                                onClick={() =>
                                  handleSuggestionClick(suggestion)
                                }
                                className="text-comic-primary hover:text-comic-accent hover:underline transition-colors font-comic font-bold"
                              >
                                {suggestion}
                              </button>
                            </motion.li>
                          ))}
                        {(!result.suggestions ||
                          result.suggestions.length === 0) && (
                          <li className="text-comic-muted italic font-comic">
                            No suggestions found.
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Recent searches with improved icon alignment */}
            {recentSearches.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-8"
              >
                <div className="flex items-center mb-3">
                  <ClockIcon
                    className="h-5 w-5 text-comic-muted mr-2 flex-shrink-0"
                    aria-hidden="true"
                  />
                  <h3 className="text-lg font-comic font-bold text-comic-muted">
                    Recent Searches
                  </h3>
                </div>
                <ul className="divide-y divide-comic-border border-t border-b border-comic-border">
                  {recentSearches.map((search, index) => (
                    <motion.li
                      key={index}
                      className="py-3 hover:bg-comic-highlight transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + index * 0.05 }}
                    >
                      <button
                        onClick={() => handleSuggestionClick(search.word)}
                        className="font-comic font-bold text-comic-primary hover:text-comic-accent hover:underline transition-colors mr-2"
                      >
                        {search.word}
                      </button>
                      {search.isExactMatch && (
                        <span className="text-sm text-comic-muted italic font-comic">
                          - {search.meaning?.substring(0, 60)}
                          {search.meaning?.length > 60 ? "..." : ""}
                        </span>
                      )}
                    </motion.li>
                  ))}
                </ul>
              </motion.div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default Dictionary;
