import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Plane, User, LogOut, Menu } from 'lucide-react';

export default function Navbar() {
  const { user, signOut } = useAuthStore();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      await fetch(import.meta.env.VITE_API_URL + '/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      console.error('Error signing out:', err);
    } finally {
      await signOut();
      navigate('/');
    }
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="flex items-center space-x-2">
          <Plane className="h-7 w-7 text-blue-600" />
          <span className="text-xl font-bold text-gray-800">Tailored Travels</span>
        </Link>

        <div className="flex items-center space-x-4">
          {user ? (
            <>
              <Link
                to="/new-trip"
                className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition"
              >
                Plan New Trip
              </Link>
              <Link
                to="/dashboard"
                className="text-gray-700 hover:text-blue-600 transition"
              >
                Dashboard
              </Link>

              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center space-x-1 focus:outline-none"
                >
                  <User className="h-6 w-6 text-gray-600" />
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 py-2 bg-white rounded-md shadow-lg">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Profile Settings
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <div className="flex items-center space-x-2">
                        <LogOut className="h-4 w-4" />
                        <span>Sign Out</span>
                      </div>
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-gray-600 hover:text-blue-600 transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
