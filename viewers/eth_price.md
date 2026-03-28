# ETH Price Viewer

## Type
Read-only oracle — streams current ETH/USD price data.

## Source
CoinGecko free API (no auth required)

## Endpoint
`https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd`

## Refresh Interval
30 seconds

## Data Schema
```json
{
  "ethereum": {
    "usd": 3450.00
  }
}
```

## Access
All agents (viewers are default-allowed per constitution)
