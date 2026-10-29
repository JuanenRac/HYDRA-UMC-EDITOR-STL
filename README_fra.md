<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Desktop editor for the STL model libraries of HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 📦 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | 🇫🇷 <b>Français</b> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 📦 Parcourir et Éditer les Vraies Bibliothèques de Modèles STL de l'Écosystème HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="Core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="Desktop">
  <img src="https://img.shields.io/badge/Tests-215%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.1.7-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-scaffolding-FFB020.svg" alt="Maturity">
</p>

---

**Vérification d'honnêteté - ce qui fonctionne vraiment aujourd'hui :**
`model_catalog.py` (découverte réelle, en lecture seule, des deux
bibliothèques de modèles), `stl_ops.py` (mutation STL réelle via
`numpy-stl` - transformer/remplacer/retirer/ajouter, plus
`model_bounds()` pour le cadrage de caméra de la visionneuse 3D),
`part_colors.py` (vrai fichier annexe de couleur par pièce),
`stl_geometry.py` (vrai chargement de géométrie Qt Quick 3D) et
`catalog_push.py` (vraie génération d'un URDF d'assemblage plus un vrai
client HTTP pour `POST /api/models/submit`) sont tous
testés contre de vrais fichiers STL générés et une vraie
`QGuiApplication` à portée de session quand nécessaire (`pytest tests/`,
215 cas réussis) et ont été vérifiés de bout en bout contre les vrais
checkouts `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` de cet écosystème
(`--cli categories`/`models`/`parts` contre les vrais arbres ;
`transform`/`remove` contre une copie jetable, jamais le vrai checkout).
Le propre `EditorBridge` de `qt_gui.py` est aussi testé directement (le
slot de couleur, la sélection préservée après un changement de
couleur). `qml/Main.qml` se charge et s'affiche sans erreur QML
(vérifié sans interface avec `QT_QPA_PLATFORM=offscreen`, y compris
avec les vraies pièces d'un modèle chargées dans la visionneuse 3D),
mais le graphe de scène QML lui-même n'a pas de test automatisé propre -
piloter une vraie boucle d'événements Qt n'est pas tenté ici, la même
limite d'honnêteté que le propre README de HYDRA-UMC-UPDATER trace déjà
pour sa propre couche Qt Quick.

---

> **État de la sûreté et de la cybersécurité :** cet écosystème n'est pas un système de sécurité certifié. Il n'existe pas encore de chaîne d'E-STOP matérielle, ni de limites ou de verrouillages imposés par le firmware, ni de commande de mouvement vérifiée ; les images de firmware sont contrôlées par CRC32 et un HMAC-SHA256 à clé partagée, pas par une signature asymétrique ; TLS et TLS mutuel sont optionnels et désactivés par défaut ; aucune carte propre n'a encore été assemblée ni testée. Lisez la [base de sécurité](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) et le [modèle de menaces](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) avant de vous fier à une affirmation d'ici pour la sécurité d'une personne.

---

## 📋 En un coup d'œil

| | |
|---|---|
| Version | `0.1.7` |
| Maturité | Ébauche |
| Tests | 215 (`python -m pytest tests -q`) |
| Technologie | Python / PySide6 / Qt Quick / numpy-stl |
| Cible | Le PC de la personne qui l'utilise |
| Sur matériel réel | Sans objet : rien ici ne s'exécute sur du matériel |

**Aller à :** [Présentation](#-présentation) · [Architecture](#-architecture) · [Sécurité et protection](#-sécurité-et-protection) · [Interfaces](#-interfaces) · [Configuration](#-configuration) · [Démarrage rapide](#-démarrage-rapide) · [Tests](#-tests) · [Dépannage](#-dépannage) · [Structure du dépôt](#-structure-du-dépôt) · [Projets liés](#-projets-liés)

## 🚦 État du projet

Chaque ligne est une partie de ce dépôt et le feu dit où elle en est aujourd'hui. Elle est écrite d'après ce que le dépôt peut montrer (tests, compilations, exécutions), pas d'après ce qui est prévu.

🟢 Fait et vérifié · 🟡 Fonctionne, avec des limites connues · 🟠 À moitié fait ou pas encore vérifié · 🔴 Pas fait ou ne fonctionne pas

| Domaine | État | Ce que cela veut dire ici |
|---|---|---|
| Logiciel | 🟠 | Seulement la structure et les premières pièces ; l'essentiel du travail reste à faire |
| Tests | 🟢 | 215 tests automatiques, exécutés à chaque modification |
| Matériel réel | 🟢 | Sans objet : rien ici ne s'exécute sur du matériel |
| Documentation | 🟢 | README en huit langues, vérifié par rapport au manifeste à chaque modification |

## 🎯 Présentation

HYDRA-UMC-EDITOR-STL est un petit outil de bureau - GUI fenêtrée par
défaut, CLI complète avec `--cli` - pour éditer les vraies pièces STL
qui composent chaque modèle de robot/machine que distribuent
HYDRA-UMC-STUDIO et HYDRA-UMC-SUITE. Les deux applications ont
réorganisé leurs propres dossiers de modèles dans la même
vraie structure de catégories (`robots-5-dof`/`robots-6-dof`/
`robots-7-dof`, `machine-pnp`/`machine-cnc`/`machine-laser`,
`heatedbeds`/`racks`/`vacuum-tables`, chaque modèle avec son propre
`metadata.json` à côté de son `ATTRIBUTION.txt`) - cet outil lit cette
même structure réelle, pas une copie séparée ni une base de données
propre.

Une vraie visionneuse 3D Qt Quick 3D affiche chaque pièce modifiable du
modèle sélectionné (`stl_geometry.py`, un vrai `QQuick3DGeometry` qui
charge les triangles de chaque pièce directement depuis son fichier
STL) - glisser pour orbiter, molette pour zoomer, cliquer sur une pièce
pour la sélectionner (vrai `View3D.pick()`, pas une estimation). La
caméra se cadre elle-même sur la vraie boîte englobante combinée du
modèle (`model_bounds()` de `stl_ops.py`), pour qu'une base de robot de
400mm et une vis de 5mm soient toutes deux cadrées correctement.

Six opérations réelles, chacune adossée à de vraies E/S fichier
contre le vrai checkout sur disque :

- **Transformer** - translater/pivoter/mettre à l'échelle les vrais
  sommets d'une pièce (via `numpy-stl`, la même bibliothèque dont
  dépend déjà `render/mesh.py` de HYDRA-UMC-SUITE) et la sauvegarder au
  même endroit.
- **Changer la couleur** - une vraie annotation de couleur par pièce
  (`part_colors.json`, un fichier annexe propre à cet outil) affichée
  dans la vue 3D - un STL binaire ne porte aucune couleur fiable qui lui
  soit propre, donc ce fichier annexe est la vraie source de vérité. Le
  propre `hooks/usePartColors.ts` de HYDRA-UMC-STUDIO et le propre
  `render/part_colors.py` de HYDRA-UMC-SUITE relisent ce même fichier,
  donc une couleur enregistrée ici atteint aussi leurs vraies
  visionneuses 3D, pas seulement l'aperçu de cet outil.
- **Remplacer** - écraser une pièce avec un autre vrai fichier STL.
- **Retirer** - sortir une pièce d'un modèle.
- **Ajouter** - apporter un nouveau vrai fichier STL à un modèle.
- **Envoyer au serveur** - soumettre les pièces modifiables actuelles du
  modèle sélectionné au vrai catalogue de soumission de modèles d'un
  HYDRA-UMC-SERVER en cours d'exécution (`catalog_push.py`,
  `POST /api/models/submit` - identifiants administrateur requis, comme
  la fonctionnalité équivalente de HYDRA-UMC-EDITOR-URDF). Comme le
  contrat de cet endpoint est pensé pour l'URDF, ceci enveloppe les
  pièces dans le plus petit URDF réel qu'il accepte : un lien racine plus
  un lien enfant non articulé (`fixed`) par pièce, puisque la position
  réelle de chaque pièce est déjà intégrée dans ses propres sommets STL -
  jamais une pose inventée.
