from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os

app = FastAPI(title="Motor IA Eikôn - SIRLA Profesional")

# --- 1. MODELO DE DATOS ---
class PeticionFoxPro(BaseModel):
    titulo_puesto: str

# --- 2. CONFIGURACIÓN ---
EXCEL_PATH = r"C:\Users\EIKON\Downloads\CatalogoOcupacional.csv"

# Variables globales
df_sirla = None
vectorizador = None
matriz_tfidf_sirla = None

def cargar_y_entrenar():
    global df_sirla, vectorizador, matriz_tfidf_sirla
    
    print(f"--- Intentando cargar: {EXCEL_PATH} ---")
    
    if not os.path.exists(EXCEL_PATH):
        print(f"ERRO CRÍTICO: Archivo no encontrado en la ruta.")
        return False

    # Intentamos primero con Latin-1 (que es el que causó el error 0xcd)
    encodings_a_probar = ['latin1', 'utf-8', 'cp1252']
    exito = False

    for encoding_actual in encodings_a_probar:
        try:
            print(f"Probando codificación: {encoding_actual}...")
            df_sirla = pd.read_csv(EXCEL_PATH, sep=',', encoding=encoding_actual, header=None, names=['codigo', 'descripcion'])
            exito = True
            print(f"¡Carga exitosa con {encoding_actual}!")
            break
        except Exception:
            continue

    if not exito:
        print("No se pudo leer el archivo con ninguna codificación conocida.")
        return False

    try:
        # Limpieza básica
        df_sirla = df_sirla.dropna(subset=['descripcion'])
        df_sirla['descripcion'] = df_sirla['descripcion'].astype(str)
        df_sirla['codigo'] = df_sirla['codigo'].astype(str)
        
        # Inicializando el Vectorizador
        vectorizador = TfidfVectorizer() 
        matriz_tfidf_sirla = vectorizador.fit_transform(df_sirla['descripcion'])
        
        print(f"¡MOTOR LISTO! IA entrenada con {len(df_sirla)} ocupaciones.")
        return True
    except Exception as e:
        print(f"ERROR EN ENTRENAMIENTO: {str(e)}")
        return False

# Carga inicial al arrancar
cargar_y_entrenar()

# --- 3. RUTAS ---

@app.post("/sugerir")
def sugerir_codigo(peticion: PeticionFoxPro):
    global vectorizador, matriz_tfidf_sirla, df_sirla
    
    if vectorizador is None:
        if not cargar_y_entrenar():
            raise HTTPException(status_code=500, detail="La IA no pudo inicializarse. Revisa el archivo CSV.")

    texto = peticion.titulo_puesto.strip().lower()
    if not texto:
        raise HTTPException(status_code=400, detail="El título está vacío")

    try:
        vector_usuario = vectorizador.transform([texto])
        similitudes = cosine_similarity(vector_usuario, matriz_tfidf_sirla)
        
        indices_top_3 = similitudes[0].argsort()[-3:][::-1]

        resultados = []
        for idx in indices_top_3:
            score = similitudes[0][idx]
            if score > 0:
                resultados.append({
                    "codigo": str(df_sirla.iloc[idx]['codigo']),
                    "descripcion": str(df_sirla.iloc[idx]['descripcion']),
                    "porcentaje": round(float(score) * 100, 1)
                })

        return {"exito": True, "sugerencias": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/recargar_catalogo")
def recargar_catalogo():
    if cargar_y_entrenar():
        return {"exito": True, "mensaje": "Catálogo recargado con éxito."}
    else:
        raise HTTPException(status_code=500, detail="Error al recargar el archivo.")