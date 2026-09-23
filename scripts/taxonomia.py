# -*- coding: utf-8 -*-
"""
Taxonomia de dos niveles (Categoria + Subcategoria) para el catalogo.
Se importa desde construir_propuesta.py. No escribe nada por si solo.
"""
import re, unicodedata


def norm(s):
    if s is None:
        return " "
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " " + re.sub(r"\s+", " ", s.lower()) + " "


# --------------------------------------------------------------------------
# Catalogo de categorias: (categoria, [subcategorias]) en orden de lectura
# --------------------------------------------------------------------------
TAXONOMIA = [
    ("Camara", ["IP / de red", "Analogica", "Termica", "Panoramica / fisheye",
                "PTZ", "LPR / placas", "A prueba de explosion", "Otra especializada"]),
    ("Grabacion y video", ["NVR", "DVR / hibrido", "Servidor / appliance",
                           "Codificador / decodificador"]),
    ("Almacenamiento", ["Disco duro", "Tarjeta de memoria"]),
    ("Monitor y visualizacion", ["Monitor", "Video wall", "Monitor publico (PVM)",
                                 "Senalizacion digital"]),
    ("Optica", ["Lente"]),
    ("Accesorio de instalacion", ["Montaje", "Caja / housing", "Cubierta / carcasa",
                                  "Adaptador / conversor", "Otros accesorios"]),
    ("Control de acceso", ["Lector / terminal", "Controladora", "Cerradura / electroiman",
                           "Boton de salida", "Credencial / tarjeta", "Intercomunicador",
                           "Torniquete"]),
    ("Deteccion de incendio", ["Panel", "Detector", "Notificacion", "Accesorio"]),
    ("Alarma e intrusion", ["Panel de alarma", "Detector de movimiento",
                            "Contacto magnetico", "Boton de panico", "Sirena",
                            "Comunicador", "Sensor ambiental", "Accesorio de alarma"]),
    ("Audio", ["Microfono", "Altavoz", "Sistema de audio IP"]),
    ("Red y conectividad", ["Switch", "Switch PoE", "Firewall / router",
                            "Fibra / transceiver", "Extensor", "Antena",
                            "Accesorio de red"]),
    ("Energia", ["Fuente de poder", "UPS", "Bateria", "Inyector PoE",
                 "Proteccion electrica", "Sistema solar"]),
    ("Materiales de instalacion", ["Canalizacion y tuberia", "Cableado",
                                   "Material electrico", "Ferreteria / postes"]),
    ("Software y licencias", ["Licencia VMS", "Suscripcion en la nube",
                              "Integracion / plugin"]),
    ("Equipo de computo", ["Computadora / workstation", "Periferico"]),
    ("Servicios", ["Instalacion", "Capacitacion", "Flete y logistica"]),
    ("Sin clasificar", [""]),
]
CATEGORIAS = [c for c, _ in TAXONOMIA]

