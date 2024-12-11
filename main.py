from fastapi import FastAPI

app = FastAPI()


@app.get("/saludo/{frase}")
def custom_saludo(frase: str):
    return {"message": frase}