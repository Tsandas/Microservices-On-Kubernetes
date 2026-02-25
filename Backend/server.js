import express from "express";
import dotenv from "dotenv";
import pool from "./config/pg.js";

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

app.post("/user", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res
      .status(400)
      .json({ error: "Username and password are required" });
  }

  const query =
    "INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id";
  const values = [username, password];
  const result = await pool.query(query, values);

  res.status(201).json({
    userId: result.rows[0].id,
    username,
    pod: HOSTNAME,
  });
});

app.get("/user", async (req, res) => {
  const query = "SELECT * FROM users LIMIT 10";
  const result = await pool.query(query);
  res.json(result.rows);
});

app.listen(PORT, async () => {
  await pool.connect();
  console.log(`Backend server running on http://localhost:${PORT}`);
});
