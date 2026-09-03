# 🎮 Contexto Base do Jogo: Terranon

> **Nota para Agentes de IA:** Este documento é a especificação canônica e visão técnica detalhada do projeto **Terranon**. Utilize este arquivo como fonte primária de contexto para compreender a arquitetura, convenções, mecânicas, hierarquia de entidades e sistemas antes de propor refatorações ou implementar novas funcionalidades.

---

## 1. 📌 Visão Geral do Jogo

- **Nome do Projeto:** Terranon
- **Gênero:** Top-Down Action / Base Defense / Tower Defense / Survival 2D
- **Linguagem:** Python 3.10+
- **Motor / Bibliotecas:** 
  - `pygame-ce` (v2.5.7)
  - `PyTMX` (v3.32) para carregamento de mapas criados no Tiled
- **Resolução da Tela:** 1056 x 720 pixels (60 FPS com delta time regulado)
- **Objetivo do Jogo:** O jogador controla um personagem em visão aérea com movimentação livre (8 direções) e disparo direcional com mira pelo mouse. O objetivo principal é proteger a **Base Central** (`MainBase`) contra sucessivas ondas de criaturas hostis (como Goblins) que surgem de ninhos/spawners espalhados pelo mapa e seguem trilhas de waypoints predeterminadas. O jogador acumula pontos derrotando inimigos para investir em estruturas defensivas e gerenciar o fluxo das batalhas.

---

## 2. 🕹️ Mecânicas de Gameplay e Loop do Jogo

```
┌────────────────────────────────────────────────────────┐
│                      GAME LOOP                         │
│                                                        │
│  [WaveManager / Spawners] ──> Spawna Inimigos          │
│            │                                           │
│            ▼                                           │
│  [Inimigos] ──(Seguem Waypoints)──> [MainBase / Player]│
│            │                               │           │
│   (Derrotados pelo Jogador/Torres)         ▼           │
│            │                       [Vida chega a 0]    │
│            ▼                               │           │
│  [EconomyManager (+Pontos)]                ▼           │
│            │                         [GAME OVER]       │
│            ▼                                           │
│  [Construção / Defesa]                                 │
└────────────────────────────────────────────────────────┘
```

### 2.1. Controles do Jogador
- **Movimento:** Teclas `W` (Cima), `A` (Esquerda), `S` (Baixo), `D` (Direita) — movimentação em 8 direções.
- **Corrida (Sprint):** `Left Shift` (duplica a velocidade base de 250 para 500 px/s).
- **Ataque / Disparo:** `Botão Esquerdo do Mouse` (dispara projéteis em direção à posição do cursor do mouse no mundo, com cooldown base de 0.3s).
- **Inventário:** Tecla `I` (abre a tela de inventário como overlay; `ESC` ou `I` fecha).
- **Menu / Pausa:** Tecla `ESC`.
- **Debug / Cheats:**
  - `F3 + C`: Alterna visualização de colisores (Hitbox amarela, Feet Hitbox ciano).
  - `F3 + S`: Alterna telemetria no HUD (FPS, Coordenadas reais, Offset da câmera, Vida, Pontos).
  - `F3 + D`: Alterna visualização de vetores de direção das entidades.
  - `F3 + Z`: Emite evento de reinicialização de ondas (`RESET_WAVES`).
  - `K` (durante o jogo): Força transição imediata para `GAME_OVER`.

### 2.2. Condições de Vitória e Derrota
- **Derrota (Game Over):** Ocorre se a vida do jogador zerar (`Player.health.current_hp <= 0`) OU se a vida da Base Central zerar (`MainBase.health.current_hp <= 0`).
- **Pontuação e Economia:** Cada abate de inimigo pelo jogador emite `ENEMY_KILLED` e adiciona pontos ao `EconomyManager`.

---

## 3. 🏛️ Arquitetura de Software e Padrões de Projeto

O projeto adota uma arquitetura modular, orientada a eventos e desacoplada baseada em padrões consagrados de desenvolvimento de jogos:

1. **Singleton Pattern (`SingletonMeta`):**
   Utilizado em todos os gerenciadores globais (`GameManager`, `StateManager`, `EventManager`, `SpatialManager`, `MapManager`, `SoundManager`, `AssetManager`, `EconomyManager`, `DebugManager`, `EnemyFactory`) para garantir instância única e acesso global seguro.
