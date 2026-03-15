import express from "express";
import dotenv from "dotenv";
import pool from "./config/pg.js";
import { connectProducer, sendMessage } from "./config/kafka.js";
import { redisClient } from "./config/redis.js";
import cors from "cors";
import client from "prom-client";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const HOSTNAME = process.env.HOSTNAME || "unknown";
app.use(express.json());
app.use(cors());

// ─── Prometheus metrics ───────────────────────────────────────────────────────

const register = new client.Registry();

client.collectDefaultMetrics({ register, labels: { pod: HOSTNAME } });

const httpRequestsTotal = new client.Counter({
  name: "http_requests_total",
  help: "Total number of HTTP requests",
  labelNames: ["method", "route", "status_code"],
  registers: [register],
});

const httpRequestDuration = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "HTTP request duration in seconds",
  labelNames: ["method", "route", "status_code"],
  buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5], // seconds
  registers: [register],
});

const httpRequestsInFlight = new client.Gauge({
  name: "http_requests_in_flight",
  help: "Number of requests currently being processed",
  labelNames: ["method", "route"],
  registers: [register],
});

const SKIP_ROUTES = ["/healthz/live", "/healthz/ready", "/metrics"];

app.use((req, res, next) => {
  if (SKIP_ROUTES.includes(req.path)) return next();

  const end = httpRequestDuration.startTimer();
  const route = req.path;

  httpRequestsInFlight.inc({ method: req.method, route });

  res.on("finish", () => {
    const labels = {
      method: req.method,
      route: req.route?.path ?? req.path,
      status_code: res.statusCode,
    };
    httpRequestsTotal.inc(labels);
    end(labels);
    httpRequestsInFlight.dec({ method: req.method, route });
  });

  next();
});

// ─── Health ───────────────────────────────────────────────────────────────────

app.get("/", (req, res) => res.send("Server is running!"));

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

// ─── Metrics endpoint ─────────────────────────────────────────────────────────

app.get("/metrics", async (req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});

// ─── Routes ───────────────────────────────────────────────────────────────────

app.get("/data", (req, res) => {
  res.json({ value: Math.floor(Math.random() * 100), pod: HOSTNAME });
});

app.post("/user", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Username and password are required" });
  }
  const result = await pool.query(
    "INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id",
    [username, password]
  );
  console.log({ message: "Event produced", username });
  res.status(201).json({ userId: result.rows[0].id, username, pod: HOSTNAME });
});

app.get("/user", async (req, res) => {
  const result = await pool.query("SELECT * FROM users LIMIT 10");
  res.json(result.rows);
});

app.post("/kafka-produce", async (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: "username is required" });
  await sendMessage(process.env.KAFKA_TOPIC, {
    event: "user_created",
    username,
    timestamp: Date.now(),
  });
  res.json({ message: "Event produced", username });
});

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

// ─── Start ────────────────────────────────────────────────────────────────────

app.listen(PORT, async () => {
  // await pool.connect();
  await connectProducer();
  console.log(`Backend server running on ${HOSTNAME}:${PORT}`);
});


// ```

// **What `GET /metrics` now returns** (standard Prometheus text format):
// ```
// # HELP http_requests_total Total number of HTTP requests
// # TYPE http_requests_total counter
// http_requests_total{method="GET",route="/user",status_code="200",pod="pod-abc"} 42

// # HELP http_request_duration_seconds HTTP request duration in seconds
// # TYPE http_request_duration_seconds histogram
// http_request_duration_seconds_bucket{le="0.01",...} 10
// http_request_duration_seconds_bucket{le="0.05",...} 35
// ...
// http_request_duration_seconds_sum{...} 1.847
// http_request_duration_seconds_count{...} 42

// # HELP nodejs_heap_size_used_bytes ...  ← free, from collectDefaultMetrics