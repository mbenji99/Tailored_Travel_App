import React from 'react';
import { Link } from 'react-router-dom';
import { Plane, Map, Calendar, DollarSign } from 'lucide-react';

export default function Home() {
  return (
    <div className="space-y-24">
      {/* Hero Section */}
      <section className="text-center py-24 px-6 bg-gradient-to-br from-blue-50 to-white animate-fadeIn">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">Your Perfect Trip Starts Here</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Discover AI-powered travel recommendations tailored to your budget and preferences. Plan, track, and experience seamless travel like never before.
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/register" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition transform hover:scale-105">
            Start Planning
          </Link>
          <Link to="/login" className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition transform hover:scale-105">
            Sign In
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-10 text-center px-4">
          {[
            {
              icon: <DollarSign className="h-10 w-10 text-blue-600 mx-auto mb-3" />,
              title: 'Budget-Friendly',
              desc: 'Find destinations that match your budget with real-time expense tracking.',
            },
            {
              icon: <Map className="h-10 w-10 text-blue-600 mx-auto mb-3" />,
              title: 'Personalized',
              desc: 'AI-driven recommendations based on your travel style and preferences.',
            },
            {
              icon: <Calendar className="h-10 w-10 text-blue-600 mx-auto mb-3" />,
              title: 'Smart Planning',
              desc: 'Automated itinerary generation with real-time updates.',
            },
          ].map(({ icon, title, desc }, index) => (
            <div
              key={index}
              className="p-6 bg-gray-50 rounded-xl shadow-md hover:shadow-lg transition transform hover:scale-105"
            >
              {icon}
              <h3 className="text-xl font-semibold mb-2">{title}</h3>
              <p className="text-gray-600">{desc}</p>
            </div>
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
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Why Choose Tailored Travels?</h2>
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
