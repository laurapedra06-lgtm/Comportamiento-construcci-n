# Expansión de la superficie construida · El Salvador

Aplicación de demostración con datos de expansión urbana procesados por la
División de Desarrollo Sostenible y Asentamientos Humanos de la CEPAL.

## Ejecutar en local

```
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501` en el navegador.

## Publicar

1. Subir esta carpeta a un repositorio de GitHub.
2. Entrar a share.streamlit.io con la cuenta de GitHub.
3. Seleccionar el repositorio e indicar `app.py` como archivo principal.

La publicación tarda un par de minutos. Cada cambio que se suba al
repositorio actualiza la aplicación de forma automática.

## Estructura

```
app.py                  interfaz y gráficas
requirements.txt        librerías
datos/sv_serie.csv      serie de El Salvador por grado de urbanización
datos/regional.csv      comparación de los 30 países, GHSL y GLAD
```

## Sobre los datos

Los archivos CSV se generan fuera de esta aplicación con los scripts de
análisis, a partir de los rásters de GHS-BUILT-S y GLCLU2000-2020. Los
rásters suman decenas de gigabytes y no se incluyen aquí: el entorno de
despliegue dispone de alrededor de 1 GB de memoria.

Para actualizar los datos, se regeneran los CSV y se suben al repositorio.

## Fuentes

- JRC/Copernicus, GHS-COUNTRY-STATS R2024A y GHS-BUILT-S R2023A
- GLAD/UMD, GLCLU2000-2020 versión 1
