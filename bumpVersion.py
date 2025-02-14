import re

def incrementar_version(version_str, parte="patch", pre_release=None, incr_suffix=False, solo_pre_release=False):
    """
    Incrementa la versión, soportando incremento en la parte principal y/o en el sufijo de pre-release.

    Parámetros:
      - version_str: Versión actual (ej. "v1.0.0", "v1.0.0-alpha", "v1.0.0-alpha.1").
      - parte: Parte a incrementar: "major", "minor" o "patch". Se utiliza solo si solo_pre_release es False.
      - pre_release: Etiqueta de pre-release deseada (ej. "alpha", "beta"). Si se deja en None no se agrega sufijo.
      - incr_suffix: Si es True y estamos en modo solo_pre_release, incrementa numéricamente el sufijo.
      - solo_pre_release: Si es True, no se modifica la parte principal y se actualiza (o incrementa) solo el sufijo pre-release.

    Retorna la nueva versión con el prefijo "v".
    """
    # Quitar el prefijo 'v' si existe
    if version_str.startswith("v"):
        version_str = version_str[1:]
    
    # Separa la parte principal de la posible parte pre-release
    main_version, sep, current_pre = version_str.partition("-")
    
    if solo_pre_release:
        # No se modifica la parte principal
        nueva_main = main_version
    else:
        # Se incrementa la parte principal según lo indicado
        try:
            major, minor, patch = map(int, main_version.split('.'))
        except ValueError:
            raise ValueError("El formato de la versión debe ser 'major.minor.patch' (ej. 1.0.0)")
    
        if parte == "major":
            major += 1
            minor = 0
            patch = 0
        elif parte == "minor":
            minor += 1
            patch = 0
        elif parte == "patch":
            patch += 1
        else:
            raise ValueError("La parte a incrementar debe ser 'major', 'minor' o 'patch'")
    
        nueva_main = f"{major}.{minor}.{patch}"
    
    nueva_pre = ""
    if pre_release:
        if solo_pre_release:
            # En modo solo pre_release, se intenta incrementar el sufijo numérico si ya existe
            if current_pre and current_pre.startswith(pre_release):
                if incr_suffix:
                    # Se busca si existe un número después del sufijo, por ejemplo, "alpha.1"
                    m = re.match(rf'({pre_release})(\.(\d+))?$', current_pre)
                    if m:
                        base = m.group(1)
                        num = m.group(3)
                        if num is None:
                            nueva_pre = f"{base}.1"
                        else:
                            nueva_pre = f"{base}.{int(num) + 1}"
                    else:
                        # Si no coincide con el patrón, se asigna el sufijo con .1
                        nueva_pre = f"{pre_release}.1"
                else:
                    nueva_pre = pre_release
            else:
                # Si no hay sufijo actual o no coincide, se asigna el pre_release dado
                nueva_pre = pre_release
        else:
            # En modo normal, si se especifica pre_release, se adjunta tal cual (sin mirar el anterior)
            nueva_pre = pre_release
    
    # Construir la nueva versión
    if nueva_pre:
        nueva_version = f"{nueva_main}-{nueva_pre}"
    else:
        nueva_version = nueva_main
    
    return f"v{nueva_version}"

def actualizar_archivo_version(ruta_archivo, nueva_version):
    """
    Actualiza el archivo que contiene la variable __version__.
    
    Se espera que el archivo tenga una línea con el formato:
      __version__ = "v1.0.0"
    """
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    
    nuevo_contenido = re.sub(
        r'(__version__\s*=\s*")[^"]*(")',
        rf'\1{nueva_version}\2',
        contenido
    )
    
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(nuevo_contenido)

if __name__ == "__main__":
    ruta_version = "vne/_version.py"
    
    # Leer la versión actual
    with open(ruta_version, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', contenido)
    if not match:
        raise ValueError("No se encontró la versión en el archivo.")
    version_actual = match.group(1)
    
    """
    Configuración:
      - Si solo deseas actualizar la parte principal, deja solo_pre_release en False.
        Ejemplo: de v1.0.0 a v1.0.1 (o v2.0.0, etc.)
      
      - Si deseas iniciar o actualizar un ciclo de pre-release sin cambiar la parte principal,
        configura solo_pre_release = True.
        Además, si quieres que el sufijo incremente (por ejemplo, de "alpha.1" a "alpha.2"),
        coloca incr_suffix = True.
    
    Ejemplos:
      1. Incrementar la parte principal (patch) y establecer un sufijo pre-release:
           parte = "patch"
           pre_release = "alpha"
           solo_pre_release = False
           => Si la versión es v1.0.0, se pasará a v1.0.1-alpha
      
      2. Incrementar solo el sufijo de pre-release:
           parte = "patch"  (no se usa en este modo)
           pre_release = "alpha"
           solo_pre_release = True
           incr_suffix = True
           => Si la versión es v1.0.0-alpha.1, se pasará a v1.0.0-alpha.2
    """
    
    # Configuración de ejemplo:
    parte = "patch"              # O "minor", "major" según se requiera (se usa solo si solo_pre_release es False)
    pre_release = "alpha"          # Cambiar o dejar None si no se requiere sufijo
    solo_pre_release = True       # Cambia a True para actualizar solo el sufijo
    incr_suffix = True            # Útil solo en modo solo_pre_release para incrementar numéricamente el sufijo
    
    # Para probar el incremento del sufijo sin cambiar la parte principal, descomenta:
    # solo_pre_release = True
    # incr_suffix = True
    
    version_nueva = incrementar_version(version_actual, parte, pre_release, incr_suffix, solo_pre_release)
    actualizar_archivo_version(ruta_version, version_nueva)
    
    print(f"Versión actualizada de {version_actual} a {version_nueva}")
