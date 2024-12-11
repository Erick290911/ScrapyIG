from fastapi import FastAPI  # Importa la clase principal FastAPI

app = FastAPI() # Crea una instancia de la aplicación FastAPI


@app.get("/saludo/{frase}") # Define una ruta (endpoint) para manejar solicitudes GET en "/"
def custom_saludo(frase: str): #Resive la frase desde el apartadourl 
    return {"message": frase}
