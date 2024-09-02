import React, { useState } from 'react';
import './App.css';

function App() {
  const [formLink, setFormLink] = useState('');
  const [requirements, setRequirements] = useState('');

  const handleSubmit = () => {
    // Handle the submit action
    console.log('Form Link:', formLink);
    console.log('Requirements:', requirements);

    // New code to post data as JSON
    fetch('http://127.0.0.1:8000/form', {  // Ensure the URL matches the FastAPI endpoint
      method: 'POST',  // Ensure the method is POST
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({  // Update the keys to match FormData model
        user_info: requirements,  // Assuming requirements is user_info
        form_url: formLink,       // Assuming formLink is form_url
      }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => console.log('Success:', data))
    .catch((error) => console.error('Error:', error));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-title">agent uno</h1>
        <p className="App-description">fill forms swiftly</p>

        <div className="input-container">
          <input
            type="text"
            placeholder="Enter form link"
            value={formLink}
            onChange={(e) => setFormLink(e.target.value)}
            className="App-input"
          />
          <textarea
            placeholder="Enter requirements"
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            className="App-textarea"
          />
          <button
            onClick={handleSubmit}
            className="App-button"
          >
            Submit
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;