# --------------------------------------------------------------------------
# 1) Categorias del proveedor confiables -> (categoria, subcategoria)
# --------------------------------------------------------------------------
CONFIABLES = {
    "camera - network": ("Camara", "IP / de red"),
    "network - camera": ("Camara", "IP / de red"),
    "ai ip 4mp -5mp- 6mp & 8mp face recognition & ai": ("Camara", "IP / de red"),
    "facial recognition ai": ("Camara", "IP / de red"),
    "lc2 - lc3 ip 5 - 6 - 8mp lc versions": ("Camara", "IP / de red"),
    'vision lc "low cost"': ("Camara", "IP / de red"),
    "ip cameras kits": ("Camara", "IP / de red"),
    "camera - analog hd": ("Camara", "Analogica"),
    "2mp analog": ("Camara", "Analogica"),
    "5mp & 8 mp analog": ("Camara", "Analogica"),
    "cameras hd tvi-ahd-cvi-analog": ("Camara", "Analogica"),
    "cameras tvi/ahd/cvi/analog": ("Camara", "Analogica"),
    "wisenet road ai": ("Camara", "LPR / placas"),
    "parking/guidance camera": ("Camara", "LPR / placas"),
    "thermal - fisheye 360 - 180 & ptz's": ("Camara", "Termica"),
    "explosion proof positioning camera": ("Camara", "A prueba de explosion"),
    "recording - network": ("Grabacion y video", "NVR"),
    "nvr's ndaa": ("Grabacion y video", "NVR"),
    "nvr's vision": ("Grabacion y video", "NVR"),
    "nvr's secure": ("Grabacion y video", "NVR"),
    "recording - hybrid": ("Grabacion y video", "DVR / hibrido"),
    "hd dvr's (tvi-ahd-cvi)": ("Grabacion y video", "DVR / hibrido"),
    "dvr's vision": ("Grabacion y video", "DVR / hibrido"),
    "blaze - appliance": ("Grabacion y video", "Servidor / appliance"),
    "wave - appliance": ("Grabacion y video", "Servidor / appliance"),
    "wave- appliance": ("Grabacion y video", "Servidor / appliance"),
    "ai box": ("Grabacion y video", "Servidor / appliance"),
    "network - encoder": ("Grabacion y video", "Codificador / decodificador"),
    "decoder - network": ("Grabacion y video", "Codificador / decodificador"),
    "decoder monitor": ("Grabacion y video", "Codificador / decodificador"),
    "wisenet wave software": ("Software y licencias", "Licencia VMS"),
    "blaze software": ("Software y licencias", "Licencia VMS"),
    "wave - client": ("Software y licencias", "Licencia VMS"),
    "blaze - client": ("Software y licencias", "Licencia VMS"),
    "open platform application license": ("Software y licencias", "Licencia VMS"),
    "epic webrtc media server license": ("Software y licencias", "Licencia VMS"),
    "bridge hardware - one-time purchase": ("Software y licencias", "Licencia VMS"),
    "wave integration": ("Software y licencias", "Integracion / plugin"),
    "lumeo": ("Software y licencias", "Integracion / plugin"),
    "30-day": ("Software y licencias", "Suscripcion en la nube"),
    "90-day": ("Software y licencias", "Suscripcion en la nube"),
    "1-year": ("Software y licencias", "Suscripcion en la nube"),
    "2-year": ("Software y licencias", "Suscripcion en la nube"),
    "3-year": ("Software y licencias", "Suscripcion en la nube"),
    "lens": ("Optica", "Lente"),
    "monitor": ("Monitor y visualizacion", "Monitor"),
    "pvm": ("Monitor y visualizacion", "Monitor publico (PVM)"),
    "monitor stand": ("Accesorio de instalacion", "Montaje"),
    "explosion proof - accessory": ("Accesorio de instalacion", "Montaje"),
    "switch": ("Red y conectividad", "Switch"),
    "networking/firewall": ("Red y conectividad", "Firewall / router"),
    "networking/poe": ("Energia", "Inyector PoE"),
    "invid extender hdmi over": ("Red y conectividad", "Extensor"),
    "transmission-fiber": ("Red y conectividad", "Fibra / transceiver"),
    "ip audio system": ("Audio", "Sistema de audio IP"),
    "microphone": ("Audio", "Microfono"),
    "microphones": ("Audio", "Microfono"),
    "speaker": ("Audio", "Altavoz"),
    "intercoms": ("Control de acceso", "Intercomunicador"),
    "instalacion/servicio": ("Servicios", "Instalacion"),
    "network - controller": ("Accesorio de instalacion", "Otros accesorios"),
    "usb - controller": ("Accesorio de instalacion", "Otros accesorios"),
    "analog - controller": ("Accesorio de instalacion", "Otros accesorios"),
}

GENERICAS = {"accessory", "accesorios", "accessories"}

