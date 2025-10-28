---
title: "Chapter 7 Broadcast"
chapter_number: 7
page_range: "89-150"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 7 Broadcast


## Introduction

This section describes the Compression and Decompression algorithm of Broadcast data and the various Broadcast messages with their structures.

## Compression of the Broadcast Data

The broadcast traffic from the exchange which gives the on-line quotes to the trading terminals has  been  continually  increasing,  especially  during  market  open  and  market  close.  To accommodate the increased broadcast traffic, the exchange has come up with a compression algorithm to compress some of the specific broadcast transaction codes, which are as follows:

| Transaction Code | Represents |
| --- | --- |
| 7201 | Mkt Watch |
| 18703 | Ticker |
| 7208 | Only MBP |
| 7214 | Call AuctionMBP |
| 7215 | BROADCAST CALL AUCTION MARKET WATCH |
| 7210 | Order Cancel Update |

LZO  compression  algorithm  is  used  to  compress  the  above  specified  broadcast  transaction codes. The details of the LZO compression algorithm are described below.

The LZO stands for Lempel Ziv Oberhaumer. This algorithm is freely available on the internet (URL:  http://www.oberhumer.com/opensource/lzo).  It  is  made  available  by  free  software foundation. The algorithm is tested on various operating systems like UNIX and red hat Linux.

## Decompression Routine

## Sequential Packing

To  improve  the  effective  data  transfer,  the  idea  of  sequential  packing  along  with  the  lzo compression algorithm has been incorporated. At the host end, sequential packing algorithm packs the incoming data packets, which is then transmitted over the network. The data packets are packed in FIFO order.

For example,

If 'n' packets are packed in a buffer, they are arranged in the following order:

1 st packet will be stored at the first place in the buffer, 2 nd  Packet will be stored at the second place, and so on.

At the front end while de packing the buffer, the packets are to be segregated in the same order, that is, isolate each packet and process each packet as per the sequence viz- first packet first and last packet at the end. The packets within a buffer may be an admixture of compressed and uncompressed data packets.

## Calling Convention

The decompression routine is a C-callable routine with the following prototype: Void Sigdec2 (char *ip, unsigned short  *ipL,

char *op, unsigned short *opL,

unsigned short *errorcode);

## Parameters

## Packet Format

Incoming packet at the front end can be interpreted by mapping onto the following structure.

```
Struct { CHAR   cNetId [2] SHORT iNoPackets CHAR   cPackData [512] }     BcastPackData where, cNetId[2] Identifies the machine ( CM broadcast or F&O Broadcast ) Please find different values of CNetId for difference segments Equity: - 4 Equity Derivative: - 2 Currency Derivative: - 6 iNoPackets The number of packets that are sequentially packed cPackData Buffer containing all the packets. The buffer when mapped to, by the above structure, the number of packets in the buffer can be known. The next task is to segregate the packets and process the individual packets. The packets received through the broadcast traffic have to be interpreted as follows COMPRESSION_BROADCAST_DATA { SHORT CompressionLen CHAR BroadcastData [ ]
```

```
}
```

## Note:

- The  first  two  bytes  of  the  broadcast  packet  indicate  the  length  of  the  data  after compression.
- If the compression length is zero, the data received is not compressed.
- If the length is non-zero, the data following the length should be decompressed by using the decompression routine.
- Inside the broadcast data, the first 8 bytes before the message header should be ignored. The message header starts from the 9 th  byte.

## Implementation at Front End

The lzo directory (lzo1.07) contains all the lzo source, header and library files. These files are to be included while building an application.

lzo1z_decompress is used for decompression. This is a function of the lzo library.

An API has to be developed to encompass the above LZO decompression function.

The syntax of the call should be:

lzo_decomp (char* inp_buff, unsigned int* inp_len, char* buffer_decomp, unsigned int *output_len, unsigned short *errorCode)

Where,  lzo_decomp  is  a  function  of  the  API  (to  be  developed  by  referring  to  the  examples specified in the lzo 1.07 directory) that calls the lzo function for decompression 'lzo1z_decompress'

The syntax of the lzo decompress function is as follows:

lzo1z_decompress (out, decomp_inlen, in, & decomp_outlen, NULL)

Where

## Note:

Inside the broadcast data, the first byte indicates the market type.  Ignore the rest of the 7 bytes before message header. If the first byte has the value of '4', it is Capital market and if it is '2' then it is futures and options market.

The message header starts from 9 th  byte.

## General Message Broadcast

Any general message is broadcasted in the following structure. The structure sent is:

| Structure Name | BROADCAST MESSAGE |
| --- | --- |
| Packet Length | 298 bytes |
| Transaction Code | BCAST_JRNL_VCT_MSG (6501) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| BranchNumber | SHORT |
| BrokerNumber | CHAR |
| ActionCode | CHAR |
| Reserved | CHAR |
| BROADCAST DESTINATION (Refer Table No. 28.1 for small endian & Table No. 28.2 for big endian) | STRUCT |
| BroadcastMessageLength | SHORT |
| BroadcastMessage | CHAR |

| Structure Name | BROADCAST DESTINATION |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| TraderWs | BIT |
| Reserved | CHAR |

Table 28.2 BROADCAST_DESTINATION (For Big Endian Machines)

| Structure Name | BROADCAST DESTINATION |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| TraderWs | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_JRNL_VCT_MSG (6501). |
| BranchNumber | This field contains the branch number of the trader or broker. |
| BrokerNumber | This field contains the Trading Member ID of the broker. |
| ActionCode | This field Indicates the action taken. |
| BroadcastDestination | This field contains the destination of the message, that is, Trader Workstation or Control Workstation. |
| BroadcastMessageLength | This field contains the length of the broadcast message. |
| BroadcastMessage | This field contains the broadcast message. |

## Change in System Status / Parameters

This message is sent when any global operating parameters are changed or status of markets is changed. The structure of the message is:

SYSTEM INFORMATION DATA (Refer to System Information Response in [Chapter 3](#chapter-3-logon-process))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_SYSTEM_INFORMATION_OUT (7206) No of machines received in the alphachar field is 0 not the actual no of machines. |

## Change in Security Master

This is sent whenever the parameter of any security is changed. The structure is given below.

Table 29 SECURITY UPDATE INFORMATION

| Structure Name | SECURITY UPDATE INFORMATION |
| --- | --- |
| Packet Length | 260 bytes |
| Transaction Code | BCAST_SECURITY_MSTR_CHG (18720) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| Token | LONG |
| SEC_INFO (Refer Table 4) | STRUCT |
| InstrumentType | SHORT |
| PermittedToTrade | SHORT |
| IssuedCapital | DOUBLE |
| SettlementType | SHORT |
| FreezePercent | SHORT |
| CreditRating | CHAR |
| Reserved | CHAR |
| SECURITY ELIGIBILITY PER MARKET [6] (refer table 29.1 for small endian& table 29.2 for big endian) | STRUCT |
| SurvInd | SHORT |
| IssueStartDate | LONG |
| InterestPaymentDate | LONG |
| IssueMaturityDate | LONG |
| BoardLotQuantity | LONG |
| TickSize | LONG |
| Name | CHAR |
| Reserved | CHAR |
| ListingDate | LONG |
| ExpulsionDate | LONG |
| ReAdmissionDate | LONG |
| RecordDate | LONG |
| ExpiryDate | LONG |
| NoDeliveryStartDate | LONG |
| Packet Length | 260 bytes |
| Transaction Code | BCAST_SECURITY_MSTR_CHG (18720) |
| Field Name | Data Type |
| NoDeliveryEndDate | LONG |
| ELIGIBLITY INDICATORS (refer table 29.3 for small endian& table 29.4 for big endian) | STRUCT |
| BookClosureStartDate | LONG |
| BookClosureEndDate | LONG |
| PURPOSE structures (refer table 29.5 for small endian& table 29.6 for big endian) | STRUCT |
| LocalUpdateDateTime | LONG |
| DeleteFlag | CHAR |
| Remark | CHAR |
| FaceValue | LONG |
| ISINNumber | CHAR |
| MktMakerSpread | LONG |
| MktMakerMinQty | LONG |
| CallAuction1Flag | SHORT |

| Structure Name | SECUIRITY ELIGIBILITY PER MARKET |
| --- | --- |
| Packet Length | 4 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Eligibility | BIT |
| Reserved | CHAR |
| Status | SHORT |

## Table 29.2 SECUIRITY ELIGIBILITY PER MARKET (For Big Endian Machines)

| Structure Name | SECUIRITY ELIGIBILITY PER MARKET |
| --- | --- |
| Packet Length | 4 bytes |
| Field Name | Data Type |
| Eligibility | BIT |
| Reserved | BIT |
| Reserved | CHAR |
| Status | SHORT |

## Table 29.3 ELIGIBLITY INDICATORS (For Small Endian Machines)

| Structure Name | ELIGIBLITY INDICATORS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| MinimumFill | BIT |
| AON | BIT |
| ParticipateInMarketIndex | BIT |
| Reserved | CHAR |

## Table 29.4 ELIGIBLITY INDICATORS (For Big Endian Machines)

| Structure Name | ELIGIBLITY INDICATORS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| ParticipateInMarketIndex | BIT |
| AON | BIT |
| MinimumFill | BIT |
| Reserved | BIT |
| Reserved | CHAR |

## Table 29.5 PURPOSE (For Small Endian Machines)

| Structure Name | PURPOSE |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| EGM | BIT |
| AGM | BIT |
| Interest | BIT |
| Bonus | BIT |
| Rights | BIT |
| Dividend | BIT |
| Reserved | CHAR |

## Table 29.6 PURPOSE (For Big Endian Machines)

| Structure Name | PURPOSE |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Dividend | BIT |
| Rights | BIT |
| Bonus | BIT |
| Interest | BIT |
| AGM | BIT |
| EGM | BIT |
| Reserved | BIT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_SECURITY_MSTR_CHG (18720). |
| Token | This field contains the token number of the security being updated. This is unique for a particular symbol-series combination. |
| SecurityInformation | This field contains the Symbol and Series (EQ / IL / TT) of the security. |
| InstrumentType | This field contains the instrument type of the security. It can be one of the following: '0' - Equities '1' - Preference Shares '2' - Debentures '3' - Warrants '4' - Miscellaneous |
| PermittedToTrade | This field contains one of the following values: '0' - Listed but not permitted to trade '1' - Permitted to trade '2' - BSE listed (BSE exclusive security will be available, however trading on the same will be allowed only in case of outage at BSE) |
| IssuedCapital | This field contains issue size of the security. |
| SettlementType | This field contains the settlement type. It can be one of the following: '0' - T+0 settlement '1' - T+1 settlement |
| FreezePercent | This field contains the volume freeze percent w.r.t.issued capital. This field indicates the volume freeze percentage w.r.t. issued capital. This field has to be interpreted as freeze percent /10000. Eg: 41 in this field has to be interpreted as 0.0041% |
| CreditRating | This field contains daily price range of the security. |
| Eligibility | The flag is set to '1' if the security is allowed to trade in a particular market. For Call Auction2 market (6th Market), eligibility will be set. |
| Status | This field contains one of the following values: '1' - Preopen ( Only for Normal Market ) '2' - Open '3' - Suspended |
|  | '4' - Preopen extended '6' - Price Discovery |
| SurvInd | Indicator for security in Surveillance Measure |
| IssueStartDate | This field contains the date of issue of the security. |
| InterestPaymentDate | This field contains the interest payment date of the issue. |
| IssueMaturityDate | This field contains the maturity date. |
| BoardLotQuantity | This field contains the Regular lot size. |
| TickSize | This field contains the Tick size/ Min spread size. |
| Name | This field contains the security name. |
| ListingDate | This field contains the date of listing. |
| ExpulsionDate | This field contains the date of expulsion. |
| ReAdmissionDate | This field contains the date of readmission. |
| RecordDate | This field contains the date of record changed. |
| ExpiryDate | This field contains the last date of trading before any corporate action. |
| NoDeliveryStartDate | This field contains the date from when physical delivery of share certificates is stopped for book closure. |
| NoDeliveryEndDate | This field contains the date from when physical delivery of share certificates starts after book closure. |
| MinimumFill | This flag is set if Minimum Fill attribute is allowed in orders of this security. |
| AON | This flag is set if AON attribute is allowed in orders of this security. |
| ParticipateInMarketIndex | This flag is set if this security participates in the market index. |
| BookClosureStartDate | This field contains the date when the record books in the company for shareholder names starts. |
| BookClosureEndDate | This field contains the date when the record books in the company for shareholder names ends. |
| Purpose | This field contains the EGM /AGM / Interest / Bonus / Rights / Dividend flags set depending on the corporate action. |
| LocalUpdateDateTime | This field contains the local database update date and time. |
| DeleteFlag | This field contains the status of the security, that is, whether the security is deleted or not. |
| Remark | This field contains remarks. |
| FaceValue | This field contains face value of the security. |
| ISIN Number | This field contains ISIN number of the security. |
| MktMakerSpread | This field contains spread value of the security, used by Market maker user to place two-way quotes. |
| MktMakerMinQty | This field contains the Minimum quantity for the security, Used by Market maker user for market maker order. |

## Change Participant Status

This message is sent whenever there is any participant change. The structure sent is:

| Structure Name | PARTICIPANT UPDATE INFO |
| --- | --- |
| Packet Length | 84 bytes |
| Transaction Code | BCAST_PART_MSTR_CHG (7306) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| ParticipantId | CHAR |
| ParticipantName | CHAR |
| ParticipantStatus | CHAR |
| ParticipantUpdateDateTime | LONG |
| DeleteFlag | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_PART_MSTR_CHG (7306). |
| ParticipantId | This field contains the Participant ID. |
| ParticipantName | This field contains the name of the participant that is changed. |
| ParticipantStatus | This field contains the status of the participant which is changed: |
|  | 'S' for Suspended 'A' for Active |
| ParticipantUpdateDateTime | This field contains the time when the participant information was changed. It is in number of seconds from January 1, 1980. |

## Change of Security Status

This message is sent whenever the status of any security changes. The structure sent is:

| Structure Name | SECURITY STATUS UPDATE INFORMATION |
| --- | --- |
| Packet Length | 442 bytes |
| Transaction Code | BCAST_SECURITY_STATUS_CHG (18130) OR BCAST_SECURITY_STATUS_CHG_PREOPEN (18707) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| TOKEN AND ELIGIBILITY [25] (Refer table 31.1) | STRUCT |

| Structure Name | TOKEN AND ELIGIBILITY |
| --- | --- |
| Packet Length | 16 bytes |
| Field Name | Data Type |
| Token | LONG |
| SECURITY STATUS PER MARKET[6] (Refer table 31.2) | STRUCT |

## Table 31.2 SECURITY STATUS PER MARKET

| Structure Name | SECURITY STATUS PER MARKET |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Status | Short |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is: When the status of the security changes BCAST_SECURITY_STATUS_CHG (18130). BCAST_SECURITY_STATUS_CHG_PREOPEN (18707). |
| NumberOfRecords | This field contains the number of records of the structure TOKEN AND ELIGIBILITY. |
| Token | This field contains the token number of the security which has been changed. |
| Status | This field contains the new status of the security. This can take one of the following values: '1' - Preopen '2' - Open '3' - Suspended '4' - Preopen extended '6' - Price Discovery This will include Call Auction2 Market data at the 6th position. |

## Turnover Limit Exceeded or Broker Reactivated

When a broker's turnover limit exceeds, the broker is deactivated and a message is broadcast to all workstations. The same structure is also sent when any broker is reactivated. The structure is:

| Structure Name | BROADCAST LIMIT EXCEEDED |
| --- | --- |
| Packet Length | 77 bytes |
| Transaction Code | BCAST_TURNOVER_EXCEEDED (9010) OR BROADCAST_BROKER_REACTIVATED (9011) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| BrokerCode | CHAR |
| Packet Length | 77 bytes |
| Transaction Code | BCAST_TURNOVER_EXCEEDED (9010) OR BROADCAST_BROKER_REACTIVATED (9011) |
| Field Name | Data Type |
| CounterBroker Code | CHAR |
| WarningType | SHORT |
| SEC_INFO (Refer Table 4) | STRUCT |
| TradeNumber | LONG |
| TradePrice | LONG |
| TradeVolume | LONG |
| Final | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is: BCAST_TURNOVER_EXCEEDED (9010), if the broker turnover is about to exceed or has already exceeded. BROADCAST_BROKER_REACTIVATED (9011), if the broker is reactivated after being deactivated. |
| BrokerCode | This field contains the Broker code who is about to exceed or has already exceeded his turnover limit. If the transaction code is BROADCAST_BROKER_REACTIVATED, then this broker is reactivated. |
| CounterBrokerCode | This field is not in use. |
| WarningType | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. The value is '1' if the turnover limit is about to exceed, '2' if turnover limit is exceeded. In the latter case the broker is deactivated. |
| Symbol | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This contains the symbol of the security in which the broker has last traded. |
| Series | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This contains the series of the security. |
| TradeNumber | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This is the trade number in which the broker has last traded |
| TradePrice | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This contains the price of the trade. |
| TradeVolume | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This contains the trade quantity of the trade. |
| Final | This field is applicable only if the transaction code is BCAST_TURNOVER_EXCEEDED. This indicates whether it is the final auction trade. |

## Auction Activity Message

This structure is sent whenever there is any auction related activity. This includes any change in Auction MBO. The structure is:

| Structure Name | MS_AUCTION_INQ_DATA |
| --- | --- |
| Packet Length | 76 bytes |
| Transaction Code | BCAST_AUCTION_INQUIRY_OUT (18700). |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| ST_AUCTION_INQ_INFO (Refer Table 33.1) | STRUCT |

Table 33.1   Auction Activity Message

| Structure Name | ST_AUCTION_INQ_INFO |
| --- | --- |
| Packet Length | 36 bytes |
| Field Name | Data Type |
| Token | LONG |
| AuctionNumber | SHORT |
| AuctionStatus | SHORT |
| InitiatorType | SHORT |
| TotalBuyQty | LONG |
| BestBuyPrice | LONG |
| TotalSellQty | LONG |
| BestSellPrice | LONG |
| AuctionPrice | LONG |
| AuctionQty | LONG |
| SettlementPeriod | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_AUCTION_INQUIRY_OUT (18700). |
| Token | This field contains the token number of the security in which the auction is started. |
| AuctionNumber | This field contains the number of the auction. |
| AuctionStatus | Refer to Auction Status in Appendix. |
| InitiatorType | This field specifies whether auction is initiated by trader or control. This field is set to control since only Exchange initiated auctions are permitted now. |
| TotalBuyQty | This field contains the total Buy Quantity for the auction. |
| BestBuyPrice | This field contains the best Buy price. This is the highest price for a Buy auction. |
| TotalSellQty | This field contains the total Sell quantity for the auction. |
| BestSellPrice | This field contains the best Sell price. This is the lowest price for a Sell auction. |
| AuctionPrice | This field contains the price at which auction trade has taken place. |
| AuctionQty | This field contains the quantity of securities that have been auctioned. |
| SettlementPeriod | This field contains the period by which settlement between the parties should take place. This value is defaulted by the Exchange and cannot be modified by the user. |

## Change of Auction Status

When the status of an auction changes (from pending to active or, competitor period or solicitor period  is  ended  or  started)  a  message  is  broadcast  to  all  workstations  with  the  following structure and transaction codes:

| Structure Name | AUCTION STATUS CHANGE |
| --- | --- |
| Packet Length | 302 bytes |
| Transaction Code | BC_AUCTION_STATUS_CHANGE (6581) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| SEC_INFO | STRUCT |
| AuctionNumber | SHORT |
| AuctionStatus | CHAR |
| ActionCode | CHAR |
| BROADCAST_DESTINATION (Refer Table 34.1 for small endian& Table 34.2 for big endian) | STRUCT |
| BroadcastMessageLength | SHORT |
| BroadcastMessage | CHAR |

| Structure Name | BROADCAST DESTINATION |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| TraderWs | BIT |
| Reserved | CHAR |

Table 34.2    BROADCAST_DESTINATION (For Big Endian Machines)

| Structure Name | BROADCAST DESTINATION |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| TraderWs | BIT |
| Reserved | BIT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BC_AUCTION_STATUS_CHANGE (6581). |
| Symbol | This field contains the symbol of the security. |
| Series | This field contains the series of the security. |
| AuctionNumber | This field contains the auction number. |
| AuctionStatus | This field contains the status of the auction. Refer to Auction Status in Appendix. |
| ActionCode | This field contains the action code to indicate the action taken. |
| BroadcastDestination | This field contains the destination of the message. |
| BroadcastMessageLength | This field contains the length of the broadcast message. |
| BroadcastMessage | This field contains the contents of the broadcast message. |

## Change of Market Status

Whenever the status of the market changes, the following structure is sent:

Table 35    Change of Market Status

| Structure Name | BCAST_VCT_MESSAGES |
| --- | --- |
| Packet Length | 298 bytes |
| Transaction Code | BC_OPEN_MESSAGE (6511) OR BC_CLOSE_MESSAGE (6521) OR BC_PREOPEN_SHUTDOWN_MSG (6531) OR BC_NORMAL_MKT_PREOPEN_ENDED (6571) OR BC_CLOSING_START(6583) OR BC_CLOSING_END(6584) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| SEC_INFO(Refer Table 4) | STRUCT |
| MarketType | SHORT |
| BROADCAST_DESTINATION (Refer Table 34.1 for small endian & Table 34.2 for big endian) | STRUCT |
| BroadcastMessageLength | SHORT |
| BroadcastMessage | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction codes are as follows: BC_OPEN_MESSAGE (6511). This is sent when the market is opened. BC_CLOSE_MESSAGE (6521). This is sent when the market is closed. BC_PREOPEN_SHUTDOWN_MSG (6531). This is sent when the market is preopened. BC_NORMAL_MKT_PREOPEN_ENDED (6571). This is sent when the preopen period ends. |
|  | BC_CLOSING_START (6583). This is sent when closing session is opened. BC_CLOSING_END (6584). This is sent when closing session is closed. |
| SecurityInformation | This field contains the symbol and series of a security. |
| MarketType | This field indicates the type of market. It contains one of the following values: '1' - Normal '2' - Odd Lot '3' - Spot '4' - Auction '5' - Call auction1 '6' - Call auction2 |
| BroadcastDestination | This field is set to '1' if it signifies that the message is for the Trader Workstation. |
| BroadcastMessageLength | This field contains the length of the broadcast message. |
| BroadcastMessage | This field contains the contents of the broadcast message. |

## Security Level Trading/Market Status Change Message

Security level trading/market status change messages are sent separately in following structure and transcode.

SECURITY LEVEL TRADING STATUS CHANGE

| Structure Name | BCAST_SYMBOL_STATUS_CHANGE _ACTION |
| --- | --- |
| Packet Length | 58 bytes |
| Transaction Code | BC_SYMBOL_STATUS_CHANGE_ACTION (7764) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 2) | STRUCT |
| SEC_INFO(Refer Table 3) | STRUCT |
| MarketType | SHORT |
| Reserved | SHORT |
| ActionCode | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BC_SYMBOL_STATUS_CHANGE_ACTION (7764) |
| SecurityInformation | This field contains the symbol and series of a security. |
| MarketType | This field indicates the type of market. It contains one of the following values: '1' - Normal '2' - Odd Lot '3' - Spot '4' - Auction '5' - Call auction1 '6' - Call auction2. |
| ActionCode | It contains of the following values: 6531(BC_PREOPEN_SHUTDOWN_MSG) - This action code is set when the security is preopened. 6571(BC_NORMAL_MKT_PREOPEN_ENDED) - This action code is set when the security's preopen period ends. 6511(BC_OPEN_MESSAGE) - This action code is set when the security is opened. 6521(BC_CLOSE_MESSAGE) - This action code is set when the security is closed. 6583(BC_CLOSING_START) - This action code is set when the security's closing session is opened. 6584( BC_CLOSING_END) - This action code is set when the security's closing session is closed |

## Ticker and Market Index

Ticker and market index information is sent in the following structure:

| Structure Name | TICKER TRADE DATA |
| --- | --- |
| Packet Length | 546 bytes |
| Transaction Code | BCAST_TICKER_AND_MKT_INDEX |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| TICKER INDEX INFORMATION [28] (Refer to TABLE 36.1) | STRUCT |

| Structure Name | TICKER INDEX INFORMATION |
| --- | --- |
| Packet Length | 18 bytes |
| Field Name | Data Type |
| Token | LONG |
| MarketType | SHORT |
| FillPrice | LONG |
| FillVolume | LONG |
| MarketIndexValue | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code sent is BCAST_TICKER_AND_MKT_INDEX (18703). |
| NumberOfRecords | This field indicates the number of times (Maximum 28) the structure TICKER INDEX INFORMATION is repeated. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| MarketType | This field contains the market type. |
| FillPrice | This field contains the price at which the order has been traded. |

| FillVolume | This field contains the quantity of security traded. |
| --- | --- |
| MarketIndexValue | This field contains the value of the market index. |

## Market by Order / Market by Price Update

The information regarding the best buy orders and the best sell orders is given in the following format:

| Structure Name | BROADCASTMBOMBP |
| --- | --- |
| Packet Length | 482 bytes |
| Transaction Code | BCAST_MBO_MBP_UPDATE (7200) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| INTERACTIVEMBODATA (Refer Table 37.1) | STRUCT |
| MBPBuffer [size of (MBP INFORMATION) * 10] (Refer MBP_INFORMATION in Table 37.7)) | CHAR |
| BbTotalBuyFlag | SHORT |
| BbTotalSellFlag | SHORT |
| TotalBuyQuantity | LONG LONG |
| TotalSellQuantity | LONG LONG |
| MBOMBPINDICATOR (Refer Table 37.2 for Small Endian& Table 37.3 for Big Endian) | STRUCT |
| ClosingPrice | LONG |
| OpenPrice | LONG |
| HighPrice | LONG |
| LowPrice | LONG |
| Reserved | CHAR |

Table 37.1 INTERACTIVE MBO DATA

| Structure Name | INTERACTIVEMBODATA |
| --- | --- |
| Packet Length | 240 bytes |
| Field Name | Data Type |
| Token | LONG |
| BookType | SHORT |
| TradingStatus | SHORT |
| VolumeTradedToday | LONG LONG |
| LastTradedPrice | LONG |
| NetChangeIndicator | CHAR |
| Filler | CHAR |
| NetPriceChangeFromClosingPrice | LONG |
| LastTradeQuantity | LONG |
| LastTradeTime | LONG |
| AverageTradePrice | LONG |
| AuctionNumber | SHORT |
| AuctionStatus | SHORT |
| InitiatorType | SHORT |
| InitiatorPrice | LONG |
| InitiatorQuantity | LONG |
| AuctionPrice | LONG |
| AuctionQuantity | LONG |
| MBOBuffer [size of (MBO INFORMATION) * 10] (Refer MBO_INFORMATION in Table 37.4) | STRUCT |

Table 37.2 MBO MBP INDICATOR (For Small Endian Machines)

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Sell | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Buy | BIT |
| LastTradeLess | BIT |
| LastTradeMore | BIT |
| Reserved | CHAR |

Table 37.3 MBO MBP INDICATOR (For Big Endian Machines)

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeMore | BIT |
| LastTradeLess | BIT |
| Buy | BIT |
| Sell | BIT |
| Reserved | BIT |
| Reserved | CHAR |

| Structure Name | MBOINFORMATION |
| --- | --- |
| Packet Length | 18 bytes |
| Field Name | Data Type |
| TraderId | LONG |
| Qty | LONG |
| Price | LONG |
| ST MBOMBPTERMS (Refer Table 37.5 for small endian & Table 37.6 for big endian) | STRUCT |
| MinFillQty | LONG |

| Structure Name | ST MBOMBPTERMS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved1 | BIT |
| Aon | BIT |
| Mf | BIT |
| Reserved2 | BIT |

Table 37.6   ST MBO MBP TERMS (For Big Endian Machines)

| Structure Name | ST MBOMBPTERMS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Mf | BIT |
| Aon | BIT |
| Reserved1 | BIT |
| Reserved2 | BIT |

Table 37.7   MBP INFORMATION

| Structure Name | MBP INFORMATION |
| --- | --- |
| Packet Length | 16 bytes |
| Field Name | Data Type |
| Quantity | LONG LONG |
| Price | LONG |
| NumberOfOrders | SHORT |
| BbBuySellFlag | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_MBO_MBP_UPDATE (7200). |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| BookType | This field contains the book type - RL / ST / SL / OL / SP / AU |
| TradingStatus | This field contains the trading status of the security: '1' - Preopen '2' - Open '3' - Suspended '4' - Preopen Extended '6' - Price Discovery |
| VolumeTradedToday | This field contains the total quantity of a security traded on the current day. |
| LastTradedPrice | This field contains the price at which the latest trade in a security has taken place. |
| NetChangeIndicator | This field is a flag which indicates any change of the order price from the LTP. '+' for increase ' - ' for decrease |
| NetPriceChange | This field contains the net change between the order price and the LTP. |
| LastTradeQuantity | This field contains the quantity at which the last trade took place in a security. |
| LastTradeTime | This field contains the time when the last trade took place in a security. |
| AverageTradePrice | This field contains the average price of all the trades in a security. |
| AuctionNumber | This field contains the auction number. The maximum value this can take is 9999. In other cases, it is set to zero. |
| AuctionStatus | Refer to Auction Status in Appendix. |
| InitiatorType | This field contains the initiator type - control or trader. Presently initiator type is control, since only the Exchange can initiate an auction. Otherwise it is blank. |
| InitiatorPrice | This field contains the price of the security of the initiator's auction order. Otherwise it is set to zero. |
| InitiatorQuantity | This field contains the quantity of the security of the initiator's auction order. Otherwise it is set to zero. |
| AuctionPrice | This field contains the price at which auction in a security takes place. Otherwise it is set to zero. |
| AuctionQuantity | This field contains the quantity at which auction in a security takes place. Otherwise it is set to zero. |
| RecordBuffer (MBO INFORMATION ) | This field contains five best Buy orders and five best Sell orders from the order book. First five contains Buy orders and next five contains Sell orders. |
| RecordBuffer (MBP INFORMATION ) | This field contains five best Buy prices and five best Sell prices from the order book .First five are for Buy and next five for Sell. |
| BbTotalBuyFlag | This field contains value '1' if there is a buyback order in the buy side else its value is zero. This is useful if the buyback order is not amongst the top five. |
| BbTotalSellFlag | Currently, its value is set to zero. |
| TotalBuyQuantity | This field contains the total quantity of buy orders in a security. |
| TotalSellQuantity | This field contains the total quantity of sell orders in a security. |
| Indicator | This structure contains flags which can be set to indicate Buy, Sell and latest trade less than or greater than the immediately previous LTP. |
| ClosingPrice | This field contains the closing price of a security. |
| OpenPrice | This field contains the open price of a security. |
| HighPrice | This field contains the highest trade price. |
| LowPrice | This field contains the lowest trade price. |
| MBOInformation | This field contains the quantity and price for a maximum of five best prices. |
| MBPInformation | This field contains the quantity, price and number of orders for a maximum of five best prices. |

## Only Market by Price Update

The information regarding the best buy orders and the best sell orders is given in the following format:

| Structure Name | BROADCAST ONLY MBP |
| --- | --- |
| Packet Length | 566 bytes |
| Transaction Code | BCAST_ONLY_MBP (7208) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NoOfRecords | SHORT |
| INTERACTIVE ONLY MBP DATA [2] (Refer Table 38.1) | STRUCT |

| Structure Name | INTERACTIVE ONLY MBP DATA |
| --- | --- |
| Packet Length | 262 bytes |
| Field Name | Data Type |
| Token | LONG |
| BookType | SHORT |
| TradingStatus | SHORT |
| VolumeTradedToday | LONG LONG |
| LastTradedPrice | LONG |
| NetChangeIndicator | CHAR |
| Filler | CHAR |
| NetPriceChangeFromClosingPrice | LONG |
| LastTradeQuantity | LONG |
| LastTradeTime | LONG |
| AverageTradePrice | LONG |
| AuctionNumber | SHORT |
| AuctionStatus | SHORT |
| InitiatorType | SHORT |
| InitiatorPrice | LONG |
| Packet Length | 262 bytes |
| Field Name | Data Type |
| InitiatorQuantity | LONG |
| AuctionPrice | LONG |
| AuctionQuantity | LONG |
| RecordBuffer [size of (MBP INFORMATION) * 10] (Refer Table 38.4) | CHAR |
| BbTotalBuyFlag | SHORT |
| BbTotalSellFlag | SHORT |
| TotalBuyQuantity | LONG LONG |
| TotalSellQuantity | LONG LONG |
| MBP INDICATOR (Refer Table 38.2 for Small Endian & Refer Table 38.3 Big Endian) | STRUCT |
| ClosingPrice | LONG |
| OpenPrice | LONG |
| HighPrice | LONG |
| LowPrice | LONG |
| IndicativeClosePrice | LONG |

## Table 38.2 MBP INDICATOR (For Small Endian Machines)

| Structure Name | MBP INDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved [4] | BIT |
| Sell | BIT |
| Buy | BIT |
| LastTradeLess | BIT |
| LastTradeMore | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | CHAR |

Table 38.3 MBP INDICATOR (For Big Endian Machines)

| Structure Name | MBP INDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeMore | BIT |
| LastTradeLess | BIT |
| Buy | BIT |
| Sell | BIT |
| Reserved | BIT |
| Reserved | CHAR |

## Table 38.4 MBP INFORMATION

| Structure Name | MBP INFORMATION |
| --- | --- |
| Packet Length | 16 bytes |
| Field Name | Data Type |
| Quantity | LONG LONG |
| Price | LONG |
| NumberOfOrders | SHORT |
| BbBuySellFlag | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code set for the purpose is BCAST_ONLY_MBP (7208). |
| NoOfRecords | This field contains the number of securities sent. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| BookType | This field contains the book type - RL / ST / SL / SP / AU |
| TradingStatus | This field specifies trading status of the security. It contains one of the following values. '1' - Preopen '2' - Open '3' - Suspended '4' - Preopen Extended '6' - Price Discovery Trading Status for a Security will be '6' during pre -open session. It will be '2' when Normal Market opens. |
| VolumeTradedToday | This field contains the total quantity of a security traded on the current day. During Preopen this field will contain Indicative Equilibrium Quantity. Once matching starts it contains total quantity traded for that security. If field value exceeds unsigned long max value (i.e. 4294967295), the value of the field will be wrapped up, i.e. start from 0. If field is read as LONG (signed LONG) and if field value exceeds signed long max value (i.e. 214748364), then the value will be negative. |
| LastTradedPrice | This field contains the price at which the latest trade in a security has taken place. During 1st preopen, LTP field will display Previous day's value in MBP screen. For next preopen sessions it will show the last traded price of security that was last updated during the market status open or Pre-Open. Once matching starts it contains the LTP of the security. |
| NetChangeIndicator | This field is a flag which indicates any change of the order price from the LTP. '+' for increase ' - ' for decrease. |
| NetPriceChange | from previous day's close price. This field contains the net change between the order price and the LTP. During Preopen it will contain net %change between previous day's close price and the indicative open price. Once matching starts it will contain net %change between previous day's close price and trade price. |
| LastTradeQuantity | This field contains the quantity at which the last trade took place in a security. During preopen, for securities which are in Price Discovery, LTQ field will display as previous day's value. Once matching starts this field contains the quantity at which the last trade took place in a security |
| LastTradeTime | This field contains the time when the last trade took place in a security. During preopen, for securities which are in Price Discovery, LTT field will display as previous day's value. Once matching starts it contains the Last Trade Time. |
| AverageTradePrice | This field contains the average price of all the trades in a security. During 1st Preopen session it will always be zero. For next preopen sessions, it will have the average traded price that was last updated during the market status open or Pre- Open. Once matching starts it will contain the Average Trade Price. |
| AuctionNumber | This field contains the auction number. The maximum value this can take is 9999. Otherwise it is set to zero. During Preopen it will always be zero. |
| AuctionStatus | Refer to Auction Status in Appendix. |
|  | During Preopen it will always be zero. |
| InitiatorType | This field contains the initiator type - control or trader. Presently initiator type is control, since only the Exchange can initiate an auction. Otherwise it is set to blank. During Preopen it will always be blank. |
| InitiatorPrice | This field contains the price of the security of the initiator's auction order. Otherwise it is set to zero. During Preopen it will always be zero. |
| InitiatorQuantity | This field contains the quantity of the security of the initiator's auction order. Otherwise it is set to zero. During Preopen it will always be zero. |
| AuctionPrice | This field contains the price at which auction in a security takes place. Otherwise it is set to zero. During Preopen it will always be zero. |
| AuctionQuantity | This field contains the quantity at which auction in a security takes place. Otherwise it is zero. During Preopen it will always be zero. |
| Record Buffer (MBP INFORMATION ) | This field contains five best Buy prices and five best Sell prices from the order book. First five are for buy and next five for sell. During Preopen order collection period (till pre-open end), in this structure the first four rows for Buy and Sell contains the four Limit orders and the last row of both sides is reserved for ATO orders. During Preopen order collection period (till pre-open end), if ATO order exists then in Price field -1 will be sent in the last row of both sides. |
| BbTotalbuyFlag | The field contains the values to represent buy back orders, market maker order or both.The values will be as below. '0' Non Market Maker and Non Buy back orders '1' Buy back orders '2' Market Maker Orders '3' Market Maker and Buy Back Order This is useful if the buyback order is not amongst the top five. |

| Field Name | Brief Description |
| --- | --- |
| BbTotalsellFlag | The field contains the values to represent buy back orders; market maker order or both.The values will be as below. '0' Non Market Maker and Non Buy back orders '1' Buy back orders '2' Market Maker Orders '3' Market Maker and Buy Back Order This is useful if the buyback order is not amongst the top five. The values in this field will be according to the flag value table given below. |
| TotalBuyQuantity | This field contains the total quantity of buy orders in a security. |
| TotalSellQuantity | This field contains the total quantity of sell orders in a security. |
| Indicator | This field contains flags which can be set to indicate Buy, Sell and Latest trade less than or greater than the immediately previous LTP. LastTradeMore During Preopen session: Indicate change from the Last received Indicative Open Price. If received open price is more than the last received open price, then it will be set to 1, else it will be 0. During Matching: Indicate change from the Last received Trade Price. If received open price is more than the last received trade price, then it will be set to 1, else it will be 0. Vice versa for LastTradeLess Buy / SELL: This BIT will be set to 0 |
| ClosingPrice | This field contains the closing price of a security. |
| OpenPrice | This field contains the open price of a security. This field contains the Indicative opening price of a security for that Preopen session and Final Open Price of a security for Matching Phase. |
| HighPrice | This field contains the highest trade price. During 1st Preopen session it will always be zero. For next preopen sessions, it will have the high price that was last updated during the market status open or Pre-Open. Once matching starts it will be updated. |
| LowPrice | This field contains the lowest trade price. |
| MBPInformation | This structure contains the quantity, price and number of orders for a maximum of five best prices. This field contains the quantity, price and number of orders for max of 5 orders out of which first four orders are best limit and the last ATO order. If there are less than 4 limit orders, ATO order will still be at the 5th place During Preopen order collection period (till pre-open end),if ATO order exists then in Price field -1 will be sent in the last row of both sides. |
| Quantity | This field contains the quantity at the price point. If field value exceeds unsigned long max value (i.e. 4294967295), the value of the field will be wrapped up, i.e. start from 0. If field is read as LONG (signed LONG) and if field value exceeds signed long max value (i.e. 214748364), then the value will be negative. |
| Price | The price point in the MBP array. |
| NumberOfOrders | The number of orders at the price point. |
| BbBuySellFlag | This field contains the values to indicate whether there is a buyback order or market maker order in the buy or sell side at the price point. The values in this field will be according to the flag value table. |

## Market Watch Update

The market watch information gives the best buy order and its quantity, best sell order and its quantity and the last trade price. The structure sent for the purpose is:

| Structure Name | BROADCAST INQUIRY RESPONSE |
| --- | --- |
| Packet Length | 466 bytes |
| Transaction Code | BCAST_MW_ROUND_ROBIN (7201) |
| Field Name | Data Type |
| BCAST_HEADER (Refer table 3) | STRUCT |
| NumberOfRecords | SHORT |
| MARKETWATCHBROADCAST [4] (Refer table 39.1) | STRUCT |

| Structure Name | MARKETWATCHBROADCAST |
| --- | --- |
| Packet Length | 106 bytes |
| Field Name | Data Type |
| Token | LONG |
| MARKET WISE INFORMATION [3] (Refer Table 39.2 ) | STRUCT |

Table 39.2 MARKET WISE INFORMATION

| Structure Name | MARKET WISE INFORMATION |
| --- | --- |
| Packet Length | 34 bytes |
| Field Name | Data Type |
| MBOMBPINDICATOR (Refer table 39.3 for small endian & table 39.4 for big endian) | STRUCT |
| BuyVolume | LONG LONG |
| Packet Length | 34 bytes |
| Field Name | Data Type |
| BuyPrice | LONG |
| SellVolume | LONG LONG |
| SellPrice | LONG |
| LastTradePrice | LONG |
| LastTradeTime | LONG |

## Table 39.3 MBO MBP INDICATOR (For Small Endian Machines)

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Sell | BIT |
| Buy | BIT |
| LastTradeLess | BIT |
| LastTradeMore | BIT |
| Reserved | CHAR |

## Table 39.4 MBO MBP INDICATOR (For Big Endian Machines)

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeMore | BIT |
| LastTradeLess | BIT |
| Buy | BIT |
| Sell | BIT |
| Reserved | BIT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code set for the purpose is BCAST_ONLY_MBP (7201). |
| NumberOfRecords | This field contains the number of times the structure MARKET WATCH BROADCAST is repeated. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| Indicator | This structure contains the flags which can be set to indicate Buy, Sell and Last trade less than or greater than previous LTP. |
| BuyVolume | This field contains the quantity of the best Buy order. |
| BuyPrice | This field contains the price of the best Buy order. |
| SellVolume | This field contains the quantity of the best Sell order. |
| SellPrice | This field contains the price of the best Sell order. |
| LastTradePrice | This field contains the latest trade price of a security. During preopen it contains the indicative open price of that security. |
| LastTradeTime | This field contains the latest trade time of a security. |

## CALL AUCTION MBP Broadcast

During Call Auction2 pre-open session, market data will b BROADCAST CALL AUCTION MBP e sent based on the order activity during the order collection period. Indicative opening price will be computed based on the order activity. When Call Auction2 pre-open session ends, order activity will be stopped and the final open price will be computed for all Call-Auction2 securities. Final open price will be available in the market data.

After computation of final open price, orders will be matched based on the final open price.

Trades related data will be available in market data once the matching is started.

Once the FOP is calculated and matching is over for a token, the MBP data for that token will be received in the existing MBP broadcast packet (7208).

The transaction code to disseminate the Call Auction2 market data during Preopen session is BCAST_CALL AUCTION_MBP (7214).

The structure on the transcode is as show below:

| Structure Name | BROADCAST CALL AUCTIONMBP |
| --- | --- |
| Transaction Code | BCAST_CALL AUCTION_MBP (7214) |
| Packet Length | 538 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NoOfRecords | SHORT |
| INTERACTIVE CALL AUCTION MBP DATA [2] (Refer Table 40.1) | STRUCT |

| Structure Name | INTERACTIVE CALL AUCTION MBP DATA |
| --- | --- |
| Packet Length | 248 bytes |
| Field Name | Data Type |
| Token | LONG |
| BookType | SHORT |
| TradingStatus | SHORT |
| VolumeTradedToday | LONG LONG |
| IndicativeTradedQty | LONG LONG |
| LastTradedPrice | LONG |
| NetChangeIndicator | CHAR |
| Filler | CHAR |
| NetPriceChangeFromClosingPrice | LONG |
| LastTradeQuantity | LONG |
| LastTradeTime | LONG |
| AverageTradePrice | LONG |
| FirstOpenPrice | LONG |
| RecordBuffer [size of (MBP INFORMATION) * 10] (Refer Table 40.4 ) | CHAR |
| BbTotalBuyFlag | SHORT |
| BbTotalSellFlag | SHORT |
| TotalBuyQuantity | LONG LONG |
| Packet Length | 248 bytes |
| Field Name | Data Type |
| TotalSellQuantity | LONG LONG |
| MBP INDICATOR (Refer Table 40.2 for small endian & Table 40.3 for Big endian) | STRUCT |
| ClosingPrice | LONG |
| OpenPrice | LONG |
| HighPrice | LONG |
| LowPrice | LONG |

## For Small Endian Machines:

| Structure Name | MBP INDICATOR |
| --- | --- |
| Packet Length | 2 Bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Sell | BIT |
| Buy | BIT |
| LastTradeLess | BIT |
| LastTradeMore | BIT |
| Reserved | CHAR |

## For Big Endian Machines:

| Structure Name | MBP INDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeMore | BIT |
| LastTradeLess | BIT |
| Buy | BIT |
| Sell | BIT |
| Reserved | BIT |
| Reserved | CHAR |

Table 40.4 MBP INFORMATION

| Structure Name | MBP INFORMATION |
| --- | --- |
| Packet Length | 16 bytes |
| Field Name | Data Type |
| Quantity | LONG LONG |
| Price | LONG |
| NumberOfOrders | SHORT |
| BbBuySellFlag | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code set for the purpose is BCAST_CALL AUCTION_MBP (7214). |
| NoOfRecords | This field contains the number of securities sent. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| BookType | This field contains the book type - RL / ST / SL / SP / AU / CA/ CB For CALL AUCTION1 session book type will be CA(11) For CALL AUCTION2 session book type will be CB(12) |
| TradingStatus | This field specifies trading status of the security. It contains one of the following values. '1' - Preopen '2' - Open '3' - Suspended '4' - Preopen Extended '6' - Price Discovery Trading Status for a Security will be '6' during pre -open session and opening session |
| VolumeTradedToday | This field contains the total quantity of a security traded on the current day. During Preopen this field will contain Indicative Equilibrium Quantity. Once matching starts it contains total quantity traded for that security. |
| LastTradedPrice | This field contains the price at which the latest trade in a security has taken place. |
|  | During Preopen as well as During matching, it contains LTP of the security. |
| NetChangeIndicator | This field is a flag which indicates any change of the IOP or LTP from previous day's close price. '+' for increase ' - ' for decrease. During Preopen it will indicate any change in Indicative Open Price from previous day's close price. Once matching starts it will indicate the change in trade price from previous day's close price. |
| NetPriceChange | This field contains the net change between the IOP or LTP from previous day's close price. During Preopen it will contain net %change between previous day's close price and the indicative open price. Once matching starts it will contain net %change between previous day's close price and trade price. |
| LastTradeQuantity | This field contains the quantity at which the last trade took place in a security. During Preopen as well as During matching, it contains the quantity at which the last trade took place in a security. |
| LastTradeTime | This field contains the time when the last trade took place in a security. During Preopen as well as During matching, it contains the Last Trade Time. |
| AverageTradePrice | This field contains the average price of all the trades in a security. During 1st Preopen session it will always be zero. For next preopen sessions, it will have the average traded price that was last updated during the market status opening. Once matching starts it will contain the Average Trade Price. |
| FirstOpenPrice | This field contains the First trade open price for call auction security. During first call auction- order collection period, this field will be zero. Once matching starts it will contain the First Trade Price. Once updated, for all subsequent call auctions, it will not change. |
|  | This field may remain zero till the first trade happens. |
| Record Buffer (MBP INFORMATION ) | This field contains five best Buy prices and five best Sell prices from the order book. First five are for buy and next five for sell. During Preopen order collection period (till pre-open end), in this structure the first five rows for Buy and Sell contains the five Limit orders. |
| BbTotalbuyFlag | This field contains the values to indicate whether there is a buyback order or market maker order in the buy side .This is useful if the buyback order or market maker order is not amongst the top five. During Preopen and matching, value will always be zero. |
| BbTotalsellFlag | This field contains the values to indicate whether there is a buyback order or market maker order in the sell side .This is useful if the buyback order or market maker order is not amongst the top five. During Preopen and matching, value will always be zero. |
| TotalBuyQuantity | This field contains the total quantity of buy orders in a security. |
| TotalSellQuantity | This field contains the total quantity of sell orders in a security. |
| Indicator | This field contains flags which can be set to indicate Buy, Sell and Latest trade less than or greater than the immediately previous LTP. LastTradeMore During Preopen session: Indicate change from the Last received Indicative Open Price. If received open price is more than the last received open price, then it will be set to 1, else it will be 0. During Matching: Indicate change from the Last received Trade Price. If received open price is more than the last received trade price, then it will be set to 1, else it will be 0. Vice versa for LastTradeLess Buy / SELL This BIT will be set to 0 |
| ClosingPrice | This field contains the closing price of a security. |
| OpenPrice | This field contains the open price of a security. This field contains the Indicative opening price of a security for that Preopen session and Final Open Price of a security for Matching Phase. |
|  | When normal market opens, Final open price will be available in this field. |
| ClosingPrice | This field contains the closing price of a security. |
| OpenPrice | This field contains the Indicative opening price of a security for that Preopen session and Final Open Price of a security for Matching Phase. When normal market opens, Final open price will be available in this field. |
| HighPrice | This field contains the highest trade price. During 1st Preopen session it will always be zero. For next preopen sessions, it will have the high price that was last updated during the market status opening. Once matching starts it will be updated. |
| LowPrice | This field contains the lowest trade price. During 1st Preopen session it will always be zero. For next preopen sessions, it will have the low price that was last updated during the market status opening. Once matching starts it will be updated. |
| MBPInformation | This field contains the quantity, price and number of orders for a maximum of five best prices. For CALL AUCTION1 This field contains the quantity, price and number of orders for max of 5 orders out of which first four orders are best limit and the last ATO order. If there are less than 4 limit orders, ATO order will still be at the 5th place During Preopen order collection period (till pre-open end), if ATO order exists then in Price field -1 will be sent in the last row of both sides. For CALL AUCTION2 This field contains the quantity, price and number of orders for max of 5 best Limit orders. |
| Quantity | This field contains the quantity at the price point. |
| Price | The price point in the MBP array. |
| NumberOfOrders | The number of orders at the price point. |

| Field Name | Brief Description |
| --- | --- |
| BbBuySellFlag | This field contains the values to indicate whether there is a buyback order or market maker order in the buy or sell side at the price point. During Preopen and matching, value will always be zero. |

This transcode will be sent only for the securities which are eligible to take part in CALL AUCTION 2 sessions.

## Flag Value Table

The values of buyback flags in MBP array and total order buyback values in both buy and sell sides will be according to the following table:

| Buy_back order | Market maker order | bb_buy_flag/ bb_sell_flag/ bb_total_buy_flag/ bb_total_sell_flag |
| --- | --- | --- |
| NO | NO | 0 |
| YES | NO | 1 |
| NO | YES | 2 |
| YES | YES | 3 |

## Market Watch Update

The market watch information gives the best buy order and its quantity, best sell order and its quantity and the last trade price. The market watch data for Call Auction market is sent through new transcode (7215). The structure sent for the purpose is:

| Structure Name | BROADCAST CALL AUCTION MARKET WATCH |
| --- | --- |
| Transaction Code | BCAST_CA_MW (7215) |
| Packet Length | 482 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NoOfRecords | SHORT |
| MARKETWATCHBROADCAST[11] (Refer Table 41.1) | STRUCT |

Table 41.1 MARKETWATCHBROADCAST

| Structure Name | MARKETWATCHBROADCAST |
| --- | --- |
| Packet Length | 40 Bytes |
| Field Name | Data Type |
| Token | LONG |
| Mkt Type | SHORT |
| MBOMBPINDICATOR (Refer Table 37.2 for small endian and Table 37.3 for big endian) | STRUCT |
| BuyVolume | LONG LONG |
| BuyPrice | LONG |
| SellVolume | LONG LONG |
| SellPrice | LONG |
| LastTradePrice | LONG |
| LastTradeTime | LONG |

## For Small Endian Machines:

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 Bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Sell | BIT |
| Buy | BIT |
| LastTradeLess | BIT |
| LastTradeMore | BIT |
| Reserved | CHAR |

## For Big Endian Machines:

| Structure Name | MBOMBPINDICATOR |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeMore | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| LastTradeLess | BIT |
| Buy | BIT |
| Sell | BIT |
| Reserved | BIT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code sent is BCAST_CA_MW (7215). |
| NumberOfRecords | This field contains the number of times the structure MARKET WATCHBROADCAST is repeated. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| Mkt Type | This field contains the market type For CALL AUCTION1, market type 5 will be received For CALL AUCTION2, market type 6 will be received |
| Indicator | This structure contains the flags which can be set to indicate Buy, Sell and Last trade less than or greater than previous LTP. |
| BuyVolume | This field contains the quantity of the best Buy order. |
| BuyPrice | This field contains the price of the best Buy order. |
| SellVolume | This field contains the quantity of the best Sell order. |
| SellPrice | This field contains the price of the best Sell order. |
| LastTradePrice | This field contains the latest trade price of a security. |
| LastTradeTime | This field contains the latest trade time of a security. |

## Security Open Message

> [!note]
> The Following transcode SECURITY_OPEN_PRICE 6013) will not be sent by exchange.

