USE [ASCTracEDI856]
GO
/****** Object:  StoredProcedure [dbo].[API_OPENDOC_CREATE_BLDG6_TEST]    Script Date: 2/24/2025 11:14:57 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[API_OPENDOC_CREATE_BLDG6_TEST] 
    @refNumber VARCHAR(MAX), 
    @status VARCHAR(50), 
    @action VARCHAR(50), 
    @Scheduled VARCHAR(50), 
    @start VARCHAR(50), 
    @end VARCHAR(50), 
    @userId VARCHAR(50), 
    @orgID VARCHAR(50), 
    @loadTypeId VARCHAR(50), 
    @dockId VARCHAR(50), 
    @tags VARCHAR(50), 
    @createdBy VARCHAR(50), 
    @lastChangedby VARCHAR(50), 
    @DoorNumber VARCHAR(50), 
    @SealNumber VARCHAR(50), 
    @DriverName VARCHAR(50), 
    @DriverPhone VARCHAR(50), 
    @TrailerNumber VARCHAR(50), 
    @Result INT OUTPUT, 
    @Message NVARCHAR(MAX) OUTPUT, 
    @InsertedID INT OUTPUT
AS
BEGIN
	SET NOCOUNT ON;
	DECLARE @BitStatus NVARCHAR(50)
	DECLARE @Source VARCHAR(100);
	DECLARE @USER_EMAIL NVARCHAR(255);
	DECLARE @WHSE_EMAIL NVARCHAR(255);
	DECLARE @USER_FNAME NVARCHAR(100);
	DECLARE @USER_LNAME NVARCHAR(100);
	DECLARE @EmailSubject NVARCHAR(255);
	DECLARE @EmailBody NVARCHAR(MAX);
    SET @InsertedID = 111; 
	DECLARE @EmailSent BIT = 0; -- Track if email has been sent

	

-- Default source to 'W' (Warehouse)
/*  START Determine if the user is a warehouse employee (all IsCarrier values = 0) */
-- Attempt to find user in Nova.Users
	SELECT @USER_EMAIL = UserEmail, 
		   @USER_FNAME = FirstName, 
		   @USER_LNAME = LastName 
	FROM AD_Analysis.Nova.Users 
	WHERE UserId = @lastChangedby;

-- ✅ If warehouse user exists, exit immediately with success
	IF @USER_EMAIL IS NOT NULL
		BEGIN

			SET @EmailSubject = 'Appointment Made but Not Validated - Please Read';

			-- Define email body with proper formatting
			SET @EmailBody = 
				'Dear ' + @USER_FNAME + ' ' + @USER_LNAME + ',' + CHAR(13) + CHAR(10) + 
				CHAR(13) + CHAR(10) + 
				'The appointment reference numbers were not validated since you are a warehouse employee.' + CHAR(13) + CHAR(10) + 
				'This means the appointment data MUST be entered in the WMS and you will need to update it manually.' + CHAR(13) + CHAR(10) + 
				CHAR(13) + CHAR(10) + 
				'Best regards,' + CHAR(13) + CHAR(10) + 
				'Allen Systems Integration Services';

			-- Send Email
		EXEC msdb.dbo.sp_send_dbmail
			@profile_name = 'Allen_Distribution_Scheduling',
			@recipients = @USER_EMAIL,  -- Send to the logged-in user
			@blind_copy_recipients = 'kevint@mizner.com;acrider@allendistribution.com',  -- Add CC recipient(s)
			@subject = @EmailSubject,
			@body = @EmailBody,
			@body_format = 'TEXT';  -- Plain text email

		SET @Result = 1;  -- Success
		SET @Message = 'User found in Nova.Users, exiting procedure.';
		RETURN;
		END;

-- -- PRINT  'checking if carrier'

-- If no user found, check in Nova.Carrier table
SET @Source = 'C';  -- Switch source to Carrier
SELECT @USER_EMAIL = CarrierEmail, 
       @USER_FNAME = FirstName, 
       @USER_LNAME = LastName  
FROM AD_Analysis.Nova.Carrier 
WHERE CarrierId = @lastChangedby;

