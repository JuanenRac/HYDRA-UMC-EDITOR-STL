<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="Banner de HYDRA-UMC-EDITOR-STL" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | 🇪🇸 <b>Español</b> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a></p>

### 📦 Explora y Edita las Librerías de Modelos STL Reales del Ecosistema HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/Licencia-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/Lenguaje-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Núcleo-numpy--stl-brightgreen.svg" alt="núcleo numpy-stl">
  <img src="https://img.shields.io/badge/Escritorio-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="GUI de escritorio PySide6 Qt Quick">
</p>

> **v0.0.4.** El núcleo real de CLI/GUI descrito abajo está implementado
> y probado de verdad, incluido un visor 3D real en Qt Quick 3D con
> selección por clic, color por pieza, transformar, reemplazar, quitar,
> añadir y un envío real de un modelo editado/añadido de vuelta al
> catálogo real `POST /api/models/submit` de HYDRA-UMC-SERVER (el mismo
> punto de integración real que usa HYDRA-UMC-EDITOR-URDF con los modelos
> URDF). El color guardado de una pieza ahora también llega a los visores
> 3D en vivo de HYDRA-UMC-STUDIO y HYDRA-UMC-SUITE (cambios reales
> propios de esos repos - ver sus propios CHANGELOG), así que
> `part_colors.json` ya no es una vista previa exclusiva de EDITOR-STL.

**Comprobación de honestidad - qué funciona de verdad hoy:**
`model_catalog.py` (descubrimiento real, de solo lectura, de las dos
librerías de modelos), `stl_ops.py` (mutación real de STL vía
`numpy-stl` - transformar/reemplazar/quitar/añadir, más
`model_bounds()` para el encuadre de cámara del visor 3D),
`part_colors.py` (fichero auxiliar real de color por pieza),
`stl_geometry.py` (carga real de geometría Qt Quick 3D) y
`catalog_push.py` (generación real de un URDF de ensamblaje más un
cliente HTTP real para `POST /api/models/submit`) están todos
probados contra ficheros STL reales generados y una `QGuiApplication`
real de ámbito de sesión donde hace falta (`pytest tests/`, 48 casos en
verde) y se han verificado de extremo a extremo contra los checkouts
reales de `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` de este ecosistema
(`--cli categories`/`models`/`parts` contra los árboles reales;
`transform`/`remove` contra una copia desechable, nunca contra el
checkout real). El propio `EditorBridge` de `qt_gui.py` también está
probado directamente (el slot de color, la selección preservada tras un
cambio de color). `qml/Main.qml` carga y se renderiza sin errores de
QML (verificado sin interfaz con `QT_QPA_PLATFORM=offscreen`, incluso
con las piezas reales de un modelo cargadas en el visor 3D), pero el
propio grafo de escena QML no tiene test automatizado propio - manejar
un bucle de eventos Qt real no se intenta aquí, el mismo límite de
honestidad que el propio README de HYDRA-UMC-UPDATER ya traza para su
propia capa Qt Quick.

---

## 1. 🛠️ VISIÓN TÉCNICA

HYDRA-UMC-EDITOR-STL es una pequeña herramienta de escritorio - GUI de
ventana por defecto, CLI completa con `--cli` - para editar las piezas
STL reales que forman cada modelo de robot/máquina que HYDRA-UMC-STUDIO
y HYDRA-UMC-SUITE distribuyen. Ambas apps reorganizaron sus propias
carpetas de modelos en 2026-09 en la misma estructura real de categorías
(`robots-5-dof`/`robots-6-dof`/`robots-7-dof`,
`machine-pnp`/`machine-cnc`/`machine-laser`,
`heatedbeds`/`racks`/`vacuum-tables`, cada modelo con su propio
`metadata.json` junto a su `ATTRIBUTION.txt`) - esta herramienta lee esa
misma estructura real, no una copia separada ni una base de datos
propia.

Un visor 3D real en Qt Quick 3D renderiza cada pieza editable del
modelo seleccionado (`stl_geometry.py`, un `QQuick3DGeometry` real que
carga los triángulos de cada pieza directamente desde su archivo STL) -
arrastra para orbitar, rueda para hacer zoom, clic en una pieza para
seleccionarla (`View3D.pick()` real, no una estimación). La cámara se
encuadra sola sobre la caja delimitadora combinada real del modelo
(`model_bounds()` de `stl_ops.py`), así que una base de robot de 400mm
y un tornillo de 5mm encuadran correctamente por igual.

