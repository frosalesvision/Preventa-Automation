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
                           "Torniquete", "Puerta / porton automatico"]),
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
    # 2026-10-30, FAAC por Rodhe (TEC #8): operadores de puerta y porton automaticos
    (("Control de acceso", "Puerta / porton automatico"),
     ["puerta automatica", "operador de puerta", "automatic door", "operador 400 cbac",
      "kit 400 cbac", "operador de porton", "porton automatico", "gate operator"]),
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
    (("Grabacion y video", "DVR / hibrido"), [" dvr", "hybrid recorder", "mobile recorder"]),
    (("Grabacion y video", "Servidor / appliance"),
     ["servidor videoxpert", "recording server", "servidor de grabacion"]),
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
     ["door controller", "controller all in one", "access controller", "controladora de acceso",
      "door module"]),
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
    # Despues de panico: un "panic push button" es de panico.
    (("Control de acceso", "Boton de salida"), ["push button"]),
    (("Alarma e intrusion", "Detector de movimiento"),
     ["detector de movimiento", "motion detector", "pir detector", "detector pir"]),
    (("Alarma e intrusion", "Contacto magnetico"),
     ["contacto magnetico", "magnetic contact", "door contact", "window contact", "windowcontact"]),
    (("Alarma e intrusion", "Panel de alarma"),
     ["panel de alarma", "alarm panel", "central de alarma"]),
    (("Alarma e intrusion", "Accesorio de alarma"), ["power g", "powerg"]),
    (("Deteccion de incendio", "Panel"),
     ["facp", "panel de incendio", "fire panel", "panel contra incendio", "loop system"]),
    (("Deteccion de incendio", "Detector"),
     ["smoke det", "smk det", "heat det", "detector de humo", "detector de calor",
      "deteccion de humo", "sensor de humo", "sensor de temperatura",
      "foto beam", "fixedtemperature", "sensor tipo", "photo sensor"]),
    (("Deteccion de incendio", "Notificacion"),
     ["annunciator", "anunciador", "pull station", "sirena", "horn strobe",
      "estacion manual", "estroboscopica", "estrodoscopica", "chimestrobe",
      "compact wall", "estrobo"]),
    (("Deteccion de incendio", "Accesorio"), ["incendio", " fire "]),

    # --- 3. Energia antes que accesorios (un "PoE Converter" es energia)
    (("Energia", "UPS"), [" ups ", "ups "]),
    (("Energia", "Bateria"), ["bateria", "battery"]),
    (("Energia", "Inyector PoE"),
     ["poe injector", "inyector poe", "hpoe injector", "poe converter",
      "injector"]),
    (("Energia", "Fuente de poder"),
     ["fuente de poder", "fuente de alimentacion", "fuentes de alimentacion",
      "cargador", "power supply", "transformador", "transformer", "power adapter",
      "receptackle", "receptacle", "inlet flanged", "vac to", "to 12vdc",
      "amp converter"]),

    # --- 4. Red
        (("Red y conectividad", "Accesorio de red"),
     ["ground loop isolator", "over coax", "balun", "patch cord"]),
    # Antes que Fibra: "SWITCH UNMANAGED 16 PORTS POE ... 1 SFP" es un switch.
    # Con espacio adelante, porque "supports PoE" tambien contiene "ports poe".
    (("Red y conectividad", "Switch PoE"), [" port poe", " ports poe", "puertos poe"]),
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
      "patch cord", "power cord"]),
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
      "enclosure", "housing", "gabinete", "cabinet", "rack estandar", "standard rack"]),
    (("Accesorio de instalacion", "Cubierta / carcasa"),
     ["skin cover", "front cover", "cover for", "weather cap", "cubierta"]),
    (("Accesorio de instalacion", "Adaptador / conversor"),
     ["adapter", "adaptor", "coupler", "thread conv", "pipe conv"]),
    (("Accesorio de instalacion", "Montaje"),
     ["bracket", " mount for", "mounting", "pole mount", "wall mount", "corner mount",
      "pendant", "pedestal", "wall plate", "installation plate", "montura", "soporte",
      "docking", "dock for", "harness", "clamp", "ceiling tile"]),

    # --- 7. Resto
    (("Almacenamiento", "Disco duro"), ["hard drive", "disco duro", " hdd", " ssd ", "hd interno"]),
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

