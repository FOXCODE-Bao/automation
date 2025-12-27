import { API_BASE_URL } from "./config.js";

// GET request
export async function get(endpoint) {
  const res = await fetch(API_BASE_URL + endpoint);

  if (!res.ok) {
    throw new Error("Network response was not ok");
  }

  const data = await res.json();
  return data;
}

// POST request (JSON hoặc FormData)
export async function post(endpoint, body, isFormData = false) {
  const options = {
    method: "POST",
    headers: {},
    body: body
  };

  if (!isFormData) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const res = await fetch(API_BASE_URL + endpoint, options);

  if (!res.ok) {
    throw new Error("API error");
  }

  const data = await res.json();

  // Backend có field success
  if (data.success === false) {
    throw new Error(data.message || "Request failed");
  }

  return data;
}
