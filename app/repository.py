import os
import json

def init_repository():
    if os.path.exists(".sbac"):
        print("Repositorio ya inicializado")
        return

    os.makedirs(".sbac/commits")
    os.makedirs(".sbac/baselines")

    with open(".sbac/tracked_files.json", "w") as f:
        json.dump([], f)

    with open(".sbac/metadata.json", "w") as f:
        json.dump({}, f)

    print("Repositorio SBAC inicializado")

def add_file(filename):

    if not os.path.exists(".sbac"):
        print("Repositorio no inicializado")
        return

    if not os.path.exists(filename):
        print("El archivo no existe")
        return

    with open(".sbac/tracked_files.json", "r") as f:
        tracked = json.load(f)

    if filename in tracked:
        print("Archivo ya agregado")
        return

    tracked.append(filename)

    with open(".sbac/tracked_files.json", "w") as f:
        json.dump(tracked, f, indent=4)

    print(f"{filename} agregado correctamente")

def status():

    if not os.path.exists(".sbac"):
        print("Repositorio no inicializado")
        return

    with open(".sbac/tracked_files.json", "r") as f:
        tracked = json.load(f)

    print("=== Estado del repositorio ===")

    if not tracked:
        print("No hay archivos rastreados")
        return

    for file in tracked:
        print(f"- {file}")