- **Barre flottante du visualiseur** - Sélectionner, Déplacer (un vrai gizmo 3 axes déplaçable), Modifier (rotation/échelle), Couleur, Ajouter, Supprimer, Fixer (enregistre définitivement le déplacement/rotation/échelle), Copier, Coller et Couper, directement dans la vue 3D. Les plateaux chauffants, tables à vide et racks sont des variantes de taille indépendantes : le visualiseur n'affiche que celle sélectionnée au lieu de les empiler.
- **Vue assemblée** - les robots, CNC, PnP et lasers s'ouvrent déjà assemblés dans leur pose de repos (lue depuis la cinématique de HYDRA-UMC-SUITE à côté de ce checkout, affichage seul) ; un bouton de la barre bascule vers les pièces brutes pour les modifier.

**Limites de l'envoi et de la transformation :** seules les pièces `.stl` sont envoyées (les autres sont signalées), l'envoi complet doit tenir dans la limite de requête de 50 Mo du serveur, et le modèle n'est stocké que dans le catalogue du serveur (HYDRA-UMC-STUDIO ne le lit pas encore). La pose identité convient aux pièces indépendantes (plateaux chauffants, racks, tables à vide) ; les pièces d'un robot ou d'une machine sont stockées dans leur propre repère de lien, elles arrivent donc empilées à l'origine et sans articulations. Préférez un hôte `https://` (ou `HYDRA_UMC_PASSWORD` / la saisie du mot de passe plutôt que `--password`). Une transformation met d'abord à l'échelle, puis tourne autour de X, Y et Z, puis translate ; la rotation se fait autour de l'origine du fichier, pas du centre de la pièce.

