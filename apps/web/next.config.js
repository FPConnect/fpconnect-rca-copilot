/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: "/:path*",
        has: [{ type: "host", value: "hypersecit.com.br" }],
        destination: "https://fpconnect.tec.br/:path*",
        permanent: true,
      },
      {
        source: "/:path*",
        has: [{ type: "host", value: "www.hypersecit.com.br" }],
        destination: "https://fpconnect.tec.br/:path*",
        permanent: true,
      },
      {
        source: "/:path*",
        has: [{ type: "host", value: "www.fpconnect.tec.br" }],
        destination: "https://fpconnect.tec.br/:path*",
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
