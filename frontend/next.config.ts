import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  // Hide the Next.js "N" badge in the bottom-left during development
  devIndicators: false,
};

export default nextConfig;
