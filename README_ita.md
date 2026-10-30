<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Desktop editor for the STL model libraries of HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 📦 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | 🇮🇹 <b>Italiano</b> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 📦 Sfoglia e Modifica le Vere Librerie di Modelli STL dell'Ecosistema HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="Core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="Desktop">
  <img src="https://img.shields.io/badge/Tests-222%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.1.7-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-scaffolding-FFB020.svg" alt="Maturity">
</p>

---

**Controllo di onestà - cosa funziona davvero oggi:**
`model_catalog.py` (scoperta reale, in sola lettura, di entrambe le
librerie di modelli), `stl_ops.py` (mutazione STL reale via
`numpy-stl` - trasforma/sostituisci/rimuovi/aggiungi, più
`model_bounds()` per l'inquadratura della fotocamera del visualizzatore
3D), `part_colors.py` (vero file laterale di colore per pezzo),
`stl_geometry.py` (vero caricamento di geometria Qt Quick 3D) e
`catalog_push.py` (vera generazione di un URDF di assemblaggio più un
vero client HTTP per `POST /api/models/submit`) sono
tutti testati contro veri file STL generati e una vera
`QGuiApplication` con ambito di sessione dove serve (`pytest tests/`,
222 casi superati) e sono stati verificati end-to-end contro i veri
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

> **Stato di sicurezza (safety e security):** questo ecosistema non è un sistema di sicurezza certificato. Non esiste ancora un percorso E-STOP hardware, né limiti o interblocchi imposti dal firmware, né un comando di movimento verificato; le immagini firmware sono controllate con CRC-32 e una firma Ed25519, e una compilazione di rilascio rifiuta le chiavi di sviluppo pubblicate (le teste utensile e le schede di espansione dietro il relè usano ancora i bootloader di URTC, che accettano un HMAC-SHA256 a chiave condivisa invece di una firma); TLS e TLS reciproco sono opzionali e disattivati per impostazione predefinita; nessuna scheda propria è stata ancora assemblata o provata. Leggi la [base di sicurezza](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) e il [modello delle minacce](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) prima di fidarti di qualsiasi affermazione qui per la sicurezza di una persona.

---

## 📋 In breve

| | |
|---|---|
| Versione | `0.1.7` |
| Maturità | Impalcatura |
| Test | 222 (`python -m pytest tests -q`) |
| Tecnologia | Python / PySide6 / Qt Quick / numpy-stl |
| Destinazione | Il PC di chi lo usa |
| Su hardware reale | Non applicabile: nulla qui gira su hardware |

