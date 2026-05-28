"""
Pruebas de integración — validan flujos completos que combinan
múltiples componentes del sistema SBAC trabajando en conjunto.
"""

import os
import json
import pytest
from app.repository import (
    init_repository,
    add_file,
    commit,
    history,
    checkout,
    create_baseline,
    list_baselines,
    restore_baseline,
)
from app.utils import diff_commits, diff_files


# ─── helpers ────────────────────────────────────────────────────────────────

def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def _read(tmp_path, name):
    return (tmp_path / name).read_text(encoding="utf-8")


# ─── Flujo básico: init → add → commit → history ────────────────────────────

class TestFlujoBasico:

    def test_ciclo_completo_init_add_commit_history(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "main.py", "print('v1')")
        add_file("main.py")
        commit("version inicial")
        history()

        out = capsys.readouterr().out
        assert "version inicial" in out
        assert os.path.exists(".sbac/commits/commit_001/main.py")

    def test_multiples_commits_historia_ordenada(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "f.txt", "v1")
        add_file("f.txt")
        commit("primera")
        _write(tmp_path, "f.txt", "v2")
        commit("segunda")
        _write(tmp_path, "f.txt", "v3")
        commit("tercera")
        history()

        out = capsys.readouterr().out
        assert "primera" in out
        assert "segunda" in out
        assert "tercera" in out
        assert os.path.exists(".sbac/commits/commit_003")

    def test_commit_preserva_contenido_exacto(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "src.py", "def foo(): return 42\n")
        add_file("src.py")
        commit("snap")

        stored = open(".sbac/commits/commit_001/src.py").read()
        assert stored == "def foo(): return 42\n"


# ─── Flujo checkout ──────────────────────────────────────────────────────────

class TestFlujoCheckout:

    def test_checkout_restaura_version_anterior(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "app.txt", "version_1")
        add_file("app.txt")
        commit("v1")
        _write(tmp_path, "app.txt", "version_2")
        commit("v2")

        checkout(1)
        assert _read(tmp_path, "app.txt") == "version_1"

    def test_checkout_y_nuevo_commit_mantiene_historial(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "f.txt", "A")
        add_file("f.txt")
        commit("A")
        _write(tmp_path, "f.txt", "B")
        commit("B")

        checkout(1)
        assert _read(tmp_path, "f.txt") == "A"

        _write(tmp_path, "f.txt", "C")
        commit("C")

        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert "commit_003" in meta

    def test_checkout_multiple_archivos(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "a.txt", "A_v1")
        _write(tmp_path, "b.txt", "B_v1")
        add_file("a.txt")
        add_file("b.txt")
        commit("inicio")
        _write(tmp_path, "a.txt", "A_v2")
        _write(tmp_path, "b.txt", "B_v2")
        commit("cambios")

        checkout(1)
        assert _read(tmp_path, "a.txt") == "A_v1"
        assert _read(tmp_path, "b.txt") == "B_v1"


# ─── Flujo baseline ──────────────────────────────────────────────────────────

class TestFlujoBaseline:

    def test_baseline_preserva_estado_antes_de_cambios(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "config.txt", "estado_estable")
        add_file("config.txt")
        create_baseline("release_1.0")
        _write(tmp_path, "config.txt", "estado_experimental")

        restore_baseline("release_1.0")
        assert _read(tmp_path, "config.txt") == "estado_estable"

    def test_multiple_baselines_restauracion_independiente(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "mod.txt", "v_alpha")
        add_file("mod.txt")
        create_baseline("alpha")
        _write(tmp_path, "mod.txt", "v_beta")
        create_baseline("beta")

        restore_baseline("alpha")
        assert _read(tmp_path, "mod.txt") == "v_alpha"

        restore_baseline("beta")
        assert _read(tmp_path, "mod.txt") == "v_beta"

    def test_baseline_con_commit_previo(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "src.txt", "original")
        add_file("src.txt")
        commit("v1")
        create_baseline("estable")
        _write(tmp_path, "src.txt", "experimental")
        commit("v2")

        restore_baseline("estable")
        assert _read(tmp_path, "src.txt") == "original"

    def test_list_baselines_muestra_todas_despues_de_crear(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "f.txt", "x")
        add_file("f.txt")
        create_baseline("b1")
        create_baseline("b2")
        capsys.readouterr()
        list_baselines()
        out = capsys.readouterr().out
        assert "b1" in out
        assert "b2" in out


# ─── Flujo diff ──────────────────────────────────────────────────────────────

class TestFlujoDiff:

    def test_diff_detecta_cambio_entre_commits(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "prog.py", "x = 1\n")
        add_file("prog.py")
        commit("v1")
        _write(tmp_path, "prog.py", "x = 2\n")
        commit("v2")

        results = diff_commits(1, 2)
        assert any(r["status"] == "modificado" for r in results)

    def test_diff_files_entre_versiones_de_archivo(self, tmp_path):
        os.chdir(tmp_path)
        p1 = tmp_path / "v1.txt"
        p2 = tmp_path / "v2.txt"
        p1.write_text("linea_a\n")
        p2.write_text("linea_b\n")

        result = diff_files(str(p1), str(p2))
        contenido = "".join(result)
        assert "linea_a" in contenido
        assert "linea_b" in contenido

    def test_diff_commits_sin_cambios(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "igual.txt", "misma_linea\n")
        add_file("igual.txt")
        commit("c1")
        commit("c2")

        results = diff_commits(1, 2)
        assert all(r["status"] == "sin_cambios" for r in results)


# ─── Flujo completo integrado ────────────────────────────────────────────────

class TestFlujoCompleto:

    def test_ciclo_desarrollo_completo(self, tmp_path):
        """
        Simula un ciclo de desarrollo:
        init → add → commit v1 → baseline → modificar → commit v2
        → checkout v1 → diff → restore_baseline
        """
        os.chdir(tmp_path)
        init_repository()

        # Desarrollo inicial
        _write(tmp_path, "app.py", "def main(): pass\n")
        add_file("app.py")
        commit("funcionalidad base")
        create_baseline("v1.0_estable")

        # Cambio experimental
        _write(tmp_path, "app.py", "def main(): raise NotImplementedError\n")
        commit("experimento")

        # El experimento falla — volver a baseline estable
        restore_baseline("v1.0_estable")
        assert _read(tmp_path, "app.py") == "def main(): pass\n"

        # Verificar que los commits anteriores siguen existiendo
        with open(".sbac/metadata.json") as fh:
            meta = json.load(fh)
        assert "commit_001" in meta
        assert "commit_002" in meta

    def test_add_commit_checkout_diff(self, tmp_path):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "data.txt", "valor=10\n")
        add_file("data.txt")
        commit("inicio")
        _write(tmp_path, "data.txt", "valor=20\n")
        commit("cambio")

        # Verificar con diff antes de hacer checkout
        results = diff_commits(1, 2)
        modificados = [r for r in results if r["status"] == "modificado"]
        assert len(modificados) == 1

        # Hacer checkout y verificar
        checkout(1)
        assert _read(tmp_path, "data.txt") == "valor=10\n"

    def test_repositorio_ya_inicializado_no_sobreescribe(self, tmp_path, capsys):
        os.chdir(tmp_path)
        init_repository()
        _write(tmp_path, "f.txt", "dato")
        add_file("f.txt")
        commit("v1")
        capsys.readouterr()

        # Intentar inicializar de nuevo
        init_repository()
        out = capsys.readouterr().out
        assert "ya inicializado" in out.lower()

        # Los datos del commit deben seguir intactos
        assert os.path.exists(".sbac/commits/commit_001/f.txt")
