/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow ngrok domains in dev mode
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig

