import { Amplify } from 'aws-amplify'

Amplify.configure({
  Auth: {
    region: process.env.NEXT_PUBLIC_AUTH_REGION,
    userPoolId: process.env.NEXT_PUBLIC_AUTH_USER_POOL_ID,
    userPoolWebClientId: process.env.NEXT_PUBLIC_AUTH_USER_POOL_WEB_CLIENT_ID,
    oauth: {
      domain: process.env.NEXT_PUBLIC_AUTH_OAUTH_DOMAIN,
      scope: ['openid'],
      redirectSignIn: process.env.NEXT_PUBLIC_AUTH_REDIRECT,
      redirectSignOut: process.env.NEXT_PUBLIC_AUTH_REDIRECT,
      responseType: 'code',
    }
  }
})
