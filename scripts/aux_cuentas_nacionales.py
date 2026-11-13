#!/usr/bin/env python
"""Insumos para ajustar los ingresos de la EPH a Cuentas Nacionales.

Salida: data/processed/cn_ingresos.csv, una fila por año:
  rta_mill   Remuneración al trabajo asalariado (sueldos + contribuciones patronales),
             millones de pesos corrientes. INDEC, Cuenta de generación del ingreso.
  imb_mill   Ingreso mixto bruto (empresas no constituidas en sociedad: cuentapropistas y
             patrones de unidades no societarias). Ídem.
  eeb_mill   Excedente de explotación bruto (sociedades). Ídem; sólo informativo.
  pii_cartera_musd, pii_mondep_musd, pii_ied_musd
             Activos externos de "otros sectores" (sector privado no financiero, que
             incluye hogares y empresas) a fin de año, millones de dólares. INDEC,
             Posición de inversión internacional (cuadro 18).
  tc         Tipo de cambio de referencia BCRA (Com. A 3500), promedio anual.

Además calcula la cobertura de la EPH respecto de Cuentas Nacionales (requiere
data/processed/eph_trimestral_decil.csv, salida de 04_microsimulacion_eph.py):
  cob_asal   ingreso salarial de la EPH expandido / RTA. Ingreso salarial EPH = salario bruto
             de registrados + contribuciones patronales simuladas (privados) + 18% del
             bruto de registrados públicos (contribución patronal, no simulada) + 6% del
             bruto de registrados (obra social patronal, que RTA incluye) + salario de no
             registrados.
  cob_imb    ingreso de independientes de la EPH (ocupación principal de cuentapropistas y
             patrones + otras ocupaciones) / ingreso mixto bruto.
La Cuenta de generación del ingreso en base 2004 se publica desde 2016. Para 2004-2015 no
hay serie oficial comparable: se usa la cobertura promedio 2016-2018 (supuesto). Los
activos externos de 2004-2005 repiten los de 2006.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, RAW  # noqa: E402

CGI = RAW / "macro" / "serie_cgi_10_26.xls"
CIN = RAW / "macro" / "cin_II_2026.xls"
TC = RAW / "macro" / "tipo_cambio_a3500_anual.csv"


def cgi_anual(hoja: str) -> pd.Series:
    """Total general anual (columnas 'Total' de cada año; valores anualizados)."""
    x = pd.read_excel(CGI, sheet_name=hoja, header=None)
    anios, cols = x.iloc[2], x.iloc[3]
    fila = x[x.iloc[:, 1].astype(str).str.strip() == "Total general"].iloc[0]
    out, a = {}, None
    for j in range(2, x.shape[1]):
        if pd.notna(anios[j]):
            a = int(str(anios[j])[:4])
        if str(cols[j]).strip().startswith("Total") and pd.notna(fila[j]):
            out[a] = float(fila[j])
    return pd.Series(out)


def pii_fin_de_anio() -> pd.DataFrame:
    """Activos externos de otros sectores al cierre de cada año (anual o 4º trimestre)."""
    x = pd.read_excel(CIN, sheet_name="Cuadro 18", header=None)
    enc = x.iloc[4]
    etiqueta = x.iloc[:, 0].astype(str).str.strip()

    def fila(prefijo):
        return x[etiqueta.str.startswith(prefijo)].iloc[0]

    filas = {"pii_cartera_musd": fila("2. Inversión de cartera"),
             "pii_mondep_musd": fila("4.2 Moneda y depósitos"),
             "pii_ied_musd": fila("1. Inversión directa")}
    out = {}
    for j in range(1, x.shape[1]):
        h = str(enc[j]).strip().rstrip("*")
        if h.endswith(".0"):
            h = h[:-2]
        if h.isdigit():
            a = int(h)
        elif h.endswith("T4") and h[:4].isdigit():
            a = int(h[:4])
        else:
            continue
        out[a] = {k: float(f[j]) for k, f in filas.items() if pd.notna(f[j])}
    return pd.DataFrame(out).T.sort_index()


def cobertura(cn: pd.DataFrame) -> pd.DataFrame:
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0)
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    a = q.groupby(["anio", "trim"]).sum(numeric_only=True).groupby("anio").mean()
    f = rec.poblacion.reindex(a.index) / a.personas * 12 / 1e6      # mensual EPH -> millones anuales país
    asal = (a.masa_bruta_reg * 1.06 + a.contrib + 0.18 * a.masa_bruta_reg_pub + a.ing_lab_asal_no_reg) * f
    ind = (a.ing_lab_independiente + a.ing_otras_ocup) * f
    c = pd.DataFrame({"cob_asal": asal / cn.rta_mill, "cob_imb": ind / cn.imb_mill})
    base = c.loc[2016:2018].mean()
    c["cobertura_estimada"] = c.cob_asal.isna()
    return c.fillna(base)


def main() -> None:
    cn = pd.DataFrame({"rta_mill": cgi_anual("RTA"), "imb_mill": cgi_anual("IBM"), "eeb_mill": cgi_anual("EEB")})
    pii = pii_fin_de_anio()
    tc = pd.read_csv(TC)
    tc = pd.Series(tc.iloc[:, 1].values, index=tc.iloc[:, 0].str[:4].astype(int), name="tc")
    out = pd.concat([cn, pii, tc], axis=1).sort_index().loc[2004:2024]
    out.index.name = "anio"
    out[["pii_cartera_musd", "pii_mondep_musd", "pii_ied_musd"]] = out[
        ["pii_cartera_musd", "pii_mondep_musd", "pii_ied_musd"]].bfill()
    out = out.join(cobertura(out))
    out.round(4).to_csv(PROCESSED / "cn_ingresos.csv")
    print(out.round(1).to_string())
    print("OK ->", PROCESSED / "cn_ingresos.csv")


if __name__ == "__main__":
    main()
