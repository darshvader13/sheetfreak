import React, { useState } from 'react';

const GoogleSheetsURLInput = ({ onValidUrl }) => {
  const [url, setUrl] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(false);

  const handleUrlChange = (e) => {
    const inputUrl = e.target.value;
    setUrl(inputUrl);
    
    // Basic validation for Google Sheets URL
    const isValid = inputUrl.startsWith('https://docs.google.com/spreadsheets/');
    setIsValidUrl(isValid);
  };

  const handleContinue = () => {
    if (isValidUrl ) {
      onValidUrl(url);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={url}
        onChange={handleUrlChange}
        placeholder="Copy and Paste Google Sheets URL"
        style={{
          padding: '10px',
          width: '300px',
          marginRight: '10px'
        }}
      />
      <button
        onClick={handleContinue}
        disabled={!isValidUrl}
        style={{
          padding: '10px 20px',
          backgroundColor: isValidUrl ? '#4CAF50' : '#ccc',
          color: 'white',
          border: 'none',
          cursor: isValidUrl ? 'pointer' : 'default',
          transition: 'background-color 0.3s'
        }}
      >
        Continue
      </button>
    </div>
  );
};

export default GoogleSheetsURLInput;