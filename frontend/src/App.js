import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dictionary from "./pages/Dictionary";
import ComicLayout from "./components/ComicLayout";
import { useAuth } from "./context/AuthContext";

function App() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-comic-bg">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-comic-primary"></div>
      </div>
    );
  }

  return (
    <ComicLayout>
      <div data-theme="comic-dark">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dictionary"
            element={
              <ProtectedRoute>
                <Dictionary />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dictionary" replace />} />
        </Routes>
      </div>
    </ComicLayout>
  );
}

export default App;