When the market opens the open price of the security is sent in the following structure:

Table 42 MS_SEC_OPEN_MSGS

| Structure Name | MS_SEC_OPEN_MSGS |
| --- | --- |
| Transaction Code | SECURITY_OPEN_PRICE (6013) |
| Packet Length | 58 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| SEC_INFO (Refer Table 4) | STRUCT |
| Token | SHORT |
| OpeningPrice | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code sent is SECURITY_OPEN_PRICE (6013). |
| SEC_INFO | This structure contains the symbol and series for a particular security. |
| Token | This field contains a unique number that is given to a particular symbol- series combination. |
| OpeningPrice | This field contains open price of the security. |

## Broadcast Circuit Check

If there has been no data on the broadcast circuit for a stipulated time period, then a pulse is sent. This time is nine seconds now but it can be changed by NSE -Control. This is only to intimate that the circuit is still there but there is no data to send. The structure sent is:

BCAST_HEADER ( Refer to Broadcast Header in chapter 2 )

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code sent is BC_CIRCUIT_CHECK (6541). |

## Multiple Index Broadcast

The multiple index broadcast structure is as follows:

Table 43 BROADCAST INDICES

| Structure Name | BROADCAST INDICES |
| --- | --- |
| Transaction Code | BCAST_INDICES (7207) |
| Packet Length | 474 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| Indices[6] (Refer Table 43.1) | STRUCT |