**Rien n'est jamais supprimé de façon permanente.** Un retrait ou un
remplacement déplace d'abord le vrai fichier original dans le propre
sous-dossier `.trash/` de ce modèle - la même discipline "ne jamais
détruire, déplacer de côté" déjà suivie par les conventions de travail
internes de cet écosystème, appliquée ici comme une vraie fonctionnalité
produit, pas seulement comme une habitude interne.

## 🧩 Rôle dans HYDRA-UMC

**HYDRA-UMC-EDITOR-STL** est l'outil de bureau qui modifie les vraies pièces STL de chaque modèle de robot et de machine fourni par HYDRA-UMC-STUDIO et HYDRA-UMC-SUITE. Il lit leurs deux dossiers de modèles tels quels, montre un modèle dans une visionneuse Qt Quick 3D, et transforme, recolore, remplace, retire ou ajoute une pièce sur le disque, en mettant l'original de côté au lieu de le supprimer. Un modèle terminé peut être envoyé au catalogue de modèles d'un HYDRA-UMC-SERVER.

## 🏛️ Architecture

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-EDITOR-STL architecture" width="100%">
</p>

### ARCHITECTURE ET DÉCISIONS DE CONCEPTION

- **Deux bibliothèques réelles, un seul module de découverte.** La
  propre constante `LIBRARIES` de `model_catalog.py` nomme les deux
  vrais arbres que cet outil édite (`HYDRA-UMC-STUDIO/public/models/`,
  `HYDRA-UMC-SUITE/assets/meshes/`) - ajouter une troisième bibliothèque
  plus tard signifie ajouter une entrée là, pas une seconde
  implémentation de découverte.
- **`stl_ops.py` est le seul endroit qui modifie jamais un fichier.**
  `model_catalog.py` reste strictement en lecture seule ; `--cli` et le
  pont Qt Quick appellent exactement les mêmes fonctions
  `transform_part()`/`replace_part()`/`remove_part()`/`add_part()`,
  donc la GUI ne peut jamais faire quelque chose que la CLI elle-même
  ne pourrait pas faire.
- **Un vrai STL, pas juste un nom de fichier finissant par `.stl`.**
  `is_real_stl()` analyse vraiment un candidat au remplacement/ajout
  avec `numpy-stl` avant qu'il ne soit jamais copié dans un vrai dossier
  de modèle - et, une vraie lacune trouvée en écrivant les propres tests
  de ce projet, rejette aussi un résultat d'analyse à **0 triangle** :
  le propre chemin de repli ASCII de `numpy-stl` ne lève pas d'exception
  sur des octets de charabia arbitraires, il les analyse silencieusement
  comme un maillage vide, donc un simple try/except seul aurait laissé
  passer un fichier qui n'est pas du tout un STL.
- **GUI Qt Quick par défaut, `--cli` pour les systèmes sans affichage.**
  `main.py` n'importe PySide6 que sur le chemin non-`--cli`, donc
  `--cli categories`/`models`/`parts`/`transform`/`replace`/`remove`/
  `add` fonctionnent sur une machine sans affichage ni runtime Qt
  installé du tout.
- **La même vraie couche visuelle que HYDRA-UMC-UPDATER.** `qml/Main.qml`
  réutilise textuellement les propres composants `GameButton`/
  `GameCombo`/`SectionPanel` de ce projet et son thème sombre
  cyan/bleu/ambre/rouge, à la demande explicite du propriétaire du
  projet - un nouvel outil PC dans cet écosystème doit donner
  l'impression d'être le même outil, pas un conçu séparément.
