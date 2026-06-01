"""
Pruebas unitarias — validan cada función del sistema SBAC de forma aislada,
cubriendo comportamiento esperado, casos límite y mensajes de error.
"""

import os
import json
import pytest
from app.repository import (
    init_repository,
    add_file,
    status,
    commit,
    history,
    checkout,
    create_baseline,
    list_baselines,
    restore_baseline,
)


# ─── helpers ────────────────────────────────────────────────────────────────

def _init(tmp_path):
    os.chdir(tmp_path)
    init_repository()


def _add_and_commit(tmp_path, filename, content, message="commit"):
    p = tmp_path / filename
    p.write_text(content)
    add_file(filename)
    commit(message)


# ═══════════════════════════════════════════════════════════════════
#  init_repository
# ═══════════════════════════════════════════════════════════════════

class TestInitRepository:

    def test_crea_directorio_sbac(self, tmp_path):
        _init(tmp_path)
        assert os.path.exists(".sbac")

    def test_crea_directorio_commits(self, tmp_path):
        _init(tmp_path)
        assert os.path.exists(".sbac/commits")

    def test_crea_directorio_baselines(self, tmp_path):
        _init(tmp_path)
        assert os.path.exists(".sbac/baselines")

    def test_crea_tracked_files_json(self, tmp_path):
        _init(tmp_path)
        assert os.path.exists(".sbac/tracked_files.json")

    def test_tracked_files_json_es_lista_vacia(self, tmp_path):
        _init(tmp_path)
        with open(".sbac/tracked_files.json") as f:
            data = json.load(f)
        assert data == []

    def test_crea_metadata_json(self, tmp_path):
        _init(tmp_path)
        assert os.path.exists(".sbac/metadata.json")

    def test_metadata_json_es_dict_vacio(self, tmp_path):
        _init(tmp_path)
        with open(".sbac/metadata.json") as f:
            data = json.load(f)
        assert data == {}

    def test_ya_inicializado_imprime_advertencia(self, tmp_path, capsys):
        _init(tmp_path)
        init_repository()
        out = capsys.readouterr().out
        assert "ya inicializado" in out.lower()

    def test_ya_inicializado_no_sobreescribe_datos(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("x")
        add_file("f.txt")
        init_repository()  # segundo init
        with open(".sbac/tracked_files.json") as f:
            tracked = json.load(f)
        assert "f.txt" in tracked

    def test_imprime_mensaje_exito(self, tmp_path, capsys):
        _init(tmp_path)
        out = capsys.readouterr().out
        assert "inicializado" in out.lower()


# ═══════════════════════════════════════════════════════════════════
#  add_file
# ═══════════════════════════════════════════════════════════════════

class TestAddFile:

    def test_agrega_archivo_al_tracking(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "x.txt").write_text("hola")
        add_file("x.txt")
        with open(".sbac/tracked_files.json") as f:
            tracked = json.load(f)
        assert "x.txt" in tracked

    def test_sin_repositorio_imprime_error(self, tmp_path, capsys):
        os.chdir(tmp_path)
        add_file("cualquiera.txt")
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_archivo_inexistente_imprime_error(self, tmp_path, capsys):
        _init(tmp_path)
        add_file("no_existe.txt")
        out = capsys.readouterr().out
        assert "no existe" in out.lower()

    def test_archivo_duplicado_no_se_repite(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "a.txt").write_text("A")
        add_file("a.txt")
        add_file("a.txt")
        with open(".sbac/tracked_files.json") as f:
            tracked = json.load(f)
        assert tracked.count("a.txt") == 1

    def test_multiples_archivos_diferentes(self, tmp_path):
        _init(tmp_path)
        for name in ["a.txt", "b.txt", "c.txt"]:
            (tmp_path / name).write_text(name)
            add_file(name)
        with open(".sbac/tracked_files.json") as f:
            tracked = json.load(f)
        assert tracked == ["a.txt", "b.txt", "c.txt"]

    def test_imprime_confirmacion(self, tmp_path, capsys):
        _init(tmp_path)
        (tmp_path / "ok.txt").write_text("ok")
        add_file("ok.txt")
        out = capsys.readouterr().out
        assert "agregado" in out.lower()


# ═══════════════════════════════════════════════════════════════════
#  status
# ═══════════════════════════════════════════════════════════════════

class TestStatus:

    def test_sin_repositorio_imprime_error(self, tmp_path, capsys):
        os.chdir(tmp_path)
        status()
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_sin_archivos_muestra_mensaje_vacio(self, tmp_path, capsys):
        _init(tmp_path)
        status()
        out = capsys.readouterr().out
        assert "no hay" in out.lower()

    def test_muestra_archivos_rastreados(self, tmp_path, capsys):
        _init(tmp_path)
        (tmp_path / "util.py").write_text("pass")
        add_file("util.py")
        capsys.readouterr()
        status()
        out = capsys.readouterr().out
        assert "util.py" in out

    def test_muestra_multiples_archivos(self, tmp_path, capsys):
        _init(tmp_path)
        for name in ["a.py", "b.py"]:
            (tmp_path / name).write_text("code")
            add_file(name)
        capsys.readouterr()
        status()
        out = capsys.readouterr().out
        assert "a.py" in out
        assert "b.py" in out


# ═══════════════════════════════════════════════════════════════════
#  commit
# ═══════════════════════════════════════════════════════════════════

class TestCommit:

    def test_sin_repositorio_imprime_error(self, tmp_path, capsys):
        os.chdir(tmp_path)
        commit("msg")
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_sin_archivos_rastreados_imprime_aviso(self, tmp_path, capsys):
        _init(tmp_path)
        commit("sin archivos")
        out = capsys.readouterr().out
        assert "no hay archivos" in out.lower()

    def test_crea_directorio_del_commit(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "v1")
        assert os.path.exists(".sbac/commits/commit_001")

    def test_copia_archivo_al_commit(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "contenido")
        assert os.path.exists(".sbac/commits/commit_001/f.txt")

    def test_guarda_mensaje_en_metadata(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "x", "mensaje de prueba")
        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert meta["commit_001"]["message"] == "mensaje de prueba"

    def test_guarda_timestamp_en_metadata(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "x")
        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert "timestamp" in meta["commit_001"]

    def test_guarda_lista_de_archivos_en_metadata(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "src.py", "code")
        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert "src.py" in meta["commit_001"]["files"]

    def test_ids_incrementales(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("v1")
        add_file("f.txt")
        commit("c1")
        (tmp_path / "f.txt").write_text("v2")
        commit("c2")
        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert "commit_001" in meta
        assert "commit_002" in meta

    def test_contenido_del_archivo_guardado_correctamente(self, tmp_path):
        _init(tmp_path)
        _add_and_commit(tmp_path, "data.txt", "linea_exacta")
        stored = open(".sbac/commits/commit_001/data.txt").read()
        assert stored == "linea_exacta"

    def test_imprime_confirmacion(self, tmp_path, capsys):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "x", "hecho")
        out = capsys.readouterr().out
        assert "hecho" in out


# ═══════════════════════════════════════════════════════════════════
#  history
# ═══════════════════════════════════════════════════════════════════

class TestHistory:

    def test_sin_repositorio_imprime_error(self, tmp_path, capsys):
        os.chdir(tmp_path)
        history()
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_sin_commits_imprime_aviso(self, tmp_path, capsys):
        _init(tmp_path)
        history()
        out = capsys.readouterr().out
        assert "no hay commits" in out.lower()

    def test_muestra_mensaje_del_commit(self, tmp_path, capsys):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "x", "mi mensaje")
        capsys.readouterr()
        history()
        out = capsys.readouterr().out
        assert "mi mensaje" in out

    def test_muestra_id_del_commit(self, tmp_path, capsys):
        _init(tmp_path)
        _add_and_commit(tmp_path, "f.txt", "x", "msg")
        capsys.readouterr()
        history()
        out = capsys.readouterr().out
        assert "#1" in out

    def test_muestra_todos_los_commits(self, tmp_path, capsys):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("A")
        add_file("f.txt")
        commit("primero")
        (tmp_path / "f.txt").write_text("B")
        commit("segundo")
        capsys.readouterr()
        history()
        out = capsys.readouterr().out
        assert "primero" in out
        assert "segundo" in out

    def test_muestra_archivos_en_el_historial(self, tmp_path, capsys):
        _init(tmp_path)
        _add_and_commit(tmp_path, "modulo.py", "pass", "con archivo")
        capsys.readouterr()
        history()
        out = capsys.readouterr().out
        assert "modulo.py" in out