Table 43.1 Indices

| Structure Name | INDICES |
| --- | --- |
| Packet Length | 71 Bytes |
| Field Name | Data Type |
| IndexName | CHAR |
| IndexValue | LONG |
| HighIndexValue | LONG |
| LowIndexValue | LONG |
| OpeningIndex | LONG |
| ClosingIndex | LONG |
| PercentChange | LONG |
| YearlyHigh | LONG |
| YearlyLow | LONG |
| NoOfUpmoves | LONG |
| NoOfDownmoves | LONG |
| MarketCapitalisation | DOUBLE |
| NetChangeIndicator | CHAR |
| FILLER | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_INDICES (7207) |
| NoOfRecords | This field contains the number of indices currently supported by the system. Depending upon this number, there will be records filled up in subsequent Indices structure. |
| Indices | This field is an array of structure. The attributes of this structure are given below in this table itself. |
| IndexName | This field contains Name of the index. For example, Nifty |
| IndexValue | This field contains the online market index value at that instance of broadcast. |
| HighIndexValue | This field contains the day's highest index value at the time of broadcast. |
| LowIndexValue | This field contains day's lowest index value at the time of broadcast. |
| OpeningIndex | This field contains the opening index value at the time of market open. In Preopen, Indicative Index value will be computed on indicative opening price. Once the final open price is computed, the final index value will be sent. |
| ClosingIndex | If market is open, this field it is set to previous day's closing index. After completion of day's batch processing, this field value shows today's close. |
| PercentChange | This field contains the percent change in current index with respect to yesterday's closing index. |
| YearlyHigh | This field contains the highest index in the year. |
| YearlyLow | This field contains the lowest index in the year. |
| NoOfupmoves | This field contains the number of time index has moved up with respect to previous index. |
| NoOfdownmoves | This field contains the number of time index has moved down with respect to previous index. |
| MarketCapitalization | This field contains the Market Capitalization of securities participating in the index. |
| NetChange Indicator | This field contains one of the following values. • '+' - if the current index is greater than previous index. • ' - ' - if the current index is less than previous index. • ' ' - if the current index is equal to previous index. |

