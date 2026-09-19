<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="Banner di HYDRA-UMC-EDITOR-STL" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | 🇮🇹 <b>Italiano</b> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a></p>

### 📦 Sfoglia e Modifica le Vere Librerie di Modelli STL dell'Ecosistema HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/Licenza-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/Linguaggio-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Nucleo-numpy--stl-brightgreen.svg" alt="nucleo numpy-stl">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="GUI desktop PySide6 Qt Quick">
</p>

> **v0.0.3.** Il vero nucleo CLI/GUI descritto sotto è realmente
> implementato e testato, incluso un vero visualizzatore 3D Qt Quick 3D
> con selezione al clic, colore per pezzo, trasforma, sostituisci,
> rimuovi e aggiungi. Non invia ancora un pezzo modificato al vero
> catalogo `POST /api/models/submit` di HYDRA-UMC-SERVER (come fa invece
> HYDRA-UMC-EDITOR-URDF per i modelli URDF), né propaga il colore
> salvato di un pezzo ai visualizzatori 3D live di STUDIO/SUITE -
> entrambe sono vero lavoro futuro delimitato (vedi ROADMAP), non date
> per scontate in silenzio.

**Controllo di onestà - cosa funziona davvero oggi:**
`model_catalog.py` (scoperta reale, in sola lettura, di entrambe le
librerie di modelli), `stl_ops.py` (mutazione STL reale via
`numpy-stl` - trasforma/sostituisci/rimuovi/aggiungi, più
`model_bounds()` per l'inquadratura della fotocamera del visualizzatore
3D), `part_colors.py` (vero file laterale di colore per pezzo) e
`stl_geometry.py` (vero caricamento di geometria Qt Quick 3D) sono
tutti testati contro veri file STL generati e una vera
`QGuiApplication` con ambito di sessione dove serve (`pytest tests/`,
41 casi superati) e sono stati verificati end-to-end contro i veri
checkout `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` di questo ecosistema
(`--cli categories`/`models`/`parts` contro gli alberi reali;
`transform`/`remove` contro una copia usa e getta, mai il vero
checkout). Anche il vero `EditorBridge` di `qt_gui.py` è testato
direttamente (lo slot del colore, la selezione preservata dopo un
cambio di colore). `qml/Main.qml` si carica e si renderizza senza
errori QML (verificato senza interfaccia con
`QT_QPA_PLATFORM=offscreen`, anche con le parti reali di un modello
caricate nel visualizzatore 3D), ma il grafo di scena QML in sé non ha
un test automatizzato proprio - guidare un vero ciclo di eventi Qt non
viene tentato qui, lo stesso limite di onestà che il proprio README di
HYDRA-UMC-UPDATER traccia già per il proprio strato Qt Quick.

---

## 1. 🛠️ PANORAMICA TECNICA

HYDRA-UMC-EDITOR-STL è un piccolo strumento desktop - GUI a finestra per
impostazione predefinita, CLI completa con `--cli` - per modificare i
veri pezzi STL che compongono ogni modello di robot/macchina distribuito
da HYDRA-UMC-STUDIO e HYDRA-UMC-SUITE. Entrambe le app hanno
riorganizzato le proprie cartelle di modelli nel 2026-09 nella stessa
vera struttura di categorie (`robots-5-dof`/`robots-6-dof`/
`robots-7-dof`, `machine-pnp`/`machine-cnc`/`machine-laser`,
`heatedbeds`/`racks`/`vacuum-tables`, ogni modello con il proprio
`metadata.json` accanto al proprio `ATTRIBUTION.txt`) - questo
strumento legge quella stessa struttura reale, non una copia separata
né un proprio database.

Un vero visualizzatore 3D Qt Quick 3D mostra ogni pezzo modificabile
del modello selezionato (`stl_geometry.py`, un vero `QQuick3DGeometry`
che carica i triangoli di ogni pezzo direttamente dal suo file STL) -
trascina per orbitare, rotella per zoomare, clicca su un pezzo per
selezionarlo (vero `View3D.pick()`, non una stima). La fotocamera si
inquadra da sola sul vero bounding box combinato del modello
(`model_bounds()` di `stl_ops.py`), così una base robot da 400mm e una
vite da 5mm si inquadrano entrambe correttamente.