CAMARA = ["camera", "camara", " dome", "bullet", " ptz", "turret", "eyeball", "fisheye",
          "sarix", " srxp"]
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
    # Modulos de un lazo de deteccion de incendio (2026-09-25). "Modulo de
    # monitoreo de una entrada" se iba a Monitor por la palabra "monitor", y
    # un modulo de incendio archivado como pantalla desaparece de las
    # busquedas de incendio. Se piden frases enteras de modulo para no
    # arrastrar nada que solo diga "monitoreo".
    (("Accesorio de instalacion", "Otros accesorios"),
     ["modulo de monitoreo", "modulo de control de senal", "modulo aislador",
      "monitor module", "signal module", "isolator module"]),
    (("Control de acceso", "Lector / terminal"),
     ["facial recognition terminal", "reconocimiento facial",
      "identificacion biometrica",
      # antes que la regla de credenciales: "RFID CARD READER" es un lector
      "card reader"]),
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
    # El panel mismo, antes de la regla de abajo: "Panel de control de
    # seguridad PowerSeries Neo" es el panel, no un accesorio.
    (("Alarma e intrusion", "Panel de alarma"), ["panel de control de seguridad"]),
    # Teclados de panel de alarma. El modelo (HS2LCD...) vive en el SKU, no
    # en el nombre, asi que hay que reconocerlos por como los describen.
    (("Alarma e intrusion", "Accesorio de alarma"),
     ["powerseries", "hs2lcd", "teclado lcd alfanumerico",
      "teclado cableado lcd alfanumerico"]),
    (("Energia", "Bateria"), ["bateria sellada"]),
    (("Accesorio de instalacion", "Montaje"),
     ["montaje tipo u", "montaje l z"]),
    # Una solucion solar que viene en gabinete es un sistema solar, no un
    # gabinete. Sin esto la palabra "gabinete" la manda a Caja / housing.
    (("Energia", "Sistema solar"),
     ["solucion solar", "solar surveillance", "panel solar", "sistema solar"]),
    # --- terminos en ESPANOL (agregado 2026-09-23) ---
    # Casi todas las reglas de este archivo estan en ingles, porque salieron
    # de listas de precios de proveedores gringos. Cuando alguien carga un
    # producto a mano lo describe en espanol, y ahi el clasificador quedaba
    # ciego: "Grabador de video en red" caia en "Sin clasificar".
    (("Grabacion y video", "NVR"),
     ["grabador de video en red", "grabador ip", "grabador de red"]),
    (("Grabacion y video", "DVR / hibrido"),
     ["grabador analogico", "grabador hibrido"]),
    (("Alarma e intrusion", "Boton de panico"),
     ["boton de emergencia", "boton de panico", "boton antipanico"]),
    (("Red y conectividad", "Switch"),
     ["conmutador de red", "conmutador poe", "conmutador gestionado"]),
    (("Accesorio de instalacion", "Montaje"),
     ["montaje de poste", "montaje de pared", "montaje de cielo", "montaje pendant",
      "soporte de poste", "soporte de pared", "brazo para camara", "brazos para camara"]),
    # Ferreteria de canalizacion: el calibre en fraccion (3/4, 1/2) es lo que
    # la distingue de un conector de red. "conectores RJ45" es Cableado.
    (("Materiales de instalacion", "Canalizacion y tuberia"),
     ["conectores 3/4", "conectores 1/2", "conector 3/4", "conector 1/2",
      "gazas 3/4", "gazas 1/2"]),
    # --- cotizaciones de proveedores y listas de Axis, APC y Aruba (2026-09-30)
    (("Software y licencias", "Licencia VMS"), ["pkg-lic", "-lic-"]),
    # Paneles DSC: el nombre trae "keypad" o "control panel", y la regla de
    # teclado los mandaba a Lector / terminal. Ojo: el modelo del panel solo
    # (hs2032) no sirve de clave: aparece tambien en los gabinetes y
    # comunicadores compatibles con ese panel.
    (("Alarma e intrusion", "Panel de alarma"), ["control panel in"]),
    (("Alarma e intrusion", "Comunicador"),
     ["alarmcommunicator", "alarm communicator", "dual path communicator"]),
    (("Deteccion de incendio", "Accesorio"), ["idnet", "iam relay"]),
    # "accesspro cntrl" y no "accesspro" solo: la tarjeta ACCESSPROXCARD lo contiene.
    (("Control de acceso", "Controladora"),
     ["accesspro cntrl", "remote control and receptor", "digital induction"]),
    # El poste del lector va antes que el lector: "NEDAP READER POLE MOUNTING KIT".
    (("Accesorio de instalacion", "Montaje"), ["reader pole", "support for bar", "fixed support"]),
    (("Control de acceso", "Lector / terminal"),
     ["proximity reader", "fingerprint reader", "lector de huella", "upass", "nedap reader"]),
    (("Control de acceso", "Credencial / tarjeta"), ["uhf wnd tg", "windshield tag", "uhf tag"]),
    (("Control de acceso", "Cerradura / electroiman"), ["magnetic knob"]),
    (("Control de acceso", "Boton de salida"), ['"rte" button', "rte button"]),
    (("Control de acceso", "Torniquete"), ["barr 120v", "barrier gate", "barrera vehicular"]),
    (("Accesorio de instalacion", "Cubierta / carcasa"), ["weather protection"]),
    (("Red y conectividad", "Accesorio de red"),
     ["cord organizer", "cable organizer", "organizator", "multiple cord", "organizador de cable"]),
    (("Energia", "Fuente de poder"), ["pwr supply"]),
    # Switches y access points: el nombre trae "SFP" o "antena", que por
    # separado mandan a Fibra / transceiver o a Antena.
    (("Red y conectividad", "Switch PoE"),
     ["class4 poe", "poe 4sfp", "fortiswitch", "switch poe de"]),
    (("Red y conectividad", "Switch"), ["sfp+ switch", "sfp switch", "4sfp/sfp+", "websmart switch", "sfp combo"]),
    (("Red y conectividad", "Antena"),
     ["access point", "unified ap", "campus ap", "instant on ap", "fortiap"]),
    (("Monitor y visualizacion", "Senalizacion digital"), ["senalizacion digital"]),
    # Repuestos cuyo nombre menciona el equipo al que van: "Smoked Dome" es la
    # burbuja de una camara domo, no una camara; "Conduit Back Box" es una
    # caja, no tuberia; "Ceiling Speaker Gasket" es un empaque, no un parlante.
    (("Accesorio de instalacion", "Cubierta / carcasa"),
     ["smoked dome", "clear dome", "dome smoked", "dome clear", "dome cover", "sm dome",
      "hard coated", "hard-coated", "dome casing", "dome cl ", "mesh cover",
      "tamper-resistant cover"]),
    (("Accesorio de instalacion", "Caja / housing"),
     ["conduit back box", "conduit backbox", "conduit top box"]),
    (("Accesorio de instalacion", "Montaje"),
     ["camera holder", "dual camera mount", "conduit bracket", "recessed mount", "picatinny"]),
    (("Accesorio de instalacion", "Otros accesorios"),
     ["gasket", "cable gland", "camera change kit", "photocell"]),
    (("Accesorio de instalacion", "Adaptador / conversor"), ["osdp converter"]),
    # Licencias que nombran el equipo que licencian ("NVR Lic", "decoder license").
    (("Software y licencias", "Licencia VMS"),
     ["nvr lic", "decoder license", "license pack", "licence"]),
    (("Red y conectividad", "Switch PoE"), ["poe+ network switch", "poe++ switch", "poe+ switch"]),
    # Lista de Aruba: "Aruba IOn Switch 1930 24G 4SFP+ PoE 370W" (el PoE no va pegado a "switch")
    (("Red y conectividad", "Switch PoE"), ["sfp+ poe", "sfp poe", "poe cl4"]),
    (("Almacenamiento", "Tarjeta de memoria"), ["surveillance card"]),
    (("Audio", "Altavoz"), ["pendant speaker"]),
    # Cable para alarma de incendio es cable: "incendio" lo mandaba a Deteccion.
    (("Materiales de instalacion", "Cableado"), ["cable para alarma", "fplr"]),
    (("Control de acceso", "Controladora"), ["panel de control de acceso"]),
    (("Control de acceso", "Credencial / tarjeta"), ["tarjeta ioprox", "ioprox card"]),
    (("Control de acceso", "Lector / terminal"), ["time attendance"]),
    # Teclados de panel DSC escritos como los abrevia el distribuidor ("TOUCH KYPD").
    (("Alarma e intrusion", "Accesorio de alarma"),
     ["kypd", "teclado cableado de pantalla", "minicontrolador audiovisual"]),
    (("Alarma e intrusion", "Detector de movimiento"),
     ["ruptura cristal", "ruptura de cristal", "rotura de vidrio", "glass break"]),
    # Sirenas de alarma. La regla general "sirena" las manda a Deteccion de
    # incendio, que es lo correcto para las de incendio (estroboscopica,
    # multicandela); estas dicen que son de alarma por como las describen.
    (("Alarma e intrusion", "Sirena"),
     ["sirena cableada", "sirena electronica", "sirena para exterior", "sirena exterior",
      "sirena de alarma", "sirena inalambrica", "sirena con led", "tone siren"]),
    (("Accesorio de instalacion", "Otros accesorios"), ["lente de repuesto"]),
    # Lo que es PARA el panel de alarma es accesorio del panel (teclados,
    # modulos); sin esto "teclado" lo manda a lectores de control de acceso.
    (("Alarma e intrusion", "Accesorio de alarma"), ["para panel de alarma"]),
    (("Alarma e intrusion", "Comunicador"), [" comunicador "]),
    # Montajes de cerradura: la palabra "cerradura" los mandaba a Cerradura.
    (("Accesorio de instalacion", "Montaje"),
     ["montaje en u", "montaje en z", "montaje p / cerradura", "montaje para cerradura", "montaje lz"]),
    (("Control de acceso", "Boton de salida"), ["texto salida de emergencia", "boton momentaneo"]),
    (("Software y licencias", "Licencia VMS"), ["software de control de acceso"]),
    (("Energia", "Fuente de poder"), ["power supply with battery", "wall adapter 12"]),
    # Equipos cuyo nombre menciona otro equipo con el que trabajan:
    # "JOYSTICK IP FOR NVR", "AVIATION CABLE ... MOBILE DVR". El joystick va
    # con frase: una camara "with OSD Joystick" sigue siendo camara.
    (("Equipo de computo", "Periferico"),
     ["joystick ip", "joystick dahua", "joystick para", "joystick keyboard", "network keyboard"]),
    (("Materiales de instalacion", "Cableado"), ["aviation cable"]),
    (("Control de acceso", "Credencial / tarjeta"), ["clamshell", "lamshell"]),
    # Camaras corporales (body worn) y sus bases de carga
    (("Camara", "Otra especializada"), ["fhd bwc", "body worn camera"]),
    (("Accesorio de instalacion", "Otros accesorios"), ["usb dock", "dockcontroller"]),
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