# Secciones del proveedor que acertan la CATEGORIA aunque no alcancen para la
# subcategoria (ej. los proveedores locales de incendio: la seccion es
# correcta, pero los nombres vienen abreviados en ingles).
SECCION_FIJA = {
    "deteccion de incendio": "Deteccion de incendio",
    "fuente de poder/ups": "Energia",
    # Estas dos estaban en CONFIABLES apuntando directo a "Lector / terminal"
    # (corregido 2026-09-22). Como CONFIABLES corta antes que las reglas por
    # nombre, TODO lo que el proveedor pusiera en su seccion de acceso salia
    # como lector: gabinetes, botones de salida, cerraduras, una bateria y
    # una fuente de poder. De 40 filas, 29 no eran lectores. Las reglas por
    # nombre para cerradura, boton de salida y gabinete ya existian; nunca
    # llegaban a correr.
    "control de acceso": "Control de acceso",
    "invidtech access control": "Control de acceso",
}


def _sub_incendio(n):
    for k in ["facp", "panel", "4100es"]:
        if k in n:
            return "Panel"
    for k in ["sensor", "detector", " det ", "det ", "beam", "humo", "temperatura",
              "fixedtemp"]:
        if k in n:
            return "Detector"
    for k in ["anunciador", "annunciator", "strobe", "estrobo", "estrodo", "sirena",
              "chime", "compact wall", "audible"]:
        if k in n:
            return "Notificacion"
    return "Accesorio"


def _sub_energia(n):
    for k in [" ups ", "ups "]:
        if k in n:
            return "UPS"
    for k in ["bateria", "battery"]:
        if k in n:
            return "Bateria"
    for k in ["supresor", "protector de descargas", "prtector"]:
        if k in n:
            return "Proteccion electrica"
    for k in ["injector", "inyector"]:
        if k in n:
            return "Inyector PoE"
    return "Fuente de poder"


def _sub_acceso(n):
    """Subcategoria dentro de Control de acceso, por el nombre del producto.
    Solo llega aca lo que ninguna regla por nombre agarro antes, asi que los
    gabinetes, las cerraduras y los botones ya salieron por su propia via."""
    for k in ["keyfob", "key fob", "tarjeta de proximidad", "rfid card",
              "credencial", "virtual key", "^tag$"]:
        if k.strip("^$") in n:
            return "Credencial / tarjeta"
    if n.strip() == "tag":
        return "Credencial / tarjeta"
    for k in ["torniquete", "turnstile"]:
        if k in n:
            return "Torniquete"
    for k in ["intercom", "portero"]:
        if k in n:
            return "Intercomunicador"
    for k in ["controller", "controlador", "access kit", "accesskit"]:
        if k in n:
            return "Controladora"
    return "Lector / terminal"


SUB_POR_SECCION = {
    "Deteccion de incendio": _sub_incendio,
    "Energia": _sub_energia,
    "Control de acceso": _sub_acceso,
}

