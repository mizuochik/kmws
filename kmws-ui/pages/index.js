import { useEffect, useState } from "react"
import { Auth, Hub } from "aws-amplify"
import "../adapters/auth"

const Index = () => {
  const [user, setUser] = useState(null)

  useEffect(() => {
    Hub.listen('auth', ({ payload: { event, data } }) => {
      if (event === 'cognitoHostedUI') {
        Auth.currentAuthenticatedUser().then(user => {
          setUser(user)
        })
      } else if (event === 'cognitoHostedUI_failure') {
        alert('Sign in failure')
      }
    })
  }, [])

  console.log('user!', user?.signInUserSession.idToken)

  return <div>
    <h1>Hello KMWS</h1>
    <button onClick={() => Auth.federatedSignIn()}>Sign In</button><br />
    <button onClick={() => Auth.signOut()}>Sign Out</button>
  </div>
}

Index.getInitialProps = async (_) => {
  return {}
}

export default Index
