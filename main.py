import sys
from app.repository import (
    init_repository, add_file, status, commit, 
    history, checkout, create_baseline, list_baselines
)
from app.utils import diff_commits

command = sys.argv[1] if len(sys.argv) > 1 else None

if command == "init":
    init_repository()

elif command == "add":
    if len(sys.argv) < 3:
        print("Uso: sbac add <archivo>")
    else:
        add_file(sys.argv[2])

elif command == "status":
    status()

elif command == "commit":
    if len(sys.argv) < 3:
        print("Uso: sbac commit \"mensaje\"")
    else:
        commit(sys.argv[2])

elif command == "history":
    history()

elif command == "checkout":
    if len(sys.argv) < 3:
        print("Uso: sbac checkout <numero_commit>")
    else:
        checkout(sys.argv[2])

elif command == "baseline":
    if len(sys.argv) < 3:
        print("Uso: sbac baseline <nombre>")
    else:
        create_baseline(sys.argv[2])

elif command == "list-baselines":
    list_baselines()

elif command == "diff":
    if len(sys.argv) < 4:
        print("Uso: sbac diff <v1> <v2>")
    else:
        diff_commits(sys.argv[2], sys.argv[3])

else:
    print("Comandos disponibles: init, add, status, commit, history, checkout, baseline, list-baselines, diff")
