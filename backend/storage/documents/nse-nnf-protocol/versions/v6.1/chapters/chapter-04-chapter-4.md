---
title: "Chapter 4"
chapter_number: 4
page_range: "46-74"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

---
title: "Chapter 4"
chapter_number: 4
page_range: "46-74"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 4


## Introduction

This  section  describes  about  entering  new  orders,  modifying  existing  orders,  and  canceling outstanding orders. The trader can begin entering the orders once he has logged on to the trading system and the market is in pre-open or open state.

Please note this section is referenced in CM_DROP_COPY_PROTOCOL document. Any change here may also impact the Order Drop Copy functionality

## Order Entry

Order entry allows the trader to place orders in the market. The system accepts the orders from the users and tries to match the orders with the orders in the books immediately. If the order does not match, the order is placed in the appropriate book with the price and time stamp.

## NOTE:

When market status is pre-open, order entry request will be accepted only if pre-open indicator is set as '1', else orders will be rejected.

## Order Types

## Regular Lot

Regular  Lot  Orders  are  orders  in  the  normal  market  that  have  none  of  the  following  terms attached:      All Or None, Minimum Fill and Trigger Price.

Preopen Orders are Regular Lot orders placed when normal market is in Preopen. Pre-open orders will be identified by pre-open indicator. None of the following terms attached: DQ, All or None, Minimum Fill and Trigger Price.

## Special Terms

Special Terms Orders are orders in the normal market which have special attribute attached to it. They must have Minimum Fill (MF) or All Or None (AON).

## Stop Loss Orders

Stop Loss Orders are orders in normal market with Trigger Price specified. They may have the Minimum Fill or AON attribute specified.

## Odd Lot Orders

## Order and Trade Management

Odd lot orders are orders in the Odd Lot Market with the order quantity being less than the Regular lot quantity.

## Spot Orders

Spot Orders are orders in spot market where the settlement period is different from the normal market and is fixed by the exchange.

## Auction Orders

Auction Orders are simple day orders and can only have the 'Day' term set to 1. ATA (at Auction) Price is not allowed for auction. A valid price has to be entered. Currently, only those auctions that are initiated by the Exchange are allowed. The trader has to enter the solicitor orders after the auction is initiated and before it ends (during Solicitor Period). Auction Orders can only be cancelled. They cannot be modified.

## Call Auction

Call Auction order are orders placed in CALL AUCTION market that have none of the following terms attached: All or None, Minimum Fill and Trigger Price, Disclosed  quantity.

Call Auction 1 orders are IOC orders and Call Auction 2 orders are DAY orders with limit price. Both Call Auction 1 and Call Auction 2 orders have settlement period same as Normal market.

## Order Terms

Following terms and conditions can be used during order entry and order modification.

## Disclosed Quantity (DQ)

This term allows the dealer to disclose only a portion of the order quantity to the market. After the initial disclosed quantity is matched, subsequent disclosed quantity is shown to the market. All the disclosures will be shown to the market with the same order number.

## Trigger Price (TP)

The Stop Loss book type allows the broker to release an order into the system after the market price crosses a threshold price referred to as the trigger price. This facility is available for orders in Normal market only. For a stop loss buy order, the trigger price should not be greater than the limit price. For a stop loss sell order, the trigger price should not be less than the limit price. All the stop loss orders will be kept in a separate book till they are triggered.

## Immediate or Cancel (IOC)

This term forces the order to match immediately, else be cancelled. If the order trades partially, the remaining part is cancelled.

## Day

This is the default term for an order. At the end of the trading day, all outstanding Day orders are cancelled by the system.

## Good till Date (GTD)

This term allows the dealer to keep an order in the system for a certain number of days. The number of days must be greater than 1 and less than or equal to the maximum number of days allowed for GTC orders. Each day is a calendar day. This facility is disabled as of now.

## Good till Cancelled (GTC)

This term allows the broker to keep an order in the system until it is canceled. However, the order  is  canceled  by  the  system  automatically  if  it  remains  outstanding  for  more  than  the maximum number of days allowed for GTC orders. This facility is disabled as of now.

## Minimum Fill (MF)

This term allows the broker to ensure that the quantity traded is at least the Minimum Fill amount specified.  The  minimum  fill  must  be  in  multiples  of  the  market  lot  and  less  than  the  order quantity. MF quantity must be less than or equal to Disclosed Quantity when the order has both MF and Disclosed Quantity attributes.