## Multiple Indicative Index Broadcast

The Indicative Index Broadcast messages will start arriving half an hour before the market close.  The multiple indicative index broadcast structure is as follows:

## BROADCAST INDICATIVE INDICES

| Structure Name | BROADCAST INDICATIVE INDICES |
| --- | --- |
| Transaction Code | BCAST_INDICATIVE_INDICES (8207) |
| Packet Length | 474 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| IndicativeIndices[6] (Refer Indicative Indices Table ) | STRUCT |

## Indicative Indices

| Structure Name | INDICATIVE INDICES |
| --- | --- |
| Packet Length | 71 Bytes |
| Field Name | Data Type |
| IndexName | CHAR |
| IndicativeCloseValue | LONG |
| Reserved | LONG |
| Reserved | LONG |
| Reserved | LONG |
| ClosingIndex | LONG |
| PercentChange | LONG |
| Reserved | LONG |
| Reserved | LONG |
| Change | LONG |
| Reserved | LONG |
| MarketCapitalization | DOUBLE |
| NetChange Indicator | CHAR |
| FILLER | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_INDICATIVE_INDICES (8207) |
| NoOfRecords | This field contains the number of indicative indices currently supported by the system. Depending upon this number, there will be records filled up in subsequent Indicative Indices structure. |
| IndicativeIndices | This field is an array of structure. The attributes of this structure are given below in this table itself. |
| IndexName | This field contains Name of the indicative index. For example, Nifty |
| IndicativeCloseValue | This field contains the indicative index close value. |
| ClosingIndex | If market is open, this field it is set to zero. After completion of day's batch processing, this field value shows closing value of the index. |
| PercentChange | This field contains the difference between the Indicative closing value and previous day's closing value of the index in percentage format. |
| Change | This field contains the absolute difference between the Indicative closing value and previous day's closing value of the index. |
| MarketCapitalization | This field contains the Market Capitalization of securities participating during the indicative close session. |
| NetChange Indicator | This field contains one of the following values. • '+' - if the current index is greater than previous indicative close index. • ' - ' - if the current index is less than previous indicative close index. • ' ' - if the current index is equal to previous indicative close index. |