Seis operaciones reales, cada una respaldada por E/S de ficheros real
contra el checkout real en disco:

- **Transformar** - trasladar/rotar/escalar los vértices reales de una
  pieza (vía `numpy-stl`, la misma librería de la que ya depende
  `render/mesh.py` de HYDRA-UMC-SUITE) y guardarla de vuelta en el
  mismo sitio.
- **Cambiar color** - una anotación real de color por pieza
  (`part_colors.json`, un fichero auxiliar propio de esta herramienta)
  mostrada en el visor 3D - un STL binario no lleva un color propio
  fiable, así que este fichero auxiliar es la fuente real de verdad.
  El propio `hooks/usePartColors.ts` de HYDRA-UMC-STUDIO y el propio
  `render/part_colors.py` de HYDRA-UMC-SUITE leen ese mismo fichero, así
  que un color guardado aquí también llega a sus visores 3D en vivo, no
  solo a la vista previa de esta herramienta.
- **Reemplazar** - sobrescribir una pieza con otro fichero STL real.
- **Quitar** - retirar una pieza de un modelo.
- **Añadir** - incorporar un nuevo fichero STL real a un modelo.
- **Enviar al servidor** - enviar las piezas editables actuales del
  modelo seleccionado al catálogo real de envío de modelos de un
  HYDRA-UMC-SERVER en ejecución (`catalog_push.py`,
  `POST /api/models/submit` - requiere una sesión de administrador,
  igual que la funcionalidad equivalente de HYDRA-UMC-EDITOR-URDF). Como
  el contrato de ese endpoint está pensado para URDF, esto envuelve las
  piezas en el URDF real más pequeño que acepta: un enlace raíz más un
  enlace hijo sin articular (`fixed`) por pieza, ya que la posición real
  de cada pieza ya está integrada en sus propios vértices STL - nunca una
  pose inventada.
- **Barra flotante del visor** - Seleccionar, Mover (un gizmo real de 3 ejes arrastrable), Editar (rotar/escalar), Color, Añadir, Borrar, Fijar (guarda de forma permanente el movimiento/rotación/escala), Copiar, Pegar y Cortar, dentro del propio visor 3D. Las camas calientes, mesas de vacío y racks son variantes de tamaño independientes, así que el visor muestra solo la seleccionada en vez de apilarlas.

**Nunca se borra nada de forma permanente.** Un "quitar" o un
"reemplazar" mueve primero el fichero original real a la propia
subcarpeta `.trash/` de ese modelo - la misma disciplina de "nunca
destruir, mover a un lado" que ya siguen las convenciones internas de
trabajo de este ecosistema, aplicada aquí como una funcionalidad real
del producto, no solo como un hábito interno.

## 2. 🧱 ARQUITECTURA Y DECISIONES DE DISEÑO

- **Dos librerías reales, un solo módulo de descubrimiento.** La propia
  constante `LIBRARIES` de `model_catalog.py` nombra los dos árboles
  reales que edita esta herramienta (`HYDRA-UMC-STUDIO/public/models/`,
  `HYDRA-UMC-SUITE/assets/meshes/`) - añadir una tercera librería más
  adelante significa añadir una entrada ahí, no una segunda
  implementación de descubrimiento.
- **`stl_ops.py` es el único sitio que muta un fichero.**
  `model_catalog.py` se mantiene estrictamente de solo lectura; tanto
  `--cli` como el puente Qt Quick llaman exactamente a las mismas
  funciones `transform_part()`/`replace_part()`/`remove_part()`/
  `add_part()`, así que la GUI nunca puede hacer nada que la CLI misma
  no pudiera.
- **Un STL real, no solo un nombre de fichero terminado en `.stl`.**
  `is_real_stl()` de verdad analiza un candidato a reemplazo/adición con
  `numpy-stl` antes de copiarlo nunca a una carpeta de modelo real - y,
  un fallo real encontrado escribiendo los propios tests de este
  proyecto, también rechaza un resultado de análisis con **0
  triángulos**: la propia ruta de reserva ASCII de `numpy-stl` no lanza
  excepción ante bytes de basura arbitrarios, los analiza en silencio
  como una malla vacía, así que un simple try/except por sí solo habría
  dejado pasar un fichero que no es un STL en absoluto.
