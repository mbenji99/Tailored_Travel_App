import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTripStore } from '../store/tripStore';
import { useAuthStore } from '../store/authStore';

export default function NewTrip() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { setBudget, setPreferences } = useTripStore();

  const [budget, setBudgetLocal] = useState('');
  const [weather, setWeather] = useState<'hot' | 'cold' | 'tropical'>('hot');
  const [environment, setEnvironment] = useState<'beach' | 'mountain' | 'historic' | 'nature'>('beach');
  const [activityType, setActivityType] = useState<'adventure' | 'relaxation' | 'cultural' | 'mixed'>('mixed');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const numericBudget = parseFloat(budget);
      if (isNaN(numericBudget) || numericBudget <= 0) {
        throw new Error('Please enter a valid budget');
      }

      // Simulate saving (or connect to real API here)
      setBudget(numericBudget);
      setPreferences({ weather, environment, activityType });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-xl bg-white p-8 rounded-xl shadow-lg space-y-6 animate-fadeIn"
      >
        <h2 className="text-2xl font-bold text-center text-blue-700">Plan Your Trip</h2>

        {error && <div className="bg-red-100 text-red-600 px-4 py-2 rounded text-sm">{error}</div>}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudgetLocal(e.target.value)}
            placeholder="e.g. 1000"
            required
            className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Weather */}
        <Selection title="Weather Preference" options={['hot', 'cold', 'tropical']} selected={weather} setSelected={setWeather} />

        {/* Environment */}
        <Selection title="Environment" options={['beach', 'mountain', 'historic', 'nature']} selected={environment} setSelected={setEnvironment} />

        {/* Activity */}
        <Selection title="Activity Type" options={['adventure', 'relaxation', 'cultural', 'mixed']} selected={activityType} setSelected={setActivityType} />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? 'Creating Trip...' : 'Create Trip'}
        </button>
      </form>
    </div>
  );
}

function Selection({
  title,
  options,
  selected,
  setSelected
}: {
  title: string;
  options: string[];
  selected: string;
  setSelected: (value: any) => void;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{title}</label>
      <div className="grid grid-cols-2 gap-3">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setSelected(option)}
            className={`px-4 py-2 rounded-lg border transition ${
              selected === option
                ? 'bg-blue-50 border-blue-600 text-blue-600 font-semibold'
                : 'border-gray-300 hover:border-blue-600'
            }`}
          >
            {option.charAt(0).toUpperCase() + option.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
