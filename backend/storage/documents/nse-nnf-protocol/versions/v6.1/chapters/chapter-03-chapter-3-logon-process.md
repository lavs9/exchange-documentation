---
title: "Chapter 3 Logon Process"
chapter_number: 3
page_range: "23-46"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 3 Logon Process


## Introduction

This section describes how a trader logs on to the trading system. It covers the log-on request and the system responses. This section also describes the download of the updated information on the securities, participants, and the status of the markets. It covers the structures and field descriptions  of  System  Information  Download,  Local  Database  Download  and  Message Download.

The process by which a trader logs on to the trading system is called Logon Process. The trader, after  issuing  a  sign-on  request,  waits  for  the  system  response.  The  response  could  be  a successful logon or an error message.

## Message Download Changes

- Messages will be sent through various streams (at The Exchange). The stream number will be sent in the TimeStamp2 field of the message header.
- The total number of streams from the Exchange will be specified in the first byte of alpha char field (alpha char is of 2 bytes) of the header section of SYSTEM_INFORMATION_OUT (1601) message. Streams are numbered starting from 1. E.g.: If the value in the alpha char field is 4, total number of streams from the Exchange is 4 and the stream numbers will be 1,2,3,4.
- The mechanism for message download request has changed, Message downloads will now be served through each individual stream . Hence, message download request needs to be sent individually for a stream by the user.
- In the message download request (Transcode 7000), first byte of alpha char field of the header section should contain the stream number for which the message download is required. If the stream no. sent in the request is invalid then exchange will drop the request. The Sequence number field must contain the sequence number value for that particular stream.
- The response of the request will be sent individually through the specified stream starting from the next sequence number specified in the request. Message download from each stream will have header, data and trailer section (same as existing format).
- o Header -This is to indicate that message download is going to commence. The first byte of alpha char field of header will contain the stream number.

- o Data -The data is wrapped in another structure. The outer header indicates that this message is a part of the Message Download Data. The inner header indicates the type of data received. The first byte of alpha char field of outer header will contain the stream number.
- o Trailer -This indicates that message download is complete. The first byte of alpha char field of header will contain the stream number.
- Message download request can be made for one or more streams. It is recommended that the user requests download for all the streams.
- If the sequence number in the request is 0, then all messages for that stream will be sent. To get incremental download for any particular stream, the message download request must contain the last sequence number received from that stream.

## Note:

- Structure for message download request is not changed.
- Structure for message download response is not changed.

## Illustration: -

In the illustration given below s1, s2, s3, s4 represent separate streams

## Order of Events to Be Followed During Logon and Logoff

The following sequence explains the order in which transaction codes are sent and received during log-on process.

| Sequence No | Transaction Code | Sent By | Received By |
| --- | --- | --- | --- |
| 1 | SIGN_ON_REQUEST_IN (2300) | TWS | Host End |
| 2 | SIGN_ON_REQUEST_OUT (2301) | Host End | TWS |
| 3 | SYSTEM_INFORMATION_IN (1600) | TWS | Host End |
| 4 | SYSTEM_INFORMATION_OUT (1601) | Host End | TWS |
| 5 | UPDATE_LOCALDB_IN (7300) | TWS | Host End |
| 6 | UPDATE_LOCALDB_HEADER (7307) | Host End | TWS |
| 7 | UPDATE_LOCALDB_DATA (7304) | Host End | TWS |
| 8 | UPDATE_LOCALDB_TRAILER (7308) | Host End | TWS |
| 9 | DOWNLOAD_REQUEST (7000) | TWS | Host End |
| 10 | HEADER_RECORD (7011) | Host End | TWS |
| 11 | MESSAGE_RECORD (7021) | Host End | TWS |
| 12 | TRAILER_RECORD (7031) | Host End | TWS |
| 1 | SIGN_OFF_REQUEST_IN (2320) | TWS | Host End |
| 2 | SIGN_OFF_REQUEST_OUT (2321) | Host End | TWS |