2. **State Pattern (`BaseState`, `StateManager`):**
   Gerencia os diferentes estados do ciclo de vida da aplicação (`MENU`, `PLAY`, `INVENTORY`, `GAME_OVER`).
3. **Observer / Event-Driven Bus (`EventManager` / `GameEventEnum`):**
   Comunicação desacoplada entre sistemas. Em vez de acoplamento direto, ações (como disparar projéteis, tocar sons, abater inimigos, disparar game over) emitem eventos tipados.
4. **Component Pattern:**
   - `AnimatorComponent`: Animações direcionais, controle de taxa de quadros e rotação.
   - `HealthComponent`: Controle de pontos de vida, invulnerabilidade temporária (i-frames) e callbacks de morte.
5. **Factory Pattern (`EnemyFactory`, `ProjectileFactory`):**
   Instanciação encapsulada e extensível de entidades e projéteis.
6. **Y-Sorting & Layered Rendering (`CameraGroup`):**
   Renderização em perspectiva isométrica/top-down 2.5D, onde a camada de renderização (`render_layer`) é recalculada dinamicamente com base na base do sprite (`rect.bottom`). Objetos estáticos que obstruem a visão do jogador tornam-se semitransparentes dinamicamente.

---

## 4. 📂 Estrutura de Diretórios e Arquivos