# --------------------------------------------------------------------------
# 2) Reglas por NOMBRE del producto (nunca por descripcion).
#    Los accesorios inequivocos van ANTES de detectar camara; las palabras
#    que tambien son caracteristicas de una camara (lente, SD, PoE, mount)
#    van DESPUES.
# --------------------------------------------------------------------------
ANTES = [
    # --- 0. Hallazgos del repaso manual de las filas sin clasificar (2026-09-21)
    (("Servicios", "Flete y logistica"),
     ["freight", "flete", "carriage and insurance"]),
    (("Control de acceso", "Torniquete"),
     ["dgate", "placa mcp", "motor dm d3", "trompo"]),
    (("Alarma e intrusion", "Comunicador"),
     ["comunicador de alarma", "ethernet communicator", "cellular and ethernet"]),
    (("Alarma e intrusion", "Contacto magnetico"),
     ["contacto metalico", "contacto para cortina", "contacto de cortina"]),
    (("Alarma e intrusion", "Sensor ambiental"),
     ["vape detector", "sensor de gas", "calidad del aire", "air quality"]),
    (("Alarma e intrusion", "Accesorio de alarma"),
     ["modulo expansor", "expansor de zonas", "zonas cableadas"]),
    (("Energia", "Proteccion electrica"),
     ["supresor de picos", "protector de descargas", "prtector de descargas",
      "surge protector"]),
    (("Energia", "Sistema solar"), ["isss", "independent surveillance"]),
    (("Red y conectividad", "Antena"), ["antena ", "antenna "]),
    (("Monitor y visualizacion", "Monitor"), ["monit led", "monit "]),
    (("Equipo de computo", "Computadora / workstation"),
     ["cpu intel", "core i7", "core i5", "procesador"]),
    (("Control de acceso", "Credencial / tarjeta"), ["card for invid"]),
    (("Accesorio de instalacion", "Montaje"), ["combo ivm-"]),
    # --- 1. Tipos de producto decisivos: si el nombre lo dice, no hay duda.
    #        Van primero porque un "NVR con Redundant Power Supply" es un NVR,
    #        no una fuente de poder.
    (("Grabacion y video", "NVR"), [" nvr", "network video recorder"]),
    (("Grabacion y video", "DVR / hibrido"), [" dvr", "hybrid recorder"]),
    (("Grabacion y video", "Codificador / decodificador"), ["decoder", "encoder"]),
    (("Servicios", "Instalacion"), ["instalacion de", "mano de obra"]),
    (("Servicios", "Capacitacion"), ["capacitacion", "training"]),

    # --- 2. Control de acceso y deteccion: vocabulario propio, sin ambiguedad
    (("Control de acceso", "Cerradura / electroiman"),
     ["cerradura", "electroiman", "electroman", "maglock", "magnetic lock"]),
    (("Control de acceso", "Boton de salida"),
     ["boton de salida", "exit button", "request to exit"]),
    (("Control de acceso", "Credencial / tarjeta"),
     ["tarjeta de proximidad", "proximity card", "desfire graphic card", "credencial",
      "key fob", "llavero"]),
    (("Control de acceso", "Controladora"),
     ["door controller", "controller all in one", "access controller"]),
    (("Control de acceso", "Torniquete"),
     ["torniquete", "turnstile", "lanes 1. size", "acrylic cover",
      "mm304 stainless"]),
    (("Control de acceso", "Intercomunicador"), ["intercom", "video porter", "doorbell"]),
    (("Control de acceso", "Lector / terminal"),
     ["access control", "control de acceso", "card reader", "lector de tarjeta",
      "wiegand", "biometric", "rfid", "mifare", "idface", "idaccess", "iduhf",
      "keypad", "teclado", "facial recognition terminal"]),
    (("Alarma e intrusion", "Boton de panico"),
     ["boton de panico", "panic button", "antipanico", "anti panico"]),
    (("Alarma e intrusion", "Detector de movimiento"),
     ["detector de movimiento", "motion detector", "pir detector", "detector pir"]),
    (("Alarma e intrusion", "Contacto magnetico"),
     ["contacto magnetico", "magnetic contact", "door contact"]),
    (("Alarma e intrusion", "Panel de alarma"),
     ["panel de alarma", "alarm panel", "central de alarma"]),
    (("Alarma e intrusion", "Accesorio de alarma"), ["power g", "powerg"]),
    (("Deteccion de incendio", "Panel"), ["facp", "panel de incendio", "fire panel"]),
    (("Deteccion de incendio", "Detector"),
     ["smoke det", "smk det", "heat det", "detector de humo", "detector de calor",
      "deteccion de humo", "sensor de humo", "sensor de temperatura",
      "foto beam", "fixedtemperature", "sensor tipo"]),
    (("Deteccion de incendio", "Notificacion"),
     ["annunciator", "anunciador", "pull station", "sirena", "horn strobe",
      "estacion manual", "estroboscopica", "estrodoscopica", "chimestrobe",
      "compact wall"]),
    (("Deteccion de incendio", "Accesorio"), ["incendio", " fire "]),

    # --- 3. Energia antes que accesorios (un "PoE Converter" es energia)
    (("Energia", "UPS"), [" ups ", "ups "]),
    (("Energia", "Bateria"), ["bateria", "battery"]),
    (("Energia", "Inyector PoE"),
     ["poe injector", "inyector poe", "hpoe injector", "poe converter",
      "injector"]),
    (("Energia", "Fuente de poder"),
     ["fuente de poder", "fuente de alimentacion", "fuentes de alimentacion",
      "cargador", "power supply", "transformador", "power adapter",
      "receptackle", "receptacle", "inlet flanged", "vac to", "to 12vdc",
      "amp converter"]),

    # --- 4. Red
        (("Red y conectividad", "Accesorio de red"),
     ["ground loop isolator", "over coax", "balun", "patch cord"]),
    (("Red y conectividad", "Fibra / transceiver"), [" sfp", "transceiver", "fibra"]),
    (("Red y conectividad", "Switch PoE"),
     ["poe switch", "switch poe", "xrj45", "x rj45", "uplink ports"]),
    (("Red y conectividad", "Switch"), ["switch", "patch panel"]),
    (("Red y conectividad", "Firewall / router"), ["firewall", "fortigate", "router"]),
    (("Red y conectividad", "Extensor"),
     ["extender", "wireless bridge", "media converter"]),

    # --- 5. Materiales de instalacion (vocabulario en espanol, proveedor local)
    (("Accesorio de instalacion", "Adaptador / conversor"),
     ["conduit adapter", "conduit adaptor", "conduit hole"]),
    (("Materiales de instalacion", "Canalizacion y tuberia"),
     ["tubo ", "tuberia", "conduit", "gaza", "abrazadera", "curva 90", "caja intemperie",
      "caja rectangular", "caja interperie", "tapa emt", "salida tubos",
      "canaleta", " emt ",
      "conector emt", "conector macho", "conector bx", "curva ", "union emt",
      "gazas"]),
    (("Materiales de instalacion", "Cableado"),
     ["cable ", "cable-", "fibra optica", " utp ", "cat6", "cat 6", "alambre",
      "patch cord"]),
    (("Materiales de instalacion", "Ferreteria / postes"), ["poste metalico", "torlack"]),
    (("Materiales de instalacion", "Material electrico"),
     ["breaker", "poliuretano", "cemento", "thhn", "tomacorriente"]),

    # --- 6. Accesorios inequivocos: ANTES de detectar camara, porque un
    #        "Mounting Bracket for Dome Camera" es una montura, no una camara.
    (("Accesorio de instalacion", "Otros accesorios"),
     ["extension cable for", "illuminator", "iluminador", "locker", "lockbox", "lock box", "air filter",
      "filter for", "mast ", "trailer"]),
    (("Accesorio de instalacion", "Caja / housing"),
     ["back box", "backbox", "junction box", "gang box", "gangbox", "installation box",
      "enclosure", "housing", "gabinete", "cabinet"]),
    (("Accesorio de instalacion", "Cubierta / carcasa"),
     ["skin cover", "front cover", "cover for", "weather cap", "cubierta"]),
    (("Accesorio de instalacion", "Adaptador / conversor"),
     ["adapter", "adaptor", "coupler", "thread conv", "pipe conv"]),
    (("Accesorio de instalacion", "Montaje"),
     ["bracket", " mount for", "mounting", "pole mount", "wall mount", "corner mount",
      "pendant", "pedestal", "wall plate", "installation plate", "montura", "soporte",
      "docking", "dock for", "harness", "clamp", "ceiling tile"]),

    # --- 7. Resto
    (("Almacenamiento", "Disco duro"), ["hard drive", "disco duro", " hdd", " ssd "]),
    (("Audio", "Altavoz"), ["speaker", "bocina"]),
    (("Audio", "Microfono"), ["microphone", "microfono"]),
    (("Equipo de computo", "Computadora / workstation"),
     ["computadora", "laptop", "workstation", "desktop pc"]),
    (("Equipo de computo", "Periferico"), ["mouse", "teclado usb"]),
    (("Software y licencias", "Suscripcion en la nube"),
     ["cloud recording", "cloud storage", "cloud service", "recording monthly",
      "recording yearly"]),
    (("Software y licencias", "Integracion / plugin"),
     ["plugin", "add-on", "addon", "integration"]),
    (("Software y licencias", "Licencia VMS"),
     ["license", "licencia", "channel bridge", "bridge hardware"]),
]

