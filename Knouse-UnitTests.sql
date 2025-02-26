
DECLARE @Result INT;
DECLARE @Message NVARCHAR(MAX);
DECLARE @InsertedID INT;


EXEC [dbo].[API_OPENDOC_CREATE_BLDG6_test]
@refNumber = '01172795X',
@status = 'Scheduled',
@action = 'create',
@Scheduled = '2025-02-13T12:31:00.000Z',
@start = '2025-02-26T15:00:00.000Z',
@end = '2025-02-26T15:30:00.000Z',
@userId = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@orgID = '7eb99f17-7482-4fe8-955e-ddad36b7a9f3',
@loadTypeId = 'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',
@dockId = 'f307f75a-85f9-4a32-bffa-3e60929b76fb',
@tags = '',
@createdBy = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@lastChangedby = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@DoorNumber = '',
@SealNumber = '',
@DriverName = '',
@DriverPhone = '',
@TrailerNumber = '',
    
	
	@Result = @Result OUTPUT,
    @Message = @Message OUTPUT,
    @InsertedID = @InsertedID OUTPUT;
	Select  @Result, @Message, @InsertedID




	DECLARE @Result INT;
DECLARE @Message NVARCHAR(MAX);
DECLARE @InsertedID INT;


EXEC [dbo].[API_OPENDOC_CREATE_BLDG6_test]
@refNumber = '01172795',
@status = 'Scheduled',
@action = 'create',
@Scheduled = '2025-02-13T12:31:00.000Z',
@start = '2025-02-26T15:00:00.000Z',
@end = '2025-02-26T15:30:00.000Z',
@userId = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6',
@orgID = '7eb99f17-7482-4fe8-955e-ddad36b7a9f3',
@loadTypeId = 'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',
@dockId = 'f307f75a-85f9-4a32-bffa-3e60929b76fb',
@tags = '',
@createdBy = '46663073-60fd-49f2-8513-8fc6e78a0557',
@lastChangedby = '46663073-60fd-49f2-8513-8fc6e78a0557',
@DoorNumber = '',
@SealNumber = '',
@DriverName = '',
@DriverPhone = '',
@TrailerNumber = '',
    
	
	@Result = @Result OUTPUT,
    @Message = @Message OUTPUT,
    @InsertedID = @InsertedID OUTPUT;
	Select  @Result, @Message, @InsertedID




	SELECT * FROM [dbo].[API_OpenDock_MultiRef_PO_Validation](
'2095076590Z',  
'2025-02-07T18:00:00.000Z',
'680f7179-4969-48d4-a814-9528c472cad9',  
'21c997be-a6b6-4fe3-9084-e14f377c267c', 
'0f38ae3e-3094-4293-881f-0df82015e3ef', 
0
)

-- valid warehouse worker details
	SELECT * FROM [dbo].[API_OpenDock_MultiRef_PO_Validation](
'TEST123',  
'2025-02-18T03:30:00.000Z',
'7eb99f17-7482-4fe8-955e-ddad36b7a9f3',  -- orgid
'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',   -- loadtypeid
'f307f75a-85f9-4a32-bffa-3e60929b76fb',  -- dockid
0
)


	SELECT * FROM [dbo].[API_OpenDock_MultiRef_PO_Validation](
'XYZPDQ',  
'2025-02-27T05:30:00.000Z',
'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',  
'f307f75a-85f9-4a32-bffa-3e60929b76fb', 
'4ddd9e6c-c352-4f31-81eb-6e85cc089e20', 
0
)


