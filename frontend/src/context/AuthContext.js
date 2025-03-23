import { createContext, useState, useContext, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_URL = "http://localhost:8000";

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API_URL}/validate-session`, {
          withCredentials: true, // Important for sending/receiving cookies
        });

        if (response.data && response.data.is_authenticated) {
          setIsAuthenticated(true);
          setUser({ username: response.data.username });
        }
      } catch (error) {
        console.error("Authentication check failed:", error);
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      // Fix: removed the unused 'response' variable assignment
      await axios.post(`${API_URL}/token`, formData, {
        withCredentials: true, // Important for cookies
      });

      setIsAuthenticated(true);
      setUser({ username });
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return {
        success: false,
        message:
          error.response?.data?.detail || "Login failed. Please try again.",
      };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await axios.post(
        `${API_URL}/logout`,
        {},
        {
          withCredentials: true,
        }
      );
      setIsAuthenticated(false);
      setUser(null);
      return true;
    } catch (error) {
      console.error("Logout failed:", error);
      return false;
    }
  };

  // Updated search function with better error handling
  const searchWord = async (word) => {
    try {
      const response = await axios.post(
        `${API_URL}/search`,
        { word },
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Search failed:", error);

      // Only log out if specifically unauthorized
      if (error.response?.status === 401) {
        console.log(
          "Authentication error during search, attempting to verify session..."
        );

        try {
          // Try to verify if the session is still valid
          const sessionCheck = await axios.get(`${API_URL}/validate-session`, {
            withCredentials: true,
          });

          if (!sessionCheck.data.is_authenticated) {
            setIsAuthenticated(false);
            setUser(null);
          }
        } catch (sessionError) {
          console.error(
            "Session verification failed, logging out",
            sessionError
          );
          setIsAuthenticated(false);
          setUser(null);
        }
      }

      throw error;
    }
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    searchWord,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
