/** @type {import('next').NextConfig} */
import nextPWA from "next-pwa";

const nextConfig = {
  experimental: {
    reactCompiler: true,
    instrumentationHook: true,
  },
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
};

const withPWA = nextPWA({
  dest: "public",
  register: true,
  skipWaiting: true,
});

export default withPWA(nextConfig);
