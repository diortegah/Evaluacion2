import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = "ca2962de-96fa-4228-8ec0-c303bb8f672e"

traduccion_direcciones = {
    "Turn right": "Gire a la derecha",
    "Turn left": "Gire a la izquierda",
    "Continue": "Continúe",
    "Head": "Diríjase",
    "Slight right": "Giro leve a la derecha",
    "Slight left": "Giro leve a la izquierda",
    "Destination": "Destino",
    "At the roundabout": "En la rotonda",
    "Take the": "Tome la",
    "Exit": "salida",
    "toward": "hacia",
    "Arrive at destination": "Ha llegado a su destino",
    "At roundabout, take exit": "En la rotonda, tome la salida.",
    "Turn sharp right onto": "Gire fuertemente a la derecha hacia",
    "Turn sharp left onto": "Gire fuertemente a la izquierda hacia",
    "Turn slight right onto": "Gire ligeramente a la derecha hacia",
    "Turn slight left onto": "Gire ligeramente a la izquierda hacia",
    "Keep left onto": "manténgase a la izquierda en",
    "Keep right and drive": "Manténgase a la derecha y conduzca",
    "Keep left": "Manténgase a la izquierda",
    "keep right": "Manténgase a la derecha",
    "keep right and take": "Manténgase a la derecha y tome"
    
}


def traducir_texto(texto):
    for eng, esp in traduccion_direcciones.items():
        texto = texto.replace(eng, esp)
    return texto

def geocoding(location, key):
    while location.strip() == "":
        location = input("La ubicación no puede estar vacía. Ingrese la ubicación nuevamente: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?" 
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(f"\nUbicación encontrada: {new_loc} (Tipo: {value})")
        print(f"URL del servicio de geocodificación: {url}")

    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(f"Error al obtener la ubicación ({json_status}): {json_data.get('message', 'Error desconocido')}")

    return json_status, lat, lng, new_loc


while True:
    loc1 = input("\nIngrese la ubicación de inicio (o 's' para salir): ").strip()
    if loc1.lower() == "s":
        print("Programa finalizado.")
        break

    orig = geocoding(loc1, key)
    print(orig)

    print("-----------------------------------------------------------------------------------------------------------------------")

    loc2 = input("\nIngrese la ubicación de destino (o 's' para salir): ").strip()
    if loc2.lower() == "s":
        print("Programa finalizado.")
        break

    dest = geocoding(loc2, key)
    print(dest)

    print("\nPerfiles de vehículos disponibles:")
    print("  - auto")
    print("  - bicicleta")
    print("  - a pie")
    vehicle = input("Seleccione un perfil de vehículo: ").strip().lower()

    if vehicle in ["auto", "car"]:
        vehicle = "car"
    elif vehicle in ["bicicleta", "bike"]:
        vehicle = "bike"
    elif vehicle in ["a pie", "foot"]:
        vehicle = "foot"
    elif vehicle == "s":
        print("Programa finalizado.")
        break
    else:
        vehicle = "car"
        print("No se ingresó un perfil válido. Se usará el perfil por defecto: 'auto'.")

    print("\n===================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp

        response = requests.get(paths_url)
        paths_status = response.status_code
        paths_data = response.json()

        print(f"Estado del servicio de rutas: {paths_status}")
        print(f"URL del servicio de rutas:\n{paths_url}")
        print("===================================================")
        print(f"Ruta desde {orig[3]} hasta {dest[3]} usando '{vehicle}'")
        print("===================================================")

        if paths_status == 200:
            km = paths_data["paths"][0]["distance"] / 1000
            miles = km / 1.61
            total_seg = int(paths_data["paths"][0]["time"] / 1000)
            hr = total_seg // 3600
            min = (total_seg % 3600) // 60
            seg = total_seg % 60

            print(f"Distancia total: {km:.2f} km / {miles:.2f} millas")
            print(f"Duración estimada: {hr:02d}:{min:02d}:{seg:02d}")
            print("===================================================")
            print("Instrucciones del viaje (paso a paso):")
            print("===================================================")
            for each in paths_data["paths"][0]["instructions"]:
                path = traducir_texto(each["text"])
                distance = each["distance"] / 1000
                print(f"{path} ({distance:.2f} km / {(distance/1.61):.2f} millas)")
            print("===================================================")
        else:
            print("Error al obtener la ruta:", paths_data.get("message", "Error desconocido"))
    else:
        print("No se pudo obtener la geolocalización para una o ambas ubicaciones.")
