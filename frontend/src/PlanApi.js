// Backend base URL, e.g. https://sem-planner-api.example.com (no trailing /api/v1).
// Set VITE_API_URL at build time; defaults to the local backend.
const BACKEND_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const API_BASE_URL = `${BACKEND_URL}/api/v1`;

const describeDetail = (detail) => {
  if (Array.isArray(detail)) {
    // FastAPI validation errors: [{ loc: ['body', 'brand_url'], msg: '...' }, ...]
    return detail.map((item) => `${(item.loc || []).slice(-1)[0]}: ${item.msg}`).join('; ');
  }
  return typeof detail === 'string' ? detail : null;
};

export const generatePlan = async (formData) => {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });
  } catch {
    throw new Error(
      `Could not reach the backend at ${BACKEND_URL}. Check that it is running and that VITE_API_URL is correct.`,
    );
  }

  if (!response.ok) {
    let detail = null;
    try {
      detail = describeDetail((await response.json()).detail);
    } catch {
      // The body was not JSON; fall back to the status code.
    }
    throw new Error(detail || `The backend returned HTTP ${response.status}.`);
  }

  return response.json();
};