## All or None (AON)

This term allows the broker to ensure that the entire order is traded and if not, nothing is traded at all. This can result in multiple trades or a single trade.

## Rules of Order Entry

Order entry is not allowed in the following conditions:

- Markets are closed.
- Security is suspended.
- Security has matured.
- Security is expelled.
- Security admission date is greater than current date.
- Security is not eligible in the particular market.

- Security does not exist in the system.
- Broker is suspended.
- Broker does not exist in trading system.
- Broker is deactivated.
- User's branch order limit has exceeded.
- User is disabled.
- User is an inquiry user.
- User does not exist in trading system.
- Participant is suspended.
- Participant does not exist in trading system.
- Order price is beyond day's minimum maximum range.
- Trigger price is worse than limit price.
- Quantity is more than issued capital.
- Quantity is not equal to multiples of regular lot.
- Disclosed Quantity is less than the given percentage (determined by exchange) of order Quantity.
- Disclosed Quantity is more than order Quantity.
- Disclosed Quantity is not equal to multiples of regular lot.
- MF Quantity is more than order Quantity.
- MF Quantity is not a multiple of regular lot.
- Limit Price is not a multiple of Tick Size.
- Trigger Price is not a multiple of Tick Size.
- GTC/GTD days more than specified days.
- Spot orders with GTC/GTD.
- Auction orders with GTC/GTD/IOC.

- IOC and Disclosed Quantity combination.
- Difference between limit price and trigger price in stop loss limit orders is greater than permissible range.

## Order Entry Request

The format of the order entry request is as follows:

| Structure Name | ORDER_ENTRY_REQUEST/RESPONSE |
| --- | --- |
| Packet Length | 290 bytes |
| Transaction Code | BOARD_LOT_IN (2000) |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| ParticipantType | CHAR |
| Reserved | CHAR |
| CompetitorPeriod | SHORT |
| SolicitorPeriod | SHORT |
| ModCxlBy | CHAR |
| Filler9 | CHAR |
| ReasonCode | SHORT |
| Reserved | CHAR |
| SEC_INFO (Refer Table 4) | STRUCT |
| AuctionNumber | SHORT |
| OpBrokerId | CHAR |
| Suspended | CHAR |
| OrderNumber | DOUBLE |
| AccountNumber | CHAR |
| BookType | SHORT |
| BuySell | SHORT |
| DisclosedVol | LONG |
| DisclosedVolRemaining | LONG |
| TotalVolRemaining | LONG |
| Volume | LONG |
| VolumeFilledToday | LONG |
| Packet Length | 290 bytes |
| Transaction Code | BOARD_LOT_IN (2000) |
| Field Name | Data Type |
| Price | LONG |
| TriggerPrice | LONG |
| GoodTillDate | LONG |
| EntryDateTime | LONG |
| MinFillAon | LONG |
| LastModified | LONG |
| ST_ORDER_FLAGS ( Refer Table 19.1 for small endian machines and Table 19.2 for big endian machines) | STRUCT |
| BranchId | SHORT |
| TraderId | LONG |
| BrokerId | CHAR |
| OERemarks | CHAR |
| Settlor | CHAR |
| ProClient | SHORT |
| SettlementType | SHORT |
| NNFField | DOUBLE |
| ExecTimeStamp | DOUBLE |
| Reserved | CHAR |
| PAN | CHAR |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| LastActivityReference | LONG LONG |
| Reserved | CHAR |

## For Small Endian Machines:

| Structure Name | ST_ORDER_FLAGS |
| --- | --- |
| Packet Length | 2 bytes |

| Field Name | Data Type | Size in Bit | Offset |
| --- | --- | --- | --- |
| MF | BIT | 1 | 0 |
| AON | BIT | 1 | 0 |
| IOC | BIT | 1 | 0 |
| GTC | BIT | 1 | 0 |
| Day | BIT | 1 | 0 |
| OnStop | BIT | 1 | 0 |
| Mkt | BIT | 1 | 0 |
| ATO | BIT | 1 | 0 |
| Reserved | BIT | 1 | 1 |
| STPC | BIT | 1 | 1 |
| Reserved | BIT | 1 | 1 |
| Preopen | BIT | 1 | 1 |
| Frozen | BIT | 1 | 1 |
| Modified | BIT | 1 | 1 |
| Traded | BIT | 1 | 1 |
| MatchedInd | BIT | 1 | 1 |

