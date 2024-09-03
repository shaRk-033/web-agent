import React, { useState } from "react";
import "./App.css";

function App() {
  const [formLink, setFormLink] = useState("");
  const [requirements, setRequirements] = useState("");
  const [status, setStatus] = useState("idle"); // New state: 'idle', 'processing', or 'success'

  const handleSubmit = () => {
    setStatus("processing");

    fetch("http://127.0.0.1:8000/form", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_info: requirements,
        form_url: formLink,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        setStatus("success");
        setFormLink(""); 
        setRequirements(""); 
        setTimeout(() => setStatus("idle"), 3000);
      })
      .catch((error) => {
        console.error("Error:", error);
        setStatus("error"); 
        setTimeout(() => setStatus("idle"), 3000);
      });
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
          <button onClick={handleSubmit} className="App-button" disabled={status === "processing"}>
            {status === "processing" ? "Processing..." : "Submit"}
          </button>
        </div>

        {status === "processing" && (
          <div className="spinner"></div>
        )}

        {status === "success" && (
          <div className="success-animation">Success!</div>
        )}

        {status === "error" && (
          <div className="error-animation">An error occurred. Please try again.</div>
        )}
      </header>
    </div>
  );
}

export default App;