## Multiple Index Broadcast for INDIA VIX

The multiple index broadcast structure for INDIA VIX is as follows:

| Structure Name | BROADCAST INDICES VIX |
| --- | --- |
| Transaction Code | BCAST_INDICES_VIX(7216) |
| Packet Length | 474 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| Indices[6] (Refer Table 44.1) | STRUCT |

Table 44.1   INDICES

| Structure Name | INDICES |
| --- | --- |
| Packet Length | 71 Bytes |
| Field Name | Data Type |
| IndexName | CHAR |
| IndexValue | LONG |
| HighIndexValue | LONG |
| LowIndexValue | LONG |
| OpeningIndex | LONG |
| ClosingIndex | LONG |
| PercentChange | LONG |
| YearlyHigh | LONG |
| YearlyLow | LONG |
| NoOfUpmoves | LONG |
| NoOfDownmoves | LONG |
| MarketCapitalisation | DOUBLE |
| NetChangeIndicator | CHAR |
| FILLER | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_INDICES (7216) |
| NoOfRecords | This field contains the number of indices currently supported by the system. Depending upon this number, there will be records filled up in subsequent Indices structure. |
| Indices | This field is an array of structure. The attributes of this structure are given below in this table itself. |
| IndexName | This field contains Name of the index. It will be India VIX |
| IndexValue | This field contains the online market index value at that instance of broadcast. |
| HighIndexValue | This field contains the day's highest index value at the time of broadcast. |
| LowIndexValue | This field contains day's lowest index value at the time of broadcast. |
| OpeningIndex | This field contains the opening index value at the time of market open. |
| ClosingIndex | If market is open, this field it is set to previous day's closing index. After completion of day's batch processing, this field value shows today's close. |
| PercentChange | This field contains the percent change in current index with respect to yesterday's closing index. |
| YearlyHigh | This field contains the highest index in the year. |
| YearlyLow | This field contains the lowest index in the year. |
| NoOfupmoves | This field contains the number of time index has moved up with respect to previous index. |
| NoOfdownmoves | This field contains the number of time index has moved down with respect to previous index. |
| MarketCapitalizat ion | This field contains the Market Capitalization of securities participating in the index. |
| NetChange Indicator | This field contains one of the following values. '+' - if the current index is greater than previous index. ' - ' - if the current index is less than previous index. ' ' - if the current index is equal to previous index. |

