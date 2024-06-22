import React from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import GoogleSheetsURLInput from './GoogleSheetsURLInput';
import ChatPage from './ChatPage';

const HomePage = () => {
  const navigate = useNavigate();

  const handleValidUrl = (url) => {
    navigate('/chat', { state: { sheetsUrl: url } });
  };

  return <GoogleSheetsURLInput onValidUrl={handleValidUrl} />;
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </Router>
  );
};

export default App;