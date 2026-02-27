/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/agents/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/agents/:path*`,
      },
      {
        source: '/api/crews/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/crews/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