```
terranon/
├── assets/                          # Recursos do jogo
│   ├── images/                      # Sprites e texturas
│   │   ├── goblin-pack/             # Animações de goblins (direções N, S, E, W)
│   │   ├── goblin-sword-pack/       # Variações de goblins armados
│   │   ├── player/                  # Frames do jogador (idle e moving em 8 direções)
│   │   └── projectile/              # Projéteis (normal, fire, etc.)
│   ├── maps/                        # Mapas e tilesets
│   │   ├── Assets/                  # Tilesets de terreno e decorações
│   │   ├── tmx/main_world.tmx       # Mapa principal exportado pelo Tiled
│   │   └── tsx/                     # Tilesets externos Tiled
│   └── sounds/                      # Áudio
│       ├── effects/                 # SFX (damage.mp3, death.mp3, shoot.wav)
│       └── music/                   # Trilhas musicais (Crashsite-Defense.wav)
├── src/                             # Código-fonte principal
│   ├── main.py                      # Ponto de entrada (Entry point)
│   ├── core/                        # Núcleo da engine e infraestrutura
│   │   ├── animator_component.py    # Gerenciador de animações por frames
│   │   ├── camera_group.py          # Grupo de sprites com câmera e Y-sort
│   │   ├── entity_sprite.py         # Ponte entre GameObject e pygame.sprite.Sprite
│   │   ├── game_object.py           # Classes base: GameObject, StaticObject, DynamicObject
│   │   ├── game_world.py            # Cena do mundo do jogo
│   │   ├── health_component.py      # Componente de vida e dano
│   │   ├── singleton_meta.py        # Metaclass para Singletons
│   │   ├── wave_manager.py          # Controle e script de hordas/ondas
│   │   ├── enums/                   # Enums tipados do sistema
│   │   │   ├── abstract_enum.py
│   │   │   ├── character_state_enum.py
│   │   │   ├── debug_option_enum.py
│   │   │   ├── directions_enum.py   # 8 direções (N, NE, E, SE, S, SW, W, NW)
│   │   │   ├── enemy_enum.py        # Tipos de inimigos (GOBLIN)
│   │   │   ├── enemy_spawner_enum.py# Identificadores de spawners (ALPHA, BETA, GAMA, DELTA)
│   │   │   ├── game_event_enum.py   # Eventos globais do jogo
│   │   │   ├── game_state_enum.py   # Estados (MENU, PLAY, INVENTORY, GAME_OVER)
│   │   │   ├── map_enums/           # Camadas, mapas e waypoints
│   │   │   └── projectile/          # Tipos e variantes de projéteis
│   │   ├── exceptions/              # Exceções customizadas
│   │   ├── factories/               # Fábricas de criação dinâmica
│   │   │   ├── enemy_factory.py     # Criação de inimigos
│   │   │   ├── factory.py           # Base factory
│   │   │   ├── factories_loader.py  # Inicializador das fábricas
│   │   │   └── projectile_factory.py# Criação de projéteis
│   │   ├── manager/                 # Gerenciadores de subsistemas (Singletons)
│   │   │   ├── asset_manager.py     # Cache de imagens, fontes e sons
│   │   │   ├── debug_manager.py     # Renderização e flags de depuração
│   │   │   ├── economy_manager.py   # Pontos e compras
│   │   │   ├── event_manager.py     # Barramento de eventos (Pub/Sub)
│   │   │   ├── game_manager.py      # Loop principal e timing
│   │   │   ├── input_manager.py     # Leitura de teclado/mouse
│   │   │   ├── sound_manager.py     # Controle de BGM e SFX
│   │   │   ├── spatial_manager.py   # Grupos de colisão e resolução física
│   │   │   └── state_manager.py     # Máquina de estados do jogo
│   │   ├── map/                     # Integração com mapas Tiled
│   │   │   ├── map.py               # Classe abstrata de mapa
│   │   │   ├── map_backgroud.py     # Objeto de fundo estático
│   │   │   ├── map_manager.py       # Gerenciador de mapas
│   │   │   ├── maps/main_world.py   # Parser e carregador de main_world.tmx
│   │   │   └── waypoints/           # Waypoints e polylines para IA de navegação
│   │   ├── settings/                # Configurações estáticas e cores
│   │   │   ├── colors.py            # Paleta de cores da UI, debug e gameplay
│   │   │   ├── maps_assets.py       # Caminhos de assets de mapa
│   │   │   └── settings.py          # Constantes globais (resolução, FPS, bindings)
│   │   └── states/                  # Estados do jogo
│   │       ├── base_state.py        # Interface BaseState
│   │       ├── play_state.py        # Estado principal de gameplay
│   │       └── ui/                  # Estados de interface
│   │           ├── game_over.py     # Tela de Game Over
│   │           ├── inventory_state.py# Tela/Overlay de Inventário
│   │           └── menu_state.py    # Tela de Menu Inicial
│   ├── entities/                    # Entidades do jogo
│   │   ├── character/
│   │   │   ├── characters.py        # Classe base Character
│   │   │   ├── goblin.py            # Inimigo Goblin
│   │   │   └── player.py            # Personagem do Jogador
│   │   ├── nature/
│   │   │   ├── tree.py              # Árvores com colisão na base
│   │   │   └── world_collider.py    # Colisores invisíveis do mapa
│   │   ├── projectiles/
│   │   │   └── projectile.py        # Projétil direcional
│   │   ├── structures/
│   │   │   ├── main_base.py         # Base principal a ser defendida
│   │   │   └── towers/generic_tower.py # Torre de defesa básica
│   │   ├── enemy.py                 # Classe base Enemy com navegação por Polyline
│   │   ├── enemy_spawner.py         # Ponto de spawn de inimigos
│   │   └── obstacle.py              # Obstáculo estático com hitboxes
│   └── utils/                       # Funções utilitárias
│       ├── direction.py             # Vetor -> Texto de direção ("N", "S", "E", "W")
│       ├── image.py                 # Carregamento seguro e redimensionamento de imagens
│       ├── position.py              # Cálculo de distância euclidiana
│       ├── resource_path.py         # Resolução de paths compatível com PyInstaller
│       └── rotation.py              # Cálculos de ângulos e rotações vetoriais
├── req.txt                          # Dependências pip
└── main.spec                        # Configuração de build do PyInstaller
```

---

## 5. ⚙️ Subsistemas e Gerenciadores (Managers)

