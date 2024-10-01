import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({ serviceName: "taller-2" });
}
