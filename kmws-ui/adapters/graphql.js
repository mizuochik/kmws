import getConfig from 'next/config'

const KMWS_ACCOUNTING_ENDPOINT = getConfig().publicRuntimeConfig.kmwsAccountingEndpoint

class Client {
  constructor(authToken) {
    this.authToken = authToken
  }

  async createPayment(form) {
    return this.runGraphQL(`
mutation CreatePayment($input: PaymentInput!) {
  createPayment(input: $input)
}`, {
      input: {
        date: form.date.value,
        place: form.place.value,
        payer: 'Somebody',
        item: form.item.value,
        amountYen: parseInt(form.amount.value),
      },
    })
  }

  async deletePayment(id) {
    return await this.runGraphQL(`
mutation DeletePayment($id: String!) {
  deletePayment(id: $id)
}`, {
      id: id,
    })
  }

  async runGraphQL(query, variables) {
    const res = await fetch(KMWS_ACCOUNTING_ENDPOINT, {
      mode: 'cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.authToken,
      },
      body: JSON.stringify({
        query: query,
        variables: variables,
      }),
    })
    return (await res.json()).data
  }

  async getAccounts(year, month) {
    return await this.runGraphQL(`
query GetPayments($year: Int!, $month: Int!) {
  payments(year: $year, month: $month) {
    id
    date
    place
    payer
    item
    amountYen
  }
}`, { year: year, month: month })
  }

  async getAdjustments(year, month) {
    return await this.runGraphQL(`
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
}`, { year: year, month: month })
  }

  async getHistory() {
    return await this.runGraphQL(`
query GetHistory {
  history {
    timestamp
    editor
    action
    before
    after
  }
}`, {})
  }
}

export { Client }