## For Big Endian Machines:

| Structure Name | ST_ORDER_FLAGS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| ATO | BIT |
| Mkt | BIT |
| OnStop | BIT |
| Day | BIT |
| GTC | BIT |
| IOC | BIT |
| AON | BIT |
| MF | BIT |
| MatchedInd | BIT |
| Traded | BIT |
| Modified | BIT |

| Frozen | BIT | 1 | 1 |
| --- | --- | --- | --- |
| Preopen | BIT | 1 | 1 |
| Reserved | BIT | 1 | 1 |
| STPC | BIT | 1 | 1 |
| Reserved | BIT | 1 | 1 |

The description and values of the fields are given below.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BOARD_LOT_IN (2000). |
| ParticipantType | Since only exchange can initiate the auction, this field should not be set to 'I' for initiator. This should be set to 'C' for competitor order and 'S' for solicitor order. |
| CompetitorPeriod | This field should be set to zero. |
| SolicitorPeriod | This field should be set to zero. |
| ModCxlBy | This field denotes which person has modified or cancelled a particular order. It should contain one of the following values: • 'T' for Trader • 'B' for Branch Manager • 'M' for Corporate Manager • 'C' for Exchange |
| ReasonCode | This field contains the reason code for a particular order request rejection or order being frozen. This has the details regarding the error along with the error code. This field should be set to zero while sending the request to the host. Refer to Reason Codes in Appendix. |
| SEC_INFO | This structure should contain the Symbol and Series of the security. |
| AuctionNumber | Auction number is available when initiation of auction is broadcast (Auction Status Change Broadcast). For an auction order, valid auction number should be given. For other books, this field should be set to zero. |
| OpBrokerId | This field will always be blank. |
| Suspended | This field specifies whether the security is suspended or not. It should be set to blank while sending order entry request. |
| AccountNumber | If the order is entered on behalf of a trader, the trader account number should be specified in this field. For broker's own order, this field should be set to the broker code. |
| BookType | This field should contain the type of order. Refer to Book Types in Appendix. MS_OE_REQUEST structure is not allowed with book type values 1 , 11 and 12 for following request transcodes 1)BOARD_LOT_IN(2000) 2)ORDER_MOD_IN(2040) 3)ORDER_CANCEL_IN(2070) Refer Trimmed Order Structure (See Appendix - Trimmed Request Structures) for placing following orders transcodes with book type 1 or 11 or 12 1)For BOARD_LOT_IN (2000), use struct MS_OE_REQUEST_TR with transcode as 20000 2)For ORDER_MOD_IN (2040), use struct MS_OM_REQUEST_TR with transcode as 20040 3)For ORDER_CANCEL_IN (2070), use struct |
| BuySell | This field should specify whether the order is a buy or sell. It should take one of the following values. • '1' for Buy order • '2' for Sell order |
| DisclosedVol | This field should specify the quantity that has to be disclosed to the market. It is not applicable if the order has either the All Or None or the Immediate Or Cancel attribute set. It should not be greater than the volume of the order and not less than the Minimum Fill quantity if the Minimum Fill attribute is set. In either case, it cannot be less than the Minimum Disclosed Quantity allowed. It should be a multiple of the Regular lot. |
| DisclosedVolRemaining | This field contains the disclosed volume remaining from the original disclosed volume after trade(s). This should be set to zero while sending to the host. |
| TotalVolRemaining | This field specifies the total quantity remaining from the original quantity after trade(s). For order entry, this field should be set to Volume. Thereafter, for every response the trading system will return this value. |
| Volume | This field should specify the quantity of the order placed. The quantity should always be in multiples of Regular Lot except for Odd Lot orders, and be less than the issued capital. The order will go for a freeze if the quantity is greater than the freeze quantity determined by NSE-Control. |
| VolumeFilledToday | This field contains the total quantity traded in a day. |
| Price | This field should contain the price at which the order is placed. To enter a Market order, the price should be zero. The price must be a multiple of the tick size. For Stop Loss orders, the limit price must be greater than the trigger price in case of a Buy order and less if it is a Sell order. This is to be multiplied by 100 before sending to the trading system host. |
| TriggerPrice | This field is applicable only for a Stop Loss order and should be a multiple of the tick size. This field should contain the price at which the order is to be triggered and brought to the market. For a Stop Loss buy order, the trigger price will be less than or equal to the limit price but greater than the last traded price. For a Stop Loss sell order, the trigger price will be greater than or equal to the limit price but less than the last traded price. This is to be multiplied by 100 before sending to trading system. |
| GoodTillDate | This field should contain the number of days for a GTD order. This field may be set in two ways. To specify an absolute date set this field to that date in number of seconds since midnight of January 1, 1980. To specify days set this to the number of days. This can take values from 2 to the maximum days specified for GTC orders only. If this field is non-zero, the GTC flag must be off. |
| EntryDateTime | This field should be set to zero while sending the order entry request. |
| MinimumFillAon | This field should contain the minimum fill quantity when the minimum fill attribute is set for an order. It should not be greater |
|  | than either the volume of the order or the disclosed quantity and must be a multiple of the regular lot. |
| LastModified | If the order has been modified, this field contains the time when the order was last modified. It is the time in seconds from midnight of January 1 1980, This field should be set to zero for the order entry request (it is same as Entry Date Time.) |
| Order_Flags | This structure specifies the attributes of an order. They are: • MF if set to 1, represents Minimum Fill attribute. • AON if set to 1, represents All Or None attribute. • IOC if set to 1, represents Immediate Or Cancel attribute. • GTC if set to 1, represents Good Till Cancel. • Day if set to 1, represents Day attribute. This is the default attribute. • SL if set to 1, represents Stop Loss attribute. • Mkt if set to 0, represents a Market order. • ATO if set to 1, represents a market order in PREOPEN or CALL AUCTION1 or CALL AUCTION 2 market. o For CALL AUCTION1 order, if it is market order, ATO bit should set to 1 & IOC bit needs to be set for mkt as well as limit orders. o For CALL AUCTION2 order,ATO& Mkt bit should set to 0 as market orders are not allowed for the same. • STPC if set to 0, represents order resulting in self-trade to be cancelled as per default action by the exchange if set to 1, represents active order resulting in self-trade to be cancelled o Order modification will be rejected if this bit is modified. In case of triggered stop loss order, bit selected during order entry will be considered. • Preopen if set to 1, represents the order is a Preopen session order and if set to 0, represents Normal Market Open order. |

