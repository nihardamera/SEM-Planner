const API_BASE_URL = 'http://localhost:8000/api/v1';

export const generatePlan = async (formData) => {
  const response = await fetch(`${API_BASE_URL}/plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An unknown error occurred');
  }

  return response.json();
};
