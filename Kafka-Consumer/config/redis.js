import Redis from "ioredis";
import dotenv from "dotenv";
dotenv.config();

console.log("Redis url: " + process.env.REDIS_URL);
let client = new Redis({
  host: process.env.REDIS_URL,
  port: process.env.REDIS_PORT,
});

client.on("ready", () => console.log("Redis connected"));
client.on("error", (err) => console.error("Redis error:", err));

export { client };

export const incrKey = async (key) => {
  return await client.incr(key);
};

export const expireKey = async (key, seconds) => {
  return await client.expire(key, seconds);
};

export const lpush = async (key, value) => {
  return await client.lpush(key, value);
};

export const ltrim = async (key, start, stop) => {
  return await client.ltrim(key, start, stop);
};
