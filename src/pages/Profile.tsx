import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { fetchProfile, updateProfile } from '../api';

export default function Profile() {
  const user = useAuthStore(s => s.user);
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail]       = useState('');
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [message, setMessage]   = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    // load profile from server
    fetchProfile()
      .then(profile => {
        setEmail(profile.email);
        setUsername(profile.username);
      })
      .catch(err => {
        console.error(err);
        navigate('/dashboard');
      })
      .finally(() => setLoading(false));
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const newUsername = await updateProfile(username);
      setUsername(newUsername);
      setMessage('Profile updated!');
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6">Loading profile…</div>;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white p-8 rounded-xl shadow space-y-6"
      >
        <h2 className="text-2xl font-bold text-center text-blue-700">Your Profile</h2>

        {message && (
          <div
            className={`px-4 py-2 rounded text-sm ${
              message.includes('updated') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}
          >
            {message}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="text"
            value={email}
            disabled
            className="w-full px-4 py-2 bg-gray-100 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
