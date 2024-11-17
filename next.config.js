/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://degents.onrender.com/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
