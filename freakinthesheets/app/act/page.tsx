'use client';

import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

interface Message {
    text: string;
    sender: string;
}

export default function Act() {
  const searchParams = useSearchParams();
  const sheetsUrl = searchParams.get('link')
  let sheetsId = ""
  if (sheetsUrl) {
    sheetsId = sheetsUrl.split('/')[5]
  }
  console.log(sheetsId)
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to the bottom of the chat container when messages update
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleSendMessage() {
    if (inputMessage.trim() !== '') {
        setMessages([...messages, { text: inputMessage, sender: 'user' }]);
        setInputMessage('');
        
        const res = await fetch('/api/freak', {
            method: 'POST',
            body: JSON.stringify({
            task_prompt: inputMessage,
            sheet_id: sheetsId,
            })
        })
        const results = await res.json()
        console.log(results.data)
        setMessages(prevMessages => [...prevMessages, { text: results.data, sender: 'bot' }]);
    }
  }

  return (
    <div className="p-10">
      <h1>Execute</h1>
      <p>Google Sheets URL: {sheetsUrl}</p>
      
      <div ref={chatContainerRef}>
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
                background: message.sender === 'user' ? '#007bff' : '#8a8a8a',
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
        <Input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Execute commands..."
        />
        <Button
            onClick={handleSendMessage}
            className=""
        >
          Send
        </Button>
      </div>
    </div>
  );
}