-- ✅ If user doesn't exist in either table, log error and exit
	IF @USER_EMAIL IS NULL
		BEGIN
			SET @Result = 0;  -- Indicate failure
			SET @Message = 'User record not found in either Users or Carrier table.';

			-- Log error
			UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG 
			SET DBField = 'USER_NOT_FOUND', SOURCE = @Source 
			WHERE ID = @InsertedID;

			-- Return failure message
			
			RETURN;  -- Exit stored procedure
		END;


 



-- END Determine if the user is a warehouse employee (all IsCarrier values = 0)
-- PRINT  @USER_EMAIL
    -- Insert Log Entry
    INSERT INTO ASCTracEDI856.[dbo].[API_OPENDOCK_LOG_SOFTEON] (
        refNumber, status, action, Scheduled, start, [end], userId, orgID,
        loadTypeId, dockId, tags, createdBy, lastChangedby, LogEntryTS,
        DoorNumber, SealNumber, DriverName, DriverPhone, TrailerNumber,UserEmail,Error
    )
    VALUES (
        @refNumber, @status, @action, @Scheduled, @start, @end, @userId, @orgID,
        @loadTypeId, @dockId, @tags, @createdBy, @lastChangedby, GETDATE(),
        @DoorNumber, @SealNumber, @DriverName, @DriverPhone, @TrailerNumber, @USER_EMAIL, 'X'
    );



 
 -- Get the newly inserted Log Entry ID
    SET @InsertedID = SCOPE_IDENTITY();

    -- Create Temporary Table
    CREATE TABLE #TempValidationResults (
        RefNum VARCHAR(35),
        LocalAppt DATETIME,
		IsValidRef BIT,
        AllValidRef BIT,
        NoMixedRef BIT,
        IsValidDock BIT,
        IsValidCust BIT,
		IsValidAppt BIT,
		IsValidWhse BIT,
        IsCustMatch BIT,
        IsValidUser BIT,
        IsCarrier BIT,
        Customer VARCHAR(100),
        LoadType VARCHAR(50),
        DockName VARCHAR(100),
        Direction VARCHAR(50),
        UserName VARCHAR(100),
        UserEmail VARCHAR(100),
        Sku VARCHAR(50),
        Cases INT,
        Plts INT,
        OrderWeight INT,
        RefField VARCHAR(50),
        ShipRefNum VARCHAR(50),
        PoNum VARCHAR(50),
        RefOrdNum VARCHAR(50),
        BolNum VARCHAR(50),
        SeqNum INT,
        ReqShipDate DATE,
        ShipToName VARCHAR(150),
        ShipToAddr VARCHAR(150),
        ShipToAddr2 VARCHAR(150),
        ShipToCity VARCHAR(100),
        ShipToState VARCHAR(50),
        ShipToZip VARCHAR(20),
        RowNum INT,
        ShipWeight INT,
		BldgPhone VARCHAR(20),
		BldgAddr VARCHAR(150),
		BldgCity VARCHAR(100),
        BldgState VARCHAR(50),
        BldgZip VARCHAR(20),
		BldgEmail VARCHAR(100)
    );

    INSERT INTO #TempValidationResults
    	SELECT * FROM [dbo].[API_OpenDock_MultiRef_PO_Validation](
	  @refnumber,
	  @start,	
	  @loadtypeid,
	  @dockid,		
	  @userid,		
	  0					
	  )

	 

-- Select * from #TempValidationResults

/*******************************************************************************/
-- START Determine if all some or none of the ref numbers were found or are valid
/*******************************************************************************/

DECLARE @ValidationStatus NVARCHAR(255);
DECLARE @RecordCount INT;


-- Debug: Start
-- -- PRINT 'DEBUG: Starting validation process...';

-- Check if there are any records in the table
SELECT @RecordCount = COUNT(*) FROM #TempValidationResults;

-- Debug: Check record count
-- -- PRINT 'DEBUG: Total Records Found = ' + CAST(@RecordCount AS NVARCHAR(10));