## Broadcast industry index

This Packet contains the index values of 17 Indices with name. The structure is as follows:

| Structure Name | BROADCAST INDUSTRY INDICES |
| --- | --- |
| Transaction Code | BCAST_IND_INDICES (7203) |
| Packet Length | 484 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| Indices[17] (Refer Table 45.1) | STRUCT |

| Structure Name | INDICES |
| --- | --- |
| Packet Length | 25 Bytes |
| Field Name | Data Type |
| Industry Name[21] | CHAR |
| Packet Length | 25 Bytes |
| Field Name | Data Type |
| IndexValue | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_IND_INDICES (7203). |
| NoOfRecords | This field contains the number of indices currently supported by the system. Depending upon this number, there will be records filled up in subsequent Indices structure. |
| Indices | This field is an array of structure. The attributes of this structure are given below in this table itself |
| IndexName | This field contains Name of the index. For example, Defty, CNX IT |
| IndexValue | This field contains the online market index value at that instance of broadcast. |

## Broadcast buy back Information

This packet will contain the buyback Information which are running on that day. This will be broadcasted for every one hour from Market open till market closes on that day. The structure is as follows:

| Structure Name | BROADCAST BUY_BACK |
| --- | --- |
| Transaction Code | BCAST_BUY_BACK (18708) |
| Packet Length | 426 Bytes |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NumberOfRecords | SHORT |
| BuyBackData [6] (Refer Table 46.1) | STRUCT |