Cinque operazioni reali, ciascuna sostenuta da vera I/O di file contro
il vero checkout su disco:

- **Trasformare** - traslare/ruotare/scalare i veri vertici di un pezzo
  (via `numpy-stl`, la stessa libreria da cui già dipende
  `render/mesh.py` di HYDRA-UMC-SUITE) e salvarlo di nuovo nello stesso
  posto.
- **Cambiare colore** - una vera annotazione di colore per pezzo
  (`part_colors.json`, un file laterale di proprietà di questo
  strumento) mostrata nella vista 3D - un STL binario non porta un
  colore proprio affidabile, e nemmeno i visualizzatori di STUDIO/SUITE
  di questo ecosistema interpretano quella convenzione, quindi oggi è
  un'anteprima onesta solo di EDITOR-STL, non ancora propagata ai loro
  visualizzatori 3D live.
- **Sostituire** - sovrascrivere un pezzo con un altro vero file STL.
- **Rimuovere** - togliere un pezzo da un modello.
- **Aggiungere** - portare un nuovo vero file STL in un modello.

**Niente viene mai eliminato in modo permanente.** Una rimozione o una
sostituzione sposta prima il vero file originale nella propria
sottocartella `.trash/` di quel modello - la stessa disciplina "mai
distruggere, spostare da parte" già seguita dalle convenzioni di lavoro
interne di questo ecosistema, applicata qui come una vera funzionalità
di prodotto, non solo come un'abitudine interna.

## 2. 🧱 ARCHITETTURA E DECISIONI DI PROGETTAZIONE

- **Due vere librerie, un solo modulo di scoperta.** La propria
  costante `LIBRARIES` di `model_catalog.py` nomina i due veri alberi
  che questo strumento modifica (`HYDRA-UMC-STUDIO/public/models/`,
  `HYDRA-UMC-SUITE/assets/meshes/`) - aggiungere una terza libreria in
  seguito significa aggiungere una voce lì, non una seconda
  implementazione di scoperta.
- **`stl_ops.py` è l'unico posto che modifica mai un file.**
  `model_catalog.py` resta rigorosamente in sola lettura; sia `--cli`
  che il ponte Qt Quick chiamano esattamente le stesse funzioni
  `transform_part()`/`replace_part()`/`remove_part()`/`add_part()`,
  quindi la GUI non può mai fare nulla che la CLI stessa non potrebbe
  fare.
- **Un vero STL, non solo un nome file che finisce in `.stl`.**
  `is_real_stl()` analizza davvero un candidato alla sostituzione/
  aggiunta con `numpy-stl` prima che venga mai copiato in una vera
  cartella di modello - e, una vera lacuna trovata scrivendo i propri
  test di questo progetto, rifiuta anche un risultato di analisi con
  **0 triangoli**: il proprio percorso di riserva ASCII di `numpy-stl`
  non solleva un'eccezione su byte spazzatura arbitrari, li analizza
  silenziosamente come una mesh vuota, quindi un semplice try/except da
  solo avrebbe lasciato passare un file che non è affatto un STL.
- **GUI Qt Quick per impostazione predefinita, `--cli` per sistemi
  senza schermo.** `main.py` importa PySide6 solo sul percorso non
  `--cli`, quindi `--cli categories`/`models`/`parts`/`transform`/
  `replace`/`remove`/`add` funzionano su una macchina senza schermo né
  runtime Qt installato affatto.
- **Lo stesso vero strato visivo di HYDRA-UMC-UPDATER.** `qml/Main.qml`
  riutilizza testualmente i propri componenti `GameButton`/`GameCombo`/
  `SectionPanel` di quel progetto e il suo tema scuro ciano/blu/ambra/
  rosso, su esplicita richiesta del proprietario del progetto - un
  nuovo strumento PC in questo ecosistema deve sembrare lo stesso
  strumento, non uno progettato a parte.
- **Radice dell'ecosistema, non un percorso fisso.** Come la propria
  radice di workspace di HYDRA-UMC-UPDATER, la directory padre di
  questo stesso progetto è il valore predefinito
  (`default_ecosystem_root()` di `main.py`), sempre sovrascrivibile
  (`--root` su `--cli`, "Sfoglia" nella GUI) e ricordata tra i
  lanci della GUI (`settings.py`).

