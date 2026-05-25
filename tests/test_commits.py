import os
import json
import pytest
from app.repository import init_repository, add_file, commit, history, checkout


def test_commit_crea_carpeta(tmp_path):
    """commit debe crear una carpeta con los archivos rastreados."""
    os.chdir(tmp_path)
    init_repository()

    with open("archivo.txt", "w") as f:
        f.write("contenido inicial")

    add_file("archivo.txt")
    commit("primer commit")

    assert os.path.exists(".sbac/commits/commit_001")
    assert os.path.exists(".sbac/commits/commit_001/archivo.txt")


def test_commit_guarda_metadata(tmp_path):
    """commit debe guardar el mensaje y timestamp en metadata.json."""
    os.chdir(tmp_path)
    init_repository()

    with open("archivo.txt", "w") as f:
        f.write("hola")

    add_file("archivo.txt")
    commit("mi mensaje")

    with open(".sbac/metadata.json", "r") as f:
        metadata = json.load(f)

    assert "commit_001" in metadata
    assert metadata["commit_001"]["message"] == "mi mensaje"
    assert "timestamp" in metadata["commit_001"]
    assert "archivo.txt" in metadata["commit_001"]["files"]


def test_commit_sin_archivos(tmp_path, capsys):
    """commit sin archivos rastreados debe mostrar advertencia."""
    os.chdir(tmp_path)
    init_repository()
    commit("sin archivos")

    captured = capsys.readouterr()
    assert "No hay archivos rastreados" in captured.out


def test_commit_incremental(tmp_path):
    """Varios commits deben tener IDs incrementales."""
    os.chdir(tmp_path)
    init_repository()

    with open("a.txt", "w") as f:
        f.write("v1")

    add_file("a.txt")
    commit("commit 1")

    with open("a.txt", "w") as f:
        f.write("v2")

    commit("commit 2")

    with open(".sbac/metadata.json", "r") as f:
        metadata = json.load(f)

    assert "commit_001" in metadata
    assert "commit_002" in metadata


def test_history_sin_commits(tmp_path, capsys):
    """history sin commits debe indicar que no hay registros."""
    os.chdir(tmp_path)
    init_repository()
    history()

    captured = capsys.readouterr()
    assert "No hay commits" in captured.out


def test_history_muestra_commits(tmp_path, capsys):
    """history debe mostrar los commits creados."""
    os.chdir(tmp_path)
    init_repository()

    with open("f.txt", "w") as f:
        f.write("datos")

    add_file("f.txt")
    commit("version inicial")
    history()

    captured = capsys.readouterr()
    assert "version inicial" in captured.out


def test_checkout_restaura_archivo(tmp_path):
    """checkout debe restaurar el contenido del archivo al estado del commit."""
    os.chdir(tmp_path)
    init_repository()

    with open("code.txt", "w") as f:
        f.write("version 1")

    add_file("code.txt")
    commit("v1")

    # Modificar el archivo
    with open("code.txt", "w") as f:
        f.write("version 2")

    commit("v2")

    # Regresar al commit 1
    checkout(1)

    with open("code.txt", "r") as f:
        contenido = f.read()

    assert contenido == "version 1"


def test_checkout_commit_inexistente(tmp_path, capsys):
    """checkout con ID inválido debe mostrar error."""
    os.chdir(tmp_path)
    init_repository()
    checkout(99)

    captured = capsys.readouterr()
    assert "no existe" in captured.out