- **Racine de l'écosystème, pas un chemin figé.** Comme la propre racine
  de workspace de HYDRA-UMC-UPDATER, le répertoire parent de ce projet
  lui-même est la valeur par défaut (`default_ecosystem_root()` de
  `main.py`), toujours modifiable (`--root` sur `--cli`, "Parcourir"
  dans la GUI) et mémorisée entre les lancements de la GUI
  (`settings.py`).

## 🔒 Sécurité et protection

| Menace | Défense | Où |
|---|---|---|
| Perdre une pièce quand elle est remplacée ou retirée | L'original est d'abord déplacé dans le dossier `.trash/` du modèle et jamais supprimé ; la restauration est possible, et vider la corbeille demande une confirmation explicite | `stl_ops.py` |
| Un fichier qui n'est pas un STL, ou un nom de pièce qui sort du dossier du modèle | Un remplacement ou un ajout est d'abord analysé et refusé s'il n'a aucun triangle ou s'il est tronqué ; un nom de pièce doit être un simple nom `.stl` dans le dossier du modèle ; une transformation qui donnerait des sommets non finis ne change rien | `stl_ops.py`, `mesh_check.py` |
| Le mot de passe du serveur dans l'historique du shell ou la liste des processus | `--password` n'est pas recommandé ; sans lui, le mot de passe est lu dans `HYDRA_UMC_PASSWORD` ou demandé sans écho ; un hôte `https://` évite de l'envoyer en clair | `main.py`, `catalog_push.py` |
| Un envoi trop gros ou qui se bloque | L'envoi complet doit tenir dans 49 Mio (la limite du serveur est de 50 Mo) et chaque requête a un délai de 20 s ; seules les pièces `.stl` sont envoyées et les autres sont signalées | `catalog_push.py` |
| Des journaux qui grossissent ou contiennent des données | Un seul journal tournant dans le dossier personnel, de 256 Kio avec deux copies | `diagnostics.py` |

**Ce qu'il ne fait jamais :** modifier quoi que ce soit hors des dossiers de modèles que vous lui indiquez, ni supprimer une pièce définitivement. L'envoi à un serveur a été écrit selon son contrat documenté et n'a pas été essayé sur un vrai serveur.

## 🔌 Interfaces

| Topic ou route | Ce qu'il porte |
|---|---|
| `--cli categories \| models \| parts <library> [...]` | liste ce qui existe : les catégories, les modèles d'une catégorie, les fichiers de pièces d'un modèle (`--json` pour les machines) ; la bibliothèque est `studio` ou `suite` |
| `--cli transform <library> <category> <model> <part> [--tx --ty --tz --rx --ry --rz --scale]` | translate, tourne et met à l'échelle une pièce sur place : d'abord l'échelle, puis la rotation autour de X, Y et Z, puis la translation, par rapport à l'origine du fichier |
| `--cli replace \| remove \| add` | remplace une pièce par un autre STL, en déplace une dans `.trash/`, ou apporte un nouveau STL (`--dest-filename` le renomme) |
| `--cli push <library> <category> <model> --host --username` | envoie les pièces modifiables d'un modèle à `POST /api/models/submit` d'un serveur (connexion administrateur ; `--port` 3000 par défaut, `--server-category`, `--overwrite`) |
| `--root <folder>` | la racine de l'écosystème qui contient `HYDRA-UMC-STUDIO` et `HYDRA-UMC-SUITE` côte à côte ; par défaut, le dossier parent de cet outil |

## ⚙️ Configuration

Il n'y a ni serveur ni fichier de configuration à modifier à la main : la fenêtre mémorise ses choix dans un fichier et chaque modèle garde ses couleurs dans un fichier annexe.

| Variable | Par défaut | Ce qu'elle définit |
|---|---|---|
| `~/.hydra_umc_editor_stl_settings.json` | aucun | la racine de l'écosystème et la langue choisie dans la fenêtre, mémorisées entre les lancements |
| `part_colors.json` (in each model folder) | `#9fb4c9` | la couleur de chaque pièce ; un STL binaire n'en porte aucune, et STUDIO et SUITE lisent le même fichier |
| `HYDRA_UMC_PASSWORD` | non définie | le mot de passe du serveur pour `--cli push`, pour qu'il reste hors de la ligne de commande |
| `~/.hydra_umc_editor_stl.log` | 256 KiB x 3 | le journal tournant de la fenêtre et de la ligne de commande |

