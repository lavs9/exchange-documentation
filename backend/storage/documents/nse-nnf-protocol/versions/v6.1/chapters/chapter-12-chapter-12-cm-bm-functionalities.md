---
title: "Chapter 12 CM-BM Functionalities"
chapter_number: 12
page_range: "168-244"
document: "TP_CM_Trimmed_NNF_PROTOCOL_6.1_1"
---

# Chapter 12 CM-BM Functionalities


## Introduction

This section describes about functionalities available to corporate manager and branch manager users for risk management and admin related activities.

## Branch Order Limit

Corporate manager can set limits on total value of buy/sell orders entered by specific branch within trading member's firm.

Branch order value limit will be applicable to users available in the branch.

## Branch Order Value Limit Update Request

The format of the message is as follows:

| Structure Name | BRANCH_ORDER_VAL_LIMIT_UPDATE |
| --- | --- |
| Packet Length | 104 bytes |
| Transaction Code | BRANCH_ORDER_VAL_UPDATE_IN (5716) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| BrokerId | CHAR |
| Reserved | CHAR |
| Branch | SHORT |
| BRANCH_LIMIT | STRUCT |

| Structure Name | BRANCH_LIMIT |
| --- | --- |
| Packet Length | 32 bytes |
| Field Name | Data Type |
| BranchBuyValueLimit | DOUBLE |
| Reserved | CHAR |
| BranchSellValueLimit | DOUBLE |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BRANCH_ORDER_VAL_LIMIT_UPDATE_IN (5716) |
| BrokerId | This field should contain the Trading Member ID |
| Branch | This field should contain the branch number for which limit to be set |
| BranchBuyValueLimit | This field should contain branch buy limit to be set (in lakhs) Valid values: 0 to 9999999.99 This is to be multiplied by (100000*100) before sending to the trading system host |
| BranchSellValueLimit | This field should contain branch sell limit to be set (in lakhs) Valid values: 0 to 9999999.99 This is to be multiplied by (100000*100) before sending to the trading system host |

## Branch Order Value Limit Update Response

On successful branch limit updates, exchange will send Branch Order Limit Update Response to

- -Corporate manager
- -Branch manager(of branch id mentioned in request)

The structure is sent as follows:

BRANCH_ORDER_VAL_LIMIT_UPDATE (Refer to Branch Order Value Limit Request structure)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BRANCH_ORDER_LIMIT_UPDATE_OUT (5717) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then user order value limit update is done successfully. |

If branch order value limit update request is rejected by trading system, then ERROR RESPONSE (Refer  Table  5)  packet  will  be  sent  to  user  who  has  sent  limit  update  request.  Reason  for rejection will be given by ErrorCode in the header.

## User Order Limit

Corporate manager can set limit on total value of buy/sell orders entered by specific user within trading member's firm. Similarly, Branch manager can set limit on total value of buy/sell orders entered by specific user within the branch.

## User Order Value Limit Update Request

The format of the message is as follows:

| Structure Name | USER_ORDER_VAL_LIMIT_UPDATE |
| --- | --- |
| Packet Length | 142 bytes |
| Transaction Code | USER_ORDER_VAL_UPDATE_IN (5719) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| BrokerId | CHAR |
| Reserved | CHAR |
| Branch | SHORT |
| Reserved | CHAR |
| UserId | LONG |
| USER_LIMITS | STRUCT |

| Structure Name | USER_LIMITS |
| --- | --- |
| Packet Length | 64 bytes |
| Field Name | Data Type |
| Reserved | CHAR |
| UserOrderBuyValueLimit | DOUBLE |
| Reserved | CHAR |
| UserOrderSellValueLimit | DOUBLE |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_ORDER_LIMIT_UPDATE_IN (5719) |
| BrokerId | This field should contain the Trading Member ID |
| Branch | This field should contain the branch number of user for which limit to be set |
| UserId | This field should contain the user ID of the user for which limit to be set |
| UserOrderBuyValueLimit | This field should contain user buy limit to be set (in lakhs) Valid values: 0 to 9999999.99 This is to be multiplied by (100000*100) before sending to the exchange trading system |
| UserOrderSellValueLimit | This field should contain user sell limit to be set (in lakhs) Valid values: 0 to 9999999.99 This is to be multiplied by (100000*100) before sending to the exchange trading system |

## User Order Value Limit Update Response

On successful user limit updates, exchange will send User Order Limit Update Response to

- -user who has sent limit update request
- -user for which limit has been set
- -Corporate manager (if branch manager tries to update limit for user within branch).

The structure is sent as follows:

USER_ORDER_VAL_LIMIT_UPDATE (Refer to User Order Value Limit Request structure)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_ORDER_LIMIT_UPDATE_OUT (5720) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then user order value limit update is done successfully. |

If user order value limit update request is rejected by trading system, then ERROR RESPONSE (Refer Table 5) packet will be sent to user who has sent limit update request. Reason for rejection will be given by ErrorCode in the header.

## Order Limit

This functionality provides facility to specify maximum quantity per order and maximum value per order that user can enter in order entry/order modification request.

Corporate manager can set limit on order quantity and order value of an order, entered by user within trading member's firm. Similarly Branch manager can set limit on order quantity and order value of an order entered by user within the branch.

## Order Limit Update Request

The format of the message is as follows:

| Structure Name | ORDER_LIMIT_UPDATE |
| --- | --- |
| Packet Length | 68 bytes |
| Transaction Code | DEALER_LIMIT_UPDATE_IN (5721) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| BrokerId | CHAR |
| Reserved | CHAR |
| UserId | LONG |
| OrderQtyLimit | DOUBLE |
| OrderValLimit | DOUBLE |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is DEALER_LIMIT_UPDATE_IN (5721) |
| BrokerId | This field should contain the Trading Member ID |
| UserId | This field should contain the User ID for which limit to be set |
| QuantityValLimit | This field should contain Order Quantity limit to be Set Valid values : 1 to 999999999 |
| OrderValLimit | This field should contain Order Limit to be Set in lakhs Valid values: 0 to 9999999.99 This is to be multiplied by (100000*100) before sending to the trading system host |

## Order Limit Update Response

On successful order limit updates, exchange will send Order Limit Update Response to

- -user who has sent limit update request
- -user for which limit has been set
- -Corporate manager (if branch manager tries to update limit for user within branch).

The structure is sent as follows:

ORDER_LIMIT_UPDATE (Refer to Order Limit Update_Request structure)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is DEALER_LIMIT_UPDATE_IN (5722) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then order limit update is done successfully. |

If order limit update request is rejected by trading system, then ERROR RESPONSE (Refer Table 5) packet will be sent to user who has sent limit update request. Reason for rejection will be given by ErrorCode in the header.

## Reset UserId

This functionality enables the Corporate Manager to terminate the active session for users within trading member's firm. Similarly, Branch Manager can terminate the active session for users within the branch.

## User Reset Request

The format of the message is as follows:

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is RESET_USERID_REQ (5723). |
| UserId | This field should contain User ID of user to be reset. This field accepts numbers only. |

## User Reset Response

In below mentioned scenarios, exchange trading system will send User Reset Response to user who has sent user reset request,

- -On Successful user session reset

The structure is sent as follows:

