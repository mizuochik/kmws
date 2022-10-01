import Head from 'next/head'
import styles from '../styles/Home.module.css'
import * as graphql from '../adapters/graphql'
import { useEffect, useState } from 'react'

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

const App = () => {
  let [payments, setPayments] = useState([])
  let [showPaymentForm, setShowPaymentForm] = useState(false)

  const toggleShowPaymentForm = () => {
    setShowPaymentForm(!showPaymentForm)
  }

  useEffect(() => {
    graphql.getAccounts().then(data => {
      setPayments(data.payments)
    })
  }, [])

  return (
    <div className={styles.container}>
      <Head>
        <title>K&amp;M Web Services</title>
      </Head>
      <header className={styles.header}>
        <h1 className={styles.headerLogo}>K&amp;M Web Services</h1>
      </header>
      <main className={styles.main}>
        <h2>Accounting</h2>
        <div className={styles.paymentHeader}>
          <h3 className={styles.serviceLogo}>Payments</h3>
          <button className={styles.actionButton} onClick={toggleShowPaymentForm}>New</button>
        </div>
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
            {payments.map(((p, i) => (<tr key={i}>
              <td>{p.date}</td>
              <td>{p.place}</td>
              <td>{p.payer}</td>
              <td>{p.item}</td>
              <td className={styles.numberCell}>{p.amountYen}</td>
              <td><button className={styles.actionButton}>Delete</button></td>
            </tr>)))}
          </tbody>
        </table>
        <h3>Sharing</h3>
        <table className={styles.dataTable}>
          <thead>
            <tr>
              <th>Month</th>
              <th>Taro Paid</th>
              <th>Hanako Paid</th>
              <th>Taro&apos;s Share</th>
              <th>Hanako&apos;s Share</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2022-01</td>
              <td className={styles.numberCell}>100</td>
              <td className={styles.numberCell}>100</td>
              <td className={styles.numberCell}>-200</td>
              <td className={styles.numberCell}>200</td>
              <td>Adjusted</td>
            </tr>
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
            <tr>
              <td>2022-01-01T00:00:00+09</td>
              <td>Taro</td>
              <td>Add</td>
              <td></td>
              <td>Payments/2022-01-01/Tokyo/Juice/100</td>
            </tr>
          </tbody>
        </table>
      </main>
    </div>
  )
}

export default App