import sys
from app.repository import init_repository, add_file, status, commit, history, checkout

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

else:
    print("Comandos disponibles: init, add, status, commit, history, checkout")
