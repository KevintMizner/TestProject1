
https://thegeekpage.com/solved-failed-to-enumerate-objects-in-the-container-windows-10-error/

takeown /F X:\FULL_PATH_TO_FOLDER

takeown /F X:\FULL_PATH_TO_FOLDER /r /d y

icacls X:\FULL_PATH_TO_FOLDER /grant Administrators:F

icacls X:\FULL_PATH_TO_FOLDER /grant Administrators:F /t

CREATE TABLE Nova.YMS_DriverEventLog (
    Facility                VARCHAR(100),         -- Facility name
    [Date]                  DATE,                 -- Date
    [Requested By]          VARCHAR(50),          -- Requester's name
    Driver                  VARCHAR(50),          -- Driver name
    [Carrier Company]       VARCHAR(100),         -- Carrier company name
    Scac                    VARCHAR(10),          -- SCAC code
    [Trailer Plate]         VARCHAR(20),          -- Trailer plate number
    [Trailer #]             VARCHAR(50),          -- Trailer number
    [Appt#]                 BIGINT,               -- Appointment number
    Customer                VARCHAR(100),         -- Customer name
    [Load Type]             VARCHAR(50),          -- Load type (new)
    [Vehicle Type]          VARCHAR(50),          -- Vehicle type (new)
    [Start Location]        VARCHAR(100),         -- Start location (new)
    [Start Spot]            VARCHAR(50),          -- Start spot (new)
    [End Location]          VARCHAR(100),         -- End location (new)
    [End Spot]              VARCHAR(50),          -- End spot (new)
    [Request Time]          TIME,                 -- Request time (new)
    [Time In Queue (Minutes)] FLOAT,              -- Time in queue in minutes (new)
    [Accept Time]           TIME,                 -- Accept time (new)
    [Start Time]            TIME,                 -- Start time (new)
    [Complete Time]         TIME,                 -- Complete time (new)
    [Elapsed Time (Minutes)] FLOAT,               -- Elapsed time in minutes
    [Priority Move]         VARCHAR(10),          -- Priority move
    [Priority Load]         VARCHAR(10),          -- Priority load
    Comments                VARCHAR(255),         -- Comments field
    [Move Comments]         VARCHAR(255),         -- Move comments field
    [Cancelled By]          VARCHAR(50),          -- Cancelled by user
    [Cancelled Time]        TIME,                 -- Cancelled time
    [Decline Reason]        VARCHAR(255),         -- Decline reason
    Event                   VARCHAR(255),         -- Event description
    Username                VARCHAR(50)           -- Username
);

GRANT SELECT, INSERT, UPDATE, DELETE ON Nova.YMS_DriverEventLog TO api_interface;


SELECT [InternalId]
      ,[InternalCreateDate]
      ,[InternalModifiedDate]
      ,[WHSE_ID]
      ,[BLDG_ID]
      ,[LINE_NO]
      ,[SKU]
      ,[COMPANY_NO]
      ,[SEQ_NO]
      ,[AISLE]
      ,[ROW_ID]
      ,[TIER]
      ,[MODIFY_USER]
      ,[MODIFY_TSTAMP]
      ,[CREATE_USER]
      ,[CREATE_TSTAMP]
  FROM [Softeon].[ADPROD].[LINE_MASTER_LOCATION]

  where 
  --company_no like 'snyder%'
  --and 
  sku like '0000002007%'
  and 
  BLDG_ID = '18'
  order by sku asc



  SELECT TOP (1000) [Whse_Id]
      ,[Bldg_Id]
	  ,[Aisle]
      ,[Vmi_Id]
      ,[Company_No]
	  ,[Row_Id]
      ,[Sku]
      ,[Pallet_Id]
      ,[Lot_No1]
      ,[Onhand_Qty]
      ,[Qc_Hold_Qty]
      ,[Units_Per_Case]
      ,[No_Cases]
      ,[Aisle]
      ,[Tier]
      ,[Zone_Id]
      ,[Status_Cd1]
      ,[Hold_Reason_cd]
      ,[Loc_Group]
      ,[Loc_Type]
      ,[Loc_Rel_Seq]
      ,[Loc_Chk_Digit]
      ,[Expiry_Date]
      ,[Po_No]
      ,[Create_Tstamp]
      ,[Mfg_Tstamp]
      ,[Modify_Tstamp]
  FROM [Softeon].[ADPROD].[INVENTORY]
  where sku = '000000200790080080'
  and (row_id <> 'cc') and  (row_id  <> 'dr')


SELECT 
      [Appt_Num]
      ,[Appt_Type]
      ,[Ref_1]
      ,[Ref_2]
      ,[Facility]
      ,[Load_Type]
      ,[Open_Dock_Appt_Id]
      ,[Download_Timestamp]
      ,[Customer]
      ,[Appt_Date]
      ,[Appt_Time]
      ,[Arrival_Time]
      ,[Time_In_Yard_Hrs]
      ,[Location]
      ,[Open_Dock_Appt_Id]
      ,[Download_Timestamp]
  FROM [AD_Analysis].[Nova].[YMS_InventorySnapshot]
  WHERE Appt_Type = 'inbound'
  AND Trailer_Status IN ('loaded','unloading')
  AND load_type IN ('Shuttle', 'bulk', 'Floor Load')
  AND ref_1 IS NOT NULL 
  AND Facility IN ('Building 38')  -- Modified line to include both buildings
  ORDER BY ref_1 DESC

  SELECT Date,
    [End Location],
    Facility, 
	[end spot],
    CASE
        WHEN [End Location] LIKE '%Docks-%03%' OR [End Location] LIKE '%Docks-%04%' 
             OR [End Location] LIKE '%Yard-%03%' OR [End Location] LIKE '%Yard-%04%' THEN 'Building 03'
        WHEN [End Location] LIKE '%Docks-%02%' OR [End Location] LIKE '%Docks-%01%' 
             OR [End Location] LIKE '%Yard-%02%' OR [End Location] LIKE '%Yard-%01%' THEN 'Building 01'
        WHEN [End Location] LIKE '%Docks-%05%' OR [End Location] LIKE '%Yard-%05%' THEN 'Building 05'
        WHEN [End Location] LIKE '%Docks-%14%' OR [End Location] LIKE '%Yard-%14%' THEN 'Building 14'
        WHEN [End Location] LIKE '%Docks-%06%' OR [End Location] LIKE '%Yard-%06%' THEN 'Building 06'
        WHEN [End Location] LIKE '%Building 6 Yard%' OR [End Location] LIKE '%Building 6 Docks%' THEN 'Building 06'
        WHEN [End Location] LIKE '%Building 14 Yard%' OR [End Location] LIKE '%Building 14 Docks%' THEN 'Building 14'
        WHEN [End Location] LIKE '%1-5%' AND ([End Location] LIKE '%LOT%' OR [End Location] LIKE '%Lot%') THEN 'Drop Lot'
        ELSE Facility
    END AS ComputedFacility
FROM [AD_Analysis].[Nova].[YMS_DriverEventLog]
WHERE 
    [End Location] LIKE '%Docks-%03%' OR [End Location] LIKE '%Docks-%04%'
    OR [End Location] LIKE '%Yard-%03%' OR [End Location] LIKE '%Yard-%04%'
    OR [End Location] LIKE '%Docks-%02%' OR [End Location] LIKE '%Docks-%01%'
    OR [End Location] LIKE '%Yard-%02%' OR [End Location] LIKE '%Yard-%01%'
    OR [End Location] LIKE '%Docks-%05%' OR [End Location] LIKE '%Yard-%05%'
    OR [End Location] LIKE '%Docks-%14%' OR [End Location] LIKE '%Yard-%14%'
    OR [End Location] LIKE '%Docks-%06%' OR [End Location] LIKE '%Yard-%06%'
    OR [End Location] LIKE '%Building 6 Yard%' OR [End Location] LIKE '%Building 6 Docks%'
    OR [End Location] LIKE '%Building 14 Yard%' OR [End Location] LIKE '%Building 14 Docks%'
	OR [END LOCATION] like '%6 & 14%' or [END LOCATION] like '%1-5%'
    OR ([End Location] LIKE '%1-5%' AND ([End Location] LIKE '%LOT%' OR [End Location] LIKE '%Lot%'));


This SQL will update tha the table with the correct Facility translations :

UPDATE [AD_Analysis].[Nova].[YMS_DriverEventLog]
SET Facility = CASE
    WHEN [End Location] LIKE '%Docks-%03%' OR [End Location] LIKE '%Docks-%04%' 
         OR [End Location] LIKE '%Yard-%03%' OR [End Location] LIKE '%Yard-%04%' THEN 'Building 03'
    WHEN [End Location] LIKE '%Docks-%02%' OR [End Location] LIKE '%Docks-%01%' 
         OR [End Location] LIKE '%Yard-%02%' OR [End Location] LIKE '%Yard-%01%' THEN 'Building 01'
    WHEN [End Location] LIKE '%Docks-%05%' OR [End Location] LIKE '%Yard-%05%' THEN 'Building 05'
    WHEN [End Location] LIKE '%Building 14 Yard%' OR [End Location] LIKE '%Building 14 Docks%'  
         OR LEFT([End Spot], 2) = '14' THEN 'Building 14' -- Prioritize Building 14
    WHEN [End Location] LIKE '%Building 6 Yard%' OR [End Location] LIKE '%Building 6 Docks%' THEN 'Building 06'
    WHEN [End Location] LIKE '%Docks-%06%' OR [End Location] LIKE '%Yard-%06%' THEN 'Building 06'
    WHEN [End Location] LIKE '%1-5%' AND ([End Location] LIKE '%LOT%' OR [End Location] LIKE '%Lot%') THEN 'Drop Lot'
    ELSE Facility
END
WHERE 
    ([End Location] LIKE '%Docks-%03%' OR [End Location] LIKE '%Docks-%04%'
    OR [End Location] LIKE '%Yard-%03%' OR [End Location] LIKE '%Yard-%04%'
    OR [End Location] LIKE '%Docks-%02%' OR [End Location] LIKE '%Docks-%01%'
    OR [End Location] LIKE '%Yard-%02%' OR [End Location] LIKE '%Yard-%01%'
    OR [End Location] LIKE '%Docks-%05%' OR [End Location] LIKE '%Yard-%05%'
    OR [End Location] LIKE '%Docks-%14%' OR [End Location] LIKE '%Yard-%14%'
    OR [End Location] LIKE '%Docks-%06%' OR [End Location] LIKE '%Yard-%06%'
    OR [End Location] LIKE '%Building 6 Yard%' OR [End Location] LIKE '%Building 6 Docks%'
    OR [End Location] LIKE '%Building 14 Yard%' OR [End Location] LIKE '%Building 14 Docks%'
    OR [End Location] LIKE '%6 & 14%' OR [End Location] LIKE '%1-5%'
    OR ([End Location] LIKE '%1-5%' AND ([End Location] LIKE '%LOT%' OR [End Location] LIKE '%Lot%')))
    AND Date = '2024-12-20';
