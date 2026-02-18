import express from "express";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const HOSTNAME = process.env.HOSTNAME || "unknown";

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Server is running!");
});

app.get("/data", (req, res) => {
  const random = Math.floor(Math.random() * 100);
  res.json({ value: random, pod: HOSTNAME });
});

app.post("/user", (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res
      .status(400)
      .json({ error: "Username and password are required" });
  }

  res.status(201).json({
    userId: Math.floor(Math.random() * 1000),
    username,
    pod: HOSTNAME,
  });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
