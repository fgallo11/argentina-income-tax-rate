# Datos de terceros (sólo para comparar)

No entran en ningún cálculo del proyecto; los usa `scripts/12_graficos_comunes.py` (desde `14_informe_graficos.py`) para la
comparación de la sección 1 del informe (figura 1).

| Archivo | Fuente | Qué es |
|---|---|---|
| `argendata_presion_por_decil_2018.csv` | Argendata (Fundar), tópico "Sistema tributario", CSV publicado en <https://argendata.fund.ar/data/TRIBUT/presion_tributaria_media_por_tipo_de_impuesto_y_decil.csv> (bajado el 17/11/2026). Datos de Pessino, Rasteletti, Artana y Lustig, *Distributional effects of taxation in Latin America*, Oxford Open Economics, vol. 4 | Presión tributaria media (% del ingreso) por decil y tipo de impuesto, Argentina 2018 |
| `ito_2026_argentina.csv` | International Tax Observatory, *Tax Progressivity and Inequality: Minimum Taxation of High-Net-Worth Individuals in Latin America and the Caribbean*, informe n.° 10, abril 2026 (figura 5, p. 16), y nota "Argentina: Impuesto Mínimo Efectivo sobre la Riqueza" (FES, p. 3) | Tasa efectiva por grupo (50% inferior, 40% medio, 10% y 1% superiores). `total`: cifras del texto de la nota. Composición: **leída a ojo del gráfico**, aproximada (±0,5 puntos); por eso la suma no da exactamente el total. Unidad: hogares; ingreso de Cuentas Nacionales (De Rosa, Flores y Morgan 2024; seguridad social de Fisher-Post y Gethin 2023). El informe no dice el año; sus fuentes llegan hasta 2019 |