-- If no records exist, set an error message and exit
IF @RecordCount = 0
BEGIN
    SET @ValidationStatus = 'Error: The reference number(s) supplied did not match and validate against any orders in our system';
    SET @Result = 0;  -- Indicate failure

    -- Debug: Log the error
    -- -- PRINT 'DEBUG: No records found. Setting validation status: ' + @ValidationStatus;

    -- Log the error in API_OPENDOCK_LOG_SOFTEON
    UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG_SOFTEON
    SET Error = @ValidationStatus
    WHERE ID = @InsertedID;

    ---- -- PRINT 'DEBUG: Error logged to API_OPENDOCK_LOG_SOFTEON for ID ' + CAST(@InsertedID AS NVARCHAR(10));

    -- Send an email notification
    -- -- PRINT 'DEBUG: Sending email to ' + @USER_EMAIL;
    SET @EmailSubject = 'Opendock Validation Failed: No Records Found - ' + @refnumber;
	EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'Allen_Distribution_Scheduling',
        @recipients = @USER_EMAIL,
		@blind_copy_recipients = 'kevint@mizner.com;', -- CC recipient(s)
        @subject = @EmailSubject,
        @body = @ValidationStatus,
        @body_format = 'TEXT';  -- Plain text email
	
	SET @EmailSent = 1; -- Mark email as sent    

	RETURN;  -- Exit procedure early
END


