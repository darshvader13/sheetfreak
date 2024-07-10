'use client';

import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Message } from "@/components/interfaces/interfaces"
import Link from 'next/link'
import Header from "@/components/ui/Header"

const CHUNK_DELIMITER = "--END_CHUNK--"

export default function Act() {
  const searchParams = useSearchParams()
  const sheetsUrl = searchParams.get('link') ?? ''
  const sheetsId = sheetsUrl.split('/')[5] || ''
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to the bottom of the chat container when messages update
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages]);

  const appendToLastMessage = (txt: string) => {
    setMessages(prevMessages => {
      let newMessages = [...prevMessages];

      if (newMessages.length > 0) {
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          text: newMessages[newMessages.length - 1].text + " " + txt,
        };
      }

      return newMessages;
    });
  }

  async function handleSendMessage() {
    if (inputMessage.trim() !== '') {
        setMessages([...messages, { text: inputMessage, sender: 'user' }])
        setInputMessage('')
        
        setMessages(prevMessages => [...prevMessages, { text: "Starting...", sender: 'bot' }])
        const res = await fetch('/api/freak', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              task_prompt: inputMessage,
              sheet_id: sheetsId,
              messages: messages,
            })
        })
        const reader = res.body?.getReader()
        const decoder = new TextDecoder('utf-8')

        if (!reader) {
            console.error('Stream reader not available')
            return
        }

        let done = false;
        let buffer = ""
        let newMessage = true

        while (!done) {
            const { value, done: readerDone } = await reader.read()
            done = readerDone;

            if (value) {
                const chunk = decoder.decode(value, { stream: true })
                buffer += chunk
                const buffer_parts = buffer.split(" ")
                for (let i = 0; i < buffer_parts.length - 1; i++) {
                  const part = buffer_parts[i]
                  if (part == CHUNK_DELIMITER) {
                    newMessage = true
                  } else {
                    if (newMessage) {

                      setMessages(prevMessages => [...prevMessages, { text: part, sender: 'bot' }])
                      newMessage = false
                    } else {
                      appendToLastMessage(part)
                    }
                  }
                }
                buffer = buffer_parts[buffer_parts.length - 1]
            }
        }
    }
  }

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="p-10 flex flex-col grow overflow-hidden">
          <h1 className="pl-2 font-bold text-2xl">Let&apos;s get freaky in your sheets!</h1>
          {sheetsUrl !== "Error" && 
            <Link
              href={sheetsUrl}
              rel="noopener noreferrer"
              target="_blank"
              className="pl-2 underline text-blue-600 hover:text-blue-800 visited:text-purple-600">
                {sheetsUrl}
            </Link>
          }
        <div ref={chatContainerRef} className="pt-4 grow overflow-y-auto">
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
                  display: 'inline-block',
                  whiteSpace: 'pre-line',
                }}
              >
                  {message.text}
              </span>
            </div>
          ))}
        </div>
        <div className="flex items-center">
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Execute commands..."
          />
          <Button
              onClick={handleSendMessage}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}