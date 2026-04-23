const express = require("express");
const axios = require("axios");
const path = require("path");

const app = express();
const port = process.env.PORT || 3000;

// API URL from environment — fallback to service name for Docker
const API_URL = process.env.API_URL || "http://api:8000";

// Middleware
app.use(express.static("public"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// Submit a new job
app.post("/api/jobs", async (req, res) => {
  try {
    const { task } = req.body;

    if (!task) {
      return res.status(400).json({ error: "task field is required" });
    }

    const response = await axios.post(`${API_URL}/jobs`, { task });
    res.json(response.data);
  } catch (error) {
    console.error("Error creating job:", error.message);
    res.status(500).json({ error: "Failed to create job" });
  }
});

// Get job status
app.get("/api/jobs/:job_id", async (req, res) => {
  try {
    const { job_id } = req.params;

    const response = await axios.get(`${API_URL}/jobs/${job_id}`);
    res.json(response.data);
  } catch (error) {
    if (error.response?.status === 404) {
      return res.status(404).json({ error: "Job not found" });
    }
    console.error("Error fetching job status:", error.message);
    res.status(500).json({ error: "Failed to fetch job status" });
  }
});

// Serve the HTML UI
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`API endpoint: ${API_URL}`);
});
EOF
