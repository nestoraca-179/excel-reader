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
    # docref_index = {dto.docref: i+2 for i, dto in enumerate(lista_con)}  # fila Excel
    docref_index = {}
    for i, dto in enumerate(lista_con):
        docref = str(int(float(dto.docref or 0))) + "/" + str(abs(float(dto.MontoD or dto.MontoH)))
        if docref not in docref_index:  # Solo si NO existe aún
            docref_index[docref] = i + 2

    for idx_adm, adm in enumerate(lista_adm, 1):  # idx_adm = fila Excel ADM
        co_tipo_doc = adm.co_tipo_doc.strip()
        nro_doc = adm.nro_doc.strip()
        co_cli = adm.co_cli.strip().upper()  # Normalizar para comparación
        total_neto = abs(adm.total_neto)
        saldo_new = adm.saldo_new

        print(f"🔎 Evaluando ADM #{idx_adm:4d} | co_tipo_doc='{co_tipo_doc}' | nro_doc='{nro_doc}' | co_cli='{co_cli}'", end=" → ")

        if co_tipo_doc == "ISLR":
            # print(f"⏭️  Ignorado por tipo_doc 'ISLR' - {saldo_new}")
            total_no_matches += 1
            continue

        if (nro_doc + "/" + str(abs(total_neto))) in docref_index:
            fila_con = docref_index[nro_doc + "/" + str(abs(total_neto))]
            con_registro = lista_con[fila_con - 2]  # Convertir fila Excel a índice Python
            descri_con = str(con_registro.descri).upper()
            monto_con = float(con_registro.MontoD or con_registro.MontoH)

            # print(f"📄 CON fila {fila_con} | descri='{con_registro.descri[:50]}...' | monto={monto_con}", end=" → ")
            # print("\n total_neto ADM:", total_neto, "| monto_con CON:", monto_con, end=" → ")
            if (total_neto != monto_con):
                print(f"❌ Monto NO coincide (ADM.total_neto={total_neto} vs CON.monto={monto_con})")
                total_no_matches += 1
                continue

            # 🎯 VERIFICAR co_cli DENTRO de descri
            if (co_cli in descri_con): # and (total_neto == monto_con):
                print("✅✅ COINCIDENCIA COMPLETA!")
                total_matches += 1
                total_acc_saldo_new += saldo_new
                adm.coincidence = fila_con
            else:
                print(f"❌ co_cli '{co_cli}' NO en descri")
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
        nro_doc = dto.nro_doc.strip() + "/" + str(abs(dto.total_neto_new))
        if nro_doc not in nro_doc_index:  # Solo si NO existe aún
            nro_doc_index[nro_doc] = i + 2  # fila Excel

    for idx_con, con in enumerate(lista_con, 1):  # idx_con = fila Excel CON
        docref = con.docref.strip()
        monto_con = float(con.MontoD or con.MontoH)
        descri_con = str(con.descri).upper()
        # print(f"Fila CON: {idx_con} | Docref: {docref} | Monto CON: {monto_con} | Descri: '{con.descri[:30]}...'")
        # print(f"🔎 INVERSO CON #{idx_con:4d} | docref='{docref}' | monto={monto_con}", end=" → ")
        # time.sleep(3)

        if (docref + "/" + str(monto_con)) in nro_doc_index:
            fila_adm = nro_doc_index[docref + "/" + str(monto_con)]
            adm_registro = lista_adm[fila_adm - 2]  # Convertir fila Excel a índice Python
            total_neto_adm = abs(adm_registro.total_neto_new)
            saldo_adm = adm_registro.saldo_new
            co_cli_adm = adm_registro.co_cli.strip().upper()
            # co_tipo_doc_adm = adm_registro.co_tipo_doc.strip()

            # print(f"Fila ADM: {fila_adm} | co_tipo_doc='{co_tipo_doc_adm}' | Nro. Doc {adm_registro.nro_doc} | Total_neto_new ADM: {total_neto_adm}", end=" → ")
            # print(f"📄 ADM fila {fila_adm} | co_tipo_doc='{co_tipo_doc_adm}' | co_cli='{co_cli_adm}'", end=" → ")
            # time.sleep(3)
            # print(f"\n total_neto ADM: {total_neto_adm} | monto_con CON: {monto_con}", end=" → ")

            # 🎯 VERIFICAR MONTOS
            if total_neto_adm != monto_con:
                # print(f"❌ Monto NO coincide (ADM.total_neto={total_neto_adm} vs CON.monto={monto_con})")
                total_no_matches += 1
                continue

            # 🎯 VERIFICAR co_cli DENTRO de descri (misma lógica)
            # print(f"🔍 Verificando si co_cli '{co_cli_adm}' está en '{descri_con}'", end=" → ")
            if co_cli_adm in descri_con:
                # print("✅✅ COINCIDENCIA COMPLETA INVERSA!")
                total_matches += 1
                total_acc_saldo_new += saldo_adm
                con.coincidence = fila_adm  # Marcar coincidencia inversa
            else:
                # print(f"❌ co_cli '{co_cli_adm}' NO en descri CON")
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