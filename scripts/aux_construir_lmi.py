#!/usr/bin/env python
"""Construye params/lmi.csv: base imponible máxima (tope) de aportes personales, mensual.

Método (reemplaza la serie hardcodeada de la notebook original, que era incorrecta):

1. Hasta 02/2009 el tope se fija en MOPRE (módulo previsional = $80):
   - 60 MOPRE = $4.800 (Dto. 290/2000; citado en considerandos del Dto. 1448/2008).
   - Ley 26.222 art. 1 (B.O. 08/03/2007): 75 MOPRE = $6.000, sólo aportes jubilatorios.
   - Dto. 1346/2007 art. 5 (RG AFIP 2340/2007): 84,375 MOPRE = $6.750 desde 09/2007.
   - Dto. 279/2008: 90,70 MOPRE = $7.256 desde 03/2008 y 97,50 MOPRE = $7.800 desde 07/2008.
   - Dto. 1448/2008: extiende el tope jubilatorio a los demás subsistemas desde 11/2008.
2. Desde 03/2009 (Ley 26.417) el tope se actualiza con la movilidad previsional. Se
   encadena con la variación del haber mínimo oficial (serie 58.1_MP_0_M_13, datos.gob.ar),
   salvo donde el haber mínimo tuvo un tratamiento distinto de la movilidad general
   (03/2009: 11,69%; 03/2020: Dto. 163/2020), casos en los que se usa un ancla.
3. La cadena se CONTROLA contra valores publicados en resoluciones (anclas). Si la
   cadena difiere de un ancla más de 0,05% el script falla.

Criterio anual: no hay "valor anual". El modelo usa el promedio de los meses de cada
trimestre EPH. Este archivo guarda la serie mensual completa.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PARAMS, RAW  # noqa: E402

# (mes, valor, fuente). Valores que figuran en la norma o en una fuente que la transcribe.
ANCLAS = {
    "2010-03": (10119.08, "Res. ANSES 130/2010 (B.O. 01/03/2010); RG AFIP 2800"),
    "2012-09": (21248.45, "citado como valor anterior en Res. ANSES 30/2013"),
    "2013-03": (24473.92, "Res. ANSES 30/2013 (B.O. 11/03/2013)"),
    "2015-09": (48598.08, "SICOSS v39 r2 (Consejo Profesional CABA, 01/12/2015)"),
    "2020-03": (173945.70, "valor vigente marzo 2020 (consistente con Res. ANSES 325/2020 / 1,075 / 1,0612)"),
    "2020-09": (198435.52, "Res. ANSES 325/2020"),
    "2023-03": (642142.18, "Res. ANSES 36/2023"),
    "2024-11": (2767090.68, "Res. ANSES 979/2024"),
    "2024-12": (2841525.42, "Res. ANSES 1122/2024"),
}
# Meses en los que NO se encadena con el haber mínimo sino que se fija el valor.
REANCLAR = {"2020-03"}
# Movilidad general cuando difiere de la variación del haber mínimo.
MOVILIDAD_OVERRIDE = {"2009-03": 0.1169, "2009-09": 0.0734}


def main() -> None:
    hm = pd.read_csv(RAW / "macro" / "haber_minimo_mensual.csv")
    hm.columns = ["mes", "haber_minimo"]
    hm["mes"] = hm["mes"].str[:7]
    hm = hm[(hm.mes >= "2003-01") & (hm.mes <= "2024-12")].reset_index(drop=True)

    filas = []
    jub = otros = 4800.0
    prev_hm = None
    for mes, h in zip(hm.mes, hm.haber_minimo):
        fuente, estado = "", "arrastre"
        if mes < "2009-03":
            if mes == "2003-01":
                fuente, estado = "60 MOPRE (Dto. 290/2000)", "verificado_indirecto"
            if mes == "2007-04":
                jub = 6000.0
                fuente, estado = "75 MOPRE, Ley 26.222 art. 1 (inicio 03 o 04/2007: no verificado)", "verificado"
            if mes == "2007-09":
                jub = 6750.0
                fuente, estado = "84,375 MOPRE, Dto. 1346/2007 art. 5; RG AFIP 2340/2007", "verificado"
            if mes == "2008-03":
                jub = 7256.0
                fuente, estado = "90,70 MOPRE, Dto. 279/2008", "verificado"
            if mes == "2008-07":
                jub = 7800.0
                fuente, estado = "97,50 MOPRE, Dto. 279/2008 art. 5 (según RG AFIP 2508)", "verificado"
            if mes == "2008-11":
                otros = jub
                fuente, estado = "Dto. 1448/2008: tope único para todos los subsistemas", "verificado"
        else:
            if mes in REANCLAR:
                jub = ANCLAS[mes][0]
                fuente, estado = ANCLAS[mes][1], "ancla"
            else:
                var = MOVILIDAD_OVERRIDE.get(mes, h / prev_hm - 1)
                if abs(var) > 1e-9:
                    jub = round(jub * (1 + var), 2)
                    fuente = f"movilidad {var:.4%} sobre valor anterior (Ley 26.417 / 27.426 / 27.609)"
                    estado = "derivado_movilidad"
            otros = jub
            if mes in ANCLAS and mes not in REANCLAR:
                ancla = ANCLAS[mes][0]
                dif = jub / ancla - 1
                if abs(dif) > 5e-4:
                    raise SystemExit(f"Cadena LMI no reproduce ancla {mes}: {jub} vs {ancla}")
                jub = otros = ancla  # se adopta el valor de la norma
                fuente, estado = ANCLAS[mes][1] + f" (cadena difería {dif:+.4%})", "ancla"
        filas.append((mes, jub, otros, estado, fuente))
        prev_hm = h

    out = pd.DataFrame(filas, columns=["mes", "tope_jubilacion", "tope_otros_subsistemas", "estado", "fuente"])
    out.to_csv(PARAMS / "lmi.csv", index=False)
    cambios = out[out.estado != "arrastre"]
    print(cambios.to_string(index=False))
    print(f"\n{len(out)} meses; {len(cambios)} cambios; "
          f"{(cambios.estado == 'ancla').sum()} anclas verificadas.")


if __name__ == "__main__":
    main()
