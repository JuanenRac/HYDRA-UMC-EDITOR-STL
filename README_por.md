<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | 🇵🇹 <b>Português</b></p>

### 📦 Explore e edite as bibliotecas reais de modelos STL do ecossistema HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="numpy-stl core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="PySide6 Qt Quick desktop GUI">
</p>

> **v0.1.3.** O núcleo real de CLI/GUI descrito abaixo está genuinamente
> implementado e testado, incluindo um verdadeiro visualizador Qt Quick 3D com
> seleção por clique, cor por peça, transformar, substituir, remover,
> adicionar e um envio real de um modelo editado/adicionado de volta para o
> catálogo `POST /api/models/submit` do próprio HYDRA-UMC-SERVER (o mesmo
> ponto de integração real que o HYDRA-UMC-EDITOR-URDF usa para modelos
> URDF). A cor guardada de uma peça chega agora também aos visualizadores 3D
> em direto do próprio HYDRA-UMC-STUDIO e do próprio HYDRA-UMC-SUITE (as suas
> próprias alterações reais e separadas - ver os CHANGELOGs desses
> repositórios), pelo que o `part_colors.json` já não é uma pré-visualização
> apenas do EDITOR-STL.

**Verificação de honestidade - o que realmente funciona hoje:** o
`model_catalog.py` (descoberta real e só de leitura de ambas as bibliotecas
de modelos), o `stl_ops.py` (mutação real de STL via `numpy-stl` -
transformar/substituir/remover/adicionar, mais `model_bounds()` para o
enquadramento da câmara do visualizador 3D), o `part_colors.py` (ficheiro
auxiliar real de cor por peça), o `stl_geometry.py` (carregamento real de
geometria Qt Quick 3D) e o `catalog_push.py` (geração real de URDF de
montagem mais um cliente HTTP real para `POST /api/models/submit`) estão
todos testados contra fixtures STL reais e geradas e, quando necessário,
uma `QGuiApplication` real de sessão (`pytest tests/`, 194 casos a passar) e
foram testados de ponta a ponta contra as cópias reais do
`HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` deste ecossistema (`--cli categories`/
`models`/`parts` contra as árvores reais; `transform`/`remove` contra uma
cópia descartável, nunca a cópia real). O próprio `EditorBridge` do
`qt_gui.py` também é testado diretamente (slot de cor, seleção preservada
após uma mudança de cor). O `qml/Main.qml` carrega e renderiza sem erros de
QML (verificado sem cabeça com `QT_QPA_PLATFORM=offscreen`, incluindo com as
peças de um modelo real carregadas no visualizador 3D), mas o próprio grafo
de cena QML não tem teste automático próprio - não se tenta conduzir um
ciclo de eventos Qt real, a mesma fronteira de honestidade que o README do
próprio HYDRA-UMC-UPDATER já traça para o seu shell Qt Quick.

---

> **Estado de segurança (safety e security):** este ecossistema não é um sistema de segurança certificado. Ainda não existe um caminho de E-STOP por hardware, nem limites ou interlocks impostos pelo firmware, nem um comando de movimento verificado; as imagens de firmware são verificadas com CRC32 e um HMAC-SHA256 de chave partilhada, não com uma assinatura assimétrica; TLS e TLS mútuo são opcionais e estão desativados por defeito; nenhuma placa própria foi ainda montada ou testada. Leia a [base de segurança](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) e o [modelo de ameaças](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) antes de confiar em qualquer afirmação aqui para a segurança de uma pessoa.

## 📋 Num relance

| | |
|---|---|
| Versão | `0.1.6` |
| Maturidade | Funcional |
| Tecnologia | Python / PySide6 / Qt Quick / numpy-stl |
| Destino | O PC de quem o usa |
| Em hardware real | Não aplicável: nada aqui corre em hardware |

## 1. 🛠️ VISÃO TÉCNICA GERAL

