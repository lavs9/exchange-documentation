---
title: "Chapter 8 Inquiry"
chapter_number: 8
page_range: "150-153"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

---
title: "Chapter 8 Inquiry"
chapter_number: 8
page_range: "150-153"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 8 Inquiry


## Introduction

This section describes the Auction Inquiry and the system responses for the same.

## Auction Inquiry Request

The format of the message sent in a structure is as follows:

| Structure Name | MS_AUCTION_INQ_REQ |
| --- | --- |
| Transaction Code | AUCTION_INQUIRY_IN (18016) |
| Packet Length | 55 Bytes |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| SEC_INFO (Refer Table 4) | STRUCT |
| AuctionNo | SHORT |
| PageIndicator | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is AUCTION_INQUIRY_IN (18016) |
| SEC_INFO | This structure should contain the symbol and series for a particular security |
| AuctionNo | This field should contain the auction number. It is optional to specify symbol and series. |
| PageIndicator | This field is to help the user browse through various pages of information. It contains the values of 'U', 'D', 'H', 'E', 'F' for Up, Down, Home, End, and First respectively |

## Auction Inquiry Response

As  soon  as  the  auction  inquiry  request  reaches  the  system,  it  sends  back  the  structure  of response in the MESSAGE HEADER (Refer to Message Header in [Chapter 2](#chapter-2-general-guidelines)). The response can be either an error code or the requested response.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is AUCTION_INQUIRY_OUT (18017). |
| ErrorCode | This field contains the error code. If this error code is not '0' then error has occurred, if this is zero, then auction inquiry is successful. In case of error, symbol, series or auction number may be wrong or the auction inquiry as a whole may be wrong. In this case, the same structure is sent back in which the message header is present. |
| NumberOf Records | This field contains the number of records that are sent in the Inquiry Data structure which follows this field. |
| InquiryData | This is an array of structure. It contains the inquiry data. Refer to Auction Activity Message in [Chapter 7](#chapter-7-broadcast) for details of fields in the Inquiry Data structure |

| Structure Name | AUCTION INQUIRY RESPONSE |
| --- | --- |
| Packet Length | 222 bytes |
| Transaction Code | AUCTION_INQUIRY_OUT (18017) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| NumberOfRecords | SHORT |
| InquiryData[5] (Refer Table 48.1) | STRUCT |

| Structure Name | INQUIRYDATA |
| --- | --- |
| Packet Length | 36 bytes |
| Field Name | Data Type |
| Token | LONG |
| AuctionNumber | SHORT |
| AuctionStatus | SHORT |
| InitiatorType | SHORT |
| TotalBuy | LONG |
| BestBuyPrice | LONG |
| TotalSell | LONG |
| BestSellPrice | LONG |
| Packet Length | 36 bytes |
| Field Name | Data Type |
| AuctioinPrice | LONG |
| AuctionQuantity | LONG |
| SettlementPeriod | SHORT |