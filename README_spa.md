<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Desktop editor for the STL model libraries of HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 📦 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | 🇪🇸 <b>Español</b> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 📦 Explora y Edita las Librerías de Modelos STL Reales del Ecosistema HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="Core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="Desktop">
  <img src="https://img.shields.io/badge/Tests-237%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.1.9-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-scaffolding-FFB020.svg" alt="Maturity">
</p>

---

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
real de ámbito de sesión donde hace falta (`pytest tests/`, 237 casos en
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

> **Estado de seguridad física y de ciberseguridad:** este ecosistema no es un sistema de seguridad certificado. Todavía no existe una ruta de E-STOP por hardware, ni límites ni enclavamientos aplicados por el firmware, ni un comando de movimiento verificado; las imágenes de firmware se comprueban con CRC-32 y una firma Ed25519, y una compilación de versión rechaza las claves de desarrollo publicadas (los cabezales de herramienta y las placas de expansión detrás del relé siguen con cargadores de URTC, que usan un HMAC-SHA256 de clave compartida en lugar de una firma); TLS y TLS mutuo son opcionales y están desactivados por defecto; aún no se ha poblado ni probado ninguna placa propia. Lee la [línea base de seguridad](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) y el [modelo de amenazas](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) antes de fiarte de cualquier afirmación de aquí para la seguridad de una persona.

---

## 📋 De un vistazo

| | |
|---|---|
| Versión | `0.1.9` |
| Madurez | Andamiaje |
| Tests | 237 (`python -m pytest tests -q`) |
| Tecnología | Python / PySide6 / Qt Quick / numpy-stl |
| Destino | El PC de quien lo usa |
| En hardware real | No aplica: nada de esto se ejecuta en hardware |

**Ir a:** [Resumen](#-resumen) · [Arquitectura](#-arquitectura) · [Seguridad y protección](#-seguridad-y-protección) · [Interfaces](#-interfaces) · [Configuración](#-configuración) · [Inicio rápido](#-inicio-rápido) · [Pruebas](#-pruebas) · [Resolución de problemas](#-resolución-de-problemas) · [Estructura del repositorio](#-estructura-del-repositorio) · [Proyectos relacionados](#-proyectos-relacionados)

## 🚦 Estado del proyecto

Cada línea es una parte de este repositorio y la luz dice hasta dónde llega hoy. Se escribe con lo que el repositorio puede demostrar (pruebas, compilaciones, ejecuciones), no con lo previsto.

🟢 Hecho y verificado · 🟡 Funciona, con límites conocidos · 🟠 Hecho a medias o sin verificar · 🔴 Sin hacer o sin funcionar

| Área | Estado | Qué significa aquí |
|---|---|---|
| Software | 🟠 | Solo estructura y primeras piezas; falta la mayor parte del trabajo |
| Pruebas | 🟡 | 237 pruebas automáticas, ejecutadas en cada cambio |
| Hardware real | 🟡 | No aplica: nada de esto se ejecuta en hardware |
| Documentación | 🟡 | README en ocho idiomas, comprobado contra el manifiesto en cada cambio |

## 🎯 Resumen

HYDRA-UMC-EDITOR-STL es una pequeña herramienta de escritorio - GUI de
ventana por defecto, CLI completa con `--cli` - para editar las piezas
STL reales que forman cada modelo de robot/máquina que HYDRA-UMC-STUDIO
y HYDRA-UMC-SUITE distribuyen. Ambas apps reorganizaron sus propias
carpetas de modelos en la misma estructura real de categorías
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
- **Vista montada** - los robots, CNC, PnP y laser se abren ya montados en su pose de reposo (leída de la cinemática de HYDRA-UMC-SUITE junto a este checkout, solo visualización); un botón de la barra cambia a las piezas sin montar para editarlas.

**Límites del envío y de la transformación:** solo se suben las piezas `.stl` (las demás se notifican), todo el envío debe caber en el límite de 50 MB de petición del servidor y el modelo solo se guarda en el catálogo del servidor (HYDRA-UMC-STUDIO aún no lo lee). La pose identidad es correcta para piezas independientes (camas calientes, racks, mesas de vacío); las piezas de un robot o máquina están en su propio marco de eslabón, así que llegan apiladas en el origen y sin articulaciones. Usa preferiblemente un host `https://` (o `HYDRA_UMC_PASSWORD` / la petición de contraseña en lugar de `--password`). Una transformación primero escala, luego rota en X, Y y Z y por último traslada; la rotación es alrededor del origen del archivo, no del centro de la pieza.

**Nunca se borra nada de forma permanente.** Un "quitar" o un
"reemplazar" mueve primero el fichero original real a la propia
subcarpeta `.trash/` de ese modelo - la misma disciplina de "nunca
destruir, mover a un lado" que ya siguen las convenciones internas de
trabajo de este ecosistema, aplicada aquí como una funcionalidad real
del producto, no solo como un hábito interno.

## 🧩 Papel en HYDRA-UMC

**HYDRA-UMC-EDITOR-STL** es la herramienta de escritorio que edita las piezas STL reales de cada modelo de robot y máquina que incluyen HYDRA-UMC-STUDIO y HYDRA-UMC-SUITE. Lee sus dos carpetas de modelos tal cual, muestra un modelo en un visor Qt Quick 3D, y transforma, recolorea, reemplaza, quita o añade una pieza en disco, apartando el original en lugar de borrarlo. Un modelo terminado se puede enviar al catálogo de modelos de un HYDRA-UMC-SERVER.

## 🏛️ Arquitectura

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-EDITOR-STL architecture" width="100%">
</p>

### ARQUITECTURA Y DECISIONES DE DISEÑO

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

## 🔒 Seguridad y protección

| Amenaza | Defensa | Dónde |
|---|---|---|
| Perder una pieza al reemplazarla o quitarla | El original se mueve primero a la carpeta `.trash/` del modelo y nunca se borra; se puede restaurar, y vaciar la papelera exige una confirmación explícita | `stl_ops.py` |
| Un fichero que no es un STL, o un nombre de pieza que sale de la carpeta del modelo | Un reemplazo o adición se analiza primero y se rechaza si no tiene triángulos o está truncado; el nombre de una pieza debe ser un nombre `.stl` simple dentro de la carpeta del modelo; una transformación que daría vértices no finitos no cambia nada | `stl_ops.py`, `mesh_check.py` |
| La contraseña del servidor en el historial de la shell o en la lista de procesos | `--password` no se recomienda; sin él la contraseña se lee de `HYDRA_UMC_PASSWORD` o se pide sin eco; un servidor `https://` evita enviarla en claro | `main.py`, `catalog_push.py` |
| Una subida demasiado grande o que se queda colgada | La subida completa debe caber en 49 MiB (el límite del servidor es 50 MB) y cada petición tiene un límite de 20 s; solo se envían las piezas `.stl` y se informa de las demás | `catalog_push.py` |
| Registros que crecen o guardan datos | Un único registro rotativo en la carpeta personal de 256 KiB con dos copias | `diagnostics.py` |

**Lo que nunca hace:** editar nada fuera de las carpetas de modelos que le indiques, ni borrar una pieza para siempre. El envío a un servidor se escribió contra su contrato documentado y no se ha probado con un servidor real.

El envío de un modelo de robot o máquina a un catálogo se rechaza por defecto, porque sus piezas llegarían apiladas en el origen; solo pasan las categorías de piezas independientes (camas, racks). El rechazo explica el motivo y se informa de las piezas que no son `.stl`.

## 🔌 Interfaces

| Topic o ruta | Qué lleva |
|---|---|
| `--cli categories \| models \| parts <library> [...]` | lista lo que hay: las categorías, los modelos de una categoría, los ficheros de piezas de un modelo (`--json` para máquinas); la biblioteca es `studio` o `suite` |
| `--cli transform <library> <category> <model> <part> [--tx --ty --tz --rx --ry --rz --scale]` | traslada, rota y escala una pieza en su sitio: escala primero, luego rota sobre X, Y y Z, y después traslada, respecto al origen del fichero |
| `--cli replace \| remove \| add` | reemplaza una pieza por otro STL, mueve una a `.trash/` o trae un STL nuevo (`--dest-filename` lo renombra) |
| `--cli push <library> <category> <model> --host --username` | envía las piezas editables de un modelo a `POST /api/models/submit` de un servidor (inicio de sesión de administrador; `--port` 3000 por defecto, `--server-category`, `--overwrite`) |
| `--root <folder>` | la raíz del ecosistema que contiene `HYDRA-UMC-STUDIO` y `HYDRA-UMC-SUITE` juntos; por defecto, la carpeta padre de esta herramienta |

`--allow-stacked-push` en `--cli push` y la casilla **Forzar** de la ventana de envío (apagada por defecto, en los ocho idiomas) dejan enviar al catálogo un modelo de robot o máquina aunque sus piezas lleguen apiladas en el origen.

## ⚙️ Configuración

No hay servidor ni fichero de configuración que editar a mano: la ventana recuerda sus elecciones en un fichero y cada modelo guarda sus colores en un fichero lateral.

| Variable | Por defecto | Qué fija |
|---|---|---|
| `~/.hydra_umc_editor_stl_settings.json` | ninguno | la raíz del ecosistema y el idioma elegido en la ventana, recordados entre arranques |
| `part_colors.json` (in each model folder) | `#9fb4c9` | el color de cada pieza; un STL binario no lleva ninguno, y STUDIO y SUITE leen el mismo fichero |
| `HYDRA_UMC_PASSWORD` | sin definir | la contraseña del servidor para `--cli push`, para que no vaya en la línea de órdenes |
| `~/.hydra_umc_editor_stl.log` | 256 KiB x 3 | el registro rotativo de la ventana y la línea de órdenes |

## 🚀 Inicio rápido

Requiere Python 3.10 o superior. La primera línea crea un entorno virtual con el extra de la interfaz y ejecuta las comprobaciones y las pruebas; Windows tiene `build.bat` y `run.bat`.

```bash
./build.sh                                    # creates .venv, installs the package with the GUI extra, checks and tests
./run.sh                                      # the windowed editor
./run.sh --cli categories studio              # lists the categories of the STUDIO library (use suite for the SUITE one)
./run.sh --cli parts studio robots-6-dof ar3  # lists the part files of one model
```

## 🧪 Pruebas

237 pruebas automáticas se ejecutan con `python -m pytest tests -q`. No necesitan hardware ni nada fuera de esta máquina.

El CI ejecuta `HYDRA_UMC_CI=1 python tools/ci_validate.py`, que comprueba el manifiesto, los documentos, los ocho README y las imágenes.

## 🏗️ Compilación y publicación

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
./run.sh --cli lite studio robots-6-dof ar3 --ratio 0.2          # copias más ligeras en .lite/ (los originales no se tocan)
./run.sh --cli diff studio robots-6-dof ar3 base_link.STL --svg diff.svg   # comparar con la versión guardada en .trash/
./run.sh --cli sync-libraries --master studio --target suite   # solo el plan; con --apply se escribe, no se borra nada
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

En Windows: `build.bat`, luego `run.bat` (GUI) o `run.bat --cli ...` /
doble clic en `run-gui.vbs` para lanzar la GUI sin consola.

`library` siempre es `studio` o `suite`; `category`/`model` son los
nombres reales de carpeta que acaban de imprimir `categories`/`models`.
`--root` sobreescribe la raíz del ecosistema para cualquier comando
`--cli` (por defecto: el directorio padre propio de esta herramienta).

## 🩺 Resolución de problemas

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

| Ves | Porque | Haz |
|---|---|---|
| «El envío tuvo éxito pero el servidor no devolvió identificador», o un error de inicio de sesión | El servidor rechazó la cuenta (el envío necesita un administrador), no es un HYDRA-UMC-SERVER o respondió algo que no es un objeto JSON | Usa una cuenta de administrador de un HYDRA-UMC-SERVER real, con su dirección y puerto |
| «la transformación produciría vértices no finitos (¿demasiado grande?): no se cambió nada» | La escala o la traslación es tan grande que los números ya no caben en un decimal de 32 bits | Usa valores menores |
| «vaciar la papelera exige una confirmación explícita» | Nada se borra para siempre si no lo confirmas | Restaura la entrada desde `.trash/`, o confirma el vaciado en la ventana |

## 📂 Estructura del repositorio

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-EDITOR-STL" width="100%">
</p>

<details>
<summary>Versión en texto del árbol</summary>

```text
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/   código fuente
│   ├── __init__.py             Versión del paquete
│   ├── model_catalog.py        Descubrimiento real, de solo lectura, de ambas librerías de modelos
│   ├── stl_ops.py              Mutación real de STL: transformar/reemplazar/quitar/añadir, copias de seguridad en .trash/
│   ├── catalog_push.py         URDF de ensamblaje + cliente HTTP para POST /api/models/submit
│   ├── settings.py             Raíz del ecosistema e idioma persistidos
│   ├── i18n.py                 Traducciones reales y completas de la GUI (8 idiomas)
│   ├── diagnostics.py          Registro rotativo en la carpeta personal y guarda de los slots de la ventana
│   ├── qt_gui.py               Puente Qt Quick sobre el núcleo real model_catalog.py/stl_ops.py
│   ├── qml/Main.qml            Capa visual de escritorio, compartida con HYDRA-UMC-UPDATER
│   ├── main.py                 Despacho: GUI por defecto, --cli para categories/models/parts/transform/replace/remove/add/push
│   ├── assembly.py             La vista ensamblada (pose de inicio) de una máquina a partir de sus piezas STL
│   ├── mesh_check.py           Comprobaciones de la malla antes de subirla al catálogo
│   ├── decimate.py             Una copia más ligera de una pieza
│   ├── mesh_diff.py            El antes y el después de una pieza, en cifras y en imagen
│   ├── library_sync.py         Pone una biblioteca de modelos al día con la otra
│   ├── part_colors.py          Anotaciones de color por pieza (un STL binario no trae las suyas)
│   └── stl_geometry.py         Los triángulos reales de un fichero STL como geometría de Qt Quick 3D
├── tests/                      Tests reales contra ficheros STL reales generados
├── docs/                       documentos del proyecto
├── images/                     Recursos multimedia e iconos de la app
├── tools/                      herramientas del proyecto y comprobaciones del CI
├── .github/                    flujo de CI y plantillas de incidencias
├── build.sh / build.bat        venv + instalación editable (extras dev+gui) + comprobación de compilación + tests
├── run.sh / run.bat            GUI por defecto / punto de entrada de la CLI
├── run-gui.vbs                 Lanzador gráfico para Windows sin ventana de consola
├── bump_version.py             Incremento de versión tipo cuentakilómetros (solo lo ejecuta el comando `bump` explícito)
├── bump_manifest_version.py    Sincroniza la versión de hydra-umc.project.json con la nativa (--sync)
├── CHANGELOG.md                qué cambió en cada versión
├── build-test.sh               comprobación de compilación sin cambios
├── hydra-umc.project.json      manifiesto: versión, madurez, familia
├── pyproject.toml              metadatos del paquete
└── test.sh                     comprobación de compilación sin cambios
```

</details>

## 🗺️ Hoja de ruta y límites conocidos

**Límites conocidos hoy**

- Un ejecutable de GUI independiente empaquetado (PyInstaller, siguiendo
  la misma convención `build_exe.bat`/`.sh` de HYDRA-UMC-SUITE).
- Deshacer/rehacer sobre el propio historial `.trash/` de una sesión, en
  vez de una restauración manual de ficheros.

## 🌍 Idiomas

Este README y los documentos del repositorio existen en ocho idiomas: inglés, español, alemán, francés, italiano, japonés, chino y portugués (Portugal). Se escriben a la vez y el CI comprueba que los ocho ficheros tengan las mismas secciones y los mismos enlaces.

## 🔗 Proyectos relacionados

Este proyecto forma parte del ecosistema de robótica HYDRA-UMC del mismo autor (JuanenRac / Electro Hobby 3D). Vale la pena conocerlo, ya que una petición podría en realidad ser sobre uno de estos en vez de sobre este repositorio.

**Proyecto Padre**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — dueño de una de las dos librerías de modelos reales que este editor lee y escribe (`public/models/`).

**Directamente Relacionados**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — dueño de la segunda librería de modelos real que este editor lee y escribe (`assets/meshes/`), mantenida en exactamente la misma estructura de categorías que la de STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — editor de escritorio hermano para el lado URDF/cinemática del mismo catálogo de modelos, en vez de la geometría STL cruda que edita esta herramienta.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — dueño del endpoint real `POST /api/models/submit` al que este editor envía sus ediciones terminadas (`catalog_push.py`, "Enviar al servidor..." en la GUI o `--cli push`).

**También Forman Parte del Ecosistema**

*Hardware y Plataforma Central*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — el diseño de la placa madre del brazo robótico: host CM5 + coprocesador STM32H745 de doble núcleo, pensado para coordinar hasta 8 brazos herramienta por CAN-OTA/SPI-OTA (firmware en fase temprana; todavía no hay ninguna placa poblada).
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — capa de producto Raspberry Pi OS reproducible para la CM5: agente de solo lectura, config/perfiles validados, aprovisionamiento WiFi de primer contacto.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — el contrato JSON-Schema compartido y la barrera de software de puerta de trabajos contra la que cada bridge valida sus comandos (no es una función de seguridad certificada).
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registro declarativo de manifiestos de adaptadores y su validador para conectores de máquinas externas; extiende la idea de contrato del SDK a máquinas externas sin reemplazar los proyectos de gateway industrial.

*Backend Central y Clientes*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app de control nativa de Android con login biométrico y una compañera Wear OS emparejada.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app de control iOS/iPadOS (Flutter) con sincronización WebSocket en tiempo real.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — UI táctil nativa para la pantalla táctil DSI de 7" integrada en la propia CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creador/editor gráfico de escritorio de URDF con carga de fuente desde GitHub/local y edición con vista previa 3D en vivo.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — barrera de coordinación para flotas AGV/AMR mediante un publicador MQTT VDA 5050 (probado solo contra una flota emulada).
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinador de alto nivel para celdas CNC con acceso a estado/bytes de control GRBL (probado solo contra un emulador).
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — barrera de coordinación para droides con patas/humanoides, con un emisor de comandos para Boston Dynamics Spot (probado solo contra un emulador).
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinador de celdas láser que lee 3 señales GPIO de llave/carcasa/enclavamiento (probado solo contra un chip simulado; no puede armar ni disparar un láser).
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinador seguro de alto nivel del flujo de placas para pick-and-place de OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — límite de coordinación seguro para impresoras 3D Moonraker/Klipper, con comandos de trabajo reales con puerta de control.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinador con un transporte ROS 2 rclpy importado de forma perezosa (todavía no ejecutado contra una instalación de ROS 2).
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — barrera de coordinación para UAV equipados con cámara, con un emisor de comandos MAVLink (probado solo contra un emulador).

*Plataforma de Herramientas URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware para la PCB física del Universal Robot Tool Controller, más de 25 perfiles de herramienta por bus CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — herramienta GUI de escritorio para flashear placas URTC, CAN-OTA más SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — herramienta de diagnóstico CAN en vivo de escritorio para placas URTC, un panel por perfil de herramienta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basada en navegador a URTC-TESTER vía la Web Serial API, sin instalación local.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — pasarela delante del bus CAN de URTC: lista de identificadores permitidos, límite de tasa y clave de sesión; software probado en ordenador, aún no en un bus real.

*Nodo de Visión IA (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub de integración para el pipeline de visión Hailo-8, con una comprobación real de preparación de hardware por etapa.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registro real de modelos compilados con verificación de carga segura por arquitectura/checksum de Hailo.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — generador real de pipeline GStreamer + config de MediaMTX con un límite de integración HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — ley de corrección Position-Based Visual Servoing con autorización condicionada al estado de zona; todavía sin estimación de pose por cámara.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — lógica v0 de invasión de zona, vigencia de calibración y solicitud de E-STOP que toma las posiciones de los objetos de un fichero; ningún detector la alimenta y todavía no hay un E-STOP físico conectado.

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
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — enrutador hardware-in-the-loop con un enclavamiento de software por colisión entre simulación y hardware real (probado sin hardware real).

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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app compañera de WearOS con patrones de alerta háptica y un relé de voz al teléfono emparejado (todavía no ejecutada en un reloj físico).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware para un rack de montaje de placas con decodificación real de ID de herramienta y lógica de precalentamiento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware más un compañero de visión en Python real para un cabezal de inspección térmica/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — herramienta administrativa de escritorio que descubre, clona y actualiza cada repo de este ecosistema, y el origen de la propia capa visual Qt Quick de este proyecto.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — herramienta de escritorio Windows/Linux que construye una imagen de CM5 lista para flashear precargada con las versiones más actuales del ecosistema, con configuración de primer arranque Wi-Fi/usuario/SSH al estilo Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinador de incidencias de mantenimiento: un rol de borde de bajo privilegio recoge una instantánea saneada de inventario/salud, un rol de plano de control la muestra en solo lectura y pide a un proveedor de IA que sugiera un diagnóstico - nunca aplica un parche ni despliega nada.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — host de desarrollo reproducible (Raspberry Pi 5 / CM5) que almacena el código fuente del ecosistema y ejecuta tareas de build/test acotadas bajo una cola durable; un rol de desarrollo dedicado, explícitamente no una CM5 operativa.

## 📚 Documentación

Dónde leer más:

* [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - cada subcomando real de `--cli`, argumento por argumento.
* [Base de seguridad del ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modelo de amenazas del ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Historial de cambios de este repositorio](CHANGELOG.md)
* [Licencia de este repositorio](LICENSE.md)

## 🤝 Contribuir y comunidad

* Antes de un pull request ejecuta `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (o `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): debe imprimir `CI_VALIDATION=PASS`. No ejecutes `build.sh` ni `build.bat` para esta comprobación; compilar no es comprobar.
* Los ocho README se escriben desde una sola fuente en HYDRA-UMC-DOCS; no los edites a mano. Cambia la fuente y vuelve a escribirlos con `tools/make_readmes.py`.
* No afirmes en un README lo que no se ha ejecutado: di «simulado» o «sin probar en hardware» cuando esa sea la verdad.
* Mira [CONTRIBUTING.md](CONTRIBUTING.md), el [código de conducta](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) y [SUPPORT.md](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENCIA

GPL-3.0-or-later - [LICENSE](LICENSE).