| Field Name | Brief Description |
| --- | --- |
|  | o Preopen bit should be set to 1 for orders in Call Auction 2 market. • Frozen if set to 1, represents the order has gone for a freeze. • Modified if set to 1, represents the order is modified. • Traded if set to 1, represents the order is traded partially or fully. For a market order, the price should be 0. The Bit fields must be set / unset by Front end as mentioned in the description. |
| BranchId | This field should contain the ID of the branch of the particular broker. |
| TraderId | This field should contain the ID of the user. This field accepts only numbers. |
| BrokerId | This field should contain the trading member ID. |
| OERemarks | This field may contain any remarks that the dealer can enter about the order in this field. |
| Settlor | This field contains the ID of the participants who are responsible for settling the trades through the custodians. By default, all orders are treated as broker's own orders and this field defaults to the Broker Code. |
| ProClient | This field should contain one of the following values based on the order entering is on behalf of the broker or a trader. '1' - represents the client's order. '2' - represents a broker's order. '4' - represents warehousing order. |
| SettlementType | This field contains the settlement type. It can be one of the following: '0' - T+0 settlement '1' - T+1 settlement This field should be set to zero while sending to the host. |
| NNFField | This field should contain a 15 digit a unique identifier for various products deployed as per Exchange circular download ref no. 16519 dated December 14, 2010 and as updated from time to time |
| ExecTimeStamp | This field is used to store the time of writing to the order book. This should be set to zero while sending to the host. |
| PAN | This field shall contain the PAN (Permanent Account Number / PAN_EXEMPT) - This field shall be mandatory for all orders (client / participant / PRO orders). |
| Algo ID | For Algo order this field shall contain the Algo ID issued by the exchange. For Non-Algo order, this field shall be Zero(0) |
| Reserved Filler | This field is reserved for future use. This should be set to Zero (0) while sending to the exchange trading system. |
| LastActivityReference | This field should be set to zero while sending the order entry request. |

## Order Entry Response

The response can be Order Confirmation, Order Freeze, Order Error or one of the general error responses.  Order  Freeze  response  is  not  expected  for  Auction  Order  Entry.  Order  freeze response is generated when the order placed by the trader has resulted in freeze and is waiting for the approval of the exchange. The order error response is given when the entered order is rejected by the trading system. The reason for the rejection is given by Error Code.

