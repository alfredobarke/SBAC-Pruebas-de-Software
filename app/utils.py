import os
import difflib


def diff_commits(commit_id1, commit_id2):
    """Compara dos commits y muestra las diferencias línea a línea."""

    key1 = f"commit_{int(commit_id1):03d}"
    key2 = f"commit_{int(commit_id2):03d}"
    dir1 = f".sbac/commits/{key1}"
    dir2 = f".sbac/commits/{key2}"

    if not os.path.exists(dir1):
        print(f"El commit #{commit_id1} no existe.")
        return []

    if not os.path.exists(dir2):
        print(f"El commit #{commit_id2} no existe.")
        return []

    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))
    all_files = files1 | files2

    results = []
    print(f"=== Diferencias entre commit #{commit_id1} y #{commit_id2} ===")

    for filename in sorted(all_files):
        path1 = os.path.join(dir1, filename)
        path2 = os.path.join(dir2, filename)

        if filename not in files1:
            entry = {"file": filename, "status": "nuevo", "diff": []}
            print(f"\n[NUEVO] {filename}")
        elif filename not in files2:
            entry = {"file": filename, "status": "eliminado", "diff": []}
            print(f"\n[ELIMINADO] {filename}")
        else:
            with open(path1, "r", encoding="utf-8", errors="replace") as f:
                lines1 = f.readlines()
            with open(path2, "r", encoding="utf-8", errors="replace") as f:
                lines2 = f.readlines()

            diff = list(
                difflib.unified_diff(
                    lines1,
                    lines2,
                    fromfile=f"{filename} (commit {commit_id1})",
                    tofile=f"{filename} (commit {commit_id2})",
                )
            )

            if diff:
                entry = {"file": filename, "status": "modificado", "diff": diff}
                print(f"\n[MODIFICADO] {filename}")
                for line in diff:
                    print(line, end="")
            else:
                entry = {"file": filename, "status": "sin_cambios", "diff": []}
                print(f"\n[SIN CAMBIOS] {filename}")

        results.append(entry)

    return results


def diff_files(path1, path2):
    """Compara dos archivos y retorna las líneas de diferencia en formato unified diff."""

    if not os.path.exists(path1):
        print(f"Archivo '{path1}' no encontrado.")
        return []

    if not os.path.exists(path2):
        print(f"Archivo '{path2}' no encontrado.")
        return []

    with open(path1, "r", encoding="utf-8", errors="replace") as f:
        lines1 = f.readlines()
    with open(path2, "r", encoding="utf-8", errors="replace") as f:
        lines2 = f.readlines()

    return list(difflib.unified_diff(lines1, lines2, fromfile=path1, tofile=path2))
