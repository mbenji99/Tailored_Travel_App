import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home         from './pages/Home';
import Login        from './pages/Login';
import Register     from './pages/Register';
import Dashboard    from './pages/Dashboard';
import NewTrip      from './pages/NewTrip';
import TripDetails  from './pages/TripDetails';
import Profile      from './pages/Profile';
import { useAuthStore } from './store/authStore';

function App() {
  const setUser = useAuthStore(s => s.setUser);
  const [loading,setLoading] = useState(true);

  useEffect(()=>{
    fetch(`${import.meta.env.VITE_API_URL}/api/session`,
      { credentials:'include' })
      .then(r=> r.ok? r.json():Promise.reject())
      .then(d=> setUser(d.user))
      .catch(()=> setUser(null))
      .finally(()=> setLoading(false));
  },[setUser]);

  if(loading) return <div>Loading…</div>;

  return (
    <Router>
      <Navbar/>
      <div className="container mx-auto p-4">
        <Routes>
          <Route path="/"          element={<Home/>}/>
          <Route path="/login"     element={<Login/>}/>
          <Route path="/register"  element={<Register/>}/>
          <Route path="/dashboard" element={<Dashboard/>}/>
          <Route path="/new-trip"  element={<NewTrip/>}/>
          <Route path="/trips/:tripId" element={<TripDetails/>}/>
          <Route path="/profile"   element={<Profile/>}/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
