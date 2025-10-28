---
title: "Chapter 6 Bhav Copy"
chapter_number: 6
page_range: "82-89"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 6 Bhav Copy


## Introduction

This section describes the end of the trading day activities. It covers the transmission of Security Bhav Copy and Index Bhav Copy.  This takes place after the markets close for the day. Broadly, the following activities are done:

- Calculation of closing price and generation of interim bhav copy (from 3.30 PM to 3. 40 PM).
- Generation of main bhav-copy will be after 4.00 PM.

Closing Batch: In closing batch, the closing price is calculated and broadcast to the traders. The interim bhav copy is also broadcast to the traders. During closing session traders can trade at the closing price.

Closing Session: After closing batch, the market is open for trading for 20 mins. This period is known as Closing Session . Traders can place orders at market price (closing price) only. Some of error codes have been introduced for closing session. Refer List of Error Codes for the same.

## Security Bhav Copy

## Message Stating the Transmission of Security Bhav Copy Will Start Now

This is the first message which is broadcasted saying that the bhav copy will be started now. The structure sent is:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_JRNL_VCT_MSG (6501). Message: Security Bhav Copy is being broadcast now. |

## Header of Report on Market Statistics

A header precedes the actual bhav copy that is sent to the trader. The message structure sent is:

Table 24 MS_RP_HDR

| Structure Name | MS_RP_HDR |
| --- | --- |
| Packet Length | 106 bytes |
| Transaction Code | MARKET_STATS_REPORT_DATA (18201) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| MsgType | CHAR |
| ReportDate | LONG |
| UserType | SHORT |
| BrokerId | CHAR |
| BrokerName | CHAR |
| TraderNumber | SHORT |
| TraderName | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MARKET_STATS_REPORT_DATA (18201). |
| MsgType | This field is set to 'H' denoting Header |
| ReportDate | This field is set to the report date. |
| UserType | This field contains the type of user. This is set to ' - 1'. |
| BrokerId | This field contains Trading Member ID. This is set to blanks. |
| BrokerName | This field contains the name of the broker. This is set to blanks. |
| TraderNumber | This field contains the trader/user ID. This is set to zero. |
| TraderName | This field contains the name of the trader. This is set to blanks. |

## Report on Market Statistics

This is the actual data that is sent for the report. The structure is as follows:

## Table 25 REPORT MARKET STATISTICS

| Structure Name | REPORT MARKET STATISTICS |
| --- | --- |
| Packet Length | 478 bytes |
| Transaction Code | MARKET_STATS_REPORT_DATA (18201) |
| Field Name | Data Type |
| MESSAGE HEADER(Refer Table 1) | STRUCT |
| MessageType | CHAR |
| Reserved | CHAR |
| Packet Length | 478 bytes |
| Transaction Code | MARKET_STATS_REPORT_DATA (18201) |
| Field Name | Data Type |
| NumberOfRecords | SHORT |
| MARKET STATISTICS DATA (Refer Table 25.1) | STRUCT |

Table 25.1 MARKET STATISTICS DATA

| Structure Name | MARKET STATISTICS DATA |
| --- | --- |
| Packet Length | 62 bytes |
| Field Name | Data Type |
| SEC_INFO (Refer Table 4) | STRUCT |
| MarketType | SHORT |
| OpenPrice | LONG |
| HighPrice | LONG |
| LowPrice | LONG |
| ClosingPrice | LONG |
| TotalQuantityTraded | LONG LONG |
| TotalValueTraded | DOUBLE |
| PreviousClosePrice | LONG |
| FiftyTwoWeekHigh | LONG |
| FiftyTwoWeekLow | LONG |
| CorporateActionIndicator | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MARKET_STATS_REPORT_DATA (18201). |
| MessageType | This field is set to 'R' denoting Report Data. |
| NumberOfRecords | This field contains the number of markets for which Market Statistics is being sent. In a packet at most 7 records can be packed. |
| Symbol | This field contains the Symbol of the security. |
| Series | This field contains the series of a security. |
| MarketType | This field contains one of the following values indicating the market type as: • '1' - Normal • '2' - Odd lot • '3' - Spot • '4' - Auction • '5' - Call Auction1 • '6' - Call Auction2 In Bhavcopy, the Market Type of Security Participating in CALL AUCTION2 will come, under Normal Market '. |
| OpenPrice | This field contains the open price of a security. |
| HighPrice | This field contains the highest trade price. |
| LowPrice | This field contains the lowest trade price. |
| ClosingPrice | This field contains the closing price of a security. |
| TotalQuantityTraded | This field contains the total quantity of the security that is traded today. |
| TotalValueTraded | This field contains the total value of the securities traded. |
| PreviousClosePrice | This field contains the previous day's closing price of the security. |
| FiftyTwoWeekHighPric e | This field contains the highest trade price in a security in the immediately previous 52 weeks. |
| FiftyTwoWeekLowPric e | This field contains the lowest trade price in a security in the immediately previous 52 weeks. |
| CorporateActionIndica tor | This field contains the Corporate Action. The EGM, AGM, Interest, Bonus, Rights and Dividend flags are set depending on the corporate action. |

