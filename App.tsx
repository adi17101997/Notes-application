import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Home } from './pages/Home';
import { SignIn } from './pages/SignIn';
import { SignUp } from './pages/SignUp';

function App() {
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Set up SEO meta tags
    document.title = 'NotesApp - Your Personal Note Taking Solution';
    
    // Create or update meta tags
    const metaTags = [
      { name: 'description', content: 'A beautiful and intuitive note-taking application to organize your thoughts and ideas efficiently.' },
      { name: 'keywords', content: 'notes, note-taking, productivity, organization, thoughts, ideas, writing' },
      { property: 'og:title', content: 'NotesApp - Your Personal Note Taking Solution' },
      { property: 'og:description', content: 'A beautiful and intuitive note-taking application to organize your thoughts and ideas efficiently.' },
      { property: 'og:type', content: 'website' },
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: 'NotesApp - Your Personal Note Taking Solution' },
      { name: 'twitter:description', content: 'A beautiful and intuitive note-taking application to organize your thoughts and ideas efficiently.' },
    ];

    metaTags.forEach(({ name, property, content }) => {
      const selector = name ? `meta[name="${name}"]` : `meta[property="${property}"]`;
      let meta = document.querySelector(selector);
      
      if (!meta) {
        meta = document.createElement('meta');
        if (name) meta.setAttribute('name', name);
        if (property) meta.setAttribute('property', property);
        document.head.appendChild(meta);
      }
      
      meta.setAttribute('content', content);
    });
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;