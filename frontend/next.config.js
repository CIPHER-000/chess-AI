/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['api.chess.com', 'images.chesscomfiles.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