DESPUES = [
    (("Monitor y visualizacion", "Senalizacion digital"),
     ["digital signage", "ad box", "screen sharing", "portrait mode"]),
    (("Energia", "Sistema solar"), ["solar"]),
    (("Optica", "Lente"), [" lens", "lente"]),
    (("Almacenamiento", "Tarjeta de memoria"), ["sd card", "tarjeta sd", "purple"]),
    (("Monitor y visualizacion", "Video wall"), ["video wall", "videowall"]),
    (("Monitor y visualizacion", "Monitor"), ["monitor", "display", "pantalla"]),
    (("Accesorio de instalacion", "Montaje"), ["mount", "base ", "stand ", "arm "]),
    (("Accesorio de instalacion", "Otros accesorios"),
     ["accessory", "accesorio", "kit ", "module", "plate", "connector", "conector"]),
]

CAMARA = ["camera", "camara", " dome", "bullet", " ptz", "turret", "eyeball", "fisheye"]
SUB_CAMARA = [
    ("Termica", ["thermal", "termica"]),
    ("LPR / placas", ["license plate", " lpr", "anpr"]),
    ("A prueba de explosion", ["explosion proof"]),
    ("Panoramica / fisheye", ["fisheye", "panoramic", "panoramica", "multisensor",
                              "multi-sensor", "360"]),
    ("PTZ", [" ptz", "ptrz", "positioning"]),
    ("Analogica", [" analog", " tvi", " ahd", " cvi", "cvbs", "hd-tvi"]),
]