# --------------------------------------------------------------------------
# 3) Secciones de la lista de Axis / 2N (2026-09-30). Los nombres de Axis
#    son cortos y las reglas generales, escritas para los nombres largos de
#    otros proveedores, se equivocan con ellos: "2N IP Verso - main W camera"
#    es un intercomunicador, no una camara; "AXIS TU9003 Keypad" es el
#    teclado de una consola de video, no un lector; "ACS PRO Core Device NVR
#    Lic" es una licencia, no un NVR. Por eso, en estas secciones, decide la
#    seccion junto con las palabras del nombre, y lo hace ANTES que las
#    reglas generales (solo PRIORITARIAS le gana).
#
#    Hoy solo la lista de Axis usa estos nombres de seccion. Si otro
#    proveedor trae una seccion "Software", "Recorder" o "Access Control",
#    pasa por aqui: por eso cada seccion termina en el destino que tiene
#    sentido para cualquier proveedor (Software -> licencia, Recorder -> NVR).
# --------------------------------------------------------------------------
def _axis_por_claves(n, reglas, defecto):
    for claves, destino in reglas:
        if any(k in n for k in claves):
            return destino
    return defecto


def _axis_grabador(n):
    return _axis_por_claves(n, [
        (["hard drive"], ("Almacenamiento", "Disco duro")),
        ([" dvr", "hybrid"], ("Grabacion y video", "DVR / hibrido")),
        # S11 / S12 son servidores (torre o rack); S93, estaciones de trabajo.
        # S21 / S22 (todo en uno con switch PoE) y S30 graban como un NVR.
        ([" s11", " s12", "server", " tower", " rack"], ("Grabacion y video", "Servidor / appliance")),
        ([" s93", "workstation"], ("Equipo de computo", "Computadora / workstation")),
    ], ("Grabacion y video", "NVR"))