Table 46.1 BUYBACKDATA

| Structure Name | BUYBACKDATA |
| --- | --- |
| Packet Length | 64 Bytes |
| Field Name | Data Type |
| Token | LONG |
| Symbol | CHAR |
| Series | CHAR |
| PdayCumVol | DOUBLE |
| PdayHighPrice | LONG |
| PdayLowPrice | LONG |
| PdayWtAvg | LONG |
| CdayCumVol | DOUBLE |
| CdayHighPrice | LONG |
| CdayLowPrice | LONG |
| CdayWtAvg | LONG |
| StartDate | LONG |
| EndDate | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_BUY_BACK (18708) |
| NoOfRecords | This field contains the number of times the structure BuyBackData is repeated. |
| BuyBackData | This field is an array of structure. The attributes of this structure are given below in this table itself. |
| Token | This field contains a unique number that is given to a particular symbol-series combination. |
| Symbol | This field contains the symbol of the security. |
| Series | This field contains the series of the security. |
| PDayCumVolume | This field contains previous day cumulative Volume |
| PDayHighPrice | This field contains Previous day's High Price |
| PDayLowPrice | This field contains Previous day's Low Price |
| PDayWeightAvg | This field contains Previous day's Weighted Average Price |
| CDayCummulativeVolume | This field contains current day's cumulative Volume |
| CDayHighPrice | This field contains current day's High Price |
| CDayLowPrice | This field contains current day's Low Price |
| CDayWeightAvg | This field contains current day's Weighted Average Price |
| StartDate | This field contains Start Date of Buy back period |
| EndDate | This field contains End Date of Buy back period |