O HYDRA-UMC-EDITOR-STL é uma pequena ferramenta de desktop - GUI com janela
por defeito, CLI completa com `--cli` - para editar as peças STL reais que
compõem cada modelo de robô/máquina que o HYDRA-UMC-STUDIO e o
HYDRA-UMC-SUITE distribuem. Ambas as aplicações reorganizaram as suas
próprias pastas de modelos em 2026-09 na mesma disposição real de categorias
(`robots-5-dof`/`robots-6-dof`/`robots-7-dof`, `machine-pnp`/`machine-cnc`/
`machine-laser`, `heatedbeds`/`racks`/`vacuum-tables`, cada modelo com o seu
`metadata.json` ao lado do `ATTRIBUTION.txt`) - esta ferramenta lê essa
disposição real exata, não uma cópia separada nem uma base de dados própria.

Um visualizador Qt Quick 3D real renderiza cada peça editável do modelo
selecionado (`stl_geometry.py`, uma `QQuick3DGeometry` real que carrega os
triângulos de cada peça diretamente do seu ficheiro STL) - arraste para
orbitar, use a roda para aproximar, clique numa peça para a selecionar
(`View3D.pick()` real, não um palpite de teste de colisão). A câmara
enquadra-se na caixa delimitadora combinada real do próprio modelo
(`model_bounds()` do `stl_ops.py`), pelo que tanto uma base de robô de 400 mm
como um parafuso de 5 mm ficam bem enquadrados.

Seis operações reais, cada uma apoiada em E/S de ficheiros real contra a
cópia verdadeira em disco:

- **Transformar** - transladar/rodar/escalar os dados de vértices reais de
  uma peça (via `numpy-stl`, a mesma biblioteca de que o `render/mesh.py` do
  próprio HYDRA-UMC-SUITE já depende) e guardá-los no mesmo sítio.
- **Mudar a cor** - uma anotação real de cor por peça (`part_colors.json`,
  um ficheiro auxiliar de que esta ferramenta é dona) mostrada na vista 3D -
  um STL binário não traz cor própria fiável, pelo que este ficheiro
  auxiliar é a verdadeira fonte de verdade. O `hooks/usePartColors.ts` do
  próprio HYDRA-UMC-STUDIO e o `render/part_colors.py` do próprio
  HYDRA-UMC-SUITE leem ambos exatamente o mesmo ficheiro, pelo que uma cor
  guardada aqui chega também aos seus visualizadores 3D em direto, e não
  apenas à pré-visualização desta ferramenta.
- **Substituir** - sobrescrever uma peça com outro ficheiro STL real.
- **Remover** - retirar uma peça de um modelo.
- **Adicionar** - trazer um novo ficheiro STL real para um modelo.
- **Enviar para o servidor** - submeter as peças editáveis atuais do modelo
  selecionado ao catálogo real de submissão de modelos de um HYDRA-UMC-SERVER
  em execução (`catalog_push.py`, `POST /api/models/submit` - exige login de
  administrador, tal como a funcionalidade equivalente do próprio
  HYDRA-UMC-EDITOR-URDF). Como o contrato desse endpoint tem forma de URDF,
  isto envolve as peças no mais pequeno URDF real que ele aceita: um link
  raiz mais um link filho sem junta (`fixed`) por peça, já que a posição
  real de cada peça já está embutida nos vértices do seu próprio STL - nunca
  uma pose sintética.
- **Barra de ferramentas flutuante do visualizador** - Selecionar, Mover (um
  gizmo real e arrastável de 3 eixos), Editar (rodar/escalar), Cor,
  Adicionar, Eliminar, Fixar (grava de forma permanente o mover/rodar/escalar),
  Copiar, Colar e Cortar, dentro da própria vista 3D. As mesas aquecidas, as
  mesas de vácuo e os racks são variantes de tamanho independentes, pelo que
  o visualizador mostra apenas a selecionada em vez de as empilhar.
- **Vista montada** - os modelos de robôs, CNC, PnP e laser abrem já montados
  na sua pose inicial (lida da cinemática do próprio HYDRA-UMC-SUITE ao lado
  desta cópia, apenas para visualização); um botão da barra de ferramentas
  passa para as peças em bruto para edição.

