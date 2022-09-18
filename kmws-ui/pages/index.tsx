import type { NextPage } from 'next'
import Head from 'next/head'
import styles from '../styles/Home.module.css'

const Home: NextPage = () => {
  return (
    <div className={styles.container}>
      <Head>
        <title>K&amp;M Web Services</title>
      </Head>

      <header>
        <h1>K&amp;M Web Services</h1>
      </header>

      <main className={styles.main}>
        <h2>Accounting</h2>
        <table>
          <tr>
            <th>Date</th>
            <th>Place</th>
            <th>Payer</th>
            <th>Item</th>
            <th>Amount</th>
            <th>Actions</th>
          </tr>
          <tr>
            <td>2022-01-01</td>
            <td>Tokyo</td>
            <td>Taro</td>
            <td>Juice</td>
            <td>100</td>
            <td><button>Delete</button></td>
          </tr>
        </table>

        <h3>History</h3>
        <table>
          <tr>
            <th>Timestamp</th>
            <th>Editor</th>
            <th>Data</th>
            <th>Action</th>
          </tr>
          <tr>
            <td>2022-01-01T00:00:00+09</td>
            <td>Taro</td>
            <td>2022-01-01/Tokyo/Juice/100</td>
            <td>Add</td>
          </tr>
        </table>
      </main>
    </div>
  )
}

export default Home
