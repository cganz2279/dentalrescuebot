import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Force cache invalidation
console.log('DentalRescueBot loaded at:', new Date().toISOString());

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
