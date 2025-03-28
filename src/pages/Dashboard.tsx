import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

interface Trip {
  id: string;
  destination: string;
  budget: number;
  remaining_budget: number;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    const fetchTrips = async () => {
      try {
        const response = await fetch(`${API_URL}/trips`, {
          credentials: 'include',
        });

        const data = await response.json();

        if (response.ok && Array.isArray(data.trips)) {
          setTrips(data.trips);
        } else {
          console.error('API returned invalid format:', data);
          setTrips([]);
        }
      } catch (error) {
        console.error('Error fetching trips:', error);
        setTrips([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, [user, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        Loading trips...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Trips</h1>
        <button
          onClick={() => navigate('/new-trip')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Plan New Trip
        </button>
      </div>

      {trips.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl shadow-sm">
          <p>No trips planned yet. Start your adventure!</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => (
            <div key={trip.id} className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900">{trip.destination}</h3>
              <p>Budget: {trip.budget}</p>
              <p>Status: {trip.status}</p>
              <button
                onClick={() => navigate(`/trips/${trip.id}`)}
                className="mt-4 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
