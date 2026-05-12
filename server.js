const path = require("path");
const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// Mock prediction endpoint (replace logic later)
app.post("/api/predict", (req, res) => {
  const input = req.body;

  // Simple heuristic mock
  const score = Math.random();
  const label = score > 0.5 ? "ATTACK" : "BENIGN";

  return res.json({
    label,
    score: Number(score.toFixed(4)),
    received: input
  });
});

app.listen(PORT, () => {
  console.log(`Frontend running on http://localhost:${PORT}`);
});