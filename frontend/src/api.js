// Base API URL from environment variables
const API_URL = process.env.REACT_APP_API_URL;

// Function to handle file upload
export const uploadFile = async (formData) => {
  console.log("API URL:", `${API_URL}/upload`);
  
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log("Server response:", data);
  return data;
};

// Function to fetch statistical analysis data
export const fetchAnalysisData = async () => {
  console.log("Fetching analysis data from:", `${API_URL}/analysis`);

  const response = await fetch(`${API_URL}/analysis`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log("Analysis data:", data);
  return data;
};

// Function to fetch plot data
export const fetchPlotData = async () => {
  console.log("Fetching plot data from:", `${API_URL}/plot`);

  const response = await fetch(`${API_URL}/plot`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log("Plot data:", data);
  return data;
};
