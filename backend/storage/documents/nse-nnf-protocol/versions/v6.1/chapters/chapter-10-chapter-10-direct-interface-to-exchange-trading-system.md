---
title: "Chapter 10 Direct Interface to Exchange Trading System"
chapter_number: 10
page_range: "156-165"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 10 Direct Interface to Exchange Trading System


This chapter describes how member systems can directly connect to NSE for trading, while using existing formats of business messages from NNF API documents.

To directly connect to NSE for trading, member systems will have carry out the changes specified herein.

## Message Formats

Change to packet format

| Length | Sequence | Checksum(MD5) for | Message Data |
| --- | --- | --- | --- |
| (2 bytes) | number | Message data | (Variable length) |
|  | (4 bytes) | (16 bytes) |  |

- Max length will be the predefined value of 1024 bytes.

Length = size of length field (2 bytes) +

size of sequence number field (4 bytes) +

size of the checksum field (16 bytes) +

size of Message data (variable number of bytes as per the transcode)

- For  members  connecting  on  encrypted  mode,  the  sequence  number  received  in  the request  message  for  Order  related  interactive  messages  will  be  echoed  back  in  the sequence number field of corresponding response messages. It is recommended to send an incremental sequence number.
- For  members  connecting  on  non-encrypted  mode,  there  is  no  change  in  sequence number. Sequence number will be sent as 0 in all the packets.
- Message data will be of variable length
- The checksum algorithm used will be MD5. Checksum is applied only on the Message data field and not on the entire packet.
- For more details on MD5 refer: RFC 1321 (rfc1321) - The MD5 Message-Digest Algorithm ()
- In case checksum is not matched, packet will be dropped at Exchange end

## Change to structure for 'MESSAGE_HEADER'

## MESSAGE_HEADER

| Structure Name | MESSAGE_HEADER |
| --- | --- |
| Packet Length | 40 bytes |
| Field Name | Data Type |
| Transaction Code | SHORT |
| LogTime | LONG |
| AlphaChar | CHAR |
| User Id | LONG |
| ErrorCode | SHORT |
| Timestamp | LONG LONG |
| TimeStamp1 | CHAR |
| TimeStamp2 | CHAR |
| MessageLength | SHORT |

## Connecting to NSE for Trading

## Sequence to be followed by the member for login

- Member to connect (TCP/IP, SSL connection) to the IP and port provided by the exchange and send the GR_REQUEST using OpenSSL (Version 1.1.1) library calls with TLS versions 1.3 (TLS1_3_VERSION). Refer annexure for Encryption/Decryption.
- Exchange will send the GR_RESPONSE to the member containing the IP address, Port and the Session key and cryptographic key  & cryptographic IV (Initialization Vector) on SSL connection. If there is any error, then ErrorCode field in MESSAGE_HEADER will be populated with relevant error code in the GR_RESPONSE.
- Member applications will then make a new TCP connection with the allocated Gateway server (IP and port provided in the GR_RESPONSE) and send SECURE_BOX_REGISTRATION_REQUEST. BoxID (received in GR_RESPONSE) is to be populated in SECURE_BOX_REGISTRATION_REQUEST

