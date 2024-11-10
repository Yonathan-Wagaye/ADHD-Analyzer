import React, { useState } from 'react';
import { uploadFile } from '../api';
import '../style/Home.css';

const Home = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); // State for handling upload errors
  const [sucessMessage, setSuccessMessage] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null); // Clear any previous errors when a new file is selected
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      setLoading(true);
      setError(null); // Reset error state before upload
      try {
        const response = await uploadFile(formData);
        onUploadSuccess(response.message);
         setSuccessMessage(response.message);
      } catch (error) {
        console.error("Error during file upload:", error);
        setError("Failed to upload file. Please try again."); // Display friendly error message
      } finally {
        setLoading(false);
      }
    } else {
      setError("Please select a file to upload."); // Show error if no file is selected
    }
  };

  return (
    <div className="home-container">
      <h1>Upload ADHD Data</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept=".zip" 
          className="file-input" 
        />
        <button type="submit" disabled={loading || !file} className="upload-button">
          {loading ? "Uploading..." : "Upload and Analyze"}
        </button>
      </form>
      {loading && <p className="loading-message">Reading and processing the file...</p>}
      {sucessMessage && <p className="loading-message">{sucessMessage}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default Home;
