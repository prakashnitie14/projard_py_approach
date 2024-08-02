import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WelcomeScreen from './components/WelcomeScreen';
import UploadScreen from './components/UploadScreen';
import ResultsScreen from './components/ResultsScreen';

function App() {
  const [results, setResults] = useState(null);

  const handleUpload = (data) => {
    setResults(data);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomeScreen />} />
        <Route path="/upload" element={<UploadScreen onUpload={handleUpload} />} />
        <Route path="/results" element={<ResultsScreen data={results} />} />
      </Routes>
    </Router>
  );
}

export default App;
