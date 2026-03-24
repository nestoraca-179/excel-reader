from controller.DataController import *
from controller.ExcelController import *
from models.AdmDTO import AdmDto
from models.ConDTO import ConDto

BASE_PATH = r"C:\Temp\ac\developer\python\excel-reader"
EXCEL_FILE_PATH = rf"{BASE_PATH}\2023_test.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**
EXCEL_FILE_RESULT_ADM_PATH = rf"{BASE_PATH}\2023_test_result_adm.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**
EXCEL_FILE_RESULT_CON_PATH = rf"{BASE_PATH}\2023_test_result_con.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**

def main():
    print("🚀 LECTOR EXCEL ADM/CON - INICIANDO...")
    print("=" * 60)

    try:
        # 1. Validar archivo
        if not validate_file(EXCEL_FILE_PATH):
            return

        # 2. Leer hojas
        adm_list: List[AdmDto] = read_adm_sheet(EXCEL_FILE_PATH)
        con_list: List[ConDto] = read_adm_con(EXCEL_FILE_PATH)

        # 3. Mostrar resumen
        print("\n" + "=" * 60)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"📋 Total registros ADM: {len(adm_list):,}")
        print(f"📋 Total registros CON: {len(con_list):,}")
        print(f"📊 Total registros: {len(adm_list) + len(con_list):,}")
        print("\n🎉 DTOs listos para usar en análisis/data science!")

        validate_fact_descriptions_v3(adm_list, con_list)
        validate_adel_descriptions_v2(adm_list, con_list)
        validate_ivan_descriptions(adm_list, con_list)
        validate_islr_descriptions(adm_list, con_list)
        validate_ajpm_descriptions(adm_list, con_list)
        validate_ajnm_descriptions(adm_list, con_list)
        validate_ncr_descriptions(adm_list, con_list)
        write_adm_sheet(EXCEL_FILE_RESULT_ADM_PATH, adm_list)

    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por usuario")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
    finally:
        print("\n👋 Fin del programa")

if __name__ == "__main__":
    main()