---
title: "Chapter 11 Exception Handling"
chapter_number: 11
page_range: "165-168"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 11 Exception Handling


## Introduction `[p.165]`

NSE's trading system constitutes of multiple matching engines (streams). Each stream hosts a range of contracts on which trading is allowed. In case of an exception single/multiple streams will get impacted. It is necessary that relevant information is disseminated in such events so that necessary action can be taken at member's end to bring their systems into a consistent state. Exception handling: `[p.165]`

- At the start of the outage message will be sent on broadcast channel with StreamNumber and status as 1 (start of outage) and members may get disconnected from the exchange (Member can also receive this message through journal download).
- On receiving message in step 1, members should clear outstanding orders at their end for the respective streams. Exchange would also cancel all the outstanding orders and no cancellation messages will be sent for these orders.
- Once exchange has restored the stream, message will be sent on broadcast channel with StreamNumber and status as 0 (end of outage) (Member can also receive this message through journal download).
- On receiving the message in step 3, Members can reconnect to the exchange in case they have got disconnected in step 1.

## Message structure `[p.165]`

Message structure is as follows:

*Table (p.165)*

| Structure Name | MS_BCAST_CONT_MESSAGE |
| --- | --- |
| Packet Length | 244 bytes |
| Transaction Code | BCAST_CONT_MSG (5294) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| StreamNumber | SHORT |
| Status | SHORT |
| Reserved | CHAR |

The following table provides details of the various fields present in above Message structure. `[p.166]`

*Table (p.166)*

| Field Name | Brief Description |
| --- | --- |
| StreamNumber | 0 - All streams are impacted or impacted stream number (eg 1, 2, 3, 4…) |
| Status | 1 - Start of outage 0 - End of outage |
| Reserved | Reserved for future use |

## DR 45 Initiative `[p.166]`

NSE trading system provides high availability of its services by having identical setup available at NSE DR Site. `[p.166]`

Please find below list of point to be considered in case of switchover to DR site `[p.166]`

- Members will have to reconnect to trading system, as they will be disconnected once the primary site is unavailable
- Member should continue to use existing connectivity parameter for connecting to NSE trading system at DR site
- Member on reconnecting at DR site will receive start of outage message as a part of journal download.

The message sent in the following format

(MS_BCAST_CONT_MESSAGE) (refer to Exception handling)

- Exchange shall not carry forward outstanding orders from primary site to DR site and no cancellation messages will be sent for these orders. Accordingly members are advised to clear outstanding orders at their end.
- Exchange  shall  publish  streamwise  trade  number  of  the  last  trade  (Exchange  trade number) available at DR site. Member may note that streamwise trades upto the last trade number shall only be considered.
- Exchange shall broadcast streamwise last trade number.
- The message sent in the following format

(MS_TRADER_INT_MSG) (refer to Interactive/broadcast messages sent from control)

- Member shall be able to perform trade modification or trade cancellation on trades which are available at DR site.
- In case member is connected after switchover, they will receive end of outage message. The message sent in the following format

(MS_BCAST_CONT_MESSAGE) (refer to Exception handling)

In case member is not connected, they will receive this message as a part of journal download post reconnecting to NSE trading system at DR site. `[p.167]`

The message sent in the following format

(MS_BCAST_CONT_MESSAGE) (refer to Exception handling)

- Journal download information before switchover shall not be available ,
- Used limit value in User Order Value Limit (UOVL) and Branch Order Value Limit (BOVL) will be reset to zero after switchover to DR site.