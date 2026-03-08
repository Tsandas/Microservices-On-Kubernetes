import express from "express";
import dotenv from "dotenv";
import pool from "./config/pg.js";
import { connectProducer, sendMessage } from "./config/kafka.js";
import { redisClient } from "./config/redis.js";
import cors from "cors";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const HOSTNAME = process.env.HOSTNAME || "unknown";
app.use(express.json());
app.use(cors());

// Health
app.get("/", (req, res) => {
  res.send("Server is running!");
});

app.get("/healthz/live", async (req, res) => {
  res.status(200).json({ status: "ok" });
});

app.get("/healthz/ready", async (req, res) => {
  try {
    await pool.query("SELECT 1");

    const pong = await redisClient.ping();
    if (pong !== "PONG") throw new Error("Redis ping failed");

    res.status(200).json({ status: "ready" });
  } catch (error) {
    res.status(503).json({ status: "unready", error: error.message });
  }
});

// Basic data routes
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

  await sendMessage(process.env.KAFKA_TOPIC, {
    event: "user_created",
    username,
    timestamp: Date.now(),
  });
  console.log({ message: "Event produced", username });

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

// Direct Kafka
app.post("/kafka-produce", async (req, res) => {
  const { username } = req.body;
  if (!username) {
    return res.status(400).json({ error: "username is required" });
  }
  await sendMessage(process.env.KAFKA_TOPIC, {
    event: "user_created",
    username,
    timestamp: Date.now(),
  });
  res.json({ message: "Event produced", username });
});

// Redis
app.get("/stats", async (req, res) => {
  const total = await redisClient.get("total_registrations");
  const lastMinute = await redisClient.get("registrations:last_minute");
  res.json({
    total_registrations: parseInt(total) || 0,
    registrations_last_minute: parseInt(lastMinute) || 0,
  });
});

app.get("/events", async (req, res) => {
  const events = await redisClient.lrange("events:recent", 0, 9);
  res.json(events.map((e) => JSON.parse(e)));
});

// Start
app.listen(PORT, async () => {
  await pool.connect();
  await connectProducer();
  console.log(`Backend server running on http://localhost:${PORT}`);
});