## 🚀 Démarrage rapide

Nécessite Python 3.10 ou plus récent. La première ligne crée un environnement virtuel avec l'extra d'interface et lance les vérifications et les tests ; Windows a `build.bat` et `run.bat`.

```bash
./build.sh                                    # creates .venv, installs the package with the GUI extra, checks and tests
./run.sh                                      # the windowed editor
./run.sh --cli categories studio              # lists the categories of the STUDIO library (use suite for the SUITE one)
./run.sh --cli parts studio robots-6-dof ar3  # lists the part files of one model
```

## 🧪 Tests

215 tests automatiques s'exécutent avec `python -m pytest tests -q`. Ils n'ont besoin ni de matériel ni de rien en dehors de cette machine.

La CI exécute `HYDRA_UMC_CI=1 python tools/ci_validate.py`, qui vérifie le manifeste, les documents, les huit README et les images.

## 🏗️ Compilation et publication

```bash
chmod +x build.sh   # une seule fois
./build.sh          # crée .venv, pip install -e ".[dev,gui]", compile et teste
./run.sh                                                    # GUI fenêtrée (par défaut)
./run.sh --cli categories studio                            # liste les catégories d'une bibliothèque
./run.sh --cli models studio robots-6-dof                   # liste les modèles d'une catégorie
./run.sh --cli parts studio robots-6-dof ar3                 # liste les vrais fichiers de pièces d'un modèle
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /chemin/nouveau.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /chemin/nouveau.stl
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

Sous Windows : `build.bat`, puis `run.bat` (GUI) ou `run.bat --cli ...` /
double-clic sur `run-gui.vbs` pour un lancement de GUI sans console.

`library` est toujours `studio` ou `suite` ; `category`/`model` sont les
vrais noms de dossier que `categories`/`models` viennent d'afficher.
`--root` remplace la racine de l'écosystème pour n'importe quelle
commande `--cli` (par défaut : le propre répertoire parent de cet
outil).

## 🩺 Dépannage

- `categories`/`models`/`parts` n'affiche rien : la racine de
  l'écosystème ne contient en réalité pas `HYDRA-UMC-STUDIO`/
  `HYDRA-UMC-SUITE` comme frères - passez `--root` explicitement, ou
  utilisez "Parcourir" dans la GUI.
- `transform`/`replace`/`add` échoue avec "not a real, parseable STL
  file" : le fichier source n'est en réalité pas un STL valide (ou en
  est un à 0 triangle) - ouvrez-le dans un vrai visualiseur CAO/maillage
  pour confirmer.
- Une pièce retirée/remplacée n'a pas disparu de la propre liste de
  pièces de la GUI : elle a bien été déplacée vers `.trash/` sur le
  disque - la liste de pièces ne montre que les vrais fichiers actuels
  de premier niveau, et un sous-dossier `.trash/` en est délibérément
  exclu.

| Vous voyez | Parce que | Faites |
|---|---|---|
| « L'envoi a réussi mais le serveur n'a renvoyé aucun identifiant », ou une erreur de connexion | Le serveur a refusé le compte (l'envoi demande un administrateur), n'est pas un HYDRA-UMC-SERVER ou a répondu autre chose qu'un objet JSON | Utilisez un compte administrateur d'un vrai HYDRA-UMC-SERVER, avec son adresse et son port |
| « la transformation produirait des sommets non finis (trop grande ?) - rien n'a été modifié » | L'échelle ou la translation est si grande que les nombres ne tiennent plus dans un flottant 32 bits | Utilisez des valeurs plus petites |
| « vider la corbeille demande une confirmation explicite » | Rien n'est supprimé définitivement sans votre confirmation | Restaurez l'entrée depuis `.trash/`, ou confirmez le vidage dans la fenêtre |

## 📂 Structure du dépôt

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-EDITOR-STL" width="100%">
</p>

<details>
<summary>Version texte de l'arborescence</summary>

```text
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/   code source
│   ├── __init__.py             Version du paquet
│   ├── model_catalog.py        Découverte réelle, en lecture seule, des deux bibliothèques de modèles
│   ├── stl_ops.py              Mutation STL réelle : transformer/remplacer/retirer/ajouter, sauvegardes .trash/
│   ├── catalog_push.py         URDF d'assemblage + client HTTP pour POST /api/models/submit
│   ├── settings.py             Racine de l'écosystème et préférence de langue persistées
│   ├── i18n.py                 Traductions réelles et complètes de la GUI (8 langues)
│   ├── diagnostics.py          Journal tournant dans le dossier personnel et garde des slots de la fenêtre
│   ├── qt_gui.py               Pont Qt Quick sur le vrai noyau model_catalog.py/stl_ops.py
│   ├── qml/Main.qml            Coquille de bureau à thème, partagée avec HYDRA-UMC-UPDATER
│   ├── main.py                 Répartition : GUI par défaut, --cli pour categories/models/parts/transform/replace/remove/add/push
│   ├── assembly.py             La vue assemblée (pose de départ) d'une machine à partir de ses pièces STL
│   ├── mesh_check.py           Contrôles du maillage avant l'envoi au catalogue
│   ├── part_colors.py          Annotations de couleur par pièce (un STL binaire n'en porte pas)
│   └── stl_geometry.py         Les vrais triangles d'un fichier STL comme géométrie Qt Quick 3D
├── tests/                      Vrais tests contre de vrais fichiers STL générés
├── docs/                       documents du projet
├── images/                     Médias et icônes de l'application
├── tools/                      outils du projet et vérifications de la CI
├── .github/                    workflow de CI et modèles de tickets
├── build.sh / build.bat        venv + installation éditable (extras dev+gui) + vérification de compilation + tests
├── run.sh / run.bat            GUI par défaut / point d'entrée CLI
├── run-gui.vbs                 Lanceur graphique Windows sans fenêtre de console
├── bump_version.py             Incrément de version type compteur kilométrique (exécuté seulement par la commande `bump` explicite)
├── bump_manifest_version.py    Synchronise la version de hydra-umc.project.json avec la native (--sync)
├── CHANGELOG.md                ce qui a changé à chaque version
├── build-test.sh               vérification de build sans modification
├── hydra-umc.project.json      manifeste : version, maturité, famille
├── pyproject.toml              métadonnées du paquet
└── test.sh                     vérification de build sans modification
```

</details>

## 🗺️ Feuille de route et limites connues

**Limites connues aujourd'hui**

- Un exécutable de GUI autonome empaqueté (PyInstaller, suivant la même
  convention `build_exe.bat`/`.sh` de HYDRA-UMC-SUITE).
- Annuler/rétablir sur le propre historique `.trash/` d'une session, au
  lieu d'une restauration manuelle de fichier.

## 🌍 Langues

Ce README et les documents du dépôt existent en huit langues : anglais, espagnol, allemand, français, italien, japonais, chinois et portugais (Portugal). Ils sont écrits ensemble et la CI vérifie que les huit fichiers ont les mêmes sections et les mêmes liens.

## 🔗 Projets liés

Ce projet fait partie de l'écosystème robotique HYDRA-UMC du même auteur (JuanenRac / Electro Hobby 3D). Bon à savoir, car une demande pourrait en réalité concerner l'un de ceux-ci plutôt que ce dépôt.

**Projet Parent**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — propriétaire de l'une des deux vraies bibliothèques de modèles que cet éditeur lit et écrit (`public/models/`).

**Directement Liés**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — propriétaire de la seconde vraie bibliothèque de modèles que cet éditeur lit et écrit (`assets/meshes/`), maintenue exactement dans la même structure de catégories que celle de STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — éditeur de bureau frère pour le côté URDF/cinématique du même catalogue de modèles, plutôt que la géométrie STL brute qu'édite cet outil.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — propriétaire du vrai point de terminaison `POST /api/models/submit` vers lequel cet éditeur envoie ses éditions terminées (`catalog_push.py`, « Envoyer au serveur... » dans la GUI ou `--cli push`).

**Fait Également Partie de l'Écosystème**

*Matériel et Plateforme Centrale*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la conception de la carte mère du bras robotique : hôte CM5 + coprocesseur STM32H745 double cœur, destinée à coordonner jusqu'à 8 bras-outils via CAN-OTA/SPI-OTA (firmware à un stade précoce ; aucune carte assemblée pour l'instant).
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — couche produit Raspberry Pi OS reproductible pour la CM5 : agent en lecture seule, config/profils validés, provisionnement WiFi de premier contact.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — le contrat JSON-Schema partagé et la barrière logicielle de contrôle des jobs contre laquelle chaque bridge valide ses commandes (pas une fonction de sécurité certifiée).
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registre déclaratif de manifestes d'adaptateurs et son validateur pour les connecteurs de machines externes ; étend l'idée de contrat du SDK aux machines externes sans remplacer les projets de passerelle industrielle.

*Backend Central et Clients*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — application de contrôle Android native avec connexion biométrique et une compagne Wear OS appairée.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — application de contrôle iOS/iPadOS (Flutter) avec synchronisation WebSocket en temps réel.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — UI tactile native pour l'écran tactile DSI 7" embarqué sur la CM5 elle-même.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — créateur/éditeur graphique de bureau pour URDF avec chargement de source GitHub/local et édition avec aperçu 3D en direct.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — frontière de coordination pour les flottes AGV/AMR via un éditeur MQTT VDA 5050 (testé uniquement contre une flotte émulée).
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinateur haut niveau pour cellules CNC avec accès au statut/octets de contrôle GRBL (testé uniquement contre un émulateur).
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — frontière de coordination pour droïdes à pattes/humanoïdes, avec un émetteur de commandes Boston Dynamics Spot (testé uniquement contre un émulateur).
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinateur de cellules laser lisant 3 signaux GPIO de clé/enceinte/verrouillage (testé uniquement contre une puce simulée ; il ne peut ni armer ni tirer un laser).
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinateur sûr de haut niveau du flux de cartes pour le pick-and-place OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — limite de coordination sûre pour imprimantes 3D Moonraker/Klipper, avec de vraies commandes de tâche à porte contrôlée.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinateur avec un transport ROS 2 rclpy à importation paresseuse (pas encore exécuté contre une installation ROS 2).
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — frontière de coordination pour UAV équipés de caméra, avec un émetteur de commandes MAVLink (testé uniquement contre un émulateur).

*Plateforme d'Outils URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware pour la carte PCB physique du Universal Robot Tool Controller, plus de 25 profils d'outils sur bus CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — outil GUI de bureau pour flasher les cartes URTC, CAN-OTA plus SWD/JTAG complet.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — outil de diagnostic bus CAN en direct de bureau pour cartes URTC, un panneau par profil d'outil.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternative basée sur navigateur à URTC-TESTER via la Web Serial API, sans installation locale.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — passerelle devant le bus CAN d'URTC : liste d'identifiants autorisés, limite de débit et clé de session ; logiciel testé sur ordinateur, pas encore sur un bus réel.

*Nœud de Vision IA (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub d'intégration pour le pipeline de vision Hailo-8, avec une vraie vérification de préparation matérielle par étape.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registre réel de modèles compilés avec vérification de chargement sûr par architecture/somme de contrôle Hailo.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — générateur réel de pipeline GStreamer + config MediaMTX avec une vraie limite d'intégration HailoRT.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — loi de correction Position-Based Visual Servoing avec autorisation conditionnée à l'état de zone ; pas encore d'estimation de pose par caméra.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — logique v0 de violation de zone, de fraîcheur de calibration et de demande d'E-STOP qui lit les positions d'objets dans un fichier ; aucun détecteur ne l'alimente et aucun E-STOP physique n'y est encore relié.

*Nœud Cognitif IA (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — hub d'intégration pour le pipeline cognitif Hailo-10 (orchestration LLM/VLA/voix).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — encodage/décodage réel de jetons d'action et génération de trajectoire pour un modèle Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — frontend vocal réel (VAD + analyseur d'intention) avec un relais Watch borné et soumis à confirmation.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — décomposition réelle de tâches basée sur des règles et récupération sémantique d'erreurs sur les codes d'erreur du MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — recherche réelle de documents TF-IDF uniquement en stdlib sur les propres docs Markdown de cet écosystème.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — technicien de maintenance IA local, à porte de politique, pour l'écosystème lui-même - observe, diagnostique et propose des corrections ; les deux niveaux de risque les plus élevés ne sont délibérément pas encore implémentés.

*Orchestration et Essaim*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — hub d'intégration avec un vrai contrat gRPC/Protobuf de rapport de santé et une machine à états de mission.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — vraie file de tâches basée sur la priorité avec déduplication, sur une vraie API HTTP.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vrai gardien de santé de flotte basé sur gRPC avec réessai/backoff et détection de non-concordance d'identité.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — vrai planificateur de trajectoire 3D basé sur RRT avec validation réelle de collision obstacle/espace de travail.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — synchronisation d'état réelle CRDT LWW-Element-Map, testée par propriétés pour la convergence multi-cellule.

*Jumeau Numérique et Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — vrai jumeau numérique de simulation physique, consommant les modèles URDF produits par HYDRA-UMC-EDITOR-URDF.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — consomme ces mêmes modèles URDF pour sa propre simulation physique.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — génère des données d'entraînement à partir de ces mêmes modèles.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — routeur hardware-in-the-loop avec un verrouillage logiciel de collision entre simulation et matériel réel (testé sans matériel réel).

*Données et Analytique*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — vrai magasin de séries temporelles adossé à sqlite3 avec une vraie API HTTP d'ingestion/requête.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — vrai détecteur d'anomalies par FFT + ligne de base statistique avec surveillance de dérive.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — vrai calcul d'OEE/disponibilité sur l'historique DATALAKE, avec export CSV reproductible.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — vrai pipeline d'ingestion CAN/WebSocket vers DATALAKE, avec déduplication de séquence.

*Passerelle Industrielle*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — hub d'intégration relayant vers les protocoles industriels, avec une vraie couche de liste blanche de commandes/contre-pression.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — vrai espace d'adressage OPC-UA, vérifié avec une vraie session client de protocole binaire.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — vrai courtier MQTT avec authentification par client optionnelle et ACL de sujets.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — vrais points de terminaison XML `/probe` et `/current` de MTConnect avec sortie en mode dégradé.

*Outils Complémentaires et Opérations de l'Écosystème*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — panneaux de Résumés Intelligents et de Mise en Évidence d'Anomalies sur DATALAKE/ANOMALY-DETECTOR, avec un repli statistique honnête.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI de flotte avec un vrai contrat de code de sortie stable, un vrai client en direct de la propre API de HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — application compagnon WearOS avec des motifs d'alerte haptique et un relais vocal vers le téléphone jumelé (pas encore exécutée sur une montre physique).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware pour un rack de montage de cartes avec décodage réel d'ID d'outil et logique de préchauffage Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus un vrai compagnon de vision Python pour une tête d'inspection thermique/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — outil administratif de bureau qui découvre, clone et met à jour chaque dépôt de cet écosystème, et l'origine de la propre couche visuelle Qt Quick de ce projet.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — outil de bureau Windows/Linux qui construit une image CM5 prête à flasher préchargée avec les versions les plus actuelles de l'écosystème, avec une configuration Wi-Fi/utilisateur/SSH au premier démarrage façon Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinateur d'incidents de maintenance : un rôle de périphérie à faible privilège collecte un instantané assaini d'inventaire/santé, un rôle de plan de contrôle l'affiche en lecture seule et demande à un fournisseur d'IA de suggérer un diagnostic - n'applique jamais de correctif ni ne déploie rien.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — hôte de développement reproductible (Raspberry Pi 5 / CM5) qui stocke le code source de l'écosystème et exécute des tâches de build/test bornées sous une file durable ; un rôle de développement dédié, explicitement pas une CM5 opérationnelle.

## 📚 Documentation

Où lire la suite :

* [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - chaque sous-commande réelle de `--cli`, argument par argument.
* [Base de sécurité de l'écosystème](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modèle de menaces de l'écosystème](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Journal des modifications de ce dépôt](CHANGELOG.md)
* [Licence de ce dépôt](LICENSE.md)

## 🤝 Contribuer et communauté

* Avant une pull request, exécutez `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (ou `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`) : il doit afficher `CI_VALIDATION=PASS`. N'exécutez pas `build.sh` ni `build.bat` pour cette vérification ; compiler n'est pas vérifier.
* Les huit README sont écrits à partir d'une source unique dans HYDRA-UMC-DOCS ; ne les modifiez pas à la main. Changez la source et réécrivez-les avec `tools/make_readmes.py`.
* N'affirmez pas dans un README ce qui n'a pas tourné : écrivez « simulé » ou « non essayé sur matériel » quand c'est la vérité.
* Voir [CONTRIBUTING.md](CONTRIBUTING.md), le [code de conduite](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) et [SUPPORT.md](SUPPORT.md).

## 👤 AUTEUR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENCE

GPL-3.0-or-later - [LICENSE](LICENSE).
