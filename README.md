# MANUAL DE USUARIO

## SBAC — Sistema Básico de Control de Versiones

SBAC es una herramienta de línea de comandos para rastrear versiones de archivos, crear commits, comparar cambios y gestionar líneas base (baselines). Se ejecuta sobre Docker, por lo que no requiere instalar dependencias en el sistema operativo local.

---

## Requisitos previos

- [Docker](https://www.docker.com/) instalado y en ejecución.
- **Mac/Linux:** El script `sbac` debe tener permisos de ejecución:

```bash
chmod +x sbac
```

- **Windows:** Usar el script `sbac.bat` incluido en el repositorio. No requiere configuración adicional.

---


## Cómo ejecutar el programa

El script `sbac` se encarga de construir la imagen Docker automáticamente y montar el directorio de trabajo actual, por lo que todos los comandos se ejecutan desde la raíz del proyecto.

### Sintaxis general

**Mac/Linux:**
```bash
./sbac <comando> [argumentos]
```

**Windows:**
```powershell
.\sbac.bat <comando> [argumentos]
```

### Ejemplo rápido

```bash
# 1. Inicializar repositorio
./sbac init

# 2. Agregar archivos al seguimiento
./sbac add archivo.txt

# 3. Crear un commit
./sbac commit "versión inicial"

# 4. Ver historial
./sbac history
```

---

## Comandos disponibles

| Comando | Argumentos | Descripción |
|---|---|---|
| `init` | — | Inicializa el repositorio SBAC en el directorio actual (crea `.sbac/`). |
| `add` | `<archivo>` | Agrega un archivo al seguimiento del repositorio. |
| `status` | — | Muestra todos los archivos actualmente rastreados. |
| `commit` | `"mensaje"` | Guarda una instantánea de todos los archivos rastreados con un mensaje descriptivo. |
| `history` | — | Muestra el historial completo de commits (más reciente primero). |
| `checkout` | `<número_commit>` | Restaura los archivos al estado de un commit específico. |
| `baseline` | `<nombre>` | Crea una línea base con nombre a partir del estado actual de los archivos rastreados. |
| `list-baselines` | — | Lista todas las líneas base registradas. |
| `diff` | `<v1> <v2>` | Muestra las diferencias línea a línea entre dos commits. |

### Descripción detallada

#### `init`
Crea la carpeta oculta `.sbac/` con la estructura interna del repositorio. Debe ejecutarse una sola vez por proyecto.

```bash
./sbac init
```

#### `add <archivo>`
Registra un archivo para que sea incluido en los siguientes commits. El archivo debe existir en el directorio de trabajo.

```bash
./sbac add config.yaml
./sbac add src/modelo.py
```

#### `status`
Lista los archivos que están actualmente bajo seguimiento.

```bash
./sbac status
```

#### `commit "mensaje"`
Crea una nueva versión guardando copias de todos los archivos rastreados. El mensaje debe ir entre comillas si contiene espacios.

```bash
./sbac commit "agrego validación de entrada"
```

#### `history`
Imprime todos los commits registrados con su número, fecha/hora, mensaje y archivos incluidos.

```bash
./sbac history
```

#### `checkout <número_commit>`
Recupera los archivos del estado guardado en el commit indicado, sobreescribiendo los archivos actuales.

```bash
./sbac checkout 3
```


#### `baseline <nombre>`
Crea una línea base nombrada (análogo a un "tag" o "release"). Es útil para marcar versiones estables.

```bash
./sbac baseline v1.0-estable
```

#### `list-baselines`
Muestra todas las líneas base existentes junto con su fecha de creación y archivos incluidos.

```bash
./sbac list-baselines
```

#### `diff <v1> <v2>`
Compara el contenido de dos commits e imprime las diferencias en formato unified diff. Los archivos nuevos, eliminados y modificados se identifican con etiquetas `[NUEVO]`, `[ELIMINADO]` y `[MODIFICADO]`.

```bash
./sbac diff 1 3
```

---

## Cómo ejecutar los tests

Los tests se ejecutan con **pytest** dentro del contenedor Docker:

```bash
docker build -t sbac-cli .
docker run --rm sbac-cli
```

La imagen tiene como `CMD` predeterminado `pytest --tb=short -v`, por lo que al correr el contenedor sin argumentos se ejecuta la suite completa de tests.


### Flags útiles de pytest

| Flag | Efecto |
|---|---|
| `-v` | Salida detallada (nombre de cada test). |
| `--tb=short` | Muestra trazas de error cortas. |
| `-x` | Detiene la ejecución al primer fallo. |
| `-k "nombre"` | Ejecuta solo los tests que coincidan con el nombre. |
| `--tb=long` | Muestra trazas de error completas. |

---

## Estructura interna generada por SBAC

Al inicializar y usar SBAC, se crea la siguiente estructura dentro de `.sbac/`:

```
.sbac/
├── tracked_files.json      # Lista de archivos bajo seguimiento
├── metadata.json           # Metadatos de todos los commits
├── baselines_meta.json     # Metadatos de las líneas base
├── commits/
│   ├── commit_001/         # Copia de archivos del commit #1
│   ├── commit_002/
│   └── ...
└── baselines/
    ├── v1.0-estable/       # Copia de archivos de la línea base
    └── ...
```

---

## Notas

- El directorio de trabajo del host se monta dentro del contenedor en `/app`, por lo que el repositorio `.sbac/` se crea y persiste en tu máquina local.
- Si un archivo rastreado no existe en disco al momento del commit, se omite con una advertencia pero el commit continúa.
- Los números de commit son incrementales y no se reutilizan.