**Vai a:** [Panoramica](#-panoramica) · [Architettura](#-architettura) · [Sicurezza e protezione](#-sicurezza-e-protezione) · [Interfacce](#-interfacce) · [Configurazione](#-configurazione) · [Avvio rapido](#-avvio-rapido) · [Test](#-test) · [Risoluzione dei problemi](#-risoluzione-dei-problemi) · [Struttura del repository](#-struttura-del-repository) · [Progetti correlati](#-progetti-correlati)

## 🚦 Stato del progetto

Ogni riga è una parte di questo repository e il semaforo dice a che punto è oggi. È scritta in base a ciò che il repository può mostrare (test, compilazioni, esecuzioni), non a ciò che è previsto.

🟢 Fatto e verificato · 🟡 Funziona, con limiti noti · 🟠 Fatto a metà o non ancora verificato · 🔴 Non fatto o non funzionante

| Area | Stato | Cosa significa qui |
|---|---|---|
| Software | 🟠 | Solo struttura e primi pezzi; gran parte del lavoro è ancora da fare |
| Test | 🟢 | 222 test automatici, eseguiti a ogni modifica |
| Hardware reale | 🟢 | Non applicabile: nulla qui gira su hardware |
| Documentazione | 🟢 | README in otto lingue, verificato rispetto al manifesto a ogni modifica |

## 🎯 Panoramica

HYDRA-UMC-EDITOR-STL è un piccolo strumento desktop - GUI a finestra per
impostazione predefinita, CLI completa con `--cli` - per modificare i
veri pezzi STL che compongono ogni modello di robot/macchina distribuito
da HYDRA-UMC-STUDIO e HYDRA-UMC-SUITE. Entrambe le app hanno
riorganizzato le proprie cartelle di modelli nella stessa
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

Sei operazioni reali, ciascuna sostenuta da vera I/O di file contro
il vero checkout su disco:

- **Trasformare** - traslare/ruotare/scalare i veri vertici di un pezzo
  (via `numpy-stl`, la stessa libreria da cui già dipende
  `render/mesh.py` di HYDRA-UMC-SUITE) e salvarlo di nuovo nello stesso
  posto.
- **Cambiare colore** - una vera annotazione di colore per pezzo
  (`part_colors.json`, un file laterale di proprietà di questo
  strumento) mostrata nella vista 3D - un STL binario non porta un
  colore proprio affidabile, quindi questo file laterale è la vera fonte
  di verità. Il proprio `hooks/usePartColors.ts` di HYDRA-UMC-STUDIO e il
  proprio `render/part_colors.py` di HYDRA-UMC-SUITE rileggono questo
  stesso file, quindi un colore salvato qui raggiunge anche i loro
  visualizzatori 3D live, non solo l'anteprima di questo strumento.
- **Sostituire** - sovrascrivere un pezzo con un altro vero file STL.
- **Rimuovere** - togliere un pezzo da un modello.
- **Aggiungere** - portare un nuovo vero file STL in un modello.
- **Invia al server** - invia i pezzi modificabili attuali del modello
  selezionato al vero catalogo di invio modelli di un HYDRA-UMC-SERVER in
  esecuzione (`catalog_push.py`, `POST /api/models/submit` - richiede un
  accesso amministratore, come la funzionalità equivalente di
  HYDRA-UMC-EDITOR-URDF). Poiché il contratto di quell'endpoint è
  pensato per URDF, questo avvolge i pezzi nel più piccolo URDF reale
  che accetta: un link radice più un link figlio non articolato
  (`fixed`) per pezzo, dato che la posizione reale di ogni pezzo è già
  incorporata nei propri vertici STL - mai una posa inventata.
- **Barra mobile del visualizzatore** - Seleziona, Sposta (un vero gizmo a 3 assi trascinabile), Modifica (ruota/scala), Colore, Aggiungi, Elimina, Fissa (salva in modo permanente spostamento/rotazione/scala), Copia, Incolla e Taglia, direttamente nella vista 3D. Piani riscaldati, tavoli a vuoto e rack sono varianti di dimensione indipendenti: il visualizzatore mostra solo quella selezionata invece di sovrapporle.
- **Vista assemblata** - robot, CNC, PnP e laser si aprono già assemblati nella posa di riposo (letta dalla cinematica di HYDRA-UMC-SUITE accanto a questo checkout, solo visualizzazione); un pulsante della barra passa ai pezzi grezzi per modificarli.

**Limiti dell'invio e della trasformazione:** vengono caricate solo le parti `.stl` (le altre vengono segnalate), l'intero invio deve rientrare nel limite di richiesta di 50 MB del server e il modello viene salvato solo nel catalogo del server (HYDRA-UMC-STUDIO non lo legge ancora). La posa identità è corretta per parti indipendenti (piani riscaldati, rack, tavoli a vuoto); le parti di un robot o di una macchina sono salvate nel proprio sistema di riferimento del link, quindi vengono inviate nella loro posizione di posa iniziale secondo la cinematica di HYDRA-UMC-SUITE, fisse e senza giunti (impilate nell'origine solo se quel posizionamento non è noto). Preferisci un host `https://` (o `HYDRA_UMC_PASSWORD` / la richiesta della password invece di `--password`). Una trasformazione scala prima, poi ruota attorno a X, Y e Z e infine trasla; la rotazione è attorno all'origine del file, non al centro della parte.

**Niente viene mai eliminato in modo permanente.** Una rimozione o una
sostituzione sposta prima il vero file originale nella propria
sottocartella `.trash/` di quel modello - la stessa disciplina "mai
distruggere, spostare da parte" già seguita dalle convenzioni di lavoro
interne di questo ecosistema, applicata qui come una vera funzionalità
di prodotto, non solo come un'abitudine interna.

## 🧩 Ruolo in HYDRA-UMC

**HYDRA-UMC-EDITOR-STL** è lo strumento desktop che modifica le vere parti STL di ogni modello di robot e macchina fornito da HYDRA-UMC-STUDIO e HYDRA-UMC-SUITE. Legge le loro due cartelle di modelli così come sono, mostra un modello in un visualizzatore Qt Quick 3D, e trasforma, ricolora, sostituisce, rimuove o aggiunge una parte su disco, mettendo da parte l'originale invece di cancellarlo. Un modello finito può essere inviato al catalogo dei modelli di un HYDRA-UMC-SERVER.

## 🏛️ Architettura

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-EDITOR-STL architecture" width="100%">
</p>

### ARCHITETTURA E DECISIONI DI PROGETTAZIONE

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

## 🔒 Sicurezza e protezione

| Minaccia | Difesa | Dove |
|---|---|---|
| Perdere una parte quando viene sostituita o rimossa | L'originale viene prima spostato nella cartella `.trash/` del modello e mai cancellato; il ripristino è possibile e svuotare il cestino richiede una conferma esplicita | `stl_ops.py` |
| Un file che non è uno STL, o un nome di parte che esce dalla cartella del modello | Una sostituzione o aggiunta viene prima analizzata e rifiutata se non ha triangoli o è troncata; il nome di una parte deve essere un semplice nome `.stl` dentro la cartella del modello; una trasformazione che darebbe vertici non finiti non cambia nulla | `stl_ops.py`, `mesh_check.py` |
| La password del server nella cronologia della shell o nell'elenco dei processi | `--password` non è consigliato; senza di esso la password viene letta da `HYDRA_UMC_PASSWORD` o chiesta senza eco; un host `https://` evita di inviarla in chiaro | `main.py`, `catalog_push.py` |
| Un caricamento troppo grande o che si blocca | L'intero caricamento deve stare in 49 MiB (il limite del server è 50 MB) e ogni richiesta ha un limite di 20 s; si inviano solo le parti `.stl` e le altre vengono segnalate | `catalog_push.py` |
| Registri che crescono o contengono dati | Un solo registro a rotazione nella cartella home di 256 KiB con due copie | `diagnostics.py` |

**Cosa non fa mai:** modificare nulla fuori dalle cartelle dei modelli che gli indichi, né cancellare una parte per sempre. L'invio a un server è stato scritto sul suo contratto documentato e non è stato provato su un server reale.

Un modello di robot o macchina va al catalogo con ogni parte nella sua posizione di posa iniziale, presa dalla cinematica di `HYDRA-UMC-SUITE` accanto a questo checkout (lo stesso posizionamento della vista assemblata); i giunti restano fissi. Se quel posizionamento non è noto per il modello, l'invio viene rifiutato, perché le sue parti arriverebbero impilate nell'origine; le parti indipendenti (piani, rack) passano sempre. Il rifiuto spiega il motivo e le parti che non sono `.stl` vengono segnalate.

## 🔌 Interfacce

| Topic o rotta | Cosa porta |
|---|---|
| `--cli categories \| models \| parts <library> [...]` | elenca ciò che c'è: le categorie, i modelli di una categoria, i file delle parti di un modello (`--json` per le macchine); la libreria è `studio` o `suite` |
| `--cli transform <library> <category> <model> <part> [--tx --ty --tz --rx --ry --rz --scale]` | trasla, ruota e scala una parte sul posto: prima scala, poi ruota attorno a X, Y e Z, poi trasla, rispetto all'origine del file |
| `--cli replace \| remove \| add` | sostituisce una parte con un altro STL, ne sposta una in `.trash/`, o porta un nuovo STL (`--dest-filename` lo rinomina) |
| `--cli push <library> <category> <model> --host --username` | invia le parti modificabili di un modello a `POST /api/models/submit` di un server (accesso da amministratore; `--port` 3000 per impostazione predefinita, `--server-category`, `--overwrite`) |
| `--root <folder>` | la radice dell'ecosistema che contiene `HYDRA-UMC-STUDIO` e `HYDRA-UMC-SUITE` affiancati; per impostazione predefinita, la cartella padre di questo strumento |

`--allow-stacked-push` su `--cli push` e la casella **Forza** della finestra di invio (spenta per impostazione predefinita, negli otto idiomi) permettono di inviare al catalogo un modello di robot o macchina anche se il posizionamento iniziale delle sue parti non è noto e arrivano impilate nell'origine.

## ⚙️ Configurazione

Non c'è un server né un file di configurazione da modificare a mano: la finestra ricorda le sue scelte in un file e ogni modello conserva i suoi colori in un file accessorio.

| Variabile | Predefinito | Cosa imposta |
|---|---|---|
| `~/.hydra_umc_editor_stl_settings.json` | nessuno | la radice dell'ecosistema e la lingua scelta nella finestra, ricordate tra gli avvii |
| `part_colors.json` (in each model folder) | `#9fb4c9` | il colore di ogni parte; uno STL binario non ne ha, e STUDIO e SUITE leggono lo stesso file |
| `HYDRA_UMC_PASSWORD` | non impostata | la password del server per `--cli push`, così non compare nella riga di comando |
| `~/.hydra_umc_editor_stl.log` | 256 KiB x 3 | il registro a rotazione della finestra e della riga di comando |

## 🚀 Avvio rapido

Richiede Python 3.10 o successivo. La prima riga crea un ambiente virtuale con l'extra dell'interfaccia ed esegue i controlli e i test; Windows ha `build.bat` e `run.bat`.

```bash
./build.sh                                    # creates .venv, installs the package with the GUI extra, checks and tests
./run.sh                                      # the windowed editor
./run.sh --cli categories studio              # lists the categories of the STUDIO library (use suite for the SUITE one)
./run.sh --cli parts studio robots-6-dof ar3  # lists the part files of one model
```

## 🧪 Test

222 test automatici si eseguono con `python -m pytest tests -q`. Non richiedono hardware né nulla al di fuori di questa macchina.

La CI esegue `HYDRA_UMC_CI=1 python tools/ci_validate.py`, che controlla il manifesto, i documenti, gli otto README e le immagini.

## 🏗️ Compilazione e rilascio

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
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

Su Windows: `build.bat`, poi `run.bat` (GUI) o `run.bat --cli ...` /
doppio clic su `run-gui.vbs` per un lancio della GUI senza console.

`library` è sempre `studio` o `suite`; `category`/`model` sono i veri
nomi di cartella appena stampati da `categories`/`models`. `--root`
sovrascrive la radice dell'ecosistema per qualsiasi comando `--cli`
(predefinito: la propria directory padre di questo strumento).

## 🩺 Risoluzione dei problemi

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

| Vedi | Perché | Fai |
|---|---|---|
| «L'invio è riuscito ma il server non ha restituito alcuno slug», o un errore di accesso | Il server ha rifiutato l'account (l'invio richiede un amministratore), non è un HYDRA-UMC-SERVER o ha risposto qualcosa che non è un oggetto JSON | Usa un account amministratore di un vero HYDRA-UMC-SERVER, con il suo indirizzo e la sua porta |
| «la trasformazione produrrebbe vertici non finiti (troppo grande?): non è stato cambiato nulla» | La scala o la traslazione è così grande che i numeri non entrano più in un float a 32 bit | Usa valori più piccoli |
| «svuotare il cestino richiede una conferma esplicita» | Nulla viene cancellato per sempre se non lo confermi | Ripristina la voce da `.trash/`, o conferma lo svuotamento nella finestra |

## 📂 Struttura del repository

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-EDITOR-STL" width="100%">
</p>

<details>
<summary>Versione testuale dell'albero</summary>

```text
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/   codice sorgente
│   ├── __init__.py             Versione del pacchetto
│   ├── model_catalog.py        Scoperta reale, in sola lettura, di entrambe le librerie di modelli
│   ├── stl_ops.py              Mutazione STL reale: trasforma/sostituisci/rimuovi/aggiungi, backup in .trash/
│   ├── catalog_push.py         URDF di assemblaggio + client HTTP per POST /api/models/submit
│   ├── settings.py             Radice dell'ecosistema e lingua persistite
│   ├── i18n.py                 Traduzioni reali e complete della GUI (8 lingue)
│   ├── diagnostics.py          Registro a rotazione nella cartella personale e protezione degli slot della finestra
│   ├── qt_gui.py               Ponte Qt Quick sul vero nucleo model_catalog.py/stl_ops.py
│   ├── qml/Main.qml            Guscio desktop a tema, condiviso con HYDRA-UMC-UPDATER
│   ├── main.py                 Smistamento: GUI per impostazione predefinita, --cli per categories/models/parts/transform/replace/remove/add/push
│   ├── assembly.py             La vista assemblata (posa iniziale) di una macchina a partire dai suoi pezzi STL
│   ├── mesh_check.py           Controlli della mesh prima dell'invio al catalogo
│   ├── part_colors.py          Annotazioni di colore per pezzo (un STL binario non ne porta di proprie)
│   └── stl_geometry.py         I triangoli reali di un file STL come geometria Qt Quick 3D
├── tests/                      Veri test contro veri file STL generati
├── docs/                       documenti del progetto
├── images/                     Media e icone dell'app
├── tools/                      strumenti del progetto e controlli della CI
├── .github/                    workflow di CI e modelli di segnalazione
├── build.sh / build.bat        venv + installazione editabile (extra dev+gui) + controllo compilazione + test
├── run.sh / run.bat            GUI predefinita / punto di ingresso CLI
├── run-gui.vbs                 Launcher grafico Windows senza finestra console
├── bump_version.py             Incremento di versione stile contachilometri (eseguito solo dal comando `bump` esplicito)
├── bump_manifest_version.py    Sincronizza la versione di hydra-umc.project.json con quella nativa (--sync)
├── CHANGELOG.md                cosa è cambiato in ogni versione
├── build-test.sh               controllo di build senza modifiche
├── hydra-umc.project.json      manifesto: versione, maturità, famiglia
├── pyproject.toml              metadati del pacchetto
└── test.sh                     controllo di build senza modifiche
```

</details>

## 🗺️ Roadmap e limiti noti

**Limiti noti oggi**

- Un eseguibile GUI standalone impacchettato (PyInstaller, seguendo la
  stessa convenzione `build_exe.bat`/`.sh` di HYDRA-UMC-SUITE).
- Annulla/ripeti sulla propria cronologia `.trash/` di una sessione,
  invece di un ripristino manuale dei file.

## 🌍 Lingue

Questo README e i documenti del repository esistono in otto lingue: inglese, spagnolo, tedesco, francese, italiano, giapponese, cinese e portoghese (Portogallo). Sono scritti insieme e la CI verifica che gli otto file abbiano le stesse sezioni e gli stessi link.

## 🔗 Progetti correlati

Questo progetto fa parte dell'ecosistema robotico HYDRA-UMC dello stesso autore (JuanenRac / Electro Hobby 3D). Utile da sapere, poiché una richiesta potrebbe in realtà riguardare uno di questi invece di questo repository.

**Progetto Padre**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — proprietario di una delle due vere librerie di modelli che questo editor legge e scrive (`public/models/`).

**Direttamente Correlati**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — proprietario della seconda vera libreria di modelli che questo editor legge e scrive (`assets/meshes/`), mantenuta esattamente nella stessa struttura di categorie di quella di STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — editor desktop gemello per il lato URDF/cinematica dello stesso catalogo di modelli, invece della geometria STL grezza che modifica questo strumento.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — proprietario del vero endpoint `POST /api/models/submit` a cui questo editor invia le proprie modifiche completate (`catalog_push.py`, "Invia al server..." nella GUI o `--cli push`).

**Fa Anche Parte dell'Ecosistema**

*Hardware e Piattaforma Centrale*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — il progetto della scheda madre del braccio robotico: host CM5 + coprocessore STM32H745 dual-core, pensato per coordinare fino a 8 bracci utensile via CAN-OTA/SPI-OTA (firmware in fase iniziale; nessuna scheda assemblata per ora).
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — strato prodotto Raspberry Pi OS riproducibile per la CM5: agente in sola lettura, config/profili validati, provisioning WiFi al primo contatto.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — il contratto JSON-Schema condiviso e la barriera software di controllo dei job contro cui ogni bridge valida i propri comandi (non è una funzione di sicurezza certificata).
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registro dichiarativo di manifest di adattatori e il suo validatore per connettori di macchine esterne; estende l'idea di contratto dell'SDK alle macchine esterne senza sostituire i progetti di gateway industriale.

*Backend Centrale e Client*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app di controllo Android nativa con login biometrico e una compagna Wear OS abbinata.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app di controllo iOS/iPadOS (Flutter) con sincronizzazione WebSocket in tempo reale.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — UI touch nativa per lo schermo touch DSI da 7" integrato sulla CM5 stessa.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creatore/editor grafico desktop per URDF con caricamento da sorgente GitHub/locale e modifica con anteprima 3D dal vivo.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — barriera di coordinamento per flotte AGV/AMR tramite un publisher MQTT VDA 5050 (testato solo contro una flotta emulata).
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinatore ad alto livello per celle CNC con accesso a stato/byte di controllo GRBL (testato solo contro un emulatore).
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — barriera di coordinamento per droidi con zampe/umanoidi, con un mittente di comandi per Boston Dynamics Spot (testato solo contro un emulatore).
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinatore per celle laser che legge 3 segnali GPIO di chiave/involucro/interblocco (testato solo contro un chip simulato; non può armare né far partire un laser).
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinatore sicuro di alto livello del flusso schede per il pick-and-place OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — confine di coordinamento sicuro per stampanti 3D Moonraker/Klipper, con veri comandi di lavoro a gate controllato.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinatore con un trasporto ROS 2 rclpy importato in modo lazy (non ancora eseguito contro un'installazione ROS 2).
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — barriera di coordinamento per UAV dotati di fotocamera, con un mittente di comandi MAVLink (testato solo contro un emulatore).

*Piattaforma Strumenti URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware per la scheda PCB fisica dell'Universal Robot Tool Controller, oltre 25 profili strumento su bus CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — strumento GUI desktop per flashare schede URTC, CAN-OTA più SWD/JTAG a chip intero.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — strumento di diagnostica bus CAN dal vivo desktop per schede URTC, un pannello per profilo strumento.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basata su browser a URTC-TESTER via la Web Serial API, senza installazione locale.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — gateway davanti al bus CAN di URTC: elenco di identificatori consentiti, limite di frequenza e chiave di sessione; software provato su computer, non ancora su un bus reale.

*Nodo Visione IA (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub di integrazione per la pipeline di visione Hailo-8, con un vero controllo di prontezza hardware per fase.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — vero registro di modelli compilati con verifica di caricamento sicuro per architettura/checksum Hailo.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — vero generatore di pipeline GStreamer + config MediaMTX con un vero confine di integrazione HailoRT.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — legge di correzione Position-Based Visual Servoing con autorizzazione condizionata allo stato di zona; ancora nessuna stima di posa da telecamera.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — logica v0 di violazione zona, freschezza di calibrazione e richiesta E-STOP che legge le posizioni degli oggetti da un file; nessun rilevatore la alimenta e nessun E-STOP fisico è ancora collegato.

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
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — router hardware-in-the-loop con un interblocco software di collisione tra simulazione e hardware reale (testato senza hardware reale).

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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app companion WearOS con schemi di avviso aptico e un relay vocale verso il telefono abbinato (non ancora eseguita su un orologio fisico).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware per un rack di montaggio schede con vera decodifica ID strumento e logica di pre-riscaldamento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware più un vero compagno di visione Python per una testa di ispezione termica/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — strumento amministrativo desktop che scopre, clona e aggiorna ogni repo di questo ecosistema, e l'origine del proprio strato visivo Qt Quick di questo progetto.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — strumento desktop Windows/Linux che costruisce un'immagine CM5 pronta da flashare precaricata con le versioni più attuali dell'ecosistema, con configurazione Wi-Fi/utente/SSH al primo avvio in stile Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinatore di incidenti di manutenzione: un ruolo edge a basso privilegio raccoglie uno snapshot sanificato di inventario/salute, un ruolo control-plane lo mostra in sola lettura e chiede a un provider IA di suggerire una diagnosi - non applica mai una patch né distribuisce nulla.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — host di sviluppo riproducibile (Raspberry Pi 5 / CM5) che archivia il codice sorgente dell'ecosistema ed esegue task di build/test limitati sotto una coda durevole; un ruolo di sviluppo dedicato, esplicitamente non una CM5 operativa.

## 📚 Documentazione

Dove leggere di più:

* [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - ogni vero sottocomando di `--cli`, argomento per argomento.
* [Base di sicurezza dell'ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modello delle minacce dell'ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Registro delle modifiche di questo repository](CHANGELOG.md)
* [Licenza di questo repository](LICENSE.md)

## 🤝 Contribuire e comunità

* Prima di una pull request esegui `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (oppure `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): deve stampare `CI_VALIDATION=PASS`. Non eseguire `build.sh` né `build.bat` per questa verifica; compilare non è verificare.
* I otto README sono scritti da un'unica fonte in HYDRA-UMC-DOCS; non modificarli a mano. Cambia la fonte e riscrivili con `tools/make_readmes.py`.
* Non affermare in un README ciò che non è stato eseguito: scrivi «simulato» o «non provato su hardware» quando è la verità.
* Vedi [CONTRIBUTING.md](CONTRIBUTING.md), il [codice di condotta](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) e [SUPPORT.md](SUPPORT.md).

## 👤 AUTORE

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENZA

GPL-3.0-or-later - [LICENSE](LICENSE).