-- Debug: Proceeding with validation checks
-- PRINT 'DEBUG: Records found, proceeding with validation checks...';

    
    -- Additional check for mixed reference numbers
	IF (SELECT MIN(IsValidRef + 0) FROM #TempValidationResults) = 0
    BEGIN
        SET @ValidationStatus = 'Opendock Validation failed: One or more reference numbers are invalid.';
            UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG_SOFTEON SET Error = @ValidationStatus WHERE ID = @InsertedID;
	PRINT @ValidationStatus
		SET @Message =@ValidationStatus
		SET @Result = 0;
		RETURN;
    END;

	ELSE IF (SELECT MIN(AllValidRef + 0) FROM #TempValidationResults) = 0
    BEGIN
        SET @ValidationStatus = 'Opendock Validation failed: One or more reference numbers are invalid.';
            UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG_SOFTEON SET Error = @ValidationStatus WHERE ID = @InsertedID;
	PRINT @ValidationStatus
		SET @Message =@ValidationStatus
		SET @Result = 0;
		RETURN
    END;

	ELSE IF (SELECT MIN(NoMixedRef + 0) FROM #TempValidationResults) = 0
    BEGIN
        SET @ValidationStatus = 'Reference numbers must all be of the same type - PO, Sales Order, or Shipment Ref Numbers.';
            UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG_SOFTEON SET Error = @ValidationStatus WHERE ID = @InsertedID;
	PRINT @ValidationStatus
		SET @Message =@ValidationStatus
		SET @Result = 0;  
		RETURN
    END;


    -- Send an email notification

	/*
	EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'Allen_Distribution_Scheduling',
        @recipients = @USER_EMAIL,
        @blind_copy_recipients = 'kevint@mizner.com;acrider@allendistribution.com', -- BCC recipients
        @subject = @EmailSubject,
        @body = @ValidationStatus,
        @body_format = 'TEXT';  -- Plain text email
    */
	SET @EmailSent = 1; 
	



DECLARE @MaxReqShipDate DATE;
DECLARE @LocalAppt DATETIME;
DECLARE @RefNumDateIssue VARCHAR(100);
-- Get the maximum requested ship date and corresponding LocalAppt from the same row
SELECT TOP 1 
    @MaxReqShipDate = ReqShipDate,
    @LocalAppt = LocalAppt,
	@RefNumDateIssue = RefNum


FROM #TempValidationResults
ORDER BY ReqShipDate DESC; -- Ensures we get the row with the latest requested ship date

-- Debugging: Print values to verify
--PRINT 'Max Requested Ship Date: ' + CONVERT(NVARCHAR, @MaxReqShipDate, 120);
--PRINT 'Local Appointment: ' + CONVERT(NVARCHAR, @LocalAppt, 120);

-- Check if appointment is scheduled before the max requested ship date
IF @LocalAppt < CAST(@MaxReqShipDate AS DATETIME)  -- Ensure consistent data type
BEGIN
    -- Set failure result and message
    SET @Result = 0;
    SET @ValidationStatus = 
        'You cannot make an appointment for ' + @RefNumDateIssue + ' before ' + CONVERT(NVARCHAR, @MaxReqShipDate, 120) + 
        '. Please book on or after ' + CONVERT(NVARCHAR, @MaxReqShipDate, 120) + '.';

    -- Log the failure
    UPDATE ASCTracEDI856.dbo.API_OPENDOCK_LOG_SOFTEON 
    SET Error = 'Datre Issue' 
    WHERE ID = @InsertedID;

 
  

 
 -- Send an email notification (uncomment when testing is complete)
    SET @EmailSubject = 'APPT DATE ISSUE - PLEASE READ';
    EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'ReportServer',
        @recipients = @USER_EMAIL,
        @blind_copy_recipients = 'kevint@mizner.com;acrider@allendistribution.com', -- BCC recipient(s)
        @subject = @EmailSubject,
        @body = @ValidationStatus,
        @body_format = 'TEXT';  -- Plain text email
    

    
	-- Exit stored procedure
    SET @Result = 0;
    SET @Message = @ValidationStatus;
    RETURN;
END;




   -- Calculate total Order Weight
    DECLARE @TotalOrderWeight INT;
	DECLARE @BldgPhone NVARCHAR(20);
	DECLARE @BLDG_ADDR  NVARCHAR(255);
 	DECLARE @BLDG_CITY   NVARCHAR(100);
	DECLARE @BLDG_STATE  NVARCHAR(100);
	DECLARE @BLDG_ZIP  NVARCHAR(100);
	DECLARE @BLDG_EMAIL NVARCHAR(100);
	DECLARE @BLDG_PHONE NVARCHAR(20);

-- Step 1: Get SUM(OrderWeight) separately
SELECT @TotalOrderWeight = SUM(OrderWeight)
FROM #TempValidationResults;

-- Step 2: Get the latest ReqShipDate and corresponding LocalAppt
SELECT TOP 1 
    @MaxReqShipDate = CAST(ReqShipDate AS DATE),
    @LocalAppt = CAST(LocalAppt AS DATETIME),
	@WHSE_EMAIL =  CAST(Bldgemail AS NVARCHAR(255)),
	@BLDG_ADDR = CAST(Bldgaddr AS NVARCHAR(255)),
	@BLDG_CITY =  CAST(BldgCity AS NVARCHAR(100)),
	@BLDG_STATE = CAST(BldgState AS NVARCHAR(100)),
	@BLDG_ZIP = CAST(BldgZip AS NVARCHAR(20)),
	@BLDG_EMAIL = CAST(Bldgemail AS NVARCHAR(100)),
	@BLDG_PHONE = CAST(BldgPhone AS NVARCHAR(20))
FROM #TempValidationResults
ORDER BY ReqShipDate DESC;

PRINT @TotalOrderWeight

PRINT @BLDG_ADDR 
PRINT @BLDG_PHONE
PRINT @BLDG_EMAIL

 -- Debugging Output
  PRINT  @TotalOrderWeight 
  PRINT 'DEBUG: @MaxReqShipDate = ' + ISNULL(CONVERT(NVARCHAR, @MaxReqShipDate, 120), 'NULL');
  PRINT 'DEBUG: @LocalAppt = ' + ISNULL(CONVERT(NVARCHAR, @LocalAppt, 120), 'NULL');

-- Step 3: Convert LocalAppt for HTML email concatenation
DECLARE @LocalApptStr NVARCHAR(50);
SET @LocalApptStr = FORMAT(@LocalAppt, 'yyyy-MM-dd HH:mm');
 PRINT  @LocalApptStr 



    -- Create HTML Email
    DECLARE @Header NVARCHAR(MAX), @Row NVARCHAR(MAX);


DECLARE @Signature NVARCHAR(MAX);

SET @Signature = 
N'<br><br>
<h2>Contact Information</h2>
<table style="border-collapse: collapse; width: 100%;">
    <tr>
        <td style="font-weight: bold;">Email:</td>
        <td>' + ISNULL(@BLDG_EMAIL, 'No Email Available') + N'</td>
    </tr>
    <tr>
        <td style="font-weight: bold;">Phone:</td>
        <td>' + ISNULL(@BLDG_PHONE, 'No Phone Available') + N'</td>
    </tr>
    <tr>
        <td style="font-weight: bold;">Address:</td>
        <td>' + ISNULL(@BLDG_ADDR, 'No Address Available') + ', ' 
            + ISNULL(@BLDG_CITY, '') + ', ' 
            + ISNULL(@BLDG_STATE, '') + ' ' 
            + ISNULL(@BLDG_ZIP, '') + N'</td>
    </tr>
</table>
<br>
<p>Best regards,</p>
<p><strong>Allen Distribution</strong></p>
</body>
</html>';




-- Construct Email Body
SET @EmailBody = 
N'<html>
<head><style>
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid black; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
</style></head>
<body>
<h2>Appointment Details - Ref# ' + ISNULL(@refNumber, 'Unknown Ref') + N'</h2>
<p>This is a follow-up email regarding your pickup details:</p>
<p>Thank you for scheduling your appointment. Your appointment will be reviewed, and if any changes need to be made, we will contact you.</p>
<br>
<p>If you have any questions or require additional assistance, please call ' + @BLDG_PHONE + N'.</p>
<br>
<h2>Order Shipment Details</h2>
<p><strong>Pickup Date/Time:</strong> ' + ISNULL(@LocalApptStr, 'No Appointment Scheduled') + N'</p>
<p><strong>Est Ship Weight:</strong> ' + CAST(FORMAT(ISNULL(@TotalOrderWeight, 0), 'N0') AS NVARCHAR) + N' lbs</p>

<table>
<tr>
    <th>Ship Ref #</th>
    <th>PO #</th>
    <th>Order #</th>
    <th>Order Wt.</th>
    <th>Req Ship Date</th>
    <th># of Cases</th>
    <th>Ship To Name</th>
    <th>Ship To Address</th>
    <th>Ship To Address 2</th>
    <th>Ship To City</th>
    <th>Ship To State</th>
    <th>Ship To Zip</th>
</tr>';

-- Initialize row content
SET @Row = '';

-- Populate HTML Table Rows
SELECT @Row = @Row + 
N'<tr>
    <td>' + ISNULL(ShipRefNum, '') + '</td>
    <td>' + ISNULL(PoNum, '') + '</td>
    <td>' + ISNULL(RefOrdNum, '') + '</td>
    <td>' + FORMAT(ISNULL(OrderWeight, 0), 'N0') + ' lbs. </td>
    <td>' + ISNULL(FORMAT(ReqShipDate, 'yyyy-MM-dd'), '') + '</td>
    <td>' + ISNULL(CAST(Cases AS NVARCHAR(10)), '') + '</td>
    <td>' + ISNULL(ShipToName, '') + '</td>
    <td>' + ISNULL(ShipToAddr, '') + '</td>
    <td>' + ISNULL(ShipToAddr2, '') + '</td>
    <td>' + ISNULL(ShipToCity, '') + '</td>
    <td>' + ISNULL(ShipToState, '') + '</td>
    <td>' + ISNULL(ShipToZip, '') + '</td>
</tr>'
FROM #TempValidationResults;

-- Append rows and signature block
SET @EmailBody = @EmailBody + @Row + '</table>' + @Signature;

-- Debugging: Print Output (Optional)
PRINT @EmailBody;


DECLARE @FinalCC NVARCHAR(500);  -- Variable for the final BCC list to include warehouse email if not null
-- Initialize the BCC list with the default recipients
SET @FinalCC = '';

-- If WHSE_EMAIL is not NULL, append it to the BCC list
IF @WHSE_EMAIL IS NOT NULL
    SET @FinalCC = @WHSE_EMAIL
	PRINT @FinalCC

    -- Send the Email
    EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'REportServer',
        @recipients = @USER_EMAIL,
		@copy_recipients = @FinalCC,
		@blind_copy_recipients = 'kevint@mizner.com;acrider@allendistribution.com', -- CC recipient(s)
        @subject = 'Opendock Appointment Confirmation [IMPORTANT]',
        @body = @EmailBody,
        @body_format = 'HTML';

    -- Drop the temp table
    DROP TABLE #TempValidationResults;


 SET @ValidationStatus = 'Appointment verified and processed successfully.';

 PRINT @ValidationStatus
 PRINT @InsertedID

       UPDATE dbo.API_OPENDOCK_LOG_SOFTEON SET Error = @ValidationStatus, Validated =1 WHERE ID = @InsertedID;

    -- Final Output Success
    SET @Result = 1;
    SET @message = 'Appointment verified and processed successfully.';
    RETURN; 
END;
