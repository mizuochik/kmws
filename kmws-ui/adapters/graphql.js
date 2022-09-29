const getAccounts = async () => {
    const res = await fetch(process.env.NEXT_PUBLIC_KMWS_ACCOUNTING_ENDPOINT, {
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

export { getAccounts }
