const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  publicRuntimeConfig: {
    kmwsAccountingEndpoint: process.env.KMWS_ACCOUNTING_ENDPOINT,
    authRegion: process.env.AUTH_REGION,
    authUserPoolId: process.env.AUTH_USER_POOL_ID,
    authUserPoolWebClientId: process.env.AUTH_USER_POOL_WEB_CLIENT_ID,
    authOauthDomain: process.env.AUTH_OAUTH_DOMAIN,
    authRedirect: process.env.AUTH_REDIRECT,
  },
  target: 'serverless',
}

module.exports = nextConfig
