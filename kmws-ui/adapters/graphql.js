import getConfig from 'next/config'

const KMWS_ACCOUNTING_ENDPOINT = getConfig().publicRuntimeConfig.kmwsAccountingEndpoint

const createPayment = async (form) => {
  const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
    mode: 'cors',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: `
mutation CreatePayment($input: PaymentInput!) {
  createPayment(input: $input)
}
`,
      variables: {
        input: {
          date: form.date.value,
          place: form.place.value,
          payer: 'Somebody',
          item: form.item.value,
          amountYen: parseInt(form.amount.value),
        },
      },
    })
  })
  return (await res.json()).data
}

class Client {
  constructor(authToken) {
    this.authToken = authToken
  }

  async getAccounts(year, month) {
    const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
      mode: 'cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.authToken,
      },
      body: JSON.stringify({
        query: `
  query GetPayments($year: Int!, $month: Int!) {
    payments(year: $year, month: $month) {
      id
      date
      place
      payer
      item
      amountYen
    }
  }`,
        variables: {
          year: year,
          month: month,
        }
      }),
    })
    return (await res.json()).data
  }

  async getAdjustments(year, month) {
    const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
      mode: 'cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.authToken,
      },
      body: JSON.stringify({
        query: `
  query GetAdjustments($year: Int!, $month: Int!) {
    adjustments(year: $year, month: $month) {
      year
      month
      paid {
        name
        amount
      }
      adjustments {
        name
        amount
      }
    }
  }`,
        variables: {
          year: year,
          month: month,
        }
      }),
    })
    return (await res.json()).data
  }

  async getHistory() {
    const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
      mode: 'cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: `
  query GetHistory {
    history {
      timestamp
      editor
      action
      before
      after
    }
  }`,
        variables: {
        }
      }),
    })
    return (await res.json()).data
  }
}

export { createPayment, Client }