def _axis_codec(n):
    return _axis_por_claves(n, [
        (["license", " lic"], ("Software y licencias", "Licencia VMS")),
    ], ("Grabacion y video", "Codificador / decodificador"))


def _axis_audio(n):
    return _axis_por_claves(n, [
        (["license", " lic", "elic"], ("Software y licencias", "Licencia VMS")),
        (["gasket", "wire kit"], ("Accesorio de instalacion", "Otros accesorios")),
        (["cover"], ("Accesorio de instalacion", "Cubierta / carcasa")),
        (["conduit adapter"], ("Accesorio de instalacion", "Adaptador / conversor")),
        (["tile bridge", "mount"], ("Accesorio de instalacion", "Montaje")),
        (["audio bridge", " amp", "volume controller", "audio manager"], ("Audio", "Sistema de audio IP")),
        (["horn", "speaker", " c1", " xc1"], ("Audio", "Altavoz")),
        (["microphone", "console", " c6", " c7"], ("Audio", "Microfono")),
    ], ("Audio", "Sistema de audio IP"))


def _2n(n):
    """2N Access Control and Intercoms / Answering Units. El orden importa:
    primero el software, despues las piezas sueltas (marcos, cajas, tornillos,
    tarjetas de botones), despues los equipos completos y al final los
    lectores. Asi "2N IP Force - 1 BTN + HD CAM + KPD" (un frente de calle que
    trae teclado) queda como intercomunicador y no como lector, y "2N IP Verso
    - Keypad" (el modulo de teclado) queda como lector."""
    return _axis_por_claves(n, [
        # la lista de Axis pone la mini PTZ AXIS M5000 en una seccion de 2N
        (["axis m5"], ("Camara", "PTZ")),
        ([" lic", "licence", "license"], ("Software y licencias", "Licencia VMS")),
        (["subs my2n", "annual "], ("Software y licencias", "Suscripcion en la nube")),
        (["plugin", "informacast"], ("Software y licencias", "Integracion / plugin")),
        (["commander box", "web relay", "ip relay", "security relay"], ("Control de acceso", "Controladora")),
        (["power supply", " psu"], ("Energia", "Fuente de poder")),
        (["injector"], ("Energia", "Inyector PoE")),
        (["antenna"], ("Red y conectividad", "Antena")),
        (["door contact"], ("Alarma e intrusion", "Contacto magnetico")),
        (["nvt pl-08 switch"], ("Red y conectividad", "Switch")),
        (["2wire"], ("Red y conectividad", "Extensor")),
        (["cable", "bus short"], ("Materiales de instalacion", "Cableado")),
        (["2n clip,"], ("Control de acceso", "Intercomunicador")),
        ([" box", "backbox", "chassi"], ("Accesorio de instalacion", "Caja / housing")),
        (["adapter", "adaptor"], ("Accesorio de instalacion", "Adaptador / conversor")),
        (["cover", "window"], ("Accesorio de instalacion", "Cubierta / carcasa")),
        (["screw", "torx", "sealing", "tamper switch", "add.switch", "audio kit", "microphone",
          "speaker", "extender", "induction loop", "usb camera", "label", "nametag", "nameplate",
          "name plate", "reflector", "clamp", "terminal", "button board", "buttons board",
          "button on pcb", "isolator", "bushings", "gasket", "tool"],
         ("Accesorio de instalacion", "Otros accesorios")),
        (["frame", "backplate", "spacer", "mounting", "mount", "stand", "bracket", "pole", "wedge",
          "plate", "lower fix", "top fix", "gooseneck", "fixture"], ("Accesorio de instalacion", "Montaje")),
        (["card reader"], ("Control de acceso", "Lector / terminal")),
        (["key fob", "keyfob", " fob", "smart card", "prox card", "rfid card", "2n card", "cards", "tags"],
         ("Control de acceso", "Credencial / tarjeta")),
        # equipos completos: frentes de calle y unidades interiores
        (["ip force", "ip safety", "ip solo", "ip base", "ip style", "ip one", "main unit", "main w",
          "indoor", "ip phone"], ("Control de acceso", "Intercomunicador")),
        (["rfid", "nfc", "125k", "13.56", "13m", "fingerprint", "keypad", "kpd", "bluetooth", "bt&",
          "ble", " qr", "access unit", " au ", " au2", "biometric"], ("Control de acceso", "Lector / terminal")),
    ], ("Control de acceso", "Intercomunicador"))


