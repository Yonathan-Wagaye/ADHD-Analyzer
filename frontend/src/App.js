import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import Plots from './pages/Plots';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [responseData, setResponseData] = useState(null);  // State to hold response data

  const handleUploadSuccess = (data) => {
    setResponseData(data);  // Store the response data
  };

  return (
    <Router>
      <div className="app-container">
        <nav className="app-nav">
          <ul>
            <li>
              <Link to="/">Social Robotics Analyzer</Link>
            </li>
            <li>
              <Link to="/analysis">Analysis</Link>
            </li>
            <li>
              <Link to="/plots">Plots</Link>
            </li>
          </ul>
        </nav>

        <div className="content">
          <Routes>
            <Route path="/" element={<Home onUploadSuccess={handleUploadSuccess} />} />
            <Route path="/analysis" element={<Analysis data={responseData} />} />
            <Route path="/plots" element={<Plots plotUrls={responseData?.plotUrls} />} />
          </Routes>
        </div>

        <Footer />  {/* Footer added here */}
      </div>
    </Router>
  );
}

export default App;