## Packet Indicating Data for Depository Securities Begins

This message indicates that hereafter the bhav copy for depository securities will be broadcast. The structure sent is:

REPORT MARKET STATISTICS (Refer to Report on Market Statistics discussed earlier in this chapter)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MARKET_STATS_REPORT_DATA (18201). |
| MessageType | This field is set to 'D' denoting Data. |

## Data for Depository Securities

This is same as the data packet for non-Depository securities. The structure sent is:

REPORT MARKET STATISTICS (Refer to Report on Market Statistics discussed earlier in this chapter)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MARKET_STATS_REPORT_DATA (18201). |

## Trailer Record

This indicates that the transmission of bhav copy ends here. The structure is:

| Structure Name | REPORT TRAILER |
| --- | --- |
| Packet Length | 46 bytes |
| Transaction Code | MARKET_STATS_REPORT_DATA (18201) |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| MessageType | CHAR |
| NumberOfRecords | LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MARKET_STATS_REPORT_DATA (18201). |
| MessageType | This field is set as 'T' for trailer record. |
| NumberOfRecords | This field contains the number of data packets sent in the bhav copy. |

## Index Bhav Copy

## Message Stating the Transmission of the Index Bhav Copy Will Start Now

This is the first message which is broadcast saying the bhav copy will start now. The structure sent is:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BCAST_JRNL_VCT_MSG (6501). Message: Index Bhav Copy is being broadcast now. |

## Header of Report on Market Statistics

Refer to Header of Report on Market Statistics (Security Bhav Copy) discussed earlier in this chapter.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MKT_IDX_RPT_DATA (1836). |

## Report on Index

This is the actual data that is sent for index data. The structure is as follows:

| Structure Name | MS_RP_MARKET_INDEX |
| --- | --- |
| Packet Length | 464 bytes |
| Transaction Code | MKT_IDX_RPT_DATA (1836) |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| MsgType | CHAR |
| Reserved | CHAR |
| NoOfIndexRecs | SHORT |
| MKT_INDEX [7] (Refer Table 27.1) | STRUCT |

| Packet Length | 60 bytes |
| --- | --- |
| Field Name | Data Type |
| IndName | CHAR |
| MktIndexPrevClose | LONG |
| MktIndexOpening | LONG |
| MktIndexHigh | LONG |
| MktIndexLow | LONG |
| MktIndexClosing | LONG |
| MktIndexPercent | LONG |
| MktIndexYrHi | LONG |
| MktIndexYrLo | LONG |
| MktIndexStart | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MKT_IDX_RPT_DATA (1836). |
| MsgType | This field is set to 'R' denoting Report for Index Data. |
| NoOfIndexRecs | This field contains the number of index records in the packet. |
| IndName | This field contains the name of the index being broadcast. For example, CNX |
| MktIndexPrevClose | This field contains the previous day's closing index. |
| MktIndexOpening | This field contains today's opening index. |
| MktIndexHigh | This field contains today's high index. |
| MktIndexLow | This field contains today's low index. |
| MktIndexClosing | This field contains today's closing index. |
| MktIndexPercent | This field contains %change today. |
| MktIndexYrHi | This field contains 52-week high index. |
| MktIndexYrLo | This field contains 52-week low index. |

## Trailer of Index Data Broadcast

Refer to Trailer Record of Security Bhav Copy discussed earlier in this chapter.