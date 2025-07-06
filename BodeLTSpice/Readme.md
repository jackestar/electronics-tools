## Requisitos

Instala las dependencias necesarias con:

```
pip install -r requirements.txt
```

## Uso

### Analizar Bode Plot

El script [`analyze_bode.py`](BodeLTSpice/analyze_bode.py) analiza archivos de datos de Bode (por defecto `bode_data.txt` o el archivo que especifiques):

```
python analyze_bode.py
```

O bien, para analizar un archivo específico:

```
python analyze_bode.py plot.txt
```

### Encontrar el valor máximo de V(out)

El script [`top.py`](BodeLTSpice/top.py) busca el valor más alto de `V(out)` en un archivo de datos con formato de tabla (por ejemplo, generado por LTspice):

```
python top.py <archivo_de_datos.txt>
```

Ejemplo:

```
python top.py bode_data.txt
```

Esto mostrará el valor máximo de `V(out)` y el tiempo (o frecuencia) en el que ocurre.