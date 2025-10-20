# NSE CM API Documentation

## 1. Introduction

This document describes the NSE Capital Market API for order management and trading.

### 1.1 Purpose

The API provides programmatic access to trading functions including:
- Order placement
- Order modification
- Order cancellation
- Market data retrieval

### 1.2 Audience

This documentation is intended for developers integrating with NSE trading systems.

## 2. Order Management

### 2.1 Order Entry

Submit new orders using the ORDER_ENTRY message type.

#### 2.1.1 Message Format

The order entry message contains:
- Client ID
- Symbol
- Quantity
- Price
- Order type (Market/Limit)

#### 2.1.2 Validation Rules

All orders must pass the following validations:
- Valid client ID
- Authorized symbol
- Positive quantity
- Price within circuit limits

### 2.2 Order Modification

Modify existing orders using the ORDER_MODIFY message.

#### 2.2.1 Allowed Modifications

You can modify:
- Quantity (increase or decrease)
- Price (for limit orders)
- Order validity

#### 2.2.2 Restrictions

You cannot modify:
- Order type (Market to Limit or vice versa)
- Symbol
- Client ID

### 2.3 Order Cancellation

Cancel pending orders using the ORDER_CANCEL message.

## 3. Market Data

### 3.1 Real-Time Data

Subscribe to real-time market data feeds for price updates.

### 3.2 Historical Data

Query historical OHLCV data for backtesting and analysis.

## 4. Error Handling

### 4.1 Error Codes

| Code | Description |
|------|-------------|
| E001 | Invalid client ID |
| E002 | Symbol not found |
| E003 | Insufficient funds |
| E004 | Circuit limit breach |

### 4.2 Error Recovery

Implement retry logic with exponential backoff for transient errors.

## 5. Appendix

### 5.1 Glossary

- **OHLCV**: Open, High, Low, Close, Volume
- **Circuit Limit**: Price band within which a stock can trade

### 5.2 References

For more information, visit: https://www.nseindia.com
