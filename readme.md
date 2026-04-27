# 🧠 Motor de IA para Homologación de Puestos (Eikôn - SIRLA)

Este microservicio implementa una solución de **Procesamiento de Lenguaje Natural (NLP)** diseñada para automatizar la clasificación de puestos de trabajo dentro del ecosistema **Eikôn ERP**, vinculándolos con el catálogo oficial del **SIRLA** (Sistema Integrado de Registro Laboral) de la República Dominicana.

---

## 🛠️ Stack Tecnológico
La solución utiliza herramientas de alto rendimiento para garantizar latencias mínimas (inferiores a 15ms):

* **Lenguaje:** Python 3.10+
* **Framework API:** [FastAPI](https://fastapi.tiangolo.com/) (Elegido por su alto rendimiento y generación automática de OpenAPI/Swagger).
* **Servidor ASGI:** Uvicorn (Con soporte para recarga en caliente y concurrencia).
* **Ciencia de Datos:** * **Pandas:** Gestión de estructuras de datos tabulares y limpieza de CSV.
    * **Scikit-Learn:** Implementación de algoritmos de Vectorización y Métricas de Similitud.

---

## 🧬 Arquitectura de la Inteligencia Artificial

A diferencia de una búsqueda tradicional por texto (LIKE en SQL), este motor utiliza **análisis vectorial** para entender la relevancia semántica entre las descripciones de cargos.

### 1. Vectorización TF-IDF
Convierte las descripciones en coordenadas matemáticas en un espacio multidimensional.
- **TF (Term Frequency):** Mide la importancia de una palabra específica en un puesto.
- **IDF (Inverse Document Frequency):** Reduce el peso de conectores comunes (como "de", "el", "para") y resalta términos técnicos y sustantivos clave ("Analista", "Soldador", "Contable").

### 2. Similitud del Coseno
Calcula el ángulo entre el vector de entrada (enviado desde FoxPro) y la matriz del catálogo SIRLA pre-entrenada en memoria.
- **Métrica:** Devuelve un valor de 0 a 100% de confianza.
- **Ventaja:** Permite identificar que "Contador Sr." es semánticamente equivalente a "Contador Profesional" aunque las palabras no coincidan exactamente.

---

## 📡 Referencia de la API (Endpoints)

### `POST /sugerir`
Analiza un string de texto y devuelve las 3 mejores coincidencias encontradas en el catálogo nacional.

**Estructura de la Petición (Request Body):**
```json
{
  "titulo_puesto": "Analista de Software"
}
```
**Estructura de la Respuesta (200 OK):**
```
{
  "exito": true,
  "sugerencias": [
    {
      "codigo": "2512",
      "descripcion": "DESARROLLADOR DE SOFTWARE Y PROGRAMADOR / ANALISTA",
      "porcentaje": 94.2
    }
  ]
}
```

### `POST /recargar_catalogo`

Instruye a la IA para que lea nuevamente el archivo CSV y reentrene el modelo TF-IDF. Útil cuando el Ministerio de Trabajo publica actualizaciones del catálogo.

----

## ⚙️ Pipeline de Datos (ETL Interno)

El motor incluye un proceso de limpieza de datos "al vuelo" para asegurar la integridad de la información:

1. *Detección de Codificación (Encoding):* Implementa un bloque de prueba secuencial (`latin-1` -> `utf-8` -> `cp1252`) para manejar correctamente tildes y caracteres especiales dominicanos.

2. *Normalización:* Limpieza de espacios en blanco, eliminación de registros nulos y conversión de tipos de datos.

3. *Mapeo Automático:* Asignación de columnas por posición indexada (A: Código, B: Descripción) para garantizar compatibilidad con los archivos brutos del SIRLA que carecen de encabezados.

---------------
## 🔌 Protocolo de Integración en Visual FoxPro
El sistema Eikôn se comunica con el motor de IA mediante el modelo de objetos COM de Windows.

*Flujo de Interacción:*
1. *Captura:* El usuario digita el nombre del puesto en el formulario de mantenimiento de personal.

2. *Transmisión:* FoxPro instancia MSXML2.XMLHTTP y envía una petición POST al puerto 8000.

3. *Procesamiento:* FastAPI procesa el vector y devuelve la respuesta JSON.

4. *Auto-completado:* FoxPro deserializa el JSON (vía STREXTRACT) y rellena automáticamente los campos correspondientes.

---------------

## 🚀 Guía de Instalación Rápida

### 1. Instalar dependencias:

```
pip install fastapi uvicorn scikit-learn pandas
```

### 2. Iniciar Servidor:

```
py -m uvicorn api_nlp_sirla:app --reload
```

### 3. Acceso a Docs:

Navegue a http://127.0.0.1:8000/docs para acceder a la consola interactiva de Swagger UI.

