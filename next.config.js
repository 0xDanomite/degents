/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://degents.vercel.app/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
