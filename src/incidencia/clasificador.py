"""Clasificación fiscal de los artículos de la ENGHo (IVA e Impuestos Internos).

Cada artículo recibe:
  - clase_iva: tratamiento legal en IVA al consumidor final (ver CLASES_IVA);
  - clase_internos: rubro de impuestos selectivos que lo grava, si corresponde.

La asignación se hace con reglas explícitas sobre la descripción del artículo y de su
subclase, iguales para las tres ediciones (2004/05, 2012/13, 2017/18). El resultado
artículo por artículo se guarda en data/processed/clasificacion_articulos_<edición>.csv
para que cualquiera pueda auditarlo y corregirlo.

Base legal (Ley de IVA 23.349, t.o. 1997):
  * art. 28 primer párrafo: alícuota general 21%.
  * art. 28 inc. a): 10,5% para carnes bovinas/ovinas/caprinas frescas, frutas,
    legumbres y hortalizas frescas, refrigeradas o congeladas, miel, granos y legumbres
    secas, harina de trigo, pan, galletas, facturas y galletitas sin envasar.
    Carnes aviar, porcina y cunícula: 10,5% desde 02/2018 (Ley 27.430, verificado).
  * art. 7 inc. a): libros, diarios y revistas exentos. inc. f): agua ordinaria, pan
    común, leche sin aditivos (a consumidores finales), medicamentos en la reventa.
    inc. h): educación (pto. 3), transporte urbano de pasajeros y taxis (pto. 12),
    alquiler de vivienda (pto. 22), entre otros.
  * Decreto 567/2019 (verificado): alícuota 0% para la canasta alimentaria del Anexo
    entre el 16/08/2019 y el 31/12/2019. NO fue prorrogado.
Estado: la lectura artículo por artículo de la ley NO fue contrastada con un texto
ordenado vigente para cada año; las reglas son una aproximación documentada.
"""
from __future__ import annotations

import re
import unicodedata

