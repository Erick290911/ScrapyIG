from fastapi import FastAPI  # Importa la clase principal FastAPI

# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Define una ruta (endpoint) para manejar solicitudes GET en "/"
@app.get("/")
def leer_raiz():
    return {"mensaje": "Hola Mundo"}