**Limites do envio e da transformação:** só são enviadas as peças `.stl` (as outras são indicadas), o envio completo tem de caber no limite de pedido de 50 MB do servidor e o modelo só fica guardado no catálogo do servidor (o HYDRA-UMC-STUDIO ainda não o lê). A pose identidade é correta para peças independentes (camas aquecidas, racks, mesas de vácuo); as peças de um robô ou máquina estão guardadas no seu próprio referencial de elo, pelo que chegam empilhadas na origem e sem articulações. Prefira um anfitrião `https://` (ou `HYDRA_UMC_PASSWORD` / o pedido da palavra-passe em vez de `--password`). Uma transformação escala primeiro, depois roda em X, Y e Z e por fim translada; a rotação é em torno da origem do ficheiro, não do centro da peça.

**Nada é alguma vez eliminado permanentemente.** Uma remoção ou uma
substituição move primeiro o ficheiro original real para a subpasta `.trash/`
do próprio modelo - a mesma disciplina de «nunca destruir, mover para o lado»
que as convenções internas de trabalho deste ecossistema já seguem, aplicada
aqui como uma funcionalidade real do produto, e não apenas um hábito interno.

## 2. 🧱 ARQUITETURA E DECISÕES DE DESIGN

- **Duas bibliotecas reais, um módulo de descoberta.** A constante
  `LIBRARIES` do `model_catalog.py` nomeia as duas árvores reais que esta
  ferramenta edita (`HYDRA-UMC-STUDIO/public/models/`,
  `HYDRA-UMC-SUITE/assets/meshes/`) - acrescentar uma terceira biblioteca
  mais tarde significa acrescentar uma entrada aí, e não uma segunda
  implementação de descoberta.
- **O `stl_ops.py` é o único sítio que alguma vez altera um ficheiro.** O
  `model_catalog.py` continua estritamente só de leitura; tanto o `--cli`
  como a ponte Qt Quick chamam exatamente as mesmas funções
  `transform_part()`/`replace_part()`/`remove_part()`/`add_part()`, pelo que a
  GUI nunca pode fazer nada que a própria CLI não pudesse.
- **Um STL real, não apenas um nome de ficheiro que acaba em `.stl`.** O
  `is_real_stl()` analisa de facto, com o `numpy-stl`, uma substituição/adição
  candidata antes de ela ser copiada para uma pasta de modelo real - e, uma
  lacuna real descoberta ao escrever os testes deste projeto, rejeita também
  um resultado de análise com **0 triângulos**: o caminho de recurso ASCII do
  próprio `numpy-stl` não levanta exceção perante bytes arbitrários, analisa-os
  em silêncio como uma malha vazia, pelo que um simples try/except teria
  deixado passar um ficheiro completamente não-STL.
- **GUI Qt Quick por defeito, `--cli` para sem cabeça.** O `main.py` só
  importa o PySide6 no caminho sem `--cli`, pelo que
  `--cli categories`/`models`/`parts`/`transform`/`replace`/`remove`/`add`
  funcionam numa máquina sem ecrã nem runtime Qt instalado.
- **O mesmo shell visual real do HYDRA-UMC-UPDATER.** O `qml/Main.qml`
  reutiliza tal como estão os componentes `GameButton`/`GameCombo`/
  `SectionPanel` desse projeto e o seu tema escuro ciano/azul/âmbar/vermelho,
  a pedido do próprio dono do projeto - uma ferramenta de PC nova neste
  ecossistema deve parecer a mesma ferramenta, não uma desenhada em separado.
- **Raiz do ecossistema, não um caminho codificado.** Tal como a raiz do
  espaço de trabalho do próprio HYDRA-UMC-UPDATER, a diretoria-mãe deste
  projeto é o valor por defeito (`default_ecosystem_root()` do `main.py`),
  sempre substituível (`--root` no `--cli`, «Procurar» na GUI) e lembrada
  entre arranques da GUI (`settings.py`).

