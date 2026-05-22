import sys
from app.repository import init_repository
from app.repository import add_file
from app.repository import status

command = sys.argv[1]

if command == "init":
    init_repository()

elif command == "add":
    filename = sys.argv[2]
    add_file(filename)

elif command == "status":
    status()

else:
    print("Comando no reconocido")