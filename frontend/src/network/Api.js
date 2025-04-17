import axios from "axios";
// Base URL for your API
import { API_URL } from "./config";

/**
 * Generic API call function
 * @param {string} endpoint - The API endpoint (e.g., '/data')
 * @param {string} method - The HTTP method ('GET', 'POST', 'PUT', 'DELETE', etc.)
 * @param {object} [data] - The data to be sent with the request (for POST/PUT)
 * @param {object} [params] - URL parameters for GET requests
 * @returns {Promise} - Resolves with the response data or rejects with an error
 */

const apiCall = async ({
  endpoint,
  method = "GET",
  data = null,
  params = {},
  headers = {},
}) => {
  const defaultHeaders = {
    "Content-Type": "application/json", // Default content type
    "api-token": localStorage.getItem("token"),
  };

  const config = {
    method,
    headers: { ...defaultHeaders, ...headers },
    url: `${API_URL}${endpoint}`,
    data,
    params,
  };

  try {
    const response = await axios(config);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // Check if there is a response from the server
      if (error.response) {
        throw error.response;
      } else {
        throw error.message;
      }
    } else {
      throw error;
    }
  }
};

export default apiCall;
