---
title: "Chapter 2 General Guidelines"
chapter_number: 2
page_range: "13-23"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 2 General Guidelines


## Introduction

This chapter provides general guidelines for the designers and programmers who develop NNF. It also provides information on data types and their size which can help in understanding various structures.

## Message Structure Details

The message structure consists of two parts namely message header and message data. The message header consists of the fields of the header which is prefaced with all the structures.

The message data consists of the actual data that is sent across to the trading system (i.e. host) or received from the trading system (i.e. host).

Transaction code, an important field of the message header, is a unique numeric identifier which is sent to or received from the trading system. This is used to identify the transaction between the TWS and the host end.

## Guidelines for Designers

- The order of the log-on messages should strictly be maintained as given in the following section ([Chapter 3](#chapter-3-logon-process)) of the document. Otherwise, the user cannot log on to the trading system.
- All time fields are number of seconds from midnight January 1, 1980.
- No host-end inquiries are permitted for NNF users.
- All price fields must be multiplied by 100 before sending to the host end and divided by 100 while receiving from the host end as the host system processes prices in paisa.
- All  branch/user/order  value  limit  fields  must  be  multiplied  by  (100000  *  100)  before sending to host end and divided by (100000 * 100) while receiving from the host end as the host system processes limits in paisa.

## Guidelines for Programmers

- If your system uses little-endian order, the data types such as UINT, SHORT, LONG and DOUBLE contained in a packet, which occupy more than one byte should be twiddled (byte reversed). Twiddling involves reversing a given number of bytes such that the byte

in 'n' position comes to the first position; the byte in (n -1) position comes to the second position and so on. For example, if the value to be sent is 1A2B (hexadecimal), reverse the bytes to 2B1A. The same applies while receiving messages. So if the value received is 02BC, the actual value is BC02. So twiddle such data types before sending and after receiving to ensure that correct data is sent and received.

## Note:

Twiddling is required because of the variety in endian order -big and little. A big-endian representation has a multi-byte integer written with its most significant byte on the left. A little-endian representation, on the other hand, places the most significant byte on the right. The trading system host end uses big-endian order.

- All alphabetical data must be converted to upper case except password before sending to the host. A combination of alphabet, numbers and special characters are allowed in the  password. More  details  on  password  are  explained  in  later  chapters  in  this document. No NULL terminated strings should be sent to the host end. Instead, fill it with blanks before  sending.  The  strings  received  from  the  host  end  are  padded  with blanks and are not NULL terminated.
- All the structures should be defined in the following manner:
- Items of type char or unsigned char, or arrays containing items of these types, are byte aligned.
- Structures are word aligned.
- All other types of structure members are word aligned.
- All structures are pragma pack 2. Structures of odd size should be padded to an even number of bytes.
- All numeric data must be set to zero (0) before sending to the host, unless a value is assigned to it.
- All reserved fields mentioned, should be mapped to CHAR buffer and initialized to NULL.
- Inside the broadcast packet, the first byte indicates the market type.  Ignore the next 7 bytes. If the first byte is 2 it indicates Futures & Options market. The message header starts from the 9th byte. The remaining portion of the buffer has to be mapped to the broadcast structures mentioned in the document.

## Note:

- The values of all the constants and transaction codes given in the document are listed in Appendix.
- The suffix IN in the transaction codes implies that the request is sent from the TWS to the host end whereas OUT implies that the message is sent from the host end to TWS

## Data Types Used

| Data Type | Size of Bytes | Signed / Unsigned |
| --- | --- | --- |
| CHAR | 1 | Signed |
| UINT | 2 | Unsigned |
| SHORT | 2 | Signed |
| LONG | 4 | Signed |
| UNSIGNED LONG | 4 | Unsigned |
| LONG LONG | 8 | Signed |
| DOUBLE | 8 | Signed and Floating Point |
| BIT | 1 bit | NA |

## Message Header

Each structure is prefaced with a MESSAGE_HEADER which is an interactive header. Some data in the header are fixed whereas some data are variable and set differently for each transaction code. The structure of the Message Header is as follows:

| Structure Name | MESSAGE_HEADER |
| --- | --- |
| Packet Length | 40 bytes |
| Field Name | Data Type |
| TransactionCode | SHORT |
| LogTime | LONG |
| AlphaChar [2] | CHAR |
| TraderId | LONG |
| ErrorCode | SHORT |
| TimeStamp | LONG LONG |
| Packet Length | 40 bytes |
| Field Name | Data Type |
| TimeStamp1 [8] | CHAR |
| TimeStamp2 [8] | CHAR |
| MessageLength | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | Transaction message number. This describes the type of message received or sent. |
| LogTime | This field should be set to zero while sending messages. |
| AlphaChar [2] | This field should be set to the first two characters of Symbol if the structure contains Symbol and Series; otherwise it should be set to blank. |
| TraderId | This field should contain the user ID. |
| ErrorCode | This field should be set to zero while sending messages to the host. In the messages coming from the host, this field describes the type of error. Refer to List of Error Codes in Appendix. |
| TimeStamp | This field should be set to numeric zero while sending to the host. This is used in host end. For transcodes listed in appendix, time in this field will be populated in nanoseconds(from 01-Jan-1980 00:00:00). This time is stamped at the matching engine in the trading system. |
| TimeStamp1 | This field should be set to numeric zero while sending. This is the time the message arrives at the trading system host. In TimeStamp1, time is sent in jiffies from host end. This8 byte data needs to be typecasted as first four bytes into double variable and typecast the other four byte into another double variable. These values need to be used while requesting message area download in the same order. |
| TimeStamp2 | This field should be set to numeric zero while sending to the host. For messages coming from the host, this field contains the machine number from which the packet is coming. |
|  | In TimeStamp2, machine number is sent from host end. |
| MessageLength | This fieldshouldbeset to the length of the entiremessage, including the length of message header while sending to host. |

## Inner Message Header

Each structure in the Data of Update Local Database Data/Message Download Data responses is prefaced with an INNER_MESSAGE_HEADER. The structure of the Inner Message Header is as follows:

| Structure Name | INNER_MESSAGE_HEADER |
| --- | --- |
| Packet Length | 40 bytes |
| Field Name | Data Type |
| TraderId | LONG |
| LogTime | LONG |
| AlphaChar [2] | CHAR |
| TransactionCode | SHORT |
| ErrorCode | SHORT |
| TimeStamp | LONG LONG |
| TimeStamp1 [8] | CHAR |
| TimeStamp2 [8] | CHAR |
| MessageLength | SHORT |

## Broadcast Process Header

The broadcast messages like market open, market close, market in pre-open are prefaced with BCAST_HEADER. Some fields in the header are fixed. The remaining fields are variable and set differently for each transaction code. The structure of the BCAST_HEADER is as follows:

Table 3 BROADCAST_HEADER

| Structure Name | BCAST_HEADER |
| --- | --- |
| Packet Length | 40 bytes |
| Field Name | Data Type |
| Reserved | CHAR |
| LogTime | LONG |
| AlphaChar | CHAR |
| TransCode | SHORT |
| ErrorCode | SHORT |
| BCSeqNo | LONG |
| Reserved | CHAR |
| TimeStamp2 | CHAR |
| Filler2 | CHAR |
| MessageLength | SHORT |

| Field Name | Brief Description |
| --- | --- |
| LogTime | This field should be set to zero while sending to host end. For messages sent from host end this field contains the time when the message was generated by the trading system host. |
| AlphaChar | This field is set to the first two characters of Symbol if the structure contains Symbol and Series; otherwise it is set to blank. |
| TransactionCode | This field contains the transaction message number. This describes the type of message received or sent. |
| ErrorCode | This field contains the error number which describes the type of error. Refer to List of Error Codes in Appendix. |
| BCSeqNo | This field contains BCAST Sequence number of the NSE host end system. The sequence number is not the unique broadcast sequence number as it has eleven set of sequence numbers for normal broadcast and six set of sequence numbers for Fast broadcast each instance of the sequence number is generated by the Individual processes in the host end. It is not an unique sequence number. |
| TimeStamp2 | This field contains the time when message is sent from the host. |
| Filler2 | This field contains the machine number. |
| MessageLength | This field is set to the length of the entire message, including the length of the message header. |

## SEC_INFO

| Structure Name | SEC_INFO |
| --- | --- |
| Packet Length | 12 bytes |
| Field Name | Data Type |
| Symbol | CHAR |
| Series | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Symbol | This field should contain the symbol of a security. |
| Series | This field should contain the series of a security. |

## Error Message

When the Error Code in the Message Header is having nonzero value, ERROR RESPONSE is sent. The Error Message will describe the error received. The structure is as follows:

| Structure Name | ERROR RESPONSE |
| --- | --- |
| Packet Length | 180 bytes |
| Field Name | Data Type |
| MESSAGE_HEADER (Refer Table 1) | STRUCT |
| SEC_INFO (Refer Table 4) | STRUCT |
| Error Message | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Symbol | This field should contain the symbol of a security. |
| Series | This field should contain the series of a security. |
| ErrorMessage | Stores the error message. Refer to List of Error Codes in Appendix. |

## Invalid Message Length Response Transcode

If a user sends a request with improper message length, then the host will send INVALID_MSG_LENGTH_RESPONSE transcode (2322) in response. This check is not specific to the type of user and may occur for both NEAT and NNF Users.

Message length may vary from one request to the other. For example, for an Order request the Host end expects a request with the message length of 214 bytes. If the order request has any message length other than 214 bytes, it will send the above mentioned transcode with the error code -ERR_INVALID_MSG_LENGTH (defined in the error codes table previously). Host sends the same incoming packet structure in response but with transcode populated as

INVALID_MSG_LENGTH_RESPONSE (2322) and error code populated as ERR_INVALID_MSG_LENGTH.

Kindly refer to individual transocde for their corresponding message length

## Communication Network Connections for NNF Users

There are two types of virtual circuit connections used to communicate with the host end. One is the Interactive Virtual Circuit ID (VCID) and the other is the Broadcast Circuit ID (BCID).

Interactive VCID follows a bidirectional path between the NNF and NEAT to host end. All the interactive / request messages and its respective response follow through this channel. Even the unsolicited  message  such  as  trade  message  flows  from  exchange  (host  end)  to  the  trader terminal through this channel.

Standard implementation of TCP/IP protocol exists on the exchange's infrastructure as a result of which default features like IP fragmentation, no QoS etc. continue to be enabled and available for use by members. Default IP fragmentation a valid feature in the TCP/IP protocol works at message  level  and  usage  of  same  by  one  member  connection  will  not  block  or  impact  the messages of other member connections.

BCID  follows  a  unidirectional  path  which  is  from  the  host  end  to  the  NFF  /  NEAT.  All  the broadcast  data  are  transmitted  through  this  broadcast  circuit  from  the  host  end  for  all  the traders. Since this is a one way connection, the data flow is always from the exchange (host end) to the trader terminal.

## Member Guide to the Gateway Router Functionality

Currently Exchange publishes a list of gateway servers (NET) in the respective segments to which members can connect. Members have the choice of connecting to any of the gateway servers.

However,  the  members  have  represented  that  they  are  required  to  try  to  login  on  multiple gateway  server  sequentially  before  they  are  able  to  successfully  login  on  the  Exchange  for trading activity. Thus, valuable time is lost by the member for trying to access the Exchange. The same is more severe during re-login / disconnections faced by the members.

In order to address these queries the Gateway Router Functionality has been proposed to be implemented.

- It  is  now  proposed  that  members will  first  connect  to  a  gateway  router  server  in  the respective segment details of which will be published by the Exchange.
- The gateway router server will decide which gateway server is available for the member and will accordingly provide the details of the allocated gateway server to the member through the response message.
- After getting the response message the member will need to connect to the allocated gateway server.

Thus,  the  process  of  allocating  gateway  servers  becomes  Exchange  determined  and  highly simplified for the member.

The gateway router will decide the gateway server for the member for each trading day in the following manner:

- The gateway router will maintain the used capacity of each gateway server. The gateway router will allocate least used gateway server (according to capacity). The capacity is based on the no. of messages allotted for each Box Id.
- If all gateway servers have similar used capacity then a gateway server will be randomly allocated by the gateway router server.
- Once a member has been provided session key with gateway server details by gateway router server, the member is expected to connect and login to the allocated gateway server at any time during rest of the trading day.
- If the member gets logged off from the allocated gateway server, then the member has to request the gateway router server for getting new session key and gateway server details.

- A member will be directed to the same gateway server by the gateway router server, once it has been allocated for the trading day.
- Though the user will get directed to the same gateway, the user must ask the gateway router  for  getting  the  gateway  details  and  session  key  as  the  old  session  key  will  be unique for that particular session and is cleaned up from the gateway once the user gets logged off.
- Also, if the gateway has a failure during the day, the user will be allocated a new gateway server. This will be done transparently for the user by the gateway router server.

At the end of each trading day the gateway router server will clean up the used capacity, and will have the same capacity (full capacity) available for all gateway servers for the next day.