| Gerenciador | Tipo | Responsabilidade |
| :--- | :--- | :--- |
| **`GameManager`** | Singleton | Controla o loop principal (`on_execute`), cálculo de `dt`, tick do clock (60 FPS), despacho de eventos e desenho final na janela. |
| **`StateManager`** | Singleton | Registra instâncias de `BaseState` e alterna o estado ativo via `change_to(GameStateEnum)`. |
| **`EventManager`** | Singleton | Hub Pub/Sub com métodos `subscribe()`, `unsubscribe()` e `emit()`. Valida eventos contra `GameEventEnum`. |
| **`SpatialManager`** | Singleton | Centraliza grupos de colisão (`obstacles`, `dynamic_group`, `enemies_group`, `friend_projectiles_group`, `structures_group`). Executa detecção de impactos (Inimigo vs Jogador, Projétil vs Inimigo, Inimigo vs Base, Jogador vs Paredes/Árvores). |
| **`MapManager`** | Singleton | Carrega e inicializa mapas Tiled (`MainWorldMap`), props da natureza e instancia entidades no `GameWorld`. |
| **`SoundManager`** | Singleton | Controla mixer do Pygame, volume mestre/música/efeitos e execução de BGM em loop ou SFX com limite de canais simultâneos. |
| **`AssetManager`** | Singleton | Carrega e armazena em cache imagens (`Surface`), fontes (`Font`) e áudio (`Sound`). |
| **`EconomyManager`** | Singleton | Rastreia `current_points` e `total_points`. Trata adições por abate e gastos com estruturas. |
| **`WaveManager`** | Instanciado | Orquestra o script de ondas de ataque, temporizadores de spawn e acionamento dos `EnemySpawner` cadastrados. |
| **`InputManager`** | Singleton | Captura estados de teclas/mouse e processa atalhos de depuração (`F3 + ...`). |
| **`DebugManager`** | Singleton | Renderiza hitboxes, caixas de colisão de pés, vetores direcionais e overlay com telemetria do player e do motor. |

---

## 6. 🧬 Hierarquia de Entidades e Componentes

### 6.1. Árvore de Classes
```
GameObject (ABC)
│
├── StaticObject
│   ├── Obstacle
│   │   ├── MainBase (Estrutura vital com 500 HP)
│   │   ├── GenericTower (Torre defensiva com range e dano)
│   │   ├── Tree (Árvore com colisor de tronco relativo)
│   │   └── WorldCollider (Paredes e bordas do mapa)
│   └── EnemySpawner (Ponto de geração de hordas)
│
└── DynamicObject
    ├── Projectile (Projétil direcional com AnimatorComponent)
    └── Character (Possui AnimatorComponent e HealthComponent)
        ├── Player (Controlado pelo usuário, 8 direções, dash, tiro)
        └── Enemy (Base para IA de percurso de Waypoints)
            └── Goblin (Inimigo melee com 20 HP e animações 4-way)
```

### 6.2. Detalhes dos Componentes
- **`HealthComponent`:**
  - `max_hp`: Vida total máxima.
  - `current_hp`: Vida atual.
  - `take_damage(amount)`: Aplica dano respeitando i-frames (`iframes_duration`).
  - `heal(amount)`: Recupera vida sem exceder `max_hp`.
  - `die()`: Dispara `on_death_callback` e marca `is_dead = True`.
- **`AnimatorComponent`:**
  - Gerencia dicionário de animações por estado (`idle_S`, `walking_N`, `running_SE`).
  - `add_animation(state_name, frames, duration)`: Registra sequência de sprites.
  - `play(state_name)`: Inicia/alterna animação.
  - `set_angle(angle)`: Aplica rotação por software nos frames (usado em projéteis).

### 6.3. Sistema de Hitboxes Diferenciadas
Para obter movimentação fluida em ambiente top-down 2.5D:
- **`hitbox` (Corpo):** Usada para detecção de dano e acerto de projéteis ou contato de inimigos (ex: 15x30 px no Player).
- **`feet_hitbox` (Pés):** Caixa de colisão reduzida (ex: 15x10 px na base dos pés do Player) usada para colisão com o chão/troncos de árvores/paredes. Isso permite que a cabeça/tronco do personagem sobreponha copas de árvores sem travar o movimento.

---

## 7. 🗺️ Sistema de Mapas, Waypoints e Navegação

### 7.1. Camadas do Mapa Tiled (`MapLayersEnum`)
- `ground`: Tiles do chão renderizados previamente em uma única superfície estática otimizada (`_ground_image`).
- `waypoints`: Pontos de interesse (ex: `player_spawnpoint`, `base`).
- `spawners`: Ninhos de inimigos associados a uma rota inicial (`start_path`).
- `enemy_routes`: Linhas quebradas (polylines) formadas por sequências ordenadas de coordenadas que os inimigos seguem até a base.
- `trees`: Objetos de vegetação com propriedades customizadas de colisão.
- `collision`: Caixas invisíveis de bloqueio físico de terreno (`WorldCollider`).

