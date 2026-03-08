import pg from "pg";
const { Pool } = pg;
const pgconfig = {
  user: process.env.POSTGRES_USER || "postgres",
  password: process.env.POSTGRES_PASSWORD || "postgres",
  database: process.env.POSTGRES_DB || "postgres",
  host: process.env.POSTGRES_HOST || "localhost",
  port: parseInt(process.env.POSTGRES_PORT || "5432", 10),
};
console.log("postgres config", pgconfig);
const pool = new Pool(pgconfig);
export default pool;
