import express from "express";
import { connectConsumer, startConsuming } from "./config/kafka.js";
import { client } from "./config/redis.js";
import dotenv from "dotenv";
dotenv.config();

const app = express();
let isAlive = true;

app.get("/healthz/live", async (req, res) => {
  res
    .status(isAlive ? 200 : 503)
    .json({ status: isAlive ? "ok" : "unhealthy" });
});

app.get("/healthz/ready", async (req, res) => {
  try {
    const pong = await client.ping();
    if (pong !== "PONG") throw new Error("Redis ping failed");

    res.status(200).json({ status: "ready" });
  } catch (error) {
    res.status(503).json({ status: "unready", error: error.message });
  }
});

const handleMessage = async (event) => {
  await client.incr("total_registrations");
  await client.incr("registrations:last_minute");
  await client.expire("registrations:last_minute", 60);
  await client.lpush("events:recent", JSON.stringify(event));
  await client.ltrim("events:recent", 0, 9);
  console.log("Processing event:", event);
};

const run = async () => {
  try {
    await connectConsumer();
    await startConsuming(handleMessage);
  } catch (err) {
    console.error("Fatal error during startup:", err);
    isAlive = false;
  }
};

app.listen(process.env.PORT, () => console.log("Kafka-Consumer started!"));
run();