- **GUI Qt Quick por defecto, `--cli` para sistemas sin pantalla.**
  `main.py` solo importa PySide6 en la ruta que no es `--cli`, así que
  `--cli categories`/`models`/`parts`/`transform`/`replace`/`remove`/
  `add` funcionan en una máquina sin pantalla ni runtime de Qt instalado
  en absoluto.
- **La misma capa visual real que HYDRA-UMC-UPDATER.** `qml/Main.qml`
  reutiliza literalmente los componentes propios `GameButton`/
  `GameCombo`/`SectionPanel` de ese proyecto y su tema oscuro
  cian/azul/ámbar/rojo, a petición explícita del dueño del proyecto -
  una herramienta de PC nueva en este ecosistema debe sentirse como la
  misma herramienta, no como una diseñada aparte.
- **Raíz del ecosistema, no una ruta fija.** Igual que la raíz de
  workspace propia de HYDRA-UMC-UPDATER, el directorio padre de este
  propio proyecto es el valor por defecto (`default_ecosystem_root()`
  de `main.py`), siempre sobreescribible (`--root` en `--cli`,
  "Examinar" en la GUI) y recordado entre lanzamientos de la GUI
  (`settings.py`).

## 📂 ESTRUCTURA DE DIRECTORIOS

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # Descubrimiento real, de solo lectura, de ambas librerías de modelos
│   ├── stl_ops.py           # Mutación real de STL: transformar/reemplazar/quitar/añadir, copias de seguridad en .trash/
│   ├── catalog_push.py       # URDF de ensamblaje + cliente HTTP para POST /api/models/submit
│   ├── settings.py          # Raíz del ecosistema e idioma persistidos
│   ├── i18n.py               # Traducciones reales y completas de la GUI (7 idiomas)
│   ├── qt_gui.py             # Puente Qt Quick sobre el núcleo real model_catalog.py/stl_ops.py
│   ├── qml/Main.qml          # Capa visual de escritorio, compartida con HYDRA-UMC-UPDATER
│   └── main.py               # Despacho: GUI por defecto, --cli para categories/models/parts/transform/replace/remove/add/push
├── tests/                    # Tests reales contra ficheros STL reales generados
├── docs/
│   └── CLI_REFERENCE.md      # Referencia de comandos
├── images/                   # Recursos multimedia e iconos de la app
├── tools/
│   ├── build_test.py         # Comprobación de compilación sin tocar versiones
│   └── ci_validate.py        # Validación de manifiesto/CHANGELOG/docs usada por CI
├── build.sh / build.bat      # venv + instalación editable (extras dev+gui) + comprobación de compilación + tests
├── run.sh / run.bat          # GUI por defecto / punto de entrada de la CLI
├── run-gui.vbs               # Lanzador gráfico para Windows sin ventana de consola
├── bump_version.py           # Incremento de versión "odómetro" del ecosistema (pyproject.toml + __init__.py)
└── bump_manifest_version.py  # Sincroniza la versión de hydra-umc.project.json con la nativa (--sync)
```

## ⚙️ GUÍA DE COMPILACIÓN Y EJECUCIÓN

```bash
chmod +x build.sh   # una sola vez
./build.sh          # crea .venv, pip install -e ".[dev,gui]", compila y prueba
./run.sh                                                    # GUI de ventana (por defecto)
./run.sh --cli categories studio                            # lista categorías en una librería
./run.sh --cli models studio robots-6-dof                   # lista modelos en una categoría
./run.sh --cli parts studio robots-6-dof ar3                 # lista los ficheros de piezas reales de un modelo
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /ruta/nuevo.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /ruta/nuevo.stl
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin --password ***
```

En Windows: `build.bat`, luego `run.bat` (GUI) o `run.bat --cli ...` /
doble clic en `run-gui.vbs` para lanzar la GUI sin consola.

`library` siempre es `studio` o `suite`; `category`/`model` son los
nombres reales de carpeta que acaban de imprimir `categories`/`models`.
`--root` sobreescribe la raíz del ecosistema para cualquier comando
`--cli` (por defecto: el directorio padre propio de esta herramienta).

**Solución de problemas**

- `categories`/`models`/`parts` no imprime nada: la raíz del ecosistema
  en realidad no contiene `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` como
  hermanos - pasa `--root` explícitamente, o usa "Examinar" en la GUI.
- `transform`/`replace`/`add` falla con "not a real, parseable STL
  file": el fichero de origen de verdad no es un STL válido (o es uno
  de 0 triángulos) - ábrelo en un visor real de CAD/mallas para
  confirmarlo.
- Una pieza quitada/reemplazada no desapareció de la lista de piezas de
  la GUI: sí se movió a `.trash/` en disco - la lista de piezas solo
  muestra ficheros reales del nivel superior actual, y una subcarpeta
  `.trash/` queda excluida de ella a propósito.

## 🚀 HOJA DE RUTA

- Un ejecutable de GUI independiente empaquetado (PyInstaller, siguiendo
  la misma convención `build_exe.bat`/`.sh` de HYDRA-UMC-SUITE).
- Deshacer/rehacer sobre el propio historial `.trash/` de una sesión, en
  vez de una restauración manual de ficheros.

## 🔗 Proyectos Relacionados

Este proyecto forma parte del ecosistema de robótica HYDRA-UMC del mismo autor (JuanenRac / Electro Hobby 3D). Vale la pena conocerlo, ya que una petición podría en realidad ser sobre uno de estos en vez de sobre este repositorio.

**Proyecto Padre**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — dueño de una de las dos librerías de modelos reales que este editor lee y escribe (`public/models/`).

**Directamente Relacionados**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — dueño de la segunda librería de modelos real que este editor lee y escribe (`assets/meshes/`), mantenida en exactamente la misma estructura de categorías que la de STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — editor de escritorio hermano para el lado URDF/cinemática del mismo catálogo de modelos, en vez de la geometría STL cruda que edita esta herramienta.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — dueño del endpoint real `POST /api/models/submit` al que este editor envía sus ediciones terminadas (`catalog_push.py`, "Enviar al servidor..." en la GUI o `--cli push`).

**También Forman Parte del Ecosistema**

*Hardware y Plataforma Central*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la placa base física del brazo robótico: host CM5 + STM32H745 de doble núcleo, orquestando hasta 8 brazos herramienta por CAN-OTA/SPI-OTA.
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — capa de producto Raspberry Pi OS reproducible para la CM5: agente de solo lectura, config/perfiles validados, aprovisionamiento WiFi de primer contacto.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — el contrato JSON-Schema compartido y el límite de puerta de seguridad contra el que valida sus comandos cada bridge.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registro declarativo de manifiestos de adaptadores y su validador para conectores de máquinas externas; extiende la idea de contrato del SDK a máquinas externas sin reemplazar los proyectos de gateway industrial.

*Backend Central y Clientes*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app de control nativa de Android con login biométrico y una compañera Wear OS emparejada.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app de control iOS/iPadOS (Flutter) con sincronización WebSocket en tiempo real.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — UI táctil nativa para la pantalla táctil DSI de 7" integrada en la propia CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creador/editor gráfico de escritorio de URDF con carga de fuente desde GitHub/local y edición con vista previa 3D en vivo.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — límite de coordinación para flotas AGV/AMR vía un publicador MQTT VDA 5050 real.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinador de celda CNC de alto nivel con acceso real a estado/byte de control GRBL.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — límite de coordinación para droides con patas/humanoides, con un emisor de comandos real para Boston Dynamics Spot.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinador de seguridad de celda láser que lee 3 salvaguardas GPIO reales de llave/carcasa/enclavamiento.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinador seguro de alto nivel del flujo de placas para pick-and-place de OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — límite de coordinación seguro para impresoras 3D Moonraker/Klipper, con comandos de trabajo reales con puerta de control.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinador de seguridad con un transporte ROS 2 rclpy real, importado de forma perezosa.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — límite de coordinación para UAVs equipados con cámara, con un emisor de comandos MAVLink real.

*Plataforma de Herramientas URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware para la PCB física del Universal Robot Tool Controller, más de 25 perfiles de herramienta por bus CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — herramienta GUI de escritorio para flashear placas URTC, CAN-OTA más SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — herramienta de diagnóstico CAN en vivo de escritorio para placas URTC, un panel por perfil de herramienta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basada en navegador a URTC-TESTER vía la Web Serial API, sin instalación local.

*Nodo de Visión IA (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub de integración para el pipeline de visión Hailo-8, con una comprobación real de preparación de hardware por etapa.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registro real de modelos compilados con verificación de carga segura por arquitectura/checksum de Hailo.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — generador real de pipeline GStreamer + config de MediaMTX con un límite de integración HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — ley de corrección real de Position-Based Visual Servoing, con puerta de seguridad según el estado de zona aguas arriba.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — comprobación real de violación de zonas y solicitud de E-STOP, con exigencia de frescura de calibración.

*Nodo Cognitivo IA (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — hub de integración para el pipeline cognitivo Hailo-10 (orquestación de LLM/VLA/voz).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — codificación/decodificación real de tokens de acción y generación de trayectorias para un modelo Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — frontend de voz real (VAD + analizador de intención) con un relé a Watch acotado y sujeto a confirmación.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — descomposición real de tareas basada en reglas y recuperación semántica de errores sobre códigos de error del MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — búsqueda real de documentos TF-IDF solo con stdlib sobre los propios docs Markdown de este ecosistema.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — técnico de mantenimiento IA local, con puerta de políticas, para el propio ecosistema - observa, diagnostica y propone arreglos; los dos niveles de riesgo más altos están deliberadamente sin implementar todavía.

*Orquestación y Enjambre*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — hub de integración con un contrato real gRPC/Protobuf de informe de salud y una máquina de estados de misión.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — cola de trabajos real basada en prioridad con deduplicación, sobre una API HTTP real.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vigilante de salud de flota real basado en gRPC con reintento/backoff y detección de discrepancia de identidad.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — planificador de trayectorias 3D real basado en RRT con validación real de colisión de obstáculos/espacio de trabajo.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — sincronización de estado real CRDT LWW-Element-Map, probada por propiedades para convergencia multi-celda.

*Gemelo Digital y Simulación*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — gemelo digital de simulación física real, consumiendo los modelos URDF que produce HYDRA-UMC-EDITOR-URDF.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — consume esos mismos modelos URDF para su propia simulación física.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — genera datos de entrenamiento a partir de esos mismos modelos.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — enclavamiento de seguridad hardware-in-the-loop real que enruta comandos entre simulación y hardware real.

*Datos y Analítica*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — almacén de series temporales real respaldado por sqlite3 con una API HTTP real de ingesta/consulta.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — detector de anomalías real por FFT + línea base estadística con monitorización de deriva.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — cálculo real de OEE/disponibilidad sobre el historial de DATALAKE, con exportación CSV reproducible.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — pipeline real de ingesta CAN/WebSocket hacia DATALAKE, con deduplicación de secuencia.

*Gateway Industrial*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — hub de integración que retransmite a protocolos industriales, con una capa real de lista blanca de comandos/contrapresión.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — espacio de direcciones OPC-UA real, verificado con una sesión de cliente de protocolo binario real.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — broker MQTT real con autenticación por cliente opcional y ACLs de tema.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — endpoints XML reales `/probe` y `/current` de MTConnect con salida en modo degradado.

*Herramientas Complementarias y Operaciones del Ecosistema*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — paneles de Resúmenes Inteligentes y Resaltado de Anomalías sobre DATALAKE/ANOMALY-DETECTOR, con un respaldo estadístico honesto.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI de flota con un contrato de código de salida real y estable, un cliente en vivo genuino de la propia API de HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app compañera WearOS con alertas hápticas reales y un relé de voz al teléfono emparejado.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware para un rack de montaje de placas con decodificación real de ID de herramienta y lógica de precalentamiento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware más un compañero de visión en Python real para un cabezal de inspección térmica/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — herramienta administrativa de escritorio que descubre, clona y actualiza cada repo de este ecosistema, y el origen de la propia capa visual Qt Quick de este proyecto.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — herramienta de escritorio Windows/Linux que construye una imagen de CM5 lista para flashear precargada con las versiones más actuales del ecosistema, con configuración de primer arranque Wi-Fi/usuario/SSH al estilo Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinador de incidencias de mantenimiento: un rol de borde de bajo privilegio recoge una instantánea saneada de inventario/salud, un rol de plano de control la muestra en solo lectura y pide a un proveedor de IA que sugiera un diagnóstico - nunca aplica un parche ni despliega nada.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — host de desarrollo reproducible (Raspberry Pi 5 / CM5) que almacena el código fuente del ecosistema y ejecuta tareas de build/test acotadas bajo una cola durable; un rol de desarrollo dedicado, explícitamente no una CM5 operativa.

---

## 📚 Documentación y Comunidad

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - cada subcomando real de `--cli`, argumento por argumento.
- [`CHANGELOG.md`](CHANGELOG.md) - qué se ha entregado realmente, versión por versión.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)**
Email: `electrohobby3d@gmail.com`
YouTube: [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENCIA

GPL-3.0 - ver [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md).
