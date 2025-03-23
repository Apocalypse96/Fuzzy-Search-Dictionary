import React from "react";
import { motion } from "framer-motion";

const ComicLayout = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-comic-bg"
    >
      <div className="comic-bg-pattern absolute inset-0 z-0 opacity-5 pointer-events-none"></div>
      <div className="relative z-10">{children}</div>

      {/* Comic-style decorations */}
      <div className="fixed top-10 right-10 w-20 h-20 bg-comic-accent opacity-10 rounded-full blur-xl"></div>
      <div className="fixed bottom-20 left-10 w-32 h-32 bg-comic-primary opacity-10 rounded-full blur-xl"></div>
      <div className="fixed top-1/2 left-1/4 w-40 h-40 bg-comic-secondary opacity-5 rounded-full blur-xl"></div>
    </motion.div>
  );
};

export default ComicLayout;
