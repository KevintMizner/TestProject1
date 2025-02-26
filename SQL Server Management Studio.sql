
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
	WHEN [End Spot] LIKE 'LOT-%' OR [End Spot] LIKE '%Lot%' THEN 'Drop Lot'
    WHEN [End Spot] LIKE '01-%' OR [End Spot] LIKE '02%' THEN 'Building 01'
    WHEN [End Spot] LIKE '03-%' OR [End Spot] LIKE '04%' THEN 'Building 03'
    WHEN [End Spot] LIKE '05-%' THEN 'Building 05'
    WHEN [End Spot] LIKE '14-%' THEN 'Building 14'
    WHEN [End Spot] LIKE '06-%' THEN 'Building 06'
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
    AND Date = '2025-02-19';
