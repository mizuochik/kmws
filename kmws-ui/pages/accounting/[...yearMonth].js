import Head from 'next/head'
import styles from '../../styles/Accounting.module.css'
import * as graphql from '../../adapters/graphql'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { Auth } from 'aws-amplify'

const NewPaymentForm = () => {
  const createPayment = async (event) => {
    event.preventDefault()
    const res = await graphql.createPayment(event.target)
    console.log(res)
  }

  return <div className={styles.newPaymentFormWrapper}>
    <form className={styles.newPaymentForm} onSubmit={createPayment}>
      <label>
        Date
        <input type="text" name="date"></input>
      </label>
      <label>
        Place
        <input type="text" name="place"></input>
      </label>
      <label>
        Item
        <input type="text" name="item"></input>
      </label>
      <label>
        Amount
        <input type="text" name="amount"></input>
      </label>
      <div className={styles.submitButtonWrapper}>
        <input type="submit" className={styles.submitButton}></input>
      </div>
    </form>
  </div>
}

const MonthNavigation = ({ year, month }) => {
  const previousYear = year - (month > 1 ? 0 : 1)
  const previousMonth = month > 1 ? month - 1 : 12
  const nextYear = year + (month < 12 ? 0 : 1)
  const nextMonth = month < 12 ? month + 1 : 1

  return <nav className={styles.monthNavigation}>
    <Link href={`/accounting/${previousYear}/${previousMonth}`}>◀</Link> {year}/{month} <Link href={`/accounting/${nextYear}/${nextMonth}`}>▶︎</Link>
  </nav>
}

const Accounting = ({ user }) => {
  const router = useRouter()
  const [payments, setPayments] = useState([])
  const [adjustments, setAdjustments] = useState([])
  const [history, setHistory] = useState([])
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [yearMonth, setYearMonth] = useState(null)
  const [client, setClient] = useState(null)

  const toggleShowPaymentForm = () => {
    setShowPaymentForm(!showPaymentForm)
  }

  useEffect(() => {
    if (!user)
      return
    setClient(new graphql.Client(user.signInUserSession.idToken.jwtToken))
  }, [user])

  useEffect(() => {
    if (!router.query.yearMonth)
      return
    const [year, month] = router.query.yearMonth
    setYearMonth([parseInt(year), parseInt(month)])
  }, [router.query.yearMonth])

  useEffect(() => {
    if (!yearMonth)
      return
    if (!client)
      return
    client.getAccounts(parseInt(yearMonth[0]), parseInt(yearMonth[1])).then(data => {
      setPayments(data.payments)
    })
    client.getAdjustments(parseInt(yearMonth[0]), parseInt(yearMonth[1])).then(data => {
      setAdjustments(data.adjustments)
    })
  }, [yearMonth, client])

  useEffect(() => {
    if (!client)
      return
    client.getHistory().then(data => {
      setHistory(data.history)
    })
  }, [client])

  let payers;
  if (adjustments && adjustments.length > 0) {
    payers = adjustments[0].paid.map(p => p.name)
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>K&amp;M Web Services</title>
      </Head>
      <header className={styles.header}>
        <h1 className={styles.headerLogo}>K&amp;M Web Services</h1>
        {user && <div>
          <span className={styles.welcomeMessage}>Welcome <strong>{user.username}</strong></span>
          <button className={styles.signOutButton} onClick={() => Auth.signOut()}>Sign Out</button>
        </div>}
      </header>
      <main className={styles.main}>
        <header className={styles.accountingHeader}>
          <h2>Accounting</h2>
          {yearMonth && <MonthNavigation year={yearMonth[0]} month={yearMonth[1]} />}
        </header>
        <header className={styles.paymentHeader}>
          <h3 className={styles.serviceLogo}>Payments</h3>
          <button className={styles.actionButton} onClick={toggleShowPaymentForm}>New</button>
        </header>
        {showPaymentForm && <NewPaymentForm />}
        <table className={styles.dataTable}>
          <thead>
            <tr>
              <th>Date</th>
              <th>Place</th>
              <th>Payer</th>
              <th>Item</th>
              <th>Amount</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p, i) => (<tr key={i}>
              <td>{p.date}</td>
              <td>{p.place}</td>
              <td>{p.payer}</td>
              <td>{p.item}</td>
              <td className={styles.numberCell}>{p.amountYen}</td>
              <td><button className={styles.actionButton}>Delete</button></td>
            </tr>))}
          </tbody>
        </table>
        <h3>Adjustments</h3>
        <table className={styles.dataTable}>
          <thead>
            <tr>
              <th>Month</th>
              {payers && payers.map((p, i) => <th key={i}>{p} Paid</th>)}
              {payers && payers.map((p, i) => <th key={i}>{p} Adjustment</th>)}
            </tr>
          </thead>
          <tbody>
            {adjustments && adjustments.map((adjustment, i) => <tr key={i}>
              <td>{adjustment.year}/{adjustment.month}</td>
              {adjustment.paid.map((paid, i) => <td key={i} className={styles.numberCell}>{paid.amount}</td>)}
              {adjustment.adjustments.map((adjustment, i) => <td key={i} className={styles.numberCell}>{adjustment.amount}</td>)}
            </tr>)}
          </tbody>
        </table>
        <h3>History</h3>
        <table className={styles.dataTable}>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Editor</th>
              <th>Action</th>
              <th>Before</th>
              <th>After</th>
            </tr>
          </thead>
          <tbody>
            {history && history.map((h, i) => <tr key={i}>
              <td>{h.timestamp}</td>
              <td>{h.editor}</td>
              <td>{h.action}</td>
              <td>{h.before || 'None'}</td>
              <td>{h.after}</td>
            </tr>)}
          </tbody>
        </table>
      </main>
    </div >
  )
}

Accounting.getInitialProps = async (ctx) => {
  return {}
}

export default Accounting