## 📂 ESTRUTURA DE DIRETORIAS

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # Descoberta real e só de leitura de ambas as bibliotecas de modelos
│   ├── stl_ops.py           # Mutação real de STL: transformar/substituir/remover/adicionar, cópias em .trash/
│   ├── catalog_push.py       # URDF de montagem + cliente HTTP para POST /api/models/submit
│   ├── settings.py          # Raiz do ecossistema persistida + preferência de idioma
│   ├── i18n.py               # Traduções reais e completas da GUI (8 idiomas)
│   ├── qt_gui.py             # Ponte Qt Quick sobre o núcleo real model_catalog.py/stl_ops.py
│   ├── qml/Main.qml          # Shell de desktop com tema, partilhado com o HYDRA-UMC-UPDATER
│   └── main.py               # Despacho: GUI por defeito, --cli para categories/models/parts/transform/replace/remove/add/push
├── tests/                    # Testes reais contra fixtures STL reais e geradas
├── docs/
│   └── CLI_REFERENCE.md      # Referência de comandos
├── images/                   # Multimédia e ícones da aplicação
├── tools/
│   ├── build_test.py         # Verificação de compilação sem alterar versões
│   └── ci_validate.py        # Validação de manifesto/CHANGELOG/docs usada pelo CI
├── build.sh / build.bat      # venv + instalação editável (extras dev+gui) + verificação de compilação + testes
├── run.sh / run.bat          # GUI por defeito / ponto de entrada da CLI
├── run-gui.vbs               # Lançador gráfico para Windows sem janela de consola
├── bump_version.py           # Subida de versão ao estilo conta-quilómetros (executada só pelo comando `bump` explícito)
└── bump_manifest_version.py  # Sincroniza a versão do hydra-umc.project.json com a nativa (--sync)
```

## ⚙️ GUIA DE COMPILAÇÃO E EXECUÇÃO

```bash
chmod +x build.sh   # uma única vez
./build.sh          # cria o .venv, pip install -e ".[dev,gui]", verificações de compilação + testes
./run.sh                                                    # GUI com janela (por defeito)
./run.sh --cli categories studio                            # lista as categorias de uma biblioteca
./run.sh --cli models studio robots-6-dof                   # lista os modelos de uma categoria
./run.sh --cli parts studio robots-6-dof ar3                 # lista os ficheiros de peças reais de um modelo
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /path/new.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /path/new.stl
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

No Windows: `build.bat` e depois `run.bat` (GUI) ou `run.bat --cli ...` /
duplo clique em `run-gui.vbs` para um arranque da GUI sem consola.

A `library` é sempre `studio` ou `suite`; a `category`/`model` são os nomes
reais das pastas que `categories`/`models` acabaram de imprimir. O `--root`
substitui a raiz do ecossistema em qualquer comando `--cli` (por defeito: a
diretoria-mãe desta ferramenta).

**Resolução de problemas**

- `categories`/`models`/`parts` não imprime nada: a raiz do ecossistema não
  contém de facto o `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` como irmãos - passe
  `--root` explicitamente, ou use «Procurar» na GUI.
- `transform`/`replace`/`add` falha com «not a real, parseable STL file»: o
  ficheiro de origem genuinamente não é um STL válido (ou é um com 0
  triângulos) - abra-o num visualizador CAD/de malhas real para confirmar.
- Uma peça removida/substituída não desapareceu da lista de peças da GUI:
  moveu-se de facto para `.trash/` em disco - a lista de peças só mostra
  ficheiros reais e atuais do nível superior, e a subpasta `.trash/` é
  deliberadamente excluída dela.

## 🚀 ROTEIRO

- Um executável autónomo da GUI empacotado (PyInstaller, em linha com a
  convenção `build_exe.bat`/`.sh` do próprio HYDRA-UMC-SUITE).
- Anular/refazer sobre o histórico `.trash/` de uma sessão, em vez de um
  restauro manual de ficheiros.

---

## 🔗 Projetos relacionados

Este projeto faz parte do ecossistema de robótica HYDRA-UMC do mesmo autor (JuanenRac / Electro Hobby 3D). Vale a pena conhecê-los, porque um pedido pode ser, na verdade, sobre um destes e não sobre este repositório.

**Projeto-mãe**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — é dono de uma das duas bibliotecas de modelos reais que este editor lê e escreve (`public/models/`).

**Diretamente relacionados**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — é dono da segunda biblioteca de modelos real que este editor lê e escreve (`assets/meshes/`), mantida exatamente na mesma disposição de categorias que a do STUDIO.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — editor de desktop irmão para o lado URDF/cinemática do mesmo catálogo de modelos, em vez da geometria STL em bruto que esta ferramenta edita.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — é dono do endpoint real `POST /api/models/submit` para onde este editor envia as edições concluídas (`catalog_push.py`, «Enviar para o servidor...» na GUI ou `--cli push`).

