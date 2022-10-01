const KMWS_ACCOUNTING_ENDPOINT = process.env.NEXT_PUBLIC_KMWS_ACCOUNTING_ENDPOINT;

const getAccounts = async () => {
  const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
    mode: 'cors',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
{
  payments(year: 2022, month: 1) {
    id
    date
    place
    payer
    item
    amountYen
  }
}`}),
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
