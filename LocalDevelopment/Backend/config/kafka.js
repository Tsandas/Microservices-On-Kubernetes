import { Kafka } from "kafkajs";
import dotenv from "dotenv";
dotenv.config();

const kafkaConfig = {
  clientId: "backend",
  brokers: [process.env.KAFKA_BROKER || "localhost:9092"],
};

const kafka = new Kafka(kafkaConfig);

const producer = kafka.producer();

export const connectProducer = async () => {
  console.log("Kafka config", kafkaConfig);
  await producer.connect();
  console.log("Kafka producer connected");
};

export const sendMessage = async (topic, message) => {
  await producer.send({
    topic,
    messages: [{ value: JSON.stringify(message) }],
  });
};