## CALL AUCTION Order Cancel Update

In case of Special Preopen Session (SPOS) for IPO/Relist, order cancellation statistics will be sent to users during order collection period.

Order cancel statistics will be sent only for securities which are eligible to take part in Special Preopen Session.

The cancellation statistics will solely reflect order cancellation initiated by market participant.

Order cancelled by system/exchange will be excluded from cancellation statistics.

The transaction code to disseminate the order cancel statistics data during call auction session is BCAST_CALL AUCTION_ORD_CXL_UPDATE (7210).

The structure on the transcode is as show below:

## BROADCAST CALL AUCTION ORD CXL UPDATE

| Structure Name | BROADCAST CALL AUCTION ORD CXL UPDATE |
| --- | --- |
| Packet Length | 490 bytes |
| Transaction Code | BCAST_CALL AUCTION_ORD_CXL_UPDATE (7210) |
| Field Name | Data Type |
| BCAST_HEADER (Refer Table 3) | STRUCT |
| NoOfRecords | SHORT |
| INTERACTIVE ORD CXL DETAILS [8] (Refer Table 69.1) | STRUCT |

## INTERACTIVE ORD CXL DETAILS

| Structure Name | INTERACTIVE ORD CXL DETAILS |
| --- | --- |
| Packet Length | 56 bytes |
| Field Name | Data Type |
| Token | LONG |
| Filler | CHAR |
| BuyOrdCxlCount | LONG LONG |
| BuyOrdCxlVol | LONG LONG |
| SellOrdCxlCount | LONG LONG |
| SellOrdCxlVol | LONG LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code set for the purpose is BCAST_CALL AUCTION_ORD_CXL_UPDATE (7210). |
| NoOfRecords | This field contains the number of securities sent. |
| Token | This field contains the token number - a unique number given to a particular symbol-series combination. |
| BuyOrdCxlCount | This field contains the total count of buy orders cancelled for the security during SPOS session. |
| BuyOrdCxlVol | This field contains the total quantity of buy orders cancelled for the security during SOPS session. |
| SellOrdCxlCount | This field contains the total count of sell orders cancelled for the security during SPOS session. |
| SellOrdCxlVol | This field contains the total quantity of sell orders cancelled for the security during SPOS session. |