## Order Confirmation Response

Successful order entry results in Order Confirmation Response. The confirmed order is returned to the user. When the entered order goes for a freeze and that freeze is approved, this same transaction code is sent. This can be an unsolicited message as well. The message sent is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_CONFIRMATION (2073). |
| Suspended | This field contains 'C' if the broker is in Closeout. |
| OrderNumber | This field contains an Order Number assigned to the order. It is a unique identification for an order. The first two digits will contain the stream number (This will be different from the stream number for Journal Download Request-Response). The next fourteen digits will contain fourteen digit sequence number. |
| Price | This field contains the price of the order. If a Market order was entered when market was in Open state, the 'Market' flag in Order Terms is set and is priced at the prevailing price at the trading system. If the market order is entered when the market was in preopen, the trading system sets the 'ATO' bit in Order Terms and prices at ' - 1'. If it was a priced order the order gets confirmed at that price. |
| Order_Flags | (Refer to Order Entry Request in Chapter 4) |
| EntryDateTime | This field contains the time at which order confirmed. |
| LastActivityReference | This field contains a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Market Price Confirmation Response

Market Price response is generated only when the order placed by the trader is a market order and the market order entered is not fully traded at exchange. This response is not expected for the limit orders.  The response packet is sent only when there is any untraded quantity left in the order.

The message sent is:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is PRICE_CONFIRMATION (2012). |
| Price | This field contains the price of the order. If a Market order was entered when market was in Open state, the 'Market' flag in Order Terms is set and price is set at the prevailing price at the trading system. If the market order is entered when the market was in preopen, this transcode is not received. For Buy order the Price will be negative but for Sell order it will be positive |

## Order Freeze Response

Order  freeze  response  is  generated  when  the  order  placed  by  the  trader  or  the  order  after modification is awaiting approval from the exchange. This response is not expected for Auction Orders. Exchange approval of the order results in a Freeze Approval Response and rejection results  in  Freeze  Reject  Response.  These  responses  are  sent  as  unsolicited  messages.  The format sent is as follows:

