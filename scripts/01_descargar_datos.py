#!/usr/bin/env python
"""Descarga todos los insumos públicos crudos a data/raw/.

Fuentes (todas de acceso público, sin login):
  - EPH continua, microdatos trimestrales 2003T3-2025T4 (INDEC).
  - ENGHo 2004/05, 2012/13 y 2017/18, microdatos (INDEC).
  - Documentos normativos y series de recaudación (ver FUENTES_VARIAS).

Los archivos .rar/.zip se extraen con `bsdtar` (libarchive), que lee ambos
formatos (si un .rar falla, se usa `unar`). Uso:  python scripts/01_descargar_datos.py [--solo eph|engho|otros|anuarios]
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import RAW, trimestres_disponibles  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) incidencia-fiscal-ar"}
INDEC = "https://www.indec.gob.ar/ftp/cuadros/menusuperior"


def nombre_eph(anio: int, trim: int) -> str:
    """Nombre del archivo de microdatos EPH en el FTP de INDEC.

    INDEC no usa una convención estable; los casos irregulares se listan
    explícitamente (verificados el 2026-11-10 contra la página de bases de
    datos de INDEC).
    """
    yy = f"{anio % 100:02d}"
    if anio <= 2015:
        ext = "rar" if (anio, trim) in {(2014, 1), (2014, 3), (2014, 4), (2015, 1), (2015, 2)} else "zip"
        return f"t{trim}{yy}_dta.{ext}"
    if anio == 2016:
        return f"EPH_usu_{ {2: '2do', 3: '3er', 4: '4to'}[trim] }Trim_2016_txt.zip"
    if (anio, trim) == (2017, 1):
        return "EPH_usu_1er_Trim_2017_txt.zip"
    return f"EPH_usu_{trim}_Trim_{anio}_txt.zip"


ENGHO = {
    "2004": [
        "ENGH0405_gastos.rar", "ENGH0405_hogar.rar", "ENGH0405_ingresos.rar",
        "ENGH0405_personas.rar", "ENGH0405_codigos_bienes_servicios.rar",
        "ENGHo200405_archivosdedatos.pdf",
    ],
    "2012": [
        "bases_datos_engho2012.rar", "codigos_engho2012.zip",
        "utilizacion_base_engho2012.pdf",
    ],
    "2017": [
        "engho2018_gastos.zip", "engho2018_hogares.zip", "engho2018_personas.zip",
        "engho2018_articulos.zip", "engho2017_18_manual_uso_bases.pdf",
        "ENGHo_2017_2018_diccionario_registros.xlsx",
        "ENGHo_2017_2018_codigos_2018_2012_2004.xlsx",
        "ENGHo_2017_2018_codigos_12_9_divisiones.xlsx",
    ],
}

def _serie(ids: str) -> str:
    return ("https://apis.datos.gob.ar/series/api/series/"
            f"?ids={ids}&start_date=1994-01-01&limit=1000&format=csv")


# (subcarpeta, nombre_local, url)
FUENTES_VARIAS = [
    ("normativa", "ganancias_2000_2025_dniaf.pdf",
     "https://www.argentina.gob.ar/sites/default/files/impuesto_a_las_ganancias_desde_el_ano_2000_al_2025_0.pdf"),
    # DNIAF (Min. Economía): recaudación nacional + provincial y presión tributaria
    ("recaudacion", "dniaf_recaudacion_nominal_desde_1991.xlsx",
     "https://www.argentina.gob.ar/sites/default/files/recaudacion_nominal_desde_1991_ppales_6.xlsx"),
    ("recaudacion", "dniaf_recaudacion_nominal_clasif_internacional.xlsx",
     "https://www.argentina.gob.ar/sites/default/files/recaudacion_nominal_clasificacion_internacional_desde_1991211.xlsx"),
    ("recaudacion", "dniaf_presion_tributaria_pbi_2004_2025.xlsx",
     "https://www.argentina.gob.ar/sites/default/files/presion_tributaria_pbi_2004-2025211.xlsx"),
    ("recaudacion", "dniaf_presion_tributaria_clasif_internacional.xlsx",
     "https://www.argentina.gob.ar/sites/default/files/presion_tributaria_clasificacion_internacional_pbi_2004-2025211.xlsx"),
    # Series oficiales (API Series de Tiempo, datos.gob.ar)
    ("macro", "ripte_mensual.csv",
     "https://infra.datos.gob.ar/catalog/sspm/dataset/158/distribution/158.1/download/"
     "remuneracion-imponible-promedio-trabajadores-estables-ripte-total-pais-pesos-serie-mensual.csv"),
    ("macro", "haber_minimo_mensual.csv", _serie("58.1_MP_0_M_13")),
    ("macro", "smvm_mensual.csv", _serie("57.1_SMVMM_0_M_34")),
    ("macro", "consumo_privado_corriente_anual.csv", _serie("4.3_DGCP_2004_A_27")),
    ("macro", "pib_corriente_anual.csv", _serie("4.3_OGP_2004_A_17")),
    # Cuentas Nacionales para el ajuste de ingresos (scripts/aux_cuentas_nacionales.py)
    ("macro", "serie_cgi_10_26.xls",
     "https://www.indec.gob.ar/ftp/cuadros/economia/serie_cgi_10_26.xls"),
    ("macro", "cin_II_2026.xls",
     "https://www.indec.gob.ar/ftp/cuadros/economia/cin_II_2026.xls"),
    ("macro", "tipo_cambio_a3500_anual.csv",
     "https://apis.datos.gob.ar/series/api/series/?ids=168.1_T_CAMBI500_D_0_0_17&collapse=year"
     "&collapse_aggregation=avg&start_date=2003-01-01&limit=1000&format=csv"),
    # Precios al consumidor para el deflactor (scripts/aux_deflactor.py)
    ("macro", "ipc_97.2_ING_2008_M_17.csv", _serie("97.2_ING_2008_M_17")),          # IPC-GBA, INDEC
    ("macro", "ipc_197.1_NIVEL_GENERAL_2014_0_13.csv", _serie("197.1_NIVEL_GENERAL_2014_0_13")),  # San Luis
    ("macro", "ipc_148.3_INIVELNAL_DICI_M_26.csv", _serie("148.3_INIVELNAL_DICI_M_26")),  # IPC Nacional
    # Canasta básica total, Gran Buenos Aires, por adulto equivalente (INDEC; figura 6)
    ("macro", "cbt_gba_mensual.csv", _serie("444.1_CANASTA_batotGBA_0_0_26_47")),
    # Población total país (Banco Mundial, SP.POP.TOTL; uso auxiliar en validación)
    ("macro", "poblacion_total_wb.json",
     "https://api.worldbank.org/v2/country/ARG/indicator/SP.POP.TOTL?format=json&date=2003:2025&per_page=100"),
] + [
    # ARCA (ex AFIP): recaudación anual por impuesto, un archivo por año
    ("recaudacion", f"arca_serie{a}.xls",
     f"https://contenidos.afip.gob.ar/institucional/estudios/archivos/serie{a}.xls")
    for a in range(2003, 2026)
]


def descargar(url: str, destino: Path, reintentos: int = 4) -> bool:
    if destino.exists() and destino.stat().st_size > 0:
        return True
    destino.parent.mkdir(parents=True, exist_ok=True)
    for i in range(reintentos):
        try:
            r = requests.get(url, headers=UA, timeout=180)
            if r.status_code == 200 and len(r.content) > 500:
                destino.write_bytes(r.content)
                return True
            print(f"   HTTP {r.status_code} en {url}")
        except requests.RequestException as e:
            print(f"   error {e!r}; reintento {i + 1}")
        time.sleep(3 * (i + 1))
    return False


def extraer(archivo: Path, carpeta: Path) -> None:
    """Extrae zip/rar con bsdtar. Idempotente (marca .ok)."""
    marca = carpeta / ".ok"
    if marca.exists():
        return
    carpeta.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["bsdtar", "-xf", str(archivo), "-C", str(carpeta)])
    if r.returncode and archivo.suffix == ".rar":
        # libarchive 3.7.2 da error de CRC con algunos .rar de la EPH 2014 (el archivo está
        # sano: coincide en tamaño con el del servidor y unar lo extrae bien).
        subprocess.run(["unar", "-q", "-f", "-D", "-o", str(carpeta), str(archivo)], check=True)
    elif r.returncode:
        raise subprocess.CalledProcessError(r.returncode, r.args)
    marca.write_text(hashlib.sha256(archivo.read_bytes()).hexdigest())


def bajar_eph() -> list[str]:
    fallas = []
    for anio, trim in trimestres_disponibles():
        nombre = nombre_eph(anio, trim)
        z = RAW / "eph" / "zips" / nombre
        if not descargar(f"{INDEC}/eph/{nombre}", z):
            fallas.append(nombre)
            continue
        extraer(z, RAW / "eph" / f"{anio}T{trim}")
        print(f"EPH {anio}T{trim} ok")
    return fallas


def bajar_engho() -> list[str]:
    fallas = []
    for edicion, archivos in ENGHO.items():
        for nombre in archivos:
            z = RAW / "engho" / edicion / "zips" / nombre
            if not descargar(f"{INDEC}/engho/{nombre}", z):
                fallas.append(nombre)
                continue
            if z.suffix in {".zip", ".rar"}:
                extraer(z, RAW / "engho" / edicion / z.stem)
            print(f"ENGHo {edicion} {nombre} ok")
    return fallas


_ET = "https://contenidos.afip.gob.ar/institucional/estudios/archivos/estadisticasTributarias"
ANUARIOS_ARCA = {a: f"{_ET}/estadisticasTributarias{a}.zip" for a in range(2003, 2019)} | {
    2019: f"{_ET}/Public2019.zip", 2020: f"{_ET}/Publicacion-2020.zip",
    2021: f"{_ET}/Estadisticas-Tributarias-2021.zip", 2022: f"{_ET}/estadisticas-Tributarias-2022.zip",
    2023: f"{_ET}/Estadisticas-Tributarias-2023.zip", 2024: f"{_ET}/Estadisticas-Tributarias-2024.zip",
    2025: f"{_ET}/Estadisticas-Tributarias-2025.zip",
}


def bajar_anuarios() -> list[str]:
    """Anuarios de estadísticas tributarias de ARCA (declaraciones juradas por tramo)."""
    fallas = []
    for anio, url in ANUARIOS_ARCA.items():
        z = RAW / "anuarios_arca" / "zips" / f"anuario_{anio}.zip"
        if not descargar(url, z):
            fallas.append(z.name)
            continue
        carpeta = RAW / "anuarios_arca" / str(anio)
        extraer(z, carpeta)
        # 2003-2008: el zip trae un instalador; las planillas están dentro de AFIP.CAB
        for cab in carpeta.glob("*.CAB"):
            extraer(cab, carpeta / "cab")
        print(f"Anuario ARCA {anio} ok")
    return fallas


def bajar_otros() -> list[str]:
    fallas = []
    for sub, nombre, url in FUENTES_VARIAS:
        if not descargar(url, RAW / sub / nombre):
            fallas.append(nombre)
        else:
            print(f"{sub}/{nombre} ok")
    return fallas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["eph", "engho", "otros", "anuarios"])
    a = ap.parse_args()
    fallas = []
    if a.solo in (None, "eph"):
        fallas += bajar_eph()
    if a.solo in (None, "engho"):
        fallas += bajar_engho()
    if a.solo in (None, "otros"):
        fallas += bajar_otros()
    if a.solo in (None, "anuarios"):
        fallas += bajar_anuarios()
    if fallas:
        print("\nNO SE PUDIERON DESCARGAR:", *fallas, sep="\n  ")
        sys.exit(1)
    print("\nDescarga completa.")
