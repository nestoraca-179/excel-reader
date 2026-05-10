declare @year varchar(4) = '2025'
declare @dateFrom varchar(10) = CONCAT('01-01-', @year)
declare @dateTo varchar(10) = CONCAT('31-12-', @year)

set dateformat dmy
--exec RepDocumentoCXCxCliente_GTSC @dfecha_emis_d = '01-01-2025', @dfecha_emis_h = '31-12-2025'
exec RepDocumentoCXPxProveedor_GTSC @dfecha_emis_d = @dateFrom, @dfecha_emis_h = @dateTo