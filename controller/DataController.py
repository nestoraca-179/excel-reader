import time
from typing import List

from models.AdmDTO import AdmDto
from models.ConDTO import ConDto

def validate_match_advanced(lista_adm: List[AdmDto], lista_con: List[ConDto]):
    """Valida: 1) nro_doc (ADM) == docref (CON) Y 2) co_cli (ADM) ⊆ descri (CON)"""
    print("\n" + "=" * 90)
    print("🔍 VALIDACIÓN AVANZADA: nro_doc (ADM) == docref (CON) + co_cli ⊆ descri")
    print("=" * 90)

    total_matches = 0
    total_no_matches = 0
    total_acc_saldo_new = 0.0

    # Crear diccionario para búsqueda O(1) en CON
    docref_index = {}
    for i, dto in enumerate(lista_con):
        index = str(int(float(dto.docref or 0))) + "/" + str(abs(float(dto.MontoD or dto.MontoH)))
        if index not in docref_index:
            docref_index[index] = i + 2

    for idx_adm, adm in enumerate(lista_adm, 1):
        co_tipo_doc_adm = adm.co_tipo_doc.strip()
        nro_doc_adm = adm.nro_doc.strip()
        co_cli_adm = adm.co_cli.strip().upper()
        total_neto_adm = abs(adm.total_neto)
        saldo_new_adm = adm.saldo_new
        index_to_search = nro_doc_adm + "/" + str(total_neto_adm)

        if co_tipo_doc_adm == "ISLR":
            # print(f"⏭️  Ignorado por tipo_doc 'ISLR' - {saldo_new_adm}")
            total_no_matches += 1
            continue

        if index_to_search in docref_index:
            fila_con = docref_index[index_to_search]
            registro_con = lista_con[fila_con - 2]  # Convertir fila Excel a índice Python
            descrip_con = str(registro_con.descri).upper()
            monto_con = float(registro_con.MontoD or registro_con.MontoH)

            if (total_neto_adm != monto_con):
                print(f"❌ Monto NO coincide (ADM.total_neto={total_neto_adm} vs CON.monto={monto_con})")
                total_no_matches += 1
                continue

            # 🎯 VERIFICAR co_cli DENTRO de descrip
            if (co_cli_adm in descrip_con):
                print("✅✅ COINCIDENCIA COMPLETA!")
                total_matches += 1
                total_acc_saldo_new += saldo_new_adm
                adm.coincidence = fila_con
            else:
                print(f"❌ co_cli '{co_cli_adm}' NO en descrip")
                total_no_matches += 1
        else:
            print("❌ SIN coincidencia nro_doc")
            total_no_matches += 1

    # 📊 RESUMEN DETALLADO
    print("\n" + "-" * 90)
    print(f"📊 RESUMEN VALIDACIÓN AVANZADA:")
    print(f"✅ Coincidencias COMPLETAS (nro_doc + co_cli⊆descri): {total_matches:,}")
    print(f"❌ Sin coincidencia nro_doc: {total_no_matches:,}")
    print(f"💰 Total saldo_new de coincidencias: {total_acc_saldo_new:,.2f}")

    # Verificar si 2 objetos AdmDTO tienen el mismo numero de fila coincidencia
    coincidencias_por_fila = {}
    for adm in lista_adm:
        if adm.coincidence > 0:
            coincidencias_por_fila.setdefault(adm.coincidence, []).append(adm)

    print("\n🔍 ANALIZANDO COINCIDENCIAS POR FILA CON:")
    for fila_con, adm_list in coincidencias_por_fila.items():
        if len(adm_list) > 1:
            print(f"⚠️  CON fila {fila_con} tiene {len(adm_list)} coincidencias:")
            for adm in adm_list:
                print(f"   - ADM.co_tipo_doc='{adm.co_tipo_doc}' | ADM.nro_doc='{adm.nro_doc}' | ADM.co_cli='{adm.co_cli}' | ADM.saldo_new={adm.saldo_new}")

def validate_match_inverse(lista_con: List[ConDto], lista_adm: List[AdmDto]):
    """INVERSO: 1) docref (CON) == nro_doc (ADM) Y 2) co_cli (ADM) ⊆ descri (CON)"""
    print("\n" + "=" * 90)
    print("🔄 VALIDACIÓN INVERSA: docref (CON) → nro_doc (ADM) + co_cli ⊆ descri")
    print("=" * 90)

    total_matches = 0
    total_no_matches = 0
    total_acc_saldo_new = 0.0

    # Crear diccionario INVERSO para búsqueda O(1) en ADM
    nro_doc_index = {}
    for i, dto in enumerate(lista_adm):
        index = dto.nro_doc.strip() + "/" + str(abs(dto.total_neto_new))
        if index not in nro_doc_index:
            nro_doc_index[index] = i + 2

    for idx_con, con in enumerate(lista_con, 1):  # idx_con = fila Excel CON
        docref_con = con.docref.strip()
        monto_con = float(con.MontoD or con.MontoH)
        descrip_con = str(con.descri).upper()
        index_to_search = str(int(float(docref_con or 0))) + "/" + str(monto_con)

        if index_to_search in nro_doc_index:
            fila_adm = nro_doc_index[index_to_search]
            registro_adm = lista_adm[fila_adm - 2]  # Convertir fila Excel a índice Python
            total_neto_adm = abs(registro_adm.total_neto_new)
            saldo_adm = registro_adm.saldo_new
            co_cli_adm = registro_adm.co_cli.strip().upper()
            # co_tipo_doc_adm = registro_adm.co_tipo_doc.strip()

            # 🎯 VERIFICAR MONTOS
            if total_neto_adm != monto_con:
                # print(f"❌ Monto NO coincide (ADM.total_neto={total_neto_adm} vs CON.monto={monto_con})")
                total_no_matches += 1
                continue

            # 🎯 VERIFICAR co_cli DENTRO de descrip (misma lógica)
            if co_cli_adm in descrip_con:
                # print("✅✅ COINCIDENCIA COMPLETA INVERSA!")
                total_matches += 1
                total_acc_saldo_new += saldo_adm
                con.coincidence = fila_adm  # Marcar coincidencia inversa
            else:
                # print(f"❌ co_cli '{co_cli_adm}' NO en descrip CON")
                total_no_matches += 1
        else:
            # print("❌ SIN coincidencia docref → nro_doc")
            total_no_matches += 1

    # 📊 RESUMEN DETALLADO INVERSO
    print("\n" + "-" * 90)
    print(f"📊 RESUMEN VALIDACIÓN INVERSA:")
    print(f"✅ Coincidencias COMPLETAS INVERSAS: {total_matches:,}")
    print(f"❌ Sin coincidencia docref: {total_no_matches:,}")
    print(f"💰 Total saldo_new de coincidencias: {total_acc_saldo_new:,.2f}")

    # Verificar duplicados INVERSOS
    coincidencias_por_fila_adm = {}
    for con in lista_con:
        if con.coincidence > 0:
            fila_adm = con.coincidence
            coincidencias_por_fila_adm.setdefault(fila_adm, []).append(con)

    print("\n🔍 ANALIZANDO COINCIDENCIAS INVERSAS POR FILA ADM:")
    for fila_adm, con_list in coincidencias_por_fila_adm.items():
        if len(con_list) > 1:
            print(f"⚠️  ADM fila {fila_adm} tiene {len(con_list)} coincidencias INVERSAS:")
            for con in con_list:
                print(f"   - CON.co_cue='{con.co_cue}' | CON.docref='{con.docref}' | CON.MontoD/H={float(con.MontoD or con.MontoH)}")