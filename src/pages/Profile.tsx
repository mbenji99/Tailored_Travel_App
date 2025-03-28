import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Profile() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!user) return navigate('/login');
    // Assume fetch profile logic here
    setUsername(user.email.split('@')[0]);
  }, [user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setMessage('Profile updated!');
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white p-8 rounded-xl shadow space-y-6 animate-fadeIn"
      >
        <h2 className="text-2xl font-bold text-center text-blue-700">Your Profile</h2>

        {message && <div className="bg-green-100 text-green-700 px-4 py-2 rounded text-sm">{message}</div>}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="text"
            value={user?.email}
            disabled
            className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