## Logon Request

When the user wants to establish an interactive circuit with the host, he sends this request.

Eligibility  for  the  broker  to  participate  in  the  CALL  AUCTION  2  Market  is  being  used.  In SIGN_ON_REQUEST_IN, one  bit  from  the  existing  reserved  bit  in  BrokerEligibilityPerMarket structure is getting re-used for CALL AUCTION 2 market eligibility.

In the request packet sent from TWS to the Exchange, the value for these bits must be set to numerical  zero,  similar  to  other  Market  eligibility  bits,  The  modified  structure  as  per  above change is given below.

| Structure Name | SIGNON IN |
| --- | --- |
| Packet Length | 276 bytes |
| Transaction Code | SIGN_ON_REQUEST_IN (2300) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| Reserved | CHAR |
| Password | CHAR |
| Reserved | CHAR |
| NewPassword | CHAR |
| TraderName | CHAR |
| LastPasswordChangeDateTime | LONG |
| BrokerId | CHAR |
| Reserved | CHAR |
| BranchId | SHORT |
| VersionNumber | LONG |
| Packet Length | 276 bytes |
| Transaction Code | SIGN_ON_REQUEST_IN (2300) |
| Field Name | Data Type |
| Reserved | CHAR |
| UserType | SHORT |
| SequenceNumber | DOUBLE |
| WorkstationNumber | CHAR |
| BrokerStatus | CHAR |
| ShowIndex | CHAR |
| BrokerEligibilityPerMarket (Refer Table 7.1 for Small Endian machines and Table 7.2 for Big Endian machines) | STRUCT |
| BrokerName | CHAR |
| Reserved | CHAR |
| Reserved | CHAR |
| Reserved | CHAR |

## For Small Endian Machines:

| Structure Name | BrokerEligibilityPerMarket |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Call Auction2 | BIT |
| Call Auction1 | BIT |
| Auction market | BIT |
| Spot market | BIT |
| Oddlot market | BIT |
| Normal market | BIT |
| Preopen | BIT |
| Reserved | BIT |

## For Big Endian Machines:

