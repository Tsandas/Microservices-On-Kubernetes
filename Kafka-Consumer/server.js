import { connectConsumer, startConsuming } from "./config/kafka.js";
import { client } from "./config/redis.js";

const handleMessage = async (event) => {
  await client.incr("total_registrations");
  await client.incr("registrations:last_minute");
  await client.expire("registrations:last_minute", 60);
  await client.lpush("events:recent", JSON.stringify(event));
  await client.ltrim("events:recent", 0, 9);
  console.log("Processing event:", event);
};

const run = async () => {
  await connectConsumer();
  await startConsuming(handleMessage);
};

run().catch(console.error);
