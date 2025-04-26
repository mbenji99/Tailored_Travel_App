// src/pages/Home.tsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plane, Star } from "lucide-react";
import { fetchRecommendation } from "../api";
import { featuredPlaces } from "../constants/featured";

export default function Home() {
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setError(null);
      setLoading(true);
      console.log("🔄 Loading featured ratings...");
      const newRatings: Record<string, number> = {};

      await Promise.all(
        featuredPlaces.map(async ({ id, label }) => {
          try {
            console.log(`📡 Fetching recommendation for ${label} (id=${id})`);
            const rec = await fetchRecommendation(id);
            console.log(`✅ Got recommendation for ${label}:`, rec);
            newRatings[label] = rec.predicted_rating;
          } catch (err: any) {
            console.error(`❌ Error fetching recommendation for ${label}:`, err);
            newRatings[label] = 0;
            if (!error) setError(err.message);
          }
        })
      );

      setRatings(newRatings);
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return <div className="flex justify-center">Loading ratings…</div>;
  }

  if (error) {
    return (
      <div className="text-red-600 text-center">
        Error loading recommendations: {error}
      </div>
    );
  }

  return (
    <div className="space-y-24">
      {/* Hero Section */}
      <section className="text-center py-24 px-6 bg-gradient-to-br from-blue-50 to-white animate-fadeIn">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Your Perfect Trip Starts Here
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Discover AI-powered travel recommendations tailored to your budget and
          preferences. Plan, track, and experience seamless travel like never
          before.
        </p>
        <div className="flex justify-center space-x-4">
          <Link
            to="/register"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition transform hover:scale-105"
          >
            Start Planning
          </Link>
          <Link
            to="/login"
            className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition transform hover:scale-105"
          >
            Sign In
          </Link>
        </div>
      </section>

      {/* Featured Destinations */}
      <section className="py-16 bg-white">
        <h2 className="text-3xl font-bold text-center mb-8">
          Featured Destinations
        </h2>
        <div className="max-w-6xl mx-auto grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 px-4">
          {featuredPlaces.map(({ id, label }) => (
            <Link
              key={id}
              to={`/new-trip?destination=${encodeURIComponent(label)}`}
              className="block bg-gray-50 rounded-xl shadow-sm p-6 hover:shadow-lg transition transform hover:scale-105"
            >
              <Plane className="h-8 w-8 text-blue-600 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2 text-center">
                {label}
              </h3>
              <div className="flex items-center justify-center space-x-1">
                <Star className="h-5 w-5 text-yellow-500" />
                <span className="font-medium">{ratings[label].toFixed(1)}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Why Choose Tailored Travels */}
      <section className="py-20 bg-blue-50">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-10 items-center px-6">
          <img
            src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80"
            alt="Travel Adventure"
            className="rounded-xl shadow-lg w-full h-[350px] object-cover transition-transform hover:scale-105"
            loading="lazy"
          />
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Why Choose Tailored Travels?
            </h2>
            <ul className="space-y-4 text-gray-700 list-disc pl-5">
              <li>Smart budget tracking and real-time price updates.</li>
              <li>AI-powered personalized recommendations.</li>
              <li>Automated itinerary generation and trip organization.</li>
            </ul>
            <Link
              to="/register"
              className="inline-block mt-6 text-blue-600 hover:text-blue-700 font-medium transition"
            >
              Start your journey →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
