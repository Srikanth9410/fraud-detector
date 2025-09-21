import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [warning, setWarning] = useState(null);
  const [reasoning, setReasoning] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8765');

    ws.onopen = () => {
      console.log('Connected to WebSocket server');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'warning') {
        setWarning(message.text);
        setReasoning(message.reasoning);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Elder Fraud/Scam Voice Detector</h1>
        {warning ? (
          <div className="warning-banner">
            <h2>⚠️ Scam Alert!</h2>
            <p><strong>Detected Text:</strong> {warning}</p>
            <div className="reasoning-box">
              <strong>Reasoning:</strong>
              <pre>{reasoning}</pre>
            </div>
          </div>
        ) : (
          <p>Listening for suspicious activity...</p>
        )}
      </header>
    </div>
  );
}

export default App;
