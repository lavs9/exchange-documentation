---
title: "Chapter 5 Unsolicited Messages"
chapter_number: 5
page_range: "74-82"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 5 Unsolicited Messages


## Introduction `[p.74]`

This section details the unsolicited messages that are received on the interactive connection. These messages are not received by the users in response to any request. `[p.74]`

Please note this section is referenced in CM_DROP_COPY_PROTOCOL document. Any change here may also impact the Order Drop Copy functionality. `[p.74]`

## Cancellation of Orders in Batch `[p.74]`

GTC\GTD orders which are  valid  till  date,  if  not  traded,  are  also  removed  from  the  book.  A response for the same is sent to the user. As of now GTC and GTD facilities are not allowed hence there will be GTC and GTD orders. The structure sent is: `[p.74]`

ORDER ENTRY REQUEST (Refer to Order Entry Request in [Chapter 4](#chapter-4)) `[p.74]`

*Table (p.74)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BATCH_ORDER_CANCEL (9002). |

## Stop Loss Order Triggering `[p.74]`

When  any  stop  loss  order  entered  is  triggered,  the  user  who  entered  the  order  is  sent  the following message: `[p.74]`

*Table (p.74)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ON_STOP_NOTIFICATION (2212). |

## Freeze Approve Response `[p.74]`

This  message  is  sent  when  a  previous  order,  which  resulted  in  freeze,  is  approved  by  the Exchange. The format of the message is as follows: `[p.74]`

*Table (p.74)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction codes are: If the entered order went for a freeze, and then got freeze approval, ORDER_CONFIRMATION (2073). |

*Table (p.75)*

|  | If the modified order went for a freeze, and then got freeze approval, ORDER_MOD_CONFIRMATION (2074). |
| --- | --- |
| LastModifiedDateTime | This field contains the time when the order was last modified. |
| LastActivityReference | This field contains a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Freeze Reject Response `[p.75]`

This  message  is  sent  when  a  previous  order,  which  resulted  in  freeze,  is  rejected  by  the Exchange. The format of the message is as follows: `[p.75]`

*Table (p.75)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction codes are: If the entered order went for a freeze, then for freeze reject ORDER_ERROR_OUT (2231). If the modified order went for a freeze, then for freeze reject ORDER_MOD_REJECT_OUT (2042). |

## Trade Confirmation `[p.75]`

Trade confirmation is an unsolicited message which is generated when any order of the trader is traded.  The  order  may  trade  completely  or  partially.  In  Trade  confirmation  message,  the ST_ORDER_FLAGS  structure  is  modified,  to  identify  Call  Auction2  session  trades.  In  this structure Preopen indicator is defined (which will be set to 1 for trades in Call Auction2 session), this is incorporated using an existing Filler bit, in the ST_ORDER_FLAGS structure as explained below: `[p.75]`

*Table (p.75-76)*

| Structure Name | MS_TRADE_CONFIRM |
| --- | --- |
| Packet Length | 228 bytes |
| Transaction Code | TRADE_CONFIRMATION (2222) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| ResponseOrderNumber | DOUBLE |
| BrokerId | CHAR |
| Reserved | CHAR |
| Packet Length | 228 bytes |
| Transaction Code | TRADE_CONFIRMATION (2222) |
| Field Name | Data Type |
| TraderNum | LONG |
| AccountNum | CHAR |
| BuySell | SHORT |
| OriginalVol | LONG |
| DisclosedVol | LONG |
| RemainingVol | LONG |
| DisclosedVolRemaining | LONG |
| Price | LONG |
| ST_ORDER_FLAGS ( Refer Table 19.1 for small endian machines and Table 19.2 for big endian machines) | STRUCT |
| Gtd | LONG |
| FillNumber | LONG |
| FillQty | LONG |
| FillPrice | LONG |
| VolFilledToday | LONG |
| ActivityType | CHAR |
| ActivityTime | LONG |
| OpOrderNumber | DOUBLE |
| OpBrokerId | CHAR |
| SEC_INFO (Refer Table 4) | STRUCT |
| Reserved | CHAR |
| BookType | SHORT |
| NewVolume | LONG |
| ProClient | SHORT |
| PAN | CHAR |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| LastActivityReference | LONG LONG |
| Reserved | CHAR |

*Table (p.77-78)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CONFIRMATION (2222). |
| ResponseOrderNumbe r | This field contains the order number of the trader's order taking part in the trade. |
| BrokerId | This field contains the Trading Member ID. |
| TraderNum | This field contains the trader's or user ID. |
| AccountNum | This field contains the Account Number or Client code. |
| BuySell | This field contains one of the following values based on Buy/Sell. '1' for Buy '2' for Sell. |
| OriginalVol | This field contains the Original traded volume. |
| DisclosedVol | This field contains the quantity to be disclosed to the market. It is not applicable if the order has either the All Or None or the Immediate Or Cancel attribute set. It should not be greater than the volume of the order and not less than the Minimum Fill quantity if the Minimum Fill attribute is set. In either case, it cannot be less than the Minimum Disclosed Quantity allowed. It should be a multiple of the Regular lot. |
| RemainingVol | This field contains the volume remaining after trade(s). |
| DisclosedVolRemaining | This field contains the disclosed volume remaining after trade(s). |
| Price | This field contains the order price. |
| OrderFlags | (Refer to Order Entry Request in [Chapter 4](#chapter-4)) Note : Preopen Indicator will be set as 0 for the trades happening in Normal Market session for Normal Market orders and pre-open carried forward orders Preopen indicator will be set as 1 for trades happening in the call auction 2 market. |
| Gtd | This field contains the number of days for a GTD Order. This field can be set in two ways as given below. To specify an absolute date, set this field to that date in number of seconds since midnight of January 1, 1980. To specify days, set this to the number of days. This can take values from 2 to the maximum days specified for GTC orders only. If this field is non-zero, the GTC flag must be off. |
| FillNumber | This field contains the trade number. |
| FillQty | This field contains the traded volume. |
| FillPrice | This field contains the price at which order is traded. |
| VolFilledToday | This field contains the quantity traded today. |
| ActivityType | This field contains the activity type. 'B' for Buy 'S' for Sell |
| ActivityTime | This field contains the time when the activity took place. |
| OpOrderNumber | This field will always be blank. |
| OpBrokerId | This field will always be blank. |
| SEC_INFO | This field contains the Symbol and Series of the security. |
| BookType | This field contains the book type - RL/ ST/ SL/ OL/ SP/ AU/CA/CB. |
| NewVolume | This field is always set to zero for trade confirmation. |
| ProCli | This field is same as Pro/Client /WHS indicator having one of the following values: '1' - client's order '2' - broker's order '4' - warehousing order |
| PAN | This field contains the PAN |
| Algo ID | This field shall contain the Algo ID |
| Reserved Filler | This field is reserved for future use |
| LastActivityReference | This field contains a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Preopen `[p.78]`

Preopen Indicator will be set as 0 for the trades happening in Normal Market session for Normal Market orders and carried forward orders. `[p.78]`

Preopen Indicator will be set as 1 for the Preopen Trades happening in the Opening Phase. `[p.78]`

> [!note]
> All trades for CALL AUCTION 2 market will be sent with Book type Regular Lot (1). `[p.78]`

## Trade Cancellation `[p.78]`

## Trade Cancellation Requested Notification `[p.78]`

This message is sent when the counter party of the trade requests a trade cancellation. The structure sent is: `[p.78]`

MS_TRADER_INT_MSG (Refer to Interactive/Broadcast Messages Sent from Control discussed later in this chapter) `[p.79]`

*Table (p.79)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is CTRL_MSG_TO_TRADER (5295). |

## Trade Cancellation Confirmation Response `[p.79]`

When NSE-Control approves the trade cancellation request the structure sent is: `[p.79]`

TRADE CONFIRM (Refer to Trade Confirmation discussed earlier in this chapter) `[p.79]`

*Table (p.79)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CANCEL_CONFIRM (2282). |

## Trade Cancellation Rejection `[p.79]`

When NSE-Control rejects the trade cancellation alert the structure sent is: `[p.79]`

TRADE CONFIRM (Refer to Trade Confirmation discussed earlier in this chapter) `[p.79]`

*Table (p.79)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CANCEL_REJECT (2286). |

## Interactive/Broadcast Messages Sent from Control `[p.79]`

A message can be sent to the trader(s) from the NSE-Control Work Station. If it is sent to all the traders,  it  comes  as  a  broadcast  in  the  structure  BROADCAST_MESSAGE.  (Refer  to General Message Broadcast in [Chapter 7](#chapter-7-broadcast)) `[p.79]`

When the message is sent to a particular user, it comes as an interactive message in the following structure: `[p.79]`

*Table (p.79)*

| Structure Name | MS_TRADER_INT_MSG |
| --- | --- |
| Packet Length | 290 bytes |

*Table (p.80)*

| Transaction Code | CTRL_MSG_TO_TRADER (5295) |
| --- | --- |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| TraderId | LONG |
| ActionCode | CHAR |
| Reserved | CHAR |
| MsgLength | SHORT |
| Msg | CHAR |

*Table (p.80)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction codes are: CTRL_MSG_TO_TRADER (5295) for interactive messages |
| ActionCode | This field contains the action code to indicate the action taken. For example, 'SYS' - System 'AUI' - Auction Initiation 'AUC' - Auction Complete 'LIS' - Listing |

*Table (p.80)*

| Structure Name | MS_TRADER_INT_MSG |
| --- | --- |
| Packet Length | 298 bytes |
| Transaction Code | BCAST_JRNL_VCT_MSG (6501) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| BranchNumber | SHORT |
| BrokerNumber | CHAR |
| ActionCode | CHAR |
| Reserved | CHAR |
| BROADCAST DESTINATION (Refer Table 23.1) | STRUCT |
| MsgLength | SHORT |
| Msg | CHAR |

*Table (p.81)*

| Structure Name | BROADCAST DESTINATION |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| TraderWs | BIT |
| Reserved | CHAR |

*Table (p.81)*

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | BCAST_JRNL_VCT_MSG (6501) for broadcasting messages. |
| ActionCode | This field contains the action code to indicate the action taken. For example, 'SYS' - System 'AUI' - Auction Initiation 'AUC' - Auction Complete 'LIS' - Listing 'MAR' - Margin violation messages |