- Exchange will send the SECURE_BOX_REGISTRATION_RESPONSE. If there is any error, then ErrorCode field in MESSAGE_HEADER will be populated with relevant error code in the SECURE_BOX_REGISTRATION_RESPONSE and the Box connection will be terminated.
- If  there  is  no  error  in  SECURE_BOX_REGISTRATION_RESPONSE,  member  should  do encryption  and  decryption  initialization  to  create  encryption  and  decryption  contexts (Please refer annexure). This initialization should be done only once. Once initialized, all further  messages between member application and allocated Gateway server will be encrypted and decrypted using same encryption and decryption contexts respectively. Further member should send the BOX_SIGN_ON_REQUEST_IN. BoxID, BrokerID and Session key (received in GR_RESPONSE) is to be populated in BOX_SIGN_ON_REQUEST_IN. MD5 Algorithm to be performed on plain messages. That means, while sending the messages to Trading system, MD5 is to be performed first and then encryption. Encrypted message length + 22 (sizeof(Header)) will have to be written in  first  2  bytes  of  header,  Sequence  Number in next 4 bytes and MD5 value (of plain message)  will  be  written  in  last  16  bytes  of  Header  and  the  header  will  have  to  be prepended to the encrypted message. This message will be sent out to Trading System. While receiving the messages from Trading System, decryption should be done first and then MD5 is to be applied on decrypted buffer. Decryption should be done on message excluding first 22 bytes of header.
- Exchange  will  send  the  BOX_SIGN_ON_REQUEST_OUT.  If  there  is  any  error,  then ErrorCode field in MESSAGE_HEADER will be populated with relevant error code in the BOX_SIGN_ON_REQUEST_OUT and the Box connection will be terminated. Note: Multiple BOX_SIGN_ON_REQUEST_IN requests on a successfully established box
- connection will lead to the existing box connection termination.
- Once a connection for a particular Box ID is established, all users linked with this Box ID can login using the SIGNON_IN structure. Refer [Chapter 3](#chapter-3-logon-process) for login request and response using SIGNON_IN structure.

- For further flow refer to existing protocol defined in [Chapter 3](#chapter-3-logon-process) of Protocol Document

## Gateway Router Request

| Structure Name | MS_GR_REQUEST |
| --- | --- |
| Packet Length | 48 bytes |
| Transaction Code | GR_REQUEST (2400) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header structure) | STRUCT |
| Box ID | SHORT |
| BrokerID | CHAR |
| Filler | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Transaction Code | This field is the part of Message Header . The transaction code is 2400. |
| Box ID | Exchange provided Box ID to be used for this connection |
| BrokerID | This field should contain the trading member ID |

## Gateway Router Response

| Structure Name | MS_GR_RESPONSE |
| --- | --- |
| Packet Length | 124 bytes |
| Transaction Code | GR_RESPONSE(2401) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header structure) | STRUCT |
| Box ID | SHORT |
| BrokerID | CHAR |
| Filler | CHAR |
| IP Address | CHAR |
| Port | LONG |
| Session Key | CHAR |
| Packet Length | 124 bytes |
| Transaction Code | GR_RESPONSE(2401) |
| Field Name | Data Type |
| Cryptographic Key | CHAR |
| Cryptographic IV (Initialization Vector) | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Transaction Code | This field is the part of Message Header. The transaction code is 2401 |
| Error Code | This field is the part of Message Header. Error Code will be set if the query is unsuccessful. Refer to List of Error Codes in Appendix. |
| Box ID | Exchange provided Box ID used for this connection |
| BrokerID | This field should contain the trading member ID |
| IP Address | IP address assigned by exchange |
| Port | Port Number given by exchange |
| Session Key | Session key to be used for authentication |
| Cryptographic Key | Cryptographic key for both the encryption and decryption of all messages betweenmemberapplicationand allocated Gateway Server. |
| Cryptographic IV (Initialization Vector) | Cryptographic IV (Initialization Vector) for both the encryption and decryption of all messages between member application and allocated Gateway Server. |

## Secure Box Registration Request

## SECURE_BOX_REGISTRATION_REQUEST

| Structure Name | MS_ SECURE_BOX_REGISTRATION_REQUEST_IN |
| --- | --- |
| Packet Length | 42 bytes |
| Transaction Code | SECURE_BOX_REGISTRATION_REQUEST_IN (23008) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header | STRUCT |
| BoxId | SHORT |

| Field Name | Brief Description |
| --- | --- |
| Transcode | This field is the part of Message Header. The transaction code is 23008 |
| BoxId | Exchange provided Box ID to be used for this connection |

## Secure Box Registration Response

## SECURE_BOX_REGISTRATION_RESPONSE

| Structure Name | MS_ SECURE_BOX_REGISTRATION_RESPONSE_OUT |
| --- | --- |
| Packet Length | 40 bytes |
| Transaction Code | SECURE_BOX_REGISTRATION_REQUEST_IN (23009) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header structure) | STRUCT |

