import time
import re
from typing import List

from models.AdmDTO import AdmDto
from models.ConDTO import ConDto
from utils.StringUtils import str_to_float_safe

def validate_match_advanced(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Valida: 1) nro_doc (ADM) == docref (CON) Y 2) co_cli (ADM) ⊆ descri (CON)"""
    print("\n" + "=" * 90)
    print("🔍 VALIDACIÓN AVANZADA: nro_doc (ADM) == docref (CON) + co_cli ⊆ descri")
    print("=" * 90)

    total_matches = 0
    total_no_matches = 0
    total_acc_saldo_new = 0.0
    total_acc_other = 0.0
    islr_already_selected = []  # Para evitar seleccionar múltiples ISLR con mismo nro_doc

    # Crear diccionario para búsqueda O(1) en CON
    docref_index = {}
    for i, dto in enumerate(con_list):
        index = str(int(str_to_float_safe(dto.docref or 0))) + "/" + str(abs(float(dto.MontoD or dto.MontoH)))
        if index not in docref_index:
            docref_index[index] = i + 2

    for idx_adm, adm in enumerate(adm_list, 1):
        co_tipo_doc_adm = adm.co_tipo_doc.strip()
        if co_tipo_doc_adm == "ISLR" or co_tipo_doc_adm == "ADEL":
            descrip = adm.observa.strip()
            nro_doc_adm = descrip.split()[-1].lstrip("0")
            nro_doc_adm = str(int(nro_doc_adm) + (1 if co_tipo_doc_adm == "ADEL" else 0))
        else:
            nro_doc_adm = adm.nro_doc.strip()

        co_cli_adm = adm.co_cli.strip().upper()
        total_neto_adm = abs(adm.total_neto)
        saldo_new_adm = adm.saldo_new
        index_to_search = nro_doc_adm + "/" + str(total_neto_adm)

        if index_to_search in docref_index:
            fila_con = docref_index[index_to_search]
            while co_tipo_doc_adm == "ISLR" and fila_con in islr_already_selected:
                fila_con += 1

            islr_already_selected.append(fila_con)

            registro_con = con_list[fila_con - 2]  # Convertir fila Excel a índice Python
            descrip_con = str(registro_con.descri).upper()
            monto_con = float(registro_con.MontoD or registro_con.MontoH)

            if (total_neto_adm != monto_con):
                # print(f"❌ Monto NO coincide (ADM.total_neto={total_neto_adm} vs CON.monto={monto_con})")
                total_no_matches += 1
                total_acc_other += saldo_new_adm
                continue

            # 🎯 VERIFICAR co_cli DENTRO de descrip
            if (co_cli_adm in descrip_con):
                # print("✅✅ COINCIDENCIA COMPLETA!")
                total_matches += 1
                total_acc_saldo_new += saldo_new_adm
                adm.coincidence = fila_con
            else:
                # print(f"❌ co_cli '{co_cli_adm}' NO en descrip")
                total_no_matches += 1
                total_acc_other += saldo_new_adm
        else:
            # print("❌ SIN coincidencia nro_doc")
            total_no_matches += 1
            total_acc_other += saldo_new_adm

    # 📊 RESUMEN DETALLADO
    print("\n" + "-" * 90)
    print(f"📊 RESUMEN VALIDACIÓN AVANZADA:")
    print(f"✅ Coincidencias COMPLETAS (nro_doc + co_cli⊆descri): {total_matches:,}")
    print(f"❌ Sin coincidencia nro_doc: {total_no_matches:,}")
    print(f"💰 Total saldo_new de coincidencias: {total_acc_saldo_new:,.2f}")
    print(f"💰 Total saldo_new de NO coincidencias: {total_acc_other:,.2f}")

    # Verificar si 2 objetos AdmDTO tienen el mismo numero de fila coincidencia
    coincidencias_por_fila = {}
    for adm in adm_list:
        if adm.coincidence > 0:
            coincidencias_por_fila.setdefault(adm.coincidence, []).append(adm)

    print("\n🔍 ANALIZANDO COINCIDENCIAS POR FILA CON:")
    for fila_con, adm_list in coincidencias_por_fila.items():
        if len(adm_list) > 1:
            print(f"⚠️  CON fila {fila_con} tiene {len(adm_list)} coincidencias:")
            for adm in adm_list:
                print(f"   - ADM.co_tipo_doc='{adm.co_tipo_doc}' | ADM.nro_doc='{adm.nro_doc}' | ADM.co_cli='{adm.co_cli}' | ADM.saldo_new={adm.saldo_new}")

def validate_match_inverse(con_list: List[ConDto], adm_list: List[AdmDto]):
    """INVERSO: 1) docref (CON) == nro_doc (ADM) Y 2) co_cli (ADM) ⊆ descri (CON)"""
    print("\n" + "=" * 90)
    print("🔄 VALIDACIÓN INVERSA: docref (CON) → nro_doc (ADM) + co_cli ⊆ descri")
    print("=" * 90)

    total_matches = 0
    total_no_matches = 0
    total_acc_saldo_new = 0.0
    total_acc_other = 0.0
    islr_already_selected = []  # Para evitar seleccionar múltiples ISLR con mismo nro_doc en inverso

    # Crear diccionario INVERSO para búsqueda O(1) en ADM
    nro_doc_index = {}
    for i, dto in enumerate(adm_list):
        if dto.co_tipo_doc.strip() == "ISLR" or dto.co_tipo_doc.strip() == "ADEL":
            descrip = dto.observa.strip()
            nro_doc_adm = descrip.split()[-1].lstrip("0")
            nro_doc_adm = str(int(nro_doc_adm) + (1 if dto.co_tipo_doc.strip() == "ADEL" else 0))
        else:
            nro_doc_adm = dto.nro_doc.strip()

        index = nro_doc_adm + "/" + str(abs(dto.total_neto_new))
        if index not in nro_doc_index:
            nro_doc_index[index] = i + 2

    for idx_con, con in enumerate(con_list, 1):  # idx_con = fila Excel CON
        docref_con = con.docref.strip()
        monto_con = float(con.MontoD or con.MontoH)
        descrip_con = str(con.descri).upper()
        index_to_search = str(int(str_to_float_safe(docref_con or 0))) + "/" + str(monto_con)

        if index_to_search in nro_doc_index:
            fila_adm = nro_doc_index[index_to_search]
            registro_adm = adm_list[fila_adm - 2]  # Convertir fila Excel a índice Python
            while registro_adm.co_tipo_doc.strip() == "ISLR" and fila_adm in islr_already_selected:
                fila_adm += 1
                registro_adm = adm_list[fila_adm - 2]

            islr_already_selected.append(fila_adm)

            total_neto_adm = abs(registro_adm.total_neto_new)
            saldo_adm = registro_adm.saldo_new
            co_cli_adm = registro_adm.co_cli.strip().upper()
            # co_tipo_doc_adm = registro_adm.co_tipo_doc.strip()

            if total_neto_adm != monto_con:
                # print(f"❌ Monto NO coincide (ADM.total_neto={total_neto_adm} vs CON.monto={monto_con})")
                total_no_matches += 1
                total_acc_other += saldo_adm
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
                total_acc_other += saldo_adm
        else:
            # print("❌ SIN coincidencia docref → nro_doc")
            total_no_matches += 1

    # 📊 RESUMEN DETALLADO INVERSO
    print("\n" + "-" * 90)
    print(f"📊 RESUMEN VALIDACIÓN INVERSA:")
    print(f"✅ Coincidencias COMPLETAS INVERSAS: {total_matches:,}")
    print(f"❌ Sin coincidencia docref: {total_no_matches:,}")
    print(f"💰 Total saldo_new de coincidencias: {total_acc_saldo_new:,.2f}")
    print(f"💰 Total saldo_new de NO coincidencias: {total_acc_other:,.2f}")

    # Verificar duplicados INVERSOS
    coincidencias_por_fila_adm = {}
    for con in con_list:
        if con.coincidence > 0:
            fila_adm = con.coincidence
            coincidencias_por_fila_adm.setdefault(fila_adm, []).append(con)

    print("\n🔍 ANALIZANDO COINCIDENCIAS INVERSAS POR FILA ADM:")
    for fila_adm, con_list in coincidencias_por_fila_adm.items():
        if len(con_list) > 1:
            print(f"⚠️  ADM fila {fila_adm} tiene {len(con_list)} coincidencias INVERSAS:")
            for con in con_list:
                print(f"   - CON.co_cue='{con.co_cue}' | CON.docref='{con.docref}' | CON.MontoD/H={float(con.MontoD or con.MontoH)}")

def validate_fact_descriptions(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Para cada AdmDto con `co_tipo_doc == 'FACT'`, forma 'VENT.<nro_doc>' y busca
    si aparece dentro del campo `descri` de algún objeto en `con_list`.
    Imprime un mensaje por cada `FACT` indicando si hubo coincidencia o no.
    """
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN FACT → DESCRI: buscar 'VENT.<nro_doc>' en CON.descri")
    print("=" * 90)

    for adm_idx, adm in enumerate(adm_list, 1):
        co_tipo = (adm.co_tipo_doc or "").strip()
        if co_tipo == "FACT":
            nro_doc = (adm.nro_doc or "").strip()
            vent_tag = f"VENT.{nro_doc}"
            vent_tag_upper = vent_tag.upper()

            found = False
            for con_idx, con in enumerate(con_list, 1):
                descri_con = str(con.descri or "").upper()
                if vent_tag_upper in descri_con:
                    # Mostrar la fila de Excel equivalente (primer registro corresponde a fila 2)
                    fila_con = con_idx + 1
                    # print(f"✅ Coincidencia: '{vent_tag}' encontrada en CON fila {fila_con}: {con.descri}")
                    adm.has_coincidence = True
                    adm.row_coincidence = fila_con
                    adm.text_coincidence = con.descri
                    found = True
                    break

            # if not found:
                # print(f"❌ No hay coincidencias en CON para {vent_tag}")

