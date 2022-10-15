import '../styles/globals.css'
import { useEffect, useState } from "react"
import { Auth } from "aws-amplify"
import "../adapters/auth"

const MyApp = ({ Component, pageProps }) => {
  const [user, setUser] = useState(null)
  useEffect(() => {
    Auth.currentAuthenticatedUser().then(user => {
      setUser(user)
    }).catch(_ => {
      Auth.federatedSignIn()
    })
  }, [])
  return <Component user={user} {...pageProps} />
}

export default MyApp
