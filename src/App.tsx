import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NewTrip from './pages/NewTrip';
import Profile from './pages/Profile';
import { useAuthStore } from './store/authStore';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const setUser = useAuthStore(state => state.setUser);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/session`, { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject('Unauthorized'))
      .then(data => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, [setUser]);

  if (loading) return <div>Loading...</div>;

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/new-trip" element={<NewTrip />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
