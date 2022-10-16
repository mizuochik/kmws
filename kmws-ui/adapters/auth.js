import { Amplify } from 'aws-amplify'
import getConfig from 'next/config'

const config = getConfig().publicRuntimeConfig

Amplify.configure({
  Auth: {
    region: config.authRegion,
    userPoolId: config.authUserPoolId,
    userPoolWebClientId: config.authUserPoolWebClientId,
    oauth: {
      domain: config.authOauthDomain,
      scope: ['openid'],
      redirectSignIn: config.authRedirect,
      redirectSignOut: config.authRedirect,
      responseType: 'code',
    }
  }
})
