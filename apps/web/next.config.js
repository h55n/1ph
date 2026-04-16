/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**' },
    ],
  },
  // Kept off to avoid enforcing typed-route constraints across legacy href usage.
  typedRoutes: false,
}

module.exports = nextConfig