ALTER FUNCTION [dbo].[API_OpenDock_MultiRef_PO_Validation](
	
	  @refnum		varchar(255)	--= XYZPDQ8'  -- '0100270202,0100257642'
	, @apptdt		datetime		--= '2025-02-14 12:00'
	, @loadtypeid	varchar(36)		--= '680f7179-4969-48d4-a814-9528c472cad9'  -- '22f93ebe-a119-4615-9b76-293933d23352'
	, @dockid		varchar(36)		--= '21c997be-a6b6-4fe3-9084-e14f377c267c'  -- '02ea9075-e5aa-47cd-a131-a9dc13b11773'
	, @userid		varchar(36)		--= '0f38ae3e-3094-4293-881f-0df82015e3ef' -- '0000865f-348a-4c62-8e09-afa3ea7c4b0d'  -- '044df540-d069-4ecf-aa20-e94ad87cd408'
	, @showdetail	bit				--= 0




DECLARE @Result INT;
DECLARE @Message NVARCHAR(MAX);
DECLARE @InsertedID INT;
EXEC [dbo].[API_OPENDOC_CREATE_BLDG6_TEST]
@refNumber = '5452189J,6182550034,SD1041126',
@status = 'Scheduled',
@action = 'create',
@Scheduled = '2025-02-13T12:31:00.000Z',
@start = '2025-02-26T15:00:00.000Z',
@end = '2025-02-26T15:30:00.000Z',
@userId = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@orgID = '7eb99f17-7482-4fe8-955e-ddad36b7a9f3',
@loadTypeId = 'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',
@dockId = 'f307f75a-85f9-4a32-bffa-3e60929b76fb',
@tags = '',
@createdBy = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@lastChangedby = '4ddd9e6c-c352-4f31-81eb-6e85cc089e20',
@DoorNumber = '',
@SealNumber = '',
@DriverName = '',
@DriverPhone = '',
@TrailerNumber = '',
@Result = @Result OUTPUT,
@Message = @Message OUTPUT,
@InsertedID = @InsertedID OUTPUT
	
	
	
	SELECT  @Result, @Message, @InsertedID

SELECT * from ad_analysis.[Nova].[Dock] where  DockID = 'f307f75a-85f9-4a32-bffa-3e60929b76fb'
select * from  ad_analysis.[Nova].[LoadType] where LoadTypeID =  'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214'
select * from  ad_analysis.[Nova].[Dock] where Dockid = 'f307f75a-85f9-4a32-bffa-3e60929b76fb'


	DECLARE @Result INT;
DECLARE @Message NVARCHAR(MAX);
DECLARE @InsertedID INT;
EXEC [dbo].[API_OPENDOC_CREATE_bldg6_test]
@refNumber = '563285',  
@status = 'Scheduled',
@action = 'create',
@Scheduled = '2025-02-27T11:09:00.000Z',
@start = '2025-03-28T04:00:00.000Z',
@end = '2025-02-18T04:00:00.000Z',
@userId = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6', -- kevint@mizner carrier
@orgID = '7eb99f17-7482-4fe8-955e-ddad36b7a9f3',
@loadTypeId = 'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',
@dockId = 'f307f75a-85f9-4a32-bffa-3e60929b76fb',
@tags = '[TESxcvT2CCC]',
@createdBy = '46663073-60fd-49f2-8513-8fc6e78a0557',
--@lastChangedby = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6',   -- kevint@mizner carrier
@lastChangedby = '46663073-60fd-49f2-8513-8fc6e78a0557', --kthomas @ allen warehouse user
@DoorNumber = '',
@SealNumber = '123',
@DriverName = '',
@DriverPhone = '',
@TrailerNumber = '',
	@Result = @Result OUTPUT,
    @Message = @Message OUTPUT,
    @InsertedID = @InsertedID OUTPUT;
	Select  @Result, @Message, @InsertedID

	SELECT * FROM [dbo].[API_OpenDock_MultiRef_PO_Validation](
'561928',
'2025-03-03T18:00:00.000Z',
'680f7179-4969-48d4-a814-9528c472cad9',  
'21c997be-a6b6-4fe3-9084-e14f377c267c', 
'0f38ae3e-3094-4293-881f-0df82015e3ef', 
0
)



	SELECT userid,UserEmail, FirstName, LastName FROM AD_Analysis.Nova.Users WHERE UserId = '46663073-60fd-49f2-8513-8fc6e78a0557'  -- UNCOMMENT FOR PRODUCTION
    SELECT Carrierid, CarrierEmail, FirstName,LastName  FROM AD_Analysis.Nova.Carrier WHERE CarrierId = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6' -- UNCOMMENT FOR PRODUCTION
  
  SELECT Carrierid,CarrierEmail, FirstName,LastName  FROM AD_Analysis.Nova.Carrier WHERE CarrierEmail = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6' -- UNCOMMENT FOR PRODUCTION

DECLARE @Result INT;
DECLARE @Message NVARCHAR(MAX);
DECLARE @InsertedID INT;
EXEC [dbo].[API_OPENDOC_CREATE]
@refNumber = '563285',
@status = 'Scheduled',
@action = 'create',
@Scheduled = '2025-02-17T11:09:00.000Z',
@start = '2025-02-28T05:30:00.000Z',
@end = '2025-02-18T04:00:00.000Z',
@userId = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6', -- kevint@mizner carrier
@orgID = '7eb99f17-7482-4fe8-955e-ddad36b7a9f3',
@loadTypeId = 'fb1a05b9-c5ba-42f3-a0c4-1080e63eb214',
@dockId = 'f307f75a-85f9-4a32-bffa-3e60929b76fb',
@tags = '[ESTIMATEDTEST]',
@createdBy = '46663073-60fd-49f2-8513-8fc6e78a0557',
@lastChangedby = '0fe4e463-d2a6-4261-95f0-a2b6fdc73fe6',   -- kevint@mizner carrier
--@lastChangedby = '46663073-60fd-49f2-8513-8fc6e78a0557', --kthomas @ allen warehouse user
@DoorNumber = '',
@SealNumber = '123',
@DriverName = '',
@DriverPhone = '',
@TrailerNumber = ''

