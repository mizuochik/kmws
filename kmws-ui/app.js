const next = require("next")
const serverless = require("serverless-http")

const handler = serverless(next({}).getRequestHandler())

module.exports = { handler }
