import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: { remotePatterns: [{ protocol: "https", hostname: "**" }] },
  async rewrites() {
    // Proxy API calls to FastAPI in dev so the browser hits one origin.
    return [{ source: "/api/:path*", destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/:path*` }];
  },
};
export default nextConfig;
