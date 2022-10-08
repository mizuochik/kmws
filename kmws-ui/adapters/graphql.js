import getConfig from 'next/config'

const KMWS_ACCOUNTING_ENDPOINT = getConfig().publicRuntimeConfig.kmwsAccountingEndpoint

const getAccounts = async (year, month) => {
  const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
    mode: 'cors',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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

const getAdjustments = async (year, month) => {
  const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
    mode: 'cors',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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

const getHistory = async () => {
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

export { getAccounts, getAdjustments, createPayment, getHistory }
