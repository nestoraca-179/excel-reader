declare @year varchar(4) = '2025'
declare @dateFrom varchar(10) = CONCAT('01-01-', @year)
declare @dateTo varchar(10) = CONCAT('31-12-', @year)

set dateformat dmy
--exec RepMayorAnalitico2KDoce_GTSC_AUX @sco_cue_d = '1.1.03.01.001', @sco_cue_h = '1.1.03.01.001', @sdfec_emis_d = '01-01-2025', @sdfec_emis_h = '31-12-2025'
exec RepMayorAnalitico2KDoce_GTSC_AUX @sco_cue_d = '2.1.02.01.001', @sco_cue_h = '2.1.02.01.001', @sdfec_emis_d = @dateFrom, @sdfec_emis_h = @dateTo