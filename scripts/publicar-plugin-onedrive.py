# -*- coding: utf-8 -*-
"""Copia el plugin, tal como esta commiteado, a la carpeta de OneDrive del equipo.

Existe porque la "Opcion A" de instalacion (sin GitHub, la que usa preventa)
lee el plugin de `Automatizaciones IA > Plugin_preventas_IA_automation`, y esa
carpeta no se actualiza sola: el 2026-10-26 seguia en la version del 7 de
septiembre, sin dos skills ni nada de octubre.

Copia solo lo trackeado en git de `.claude-plugin/` y `plugin-preventa/`, en
su version de HEAD: nunca `recursos-originales/`, `material-video/` ni nada sin
commitear (lo de otra sesion a medio hacer no se publica). Por eso se corre
DESPUES del commit.

Uso:
    python scripts/publicar-plugin-onedrive.py            (solo compara)
    python scripts/publicar-plugin-onedrive.py --copiar   (copia y verifica)

No borra nada de la carpeta compartida: lo que sobre alli solo se informa.
Despues de copiar, esperar a que OneDrive suba (estado 2 en
System.StorageProviderState); si se traba, abrir y cerrar el archivo, nunca
reiniciar OneDrive.
"""
import hashlib, os, pathlib, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DESTINO = (pathlib.Path(os.environ["USERPROFILE"]) / "OneDrive - GRUPO VISION - DYNAMIC"
           / "Archivos de Info Costa Rica - Automatizaciones IA" / "Plugin_preventas_IA_automation")
CARPETAS = (".claude-plugin", "plugin-preventa")


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, check=True).stdout


def main():
    copiar = "--copiar" in sys.argv
    if not DESTINO.is_dir():
        print(f"No encuentro la carpeta compartida: {DESTINO}")
        return 1
    sucio = git("status", "--porcelain", "--", *CARPETAS).decode("utf-8").rstrip()
    if sucio:
        print("Aviso: hay cambios sin commitear que NO se van a publicar:\n" + sucio + "\n")

    rutas = [r for r in git("ls-files", "-z", "--", *CARPETAS).decode("utf-8").split("\0") if r]
    nuevo = {r: git("show", f"HEAD:{r}") for r in rutas}
    assert not any("recursos-originales" in r for r in nuevo)
    h = lambda b: hashlib.sha256(b).hexdigest()
    viejo = {p.relative_to(DESTINO).as_posix(): p for p in DESTINO.rglob("*") if p.is_file()}

    agregar = sorted(set(nuevo) - set(viejo))
    cambiar = sorted(r for r in set(nuevo) & set(viejo) if h(nuevo[r]) != h(viejo[r].read_bytes()))
    print(f"HEAD {git('rev-parse', '--short', 'HEAD').decode().strip()}: {len(nuevo)} archivos")
    print(f"nuevos: {len(agregar)}  cambian: {len(cambiar)}  iguales: {len(nuevo) - len(agregar) - len(cambiar)}")
    for r in agregar:
        print("  + " + r)
    for r in cambiar:
        print("  ~ " + r)
    for r in sorted(set(viejo) - set(nuevo)):
        print("  sobra en OneDrive (no se toca): " + r)
    if not copiar:
        print("\nSolo comparé. Para copiar: --copiar")
        return 0
    for r in agregar + cambiar:
        d = DESTINO / r
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(nuevo[r])
    malos = [r for r in nuevo if h(nuevo[r]) != h((DESTINO / r).read_bytes())]
    print(f"\ncopiados: {len(agregar) + len(cambiar)}; distintos después de copiar: {malos or 'ninguno'}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
