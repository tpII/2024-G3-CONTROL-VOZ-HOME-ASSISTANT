/** @type {import('next').NextConfig} */
import withSerwistInit from "@serwist/next";

const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
};

const withPWA = withSerwistInit({
  reloadOnOnline: true,
  swSrc: "src/sw.ts",
  swDest: "public/sw.js",
});

export default withPWA(nextConfig);
