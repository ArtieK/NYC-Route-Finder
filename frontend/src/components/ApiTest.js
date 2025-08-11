// ApiTest.js - Component for testing API connectivity during development
import React, { useState } from 'react';
import { transportationAPI, apiUtils } from '../services/api';

const ApiTest = () => {
  const [testResults, setTestResults] = useState({});
  const [isRunning, setIsRunning] = useState(false);

  const runTests = async () => {
    setIsRunning(true);
    const results = {};

    console.log('🧪 Starting API Tests...');

    // Test 1: Health Check
    try {
      console.log('1️⃣ Testing health check...');
      const health = await transportationAPI.healthCheck();
      results.healthCheck = { success: true, data: health };
    } catch (error) {
      results.healthCheck = { success: false, error: error.message };
    }

    // Test 2: Connection Test
    try {
      console.log('2️⃣ Testing API connection...');
      const connection = await transportationAPI.testConnection();
      results.connectionTest = { success: true, data: connection };
    } catch (error) {
      results.connectionTest = { success: false, error: error.message };
    }

    // Test 3: Geocoding
    try {
      console.log('3️⃣ Testing geocoding...');
      const geocode = await transportationAPI.geocodeAddress('Times Square, NYC');
      results.geocoding = { success: true, data: geocode };
    } catch (error) {
      results.geocoding = { success: false, error: error.message };
    }

    // Test 4: Route Search (using both methods)
    try {
      console.log('4️⃣ Testing route search (GET)...');
      const routes = await transportationAPI.getRoutes('Times Square', 'Central Park');
      results.routesGET = { success: true, data: routes };
    } catch (error) {
      results.routesGET = { success: false, error: error.message };
    }

    try {
      console.log('5️⃣ Testing route search (POST)...');
      const routesPost = await transportationAPI.getRoutesPost('Times Square', 'Central Park');
      results.routesPOST = { success: true, data: routesPost };
    } catch (error) {
      results.routesPOST = { success: false, error: error.message };
    }

    // Test 5: Input Validation
    console.log('6️⃣ Testing input validation...');
    const validation1 = apiUtils.validateSearchInputs('', 'Central Park');
    const validation2 = apiUtils.validateSearchInputs('Times Square', 'Times Square');
    const validation3 = apiUtils.validateSearchInputs('Times Square', 'Central Park');
    
    results.validation = {
      success: true,
      data: {
        emptyOrigin: validation1,
        sameLocations: validation2,
        validInput: validation3
      }
    };

    // Test 6: NYC Location Detection
    console.log('7️⃣ Testing NYC location detection...');
    const nycTests = {
      'Times Square': apiUtils.isLikelyNYCLocation('Times Square'),
      'Central Park NYC': apiUtils.isLikelyNYCLocation('Central Park NYC'),
      'Brooklyn Bridge': apiUtils.isLikelyNYCLocation('Brooklyn Bridge'),
      'Los Angeles': apiUtils.isLikelyNYCLocation('Los Angeles'),
      'Manhattan': apiUtils.isLikelyNYCLocation('Manhattan')
    };
    
    results.nycDetection = { success: true, data: nycTests };

    setTestResults(results);
    setIsRunning(false);
    console.log('✅ All tests completed!', results);
  };

  const TestResult = ({ title, result }) => {
    if (!result) return null;

    return (
      <div style={{ 
        margin: '10px 0', 
        padding: '15px', 
        border: `2px solid ${result.success ? '#4CAF50' : '#f44336'}`,
        borderRadius: '8px',
        backgroundColor: result.success ? '#f8fff8' : '#fff8f8'
      }}>
        <h4 style={{ margin: '0 0 10px 0' }}>
          {result.success ? '✅' : '❌'} {title}
        </h4>
        {result.success ? (
          <pre style={{ fontSize: '12px', overflow: 'auto' }}>
            {JSON.stringify(result.data, null, 2)}
          </pre>
        ) : (
          <p style={{ color: '#f44336', margin: 0 }}>
            Error: {result.error}
          </p>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>🧪 API Test Suite</h2>
      <p>Test all API endpoints and utilities before building the full application.</p>
      
      <button
        onClick={runTests}
        disabled={isRunning}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: isRunning ? '#ccc' : '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: isRunning ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}
      >
        {isRunning ? 'Running Tests...' : 'Run All Tests'}
      </button>

      <div id="test-results">
        <TestResult title="Health Check" result={testResults.healthCheck} />
        <TestResult title="Connection Test" result={testResults.connectionTest} />
        <TestResult title="Geocoding API" result={testResults.geocoding} />
        <TestResult title="Routes API (GET)" result={testResults.routesGET} />
        <TestResult title="Routes API (POST)" result={testResults.routesPOST} />
        <TestResult title="Input Validation" result={testResults.validation} />
        <TestResult title="NYC Location Detection" result={testResults.nycDetection} />
      </div>

      {Object.keys(testResults).length > 0 && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
          <h4>Test Summary</h4>
          <p>
            ✅ Passed: {Object.values(testResults).filter(r => r.success).length} | 
            ❌ Failed: {Object.values(testResults).filter(r => !r.success).length}
          </p>
          <p><strong>Check browser console for detailed logs</strong></p>
        </div>
      )}
    </div>
  );
};

export default ApiTest;