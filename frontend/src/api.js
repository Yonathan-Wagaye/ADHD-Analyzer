export const uploadFile = async (formData) => {
    console.log("API URL:", `${process.env.REACT_APP_API_URL}/upload`);
    
    const response = await fetch(`${process.env.REACT_APP_API_URL}/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        Accept: 'application/json'  // Place Accept in headers
      }
    });
  
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  
    // Parse and store the JSON response only once
    const data = await response.json();
    console.log("Server response:", data);
    return data;
  };
  