def validate_fact_descriptions_v2(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Versión con índice invertido — ideal cuando con_list es muy grande
    y los nro_doc son tokens discretos dentro de descri.
    """
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN FACT → DESCRI: buscar 'VENT.<nro_doc>' en CON.descri")
    print("=" * 90)

    # ✅ Índice invertido: mapea cada token "VENT.XXX" → primer con que lo contiene
    # Construido en O(m) — búsqueda posterior en O(1)
    vent_index: dict[str, tuple[int, any]] = {}
    for idx, con in enumerate(con_list):
        descri_upper = str(con.descri or "").upper()
        # Extraer tokens VENT.* presentes en este descri
        tokens = {word for word in descri_upper.split() if word.startswith("VENT.")}
        for token in tokens:
            if token not in vent_index:  # Guarda solo la primera aparición
                vent_index[token] = (idx + 2, con.descri)

    # ✅ Lookup O(1) por FACT
    for adm in adm_list:
        if (adm.co_tipo_doc or "").strip() != "FACT":
            continue

        nro_doc = (adm.nro_doc or "").strip()
        vent_tag_upper = f"VENT.{nro_doc}".upper()

        if vent_tag_upper in vent_index:
            fila_con, descri_original = vent_index[vent_tag_upper]
            adm.has_coincidence = True
            adm.row_coincidence = fila_con
            adm.text_coincidence = descri_original

# IN USE
def validate_fact_descriptions_v3(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Para cada AdmDto con `co_tipo_doc == 'FACT'`, forma 'VENT.<nro_doc>' y busca
    si aparece dentro del campo `descri` de algún objeto en `con_list`.
    Imprime un mensaje por cada `FACT` indicando si hubo coincidencia o no.
    """
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN FACT → DESCRI: buscar 'VENT.<nro_doc>' en CON.descri")
    print("=" * 90)

    # ✅ Pre-procesar con_list UNA SOLA VEZ → O(m) en lugar de O(n*m)
    # Guarda (descri_upper, fila_excel, descri_original) por cada con
    con_preprocessed = [
        (str(con.descri or "").upper(), idx + 2, con.descri)
        for idx, con in enumerate(con_list)
    ]

    # ✅ Filtrar solo los FACT una vez
    fact_adms = [
        adm for adm in adm_list
        if (adm.co_tipo_doc or "").strip() == "FACT"
    ]

    for adm in fact_adms:
        nro_doc = (adm.nro_doc or "").strip()
        vent_tag_upper = f"VENT.{nro_doc}".upper()

        # ✅ next() con generador: detiene en la primera coincidencia sin crear lista
        match = next(
            (
                (fila_con, descri_original)
                for descri_upper, fila_con, descri_original in con_preprocessed
                if vent_tag_upper in descri_upper
            ),
            None,
        )

        if match:
            fila_con, descri_original = match
            adm.has_coincidence = True
            adm.row_coincidence = fila_con
            adm.text_coincidence = descri_original

def validate_adel_descriptions(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Valida objetos ADEL: extrae número de cobro desde `adm.observa` y busca
    la cadena 'APLIC. ADEL. CLIE. CxC,<numero>' dentro de `con.descri`.

    Si se encuentra, asigna en el objeto `adm`:
      adm.has_coincidence = True
      adm.row_coincidence = <fila donde se halló>
      adm.text_coincidence = <texto de la coincidencia>
    """
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN ADEL → DESCRI: buscar 'APLIC. ADEL. CLIE. CxC,<nro_cobro>' en CON.descri")
    print("=" * 90)

    for adm_idx, adm in enumerate(adm_list, 1):
        if (adm.co_tipo_doc or "").strip() != "ADEL":
            continue

        observa = str(adm.observa or "").strip()
        # Extraer el número de cobro (última secuencia de dígitos en la cadena)
        matches = re.findall(r"\d+", observa)
        if not matches:
            continue

        nro_cobro_original = matches[-1]
        width = len(nro_cobro_original)
        base_int = int(nro_cobro_original)

        found = False
        # Intentar el valor original y hasta +10 incrementos
        for inc in range(0, 11):
            candidate_int = base_int + inc
            candidate_str = str(candidate_int).zfill(width)
            target = f"APLIC. ADEL. CLIE. CxC,{candidate_str}"
            target_upper = target.upper()

            for con_idx, con in enumerate(con_list, 1):
                descri_con_upper = str(con.descri or "").upper()
                if target_upper in descri_con_upper:
                    fila_con = con_idx + 1
                    adm.has_coincidence = True
                    adm.row_coincidence = fila_con
                    adm.text_coincidence = con.descri
                    found = True
                    break

            if found:
                break

# IN USE
def validate_adel_descriptions_v2(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Versión con índice — O(n + m) en lugar de O(n × 11 × m)."""
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN ADEL → DESCRI: buscar 'APLIC. ADEL. CLIE. CxC,<nro_cobro>' en CON.descri")
    print("=" * 90)

    PREFIX = "APLIC. ADEL. CLIE. CXC,"
    digit_pattern = re.compile(r"\d+")

    # ✅ Índice: extrae todos los números tras el prefijo en cada descri → O(m)
    # Mapea numero_str → (fila_excel, descri_original) de la primera aparición
    cobro_index: dict[str, tuple[int, any]] = {}
    for idx, con in enumerate(con_list):
        descri_upper = str(con.descri or "").upper()
        # Buscar ocurrencias del prefijo y capturar el número que le sigue
        pos = 0
        while True:
            found_pos = descri_upper.find(PREFIX, pos)
            if found_pos == -1:
                break
            after = descri_upper[found_pos + len(PREFIX):]
            num_match = re.match(r"(\d+)", after)
            if num_match:
                token = num_match.group(1)
                if token not in cobro_index:          # Guarda solo la primera aparición
                    cobro_index[token] = (idx + 2, con.descri)
            pos = found_pos + 1

    # ✅ Lookup O(1) por cada ADEL × 11 candidatos
    for adm in adm_list:
        if (adm.co_tipo_doc or "").strip() != "ADEL":
            continue

        co_cli = adm.co_cli.strip().upper()
        observa = str(adm.observa or "").strip()
        nums = digit_pattern.findall(observa)
        if not nums:
            continue

        nro_cobro_original = nums[-1]
        width = len(nro_cobro_original)
        base_int = int(nro_cobro_original)

        # Buscar entre los 10001 candidatos en el índice → O(10001) = O(1)
        for inc in range(10001):
            candidate = str(base_int + inc).zfill(width)
            if candidate in cobro_index:
                fila_con, descri_original = cobro_index[candidate]
                if descri_original.upper().find(co_cli) == -1:
                    continue

                adm.has_coincidence = True
                adm.row_coincidence = fila_con
                adm.text_coincidence = descri_original
                break

def validate_ivan_descriptions(adm_list: List[AdmDto], con_list: List[ConDto]):
    """Para cada AdmDto con `co_tipo_doc == 'IVAN'`, forma 'VENT.<nro_doc>' y busca
    si aparece dentro del campo `descri` de algún objeto en `con_list`.
    Imprime un mensaje por cada `IVAN` indicando si hubo coincidencia o no.
    """
    print("\n" + "=" * 90)
    print("🔎 VALIDACIÓN IVAN → DESCRI: buscar 'Retención de IVA N°:<nro_doc>' en CON.descri")
    print("=" * 90)

    # ✅ Pre-procesar con_list UNA SOLA VEZ → O(m) en lugar de O(n*m)
    # Guarda (descri_upper, fila_excel, descri_original) por cada con
    con_preprocessed = [
        (str(con.descri or "").upper(), idx + 2, con.descri)
        for idx, con in enumerate(con_list)
    ]

    # ✅ Filtrar solo los IVAN una vez
    ivan_adms = [
        adm for adm in adm_list
        if (adm.co_tipo_doc or "").strip() == "IVAN"
    ]

    for adm in ivan_adms:
        nro_doc = (adm.nro_doc or "").strip()
        ret_tag_upper = f"Retención de IVA N°:{nro_doc}"

        # ✅ next() con generador: detiene en la primera coincidencia sin crear lista
        match = next(
            (
                (fila_con, descri_original)
                for descri_upper, fila_con, descri_original in con_preprocessed
                if ret_tag_upper in descri_upper
            ),
            None,
        )

        if match:
            fila_con, descri_original = match
            adm.has_coincidence = True
            adm.row_coincidence = fila_con
            adm.text_coincidence = descri_original