## 📂 STRUTTURA DELLE DIRECTORY

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # Scoperta reale, in sola lettura, di entrambe le librerie di modelli
│   ├── stl_ops.py           # Mutazione STL reale: trasforma/sostituisci/rimuovi/aggiungi, backup in .trash/
│   ├── settings.py          # Radice dell'ecosistema e lingua persistite
│   ├── i18n.py               # Traduzioni reali e complete della GUI (7 lingue)
│   ├── qt_gui.py             # Ponte Qt Quick sul vero nucleo model_catalog.py/stl_ops.py
│   ├── qml/Main.qml          # Guscio desktop a tema, condiviso con HYDRA-UMC-UPDATER
│   └── main.py               # Smistamento: GUI per impostazione predefinita, --cli per categories/models/parts/transform/replace/remove/add
├── tests/                    # Veri test contro veri file STL generati
├── docs/
│   └── CLI_REFERENCE.md      # Riferimento dei comandi
├── images/                   # Media e icone dell'app
├── tools/
│   ├── build_test.py         # Controllo di compilazione senza toccare le versioni
│   └── ci_validate.py        # Validazione manifest/CHANGELOG/docs usata dalla CI
├── build.sh / build.bat      # venv + installazione editabile (extra dev+gui) + controllo compilazione + test
├── run.sh / run.bat          # GUI predefinita / punto di ingresso CLI
├── run-gui.vbs               # Launcher grafico Windows senza finestra console
├── bump_version.py           # Incremento "odometro" a livello di ecosistema (pyproject.toml + __init__.py)
└── bump_manifest_version.py  # Sincronizza la versione di hydra-umc.project.json con quella nativa (--sync)
```

## ⚙️ GUIDA A COMPILAZIONE ED ESECUZIONE

```bash
chmod +x build.sh   # una sola volta
./build.sh          # crea .venv, pip install -e ".[dev,gui]", compila e testa
./run.sh                                                    # GUI a finestra (predefinita)
./run.sh --cli categories studio                            # elenca le categorie in una libreria
./run.sh --cli models studio robots-6-dof                   # elenca i modelli in una categoria
./run.sh --cli parts studio robots-6-dof ar3                 # elenca i veri file di pezzi di un modello
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /percorso/nuovo.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /percorso/nuovo.stl
```

Su Windows: `build.bat`, poi `run.bat` (GUI) o `run.bat --cli ...` /
doppio clic su `run-gui.vbs` per un lancio della GUI senza console.

`library` è sempre `studio` o `suite`; `category`/`model` sono i veri
nomi di cartella appena stampati da `categories`/`models`. `--root`
sovrascrive la radice dell'ecosistema per qualsiasi comando `--cli`
(predefinito: la propria directory padre di questo strumento).

**Risoluzione dei problemi**

- `categories`/`models`/`parts` non stampa nulla: la radice
  dell'ecosistema in realtà non contiene `HYDRA-UMC-STUDIO`/
  `HYDRA-UMC-SUITE` come fratelli - passa `--root` esplicitamente, o
  usa "Sfoglia" nella GUI.
- `transform`/`replace`/`add` fallisce con "not a real, parseable STL
  file": il file sorgente in realtà non è un STL valido (o ne è uno da
  0 triangoli) - aprilo in un vero visualizzatore CAD/mesh per
  confermarlo.
- Un pezzo rimosso/sostituito non è scomparso dalla propria lista pezzi
  della GUI: è stato davvero spostato in `.trash/` su disco - la lista
  pezzi mostra solo i veri file attuali di primo livello, e una
  sottocartella `.trash/` ne è deliberatamente esclusa.

## 🚀 ROADMAP

- Inviare un pezzo modificato/aggiunto al vero endpoint
  `POST /api/models/submit` di HYDRA-UMC-SERVER, lo stesso vero punto
  di integrazione già usato da HYDRA-UMC-EDITOR-URDF per i modelli
  URDF.
- Propagare il colore salvato di un pezzo (`part_colors.json`, vedi
  sopra) ai visualizzatori 3D live di HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE -
  vero lavoro separato, multi-repository.
- Un eseguibile GUI standalone impacchettato (PyInstaller, seguendo la
  stessa convenzione `build_exe.bat`/`.sh` di HYDRA-UMC-SUITE).
- Annulla/ripeti sulla propria cronologia `.trash/` di una sessione,
  invece di un ripristino manuale dei file.

## 🔗 Progetti Correlati

Questo progetto fa parte dell'ecosistema robotico HYDRA-UMC dello stesso autore (JuanenRac / Electro Hobby 3D). Utile da sapere, poiché una richiesta potrebbe in realtà riguardare uno di questi invece di questo repository.

**Progetto Padre**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — proprietario di una delle due vere librerie di modelli che questo editor legge e scrive (`public/models/`).

**Direttamente Correlati**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — proprietario della seconda vera libreria di modelli che questo editor legge e scrive (`assets/meshes/`), mantenuta esattamente nella stessa struttura di categorie di quella di STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — editor desktop gemello per il lato URDF/cinematica dello stesso catalogo di modelli, invece della geometria STL grezza che modifica questo strumento.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — proprietario del vero endpoint `POST /api/models/submit` a cui questo editor è previsto invii le proprie modifiche completate (vedi ROADMAP - non ancora collegato nella v0.0.1).

**Fa Anche Parte dell'Ecosistema**

*Hardware e Piattaforma Centrale*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la scheda madre fisica del braccio robotico: host CM5 + STM32H745 dual-core, che orchestra fino a 8 bracci utensile via CAN-OTA/SPI-OTA.
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — strato prodotto Raspberry Pi OS riproducibile per la CM5: agente in sola lettura, config/profili validati, provisioning WiFi al primo contatto.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — il contratto JSON-Schema condiviso e il confine di gate di sicurezza contro cui ogni bridge valida i propri comandi.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registro dichiarativo di manifest di adattatori e il suo validatore per connettori di macchine esterne; estende l'idea di contratto dell'SDK alle macchine esterne senza sostituire i progetti di gateway industriale.

*Backend Centrale e Client*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app di controllo Android nativa con login biometrico e una compagna Wear OS abbinata.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app di controllo iOS/iPadOS (Flutter) con sincronizzazione WebSocket in tempo reale.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — UI touch nativa per lo schermo touch DSI da 7" integrato sulla CM5 stessa.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creatore/editor grafico desktop per URDF con caricamento da sorgente GitHub/locale e modifica con anteprima 3D dal vivo.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — confine di coordinamento per flotte AGV/AMR via un vero publisher MQTT VDA 5050.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinatore di cella CNC di alto livello con vero accesso a stato/byte di controllo GRBL.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — confine di coordinamento per droidi con zampe/umanoidi, con un vero mittente di comandi Boston Dynamics Spot.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinatore di sicurezza cella laser che legge 3 vere protezioni GPIO chiave/involucro/interblocco.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinatore sicuro di alto livello del flusso schede per il pick-and-place OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — confine di coordinamento sicuro per stampanti 3D Moonraker/Klipper, con veri comandi di lavoro a gate controllato.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinatore di sicurezza con un vero trasporto ROS 2 rclpy importato pigramente.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — confine di coordinamento per UAV dotati di fotocamera, con un vero mittente di comandi MAVLink.

*Piattaforma Strumenti URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware per la scheda PCB fisica dell'Universal Robot Tool Controller, oltre 25 profili strumento su bus CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — strumento GUI desktop per flashare schede URTC, CAN-OTA più SWD/JTAG a chip intero.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — strumento di diagnostica bus CAN dal vivo desktop per schede URTC, un pannello per profilo strumento.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basata su browser a URTC-TESTER via la Web Serial API, senza installazione locale.

*Nodo Visione IA (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub di integrazione per la pipeline di visione Hailo-8, con un vero controllo di prontezza hardware per fase.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — vero registro di modelli compilati con verifica di caricamento sicuro per architettura/checksum Hailo.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — vero generatore di pipeline GStreamer + config MediaMTX con un vero confine di integrazione HailoRT.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — vera legge di correzione Position-Based Visual Servoing, con gate di sicurezza sullo stato di zona a monte.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — vero controllo di violazione zona e richiesta E-STOP, con imposizione di freschezza della calibrazione.

*Nodo Cognitivo IA (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — hub di integrazione per la pipeline cognitiva Hailo-10 (orchestrazione LLM/VLA/voce).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — vera codifica/decodifica di token d'azione e generazione di traiettoria per un modello Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — vero frontend vocale (VAD + parser di intenti) con un relay Watch limitato e soggetto a conferma.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — vera scomposizione di task basata su regole e recupero semantico di errori sui codici di errore del MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — vera ricerca di documenti TF-IDF solo stdlib sui propri doc Markdown di questo ecosistema.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — tecnico di manutenzione IA locale, con gate di policy, per l'ecosistema stesso - osserva, diagnostica e propone correzioni; i due livelli di rischio più alti sono deliberatamente non ancora implementati.

*Orchestrazione e Sciame*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — hub di integrazione con un vero contratto gRPC/Protobuf di report di salute e una macchina a stati di missione.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — vera coda di lavori basata su priorità con deduplicazione, su una vera API HTTP.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vero watchdog di salute della flotta basato su gRPC con retry/backoff e rilevamento di discordanza di identità.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — vero pianificatore di percorso 3D basato su RRT con validazione reale di collisione ostacolo/spazio di lavoro.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — vera sincronizzazione di stato CRDT LWW-Element-Map, testata per proprietà per la convergenza multi-cella.

*Gemello Digitale e Simulazione*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — vero gemello digitale di simulazione fisica, che consuma i modelli URDF prodotti da HYDRA-UMC-EDITOR-URDF.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — consuma questi stessi modelli URDF per la propria simulazione fisica.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — genera dati di addestramento da questi stessi modelli.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — vero interblocco di sicurezza hardware-in-the-loop che instrada comandi tra simulazione e hardware reale.

*Dati e Analisi*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — vero archivio di serie temporali basato su sqlite3 con una vera API HTTP di ingestione/query.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — vero rilevatore di anomalie FFT + baseline statistica con monitoraggio della deriva.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — vero calcolo di OEE/disponibilità sulla cronologia DATALAKE, con esportazione CSV riproducibile.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — vera pipeline di ingestione CAN/WebSocket verso DATALAKE, con deduplicazione di sequenza.

*Gateway Industriale*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — hub di integrazione che inoltra a protocolli industriali, con un vero strato di whitelist comandi/contropressione.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — vero spazio di indirizzi OPC-UA, verificato con una vera sessione client di protocollo binario.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — vero broker MQTT con autenticazione per client opzionale e ACL sui topic.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — veri endpoint XML `/probe` e `/current` di MTConnect con output in modalità degradata.

*Strumenti Complementari e Operazioni dell'Ecosistema*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — pannelli di Riepiloghi Intelligenti ed Evidenziazione Anomalie su DATALAKE/ANOMALY-DETECTOR, con un ripiego statistico onesto.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI di flotta con un vero contratto di codice di uscita stabile, un vero client dal vivo della propria API di HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app compagna WearOS con vere allerte aptiche e un relay vocale al telefono abbinato.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware per un rack di montaggio schede con vera decodifica ID strumento e logica di pre-riscaldamento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware più un vero compagno di visione Python per una testa di ispezione termica/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — strumento amministrativo desktop che scopre, clona e aggiorna ogni repo di questo ecosistema, e l'origine del proprio strato visivo Qt Quick di questo progetto.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — strumento desktop Windows/Linux che costruisce un'immagine CM5 pronta da flashare precaricata con le versioni più attuali dell'ecosistema, con configurazione Wi-Fi/utente/SSH al primo avvio in stile Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinatore di incidenti di manutenzione: un ruolo edge a basso privilegio raccoglie uno snapshot sanificato di inventario/salute, un ruolo control-plane lo mostra in sola lettura e chiede a un provider IA di suggerire una diagnosi - non applica mai una patch né distribuisce nulla.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — host di sviluppo riproducibile (Raspberry Pi 5 / CM5) che archivia il codice sorgente dell'ecosistema ed esegue task di build/test limitati sotto una coda durevole; un ruolo di sviluppo dedicato, esplicitamente non una CM5 operativa.

---

## 📚 Documentazione e Comunità

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - ogni vero sottocomando di `--cli`, argomento per argomento.
- [`CHANGELOG.md`](CHANGELOG.md) - cosa è stato realmente consegnato, versione per versione.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md).

## 👤 AUTORE

**JuanenRac (Electro Hobby 3D)**
Email: `electrohobby3d@gmail.com`
YouTube: [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENZA

GPL-3.0 - vedi [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md).
