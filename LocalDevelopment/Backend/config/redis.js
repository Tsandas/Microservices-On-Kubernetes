import Redis from "ioredis";
import dotenv from "dotenv";
dotenv.config();

const redisConfig = {
  host: process.env.REDIS_URL,
  port: process.env.REDIS_PORT,
};

console.log("Redis config: ", redisConfig);
let redisClient = new Redis(redisConfig);

redisClient.on("ready", () => console.log("Redis connected"));
redisClient.on("error", (err) => console.error("Redis error:", err));

export { redisClient };