def _2n_audio(n):
    return _axis_por_claves(n, [
        (["power supply"], ("Energia", "Fuente de poder")),
        (["microphone", " mic"], ("Audio", "Microfono")),
        (["speaker", "horn"], ("Audio", "Altavoz")),
    ], ("Audio", "Sistema de audio IP"))


def _axis_acceso(n):
    return _axis_por_claves(n, [
        (["converter"], ("Accesorio de instalacion", "Adaptador / conversor")),
        (["card reader"], ("Control de acceso", "Lector / terminal")),
        (["card", "fob", " tag"], ("Control de acceso", "Credencial / tarjeta")),
        # AXIS I70xx / I80xx / I81xx y A82xx: intercomunicadores y porteros de video
        ([" i70", " i80", " i81", " a82", "intercom"], ("Control de acceso", "Intercomunicador")),
        (["reader", "keypad", " a40", " a41", " a46"], ("Control de acceso", "Lector / terminal")),
        (["lock", "cerradura"], ("Control de acceso", "Cerradura / electroiman")),
        (["exit button", "request to exit"], ("Control de acceso", "Boton de salida")),
        (["enclosure", " box"], ("Accesorio de instalacion", "Caja / housing")),
        (["adapter"], ("Accesorio de instalacion", "Adaptador / conversor")),
        (["cover", "weathershield"], ("Accesorio de instalacion", "Cubierta / carcasa")),
        (["mount", "bracket", "plate"], ("Accesorio de instalacion", "Montaje")),
        (["strain relief", "clip", "label", "tamper"], ("Accesorio de instalacion", "Otros accesorios")),
    ], ("Control de acceso", "Controladora"))


