UPDATE [AD_Analysis].[Nova].[YMS_DriverEventLog] 
SET Facility = 
    CASE 
        -- ✅ 'Building 03' Mapping
        WHEN LEFT(LTRIM(RTRIM([End Spot])), 2) IN ('03', '04') THEN 'Building 03'

        -- ✅ 'Building 01' Mapping
        WHEN LEFT(LTRIM(RTRIM([End Spot])), 2) IN ('02', '01') THEN 'Building 01'

        -- ✅ 'Building 05' Mapping (Fix for 05-DR-02)
        WHEN LEFT(LTRIM(RTRIM([End Spot])), 2) = '05' 
        OR UPPER([End Location]) LIKE '%DOCKS-05%' 
        OR UPPER([End Location]) LIKE '%YARD-05%' 
        THEN 'Building 05'

        -- ✅ 'Building 14' Mapping
        WHEN LEFT(LTRIM(RTRIM([End Spot])), 2) = '14' 
        OR UPPER([End Location]) LIKE '%DOCKS-14%' 
        OR UPPER([End Location]) LIKE '%YARD-14%' 
        OR UPPER([End Location]) LIKE '%BUILDING 14%' 
        THEN 'Building 14'

        -- ✅ 'Building 06' Mapping
        WHEN LEFT(LTRIM(RTRIM([End Spot])), 2) = '06' 
        OR UPPER([End Location]) LIKE '%DOCKS-06%' 
        OR UPPER([End Location]) LIKE '%YARD-06%' 
        OR UPPER([End Location]) LIKE '%BUILDING 06%'
        THEN 'Building 06'

        -- ✅ 'Drop Lot' Mapping (If 'LOT' appears anywhere in End Spot)
        WHEN UPPER(LTRIM(RTRIM([End Spot]))) LIKE '%LOT%' 
        THEN 'Drop Lot'

        ELSE Facility  
    END
WHERE 
    -- 🔹 Only update relevant records
    (
        UPPER([End Location]) LIKE '%DOCKS-%' 
        OR UPPER([End Location]) LIKE '%YARD-%' 
        OR UPPER([End Location]) LIKE '%BUILDING 14%' 
        OR UPPER([End Location]) LIKE '%BUILDING 06%' 
        OR LEFT(LTRIM(RTRIM([End Spot])), 2) IN ('03', '04', '02', '01', '05', '06', '14') 
        OR UPPER(LTRIM(RTRIM([End Spot]))) LIKE '%LOT%'  -- ✅ Ensure 'LOT' detection works
    )
    AND [Date] >= '2024-12-20';  -- ✅ Ensure correct date filter