# ═══════════════════════════════════════════════════════════════════
#  checkout
# ═══════════════════════════════════════════════════════════════════

class TestCheckout:

    def test_sin_repositorio_imprime_error(self, tmp_path, capsys):
        os.chdir(tmp_path)
        checkout(1)
        out = capsys.readouterr().out
        assert "no inicializado" in out.lower()

    def test_commit_inexistente_imprime_error(self, tmp_path, capsys):
        _init(tmp_path)
        checkout(99)
        out = capsys.readouterr().out
        assert "no existe" in out.lower()

    def test_restaura_contenido_correcto(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("estado_v1")
        add_file("f.txt")
        commit("v1")
        (tmp_path / "f.txt").write_text("estado_v2")
        commit("v2")
        checkout(1)
        assert (tmp_path / "f.txt").read_text() == "estado_v1"

    def test_restaura_version_mas_reciente(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("v1")
        add_file("f.txt")
        commit("v1")
        (tmp_path / "f.txt").write_text("v2")
        commit("v2")
        checkout(2)
        assert (tmp_path / "f.txt").read_text() == "v2"

    def test_imprime_confirmacion_de_checkout(self, tmp_path, capsys):
        _init(tmp_path)
        (tmp_path / "f.txt").write_text("x")
        add_file("f.txt")
        commit("ok")
        capsys.readouterr()
        checkout(1)
        out = capsys.readouterr().out
        assert "checkout" in out.lower() or "completado" in out.lower()

    def test_restaura_multiples_archivos(self, tmp_path):
        _init(tmp_path)
        (tmp_path / "a.txt").write_text("A_v1")
        (tmp_path / "b.txt").write_text("B_v1")
        add_file("a.txt")
        add_file("b.txt")
        commit("inicio")
        (tmp_path / "a.txt").write_text("A_v2")
        (tmp_path / "b.txt").write_text("B_v2")
        commit("modificado")
        checkout(1)
        assert (tmp_path / "a.txt").read_text() == "A_v1"
        assert (tmp_path / "b.txt").read_text() == "B_v1"