| Field Name | Brief Description |
| --- | --- |
| Transcode | This field is the part of Message Header. The transaction code is 23009 |
| ErrorCode | This field is the part of Message Header. Error Code will be set if the query is unsuccessful. Refer to List of Error Codes in Appendix |

## Box Sign on Request

## MS_BOX_SIGN_ON_REQUEST_IN

| Structure Name | MS_BOX_SIGN_ON_REQUEST_IN |
| --- | --- |
| Packet Length | 60 bytes |
| Transaction Code | BOX_SIGN_ON_REQUEST_IN(23000) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header structure) | STRUCT |
| BoxId | SHORT |
| BrokerID | CHAR |
| Reserved | CHAR |
| SessionKey | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Transcode | This field is the part of Message Header.The transaction code is 23000 |
| BoxId | Exchange provided Box ID to be used for this connection |
| BrokerID | This field should contain the trading member ID |
| SessionKey | Session key received in GR_RESPONSE(2401) |

## Box Sign on Response

## MS_BOX_SIGN_ON_REQUEST_OUT

| Structure Name | MS_BOX_SIGN_ON_REQUEST_OUT |
| --- | --- |
| Packet Length | 52 bytes |
| Transaction Code | BOX_SIGN_ON_REQUEST_OUT(23001) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Message Header structure) | STRUCT |
| BoxId | SHORT |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Transaction Code | This field is the part of Message Header. The transaction code is 23001 |
| Error Code | This field is the part of Message Header. Error Code will be set if the query is unsuccessful. Refer to List of Error Codes in Appendix. |
| BoxId | Exchange provided Box ID used for this connection |

## SignOn In

Members systems must send other messages immediately using existing protocol defined in [Chapter 3](#chapter-3-logon-process)  of  Protocol  Document.  A  few  fields  in  the  Logon  message  have  to  be  populated differently for direct connection:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is MS_SIGNON (2300). |
| ShowIndex | 'T' = to use Trimmed -NNF protocol with Total Traded Quantity and Value Data Type Change Note: Only Trimmed-NNF protocol is supported by Direct Interface |

## How to Logoff?

To logoff from the exchange trading system, there is no change and use the existing protocol defined in [Chapter 3](#chapter-3-logon-process) of protocol document.

## Heartbeat exchange

Member systems must exchange heartbeat signals with exchange trading system during periods of  inactivity.  Trading  Host  will  consider  the  member  system  as  inactive  after  missing  two heartbeats in succession and disconnect the socket connection. Heartbeats will carry following data in MessageData segment of the message. Heartbeat is to be sent only if there is inactivity for 30 seconds. The format is MESSAGE_HEADER with following detail.

## HEARTBEAT

| Structure Name | HEARTBEAT |
| --- | --- |
| Packet Length | 40 bytes |
| Transaction Code | 23506 |
| Field Name | Data Type |
| MESSAGE HEADER | STRUCT |

## Recovering from disconnections

If member system detects a loss of TCP connection with the exchange trading system, please perform the same operations for starting a fresh login given above.

## Performing Trading activities

Once  authenticated  connection  is  successfully  established,  member  systems  can  send  any business message to exchange as described in NNF protocol documents. Care should be taken to use MESSAGE_HEADER described in this chapter wherever applicable in front of business messages.

## Connection Termination

When  connection is terminated by exchange,  BOX_SIGN_OFF  (20322)  message  with appropriate error code will be sent.

## Box Sign Off

| Structure Name | MS_BOX_SIGN_OFF |
| --- | --- |
| Packet Length | 42 bytes |
| Transction code | BOX_SIGN_OFF |
| Field Name | Data Type |
| MESSAGE HEADER | STRUCT |
| BoxId | SHORT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | This field is the part ofMessage Header . The transaction code is 20322. |
| Error Code | This field is the part of Message Header.Error Code will be set if the query is unsuccessful. Refer to List of Error Codes in Appendix. |
| BoxId | Exchange provided Box ID used for this connection |