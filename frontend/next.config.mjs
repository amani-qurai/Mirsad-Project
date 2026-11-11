/** @type {import('next').NextConfig} */
const nextConfig = {
  // A self-contained server bundle, so the web image needs no node_modules.
  output: "standalone",
  reactStrictMode: true,
};

export default nextConfig;
