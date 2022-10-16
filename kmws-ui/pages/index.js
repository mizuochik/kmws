import Router from "next/router"
import { useEffect } from "react"

const Index = ({ user }) => {
  useEffect(() => {
    if (!user)
      return
    const d = new Date()
    Router.push(`/accounting/${d.getFullYear()}/${d.getMonth() + 1}`)
  }, [user])
  return <div></div>
}

Index.getInitialProps = async (_) => {
  return {}
}

export default Index