def _axis_sistema(n):
    return _axis_por_claves(n, [
        (["surveillance card", "sd card"], ("Almacenamiento", "Tarjeta de memoria")),
        (["hard drive"], ("Almacenamiento", "Disco duro")),
        (["midspan", "mdspn", "poe injector", "splitter"], ("Energia", "Inyector PoE")),
        (["poe+ network switch", "poe switch", "poe+ switch"], ("Red y conectividad", "Switch PoE")),
        (["switch"], ("Red y conectividad", "Switch")),
        (["sfp", "fiber", "media converter"], ("Red y conectividad", "Fibra / transceiver")),
        (["coax"], ("Red y conectividad", "Accesorio de red")),
        (["extender"], ("Red y conectividad", "Extensor")),
        (["joystick", "keyboard", "keypad", "control board", " t831"], ("Equipo de computo", "Periferico")),
        (["surge", "protector"], ("Energia", "Proteccion electrica")),
        (["power supply", " psu", "power adapter", "charger", "mains adap", " ps12", " ps24", " ps57"],
         ("Energia", "Fuente de poder")),
        (["battery"], ("Energia", "Bateria")),
        (["microphone"], ("Audio", "Microfono")),
        (["lens"], ("Optica", "Lente")),
        (["cover"], ("Accesorio de instalacion", "Cubierta / carcasa")),
        (["cabinet", "enclosure", "housing"], ("Accesorio de instalacion", "Caja / housing")),
        (["mount", "bracket"], ("Accesorio de instalacion", "Montaje")),
        (["cable"], ("Materiales de instalacion", "Cableado")),
        (["adapter", "adaptor"], ("Accesorio de instalacion", "Adaptador / conversor")),
    ], ("Accesorio de instalacion", "Otros accesorios"))


