import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Pages
import Home from './pages/Home';
import Results from './pages/Results';

// Development Components
import ApiTest from './components/ApiTest';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<Results />} />
          <Route path="/test" element={<ApiTest />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;