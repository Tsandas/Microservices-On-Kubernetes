import { Kafka } from "kafkajs";
import dotenv from "dotenv";
dotenv.config();

const kafka = new Kafka({
  clientId: "worker",
  brokers: [process.env.KAFKA_BROKER || "localhost:9092"],
});

const consumer = kafka.consumer({ groupId: "worker-group" });

export const connectConsumer = async () => {
  await consumer.connect();
  await consumer.subscribe({
    topic: process.env.KAFKA_TOPIC || "user-events",
    fromBeginning: false,
  });
  console.log("Kafka consumer connected");
};

export const startConsuming = async (onMessage) => {
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      try {
        const parsed = JSON.parse(message.value.toString());
        console.log("Received event:", parsed);
        await onMessage(parsed);
      } catch (err) {
        console.warn("Skipping malformed message:", message.value.toString());
      }
    },
  });
};
