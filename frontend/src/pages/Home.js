import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchForm from '../components/SearchForm';
import './Home.css';

const Home = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (origin, destination) => {
    setLoading(true);
    
    try {
      // Store search parameters in sessionStorage for the Results page
      sessionStorage.setItem('searchOrigin', origin);
      sessionStorage.setItem('searchDestination', destination);
      
      // Navigate to results page
      navigate('/results', { 
        state: { 
          origin, 
          destination,
          fromSearch: true
        } 
      });
    } catch (error) {
      console.error('Search error:', error);
      // Error handling will be done in SearchForm component
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <div className="home-container">
        <SearchForm onSearch={handleSearch} loading={loading} />
        
        <div className="features-section">
          <h2>🚀 Compare All Transportation Options</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🚗</div>
              <h3>Rideshare</h3>
              <p>Uber & Lyft with all vehicle types including bikes and scooters</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🚇</div>
              <h3>Public Transit</h3>
              <p>NYC Subway and Bus routes with real-time information</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🚲</div>
              <h3>Bike Share</h3>
              <p>Citi Bike stations with live availability data</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>All-in-One</h3>
              <p>See all options in one place with clear pricing and availability</p>
            </div>
          </div>
        </div>

        <div className="how-it-works">
          <h2>📱 How It Works</h2>
          <div className="steps">
            <div className="step">
              <span className="step-number">1</span>
              <p>Enter your starting point and destination</p>
            </div>
            <div className="step">
              <span className="step-number">2</span>
              <p>We instantly compare all transportation options</p>
            </div>
            <div className="step">
              <span className="step-number">3</span>
              <p>Choose your preferred option and book directly</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;