**Também fazem parte do ecossistema**

*Hardware e plataforma centrais*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — o desenho da placa-mãe do braço robótico: anfitrião CM5 + STM32H745 de dois núcleos, pensado para orquestrar até 8 braços de ferramenta por CAN-OTA/SPI-OTA (firmware numa fase inicial; ainda sem placa montada).
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — camada de produto reproduzível do Raspberry Pi OS para o CM5: agente só de leitura, configuração/perfis validados, aprovisionamento Wi-Fi de primeiro contacto.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — o contrato JSON-Schema partilhado e a fronteira de software de controlo de trabalhos contra a qual cada bridge valida os seus comandos (não é uma função de segurança certificada).
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registo declarativo de manifestos de adaptador e validador para conectores de máquinas externas; estende a ideia de contrato do SDK a máquinas externas sem substituir os projetos de gateway industrial.

*Backend central e clientes*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — aplicação Android nativa de controlo, com início de sessão biométrico e um companheiro Wear OS emparelhado.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — aplicação de controlo para iOS/iPadOS (Flutter) com sincronização WebSocket em tempo real.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interface tátil nativa para o ecrã tátil DSI de 7" integrado, executada no próprio CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — criador/editor gráfico de URDF para desktop, com carregamento de origem a partir do GitHub/local e edição com pré-visualização 3D em direto.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — fronteira de coordenação para frotas AGV/AMR através de um publicador MQTT VDA 5050 (testado apenas contra uma frota emulada).
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordenador de células CNC de alto nível com acesso ao estado GRBL e aos bytes de controlo (testado apenas contra um emulador).
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — fronteira de coordenação para droides com patas/humanoides, com um emissor de comandos para o Boston Dynamics Spot (testado apenas contra um emulador).
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordenador de células laser que lê 3 sinais GPIO (chave, caixa e interlock) (testado apenas contra um chip simulado; não pode armar nem disparar um laser).
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordenador seguro de fluxo de placa de alto nível para pick-and-place com OpenPnP.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — fronteira de coordenação segura para impressoras 3D Moonraker/Klipper, com comandos de trabalho reais protegidos por portas.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordenador com um transporte ROS 2 baseado em rclpy importado sob demanda (ainda não executado contra uma instalação ROS 2).
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — fronteira de coordenação para UAV com câmara, com um emissor de comandos MAVLink (testado apenas contra um emulador).

*Plataforma de ferramentas URTC*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware da placa física Universal Robot Tool Controller, mais de 25 perfis de ferramenta por barramento CAN.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — ferramenta gráfica de gravação para desktop das placas URTC, por CAN-OTA e também SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — ferramenta de diagnóstico CAN em tempo real para desktop das placas URTC, com um painel por perfil de ferramenta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa no navegador ao URTC-TESTER através da Web Serial API, sem instalação local.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — gateway à frente do barramento CAN do URTC: lista de identificadores permitidos, limite de taxa e chave de sessão; software testado num computador, ainda não num barramento real.

