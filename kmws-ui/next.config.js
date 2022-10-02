const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  publicRuntimeConfig: {
    kmwsAccountingEndpoint: process.env.KMWS_ACCOUNTING_ENDPOINT,
  }
}

module.exports = nextConfig
