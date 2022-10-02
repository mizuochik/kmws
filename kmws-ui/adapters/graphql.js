const KMWS_ACCOUNTING_ENDPOINT = process.env.NEXT_PUBLIC_KMWS_ACCOUNTING_ENDPOINT;

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

export { getAccounts, createPayment }
