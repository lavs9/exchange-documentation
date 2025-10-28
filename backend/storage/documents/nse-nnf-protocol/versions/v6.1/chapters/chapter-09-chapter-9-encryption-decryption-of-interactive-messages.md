---
title: "Chapter 9 Encryption Decryption of Interactive Messages"
chapter_number: 9
page_range: "153-156"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 9 Encryption Decryption of Interactive Messages


## Background

NSE provides a pan-India trading platform to its trading members. Members connect to this platform  using  client-server  architecture.  Connections  are  made  using  TCP/IP  protocol  and messages  are  exchanged  using  NSE's  own  messaging  format  (also  known  as  NNF  f ormat). Messages  exchanged  are  binary  in  nature.  Currently  these  messages  are  not  encrypted, exchange now proposes to encrypt them. This section of document provides an overview of the implementation approach that exchange has finalized, for doing the same.

## Overview

Interactive messages which are exchanged between member applications and the exchange today use the NNF protocol published by exchange. As for every trading platform, similarly in this case as well availability, reliability and speed are the key considerations in the protocol. In order to enhance the security posture, it is now proposed to encrypt these messages on an endto-end basis. While encryption of messages within member environment towards their clients will  need  to  be  done  by  respective  members. For the communication that happens between member  applications  and  exchange,  a  few  changes  into  NNF  protocol  are  being  proposed. Changes have been envisaged considering the following attributes.

- (i) Secure communication
- (ii) Availability
- (iii) Reliability
- (iv) Speed

Minimal changes in member applications

## Proposed Methodology

Exchange  proposes  a  combination  of  TLS  1.3  security  protocol  and  AES-256  bits-based symmetric encryption approach. Following is an overview.

1 st  Step: Member applications will connect initially to Exchange Gateway Router server using TCP  with  TLS  1.3  security  protocol  and  will  receive  unique  session  key  from  the  Exchange through the secured connection.

2 nd  Step: Member applications will then connect to allocated Exchange Gateway server through TCP,  and each  and  every  message  will  be  encrypted/decrypted  using  the  same  session key (symmetric cryptography AES 256 bits GCM mode) at both member end and Exchange end.

## Below are the details of the methodology

- (i) Exchange will generate self-signed CA certificates on periodic basis. CA certificate will remain common for all members and shall be distributed as and when generated via extranet.
- (ii) On a daily basis when member applications need to connect to trading platform they will need to do the following
- Member applications will connect to Exchange Gateway Router server on TCP using  TLS  1.3  security  protocol.  As  part  of  TLS  1.3  security  protocol,  it  is recommended that member applications verify Gateway Router server authenticity using the CA certificate provided by the Exchange.
- GR request  and  GR  response  messages  will  be  sent  and  received  by  member applications using TLS 1.3 security protocol.
- A unique 32-byte session key will be provided to member applications as part of GR response message.
- (iii) Post successful communication with Gateway router server, member applications will establish a new TCP connection with the allocated gateway server of Exchange. The  first  message  after  connecting  through  TCP  will  be  a  non-encrypted  special registration  message  (SECURE_BOX_REGISTRATION_REQUEST)  to  indicate  that member application is using encryption. All the messages, after the first message, that are exchanged on this connection from both sides (member applications and Exchange) will be encrypted and decrypted using the 32-byte session key that was

provided from Exchange at the time of Gateway Router handshake. GCM mode of symmetric  cryptography  AES  256  bits  will  be  used  by  member  applications  and Exchange.

- (iv) In case of new login or disconnection and then re login, the above-mentioned steps will be repeated

We envisage minimal changes in member applications. Sample function calls which could be considered for encryption-decryption for the above proposed approaches are provided in annexure for Encryption/Decryption.

## Disconnection on MD5 Checksum failure

- (i) If member is connected on encrypted channel and MD5 checksum fails then a box sign off message with error code (19031) will be sent to member before disconnection.
- (ii) If member is connected on non-encrypted channel and MD5 checksum fails then there will be no change in the behavior. The packet will be dropped by Trading system and continue reading the next packet.