def _axis_dispositivo(n):
    return _axis_por_claves(n, [
        # AXIS D21xx / D22xx son radares aunque el nombre no lo diga ("AXIS D2110-VE")
        (["radar", " d21", " d22"], ("Alarma e intrusion", "Detector de movimiento")),
        (["siren", "strobe", " d41", " d42"], ("Alarma e intrusion", "Sirena")),
        (["air quality", " d6"], ("Alarma e intrusion", "Sensor ambiental")),
        (["poe switch", "poe+ switch", "poe++ switch"], ("Red y conectividad", "Switch PoE")),
        (["switch"], ("Red y conectividad", "Switch")),
        (["audio and i/o", "audio i/o", "interface"], ("Audio", "Sistema de audio IP")),
    ], ("Alarma e intrusion", "Accesorio de alarma"))


def _axis_software(n):
    return _axis_por_claves(n, [
        (["cloud"], ("Software y licencias", "Suscripcion en la nube")),
        (["plugin", "integration"], ("Software y licencias", "Integracion / plugin")),
    ], ("Software y licencias", "Licencia VMS"))


def _axis_vestible(n):
    return _axis_por_claves(n, [
        ([" lic", "license", " live", "insight", "subscription"], ("Software y licencias", "Suscripcion en la nube")),
        (["lens protector", "cable holder"], ("Accesorio de instalacion", "Otros accesorios")),
        (["rail", "mount", "clip", "harness"], ("Accesorio de instalacion", "Montaje")),
        (["battery"], ("Energia", "Bateria")),
        (["charging", "charger", "adaptor", "adapter"], ("Accesorio de instalacion", "Adaptador / conversor")),
        (["dock", "controller", "system"], ("Accesorio de instalacion", "Otros accesorios")),
    ], ("Camara", "Otra especializada"))


SECCION_PROVEEDOR = {
    "recorder": _axis_grabador,
    "encoder decoder": _axis_codec,
    "audio system": _axis_audio,
    "2n audio": _2n_audio,
    "2n access control and intercoms": _2n,
    "2n answering units": _2n,
    "access control": _axis_acceso,
    "system accessory": _axis_sistema,
    "system device": _axis_dispositivo,
    "software": _axis_software,
    "wearables": _axis_vestible,
}


def clasificar(nombre, cat_orig):
    """Devuelve (categoria, subcategoria, como_se_resolvio)."""
    n = norm(nombre)
    c = norm(cat_orig).strip()

    # H-14: si el nombre dice que es un montaje, gana sobre la seccion del
    # proveedor. Va antes que todo lo demas, incluido CONFIABLES.
    if es_accesorio_de_montaje(nombre):
        return ("Accesorio de instalacion", _sub_montaje(nombre),
                "el nombre dice que es un montaje, no una camara")

    # Un panel de incendio EMPIEZA diciendo "Panel". Si la palabra aparece en
    # medio suele ser un dispositivo PARA un panel: el sensor GD-6 se llama
    # "Sensor de Gas ... para Panel de Deteccion de Incendio" y una regla por
    # subcadena lo convertia en panel.
    if _re.match(r"(?i)^\s*panel\b.*(incendio|fire)", str(nombre or "")):
        return "Deteccion de incendio", "Panel", "el nombre empieza con Panel de incendio"

    for (cat, sub), claves in PRIORITARIAS:
        for k in claves:
            if k in n:
                return cat, sub, "regla prioritaria: '%s'" % k

    if c in SECCION_PROVEEDOR:
        cat, sub = SECCION_PROVEEDOR[c](n)
        return cat, sub, "seccion de la lista de Axis / 2N"

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
