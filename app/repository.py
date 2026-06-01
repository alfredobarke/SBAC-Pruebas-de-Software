import os
import json
import shutil
from datetime import datetime


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


# ─────────────────────────────────────────────
#  NUEVAS FUNCIONES: commit, history, checkout
# ─────────────────────────────────────────────

def commit(message):
    """Crea una nueva versión guardando una copia de todos los archivos rastreados."""

    if not os.path.exists(".sbac"):
        print("Repositorio no inicializado")
        return

    with open(".sbac/tracked_files.json", "r") as f:
        tracked = json.load(f)

    if not tracked:
        print("No hay archivos rastreados. Usa 'sbac add <archivo>' primero.")
        return

    # Leer historial de commits
    with open(".sbac/metadata.json", "r") as f:
        metadata = json.load(f)

    # Generar ID del commit (incremental)
    commit_id = len(metadata) + 1
    commit_key = f"commit_{commit_id:03d}"

    # Crear carpeta para este commit
    commit_dir = f".sbac/commits/{commit_key}"
    os.makedirs(commit_dir)

    # Copiar cada archivo rastreado al commit
    for file in tracked:
        if os.path.exists(file):
            shutil.copy2(file, commit_dir)
        else:
            print(f"Advertencia: '{file}' no encontrado, se omite.")

    # Guardar metadatos del commit
    metadata[commit_key] = {
        "id": commit_id,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": tracked.copy()
    }

    with open(".sbac/metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Commit #{commit_id} creado: \"{message}\"")


def history():
    """Muestra el historial de commits."""

    if not os.path.exists(".sbac"):
        print("Repositorio no inicializado")
        return

    with open(".sbac/metadata.json", "r") as f:
        metadata = json.load(f)

    if not metadata:
        print("No hay commits registrados.")
        return

    print("=== Historial de versiones ===")
    for key, data in sorted(metadata.items(), key=lambda x: x[1]["id"], reverse=True):
        print(f"\n  #{data['id']} - {data['timestamp']}")
        print(f"  Mensaje : {data['message']}")
        print(f"  Archivos: {', '.join(data['files'])}")


def checkout(commit_id):
    """Regresa el repositorio al estado de un commit específico."""

    if not os.path.exists(".sbac"):
        print("Repositorio no inicializado")
        return

    commit_key = f"commit_{int(commit_id):03d}"
    commit_dir = f".sbac/commits/{commit_key}"

    if not os.path.exists(commit_dir):
        print(f"El commit #{commit_id} no existe.")
        return

    with open(".sbac/metadata.json", "r") as f:
        metadata = json.load(f)

    commit_data = metadata.get(commit_key)
    if not commit_data:
        print(f"Metadatos del commit #{commit_id} no encontrados.")
        return

    # Restaurar archivos desde la carpeta del commit
    for file in commit_data["files"]:
        src = os.path.join(commit_dir, os.path.basename(file))
        if os.path.exists(src):
            shutil.copy2(src, file)
            print(f"  Restaurado: {file}")
        else:
            print(f"  Advertencia: '{file}' no encontrado en el commit.")

    print(f"\nCheckout al commit #{commit_id} (\"{commit_data['message']}\") completado.")