*Nó de IA de visão (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — centro de integração do pipeline de visão Hailo-8, com uma verificação real de prontidão de hardware por fase.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registo real de modelos compilados com verificação segura de carga por arquitetura Hailo e soma de verificação.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — pipeline GStreamer real e gerador de configuração MediaMTX com uma fronteira de integração HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — lei de correção de servovisão baseada em posição com autorização condicionada ao estado da zona; ainda sem estimativa de pose por câmara.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — lógica v0 de violação de zonas, atualidade da calibração e pedido de E-STOP que lê as posições dos objetos de um ficheiro; nenhum detetor a alimenta e ainda não há E-STOP físico ligado.

*Nó de IA cognitiva (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — centro de integração do pipeline cognitivo do Hailo-10 (orquestração de LLM/VLA/voz).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — codificação/descodificação real de tokens de ação e geração de trajetórias para um modelo Visão-Linguagem-Ação.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — front-end de voz real (VAD + analisador de intenções) com um relé para o relógio limitado e protegido por confirmação.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — decomposição real de tarefas baseada em regras e recuperação semântica de erros sobre os códigos de erro do MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — pesquisa real de documentos TF-IDF só com a biblioteca padrão sobre a documentação Markdown deste ecossistema.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — técnico de manutenção de IA local, protegido por políticas, para o próprio ecossistema: observa, diagnostica e propõe correções; os dois níveis de maior risco não estão implementados de propósito.

*Orquestração e enxame*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — centro de integração com um contrato real de relatório de saúde gRPC/Protobuf e uma máquina de estados de missões.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — fila real de trabalhos por prioridade com deduplicação, sobre uma API HTTP real.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vigilante real de saúde da frota por gRPC com repetição/recuo e deteção de identidade incoerente.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — planeador real de trajetórias 3D baseado em RRT com validação real de colisões com obstáculos e espaço de trabalho.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — sincronização real de estado CRDT LWW-Element-Map, testada por propriedades para a convergência de várias células.

*Gémeo digital e simulação*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — gémeo digital real de simulação física, que consome os modelos URDF que o HYDRA-UMC-EDITOR-URDF produz.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — consome os mesmos modelos URDF para conduzir a sua própria simulação física.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — gera dados de treino a partir desses mesmos modelos.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — encaminhador hardware-in-the-loop com um interlock de software de colisão entre a simulação e o hardware real (testado sem hardware real).

*Dados e análise*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — armazém real de séries temporais sobre sqlite3 com uma API HTTP real de ingestão/consulta.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — detetor real de anomalias por FFT e linha de base estatística, com monitorização de deriva.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — cálculo real de OEE/disponibilidade sobre o histórico do DATALAKE, com exportação CSV reprodutível.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — pipeline real de ingestão CAN/WebSocket para o DATALAKE, com deduplicação por sequência.

*Gateway industrial*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — centro de integração que retransmite para protocolos industriais, com uma camada real de lista de comandos permitidos e contrapressão.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — espaço de endereços OPC-UA real, verificado com uma sessão de cliente real do protocolo binário.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — broker MQTT real com autenticação opcional por cliente e ACL de tópicos.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — endpoints XML MTConnect `/probe` e `/current` reais com saída em modo degradado.

*Ferramentas complementares e operações do ecossistema*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — painéis de Resumos Inteligentes e Realce de Anomalias sobre o DATALAKE/ANOMALY-DETECTOR, com um recurso estatístico honesto.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI da frota com um contrato de códigos de saída real e estável, um cliente vivo genuíno da API do HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — aplicação companheira WearOS com padrões de alerta tátil e um relé de voz para o telemóvel emparelhado (ainda não executada num relógio físico).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware de um rack de montagem de placas com descodificação real do ID da ferramenta e lógica de pré-aquecimento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware mais um companheiro de visão em Python real para uma cabeça de ferramenta de inspeção térmica/RGB.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — ferramenta administrativa de desktop que descobre, clona e atualiza cada repositório deste ecossistema, e a origem do shell visual Qt Quick deste próprio projeto.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — ferramenta de desktop para Windows/Linux que constrói uma imagem do CM5 pronta a gravar com as versões mais recentes do ecossistema, com configuração de primeiro arranque de Wi-Fi/utilizador/SSH ao estilo do Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordenador de incidentes de manutenção: um papel de borda de poucos privilégios recolhe um inventário/estado higienizado, um papel de plano de controlo mostra-o só de leitura e pede a um fornecedor de IA que sugira um diagnóstico; nunca aplica um patch nem implanta nada.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — anfitrião de desenvolvimento reproduzível (Raspberry Pi 5 / CM5) que guarda o código-fonte do ecossistema e executa tarefas limitadas de compilação/teste numa fila durável; um papel de desenvolvimento dedicado, explicitamente não um CM5 operacional.

---

## 📚 Documentação e comunidade

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - cada subcomando `--cli` real, argumento a argumento.
- [`CHANGELOG.md`](CHANGELOG.md) - o que realmente foi entregue, versão a versão.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)**
E-mail: `electrohobby3d@gmail.com`
YouTube: [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENÇA

GPL-3.0-or-later - veja [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md).