ORDER ENTRY REQUEST (Refer to Order Entry Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is FREEZE_TO_CONTROL (2170). |
| Order_Flags | (Refer to Order Entry Request in Chapter 4) |

## Order Error Response

The order error response is sent when the entered order is rejected by the trading system. The reason for the rejection is given by the reason code and the reason string. The message sent is:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_ERROR (2231). |
| ErrorCode | This field contains the error number. Refer to List of Error Codes in Appendix. |
| Suspended | This field contains 'C' if the broker is in Closeout. |

## Order Modification

Order  Modification  enables  the  trader  to  modify  unmatched  orders.  All  order  types  except Auction can be modified.

## Rules of Order Modification

The following modifications are not allowed:

- Buy to Sell or vice versa.
- Modifying Symbol and Series.
- Modifying Participant field.

- Modifying Pro/Cli field.
- Modifying Frozen orders.
- BM modifying CM's orders.
- DL modifying BM's orders.
- DL modifying CM's orders.
- Modifying non existing order.
- Inquiry user trying to modify.
- Modifying an order in such a way that it results in a branch order value to be exceeded.
- Modifying Auction orders.
- Modifying deactivated broker's orders.
- Changing of original data.
- Modifying AU, SP, OL book type fields.
- Difference between limit price and trigger price in stop loss limit orders is greater than permissible range.

> [!note]
> RL/ST/SL book types can be toggled between themselves only.  They cannot be modified to AU or SP or OL.

## Order Modification Request

The trader  can  modify  the  quantity,  price  and  attributes  of  an  order  by  specifying  the  order number of the order to be modified. The message sent is:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_MOD_IN (2040). |
| OrderNumber | This should contain order number which is the identity of the order to be modified. |
| LastModifiedTime | This should contain time of last activity done on that order. Last activity could be order entry, order modification or last trade time of that order. It is in number of seconds from midnight of January 1, 1980, |
| LastActivityReference | This field should contain LastActivityReference value received in response of last activity done on that order. Last activity could be order entry confirmation, order modification confirmation or last trade of that order. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Order Modification Confirmation Response

Successful modification of the order results in Order Modification Confirmation. When the order modification is confirmed, the order-modified time is filled and sent back. On modification, the order can result in a freeze. If the freeze is approved, order modification will be received as an 'Unsolicited Message'.

Unmatched ATO/ Limit Pre-open orders are carried forward to the Normal Market without any change in time priority. For unmatched ATO orders which are carried forward, derived price will be  assigned,  response for  these  orders  will  be  sent  to  traders  as  'Unsolicited'  modification response.

Unmatched Limit Pre-open orders are cancelled or carried forward to the Normal Market without any change in time priority for IPO/Relisting securities.

Unmatched limit Pre-open orders are carried forward to the next session without any change in time priority for illiquid securities

The structure sent is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_MOD_CONFIRMATION (2074). |
| LastModifiedTime | This field contains the time when the order was last modified. It is in number of seconds from midnight of January 1, 1980, |
| EntryDateTime | This field contains the time at which last modified by user. It is in number of seconds from midnight of January 1, 1980, |
| ModCxlBy | This field will be set to `C` for the unmatched ATO orders, which are being carried forward to the Normal Market. |
|  | This field will be set to `F` for the unmatched orders, which are being carried forward to the Normal Market from call auction 2 market for IPO/Relisting securities. Unmatched ATO orders are assigned derived price and are carried forward to the Normal Market. |
| Order_Flags | Preopen - This bit will be set to 1 for pre-open order modification response during pre-open market session and during Normal market session (for the carried forward orders). Preopen - This bit will be set to 1 for Call Auction 2 order modification response during Call Auction2 pre-open session and during Normal market session (for the carried forward orders) for IPO/Relisting securities. It will be set to 0 for Normal Market Open order modification response |
| LastActivityReference | This field contains a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Order Modification Error Response

The reason for rejection is given by the Error Code in the header. The message sent is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_MOD_REJECT (2042). |
| Order_Flags | This bit will be set to 1 for pre-open order modification response during pre-open market session and during Normal market session (for the carried forward orders). Preopen - This bit will be set to 1 for Call Auction 2 order modification response during Call Auction2 pre-open session and during Normal market session (for the carried forward orders) for IPO/Relisting securities. It will be set to 0 for Normal Market Open order modification response |
| Reason code | For Call Auction2, the reason code 24 will be sent. Refer to List of Reason Codes in Appendix. |

## Effect of Modifying the Terms of an Order on Price-Time Priority

| Field Name | Can Change | Comments |
| --- | --- | --- |
| Buy/Sell | No |  |
| Order Type |  | Refer to Rules of Order Modification |
| Symbol | No |  |
| Series | No |  |
| Price | Yes | Changing the order price will always result in the order losing its time priority. |
| Quantity | Yes | The quantity of an order can be reduced any number of times without the order losing its time priority. However, increasing the quantity of an order will always result in the order losing its time priority. |
| PRO/CLI | No |  |
| Account No. | No |  |
| Day | Yes | Changing to or from a Day order retains time priority |
| GTC | Yes | Changing to or from a GTC order retains time priority |
| GTD | Yes | Changing to or from a GTD order retains time priority |
| Days in GTD | Yes |  |
| DQ | Yes | Time Priority shall be lost if: - ChangedDQ leads to an increase in quantity disclosed in the order book - DQ changed to non-DQ or vice versa and quantity disclosed in the order book increases |
| MF & AON | Yes | Changing MF to AON order or vice-versa will result in the order losing its time priority. |
| MF | Yes | Same as in Quantity. |
| SL | Yes | A SL order can be changed to a normal limit order or a Special Terms order by removing the SL attribute. The SL limit and trigger price can also be changed. In each of these cases the order loses its time priority. |
| Participant | No |  |
| Remarks | Yes | Changing this does not change time priority. |
| Note: When the order quantity of an ATO or 'Market' order is modified, the order loses priority irrespective of increase or decrease in the quantity. |  |  |

## Order Cancellation

The trader can cancel any unmatched/partially matched order by specifying the order number.

In after order collection period, the call auction order matching will be done. Once matching is completed the IOC orders which were not traded will get cancelled by the system, the transcode ORDER_CANCEL_CONFIRMATION (2075) will be sent.

In case of circuit hit, if Order collection phase is planned, orders related to normal market which were not traded will get cancelled by the system, the transcode ORDER_CANCEL_CONFIRMATION (2075) will be sent.

## Rules of Order Cancellation

- CM can cancel BM's and DL's order, but BM and DL cannot cancel CM's order.
- BM can cancel DL's order, but DL cannot cancel BM's order.
- Deactivated broker cannot cancel his/her order.
- Auction orders cannot be cancelled after auction is finished.
- In case of CALL AUCTION 2 market, it is mandatory to mention a non-zero value in the price field.

## Order Cancellation Request

The format of the message is as follows:

ORDER ENTRY REQUEST (Refer to Order Entry Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_CANCEL_IN (2070). |
| OrderNumber | This field should contain the order number which is the identity of the order to be cancelled. |
| Last ModifiedTime | This should contain time of last activity done on that order. Last activity could be order entry, order modification or last trade time of that order. It is in number of seconds from midnight of January 1, 1980, |
| LastActivityReference | This field should contain LastActivityReference value received in response of last activity done on that order. Last activity could be order entry confirmation, order modification confirmation or last trade of that order. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Order Cancellation Response

The response can be Order Cancellation Confirmation, Order Cancellation Error or one of the general error responses.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_CANCEL_IN (2070). |

## Order Cancellation Confirmation Response

Successful cancellation of order results in Order Cancellation Confirmation Response. This will be an 'Unsolicited Message ' if NSE-Control cancels the order. The message sent is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_CANCEL_CONFIRMATION (2075). |
| Suspended | This field contains 'C' if the broker is in Closeout. |
| ModCxlBy | This field will be set to `C` for unmatched Pre-open orders cancelled by the Exchange. It will be blank for Pre-open orders which are cancelled by the trader in Preopen session and in Normal Market session. This field will be set to `C` for unmatched Call Auction orders cancelled by the Exchange. |
|  | It will be blank for Call Auction2 orders which are cancelled by the trader in Call Auction 2 Preopen session and in Normal Market session for IPO/Relisting securities. |
| Order_Flags | This bit will be set to 1 for Pre-open order cancellation response and Pre-open carried forward order cancellation response. Preopen - This bit will be set to 1 for Call Auction 2 order modification response during Call Auction2 pre-open session and during Normal market session (for the carried forward orders) session for IPO/Relisting securities. It will be set to 0 for Normal Market Open order modification response |
| LastActivityReference | This field contains a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Order Cancellation Error Response

The order cancellation error is sent when the cancellation request is rejected by the  trading system. The reason for rejection is given by the Error Code in the header. The message sent is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_CANCEL_REJECT (2072). |
| Order_Flags | Preopen - This bit will be set to 1 for Pre-open order cancellation response and Pre-open carried forward order cancellation response. Preopen -This bit will be set to 1 for Call Auction 2 order modification response during Call Auction2 pre-open session and during Normal market session (for the carried forward orders) for IPO/Relisting securities. And it will be set to 0 for Normal Market Open order cancellation response |

## Kill Switch

This functionality provides a facility to traders to cancel all of their orders at the same time.

Also, user can cancel all outstanding orders on particular security by specifying security information in request packet.

## Kill Switch Request

The format of the message is as follows:

ORDER ENTRY REQUEST       (Refer to Order Entry Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is KILL_SWITCH_IN (2062). |
| User | This field should contain the user id for which orders should be cancelled. |
| SEC_INFO | For cancellation of all orders, Symbol and series fields should be set as blank. For cancellation of all orders on particular security, this structure should contain the Symbol and Series of the security. |

## Kill Switch Response

The Quick cancel out response is sent when the kill switch is requested by the user. The message sent is as follows:

ORDER ENTRY REQUEST       (Refer to Order Entry Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is QUICK_CANCEL_OUT(2061) |

## Kill Switch Error Response

The kill switch error is sent when the request is rejected by the trading system. The reason for rejection will be given by the Error Code in the header. The message sent is as follows:

ORDER ENTRY REQUEST       (Refer to Order Entry Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_ERROR (2231). |

## Trade Modification

This  functionality  provides  facility  to  traders  to  modify  the  trades.  Only  account  number modification is allowed.

## Following modifications are not allowed:

- Modifying Trade Quantity
- Modifiying Pro/Cli field
- Modifying Participant field.
- BM modifying CM's trades.
- DL modifying BM's trades.
- DL modifying CM's trades.
- Modifying non existing trade.
- Modifying Auction trades.

## Trade Modification Request

The format of the message is as follows:

## Table 20 TRADE_INQUIRY_DATA

| Structure Name | TRADE_INQUIRY_DATA |
| --- | --- |
| Packet Length | 210 Bytes |
| Transaction Code | TRADE_MOD_IN (5445) |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| SEC_INFO (Refer Table 4) | STRUCT |
| FillNumber | LONG |
| FillQty | LONG |
| FillPrice | LONG |
| MarketType | SHORT |
| NewVolume | LONG |
| Reserved | CHAR |
| BuyBrokerId | CHAR |
| SellBrokerId | CHAR |
| TraderId | LONG |
| Packet Length | 210 Bytes |
| Transaction Code | TRADE_MOD_IN (5445) |
| Field Name | Data Type |
| RequestedBy | SHORT |
| BuyAccountNumber | CHAR |
| SellAccountNumber | CHAR |
| BuyPAN | CHAR |
| SellPAN | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_MOD_IN (5445). |
| SEC_INFO | This structure should contain the Symbol and Series of the security. |
| FillNumber | This field should contain the trade number of the trade to be modified. |
| FillQuantity | This field should contain the quantity that has been traded. |
| FillPrice | This field should contain the price at which the trade took place. This is to be multiplied by 100 before sending to the trading system host. |
| MarketType | This field should contain the value to denote the type of market, • '1' for Normal Market. • '2' for Odd Lot Market • '3' for Spot Market • '4' for Auction Market • '5' for CA1 • '6' for CA2 |
| NewVolume | This field value should be same as that of FillQuantity. |
| Buy / SellBrokerId | This field should contain the trading member ID of the broker who placed the order for the trade or the one who is responsible for the settlement. |
| TraderId | This field should contain the ID of the user on whose behalf request is to be made. |
| RequestedBy | This field indicates which side (Buy/Sell) of the trade is to be modified/cancelled. This should contain one of the following values • '1' (BUY) if the buy side is to be modified/cancelled • '2' (SELL) if the sell side is to be modified/cancelled • '3' (BUY & SELL) if both the sides are to be modified/cancelled . |
| BuyAccountNumber | This field should contain the Account Number of the trade on Buy side. |
| SellAccountNumber | This field should contain the Account Number of the trade on Sell side. |
| BuyPAN | This field shall contain the PAN (Permanent Account Number/PAN_EXEMPT). This field shall be mandatory for all orders (client/participant/PRO orders). |
| SellPAN | This field shall contain the PAN (Permanent Account Number/PAN_EXEMPT). This field shall be mandatory for all orders (client/participant/PRO orders). |

## Trade Modification Confirmation Response

This message is sent when trade modification is confirmed by exchange trading system and corresponding new trade data is sent.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_MODIFY_CONFIRM (2287). |
| LogTime (of MESSAGE_HEADER) | This will contain the activity Time i.e., the latest modified time. |

## Trade Modification Error

If trade modification request is rejected due to erroneous data, then the structure sent is:

MS_TRADER_INT_MSG (Refer to Interactive/Broadcast Messages Sent from Control discussed later in this chapter)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is CTRL_MSG_TO_TRADER (5295). |
| ErrorCode | Refer to List of Error Codes in Appendix. |

## Trade Cancellation

To cancel a trade, both the parties of the trade must request for trade cancellation. As soon as the request reaches the trading system, a requested message is sent. If any error is encountered in the entered data, Trade Error message is sent. Otherwise, it goes to the NSE-Control as an alert. The counter party to the trade is notified of the trade cancellation request (Refer to Trade Cancel Requested Notification in [Chapter 5](#chapter-5-unsolicited-messages)). When both the parties of the trade ask for trade cancellation,  it  may  be  approved  or  rejected  by  the  Exchange  (Refer  to Trade  Cancellation Confirmation in [Chapter 5](#chapter-5-unsolicited-messages)).

## Trade Cancellation Request

The format of the message is as follows:

TRADE_INQUIRY_DATA ( Refer to Trade Modification Request in Chapter 4

)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CANCEL_IN (5440). |
| FillNumber | This field should contain the trade number of the trade to be cancelled. |

## Trade Cancellation Requested Response

This is an acknowledgement signifying that the request has reached the trading system.

The following structure is sent:

TRADE INQUIRY DATA (Refer to Trade Modification Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CANCEL_OUT (5441). |

## Trade Cancellation Error

After the requested response, if any error is detected in the data, the following structure is sent:

TRADE INQUIRY DATA (Refer to Trade Modification Request in Chapter 4)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_ERROR (2223) |
| ErrorCode | Refer to List of Error Codes in Appendix. |