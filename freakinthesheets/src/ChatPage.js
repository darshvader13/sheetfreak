import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const ChatPage = () => {
  const location = useLocation();

  const sheetsUrl = location.state?.sheetsUrl;
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const chatContainerRef = useRef(null);

  const sheetsId = sheetsUrl.split('/')[5];

  useEffect(() => {
    // Scroll to the bottom of the chat container when messages update
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (inputMessage.trim() !== '') {
      setMessages([...messages, { text: inputMessage, sender: 'user' }]);
      setInputMessage('');
      
      // Simulate a response (replace this with actual API call in a real app)
      setTimeout(() => {
        setMessages(prevMessages => [...prevMessages, { text: 'This is a simulated response.', sender: 'bot' }]);
      }, 1000);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1>Freaky Sheets Chat</h1>
      <p>Google Sheets ID: {sheetsId}</p>
      
      <div 
        ref={chatContainerRef}
        style={{
          height: '400px',
          border: '1px solid #ccc',
          overflowY: 'auto',
          padding: '10px',
          marginBottom: '20px'
        }}
      >
        {messages.map((message, index) => (
          <div 
            key={index}
            style={{
              marginBottom: '10px',
              textAlign: message.sender === 'user' ? 'right' : 'left'
            }}
          >
            <span
              style={{
                background: message.sender === 'user' ? '#007bff' : '#28a745',
                color: 'white',
                padding: '5px 10px',
                borderRadius: '10px',
                display: 'inline-block'
              }}
            >
              {message.text}
            </span>
          </div>
        ))}
      </div>
      
      <div style={{ display: 'flex' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type a message..."
          style={{ flexGrow: 1, marginRight: '10px', padding: '10px' }}
        />
        <button
          onClick={handleSendMessage}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;