| Structure Name | BrokerEligibilityPerMarket |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Normal market | BIT |
| Oddlot market | BIT |
| Spot market | BIT |
| Auction market | BIT |
| Call Auction1 | BIT |
| Call Auction2 | BIT |
| Reserved | BIT |
| Reserved | BIT |
| Preopen | BIT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SIGN_ON_REQUEST_IN (2300). |
| UserId | This field should contain User ID of user/broker. This field accepts numbers only. |
| Password | This field should contain the password entered by the user. A combination of alphabet, numbers and special characters are allowed in the password. The user should enter the password for a successful Logon.Whentheuserlogs onfor the first time the default password provided by NSE must be entered and the password should be changed by entering a new password. |
| NewPassword | This field should contain the new password entered by the user. This field should be entered only when the user wishes to change the password or the password has expired. Otherwise this field should be blank. The New Password should be entered along with the old password in the Password field. While logging on the system for the first time, the default password provided by NSE must be changed. the new password entered will undergo following new validations : |
|  | • The length of password should be of exact 8 characters. • The password should contain at least 1 upper case letter, 1 lower case letter, 1 numeral and 1 special characters from the list (@ #$%&*/\). • New password must be different from previous 5 passwords. • User Id shall be locked after 3 invalid login attempts. • User shall not be allowed to set the default password as new password. |
| TraderName | This field when received from the host contains the user's name. This field should be sent to host as blanks. |
| LastPassword ChangeDateTime | This field should be set to numerical zero while log on. |
| BrokerId | This field should contain the trading member ID. |
| BranchId | This field should contain the Branch ID to which the broker belongs. |
| VersionNumber | This field should contain the version number of the trading system. It must be in the following format: VERSION.RELEASE.SUB_RELEASE (For example, 01.00.01) As and when these structures are changed, the version number will be changed. |
| UserType | This field indicates the type of user. It can take one of the following values when it is sent from the host: '0' denotes Dealer '4' denotes Corporate Manager '5' denotes Branch Manager '7' denotes Market Maker This field should be set to '0' while sending to the host. |
| SequenceNumber | This field should be set to numerical zero while sending the request to host. |
| WorkstationNumber | The network ID of the workstation should be provided. This is a seven digit number. The first five digits are fixed by the Exchange and represent the various ports / switch locations. The last two digits denote the user's PC - ID. It must be any number other than '00'. |
| BrokerStatus | This field should be set to blank. |
| BrokerEligibilityPer Market | This field should be set to numerical zero. |
| BrokerName | This field should be set to blank |

## Logon Response

The response will either be Confirmation or Logon Error .

## Logon Confirmation Response

A successful logon results in the Logon Confirmation Response. In SIGN_ON_REQUEST_OUT, Eligibility for the broker in CALL AUCTION 2 is being used by the existing reserved Market bit in BrokerEligibilityPerMarket structure. If the value received in these bits is 1', the broker is eligible to trade in respective markets. The following modified structure will be sent to the TWS from the Exchange:

| Structure Name | SIGNON OUT |
| --- | --- |
| Packet Length | 276 bytes |
| Transaction Code | SIGN_ON_REQUEST_OUT (2301) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| Reserved | CHAR |
| Password | CHAR |
| Reserved | CHAR |
| NewPassword | CHAR |
| TraderName | CHAR |
| LastPasswordChangeDate | LONG |
| BrokerId | CHAR |
| Reserved | CHAR |
| BranchId | SHORT |
| VersionNumber | LONG |
| EndTime | LONG |
| Packet Length | 276 bytes |
| Transaction Code | SIGN_ON_REQUEST_OUT (2301) |
| Field Name | Data Type |
| Reserved | CHAR |
| UserType | SHORT |
| SequenceNumber | DOUBLE |
| Reserved | CHAR |
| BrokerStatus | CHAR |
| Reserved | CHAR |
| BrokerEligibilityPerMarket (Refer Table 8.1 for Small Endian Machines and Table 8.2 for Big Endian Machines) | STRUCT |
| BrokerName | CHAR |
| Reserved | CHAR |
| Reserved | CHAR |
| Reserved | CHAR |

| Structure Name | BrokerEligibilityPerMarket |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Call Auction2 | BIT |
| Call Auction1 | BIT |
| Auction market | BIT |
| Spot market | BIT |
| Oddlot market | BIT |
| Normal market | BIT |
| Preopen | BIT |
| Reserved | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Normal market | BIT |
| Oddlot market | BIT |
| Spot market | BIT |
| Auction market | BIT |
| Call Auction1 | BIT |
| Call Auction2 | BIT |
| Reserved | BIT |
| Reserved | BIT |
| Preopen | BIT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SIGN_ON_REQUEST_OUT (2301). |
| LogTime | The current time at the trading system is sent back as number of seconds since midnight of January 1, 1980 The time at the Trader workstation must be synchronized with this. |
| UserId | This field contains the ID of the user. |
| Password | This field will be set to NULL. |
| NewPassword | This field will be set to NULL. |
| TraderName | This field contains the user name. |
| LastPassword ChangeDate | This filed contains the last date time when the password was changed. |
| BrokerId | This field contains the Trading Member ID. |
| BranchId | This field contains the branch ID of the particular user. |
| Version No | This field contains the version number of the trading system |
| EndTime | This field contains the time the markets last closed and is sent as the number of seconds since midnight of January 1, 1980. If this time is different from the time sent in an earlier log on, all orders, trades and messages for this trader must be deleted from the Local Database. |
| UserType | This field contains the type of user who is logging on: • '0' - Dealer • '4' - Corporate Manager |
|  | • '5' - Branch Manager • '7' - Market Maker |
| SequenceNumber | This field contains the time when the markets closed the previous trading day. |
| BrokerStatus | This field contains the current status of the broker: • 'S' for Suspended • 'A' for Active • 'D' for Deactivated • 'C' for Closeout or voluntary closeout |
| BrokerEligibility PerMarket | This structure specifies the markets that are allowed for the trading member. The trading member is eligible to enter orders in the markets that are set to 1. |
| BrokerName | This field contains the broker's name (trading member name). |

## Logon Error

In case of any error, the structure returned is:

ERROR RESPONSE (Refer to Error Message in [Chapter 2](#chapter-2-general-guidelines))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SIGN_ON_REQUEST_OUT (2301). |
| ErrorCode | This contains the error number. If the version number is not the same as at the host end, the version number at the host can be extracted from Error_Message in ERROR_RESPONSE (8 bytes from location 95 in the string). The format of it will be VV.RR.SS. The version number at the front end should be set to VVRRSS. Refer to List of Error Codes in Appendix. |

## System Information Download

The current status of the markets and the values of global variables are downloaded to the trader in response to system information request.

## System Information Request

This request can be sent only if the user has logged on successfully. The format of the request is as follows:

## Table 9 SYSTEM_INFO_REQ

| Structure Name | SYSTEM_INFO_REQ |
| --- | --- |
| Packet Length | 40 bytes |
| Transaction Code | SYSTEM_INFORMATION_IN (1600) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SYSTEM_INFORMATION_IN (1600). |

> [!note]
> TWS User has to set time_stamp2 field present in the TWS message header to                zero in SYSTEM_INFORMATION_IN message.

## System Information Response

The following structure is returned as a response to the system information request:

## Table 10 SYSTEM_INFORMATION_DATA

| Structure Name | SYSTEM_INFORMATION_DATA |
| --- | --- |
| Packet Length | 94 bytes |
| Transaction Code | SYSTEM_INFORMATION_OUT (1601) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Normal | SHORT |
| Oddlot | SHORT |
| Spot | SHORT |
| Auction | SHORT |
| Call Auction1 | SHORT |
| Call Auction2 | SHORT |
| MarketIndex | LONG |
| DefaultSettlementPeriod (Normal) | SHORT |
| DefaultSettlementPeriod (Spot) | SHORT |
| DefaultSettlementPeriod (Auction) | SHORT |
| CompetitorPeriod | SHORT |
| SolicitorPeriod | SHORT |
| WarningPercent | SHORT |
| VolumeFreezePercent | SHORT |
| Packet Length | 94 bytes |
| Transaction Code | SYSTEM_INFORMATION_OUT (1601) |
| Field Name | Data Type |
| Reserved | CHAR |
| TerminalIdleTime | SHORT |
| BoardLotQuantity | LONG |
| TickSize | LONG |
| MaximumGtcDays | SHORT |
| SECURITY ELIGIBLE INDICATORS(Refer Table 10.1 for Small Endian machines and Table 10.2 for Big Endian machines) | STRUCT |
| DisclosedQuantityPercentAllowed | SHORT |
| Reserved | CHAR |

Table 10.1 SECURITY ELIGIBLE INDICATORS (For Small Endian Machines)

| Structure Name | SECURITY ELIGIBLE INDICATORS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | BIT |
| Books Merged | BIT |
| Minimum Fill | BIT |
| AON | BIT |
| Reserved | CHAR |

Table 10.2 SECURITY ELIGIBLE INDICATORS (For Big Endian Machines)

| Structure Name | SECURITY ELIGIBLE INDICATORS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| AON | BIT |
| Minimum Fill | BIT |
| Books Merged | BIT |
| Reserved | BIT |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SYSTEM_INFORMATION_OUT (1601). |
| Alphachar | This field contains the number of streams present in the host from which Message download will be served. This field is present in the Message Header. This is totally of two bytes. Stream number will be populated in the first byte of alphachar. |
| MarketStatus | This field contains a value assigned for market status. Values are: '0' if it is Preopen '1' if it is Open '2' if it is Closed '3' if it is Preopen end For CALL AUCTION2 market, market status will be received as : '0' - Preopen '2' - Closed '3' - Preopen end In the pre-open state of the market, orders can only be entered but no matching takes place. The trading starts when the market is Open. No orders can be entered for a security when |
| MarketIndex | This field contains the current market index. |
| SettlementPeriod | This field contains the default settlement period in various markets. Default Settlement (Normal), Default Settlement (Spot) and Default Settlement (Auction). |
| CompetitorPeriod | This field contains the default competitor period for auction. |
| SolicitorPeriod | This field contains the default solicitor period for auction. |
| WarningPercent | This field contains the warning percentage. If a broker exceeds his turnover by this value in percent, a warning message is broadcast to all traders. Refer to Turnover Limit Exceeded Or Broker Reactivated in [Chapter 7](#chapter-7-broadcast). |
| VolumeFreezePercent | This field contains the volume freeze percentage. If a broker exceeds his turnover by this value in percent, the broker is deactivated and a message is broadcasted to all traders. Refer to Turnover Limit Exceeded Or Broker Reactivated in [Chapter 7](#chapter-7-broadcast). |
| TerminalIdleTime | This field contains the idle time of the TWS terminal. |
| BoardLotQuantity | This field contains the board lot quantity. The regular lot order quantity must be a multiple of this quantity. |
| TickSize | This field contains the Tick size. The order price and the trigger price, if applicable, must be a multiple of this tick size. |
| MaximumGTCDays | This field contains the maximum GTC days, that is, the maximum number of days after which a Good Till Canceled order will be canceled. |
| SecurityEligibilityIndicato r | If the Minimum Fill flag is set, then orders will have the Minimum Fill attribute set. If the All Or None (AON) flag is set, then orders will have the AON attribute set. |
| DisclosedQuantity PercentAllowed | This field contains the disclosed quantity allowed percentage. The disclosed quantity, if set, will not be lesser than this percent of the total quantity. |

## Update Local Database Download

The  list  of  updated  securities  and  participants  is  downloaded  in  response  to update  local database request. Any carried over GTC or GTD orders are also downloaded with this request. As of now GTC and GTD facilities are not allowed hence there will be no download for GTC and GTD orders.

## Update Local Database Request

This message is sent to request the host end to update the local database at the front end. The structure sent is as follows:

| Structure Name | UPDATE_LOCALDB_IN |
| --- | --- |
| Packet Length | 62 bytes |
| Transaction Code | UPDATE_LOCALDB_IN (7300) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Packet Length | 62 bytes |
| Transaction Code | UPDATE_LOCALDB_IN (7300) |
| Field Name | Data Type |
| LastUpdateSecurityTime | LONG |
| LastUpdateParticipantTime | LONG |
| RequestForOpenOrders | CHAR |
| Reserved | CHAR |
| NormalMarketStatus | SHORT |
| OddLotMarketStatus | SHORT |
| SpotMarketStatus | SHORT |
| AuctionMarketStatus | SHORT |
| CallAuction1MarketStatus | SHORT |
| CallAuction2MarketStatus | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is UPDATE_LOCALDB_IN (7300). |
| LastUpdateSecurityTime | This field should contain the time when the security information was last updated. This field is for each security for which information is downloaded. Further download requests can use the latest time to get updated information on the securities. Setting this time to zero results in complete download. |
| LastUpdateParticipantTime | This field should contain the time when the participant information was updated. This field is set for each participant for whom information is downloaded. Further download requests can use the latest time to get updated information on the participants. Setting this time to zero results in complete download. |
| RequestForOpenOrders | This field should be set to 'G' if GTC and GTD orders are to be downloaded. In other cases, it should be set to 'N'. |
| NormalMarketStatus | This field should contain the latest Normal Market status available at TWS. |
| OddLotMarketStatus | This field should contain the latest Odd Lot Market status available at TWS. |
| SpotMarketStatus | This field should contain the latest Spot Market status available at TWS. |
| AuctionMarketStatus | This field should contain the latest Auction Market status available at TWS. |
| Call Auction1MarketStatus | This field should contain the latest CALL AUCTION1 Market status available at TWS. |
| Call Auction2MarketStatus | This field should contain the latest CALL AUCTION2 Market status available at TWS. |

## Update Local Database Response

The response will be either the database download, or a partial system information download. The latter will occur if the trader does not have the latest market status.

## Partial System Information Response

This is returned if the market status sent in the UPDATE_LOCALDB_IN message is not the same at the host end or the symbols (securities) are opening. In this case the market status at the host end is sent back in the MARKET STATUS as 'wait till markets are open ' . The following structure is returned:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is PARTIAL_SYSTEM_INFORMATION (7321). |
| MarketStatus | This contains the latest market status. |

## Update Local Database Download

The  download  comprises  of  a  header,  data  and  the  trailer.  Each  updated  security  status, participant (if selected) and GTC/GTD order will be sent as a separate message. As of now GTC and GTD facilities are not allowed hence there will be no download for GTC and GTD orders.

## Update Local Database Header

This is sent only to indicate that a sign-on download is going to commence. There is no additional data sent. The header is sent in the following format:

## Table 12 UPDATE_LDB_HEADER

| Structure Name | UPDATE_LDB_HEADER |
| --- | --- |
| Packet Length | 42 bytes |
| Transaction Code | UPDATE_LOCALDB_HEADER (7307) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is UPDATE_LOCALDB_HEADER (7307). |

## Update Local Database Data

The actual data is sent wrapped in another header. The outer header indicates that this message is part of the Update Local Database Data. The inner header indicates the type of data received.

The structure is as follows:

| Structure Name | UPDATE_LOCAL_DB_DATA |
| --- | --- |
| Packet Length | 80 to 512 bytes |
| Transaction Code | UPDATE_LOCALDB_DATA (7304) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Data | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is UPDATE_LOCALDB_DATA (7304). |
| InnerTransactionCode | The transaction codes sent are BCAST_SECURITY_MSTR_CHG. It is determined by NSE-Control whether to send this or not. (Refer to Change in Security Master in [Chapter 7](#chapter-7-broadcast)) |
|  | BCAST_SECURITY_STATUS_CHG. This transaction code is sent when the status of the stock is different from the expected status at the host end (Refer to Change of Security Status in [Chapter 7](#chapter-7-broadcast)) BCAST_PART_MSTR_CHG. If there is any change in the participant master after the time specified by the Last Update Participant Time, it is downloaded. (Refer to Change Participant Status in [Chapter 7](#chapter-7-broadcast)) - In all above messages, use INNER_MESSAGE_HEADER [ Refer Inner Message Header in [Chapter 2](#chapter-2-general-guidelines) ] instead of MESSAGE_HEADER |

## Update Local Database Trailer

This indicates that the download is complete. This is sent in the following format:

| Structure Name | UPDATE_LDB_ TRAILER |
| --- | --- |
| Packet Length | 42 bytes |
| Transaction Code | UPDATE_LOCALDB_TRAILER. (7308) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is UPDATE_LOCALDB_TRAILER (7308). |

## Message Download

This request is used to download the messages intended for the trader from the trading system. When the trader makes a request for message download, all the transactions of the trader and other important broadcasts are downloaded.

Message downloads will be served through each individual stream. Hence, message download request needs to be sent individually for a stream by the user.

## Message Download Request

This message is sent for requesting message download. The structure sent to the trading system is:

| Structure Name | MESSAGE DOWNLOAD |
| --- | --- |
| Packet Length | 48 bytes |
| Transaction Code | DOWNLOAD_REQUEST (7000) |
| Field Name | Data Type |
| MESSAGE_HEADER(Refer Table 1) | STRUCT |
| SequenceNumber | DOUBLE |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is DOWNLOAD_REQUEST (7000). |
| SequenceNumber | This contains the time last message was received by the workstation. This can be obtained from the Time Stamp1 of the MESSAGE_HEADER. To retrieve the messages from the beginning of the trading day, this field should be set to '0' or the Sequence Number received in the logon response message. |
| AlphaChar | This contains the stream number of the host to which it has to send the DOWNLOAD_REQUEST. The alpachar is the character array of size 2. The stream number of the host is sent in the first byte of the alphachar. The number of streams is obtained in SYSTEM_INFORMATION_OUT from host during login sequence. |

## Message Download Response

The download comprises of a header, data and the trailer. Each trader specific and broadcast message will be sent as a separate message.

## Message Download Header

This is only to indicate that a message download is going to commence. There is no additional data sent. The header is sent in the following format:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is HEADER_RECORD (7011). |

## Message Download Data

The messages are similar to Update Local Database Data. The actual data is sent wrapped in another structure. The outer header indicates that this message is part of the Message Download Data. The inner header indicates the type of data received. The structure is shown below.

| Structure Name | MESSAGE_HEADER |
| --- | --- |
| Packet Length | 80 to 512 bytes |
| Transaction Code | MESSAGE_RECORD (7021) |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| Data | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | This field is the part of Message Header (Refer to MESSAGE_HEADER structure chapter . The transaction code is MESSAGE_RECORD (7021). |
| InnerData | Set of transaction codes are received. They include Trader Specific Messages • Logon / Logoff response Refer to Logon Process, Chapter 3. • Interactive message sent to the user from the NSE-Control. Refer to Unsolicited Messages, [Chapter 5](#chapter-5-unsolicited-messages). • Order entry, Modification, Cancellation responses Refer to Order and Trade Management, [Chapter 4](#chapter-4) • Trade Modification, Cancellation responses Refer to Order and Trade Management, [Chapter 4](#chapter-4). |
|  | • Trade Confirmation, Stop Loss Trigger Refer to Unsolicited Messages, [Chapter 5](#chapter-5-unsolicited-messages). • Broadcast Messages Market Open, Market Close, Market Pre-Open ended, Preopen Shutdown Message, Broadcast Message String, Turnover exceeded, Broker Reactivated, Broadcast message sent from NSE-Control. Refer to Broadcast, [Chapter 7](#chapter-7-broadcast) • Contingency Broadcast Message Refer to Exception Handling, [Chapter 11](#chapter-11-exception-handling). |

## Message Download Trailer

This indicates that message download is completed for the particular stream. Once download is completed  for  one  stream,  DOWNLOAD_REQUEST  will  be  sent  for  the  next  stream  with  its corresponding sequence number. Request will be sent until message download gets completed for all the streams. The format is as follows:

MESSAGE HEADER (Refer to Table 1 )

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRAILER_RECORD (7031). |

## Logoff Request

The process by which a trader quits or signs off from the trading system is called Logoff Process. The structure sent is:

MESSAGE HEADER (Refer to Table 1 ).

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SIGN_OFF_REQUEST_IN (2320). |

## Logoff Confirmation Response

When the user logs on again, the user receives a packet giving the details of when he/she logged off. The structure sent is:

MESSAGE HEADER (Refer to Table 1 )

> [!note]
> MS_SIGNOFF message is sent in the Message Header itself. The length of the packet is 40 bytes.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is SIGN_OFF_REQUEST_OUT (2321). |
| LogTime | This field contains the current time at the trading system is sent back as number of seconds since midnight of January 1, 1980. The time at the workstation must be synchronized with this. |