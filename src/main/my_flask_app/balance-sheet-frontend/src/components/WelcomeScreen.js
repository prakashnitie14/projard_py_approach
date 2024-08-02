import React from 'react';
import { useNavigate } from 'react-router-dom';

const WelcomeScreen = () => {
  const navigate = useNavigate();

  const goToUpload = () => {
    navigate('/upload');
  };

  return (
    <div>
      <h1>Welcome to the Financial Analysis App</h1>
      <button onClick={goToUpload}>Upload Financial Statement</button>
    </div>
  );
};

export default WelcomeScreen;