IP_EXPLICITO = ["ip plug & play", " ip plug", "megapixel ip", " ip camera", "network camera"]


def _sub_camara(n, base):
    if base == "Analogica":
        for k in IP_EXPLICITO:
            if k in n:
                return "IP / de red"
    for sub, claves in SUB_CAMARA:
        for k in claves:
            if k in n:
                return sub
    return base


# Reglas que ganan sobre TODAS las demas. Salieron de revisar a mano las 40
# filas que el bug de CONFIABLES habia mandado a "Lector / terminal"
# (2026-09-22): ahi se vio que varias las agarraba mal una regla generica.
# El nombre de estos productos trae la descripcion completa del fabricante,
# asi que una palabra suelta en medio del texto decide mal:
#   - "iDBox ... monitorea botones y sensores"  ->  se iba a Monitor
#   - "iDFace ... Intercomunicador SIP integrado"  ->  se iba a Intercomunicador
#     siendo una terminal de reconocimiento facial
#   - los kits listan sus keyfobs, y se iban a Credencial en vez de Controladora
PRIORITARIAS = [
    (("Control de acceso", "Lector / terminal"),
     ["facial recognition terminal", "reconocimiento facial",
      "identificacion biometrica"]),
    (("Control de acceso", "Controladora"),
     # Los kits traen en su nombre la lista de lo que incluyen, empezando por
     # el controlador ("1 - INVID-AIR-CR, 2 - INVID-KEYFOB, ..."). Por eso se
     # busca el controlador y no la palabra "kit", que vive en el SKU y no en
     # el nombre: sin esto el keyfob de la lista los mandaba a Credencial.
     ["access kit", "accesskit", "controller all in one", "controller 4 relay",
      "controlador autonomo", "software de acceso web incluido",
      "invid-air-cr", "invid-icon-pro"]),
    (("Control de acceso", "Credencial / tarjeta"),
     ["keyfob", "key fob", "virtual key", "rfid card", "rfid/card", "rfid/tag"]),
    (("Control de acceso", "Boton de salida"),
     ["button no touch", "boton de salida"]),
    # Teclados de panel de alarma. El modelo (HS2LCD...) vive en el SKU, no
    # en el nombre, asi que hay que reconocerlos por como los describen.
    (("Alarma e intrusion", "Accesorio de alarma"),
     ["powerseries", "hs2lcd", "teclado lcd alfanumerico",
      "teclado cableado lcd alfanumerico"]),
    (("Energia", "Bateria"), ["bateria sellada"]),
    (("Accesorio de instalacion", "Montaje"),
     ["montaje tipo u", "montaje l z"]),
    # Ferreteria de canalizacion: el calibre en fraccion (3/4, 1/2) es lo que
    # la distingue de un conector de red. "conectores RJ45" es Cableado.
    (("Materiales de instalacion", "Canalizacion y tuberia"),
     ["conectores 3/4", "conectores 1/2", "conector 3/4", "conector 1/2",
      "gazas 3/4", "gazas 1/2"]),
]