SIGNON IN (Refer to Logon Structure in [Chapter 3](#chapter-3-logon-process))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is RESET_USERID_RESP (5724). |
| ErrorCode | This field contains error code. If error code field value is zero (0) then reset user is done successfully. |

If User Reset request is rejected by exchange trading system, then ERROR RESPONSE (Refer Table 5) packet will be sent to user who has sent user reset request. Reason for rejection will be given by ErrorCode in the header.

## Reset Password

Corporate manager can reset password of users within trading member's firm.

- The user's password will reset to 'Neat@CM1' i.e. default password.
- User whose password is to be reset should be 'Disabled' or 'Inactive'
- On resetting the password of disabled user, status of the user will be changed to inactive.
- The Corporate Manager will not be allowed to reset his own password.

## User Password Reset Request

The format of the message is as follows:

| Structure Name | RESET_PASSWORD |
| --- | --- |
| Packet Length | 58 bytes |
| Transaction Code | RESET_PASSWORD_IN (5738) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is RESET_PASSWORD_IN (5738) |
| UserId | This field should contain user id for which password to be reset |

## User Password Reset Response

In below mentioned scenarios, exchange trading system will send User password reset response to user who has sent user password reset request

- -On Successful user password reset
- -If user password reset request is rejected by exchange trading system (Reason for rejection will be given by ErrorCode in the header.)

The structure is sent as follows:

RESET_PASSWORD (Refer to User Password Reset Request structure)

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is RESET_PASSWORD_OUT (5739) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then reset password for user is done successfully. If error code field value is non-zero, then reset password request for user is rejected. Refer to List of Error Codes in Appendix. |

## Cancel On Logout (COL) Status

This functionality if enabled provides facility to traders to cancel all their outstanding orders when user logs off from exchange trading system.

Corporate manager can enable/disable COL status for the users within trading member's firm.

## User COL Status Update Request

The format of the message is as follows:

| Structure Name | COL_ USER_STATUS_CHANGE_REQ |
| --- | --- |
| Packet Length | 52 bytes |
| Transaction Code | COL_USER_STATUS_CHANGE _IN (5790) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| ColoUserBit | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is COL_USER_STATUS_CHANGE_IN (5790) |
| UserId | This field should contain user id for which COL status to be set |
| ColoUserBit | This field should contain user's COL status to be set. It should contain one of the following values. • '0' for Disable COL status • '1' for Enable COL status |

## User COL Status Update Response

In below mentioned scenarios, exchange trading system will send User COL Status Update response to user who has sent status update request

- -On Successful COL status updates
- -If User COL status update request is rejected by exchange trading system (Reason for rejection will be given by ErrorCode in the header.)

The structure is sent as follows:

| Structure Name | COL_USER_STATUS_CHANGE_RESP |
| --- | --- |
| Packet Length | 46 bytes |
| Transaction Code | COL_USER_STATUS_CHANGE _OUT (5791) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| ColoUserBit | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is COL_USER_STATUS_CHANGE_OUT (5791) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then user's COL status update is done successfully. If error code field value is non-zero, then request for user's COL status update is rejected. Refer to List of Error Codes in Appendix. |
| UserId | This field will contain user id for which COL status is set |
| ColoUserBit | This field will contain user's COL status is set. It will contain one of the following values. • '0' for Disable COL status • '1' for Enable COL status |

Also, in case of successful COL status update, trading system will send interactive message to

- -user who has sent status update request
- -user for which status has been updated
- -Branch manager (if the status update is done for the dealer under his branch).
- -Other Branch managers of same branch if status update is done for Branch manager.

The message sent will be of the following format:

MS_TRADER_INT_MSG (Refer to Interactive/Broadcast Messages Sent from Control)

The following table provides the details of the various fields present in the MS_TRADER_INT_MSG Structure.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is CTRL_MSG_TO_TRADER (5295). |
| BroadCastMessage Length | This field contains Message Length |
| BroadCastMessage | This field contains actual Message |

## Trade Cancellation Status

Corporate manager can enable/disable Trade Cancellation Status for the users within trading member's firm.

If Trade Cancellation status for user is enabled, then user will be allowed to send Trade cancellation request to exchange trading system.

## User TRD-CXL Status Update Request

The format of the message is as follows:

| Structure Name | USER_ TRD_MOD_CXL_CHANGE_REQ |
| --- | --- |
| Packet Length | 52 bytes |
| Transaction Code | USER_ TRD_MOD_CXL_CHANGE _IN (5792) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| TrdModCxlBit | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_TRD_MOD_CXL_CHANGE_IN (5792) |
| AlphaChar | To identify status change for Trade Cancellation, AlphaChar values to be set as below • AlphaChar[0] = 'T' |
|  | • AlphaChar[1] = 'X' |
| UserId | This field should contain user id for which trade cancel status to be set. |
| TrdModCxlBit | This field should contain user's Trade Cancellation Status to be set. It should contain one of following values, • 'Y' for Enable Trade Cancellation Status • 'N' for Disable Trade Cancellation Status |

## User TRD-CXL Status Update Response

On successful Trade CXL status updates, exchange trading system will send User TRD-CXL Status Update Response to the user who has sent status update request as well as to the user for which TRD-CXL status has been set.

If User TRD-CXL status update request is rejected by exchange trading system, then status update response packet will be sent to user who has sent status update request. Reason for rejection will be given by ErrorCode in the header.

The structure is sent as follows:

| Structure Name | USER_TRD_MOD_CXL_CHANGE_RESP |
| --- | --- |
| Packet Length | 46 bytes |
| Transaction Code | USER_TRD_MOD_CXL_CHANGE _OUT (5793) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| TrdModCxlBit | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_TRD_MOD_CXL_CHANGE_OUT (5793) |
| ErrorCode | This field contains error code. |
|  | If error code field v alue is zero (0) then user's Trade Cxl status update is done successfully. If error code field value is non-zero, then request for user's Trade Cxl status update is rejected. Refer to List of Error Codes in Appendix. |
| UserId | This field will contain user id for which trade cancel status is set. |
| TrdModCxlBit | This field will contain user's Trade Cancellation Status is set. It will contain one of following values, • 'Y' for Enable Trade Cancellation Status • 'N' for Disable Trade Cancellation Status |

- -user who has sent status update request
- -user for which status has been updated
- -Branch manager (if the status update is done for the dealer under his branch).
- -Other Branch managers of same branch if status update is done for Branch manager

The message sent will be of the following format: MS_TRADER_INT_MSG (Refer to Interactive/Broadcast Messages Sent from Control)

The following table provides the details of the various fields present in the MS_TRADER_INT_MSG Structure.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is CTRL_MSG_TO_TRADER (5295). |
| BroadCastMessage Length | This field contains Message Length |
| BroadCastMessage | This field contains actual Message |

## Trade Modification Status

Corporate manager can enable/disable Trade Modification Status for the users within trading member's firm.

If Trade Modification status for user is enabled, then user will be allowed to send Trade modification request to exchange trading system.

## User TRD-MOD Status Update Request

The message sent will be of the following format:

USER_ TRD_MOD_CXL_CHANGE_REQ ( Refer to User TRD-CXL Status Update Request structure )

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_TRD_MOD_CXL_CHANGE_IN (5792) |
| UserId | This field should contain user id for which trade modification status to be set. |
| TrdCxlBit | This field should contain user's Trade Modification Status to be set. It should contain one of following values, • 'Y' for Enable Trade Modification Status • 'N' for Disable Trade Modification Status |

## User TRD-MOD Status Update Response

On successful Trade MOD status updates, exchange trading system will send User TRD-MOD Status Update Response to the user who has sent status update request as well as to the user for which TRD-MOD status has been set.

If User TRD-MOD status update request is rejected by exchange trading system, then status update response packet will be sent to user who has sent status update request. Reason for rejection will be given by ErrorCode in the header.

The message sent will be of the following format:

USER_ TRD_MOD_CXL_CHANGE_RESP ( Refer to User TRD-CXL Status Update Response structure )

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_TRD_MOD_CXL_CHANGE_OUT (5793) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then user's Trade Mod status update is done successfully. If error code field value is non-zero, then request for user's Trade Mod status update is rejected. Refer to List of Error Codes in Appendix. |
| UserId | This field will contain user id for which trade modification status is set. |
| TrdModCxlBit | This field will contain user's Trade Modification Status is set. It will contain one of following values, • 'Y' for Enable Trade Modification Status • 'N' for Disable Trade Modification Status |

Also, in case of successful TRD-MOD status update, trading system will send interactive message to

- -user who has sent status update request
- -user for which status has been updated
- -Branch manager (if the status update is done for the dealer under his branch).
- -Other Branch managers of same branch if status update is done for Branch manager

The message sent will be of the following format:

MS_TRADER_INT_MSG (Refer to Interactive/Broadcast Messages Sent from Control)

The following table provides the details of the various fields present in the MS_TRADER_INT_MSG Structure.

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is CTRL_MSG_TO_TRADER (5295). |
| BroadCastMessage Length | This field contains Message Length |
| BroadCastMessage | This field contains actual Message |

## Unlock User

Corporate manager can send unlock request for the users within trading member's firm. As soon as User Unlock request reaches trading system, User Unlock Requested Response message is sent to user who has sent Unlock User Request. This in turn generates alert to NSEControl user. This alert may be approved or rejected by exchange.

## User Unlock Request

The format of the message is as follows:

| Structure Name | USER_ADDR_UNLOCK_REQ |
| --- | --- |
| Packet Length | 68 bytes |
| Transaction Code | USER_ADDR_UNLOCK_IN (5424) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_ADDR_UNLOCK_IN (5424) |
| UserId | This field should contain user id for which unlock request to be made |

## User Unlock Requested Response

This is an acknowledgement signifying that the User Unlock Request has reached the trading system. If any error is encountered in the User Unlock Request data, then appropriate error code will be set.

The structure is sent as follows:

| Structure Name | USER_ADDR_UNLOCK_RESP |
| --- | --- |
| Packet Length | 44 bytes |
| Transaction Code | USER_ADDR_UNLOCK_OUT (5425) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_ADDR_UNLOCK_OUT (5425) |
| ErrorCode | This field contains error code. If error code field value is zero (0) then user unlock request for user is made to exchange successfully. If error code field value is non-zero, then user unlock request for user is rejected. Refer to List of Error Codes in Appendix. |

## User Unlock Approval/Rejection Response

On approval of user unlock request by exchange trading system, exchange trading system will send user unlock response to user who has sent user unlock request.

The structure is sent as follows:

| Structure Name | USER_ADDR_UNLOCK_APP_REJ_RESP |
| --- | --- |
| Packet Length | 44 bytes |
| Transaction Code | USER_ADDR_UNLOCK_APPROVE_OUT (5575) |
| Field Name | Data Type |
| MESSAGE HEADER (Refer Table 1) | STRUCT |
| UserId | LONG |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is USER_ADDR_UNLOCK_APPROVE_OUT (5575) |
| ErrorCode | This field contains error code. If error code field value is non-zero, then user unlock request for user is rejected. Refer to List of Error Codes in Appendix. |
| TransactionCode | The transaction code is USER_ADDR_UNLOCK_REJECT_OUT (5579) |
| ErrorCode | This field contains error code. If error code field value is non-zero, then user unlock request for user is rejected. Refer to List of Error Codes in Appendix. |

## Trading Member Level Kill Switch

This functionality provides a facility to Corporate Manager, to cancel all pending orders of all the users under trading member's firm at the same time.

Also, user can cancel all outstanding orders on particular security by specifying security information in request packet.

## Member Level Kill Switch Request

The format of the message is as follows:

ORDER_ENTRY_REQUEST (Refer to Order Entry Request in [Chapter 4](#chapter-4))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is KILL_SWITCH_IN (2062). |
| User | This field should contain 0 for Trading Member level kill switch request. |
| SEC_INFO | For cancellation of all orders, Symbol and series fields should be set as blank. For cancellation of all orders on particular security, this structure should contain the Symbol and Series of the security. |

## Member Level Kill Switch Response

The Quick cancel out response is sent when the member level kill switch is requested by the corporate manager.

The message sent is as follows:

ORDER_ENTRY_REQUEST (Refer to Order Entry Request in [Chapter 4](#chapter-4))

## Member Level Kill Switch Error Response

The kill switch error is sent when the request is rejected by the trading system. The reason for rejection will be given by the Error Code in the header.

The message sent is as follows:

ORDER_ENTRY_REQUEST (Refer to Order Entry Request in [Chapter 4](#chapter-4))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_ERROR (2231). |
| ErrorCode | This field contains the error number. Refer to List of Error Codes in Appendix. |

## User Level Kill Switch

This functionality provides a facility to Corporate Manager and Branch Manager to cancel all of their orders at the same time.

Also, they can cancel all of their outstanding orders on particular security by specifying security information in request packet.

## User Level Kill Switch Request

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is KILL_SWITCH_IN (2062). |
| User | This field should contain the user id for which orders should be cancelled. |
| SEC_INFO | For cancellation of all orders, Symbol and series fields should be set as blank. For cancellation of all orders on particular security, this structure should contain the Symbol and Series of the security. |

## User Level Kill Switch Response

The Quick cancel out response is sent when the kill switch is requested by the user. The message sent is as follows:

ORDER ENTRY REQUEST       (Refer to Order Entry Request in [Chapter 4](#chapter-4))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is QUICK_CANCEL_OUT(2061) |

## User Level Kill Switch Error Response

The kill switch error is sent when the request is rejected by the trading system. The reason for rejection will be given by the Error Code in the header. The message sent is as follows:

ORDER ENTRY REQUEST       (Refer to Order Entry Request in [Chapter 4](#chapter-4))

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_ERROR (2231). |

## Order and Trade

## Order Entry

This functionality enables the Corporate Manager and Branch Manager to place orders in the market.

Please  refer  Trimmed  Order  Entry  Request  Structure  from  Trimmed  Structures  section  for further details.

## Order Modification

This  functionality  enables  the  Corporate  Manager  and  Branch  Manager  to  modify  their unmatched orders by specifying the order number of the order to be modified. All order types except Auction can be modified. Corporate Manager can modify his own order and also for his Branch Manager and Dealers/Traders. Branch Manager can modify his own order and also for his Dealers/Traders.

Please refer Trimmed Order Mod/Cxl Request Structure from Trimmed Structures section for further details.

## Order Cancellation

The  functionality  enables  the  Corporate  Manager  and  Branch  Manager  to  cancel  their  any unmatched/partially matched order by specifying the order number. Corporate Manager can

cancel his own order and also for this Branch Managers and Dealers/Traders. Branch Manager can cancel his own order and also for his Dealers/Traders.

Please refer Trimmed Order Mod/Cxl Request Structure from Trimmed Structures section for further details.

## Trade Modification

This functionality enables the Corporate Manager and Branch Manager to modify their trades. Only account number modification is allowed. Corporate Manager can modify his own trade and also for his Branch Managers and Dealers/Traders. Branch Manager can modify his own trade and also for his Dealers/Traders.

Please refer Trade Modification section (in [Chapter 4](#chapter-4)) for further details.

## Trade Cancellation

This functionality enables the Corporate Manager and Branch Manager to cancel their trades. But to cancel a trade, both the parties of the trade must request for trade cancellation. Corporate Manager can cancel his own trade and also for his Branch Managers and Dealers/Traders. Branch Manager can cancel his own trade and also for his Dealers/Traders.

Please refer Trade Cancellation section (in [Chapter 4](#chapter-4)) for further details.

## Close Out Order Entry

This facility is provided to trading members in closeout mode to place an opposite order with intent  to  reduce  the  open  positions.  Close  out  orders  entered  shall  be  Regular  Lot  (RL)  and Immediate or Cancel (IOC) orders.

Clearing members can place order entry on behalf of the linked trading members. A close out order entry can be placed by Corporate Manager of member type PCM (Professional clearing member) or PCM+TM (Professional clearing member which is also a Trading member).

Order  Confirmation/Cancellation  messages  shall  be  sent  to  Corporate  Manager  of  clearing member and Corporate Manager of trading member, on whose behalf the order was placed.

If the order is rejected by the close out system, the rejection message shall be sent only to the clearing member.  If the order is matched, the trade confirmation shall be sent to the clearing member and the trading member on whose behalf order was placed.

The format for closeout order entry please refer Trimmed Order Entry Request Structure from Trimmed Structures section for further details.

The UserId and BrokerId field has to be the one given below in case of close out order entry.

| Field Name | Brief Description |
| --- | --- |
| UserId | This field should be zero. |
| BrokerId | This field should contain the trading member ID on whose behalf the order is being placed |

## Appendix

Please note the details in appendix are also directly or indirectly referenced in CM_DROP_COPY_PROTOCOL document. Any change here may also impact the Order Drop Copy functionality.

## List of Error Codes

| Error Code ID | Error Code Value | Description of Error Code |
| --- | --- | --- |
| ERR_MARKET_NOT_OPEN | 16000 | The trading system is not available for trading. |
| ERR_INVALID_USER_TYPE | 16001 | Invalid User Type OR Reset User Password not requested by Corporate manager |
| ERR_BAD_TRANSACTION_CODE | 16003 | Erroneous transaction code received. |
| ERR_USER_ALREADY_SIGNED_ON | 16004 | User already signed on. |
| ERR_INVALID_SIGNON | 16006 | Invalid Box/User sign-on, please try again. |
| ERR_SIGNON_NOT_POSSIBLE | 16007 | Signing on to the trading system is restricted. Please try later on. |
| ERR_INVALID_SYMBOL | 16012 | Invalid symbol/series. |
| ERR_INVALID_ORDER_NUMBER | 16013 | Invalid order number |
| NOT_YOUR_FILL | 16015 | Invalid trade cancel request. |
| ERR_SECURITY_NOT_AVAILABLE | 16035 | Security is unavailable for trading at this time. Please try later. |
| ERR_INVALID_BROKER_OR_BRANCH | 16041 | Trading Member does not exist in the system. |
| ERR_USER_NOT_FOUND | 16042 | Dealer does not exist in the system. |
| ERR_TRD_MOD_REJ_END_OF_DAY_PR OCESSING_STARTED | 16050 | Trade modification request rejected as end of the day processing started. |
| FUNCTION_NOT_AVAILABLE | 16052 | When Preopen trade cancel request is rejected |
|  |  | OR BOVL/UOVL Limits not allowed to be set as unlimited OR BOVL update not requested by Corporate Manager OR Inconsistent data for BOVL update OR Branch Manager not allowed UOVL update for self/CM/other BM/users of other branch. OR Branch Manager not allowed Dealer Limit update for self. OR User Unlock Request not requested by Corporate Manager OR User Unlock Request not allowed for Corporate Manager OR |
| ERR_PASSWORD_HAS_EXPIRED | 16053 | Your password has expired, must be changed. |
| ERR_INVALID_BRANCH | 16054 | Branch does not exist in the system. OR Inconsistent data for UOVL update |
| ERR_PROGRAM_ERROR | 16056 | Program error. |
| ORDER_NOT_FOUND | 16060 | Modified/Cancelled order not found |
| ERROR_INVALID_STATUS_CHANGE | 16063 | Requested status change not allowed |
| ERROR_NOTHING_CHANGED | 16070 | Data has not changed |
| ERR_INVALID_BUYER_USER_ID | 16098 | Invalid trader ID for buyer. |
| ERR_INVALID_SELLER_USER_ID | 16099 | Invalid trader ID for seller. |
| ERR_INVALID_SYSTEM_VERSION | 16100 | Your system version has not been updated. |
| ERR_SYSTEM_ERROR | 16104 | System could not complete your transaction - ADMIN notified. |
| ERR_MOD_CAN_REJECT | 16115 | Order Modification/ Cancellation rejected by the system. |
| ERR_CANT_COMPLETE_YOUR_REQUES T | 16123 | System not able to complete your request. Please try again. |
| ERR_USER_IS_DISABLED | 16134 | This Dealer is disabled. Please call the Exchange. |
| OE_INVALID_STOCK_STATUS | 16145 | Security is not eligible to trade in Preopen. |
| ERR_INVALID_USER_ID | 16148 | Invalid Dealer ID entered. |
| ERR_INVALID_TRADER_ID | 16154 | Invalid Trader ID entered. |
| ERR_ATO_IN_OPEN | 16169 | Order priced ATO cannot be entered when a security is open. |
| ORD_NOT_ALLOWED_IN_PREOPEN | 16197 | Order Entry or Modification not allowed in preopen. |
| ERROR_PRO_PARTICIPANT_INVALID | 16233 | Proprietary requests cannot be made for participant. |
| INVALID_PRICE | 16247 | Invalid price in the price field. |
| ERR_TRADE_MOD_DIFF_VOL | 16251 | Trade modification with different quantities is received. |
| CXLD_TRADE_MOD_REQUEST | 16252 | Cancelled the trade modify request. |
| OE_DELETED_BUT_EXISTS | 16260 | Record is there in master file but delete flag is set. |
| ERROR_ALREADY_DELETED | 16264 | The member has already been deleted. |
| ERR_NOT_FOUND | 16273 | Record does not exist. |
| ERR_MARKETS_CLOSED | 16278 | The markets have not been opened for trading. |
| ERR_SECURITY_NOT_ADMITTED | 16279 | The security has not yet been admitted for trading. |
| ERR_SECURITY_MATURED | 16280 | The security has matured. |
| ERR_SECURITY_EXPELLED | 16281 | The security has been expelled. |
| ERR_QUANTITY_EXCEEDS_ISSUED_CA PITAL | 16282 | The order quantity is greater than the issued capital. |
| ERR_PRICE_NOT_MULT_TICK_SIZE | 16283 | The order price is not multiple of the tick size. |
| ERR_PRICE_EXCEEDS_DAY_MIN_MAX | 16284 | The order price is out of the day's price range. |
| ERR_BROKER_NOT_ACTIVE | 16285 | The broker is not active. |
| ERROR_INVALID_SYSTEM_STATUS | 16300 | System is in a wrong state to make the requested change. |
| OE_AUCTION_PENDING | 16303 | Request denied. Pending auctions. |
| ERR_ QUANTITY_FREEZE_CANCELLED | 16307 | The order is canceled due to quantity freeze. |
| ERR_PRICE_FREEZE_CANCELLED | 16308 | The order is canceled due to price freeze. |
| AON_VOLUME_NOT_ENOUGH | 16310 | AON volume not enough |
| ERR_SOLICITOR_PERIOD_OVER | 16311 | The Solicitor period for the Auction is over. |
| ERR_COMPETITIOR_PERIOD_OVER | 16312 | The Competitor period for the Auction is over. |
| OE_AUC_PERIOD_GREATER | 16313 | The Auction period will cross Market Close time. |
| OE_AUC_NOT_CAN | 16314 | The Auction cannot be cancelled. |
| ERR_LIMIT_WORSE_TRIGGER | 16315 | The limit price is worse than the trigger price. |
| ERR_TRG_PRICE_NOT_MULT_TICK_SI ZE | 16316 | The trigger price is not a multiple of tick size. |
| ERR_NO_AON_IN_LIMITS | 16317 | AON attribute not allowed. |
| ERR_NO_MF_IN_LIMITS | 16318 | MF attribute not allowed. |

| Error Code ID | Error Code Value | Description of Error Code |
| --- | --- | --- |
| ERR_NO_AON_IN_SECURITY | 16319 | AON attribute not allowed at security level. |
| ERR_NO_MF_IN_SECURITY | 16320 | MF attribute not allowed at security level. |
| ERR_MF_EXCEEDS_DQ | 16321 | MF quantity is greater than Disclosed quantity. |
| ERR_MF_NOT_MULT_BOARD_LOT | 16322 | MF quantity is not a multiple of regular lot. |
| ERR_MF_EXCEEDS_ORIGINAL_ QUANTITY | 16323 | MF quantity is greater than Original quantity. |
| ERR_DQ_EXCEEDS_ORIGINAL_ QUANTITY | 16324 | Disclosed quantity is greater than Original quantity. |
| ERR_DQ_NOT_MULT_BOARD_LOT | 16325 | Disclosed quantity is not a multiple of regular lot. |
| ERR_GTD_EXCEEDS_LIMIT | 16326 | GTD is greater than that specified at System. |
| OE_QUANTITY_GERATER_RL | 16327 | Quantity is greater than Regular lot size. |
| ERR_QUANTITY_NOT_MULT_BOARD_L OT | 16328 | Quantity is not a multiple of regular lot. |
| ERR_BROKER_NOT_PERMITTED_IN_M KT | 16329 | Trading Member not permitted in the market. |
| ERR_SECURITY_IS_SUSPENDED | 16330 | Security is suspended. |
| CXL_REMAIN_ACTIVE_ORDER | 16332 | Remaining passive order has to be cancelled. |
| ERR_BRANCH_LIMIT_EXCEEDED | 16333 | Branch Order Value Limit is exceeded. |
| OE_ORD_CAN_CHANGED | 16343 | The order to be cancelled has changed. |
| OE_ORD_CANNOT_CANCEL | 16344 | The order cannot be cancelled. |
| OE_INIT_ORD_CANCEL | 16345 | Initiator order cannot be cancelled. |
| OE_ORD_CANNOT_MODIFY | 16346 | Order cannot be modified. |
| ERR_TRADING_NOT_ALLOWED | 16348 | Trading is not allowed in this market. |
| CHG_ST_EXISTS | 16363 | New status requested should not be same as existing one. |
| OE_SECURITY_IN_PREOPEN | 16369 | The security status is preopen. |
| ERR_USER_TYPE_INQUIRY | 16372 | Order entry not allowed for user as it is of inquiry type. |
| ERR_SOLICITION_NOT_ALLOWED | 16379 | The broker is not allowed to enter soliciting orders. |
| ERR_AUCTION_FINISHED | 16383 | Trading in this auction is finished. |
| ERR_NO_TRADING_IN_SECURITY | 16387 | Security is not allowed to trade in this market. |
| ERR_FOK_ORDER_CANCELLED | 16388 | When Preopen unmatched orders are cancelled by the system after preopen session ends. When normal market unmatched orders are cancelled by the system if order collection phase is planned after circuit hit. When IOC unmatched orders are cancelled by the system. |
| ERR_TURNOVER_LIMIT_NOT_SET | 16392 | Turnover limit not provided. Please contact Exchange. |
| ERR_DQ_EXCEEDS_LIMIT | 16400 | DQ has exceeded limit set in control. |
| ERR_WRONG_LOGIN_ADDRESS | 16403 | You are trying to sign on from a different location. Sign on is not allowed. |
| ERR_ADMIN_SUSP_CANCELLED | 16404 | Order is cancelled due to freeze admin suspension. |
| ERR_INVALID_PRO_CLIENT | 16411 | Pro-client can be either Pro or Client only. |
| ERR_INVALID_NEW_VOLUME | 16412 | New volume should be less than the traded volume. |
| ERR_INVALID_BUY_SELL | 16413 | Requested by can be BUY or SELL or BOTH. |
| ERR_INVALID_INST | 16414 | Invalid combination of book type and instructions (order_type). |
| ERR_INVALID_ORDER_PARAM | 16415 | Invalid combination of MF / AON / Disclosed Volume. |
| ERR_INVALID_CP_ID | 16416 | Invalid counter broker Id. |
| ERR_NNF_REQ_EXCEEDED | 16417 | Number of NNF requests exceeded. |
| ERR_INVALID_ORDER | 16418 | Order entered has invalid data. |
| ERR _CXLED_TRADE_CXL_REQ | 16419 | Cancelled trade cancel request. |
| ERR_INVALID_ALPHA_CHAR | 16420 | Alpha char must be the same as first two chars of symbol. |
| ERR_TRADER_CANT_INIT_AUCTION | 16421 | Only control can initiate auctions, not trader. |
| ERR_INVALID_BOOK_TYPE | 16422 | Book type should be between 1(RL) and 7(AU). |
| ERR_INVALID_TRIGGER_PRICE | 16423 | Invalid trigger price entered. |
| ERR_INVALID_MSG_LENGTH | 16424 | Message length is invalid. |
| ERR_INVALID_PARTICIPANT | 16425 | Participant does not exist. |
| ERR_PARTICIPANT_AND_VOLUME_ CHANGED | 16426 | Participant and volume cannot be changed simultaneously. |
| ERR_BROKER_SUSP_TRD_MOD_REJ | 16427 | Trade modification rejected due to broker suspension |
| INVALID_AUCTION_INQUIRY | 16430 | Invalid auction inquiry request. |
| INVALID_ACCOUNT | 16431 | Invalid Account in the Account field |
| ORDER_VALUE_LIMIT_EXCEEDED | 16436 | The order value limit has exceeded |
| DQ_NOT_ALLOWED_IN_PREOPEN | 16439 | DQ Orders are not allowed in preopen. |
| SERIES_NOT_ALLOWED_IN_PREOPEN | 16440 | Order Entry is not allowed in preopen for the series. |
| ST_NOT_ALLOWED_IN_PREOPEN | 16441 | ST Orders are not allowed in preopen. |
| ORDER_VALUE_EXCEEDS_ORDER_VAL UE_LIMIT | 16442 | The current placed order's value is more than users order value limit |
| ERROR_SL_LMT_RSNBLTY_CHECK | 16448 | Difference between limit price and trigger price is beyond permissible range |
| ACCOUNT_MANDATORY | 16450 | Account number is mandatory in Account field |
| OE_BL_MKT_ORDERS_IN_CLOSING | 16473 | Only board lot market orders are allowed in Closing Session. |
| ORDER_CANCELED_DUE_TO_SECURIT Y_ SUSPENSION | 16482 | The order has been cancelled as security has been suspended |
| ORDER_CANCELED_DUE_TO_PARTICIP ANT_ SUSPENSION | 16483 | The order has been cancelled as participant has been suspended |
| ERR_FUNCTION_NOT_FOR_INQ_USER | 16493 | Functionality not available for Inquiry user |
| ERR_PRICE_OUTSIDE_REVISED_PRICE _RANGE | 16521 | Order price is outside the revised price range. |
| BUY_ORDER_VALUE_LIMIT_EXCEEDED | 16530 | Users buy order value limit has exceeded. |
| SELL_ORDER_VALUE_LIMIT_ EXCEEDED | 16531 | The order value limit for the sell quantity has exceeded its limit |
| ERR_BR_BUY_ORD_VAL_LIMIT_EXCEE DED | 16532 | Branch buy order limit has been exceeded |
| ERR_BR_SELL_ORD_VAL_LIMIT_EXCEE DED | 16533 | Branch sell order limit has been exceeded |
| NO_BUY_BACK_RUNNING | 16534 | No buyback running for that security. |

| Error Code ID | Error Code Value | Description of Error Code |
| --- | --- | --- |
| PARTIAL_ORDER_REJECTED | 16535 | Order partially rejected. Remaining order quantity specified rejected due to system error. |
| QUICK_CXL_REJECTED | 16536 | Quick Cancel request rejected due to system error. Retry Quick Cancel Request |
| ERR_CANNOT_LOGOFF_SELF | 16560 | Not allowed to reset user's own login session |
| ERR_USER_ALREADY_SIGNED_OFF | 16562 | Requested user is already signed off |
| ERR_NO_PRIVILEGE_FOR_USER | 16563 | No privilege to execute functionality |
| ERR_FRZ_REJECT_FOR_CLOSEOUT | 16567 | This error code will be returned when a Close out order goes into freeze. |
| ERR_CLOSEOUT_NOT_ALLOWED | 16568 | This error code is returned when a Close out order entry is not allowed. |
| ERR_CLOSEOUT_ORDER_REJECT | 16569 | This error code is returned when a Close out order is rejected by the system. |
| ERR_CLOSEOUT_TRDMOD_REJECT | 16571 | This error code will be returned when a user under a broker in 'Close out' state tries to modify Trade. |
| INVALID_MSG_LENGTH | 16573 | Message length is invalid. |
| ERR_MAX_UOVL_VALUE_EXCEEDED | 16576 | Maximum UOVL exceeded |
| ERR_MAX_BOVL_VALUE_EXCEEDED | 16577 | Maximum BOVL exceeded |
| ERR_USER_IP_REC_NOT_FOUND | 16588 | User does not exist |
| ERR_SYS_REJECT | 16592 | Order Entry is not allowed |
| rms_order_reject | 16597 | Order entry / Modification rejected by the Exchange |
| ERR_SEC_REJECT | 16598 | Order Entry is not allowed |
| ERR_ORD_VAL_EXCEEDED | 16600 | The order value has exceeded maximum permissible limit |
| ERR_PREOPEN_ORDER_REJECT | 16601 | Request Rejected by the exchange |
| MARKET_ORDER_NOT_ALLOWED_IN_B T_SESSION | 16603 | Market order not allowed in Block Trade session |
| DQ_ORDER_NOT_ALLOWED_IN_CLOSI NG | 16604 | Disclosed Quantity (DQ) order not allowed in closing session |
| ERR_INVALID_CLIENT | 16606 | Client order not allowed for market maker user |
| ERR_INST_PARTICIPANT_ORD_NOT_A LLOWED | 16700 | INST Participant orders not allowed for T+0 settlement |
| ERROR_ALGOID_NNFID_MISMATCH _1 | 16730 | NNF id & Algo id mismatch - Algo ID entered is 0 in order request. |
| ERROR_ALGOID_NNFID_MISMATCH _2 | 16731 | NNF id & Algo id mismatch - For Non-Algo orders Algo id should be 0 (zero) in order request. |
| ERROR_ALGO_MKT_NOT_ALLOWED | 16732 | Market order not allowed for Algo order. |
| ERROR_INVALID_NNF_ID | 16733 | 13 th digit of NNF id is invalid. |
| ERROR_BL_ORD_TIMED_OUT | 16738 | Block Deal order timed out. |
| ERR_ORD_LIM_EXCEEDS_SET_ORD_VA L_LIM | 16750 | Order Limit exceeds the set User Order Value Limit |
| ERROR_USER_ALREADY_UNLOCKED | 16752 | User already unlocked |
| ERROR_DUPLICATE_UNLOCK_ALERT | 16753 | Duplicate user unlock request |
| ERR_ACCNT_DISABLE_TRADING | 16761 | The account is disabled from trading as per directions of SEBI/Statutory Authority. |
| ERR_NEW_PWD_INVALID | 16778 | Password set is not in lines of the password policy |
| ERR_ACCNT_DISABLE_TRADING_FOR_ PIT | 16910 | Account is disabled for trading in the scrip during the Trading Window closure period (SEBI PIT Reg). Please contact the company for more details. |
| ERR_STATUS_CHANGE_NOT_ALLOWED | 17015 | Status change not allowed. User should be Dealer/Branch Manager/Inquiry |
| ERROR_INVALID_PACKET | 17101 | The packet has invalid transaction code OR Packet has invalid data |
| ERR_HEARTBEAT_NOT_RECEIVED | 17102 | Heart Beat not received |
| ERR_INVALID_BOX_ID | 17104 | Invalid Box Id |
| ERR_SEQ_NUM_MISMATCH | 17105 | Sequence number mismatch found |
| ERROR_BOX_RATE_EXCEEDED | 17106 | Box Rate has been exceeded by the Member |
| ERR_VOLUNTARY_CLOSEOUT_ORDR_R EJECT | 17017 | Order Cancelled due to Voluntary Closeout. |
| ERR_ACTV_NUM_OF_USRS_IN_BRNCH _EXCEEDED | 17022 | Number for active users in branch exceeded |
| ERR_ORD_COULD_RESULT_IN_SELF_T RADE | 17080 | The order could have resulted in self-trade. |
| ERR_MAX_USR_LOGIN_EXCEEDED | 17142 | Maximum user login allowed per box has been exceeded |
| ERR_INVALID_PAN_ID | 17177 | Invalid PAN Id |
| ERR_INVALID_ALGO_ID | 17179 | Invalid Algo Id |
| ERR_INVALID_RESERVED_FILLER | 17180 | Invalid value in the Reserved Filler field |
| ERR_MKT_ORD_NOT_ALLOWED | 17182 | Security not traded. Market order not allowed. |
| ERR_TRADE_BEYOND_MARKUP_PRICE | 17183 | Order could have resulted in trade beyond mark-up price. |
| ERR_USER_HAVING_NULL_RIGHTS | 17184 | Order rejected as user has NO trading rights |
| ERR_CHECKSUM_FAILED_GR | 19028 | Checksum verification failed at Gateway Router. |
| ERR_MULTIPLE_GR_QUERY_RCV | 19029 | Multiple GR_QUERY request received. |
| ERR_CANNOT_MOD_AUC_ORDER | 16397 | Modifying Auction Order not allowed |
| ERR_ENCRYPTION_FLAG_MISMATCH | 19030 | Encryption Flag Mismatch |
| ERR_MD5_CHECKSUM_FAILURE | 19031 | MD5 Checksum Failed |

## Reason Codes

The reason codes and the corresponding values are given below.

| Reason Code | Value |
| --- | --- |
| Security | 5 |
| Broker | 6 |
| Branch | 7 |
| User | 8 |
| Participant | 9 |
| Counter Party | 10 |
| Order Number | 11 |
| Auction Number | 15 |
| Order Type | 16 |
| Price Freeze | 17 |
| Quantity Freeze | 18 |
| Call Auction 1 | 23 |
| Call Auction 2 | 24 |

## List of Transaction Codes

| Transaction Code | Code | Structure | Size | I/B* |
| --- | --- | --- | --- | --- |
| SYSTEM_INFORMATION_IN | 1600 | MESSAGE_HEADER | 40 | I |
| SYSTEM_INFORMATION_OUT | 1601 | SYSTEM_INFORMATION_DATA | 90 | I |
| BOARD_LOT_IN | 2000 | ORDER_ENTRY_REQUEST | 290 | I |
| BOARD_LOT_OUT | 2001 | ORDER_ENTRY_REQUEST | 214 | I |
| PRICE_CONFIRMATION | 2012 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_MOD_IN | 2040 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_MOD_REJECT | 2042 | ORDER_ENTRY_REQUEST | 290 | I |
| QUICK_CANCEL_OUT | 2061 | ORDER_ENTRY_REQUEST | 290 | I |
| KILL_SWITCH_IN | 2062 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_CANCEL_IN | 2070 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_CANCEL_OUT | 2071 | ORDER_ENTRY_REQUEST | 214 | I |
| ORDER_CANCEL_REJECT | 2072 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_CONFIRMATION | 2073 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_MOD_CONFIRMATION | 2074 | ORDER_ENTRY_REQUEST | 290 | I |
| ORDER_CANCEL_CONFIRMATION | 2075 | ORDER_ENTRY_REQUEST | 290 | I |
| FREEZE_TO_CONTROL | 2170 | ORDER_ENTRY_REQUEST | 290 | I |
| ON_STOP_NOTIFICATION | 2212 | TRADE_CONFIRM | 228 | I |
| TRADE_CONFIRMATION | 2222 | TRADE_CONFIRM | 228 | I |
| TRADE_ERROR | 2223 | TRADE_INQUIRY_DATA | 210 | I |
| ORDER_ERROR | 2231 | ORDER_ENTRY_REQUEST | 290 | I |
| TRADE_CANCEL_CONFIRM | 2282 | TRADE_CONFIRM | 228 | I |
| TRADE_CANCEL_REJECT | 2286 | TRADE_CONFIRM | 228 | I |
| TRADE_MODIFY_CONFIRM | 2287 | TRADE_CONFIRM | 228 | I |
| SIGN_ON_REQUEST_IN | 2300 | SIGNON_IN | 276 | I |
| SIGN_ON_REQUEST_OUT | 2301 | SIGNON_OUT | 276 | I |
| ERROR_RESPONSE_OUT | 2302 | ERROR_RESPONSE | 180 | I |
| SIGN_OFF_REQUEST_OUT | 2321 | MESSAGE HEADER | 40 | I |
| GR_REQUEST | 2400 | MS_GR_REQUEST | 48 | I |
| GR_RESPONSE | 2401 | MS_GR_RESPONSE | 124 | I |
| BCAST_CONT_MSG | 5294 | MS_BCAST_CONT_MESSAGE | 244 | B |
| CTRL_MSG_TO_TRADER | 5295 | MS_TRADER_INT_MSG | 290 | I |
| USER_ADDR_UNLOCK_IN | 5424 | USER_ADDR_UNLOCK_REQ | 68 | I |
| USER_ADDR_UNLOCK_OUT | 5425 | USER_ADDR_UNLOCK_RESP | 44 | I |
| TRADE_CANCEL_IN | 5440 | TRADE_INQUIRY_DATA | 210 | I |
| TRADE_CANCEL_OUT | 5441 | TRADE_INQUIRY_DATA | 210 | I |
| TRADE_MOD_IN | 5445 | TRADE_INQUIRY_DATA | 210 | I |
| USER_ADDR_UNLOCK_APPROVE_OUT | 5575 | USER_ADDR_UNLOCK_APP_REJ_RESP | 44 | I |
| USER_ADDR_UNLOCK_REJECT_OUT | 5579 | USER_ADDR_UNLOCK_APP_REJ_RESP | 44 | I |
| BRANCH_ORDER_LIMIT_UPDATE_IN | 5716 | BRANCH_ORDER_VAL_LIMIT_UPDATE | 104 | I |
| BRANCH_ORDER_LIMIT_UPDATE_OUT | 5717 | BRANCH_ORDER_VAL_LIMIT_UPDATE | 104 | I |
| USER_ORDER_LIMIT_UPDATE_IN | 5719 | USER_ORDER_VAL_LIMIT_UPDATE | 142 | I |
| USER_ORDER_LIMIT_UPDATE_OUT | 5720 | USER_ORDER_VAL_LIMIT_UPDATE | 142 | I |
| DEALER_LIMIT_UPDATE_IN | 5721 | ORDER_LIMIT_UPDATE | 68 | I |
| DEALER_LIMIT_UPDATE_OUT | 5722 | ORDER_LIMIT_UPDATE | 68 | I |
| SIGN_OFF_TRADER_IN | 5723 | SIGNON IN | 276 | I |
| SIGN_OFF_TRADER_OUT | 5724 | SIGNON IN | 276 | I |
| RESET_PASSWORD_IN | 5738 | RESET_PASSWORD | 58 | I |
| RESET_PASSWORD_OUT | 5739 | RESET_PASSWORD | 58 | I |
| COL_USER_STATUS_CHANGE _IN | 5790 | COL_ USER_STATUS_CHANGE_REQ | 52 | I |
| COL_USER_STATUS_CHANGE _OUT | 5791 | COL_USER_STATUS_CHANGE_RESP | 46 | I |
| TRD_MOD_CXL_STATUS_CHANGE _IN | 5792 | USER_ TRD_MOD_CXL_CHANGE_REQ | 52 | I |
| TRD_MOD_CXL_STATUS_CHANGE _OUT | 5793 | USER_TRD_MOD_CXL_CHANGE_RESP | 46 | I |
| BCAST_JRNL_VCT_MSG | 6501 | BCAST_VCT_MESSAGES | 298 | B |
| BC_OPEN_MESSAGE | 6511 | BCAST_VCT_MESSAGES | 298 | B |
| BC_CLOSE_MESSAGE | 6521 | BCAST_VCT_MESSAGES | 298 | B |
| BC_PREOPEN_SHUTDOWN_MSG | 6531 | BCAST_VCT_MESSAGES | 298 | B |
| BC_CIRCUIT_CHECK | 6541 | BCAST_HEADER | 40 | B |
| BC_NORMAL_MKT_PREOPEN_ENDED | 6571 | BCAST_VCT_MESSAGES | 298 | B |
| BC_AUCTION_STATUS_CHANGE | 6581 | AUCTION_STATUS_CHANGE | 302 | B |
| DOWNLOAD_REQUEST | 7000 | MESSAGE_DOWNLOAD | 48 | I |
| HEADER_RECORD | 7011 | MESSAGE HEADER | 40 | I |
| MESSAGE_RECORD | 7021 | MESSAGE HEADER | 40 | I |
| TRAILER_RECORD | 7031 | MESSAGE HEADER | 40 | I |
| BROADCAST_MBO_MBP | 7200 | BROADCAST MBO MBP | 482 | B |
| BCAST_MW_ROUND_ROBIN | 7201 | BROADCAST INQUIRY RESPONSE | 466 | B |
| BCAST_SYSTEM_INFORMATION_OUT | 7206 | SYSTEM_INFORMATION_DATA | 90 | B |
| BCAST_ONLY_MBP | 7208 | BROADCAST ONLY MBP | 566 | B |
| BCAST_CALL | 7210 | BROADCAST CALL AUCTION ORD CXL | 490 | B |
| BCAST_CALL AUCTION_MBP | 7214 | BROADCAST CALL AUCTION MBP | 538 | B |
| BCAST_CA_MW | 7215 | BROADCAST CALL AUCTION MARKET WATCH | 482 | B |
| BCAST_INDICES | 7207 | BROADCAST INDICES | 474 | B |
| BCAST_INDICES_VIX | 7216 | BROADCAST INDICES VIX | 474 | B |
| UPDATE_LOCALDB_IN | 7300 | UPDATE_LOCAL_DATABASE | 58 | I |
| UPDATE_LOCALDB_DATA | 7304 | Packet of size >80 and <=512 | 512 | I |
| BCAST_PART_MSTR_CHG | 7306 | PARTICIPANT_UPDATE_INFO | 84 | B |
| UPDATE_LOCALDB_HEADER | 7307 | UPDATE_LDB_HEADER | 42 | I |
| UPDATE_LOCALDB_TRAILER | 7308 | UPDATE_LDB_TRAILER | 42 | I |
| PARTIAL_SYSTEM_INFORMATION | 7321 | SYSTEM_INFORMATION_DATA | 90 | I |
| BC_SYMBOL_STATUS_CHANGE _ACTION | 7764 | BCAST_SYMBOL_STATUS_CHANGE _ACTION | 58 | B |
| BCAST_INDICATIVE_INDICES | 8207 | BROADCAST INDICATIVE INDICES | 474 | B |
| BATCH_ORDER_CANCEL | 9002 | ORDER_ENTRY_REQUEST | 290 | I |
| BCAST_TURNOVER_EXCEEDED | 9010 | BROADCAST_LIMIT_EXCEEDED | 77 | B |
| BROADCAST_BROKER_REACTIVATED | 9011 | BROADCAST_LIMIT_EXCEEDED | 77 | B |
| AUCTION_INQUIRY_IN | 18016 | MS_AUCTION_INQ_REQ | 55 | I |
| AUCTION_INQUIRY_OUT | 18017 | AUCTION INQUIRY RESPONSE | 222 | I |
| MARKET_STATS_REPORT_DATA | 18201 | MS_RP_HDR REPORT MARKET STATISTICS REPORT TRAILER | 106 478 46 | B |
| BCAST_AUCTION_INQUIRY_OUT | 18700 | MS_AUCTION_INQ_DATA | 76 | B |
| BCAST_TICKER_AND_MKT_INDEX | 18703 | TICKER TRADE DATA | 546 | B |
| BCAST_SECURITY_STATUS_CHG_PREO PEN | 18707 | SECURITY STATUS UPDATE INFORMATION | 442 | I/B |
| BCAST_BUY_BACK | 18708 | BROADCAST BUY_BACK | 426 | B |
| BCAST_SECURITY_MSTR_CHG | 18720 | SECURITY UPDATE INFORMATION | 260 | I/B |
| BCAST_SECURITY_STATUS_CHG | 18130 | SECURITY STATUS UPDATE INFORMATION | 442 | I/B |
| BOARD_LOT_IN_TR | 20000 | ORDER_ENTRY_ REQUEST _TR | 136 | I |
| BOARD_LOT_OUT_TR | 20001 | MS_OM_REQUEST_TR | 132 | I |
| ORDER_MOD_IN_TR | 20040 | ORDER_OM_ REQUEST _TR | 180 | I |
| ORDER_MOD_OUT_TR | 20041 | MS_OM_REQUEST_TR | 132 | I |
| ORDER_MOD_REJECT_TR | 20042 | ORDER_OM_ RESPONSE_TR | 216 | I |
| ORDER_CANCEL_IN_TR | 20070 | ORDER_OM_ REQUEST _TR | 180 | I |
| ORDER_CANCEL_REJECT_TR | 20072 | ORDER_OM_ RESPONSE_TR | 216 | I |
| ORDER_CONFIRMATION_TR | 20073 | ORDER_OM_ RESPONSE_TR | 216 | I |
| ORDER_MOD_CONFIRMATION_TR | 20074 | ORDER_OM_ RESPONSE_TR | 216 | I |
| ORDER_CXL_CONFIRMATION_TR | 20075 | ORDER_OM_ RESPONSE_TR | 216 | I |
| ORDER_ERROR_TR | 20231 | ORDER_OM_ RESPONSE_TR | 216 | I |
| PRICE_CONFIRMATION_TR | 20012 | ORDER_OM_ RESPONSE_TR | 216 | I |
| TRADE_CONFIRMATION_TR | 20222 | MS_TRADE_CONFIRM_TR | 192 | I |
| BOX_SIGN_ON_REQUEST_IN | 23000 | MS_BOX_SIGN_ON_REQUEST_IN | 60 | I |
| BOX_SIGN_ON_REQUEST_OUT | 23001 | MS_BOX_SIGN_ON_REQUEST_OUT | 52 | I |
| SECURE_BOX_REGISTRATION_REQUE ST_IN | 23008 | MS_SECURE_BOX_REGISTRATION_RE QUEST_IN | 42 | I |
| SECURE_BOX_REGISTRATION_RESPO NSE_OUT | 23009 | MS_SECURE_BOX_REGISTRATION_RES PONSE_OUT | 40 | I |
| BOX_SIGN_OFF | 20322 | MS_BOX_SIGN_OFF | 42 | I |

## List of Transaction Codes Containing Timestamp in Nanoseconds

The transaction codes that will contain timestamp in nanoseconds from 01-Jan-1980 00:00:00 are listed in following table:

| Transaction Code | Code |
| --- | --- |
| PRICE_CONFIRMATION | 2012 |
| ORDER_MOD_REJECT | 2042 |
| ORDER_CANCEL_REJECT | 2072 |
| ORDER_CONFIRMATION | 2073 |
| ORDER_MOD_CONFIRMATION | 2074 |
| ORDER_CANCEL_CONFIRMATION | 2075 |
| FREEZE_TO_CONTROL | 2170 |
| ON_STOP_NOTIFICATION | 2212 |
| TRADE_CONFIRMATION | 2222 |
| ORDER_ERROR | 2231 |
| BATCH_ORDER_CANCEL | 9002 |
| PRICE_CONFIRMATION_TR | 20012 |
| ORDER_MOD_REJECT_TR | 20042 |
| ORDER_CANCEL_REJECT_TR | 20072 |
| ORDER_CONFIRMATION_TR | 20073 |
| ORDER_MOD_CONFIRMATION_TR | 20074 |
| ORDER_CXL_CONFIRMATION_TR | 20075 |
| TRADE_CONFIRMATION_TR | 20222 |
| ORDER_ERROR_TR | 20231 |

## Quick Reference for Order Entry Parameters

The order flags are given below.

## Order Terms:

| Order Flags | Input/Output |
| --- | --- |
| MF | Input, to be set when the min fill quantity is given |
| AON | Input |
| IOC | Input |
| GTC | Input |
| Day | Input |
| SL | Input |
| Market | Output |
| ATO | Output |
| STPC | Input |
| Preopen | Input |
| Frozen | Output |
| Modified | Input |
| Traded | Output |
| MatchedInd | Output |

| Status | Market | Book Type | Order Terms and Other Characteristic Fields |
| --- | --- | --- | --- |
| Preopen | Normal Market | RL** | Non-zero value of Good Till Date/DAY/GTC mandatory, mutually exclusive, input |
|  |  |  | ATO output, set if Market order, value of order price returned is ' - 1'. |
| Open | Normal Market | RL** | Non-zero value of Good Till Date/DAY/ GTC/ IOC mandatory, mutually exclusive, input MKT output, set if it is Market order. |
| Open | Normal Market | SL** | SL mandatory, input Non-zero value of Good Till Date/DAY/ GTC/ IOC mandatory, mutually exclusive, input MF/ AON mutually exclusive, input MKT output, set if Market order Trigger Price is mandatory. |
| Open | Normal Market | ST** | Non-zero value of Good Till Date /DAY/ GTC/ IOC mandatory, mutually exclusive, input MF/ AON mandatory, mutually exclusive, input MKT output, set if it is Market order. |
| Open | Odd Lot Market | OL** | Non-zero value of Good Till Date/DAY/ GTC/ IOC mandatory, mutually exclusive, input. Volume is less than Board Lot quantity. |
| Open | Auction Market | AU** | DAY mandatory, input. Auction Number and Participant Type are mandatory. |
| Preopen | Call Auciton 1 Market | CA | Non-zero value of IOC /DAY mandatory, mutually exclusive, input. ATO output, set if Market order, value of order price returned is ' - 1'. |
| Preopen | Call Auciton 2 Market | CB | Value of IOC set as 0 mandatory, mutually exclusive, input. ATO output set as 0, as Market Order Not allowed. Value of DAY set as 1 mandatory, mutually exclusive, input. |
| Close |  |  | Order entry is not allowed. |

## Market Type

The market types are:

| Status | Market Status ID |
| --- | --- |
| Normal Market | 1 |
| Odd Lot Market | 2 |
| Spot Market | 3 |
| Auction Market | 4 |
| Call auction1 Market | 5 |
| Call auction2 Market | 6 |

## Market Status

The market can be in one of the following statuses:

| Status | Market Status ID |
| --- | --- |
| PreOpen (only for Normal Market) | 0 |
| Open | 1 |
| Closed | 2 |
| Preopen ended | 3 |

## Book Types

There are seven books. These books fall in four markets.

| Book Type | Book ID | Market Type |
| --- | --- | --- |
| Regular Lot Order | 1 | Normal Market |
| Special Terms Order | 2 | Normal Market |
| Stop Loss Order | 3 | Normal Market |
| Odd Lot Order | 5 | Odd Lot Market |
| Spot Order | 6 | Spot Market |
| Auction Order | 7 | Auction Market |
| Call Auction1 | 11 | Call auction1 market |
| Call Auction2 | 12 | Call auction2 market |

## Auction Status

| Status | Value Sent in Packet | ID | Description |
| --- | --- | --- | --- |
| AUCTION_PENDING_APPROVAL |  | 1 | If the auction is initiated by the trader an alert is generated at the CWS. The auction status is in pending for approval. |
| AUCTION_PENDING | 'P' | 2 | If any auction in the particular security is already going on, the status of the auction entered next is pending. |
| OPEN_COMPETITIOR_PERIOD | 'C' | 3 | When the auction gets initiated, this is the status. |
| OPEN_SOLICITOR_PERIOD | 'S' | 4 | Auction enters solicitor period. |
| AUCTION_MATCHING | 'M' | 5 | After solicitor period ends, the auction enters matching state. The matching of auction orders takes place. |
| AUCTION_FINISHED | 'F' | 6 | Status after matching of orders is done and auction trades are generated. |
| AUCTION_CXLED | 'X' | 7 | Auction is cancelled by NSE-Control. |

## Security Status

| Status | Status ID |
| --- | --- |
| Preopen | 1 |
| Open | 2 |
| Suspended | 3 |
| Preopen Extended | 4 |
| Price Discovery | 6 |

## Activity Types

The activity types that are sent in reports are given below.

| Activity Type | Description | Code |
| --- | --- | --- |
| ORIGINAL_ORDER | This is the order that was entered. GTC/GTD orders still in the book also come with this activity type. | 1 |
| ACTIVITY_TRADE | The trade was done. | 2 |
| ACTIVITY_ORDER_CANCEL | The order was cancelled. | 3 |
| ACTIVITY_ORDER_MODIFY | The order was modified. | 4 |
| ACTIVITY_TRADE_MOD | The trade was modified. | 5 |
| ACTIVITY_TRADE_CXL_1 | Trade cancellation was requested. | 6 |
| ACTIVITY_TRADE_CXL_2 | Action has been taken on this request. | 7 |
| ACTIVITY_BATCH_ORDER_CANCEL | At the end of the day, all untraded Day orders are cancelled. GTC/GTD orders due for cancellation are also cancelled. | 8 |

## Pipe Delimited File Structures

The upload files have a header record at the beginning of the file followed by the detail records. All the fields in both the header and detail records are separated by pipe ('|').The fields are not of fixed width. Any two fields are separated by a '|' sym bol.

## Security File Structure

Header

| Structure Name | SECURITY_FILE_HEADER |
| --- | --- |
| Packet Length | 19 bytes |
| Field Name | Data Type |
| NEATCM | CHAR |
| Reserved | CHAR |
| VersionNumber | CHAR |
| Reserved | CHAR |
| DATE | LONG |

## Stock Structure

## Table 52 STOCK_STRUCTURE

| Structure Name | STOCK_STRUCTURE |
| --- | --- |
| Packet Length | 270 bytes |
| Field Name | Data Type |
| Token | LONG |
| Reserved | CHAR |
| Symbol | CHAR |
| Reserved | CHAR |
| Series | CHAR |
| Reserved | CHAR |
| InstrumentType | SHORT |
| Reserved | CHAR |
| IssuedCapital | DOUBLE |
| Reserved | CHAR |
| PermittedToTrade | SHORT |
| Reserved | CHAR |
| CreditRating | CHAR |
| Reserved | CHAR |
| ST_SEC_ELIGIBILITY_ PER_ MARKET [6] (Refer Table 52.1) | STRUCT |
| BoardLotQuantity | LONG |
| Reserved | CHAR |
| TickSize | LONG |
| Reserved | CHAR |
| Name | CHAR |
| Reserved | CHAR |
| SurvInd | SHORT |
| Reserved | CHAR |
| IssueStartDate | LONG |
| Reserved | CHAR |
| IssueIPDate | LONG |
| Reserved | CHAR |
| Packet Length | 270 bytes |
| Field Name | Data Type |
| MaturityDate | LONG |
| Reserved | CHAR |
| FreezePercent | SHORT |
| Reserved | CHAR |
| ListingDate | LONG |
| Reserved | CHAR |
| ExpulsionDate | LONG |
| Reserved | CHAR |
| ReAdmissionDate | LONG |
| Reserved | CHAR |
| ExDate | LONG |
| Reserved | CHAR |
| RecordDate | LONG |
| Reserved | CHAR |
| NoDeliveryDateStart | LONG |
| Reserved | CHAR |
| NoDeliveryDateEnd | LONG |
| Reserved | CHAR |
| ParticipantInMktIndex | CHAR |
| Reserved | CHAR |
| AON | CHAR |
| Reserved | CHAR |
| MF | CHAR |
| Reserved | CHAR |
| SettlementType | SHORT |
| Reserved | CHAR |
| BookClosureStartDate | LONG |
| Reserved | CHAR |
| BookClosureEndDate | LONG |
| Reserved | CHAR |
| Dividend | CHAR |
| Reserved | CHAR |
| Packet Length | 270 bytes |
| Field Name | Data Type |
| Rights | CHAR |
| Reserved | CHAR |
| Bonus | CHAR |
| Reserved | CHAR |
| Interest | CHAR |
| Reserved | CHAR |
| AGM | CHAR |
| Reserved | CHAR |
| EGM | CHAR |
| Reserved | CHAR |
| MMSpread | LONG |
| Reserved | CHAR |
| MMMinQty | LONG |
| Reserved | CHAR |
| SSEC | SHORT |
| Reserved | CHAR |
| Remarks | CHAR |
| Reserved | CHAR |
| LocalDBUpdateDateTime | LONG |
| Reserved | CHAR |
| DeleteFlag | CHAR |
| Reserved | CHAR |
| FaceValue | LONG |
| Reserved | CHAR |
| ISIN Number | CHAR |

Table 52.1 ST_SEC_ELIGIBILITY_PER_MARKET

| Structure Name | ST_SEC_ELIGIBILITY_PER_MARKET |
| --- | --- |
| Packet Length | 6 bytes |
| Field Name | Data Type |
| Security Status | SHORT |

| Reserved | CHAR | 1 | 2 |
| --- | --- | --- | --- |
| Eligibility | CHAR | 1 | 3 |
| Reserved | CHAR | 2 | 4 |

| Field Name | Brief Description |
| --- | --- |
| Token | Token number of the security being updated. This is unique for a particular symbol-series combination. |
| Symbol | This field should contain the symbol of a security. |
| Series | This field should contain the series of a security |
| InstrumentType | This field contains the instrument type of the security. It can be one of the following: ▪ '0' - Equities ▪ '1' - Preference Shares ▪ '2' - Debentures ▪ '3' - Warrants ▪ '4' - Miscellaneous |
| IssuedCapital | Issue size of the security. |
| PermittedToTrade | • '0' - Listed but not permitted to trade • '1' - Permitted to trade • '2' - BSE listed (BSE exclusive security will be available, however trading on the same will be allowed only in case of outage at BSE) |
| CreditRating | This field contains daily price range of the security. |
| SecurityStatus | • '1' - Preopen (Only for Normal market) • '2' - Open • '3' - Suspended • '4' - Preopen extended • '5' - Stock Open With Market • '6' - Price Discovery This will contain the Call Auction2 Market security status at 6th position The values can be : 1' : Preopen |
|  | 3' : Suspended 6': Price Discovery. |
| Eligibility | • 0' - for Stocks not eligible in current market • '1' - for stocks eligible in current Market 6th Position represents eligibility for Call Auction 2 Market. |
| BoardLotQuantity | Regular lot size. |
| TickSize | Tick size/ Min spread size. |
| Name | Security name. |
| SurvInd | Indicator for security in Surveillance Measure |
| IssueStartDate | Date of issue of the security. |
| IssueIPDate | Interest Payment Date |
| IssueMaturityDate | Maturity Date. |
| FreezePercent | Freeze percent. This field indicates the volume freeze percentage w.r.t. issued capital. This field has to be interpreted as freeze percent /10000. E.g.: 41 in this field has to be interpreted as 0.0041% |
| ListingDate | Date of listing. |
| ExpulsionDate | Date of expulsion. |
| ReAdmissionDate | Date of readmission. |
| ExDate | Last date of trading before any corporate action. |
| RecordDate | Date of record changed. |
| NoDeliveryStartDate | Date from when physical delivery of share certificates is stopped for book closure. |
| NoDeliveryEndDate | No delivery end date. |
| ParticipateInMktIndex | '1' - Security is present in NIFTY Index. '0' - Security is not present in NIFTY Index. |
| AON | '1' - AONis allowed. '0' - AONis not allowed |
| MF | '1' - MF is allowed. '0' - MF is not allowed |
| SettlementType | This field contains the settlement type. It can be one of the following: '0' - T+0 settlement |
|  | '1' - T+1 settlement |
| BookClosureStartDate | Date at which the record books in the company for shareholder names starts. |
| BookClosureEndDate | Date at which the record books in the company for shareholder names ends. |
| Dividend | '1' - Dividend '0' - No Dividend |
| Rights | '1' - Rights '0' - No Rights |
| Bonus | '1' - Rights '0' - No Rights |
| Interest | '1' - Interest '0' - No Interest |
| AGM | '1' - AGM '0' - NoAGM |
| EGM | '1' - EGM '0' - No EGM |
| MMSpread | This is the spread value per security. |
| MMMinQty | This field contains the Minimum quantity for the security, Used by Market maker user for market maker order. |
| SSEC | '1' - Securities (except SME) eligible in Normal market and Odd Lot markets. '2' - IPO Session is held security (including SME) '3' - Re-list Session is held security (including SME). '4' - Illiquid security eligible for Call Auction session (CA2) (including SME). '5' - SME securities eligible in normal market. This is used as an identifier for different market securities. |
| Remark | Remarks |
| LocalLDBUpdateDateTime | This is the local database update date-time. |
| DeleteFlag | This indicates the status of the security, whether the security is deleted or not. • 'N' : Active • 'Y' : Deleted |
| FaceValue | This field contains face value of the security |
| ISIN Number | This field contains the ISIN Number of the security. |

## Contract File Structure

Header

## Table 53 CONTRACT_FILE_HEADER

| Structure Name | CONTRACT_FILE_HEADER |
| --- | --- |
| Packet Length | 13 bytes |
| Field Name | Data Type |
| NEATFO | CHAR |
| Reserved | CHAR |
| VersionNumber | CHAR |
| Reserved | CHAR |

## Stock Structure

## Table 54 STOCK_STRUCTURE

| Structure Name | STOCK_STRUCTURE |
| --- | --- |
| Packet Length | 322 bytes |
| Field Name | Data Type |
| Token | LONG |
| Reserved | CHAR |
| AssetToken | LONG |
| Reserved | CHAR |
| InstrumentName | CHAR |
| Reserved | CHAR |
| Symbol | CHAR |
| Reserved | CHAR |
| Series | CHAR |
| Reserved | CHAR |
| Packet Length | 322 bytes |
| Field Name | Data Type |
| ExpiryDate (in seconds from | LONG |
| January 1,1980) Reserved | CHAR |
| StrikePrice | LONG |
| Reserved | CHAR |
| OptionType | CHAR |
| Reserved | CHAR |
| Category | CHAR |
| Reserved | CHAR |
| CALevel | SHORT |
| Reserved | CHAR |
| PermittedToTrade | SHORT |
| Reserved | CHAR |
| IssueRate | SHORT |
| Reserved | CHAR |
| ST_SEC_ELIGIBILITY_ PER_ MARKET [4] (Refer Table 54.1) | STRUCT |
| IssueStartDate | LONG |
| Reserved | CHAR |
| InterestPaymentDate | LONG |
| Reserved | CHAR |
| Issue Maturity Date | LONG |
| Reserved | CHAR |
| MarginPercentage | LONG |
| Reserved | CHAR |
| MinimumLotQuantity | LONG |
| Reserved | CHAR |
| BoardLotQuantity | LONG |
| Reserved | CHAR |
| TickSize | LONG |
| Reserved | CHAR |
| IssuedCapital | DOUBLE |
| Packet Length | 322 bytes |
| Field Name | Data Type |
| Reserved | CHAR |
| FreezeQuantity | LONG |
| Reserved | CHAR |
| WarningQuantity | LONG |
| Reserved | CHAR |
| ListingDate | LONG |
| Reserved | CHAR |
| ExpulsionDate | LONG |
| Reserved | CHAR |
| ReadmissionDate | LONG |
| Reserved | CHAR |
| RecordDate | LONG |
| Reserved | CHAR |
| NoDeliveryStartDate | LONG |
| Reserved | CHAR |
| NoDeliveryEndDate | LONG |
| Reserved | CHAR |
| LowPriceRange | LONG |
| Reserved | CHAR |
| HighPriceRange | LONG |
| Reserved | CHAR |
| ExDate | LONG |
| Reserved | CHAR |
| BookClosureStartDate | LONG |
| Reserved | CHAR |
| BookClosureEndDate | LONG |
| Reserved | CHAR |
| LocalLDBUpdateDateTime | LONG |
| Reserved | CHAR |
| ExerciseStartDate | LONG |
| Reserved | CHAR |
| ExerciseEndDate | LONG |
| Packet Length | 322 bytes |
| Field Name | Data Type |
| Reserved | CHAR |
| TickerSelection | SHORT |
| Reserved | CHAR |
| OldTokenNumber | LONG |
| Reserved | CHAR |
| CreditRating | CHAR |
| Reserved | CHAR |
| Name | CHAR |
| Reserved | CHAR |
| EGMAGM | CHAR |
| Reserved | CHAR |
| InterestDivident | CHAR |
| Reserved | CHAR |
| RightsBonus | CHAR |
| Reserved | CHAR |
| MFAON | CHAR |
| Reserved | CHAR |
| Remarks | CHAR |
| Reserved | CHAR |
| ExStyle | CHAR |
| Reserved | CHAR |
| ExAllowed | CHAR |
| Reserved | CHAR |
| ExRejectionAllowed | CHAR |
| Reserved | CHAR |
| PlAllowed | CHAR |
| Reserved | CHAR |
| CheckSum | CHAR |
| Reserved | CHAR |
| IsCorporateAdjusted | CHAR |
| Reserved | CHAR |
| SymbolForAsset | CHAR |

| Structure Name | STOCK_STRUCTURE |
| --- | --- |
| Packet Length | 322 bytes |
| Field Name | Data Type |
| Reserved | CHAR |
| InstrumentOfAsset | CHAR |
| Reserved | CHAR |
| BasePrice | LONG |
| Reserved | CHAR |
| DeleteFlag | CHAR |

Table 54.1 ST_SEC_ELIGIBILITY_PER_MARKET

| Structure Name | ST_SEC_ELIGIBILITY_PER_MAKRET |
| --- | --- |
| Packet Length | 6 bytes |
| Field Name | Data Type |
| Security Status | SHORT |
| Reserved | CHAR |
| Eligibility | CHAR |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| Token | Token number of the security being updated. This is unique for a particular symbol-series combination. |
| AssetToken | Token number of the asset. |
| SecurityInformation | This contains the Instrument Name, Symbol & Series (EQ / IL / TT), Expiry date, Strike Price, Option Type, Corporate Action level of the security |
| PermittedToTrade | This field can have any one of the following value: • '0' - Listed but not permitted to trade • '1' - Permitted to trade |
| Reserved Identifier | This field can have any one of the following value: • '0' - Unreserved Contract • '1' - Reserved Contract |
| IssueRate | Price of the issue. |
| Eligibility | The flag is set to 1 if the security is allowed to trade in a particular market. |
| SecurityStatus | This field can have any one of the following value: • '1' - Preopen (Only for Normal market) • '2' - Open • '3' - Suspended • '4' - Preopen extended |
| IssueStartDate | Date of issue of the security. |
| InterestPaymentDate | Interest payment date |
| IssueMaturityDate | Maturity date. |
| MarginPercent | It is an initial margin percent to be collected on a contract. |
| MinimumLotQuantity | It is minimum lot of the order which can be placed. |
| BoardLotQuantity | Regular lot size. |
| TickSize | Tick size/ Min spread size. |
| IssuedCapital | Issue size of the security. |
| FreezeQuantity | Freeze quantity. |
| WarningQuantity | Warning quantity. |
| ListingDate | Date of listing. |
| ExpulsionDate | Date of expulsion. |
| ReAdmissionDate | Date of readmission. |
| RecordDate | Date of record changed. |
| NoDeliveryStartDate | Date from when physical delivery of share certificates is stopped for book closure. |
| NoDeliveryEndDate | No delivery end date. |
| LowPriceRange | Minimum price at which order can be placed without causing a price freeze. |
| HighPriceRange | Maximum price at which order can be placed without causing a price freeze. |
| ExDate | Last date of trading before any corporate action. |
| BookClosureStartDate | Date at which the record books in the company for shareholder names starts. |
| BookClosureEndDate | Date at which the record books in the company for shareholder names ends. |
| LocalLDBUpdateDateTime | This is the local database update date-time. |
| ExerciseStartDate | This is the starting date for exercise. |
| ExerciseEndDate | This is the last date for exercise. |
| OldTokenNumber | Not used. |
| CreditRating | This field contains daily price range of the security. |
| Name | Security name. |
| EGM/AGM | This field can have any one of the following value: • '0' - No EGM/AGM • '1' - EGM • '2' - AGM • '3' - BothEGM andAGM |
| InterestDividend | This field can have any one of the following value: • '0' - No Interest/ Dividend • '1' - Interest • '2' - Dividend |
| RightsBonus | This field can have any one of the following value: • '0' - No Rights/Bonus • '1' - Rights • '2' - Bonus • '3' - Both Rights and Bonus |
| MFAON | This field can have any one of the following value: • '0' - MF/AON not allowed • '1' - MF allowed • '2' - AON allowed • '3' - MF and AONallowed |
| Remark | Remarks |
| ExStyle | This field can have any one of the following value: |
|  | • 'A' - American style Exercise allowed • 'E' - European style Exercise allowed |
| ExAllowed | Exercise is allowed on this contract if this flag is set to true. |
| ExRejectionAllowed | Exercise rejection is allowed on this contract if this bit is set to true. |
| PlAllowed | Position liquidation is allowed on this contract if this flag is set to true. |
| CheckSum | Not used. |
| IsCorporateAdusted | This field shows whether this contract is corporate adjusted. |
| AssetName | Name of the underlying asset. Note: For example, NIFTY. |
| InstrumentIDOfAsset | ID of the instrument for the underlying asset of this contract. |
| AssetInstrument | Underlying asset type. Note: For example, INDEX. |
| BasePrice | Base price of the security. |
| DeleteFlag | This flag indicates the status of the security, whether the security is deleted or not. This field can have any one of the following value: • 'N' : Active • 'Y' : Deleted |

## Participant Structure

Header

## Table 55 PARTICIPANT_FILE_HEADER

| Structure Name | PARTICIPANT_FILE_HEADER |
| --- | --- |
| Packet Length | 20 bytes |
| Field Name | Data Type |
| NEATCM | CHAR |
| Reserved | CHAR |

| VersionNumber | CHAR | 7 | 7 |
| --- | --- | --- | --- |
| Reserved | CHAR | 1 | 14 |
| DATE | LONG | 4 | 15 |
| Reserved | CHAR | 1 | 19 |

## Structure

## Table 56 PARTICIPANT_STRUCTURE

| Structure Name | PARTICIPANT_STRUCTURE |
| --- | --- |
| Packet Length | 47 bytes |
| Field Name | Data Type |
| ParticipantId | CHAR |
| Reserved | CHAR |
| ParticipantName | CHAR |
| Reserved | CHAR |
| ParticipantStatus | CHAR |
| Reserved | CHAR |
| DeleteFlag | CHAR |
| Reserved | CHAR |
| LastUpdateTime | LONG |

| Field Name | Brief Description |
| --- | --- |
| ParticipantId | ID of the participant. |
| ParticipantName | Name of the participant. |
| ParticipantStatus | If this field is set to 'S' then the participant is suspended. If this is field is set to 'A' then the participant is active. |
| DeleteFlag | If this field is set to 'Y' then the participant is deleted from the system, else he/she is present in the system. |
| LastUpdateTime | The last time this record was modified. |

## Trimmed Structures

## Trimmed Order Entry Request structure

## Table 57 ORDER_ENTRY_REQUEST

| Structure Name | ORDER_ENTRY_ REQUEST _TR |
| --- | --- |
| Transaction Code | BOARD_LOT_IN_TR (20000) |
| Packet Length | 136 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| Transcode | SHORT |
| TraderId | LONG |
| SEC_INFO (Refer Table 4) | STRUCT |
| AccountNumber [10] | CHAR |
| BookType | SHORT |
| BuySell | SHORT |
| DisclosedVol | LONG |
| Volume | LONG |
| Price | LONG |
| GoodTillDate | LONG |
| ST_ORDER_FLAGS ( Refer Table 57.1 for small endian machines and Table 57.2 for big endian machines) | STRUCT |
| BranchId | SHORT |
| UserId | LONG |
| BrokerId [5] | CHAR |
| Suspended | CHAR |
| Settlor [12] | CHAR |
| ProClient | SHORT |
| NNFField | DOUBLE |
| TransactionId | LONG |
| PAN | CHAR |
| Transaction Code | BOARD_LOT_IN_TR (20000) |
| Packet Length | 136 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| Reserved | CHAR |

## For Small Endian Machines:

| Structure Name | ST_ORDER_FLAGS |
| --- | --- |
| Packet Length | 2 bytes |
| Field Name | Data Type |
| MF | BIT |
| AON | BIT |
| IOC | BIT |
| GTC | BIT |
| Day | BIT |
| OnStop | BIT |
| Mkt | BIT |
| ATO | BIT |
| Reserved | BIT |
| STPC | BIT |
| Reserved | BIT |
| Preopen | BIT |
| Frozen | BIT |
| Modified | BIT |
| Traded | BIT |
| MatchedInd | BIT |

## For Big Endian Machines:

Table 57.2 ST_ORDER_FLAGS

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
| Frozen | BIT |
| Preopen | BIT |
| Reserved | BIT |
| STPC | BIT |
| Reserved | BIT |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is BOARD_LOT_IN_TR (20000). |
| TraderId | This field should contain the user ID of the user. |
| SEC_INFO | This structure should contain the Symbol and Series of the security. |
| AccountNumber | If the order is entered on behalf of a trader, the trader account number should be specified in this field. For broker's own order, this field should be set to the broker code. |
| BookType | This field should contain the type of order. BOARD_LOT_IN_TR (20000) must have BookType 1 or 11 or 12. |
| BuySell | This field should specify whether the order is a buy or sell. It should take one of the following values. • '1' for Buy order • '2' for Sell order |
| DisclosedVol | This field should specify the quantity that has to be disclosed to the market. It is not applicable if the order has either the All Or None or the Immediate Or Cancel attribute set. It should not be greater than the volume of the order and not less than the Minimum Fill quantity if the Minimum Fill attribute is set. In either case, it cannot be less than the Minimum Disclosed Quantity allowed. It should be a multiple of the Regular lot. |
| Volume | This field should specify the quantity of the order placed. The quantity should always be in multiples of Regular Lot except for Odd Lot orders and be less than the issued capital. The order will go for a freeze if the quantity is greater than the freeze quantity determined by NSE-Control. |
| Price | This field should contain the price at which the order is placed. To enter a Market order, the price should be zero. The price must be a multiple of the tick size. For Stop Loss orders, the limit price must be greater than the trigger price in case of a Buy order and less if it is a Sell order. This is to be multiplied by 100 before sending to the trading system host. |
| GoodTillDate | This field should contain the number of days for a GTD order. This field may be set in two ways. To specify an absolute date set this field to that date in number of seconds since midnight of January 1, 1980. To specify days set this to the number of days. This can take values from 2 to the maximum days specified for GTC orders only. If this field is non-zero, the GTC flag must be off. |
| Order_Flags | This structure specifies the attributes of an order. They are: • MF if set to 1, represents Minimum Fill attribute. • AON if set to 1, represents All Or None attribute. • IOC if set to 1, represents Immediate Or Cancel attribute. • GTC if set to 1, represents Good Till Cancel. • Day if set to 1, represents Day attribute. This is the default attribute. • SL if set to 1, represents Stop Loss attribute. • Mkt if set to 0, represents a Market order. |
|  | • ATO if set to 1, represents a market order in PREOPEN or CALL AUCTION1 or CALL AUCTION 2 market. • STPC if set to 0, represents order resulting in self-trade to be cancelled as per default action by the exchange if set to 1, represents active order resulting in self-trade to be cancelled Order modification will be rejected if this bit is modified. In case of triggered stop loss order, bit selected during order entry will be considered. • Preopen if set to 1, represents the order is a Preopen session order and if set to 0, represents Normal Market Open order. Preopen bit should be set to 1 for orders in Call Auction 2 market. • Frozen if set to 1, represents the order has gone for a freeze. • Modified if set to 1, represents the order is modified. • Traded if set to 1, represents the order is traded partially or fully. For a market order, the price should be 0. The Bit fields must be set / unset by Front end as mentioned in the description. For CALL AUCTION1 order, if it is market order, ATO bit should set to1& IOC bit needs to be set for mkt as well as limit orders. For CALL AUCTION2 order,ATO& Mkt bit should set to 0 as |
| BranchId | This field should contain the ID of the branch of the particular broker. |
| UserId | This field should contain the ID of the user. This field accepts only numbers. |
| BrokerId | This field should contain the trading member ID. |
| Suspended | This field specifies whether the security is suspended or not. It should be set to blank while sending order entry request. |
| Settlor | This field contains the ID of the participants who are responsible for settling the trades through the custodians. By default, all orders are treated as broker's own orders and this field defaults to the Broker Code. |
| ProClient | This field should contain one of the following values based on the order entering is on behalf of the broker or a trader. '1' - represents the client's order. '2' - represents a broker's order. '4' - represents warehousing order. |
| NNFField | This field should contain a 15 digit a unique identifier for various products deployed as per Exchange circular download ref no. 16519 dated December 14, 2010, and as updated from time to time |
| PAN | This field shall contain the PAN (Permanent Account Number / PAN_EXEMPT) - This field shall be mandatory for all orders (client / participant / PRO orders). |
| Algo ID | For Algo order this field shall contain the Algo ID issued by the exchange. For Non-Algo order, this field shall be Zero(0) |
| Reserved Filler | This field is reserved for future use. This should be set to Zero (0) while sending to the exchange trading system. |

## Trimmed Order Mod/Cancel Request Structure

## Table 58 ORDER_OM_REQUEST

| Structure Name | ORDER_OM_ REQUEST _TR |
| --- | --- |
| Transaction Code | ORDER_MOD_IN_TR (20040) ORDER_CANCEL_IN_TR (20070) |
| Packet Length | 180 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| TransactionCode | SHORT |
| Transaction Code | ORDER_MOD_IN_TR (20040) ORDER_CANCEL_IN_TR (20070) |
| Packet Length | 180 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| LogTime | LONG |
| UserId | LONG |
| ErrorCode | SHORT |
| TimeStamp1 | LONG LONG |
| TimeStamp2 | CHAR |
| Modified / Cancelled By | CHAR |
| ReasonCode | SHORT |
| SEC_INFO (Refer Table 4) | STRUCT |
| OrderNumber | DOUBLE |
| AccountNumber [10] | CHAR |
| BookType | SHORT |
| BuySell | SHORT |
| DisclosedVol | LONG |
| DisclosedVolRemaining | LONG |
| TotalVolRemaining | LONG |
| Volume | LONG |
| VolumeFilledToday | LONG |
| Price | LONG |
| EntryDateTime | LONG |
| LastModified | LONG |
| ST_ORDER_FLAGS ( Refer Table 19.1 for small endian machines and Table 19.2 for big endian machines) | STRUCT |
| BranchId | SHORT |
| UserId | LONG |
| BrokerId [5] | CHAR |
| Suspended | CHAR |
| Settlor [12] | CHAR |
| Transaction Code | ORDER_MOD_IN_TR (20040) ORDER_CANCEL_IN_TR (20070) |
| Packet Length | 180 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| ProClient | SHORT |
| SettlementType | SHORT |
| NNFField | DOUBLE |
| TransactionId | LONG |
| PAN | CHAR |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| LastActivityReference | LONG LONG |
| Reserved | CHAR |

## Trimmed Order Mod/Cancel Response Structure

## Table 59 ORDER_OM_RESPONSE

| Structure Name | ORDER_OM_ RESPONSE_TR |
| --- | --- |
| Transaction Code | ORDER_MOD_REJECT_TR (20042) ORDER_CANCEL_REJECT_TR (20072) ORDER_CONFIRMATION_TR (20073) ORDER_MOD_CONFIRMATION_TR (20074) ORDER_CXL_CONFIRMATION_TR (20075) ORDER_ERROR_TR (20231) PRICE_CONFIRMATION_TR (20012) |
| Packet Length | 216 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| TransactionCode | SHORT |
| LogTime | LONG |
| UserId | LONG |
| ErrorCode | SHORT |
| TimeStamp1 | LONG LONG |
| Transaction Code | ORDER_MOD_REJECT_TR (20042) ORDER_CANCEL_REJECT_TR (20072) ORDER_CONFIRMATION_TR (20073) ORDER_MOD_CONFIRMATION_TR (20074) ORDER_CXL_CONFIRMATION_TR (20075) ORDER_ERROR_TR (20231) PRICE_CONFIRMATION_TR (20012) |
| Packet Length | 216 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| TimeStamp2 | CHAR |
| Modified / Cancelled By | CHAR |
| ReasonCode | SHORT |
| SEC_INFO (Refer Table 4) | STRUCT |
| OrderNumber | DOUBLE |
| AccountNumber [10] | CHAR |
| BookType | SHORT |
| BuySell | SHORT |
| DisclosedVol | LONG |
| DisclosedVolRemaining | LONG |
| TotalVolRemaining | LONG |
| Volume | LONG |
| VolumeFilledToday | LONG |
| Price | LONG |
| EntryDateTime | LONG |
| LastModified | LONG |
| ST_ORDER_FLAGS ( Refer Table 19.1 for small endian machines and Table 19.2 for big endian machines) | STRUCT |
| BranchId | SHORT |
| UserId | LONG |
| BrokerId [5] | CHAR |
| Suspended | CHAR |
| Transaction Code | ORDER_MOD_REJECT_TR (20042) ORDER_CANCEL_REJECT_TR (20072) ORDER_CONFIRMATION_TR (20073) ORDER_MOD_CONFIRMATION_TR (20074) ORDER_CXL_CONFIRMATION_TR (20075) ORDER_ERROR_TR (20231) |
| Packet Length | 216 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| Settlor [12] | CHAR |
| ProClient | SHORT |
| SettlementType | SHORT |
| NNFField | DOUBLE |
| TransactionId | LONG |
| Timestamp | LONG LONG |
| PAN | CHAR |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| LastActivityReference | LONG LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is ORDER_MOD_REJECT_TR (20042) ORDER_CANCEL_REJECT_TR (20072) ORDER_CONFIRMATION_TR (20073) ORDER_MOD_CONFIRMATION_TR (20074) ORDER_CXL_CONFIRMATION_TR (20075) ORDER_ERROR_TR (20231) PRICE_CONFIRMATION_TR (20012) |
| TraderId | This field should contain the user ID of the user. |
| TimeStamp2 | This field contains the number of the machine from which the packet is coming. |
| ModCxlBy | This field denotes which person has modified or cancelled a particular order. It should contain one of the following values: • 'T' for Trader • 'B' for Branch Manager • 'M' for Corporate Manager • 'C' for Exchange |
| ReasonCode | This field contains the reason code for a particular order request rejection or order being frozen. This has the details regarding the error along with the error code. This field should be set to zero while sending the request to the host. Refer to Reason Codes in Appendix. |
| SEC_INFO | This structure should contain the Symbol and Series of the security. |
| AccountNumber | If the order is entered on behalf of a trader, the trader account number should be specified in this field. For broker's own order, this field should be set to the broker code. |
| BookType | This field should contain the type of order. Refer to Book Types in Appendix. The Request messages in transaction codes mentioned above must have BookType 1 or 11 or 12. |
| BuySell | This field should specify whether the order is a buy or sell. It should take one of the following values. • '1' for Buy order • '2' for Sell order |
| DisclosedVol | This field should specify the quantity that has to be disclosed to the market. It is not applicable if the order has either the All Or None or the Immediate Or Cancel attribute set. It should not be greater than the volume of the order and not less than the Minimum Fill quantity if the Minimum Fill attribute is set. In either case, it cannot be less than the Minimum Disclosed Quantity allowed. It should be a multiple of the Regular lot. |
| DisclosedVolRemaining | This field contains the disclosed volume remaining from the original disclosed volume after trade(s). This should be set to zero while sending to the host. |
| TotalVolRemaining | This field specifies the total quantity remaining from the original quantity after trade(s). For order entry, this field should be set to Volume. Thereafter, for every response the trading system will return this value. |
| Volume | This field should specify the quantity of the order placed. The quantity should always be in multiples of Regular Lot except for Odd Lot orders and be less than the issued capital. The order will go for a freeze if the quantity is greater than the freeze quantity determined by NSE-Control. |
| VolumeFilledToday | This field contains the total quantity traded in a day. |
| Price | This field should contain the price at which the order is placed. To enter a Market order, the price should be zero. The price must be a multiple of the tick size. For Stop Loss orders, the limit price must be greater than the trigger price in case of a Buy order and less if it is a Sell order. This is to be multiplied by 100 before sending to the trading system host. |
| EntryDateTime | This field should be set to zero while sending the order entry request. |
| LastModified | If the order has been modified, this field contains the time when the order was last modified. It is the time in seconds from midnight of January 1 1980, This field should be set to zero for the order entry request (it is same as Entry Date Time.) |
| Order_Flags | This structure specifies the attributes of an order. They are: • MF if set to 1, represents Minimum Fill attribute. • AON if set to 1, represents All Or None attribute. • IOC if set to 1, represents Immediate Or Cancel attribute. • GTC if set to 1, represents Good Till Cancel. • Day if set to 1, represents Day attribute. This is the default attribute. • SL if set to 1, represents Stop Loss attribute. • Mkt if set to 0, represents a Market order. • ATO if set to 1, represents a market order in PREOPEN or CALL AUCTION1 or CALL AUCTION 2 market. |
|  | • STPC if set to 0, represents order resulting in self-trade to be cancelled as per default action by the exchange if set to 1, represents active order resulting in self-trade to be cancelled Order modification will be rejected if this bit is modified. In case of triggered stop loss order, bit selected during order entry will be considered. • Preopen if set to 1, represents the order is a Preopen session order and if set to 0, represents Normal Market Open order. Preopen bit should be set to 1 for orders in Call Auction 2 market. • Frozen if set to 1, represents the order has gone for a freeze. • Modified if set to 1, represents the order is modified. • Traded if set to 1, represents the order is traded partially or fully. For a market order, the price should be 0. The Bit fields must be set / unset by Front end as mentioned in the description. For CALL AUCTION1 order, if it is market order, ATO bit should set to1& IOC bit needs to be set for mkt as well as limit orders. For CALL AUCTION2 order,ATO& Mkt bit should set to 0 as |
| BranchId | This field should contain the ID of the branch of the particular broker. |
| TraderId | In Request packet, this field should contain the ID of the user on whose behalf order is to be modified/cancelled. This field accepts only numbers. |
| BrokerId | This field should contain the trading member ID. |

| Field Name | Brief Description |
| --- | --- |
| Suspended | This field specifies whether the security is suspended or not. It should be set to blank while sending order entry request. |
| ProClient | This field should contain one of the following values based on the order entering is on behalf of the broker or a trader. '1' - represents the client's order. '2' - represents a broker's order. '4' - represents warehousing order. |
| SettlementType | This field contains the settlement type. It can be one of the following: '0' - T+0 settlement '1' - T+1 settlement This field should be set to zero while sending to the host. |
| NNFField | This field should contain a 15 digit a unique identifier for various products deployed as per Exchange circular download ref no. 16519 dated December 14, 2010, and as updated from time to time |
| Timestamp | Time in this field will be populated in nanoseconds (from 01-Jan- 1980 00:00:00). This time is stamped at the matching engine in the trading system. |
| PAN | This field shall contain the PAN (Permanent Account Number / PAN_EXEMPT) - This field shall be mandatory for all orders (client / participant / PRO orders). |
| Algo ID | For Algo order this field shall contain the Algo ID issued by the exchange. For Non-Algo order, this field shall be Zero(0) |
| Reserved Filler | This field is reserved for future use. This should be set to Zero (0) while sending to the exchange trading system. |
| LastActivityReference | For Order Modification/Cancellation request, this field should contains LastActivityReference value received in response of last activity done on that order. Last activity could be order entry confirmation, order modification confirmation or last trade of that order. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Trimmed Trade Confirmation Structure

## Table 60 MS_TRADE_CONFIRM

| Structure Name | MS_TRADE_CONFIRM_TR |
| --- | --- |
| Transaction Code | TRADE_CONFIRMATION_TR (20222) |
| Packet Length | 192 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| TransactionCode | SHORT |
| LogTime | LONG |
| UserId | LONG |
| TimeStamp | LONG LONG |
| TimeStamp1 | CHAR |
| ResponseOrderNumber | DOUBLE |
| TimeStamp2 | CHAR |
| BrokerId [5] | CHAR |
| TraderNum | LONG |
| BuySell | SHORT |
| AccountNum [10] | CHAR |
| OriginalVol | LONG |
| DisclosedVol | LONG |
| RemainingVol | LONG |
| DisclosedVolRemaining | LONG |
| Price | LONG |
| ST_ORDER_FLAGS ( Refer Table 19.1 for small endian machines and Table 19.2 for big endian machines) | STRUCT |
| FillNumber | LONG |
| FillQty | LONG |
| FillPrice | LONG |
| VolFilledToday | LONG |
| ActivityType [2] | CHAR |
| ActivityTime | LONG |
| SEC_INFO (Refer Table 4) | STRUCT |
| Transaction Code | TRADE_CONFIRMATION_TR (20222) |
| Packet Length | 192 bytes |
| Usage | PRAGMA Pack(2) |
| Field Name | Data Type |
| BookType | SHORT |
| ProClient | SHORT |
| PAN | CHAR |
| Algo ID | LONG |
| Reserved Filler | SHORT |
| LastActivityReference | LONG LONG |
| Reserved | CHAR |

| Field Name | Brief Description |
| --- | --- |
| TransactionCode | The transaction code is TRADE_CONFIRMATION_TR (20222). |
| Timestamp | Time in this field will be populated in nanoseconds (from 01-Jan- 1980 00:00:00). This time is stamped at the matching engine in the trading system. |
| PAN | This field shall contain the PAN |
| Algo ID | This field shall contain the Algo ID |
| Reserved Filler | This field is reserved for future use |
| LastActivityReference | This field shall contain a unique value. Currently the same shall be in nanoseconds. Changes if any shall be notified. |

## Annexure for Encryption/Decryption

## Sr. No. The following are sample function calls of OpenSSL library in Linux (for reference) 1 Note -

- Openssl Library version used is OpenSSL 1.1.1.
- TLS protocol version has been set to 1.3 (TLS1_3_VERSION).

Following are the system library calls for TLS1.3-

## SSL/TLS library initialization →

- SSL_library_init () - Initialize SSL library by registering algorithms.
- OpenSSL_add_all_algorithms ()  -  Adds  all  algorithms  to  the  table  (digests  and ciphers)
- SSL_load_error_strings () - Registers the error strings for all libcrypto and libssl error strings.
- SSL_CTX_new ( TLS_client_method ()) - Create a new SSL_CTX object as framework for TLS/SSL enabled functions.
- SSL_CTX_set_min_proto_version (SSL_CTX  *ctx,  int  version)  -  Set  the  minimum protocol versions to TLS1_3_VERSION.
- SSL_CTX_set_max_proto_version (SSL_CTX  *ctx,  int  version)  -  Set  the  maximum protocol versions to TLS1_3_VERSION.

## Establishing the SSL/TLS connection →

- socket (PF_INET, SOCK_STREAM, 0) - Create TCP socket.
- connect (int  sockfd,  const  struct  sockaddr  *addr,  socklen_t  addrlen)  -  Initiate  the TCP/IP connection with server.
- SSL_new (SSL_CTX *ctx) - Create new SSL connection state.
- SSL_set_fd (SSL *ssl, int fd) - Attach the socket descriptor.
- SSL_connect (SSL *ssl) - Perform the SSL connection.

## Validating the Gateway Router server certificate →

- SSL_get_peer_certificate (const SSL *ssl) - Get the server's certificate.
- X509_STORE_new () - This function returns a new X509_STORE.
- X509_STORE_CTX_new () -This function returns a newly initialised X509_STORE_CTX.

- X509_STORE_load_locations (X509_STORE *ctx, const char *file, const char *dir) Configure files and directories used by a certificate store. The path of CA certificate (gr_ca_cert1.pem) will be used in this function. The CA certificate (gr_ca_cert1.pem) will be provided by the Exchange for validation of Gateway Router certificate.
- X509_STORE_CTX_init (X509_STORE_CTX  *ctx,  X509_STORE  *trust_store,  X509 *target,  STACK_OF(X509)  *untrusted)  -  This  function  returns  a  newly  initialised X509_STORE_CTX structure.
- X509_verify_cert (X509_STORE_CTX  *ctx)  -  This  function  builds  and  verify  X509 certificate chain.

## Send and Receive messages on SSL/TLS connection →

- SSL_write (SSL *ssl, const void *buf, int num) - Send message on SSL.
- SSL_read (SSL *ssl, void *buf, int num) - Receive message from SSL.

## 2 For symmetric encryption/decryption methodology -

```c
Encryption: Initialization → void encrypt_EVP_aes_256_cbc_init(EVP_CIPHER_CTX **ctx, unsigned char *key, unsigned char *iv) { if(!(*ctx = EVP_CIPHER_CTX_new() )) handleErrors(); if(1 != EVP_EncryptInit_ex (*ctx , EVP_aes_256_gcm() , NULL, key, iv)) handleErrors(); } Encryption → void encrypt(EVP_CIPHER_CTX *ctx, unsigned char *plaintext, int plaintext_len, unsigned char *ciphertext, int *ciphertext_len) { int len;
```

- if(1 != EVP_EncryptUpdate (ctx, ciphertext, &len, plaintext, plaintext_len)) handleErrors(); *ciphertext_len = len; } Decryption: Initialization → void decrypt_EVP_aes_256_cbc_init(EVP_CIPHER_CTX **ctx, unsigned char *key, unsigned char *iv) { if(!(*ctx = EVP_CIPHER_CTX_new ())) handleErrors(); if(1 != EVP_DecryptInit_ex (*ctx, EVP_aes_256_gcm (), NULL, key, iv)) handleErrors(); } Decryption → int decrypt(EVP_CIPHER_CTX *ctx, unsigned char *ciphertext, int ciphertext_len, unsigned char *plaintext, int *plaintext_len) { int len; if(1 != EVP_DecryptUpdate (ctx, plaintext, &len, ciphertext, ciphertext_len)) handleErrors(); *plaintext_len = len; } Note -· The ones highlighted in bold are OpenSSL library functions. · plaintext is the actual message buffer. · ciphertext is the encrypted message buffer.