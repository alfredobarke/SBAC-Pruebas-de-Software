import os
import json
import pytest
from app.repository import (
    init_repository,
    add_file,
    create_baseline,
    list_baselines,
    restore_baseline,
)


# ─── helpers ────────────────────────────────────────────────────────────────

def _setup(tmp_path, filenames_contents):
    """Inicializa repo, crea archivos y los agrega al tracking."""
    os.chdir(tmp_path)
    init_repository()
    for name, content in filenames_contents.items():
        p = tmp_path / name
        p.write_text(content)
        add_file(name)


# ─── create_baseline ────────────────────────────────────────────────────────

class TestCreateBaseline:

    def test_crea_directorio_baseline(self, tmp_path):
        _setup(tmp_path, {"archivo.txt": "v1"})
        create_baseline("release_1")
        assert os.path.exists(".sbac/baselines/release_1")

    def test_copia_archivos_al_baseline(self, tmp_path):
        _setup(tmp_path, {"codigo.py": "print('hola')"})
        create_baseline("v1.0")
        assert os.path.exists(".sbac/baselines/v1.0/codigo.py")

    def test_guarda_metadata_baseline(self, tmp_path):
        _setup(tmp_path, {"f.txt": "datos"})
        create_baseline("beta")
        assert os.path.exists(".sbac/baselines_meta.json")
        with open(".sbac/baselines_meta.json") as fh:
            meta = json.load(fh)
        assert "beta" in meta
        assert meta["beta"]["name"] == "beta"
        assert "timestamp" in meta["beta"]
        assert "f.txt" in meta["beta"]["files"]

    def test_multiples_baselines(self, tmp_path):
        _setup(tmp_path, {"a.txt": "x"})
        create_baseline("alpha")
        create_baseline("beta")
        with open(".sbac/baselines_meta.json") as fh:
            meta = json.load(fh)
        assert "alpha" in meta
        assert "beta" in meta

    def test_sin_repositorio(self, tmp_path, capsys):
        os.chdir(tmp_path)
        create_baseline("cualquiera")
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_sin_archivos_rastreados(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        create_baseline("vacia")
        out = capsys.readouterr().out
        assert "no hay archivos" in out.lower()

    def test_baseline_duplicado(self, tmp_path, capsys):
        _setup(tmp_path, {"x.txt": "1"})
        create_baseline("dup")
        create_baseline("dup")
        out = capsys.readouterr().out
        assert "ya existe" in out.lower()

    def test_contenido_copiado_es_correcto(self, tmp_path):
        _setup(tmp_path, {"data.txt": "contenido_original"})
        create_baseline("snap")
        stored = open(".sbac/baselines/snap/data.txt").read()
        assert stored == "contenido_original"


# ─── list_baselines ─────────────────────────────────────────────────────────

class TestListBaselines:

    def test_sin_repositorio(self, tmp_path, capsys):
        os.chdir(tmp_path)
        list_baselines()
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_sin_baselines(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        list_baselines()
        out = capsys.readouterr().out
        assert "no hay" in out.lower()

    def test_muestra_baseline_creado(self, tmp_path, capsys):
        _setup(tmp_path, {"f.txt": "hola"})
        create_baseline("release_1")
        capsys.readouterr()          # limpiar salida de create_baseline
        list_baselines()
        out = capsys.readouterr().out
        assert "release_1" in out

    def test_muestra_multiples_baselines(self, tmp_path, capsys):
        _setup(tmp_path, {"f.txt": "hola"})
        create_baseline("alpha")
        create_baseline("beta")
        capsys.readouterr()
        list_baselines()
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out

    def test_muestra_archivos_en_baseline(self, tmp_path, capsys):
        _setup(tmp_path, {"main.py": "code"})
        create_baseline("snap")
        capsys.readouterr()
        list_baselines()
        out = capsys.readouterr().out
        assert "main.py" in out


# ─── restore_baseline ───────────────────────────────────────────────────────

class TestRestoreBaseline:

    def test_restaura_contenido_original(self, tmp_path):
        _setup(tmp_path, {"app.txt": "version_original"})
        create_baseline("v1")

        # Modificar el archivo
        (tmp_path / "app.txt").write_text("version_modificada")

        restore_baseline("v1")

        assert (tmp_path / "app.txt").read_text() == "version_original"

    def test_sin_repositorio(self, tmp_path, capsys):
        os.chdir(tmp_path)
        restore_baseline("inexistente")
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_baseline_inexistente(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        restore_baseline("no_existe")
        out = capsys.readouterr().out
        assert "no existe" in out.lower()

    def test_restaura_multiples_archivos(self, tmp_path):
        _setup(tmp_path, {"a.txt": "A", "b.txt": "B"})
        create_baseline("multi")

        (tmp_path / "a.txt").write_text("A_mod")
        (tmp_path / "b.txt").write_text("B_mod")

        restore_baseline("multi")

        assert (tmp_path / "a.txt").read_text() == "A"
        assert (tmp_path / "b.txt").read_text() == "B"

    def test_mensaje_confirmacion(self, tmp_path, capsys):
        _setup(tmp_path, {"x.txt": "data"})
        create_baseline("ok")
        capsys.readouterr()
        restore_baseline("ok")
        out = capsys.readouterr().out
        assert "restaurada" in out.lower() or "restaurado" in out.lower()

    def test_restaurar_no_modifica_baseline_almacenado(self, tmp_path):
        _setup(tmp_path, {"f.txt": "original"})
        create_baseline("snap")
        (tmp_path / "f.txt").write_text("modificado")
        restore_baseline("snap")
        # El archivo en el baseline no se debe haber alterado
        stored = open(".sbac/baselines/snap/f.txt").read()
        assert stored == "original"