# H-14 (2026-09-23): 78 filas estaban como "Camara" siendo accesorios de
# montaje, 58 de ellas de una sola marca. Misma causa que H-11: el PDF del
# proveedor las traia bajo un encabezado de seccion "CAMERAS" y CONFIABLES le
# creyo a la seccion. Las reglas por nombre nunca llegaban a correr.
#
# Ojo con el falso positivo obvio: "PTZ camera WITH wall mount" es una CAMARA
# que incluye su montaje, no un montaje. Por eso se exige que el nombre
# EMPIECE con la palabra de accesorio, o que diga "<accesorio> for <modelo>".
import re as _re

_ACC_INICIO = _re.compile(
    r"(?i)^\s*(paramont\s+)?"
    r"(ceiling|in-?ceiling|wall|pole|corner|parapet|pendant|flush|stand|short|heavy duty)?\s*"
    r"(mount|bracket|junction box|back box)\b")
_ACC_PARA = _re.compile(
    r"(?i)\b(mount|bracket|junction box|back box|pedestal)\s+(bracket\s+)?for\b")
_NO_ACC = _re.compile(r"(?i)\b(with|incluye|con)\s+(wall\s+)?mount\b")


def es_accesorio_de_montaje(nombre):
    """True si el NOMBRE dice que la fila es un montaje, no una camara."""
    n = str(nombre or "")
    if _NO_ACC.search(n):
        return False
    return bool(_ACC_INICIO.match(n) or _ACC_PARA.search(n))


def _sub_montaje(nombre):
    n = str(nombre or "").lower()
    if "junction box" in n or "back box" in n:
        return "Caja / housing"
    return "Montaje"


def clasificar(nombre, cat_orig):
    """Devuelve (categoria, subcategoria, como_se_resolvio)."""
    n = norm(nombre)
    c = norm(cat_orig).strip()

    # H-14: si el nombre dice que es un montaje, gana sobre la seccion del
    # proveedor. Va antes que todo lo demas, incluido CONFIABLES.
    if es_accesorio_de_montaje(nombre):
        return ("Accesorio de instalacion", _sub_montaje(nombre),
                "el nombre dice que es un montaje, no una camara")

    for (cat, sub), claves in PRIORITARIAS:
        for k in claves:
            if k in n:
                return cat, sub, "regla prioritaria: '%s'" % k

    if c in CONFIABLES:
        cat, sub = CONFIABLES[c]
        if cat == "Camara":
            fino = _sub_camara(n, sub)
            if fino != sub:
                return cat, fino, "categoria del proveedor + subtipo por nombre"
        return cat, sub, "categoria del proveedor"

    for (cat, sub), claves in ANTES:
        for k in claves:
            if k in n:
                return cat, sub, "nombre: '%s'" % k.strip()

    if " lpr" in n or "license plate" in n:
        return "Camara", "LPR / placas", "nombre: LPR"
    for k in CAMARA:
        if k in n:
            return "Camara", _sub_camara(n, "IP / de red"), "nombre: camara"

    if "monitor" in c:
        return "Monitor y visualizacion", "Monitor", "pista: la seccion del proveedor es de monitores"
    if "camera" in c or "camaras" in c or "camara" in c:
        return "Camara", _sub_camara(n, "IP / de red"), "pista: la seccion del proveedor es de camaras"

    for (cat, sub), claves in DESPUES:
        for k in claves:
            if k in n:
                return cat, sub, "nombre: '%s'" % k.strip()

    if c in SECCION_FIJA:
        cat = SECCION_FIJA[c]
        return cat, SUB_POR_SECCION[cat](n), "seccion del proveedor fija la categoria"

    if c in GENERICAS:
        return "Accesorio de instalacion", "Otros accesorios", "categoria generica del proveedor"
    return "Sin clasificar", "", "sin regla"