# Alícuota legal por clase y año la define indirectos.alicuota_iva().
CLASES_IVA = {
    "G21": "gravado 21%",
    "G105": "gravado 10,5%",
    "EX": "exento / no alcanzado",
    "AVPO": "carne aviar y porcina: 21% hasta 01/2018, 10,5% después",
    "C567_21": "canasta Dto. 567/2019, alícuota base 21%",
    "C567_105": "canasta Dto. 567/2019, alícuota base 10,5%",
    "MED": "medicamentos: IVA 21% en la etapa fabricante/importador; reventa exenta",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def sector_coicop(edicion: str, articulo: str) -> str:
    """División tipo COICOP ('01'..'12') a partir del código de artículo."""
    a = str(articulo)
    if edicion == "2017":
        return a[1:3]
    # Nomenclador ENGHo 2004/05 y 2012/13 (9 capítulos)
    if a.startswith("122"):
        return "02"
    if a.startswith("13"):
        return "11"
    if a.startswith("1"):
        return "01"
    if a.startswith("2"):
        return "03"
    if a.startswith("3"):
        return "04"
    if a.startswith("4"):
        return "05"
    if a.startswith("5"):
        return "06"
    if a.startswith("61"):
        return "07"
    if a.startswith("62"):
        return "08"
    if a.startswith("7"):
        return "09"
    if a.startswith("8"):
        return "10"
    if a.startswith("911"):
        return "02"
    return "12"


_SEMIPREP = r"semiprepar|hamburgues|milanesa|rebozad|preparados|formitas|patitas|surtido"


def clase_iva(sector: str, desc: str, subdesc: str) -> tuple[str, str]:
    """Devuelve (clase_iva, regla aplicada)."""
    d, s = norm(desc), norm(subdesc)

    if sector == "01":
        if re.search(r"agua potable", d):
            return "EX", "agua ordinaria (art. 7 f)"
        if re.search(r"^pan (tipo )?frances|^pan integral fresco|^panes y panecillos frescos|"
                     r"^pan blanco de molde|^pan fresco|^pan comun|^pan$|^pan (blanco|negro|de salvado)", d) \
                and not re.search(r"envasad|rallad|lactal", d):
            return "EX", "pan común (art. 7 f)"
        if re.search(r"^leche", d):
            if re.search(r"soja|vegetal|condensad|evaporad|chocolat|fortificad", d):
                return "G21", "leche con procesos/otros"
            if re.search(r"aditament|saboriz|cultivad", d):
                return "C567_21", "leche con aditivos (Dto. 567/2019)"
            if re.search(r"surtido", d):
                return "EX", "leche (surtido)"
            return "EX", "leche sin aditivos (art. 7 f)"
        if re.search(r"pan rallado|rebozador", d):
            return "C567_21", "pan rallado (Dto. 567/2019)"
        if re.search(r"facturas|galletas, grisines|galletitas .*sueltas|pancitos|bollitos|bizcochos de grasa|"
                     r"^galletas|^grisines", d) and not re.search(r"envasad", d):
            return "G105", "panificados sin envasar (art. 28 a)"
        if re.search(r"harina de trigo", d):
            return "C567_105", "harina de trigo (art. 28 a; Dto. 567/2019)"
        if re.search(r"cereales en grano", d):
            return "G105", "granos (art. 28 a)"
        if re.search(r"^arroz( blanco| integral)?$|^arroz (blanco|integral|comun)", d):
            return "C567_21", "arroz (Dto. 567/2019)"
        if re.search(r"harina de maiz|polenta", d):
            return "C567_21", "harina de maíz (Dto. 567/2019)"
        if re.search(r"fideos secos|pastas secas", d):
            return "C567_21", "pastas secas (Dto. 567/2019)"
        if "carne vacuna" in s or "carne bovina" in s:
            if re.search(_SEMIPREP, d) and "surtido" not in d:
                return "G21", "carne semipreparada"
            return "G105", "carne bovina fresca (art. 28 a)"
        if "carne de ave" in s:
            if re.search(_SEMIPREP, d) and "surtido" not in d:
                return "G21", "ave semipreparada"
            return "AVPO", "carne aviar (Ley 27.430)"
        if "porcina" in s:
            if re.search(r"ovin|caprin|cordero|chivito", d):
                return "G105", "carne ovina/caprina (art. 28 a)"
            if re.search(_SEMIPREP, d) and "surtido" not in d:
                return "G21", "cerdo semipreparado"
            return "AVPO", "carne porcina (Ley 27.430)"
        if "frutas frescas" in s:
            return "G105", "frutas frescas o congeladas (art. 28 a)"
        if re.search(r"verduras.*fresc", s) or s.startswith("verduras frescas"):
            if re.search(r"aceitunas|milanesa|semiprepar", d):
                return "G21", "hortaliza procesada"
            return "G105", "hortalizas frescas o congeladas (art. 28 a)"
        if "congelados y semipreparados" in s:
            if re.search(r"^verduras congeladas|tuberculos congelados|^legumbres congeladas", d):
                return "G105", "hortalizas congeladas (art. 28 a)"
            return "G21", "semipreparado vegetal"
        if re.search(r"(arvejas|lentejas|porotos|garbanzos|otras legumbres) sec", d):
            return "G105", "legumbres secas (art. 28 a)"
        if re.search(r"en conserva|en almibar", d) and re.search(r"fruta|verdura|legumbre", s):
            return "C567_21", "conservas de frutas/hortalizas/legumbres (Dto. 567/2019)"
        if re.search(r"^miel", d):
            return "G105", "miel (art. 28 a)"
        if re.search(r"^aceite (mezcla|de girasol|de maiz)|^aceite comun", d):
            return "C567_21", "aceite girasol/maíz/mezcla (Dto. 567/2019)"
        if re.search(r"^azucar", d):
            return "C567_21", "azúcar (Dto. 567/2019)"
        if re.search(r"^huevos", d):
            return "C567_21", "huevos (Dto. 567/2019)"
        if re.search(r"^yogur", d):
            return "C567_21", "yogur (Dto. 567/2019)"
        if re.search(r"^yerba|^mate cocido|^te( |$)", d):
            return "C567_21", "yerba, mate cocido, té (Dto. 567/2019)"
        return "G21", "alimentos y bebidas: general"

    if sector == "04":
        if re.search(r"alquiler|pensionista|expensas|gastos comunes|abonos para mantenimiento|tiempo compartido", d):
            return "EX", "alquiler de vivienda y expensas (art. 7 h.22 / no alcanzado)"
        if re.search(r"recoleccion de residuos|alumbrado|barrido", d):
            return "EX", "tasa municipal, no es precio"
        if re.search(r"garrafa|gas a granel|gas envasado|gas .*tubo", d):
            return "G105", "gas licuado (art. 28; no verificado)"
        return "G21", "vivienda: general (servicios públicos residenciales 21%)"

    if sector == "05":
        if "servicio domestico" in s or "servicios domesticos" in s:
            return "EX", "trabajo en casas particulares: no es venta gravada"
        return "G21", "equipamiento: general"

    if sector == "06":
        if "farmaceutic" in s or re.search(r"^medicamentos", s):
            return "MED", "medicamentos (art. 7 f: reventa exenta)"
        if "seguros relacionados con la salud" in s:
            return "G105", "medicina prepaga (art. 28; no verificado)"
        if re.search(r"chequeras|ordenes", d):
            return "EX", "coseguros de obra social (art. 7 h.7)"
        return "G21", "salud: general"

    if sector == "07":
        if re.search(r"internacional| int\b|al exterior", d):
            return "EX", "transporte internacional (art. 7 h.13)"
        if re.search(r"colectivo|subte|tren corta|abono de tren|boleto tren|taxi|remis|transporte escolar|"
                     r"charter|abono de lancha|otros transportes publicos|tarjeta recargable|boleto de tren$|"
                     r"transporte urbano|omnibus urbano", d):
            return "EX", "transporte urbano de pasajeros y taxis (art. 7 h.12)"
        if re.search(r"larga distancia|cabotaje|buque|aliscafo|media distancia|avion|aereo", d):
            return "G105", "transporte de pasajeros de larga distancia (art. 28)"
        if "ferroviario" in s or "transporte automotor" in s or "servicios de transporte" in s:
            return "EX", "transporte público de pasajeros (art. 7 h.12)"
        return "G21", "transporte: general"

    if sector == "09":
        if re.search(r"libros|diarios|textos|publicaciones periodicas", s) or re.search(r"^libro|^revista|^diario", d):
            return "EX", "libros, diarios y revistas (art. 7 a)"
        if re.search(r"teatro", d):
            return "EX", "espectáculos teatrales (art. 7 h.10)"
        if re.search(r"prode|loteria|quiniela|juegos de azar", d) or "juegos de azar" in s:
            return "EX", "juegos de azar (art. 7)"
        if re.search(r"cuota de club", d):
            return "EX", "cuotas de entidades sin fines de lucro"
        if re.search(r"exterior", d):
            return "EX", "turismo al exterior"
        if "computacion" in s and re.search(r"computadora|notebook|cpu|impresora|monitor|disco|mouse|teclado", d):
            return "G105", "informática (Dto. 493/2001; no verificado)"
        return "G21", "esparcimiento: general"

    if sector == "10":
        if re.search(r"no formal|no atribuible", s) and not re.search(r"especial", d):
            return "G21", "enseñanza no formal"
        if re.search(r"material escolar", s):
            return "G21", "útiles escolares"
        return "EX", "servicios educativos y textos (art. 7 h.3 y a)"

    if sector == "12":
        if re.search(r"seguro de vida|seguros de retiro", d):
            return "EX", "seguros de vida y retiro (art. 7 h)"
        if re.search(r"jardin maternal|sepelio|funerar|nicho|panteon|documentos|cuotas de afiliacion|"
                     r"transferencias", d):
            return "EX", "servicios exentos / tasas"
        return "G21", "bienes y servicios varios: general"

    # 02 alcohol y tabaco, 03 indumentaria, 08 comunicaciones, 11 restaurantes
    return "G21", "general"


def clase_internos(sector: str, desc: str, subdesc: str) -> str:
    """Rubro de impuestos selectivos (clasificación DNIAF 3.2.x / 3.3.2). '' si no aplica.

    Ley 24.674: tabaco, bebidas alcohólicas, cervezas, bebidas analcohólicas, vehículos,
    telefonía celular. Los vinos no están gravados por Internos.
    """
    d, s = norm(desc), norm(subdesc)
    if sector == "02":
        if re.search(r"cigarr|tabaco", d):
            return "tabaco"
        if "cerveza" in d:
            return "cerveza"
        if re.search(r"ginebra|whisky|licor|destilad|grapa|vodka|fernet|aperitivo|cana", d) and "vino" not in s:
            return "alcohol"
        if "destilad" in s:
            return "alcohol"
        return ""
    if sector == "01":
        if re.search(r"gaseosa|jugos y refrescos|agua mineral|aguas minerales|soda|aguas saborizadas|"
                     r"isotonic|energizante|aperitivo sin alcohol|jugos? ", d) and not re.search(r"potable|hielo", d):
            return "analcoholicas"
        return ""
    if sector == "07":
        if re.search(r"compra de automovil|compra-venta de vehiculos", s) or re.search(r"^automovil|^auto ", d):
            return "vehiculos"
        return ""
    if sector == "08":
        if re.search(r"celular|movil", d) and re.search(r"servicio|telefonia", s) and "internet" not in d:
            return "telefonia"
        return ""
    return ""
