import instaloader #Librería para interactuar con Instagram, permite iniciar sesión y obtener datos como seguidores y perfiles.
import pandas as pd #Para manejar los datos extraídos y guardarlos en formato CSV.
import time #Para manejar pausas temporales entre solicitudes, evitando problemas con el servidor de Instagram.
import matplotlib.pyplot as plt #Para graficar los datos según la Ley de Benford.
from instaloader.exceptions import ConnectionException, BadResponseException #Manejan errores comunes al conectarse con Instagram.
from getpass import getpass  # Para ocultar la contraseña

# Configuración Inicio de de sesión en instagram
print("*** Sistema de Scrapy en Instagram ***")
nombre_usuario = input("Ingrese su nombre de usuario (Instagram): ") # Ingresar el Usuario
contrasena_usuario = getpass("Ingrese la contraseña de su Instagram: ")  # Oculta la contraseña al ingresarla
nombre_usuario_formateado = nombre_usuario.replace(" ", "_").lower() #Convierte el nombre de usuario a un formato seguro para usar como nombre de archivo.
output_csv = f"{nombre_usuario_formateado}_seguidores.csv" #Define el nombre del archivo CSV donde se guardarán los datos de los seguidores.

# Función para manejar errores y reintentar
def process_profile_with_retry(profile, retries=3): # funcion para ingresar al perfil 3 veces
    for attempt in range(retries): #Realiza hasta 3 intentos para acceder al perfil.
        try:
            return profile.followers #Devuelve la cantidad de seguidores si se accede correctamente.
        except (ConnectionException, BadResponseException) as e:
            print(f"Error al intentar acceder al perfil: {e}. Reintento {attempt + 1}/{retries}...")
            time.sleep(10) #Espera 10 segundos entre intentos para evitar bloqueos del servidor.
    print("No se pudo acceder al perfil después de múltiples intentos.")
    return None  #Si falla tras 3 intentos, devuelve None

# Crear instancia de Instaloader y autenticarse
loader = instaloader.Instaloader() 
try:
    loader.login(nombre_usuario, contrasena_usuario) #Inicia sesión con el nombre de usuario y contraseña.
except Exception as e: #Maneja errores como contraseñas incorrectas
    print(f"Error al iniciar sesión: {e}")
    exit(1)

# Obtener perfil principal
try:
    profile = instaloader.Profile.from_username(loader.context, nombre_usuario) #Carga los datos del perfil principal.
except Exception as e:
    print(f"Error al obtener el perfil principal: {e}")
    exit(1)

# Descargar datos de los seguidores
try:
    print("Descargando lista de seguidores...")
    followers = list(profile.get_followers()) #Obtiene un generador con los seguidores del perfil. Convierte el generador en una lista para su procesamiento.
except Exception as e:
    print(f"Error al descargar la lista de seguidores: {e}")
    exit(1)

# Mostrar lista de seguidores Muestra una lista numerada de seguidores, indicando el nombre de usuario y el número de seguidores de cada uno.
print("\nLista de seguidores:")
for idx, person in enumerate(followers, start=1):
    print(f"{idx}. {person.username} - {person.followers} seguidores")

# Selección de un seguidor
while True: #Repite hasta que se ingrese una opción válida.
    try:
        choice = int(input("\nSeleccione el número del seguidor que desea analizar: "))
        if 1 <= choice <= len(followers): #Recorre la lista de seguidores
            selected_person = followers[choice - 1] #Guarda el seguidor seleccionado.
            break
        else:
            print(f"Por favor, ingrese un número entre 1 y {len(followers)}.")
    except ValueError:
        print("Entrada no válida. Por favor, ingrese un número.")

# Descargar seguidores del seguidor seleccionado
data = []
try:
    print(f"Descargando seguidores de {selected_person.username}...")
    sub_followers = list(selected_person.get_followers()) #Obtiene la lista de seguidores del seguidor seleccionado.
    for idx, sub_person in enumerate(sub_followers, start=1):
        print(f"{idx}/{len(sub_followers)}: Procesando {sub_person.username}...")
        followers_count = process_profile_with_retry(sub_person) #cuenta los seguidores de la persona selecionada Maneja errores al obtener seguidores de cada perfil.
        if followers_count is not None:
            data.append({"username": sub_person.username, "followers": followers_count})
        else:
            print(f"Saltando {sub_person.username} debido a error.")

        # Guardar datos parciales
        pd.DataFrame(data).to_csv(f"{selected_person.username}_subseguidores.csv", index=False)
        time.sleep(2)
except Exception as e:
    print(f"Error al descargar los seguidores de {selected_person.username}: {e}")
    exit(1)

# Aplicar Ley de Benford
if data:
    df = pd.DataFrame(data)
    df["first_digit"] = df["followers"].astype(str).str[0].astype(int) # Extrae el primer dígito del número de seguidores.
    digit_counts = df["first_digit"].value_counts().sort_index() #Cuenta la frecuencia de cada dígito.

    plt.figure(figsize=(10, 6))
    plt.bar(digit_counts.index, digit_counts.values, color="skyblue") #Genera un gráfico de barras para mostrar la distribución.
    plt.xlabel("Primer dígito")
    plt.ylabel("Frecuencia")
    plt.title(f"Distribución de seguidores de {selected_person.username} (Ley de Benford)")
    plt.xticks(range(1, 10))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(f"grafico_benford_{selected_person.username}.png")
    plt.show()
else:
    print("No se generó ningún gráfico porque no hay datos suficientes.")