import os
import pytest
from app.repository import init_repository, add_file, commit
from app.utils import diff_commits, diff_files


# ─── helpers ────────────────────────────────────────────────────────────────

def _setup_repo(tmp_path):
    os.chdir(tmp_path)
    init_repository()


def _make_commit(tmp_path, filename, content, tracked=True):
    p = tmp_path / filename
    p.write_text(content)
    if tracked:
        add_file(filename)
    commit(f"commit de {filename}")


# ─── diff_commits ────────────────────────────────────────────────────────────

class TestDiffCommits:

    def test_archivos_identicos_sin_diff(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        (tmp_path / "f.txt").write_text("mismo contenido\n")
        add_file("f.txt")
        commit("v1")
        commit("v2")
        results = diff_commits(1, 2)
        sin_cambios = [r for r in results if r["status"] == "sin_cambios"]
        assert len(sin_cambios) == 1

    def test_detecta_archivo_modificado(self, tmp_path):
        _setup_repo(tmp_path)
        (tmp_path / "code.txt").write_text("linea original\n")
        add_file("code.txt")
        commit("v1")
        (tmp_path / "code.txt").write_text("linea modificada\n")
        commit("v2")
        results = diff_commits(1, 2)
        modificados = [r for r in results if r["status"] == "modificado"]
        assert len(modificados) == 1
        assert modificados[0]["file"] == "code.txt"

    def test_diff_contiene_lineas_agregadas(self, tmp_path):
        _setup_repo(tmp_path)
        (tmp_path / "prog.txt").write_text("linea_a\n")
        add_file("prog.txt")
        commit("v1")
        (tmp_path / "prog.txt").write_text("linea_a\nlinea_b\n")
        commit("v2")
        results = diff_commits(1, 2)
        diff_lines = results[0]["diff"]
        agregadas = [l for l in diff_lines if l.startswith("+") and "linea_b" in l]
        assert len(agregadas) > 0

    def test_diff_contiene_lineas_eliminadas(self, tmp_path):
        _setup_repo(tmp_path)
        (tmp_path / "doc.txt").write_text("linea_a\nlinea_b\n")
        add_file("doc.txt")
        commit("v1")
        (tmp_path / "doc.txt").write_text("linea_a\n")
        commit("v2")
        results = diff_commits(1, 2)
        diff_lines = results[0]["diff"]
        eliminadas = [l for l in diff_lines if l.startswith("-") and "linea_b" in l]
        assert len(eliminadas) > 0

    def test_commit_inexistente_primer_argumento(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        (tmp_path / "x.txt").write_text("data\n")
        add_file("x.txt")
        commit("v1")
        diff_commits(99, 1)
        out = capsys.readouterr().out
        assert "no existe" in out.lower()

    def test_commit_inexistente_segundo_argumento(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        (tmp_path / "x.txt").write_text("data\n")
        add_file("x.txt")
        commit("v1")
        diff_commits(1, 99)
        out = capsys.readouterr().out
        assert "no existe" in out.lower()

    def test_retorna_lista_vacia_si_commit_invalido(self, tmp_path):
        _setup_repo(tmp_path)
        result = diff_commits(5, 6)
        assert result == []

    def test_multiples_archivos_en_diff(self, tmp_path):
        _setup_repo(tmp_path)
        (tmp_path / "a.txt").write_text("A\n")
        (tmp_path / "b.txt").write_text("B\n")
        add_file("a.txt")
        add_file("b.txt")
        commit("v1")
        (tmp_path / "a.txt").write_text("A_mod\n")
        commit("v2")
        results = diff_commits(1, 2)
        nombres = {r["file"] for r in results}
        assert "a.txt" in nombres
        assert "b.txt" in nombres

    def test_diff_mismo_commit(self, tmp_path):
        _setup_repo(tmp_path)
        (tmp_path / "f.txt").write_text("igual\n")
        add_file("f.txt")
        commit("v1")
        results = diff_commits(1, 1)
        assert all(r["status"] == "sin_cambios" for r in results)

    def test_salida_impresa_en_consola(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        (tmp_path / "f.txt").write_text("v1\n")
        add_file("f.txt")
        commit("v1")
        (tmp_path / "f.txt").write_text("v2\n")
        commit("v2")
        diff_commits(1, 2)
        out = capsys.readouterr().out
        assert "diferencias" in out.lower() or "modificado" in out.lower()


# ─── diff_files ──────────────────────────────────────────────────────────────

class TestDiffFiles:

    def test_archivos_identicos_retorna_lista_vacia(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "f1.txt"
        p2 = tmp_path / "f2.txt"
        p1.write_text("igual\n")
        p2.write_text("igual\n")
        result = diff_files(str(p1), str(p2))
        assert result == []

    def test_detecta_diferencia_entre_archivos(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "v1.txt"
        p2 = tmp_path / "v2.txt"
        p1.write_text("linea_a\n")
        p2.write_text("linea_b\n")
        result = diff_files(str(p1), str(p2))
        assert len(result) > 0

    def test_formato_unified_diff(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "a.txt"
        p2 = tmp_path / "b.txt"
        p1.write_text("original\n")
        p2.write_text("modificado\n")
        result = diff_files(str(p1), str(p2))
        # unified diff comienza con --- y +++
        assert any(l.startswith("---") for l in result)
        assert any(l.startswith("+++") for l in result)

    def test_archivo_no_encontrado_primero(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        p2 = tmp_path / "real.txt"
        p2.write_text("existe\n")
        result = diff_files("no_existe.txt", str(p2))
        out = capsys.readouterr().out
        assert "no encontrado" in out.lower()
        assert result == []

    def test_archivo_no_encontrado_segundo(self, tmp_path, capsys):
        _setup_repo(tmp_path)
        p1 = tmp_path / "real.txt"
        p1.write_text("existe\n")
        result = diff_files(str(p1), "fantasma.txt")
        out = capsys.readouterr().out
        assert "no encontrado" in out.lower()
        assert result == []

    def test_lineas_agregadas_marcadas_con_plus(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "base.txt"
        p2 = tmp_path / "nueva.txt"
        p1.write_text("linea1\n")
        p2.write_text("linea1\nlinea_nueva\n")
        result = diff_files(str(p1), str(p2))
        plus_lines = [l for l in result if l.startswith("+") and "linea_nueva" in l]
        assert len(plus_lines) > 0

    def test_lineas_eliminadas_marcadas_con_menos(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "completo.txt"
        p2 = tmp_path / "reducido.txt"
        p1.write_text("linea1\nlinea2\n")
        p2.write_text("linea1\n")
        result = diff_files(str(p1), str(p2))
        minus_lines = [l for l in result if l.startswith("-") and "linea2" in l]
        assert len(minus_lines) > 0

    def test_retorna_lista(self, tmp_path):
        _setup_repo(tmp_path)
        p1 = tmp_path / "x.txt"
        p2 = tmp_path / "y.txt"
        p1.write_text("a\n")
        p2.write_text("b\n")
        result = diff_files(str(p1), str(p2))
        assert isinstance(result, list)