### 7.2. Algoritmo de Navegação dos Inimigos
1. O inimigo nasce no `EnemySpawner` e recebe uma rota `Polyline`.
2. Calcula o vetor de direção em relação ao `current_waypoint`.
3. Quando a distância é inferior a 5 pixels, avança para o próximo waypoint da lista.
4. Ao atingir o último waypoint (a `MainBase`), para de navegar e ataca a base diretamente.

---

## 8. 📡 Tabela de Eventos Globais (`GameEventEnum`)

| Evento | Payload / Parâmetros | Emissor Comum | Efeito / Assinante Principal |
| :--- | :--- | :--- | :--- |
| `PLAY_SFX` | `filename: str` | `Player`, `SpatialManager` | `SoundManager` reproduz o arquivo de áudio. |
| `PLAY_MUSIC` | `filename: str, loops, fade_ms` | `PlayState` | `SoundManager` inicia reprodução da música. |
| `GAME_OVER` | Nenhum | `Player.on_death`, `MainBase.on_death` | `PlayState` reseta economia e transiciona para `GameOverState`. |
| `WAVE_STARTED` | `wave_index: int` | `WaveManager` | Notifica início de nova horda. |
| `WAVE_ENDED` | `wave_index: int` | `WaveManager` | Notifica fim da horda atual. |
| `ENEMY_SPAWNED`| `enemy: Enemy` | `EnemySpawner` | `PlayState` adiciona a entidade ao `GameWorld`. |
| `ENEMY_KILLED` | `points: int` | `Enemy.on_death` | `EconomyManager` credita pontos ao jogador. |
| `SPAWN_PROJECTILE` | `position, direction, type, variant, speed, damage, lifetime, friendly` | `Player.shoot`, Torres | `ProjectileFactory` cria e injeta projétil no `GameWorld`. |
| `SPEND_POINTS` | `points: int` | Sistema de Compra / Torres | `EconomyManager` debita o saldo se disponível. |
| `RESET_WAVES`  | Nenhum | `InputManager` (Debug F3+Z) | `WaveManager` reinicia temporizador e contadores de hordas. |

---

## 9. 🧭 Diretrizes para Agentes de IA

Ao desenvolver novas features, corrigir bugs ou estender o código, siga rigorosamente as diretrizes abaixo:

1. **Uso de Eventos para Desacoplamento:**
   - Nunca acople entidades diretamente ao `SoundManager`, `EconomyManager` ou à lista de entidades do `GameWorld`. Dispare eventos via `EventManager().emit(GameEventEnum.<EVENTO>, ...)`.
2. **Registro de Recursos no `AssetManager`:**
   - Sempre utilize `AssetManager().load_image(...)` ou `load_sound(...)` com caminhos relativos ao diretório `assets/`.
3. **Novos Inimigos:**
   - Herde de `Enemy` (em `src/entities/character/`).
   - Adicione o tipo no enum `EnemyEnum` (`src/core/enums/enemy_enum.py`).
   - Registre a nova classe no `EnemyFactory._registry`.
4. **Novos Projéteis:**
   - Adicione os tipos e variantes em `ProjectileTypesEnum` e `ProjectileVariantEnum`.
   - Organize os sprites em `assets/images/projectile/<tipo>/<variante>/<frame>.png`.
5. **Novos Estados de Jogo:**
   - Herde de `BaseState` (em `src/core/states/`).
   - Adicione o estado em `GameStateEnum`.
   - Registre o novo estado no `StateManager` dentro de `src/main.py`.
6. **Colisões e Grupos Físicos:**
   - Toda entidade que interage no mundo físico deve passar pelo `SpatialManager().add_obj_to_group(obj)`.
   - Implemente o método `on_collision(self, other)` na entidade quando necessário.
7. **Padrão de Código:**
   - Tipagem estática (`typing`) em todas as assinaturas de funções e métodos.
   - Nomes de classes em `PascalCase`, variáveis/métodos em `snake_case`, constantes e Enums em `SCREAMING_SNAKE_CASE`.
