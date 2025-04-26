// src/pages/NewTrip.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTrip } from '../api';

export default function NewTrip() {
  const navigate = useNavigate();
  const [destination, setDestination] = useState('');
  const [budget, setBudget] = useState('');
  const [weather, setWeather] = useState<'hot'|'cold'|'tropical'>('hot');
  const [env, setEnv] = useState<'beach'|'mountain'|'historic'|'nature'>('beach');
  const [act, setAct] = useState<'adventure'|'relaxation'|'cultural'|'mixed'>('mixed');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr('');
    setLoading(true);
    try {
      const b = parseFloat(budget);
      if (!destination || isNaN(b) || b <= 0) {
        throw new Error('Please enter a valid destination and budget');
      }
      const trip = await createTrip({
        destination,
        budget: b,
        weather_preference: weather,
        environment_preference: env,
        activity_preference: act,
      });
      navigate(`/trips/${trip.id}`);
    } catch (e: any) {
      setErr(e.message || 'Error creating trip');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 px-6 space-y-6">
      <h1 className="text-3xl font-bold text-center">Create a New Trip</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {err && <div className="text-red-600">{err}</div>}

        <input
          type="text"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="Destination (e.g. Rome, Italy)"
          className="w-full px-4 py-2 border rounded"
          required
        />

        <input
          type="number"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          placeholder="Budget (USD)"
          className="w-full px-4 py-2 border rounded"
          required
        />

        {/* Weather Preference */}
        <div>
          <label className="block font-medium mb-1">Weather Preference:</label>
          <div className="flex space-x-4">
            {['hot', 'cold', 'tropical'].map((opt) => (
              <label key={opt} className="inline-flex items-center">
                <input
                  type="radio"
                  name="weather"
                  value={opt}
                  checked={weather === opt}
                  onChange={() => setWeather(opt as any)}
                  className="form-radio"
                />
                <span className="ml-2 capitalize">{opt}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Environment Preference */}
        <div>
          <label className="block font-medium mb-1">Environment Preference:</label>
          <div className="flex space-x-4">
            {['beach', 'mountain', 'historic', 'nature'].map((opt) => (
              <label key={opt} className="inline-flex items-center">
                <input
                  type="radio"
                  name="environment"
                  value={opt}
                  checked={env === opt}
                  onChange={() => setEnv(opt as any)}
                  className="form-radio"
                />
                <span className="ml-2 capitalize">{opt}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Activity Preference */}
        <div>
          <label className="block font-medium mb-1">Activity Preference:</label>
          <div className="flex space-x-4">
            {['adventure', 'relaxation', 'cultural', 'mixed'].map((opt) => (
              <label key={opt} className="inline-flex items-center">
                <input
                  type="radio"
                  name="activity"
                  value={opt}
                  checked={act === opt}
                  onChange={() => setAct(opt as any)}
                  className="form-radio"
                />
                <span className="ml-2 capitalize">{opt}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          {loading ? 'Creating…' : 'Create Trip'}
        </button>
      </form>
    </div>
  );
}
