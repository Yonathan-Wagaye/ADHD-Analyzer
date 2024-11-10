import React, { useState } from 'react';
import { uploadFile } from '../api';
import '../style/Home.css';

const Home = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      setLoading(true);
      try {
        const response = await uploadFile(formData);
        onUploadSuccess(response);  // Pass response to App component
      } catch (error) {
        console.error("Error during file upload:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div>
      <h1>Upload ADHD Data</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".zip" />
        <button type="submit" disabled={loading}>Upload and Analyze</button>
      </form>
      {loading && <p className="loading-message">Reading and processing the file...</p>}
    </div>
  );
};

export default Home;
