"""
Aplicación Consola - Lector Excel ADM/CON
Analista de Datos & Data Scientist
"""

import time

from controller.DataController import validate_match_advanced, validate_match_inverse
from controller.ExcelController import *
from models.AdmDTO import AdmDto
from models.ConDTO import ConDto

BASE_PATH = r"C:\Temp\ac\developer\python\excel-reader"
EXCEL_FILE_PATH = rf"{BASE_PATH}\2022_test.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**
EXCEL_FILE_RESULT_ADM_PATH = rf"{BASE_PATH}\2022_test_result_adm.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**
EXCEL_FILE_RESULT_CON_PATH = rf"{BASE_PATH}\2022_test_result_con.xlsx"  # ← **ESPECIFICA TU RUTA AQUÍ**

def main():
    print("🚀 LECTOR EXCEL ADM/CON - INICIANDO...")
    print("=" * 60)

    try:
        # 1. Validar archivo
        if not validar_archivo(EXCEL_FILE_PATH):
            return

        # 2. Leer hojas
        lista_adm: List[AdmDto] = leer_hoja_adm(EXCEL_FILE_PATH)
        lista_con: List[ConDto] = leer_hoja_con(EXCEL_FILE_PATH)

        # 3. Mostrar resumen
        print("\n" + "=" * 60)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"📋 Total registros ADM: {len(lista_adm):,}")
        print(f"📋 Total registros CON: {len(lista_con):,}")
        print(f"📊 Total registros: {len(lista_adm) + len(lista_con):,}")
        print("\n🎉 DTOs listos para usar en análisis/data science!")

        # 4. Buscando coincidencias
        print("\n🔍 BUSCANDO COINCIDENCIAS ENTRE ADM Y CON...")
        time.sleep(2)  # Simulación de proceso

        validate_match_advanced(lista_adm, lista_con)
        # escribir_hoja_adm(EXCEL_FILE_RESULT_ADM_PATH, lista_adm)  # Guardar resultados en nueva hoja
        time.sleep(2)

        print("\n🔍 BUSCANDO COINCIDENCIAS ENTRE CON Y ADM...")
        time.sleep(2)  # Simulación de proceso

        validate_match_inverse(lista_con, lista_adm)
        # escribir_hoja_con(EXCEL_FILE_RESULT_CON_PATH, lista_con)  # Guardar resultados en nueva hoja
        time.sleep(2)

    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por usuario")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
    finally:
        print("\n👋 Fin del programa")

if __name__ == "__main__":
    main()