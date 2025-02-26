# How to refire 945 (T4) Transactions for Bradford White

## Description

Bradford White receives 945 (what they refer to a T4s) via an API transaction.  If a transaction is requested to be resent you will need to run the following SQL statement :

```
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW925821804'

```

The value BW925821804 would be resplaced the delivery number with a BW as the prefix.

When the API call is made to send the trasnactions, the following Stored Procedure is run.

```
USE [ASCTracEDI856]
GO
/****** Object:  StoredProcedure [dbo].[API_945_REQUEST_BRAWHI]    Script Date: 7/8/2024 3:42:22 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER PROCEDURE [dbo].[API_945_REQUEST_BRAWHI]
	-- Add the parameters for the stored procedure here
@customer as varchar(max) = NULL
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
SELECT       salesOrder as salesOrderNumber, lineNumber as salesOrderLineNumber, itemNumber,itemDescription, requestedQuantity, uomCode, 
coalesce(customerPo, '') as custPoNumber, serialNumber, trailerNumber, billOfLading, carrierCode, locationId,
shipDate, sealNumber, proNum, deliveryId, tripStopNumber,shipmentTotalUnits, warehouseId, '01' as partnerId, proNum as projectNumber, shipDate as [dateTime],
'PROD' as environment, shipmentNumber, warehouseId, '01' as partnerId, shippingMethod,
 NULL as shipmentCost, shipAddress, serialNumber as ContainerNumber, tripNumber , uomCode as unitOfMeasure,  requestedQuantity as quantityShipped
FROM            tbl_asctohost_BW_API_945_request order by  shipmentNumber, salesOrder, salesOrderLineNumber;

delete from tbl_asctohost_BW_API_945_request;

END;
```

## Email support example 

```email
Good morning Allen Team

Can you please resend T4 for Trip 4325545 Deliveries 925821804, 925947128, 925954034, 926146683, 926178855?

Thank you
```

The following SQL would be executed 

```SQL
--Execute on production server sql-wmsag

USE [ASCTracEDI856]
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW925821804'
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW925947128'
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW925954034'
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW926146683'
update asctracedi856.dbo.EDI856_SHIPMENT set record_sent ='N', DATETIME_SENT = getdate() where SHIPMENT_ID = 'BW926178855'
```

These transactions will be swept up the next time the API call is made.

## Contact

Contact EDISupport@allendistribution.com for support. 

This `README.md` provides both a layman's summary and a section with technical details, including instructions on setting up and running the scripts.
```

This version should render correctly on most Markdown editors and viewers. If you still face issues, please let us know the specific rendering problem you're encountering.




# AD/BWC Team

- Please save the following instructions when you run across a Link # that can’t be found or is missing information. This is applicable for missing stops, deliveries, items, quantities, and carriers.


- 1.	AD Notifies BWC they Can’t find the link # or are missing data
- 2.	BWC checks PBI T3 Response summary 3PL Shipment Verification - Power BI (BWC use only)
a.	Result-Failure
i.	BWC provides Delivery(Customer Order #) associate with Link #, AD looks up Delivery(Customer Order #) associate with Link #
ii.	If Delivery(Customer Order #) found and open in ASC, then AD unschedules/Unpicks Order, AD Communicates this has been completed, and BWC retransmits T3
iii.	If Delivery(Customer Order #) found and cancelled in ASC, Then BWC deletes delivery, creates new delivery, adds new delivery to Link #, and BWC retriggers T3, BWC reviews that it was successfully transmitted in PBI T3 Response summary, and AD verifies they now see new delivery . 
iv.	If Delivery(Customer Order #) found and shipped in ASC , Then BWC needs to work internal processes for T4 errors. 
b.	Result-Success
i.	AD needs to reach out to their EDI team for support as our system shows it was imported correctly. 

Any questions let me know

Thanks

Ben Shinn


G:\EDI\ASC\BRAWHI-Upload\Temp