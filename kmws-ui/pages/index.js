import Router from "next/router"
import { useEffect } from "react"

const Index = ({ }) => {
  useEffect(() => {
    const d = new Date()
    Router.push(`/accounting/${d.getFullYear()}/${d.getMonth()}`)
  }, [])
  return <div></div>
}

Index.getInitialProps = async (_) => {
  return {}
}

export default Index

