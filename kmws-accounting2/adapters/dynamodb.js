import { QueryCommand } from "@aws-sdk/client-dynamodb"

export class PaymentEventDao {
    #client

    constructor(client) {
        this.#client = client
    }

    async create(paymentEvent) {
    }

    async readByMonth(year, month) {
        if (month < 1 || month > 12)
            throw 'Invalid Year'
        const nextYear = year + (month >= 12 ? 1 : 0)
        const nextMonth = (month + 1) % 12
        const got = await this.#client.send(new QueryCommand({
            TableName: 'TestKmwsAccounting',
            IndexName: 'PK-PaidAt-index',
            KeyConditionExpression: 'PK = :pk and PaidAt between :month_start and :month_end',
            ExpressionAttributeValues: {
                ":pk": { S: "PaymentEvent" },
                ":month_start": { S: `${year}-${String(month).padStart(2, '0')}` },
                ":month_end": { S: `${nextYear}-${String(nextMonth).padStart(2, '0')}` }
            }
        }))
        return got.Items.map(i => ({
            paymentId: i.PaidAt.S,
            item: i.Item.S,
            paidAt: new Date(i.PaidAt.S),
            amountYen: i.AmountYen.N,
            place: i.Place.S,
            payer: i.Payer.S,
            createdAt: new Date(i.SK.S),
        }))
    }
}
