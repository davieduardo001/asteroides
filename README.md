# Asteroides

Este é um jogo de Asteroides clássico desenvolvido em Python usando a biblioteca Pygame.

## Funcionalidades Atuais

- **Nave do Jogador:** Controlada pelo teclado, a nave pode rotacionar para a esquerda e direita (teclas de seta) e aplicar impulso para frente (tecla de seta para cima).
- **Movimentação:** A nave possui velocidade, atrito (drag) e velocidade máxima.
- **Rotação da Nave:** A imagem da nave é rotacionada dinamicamente de acordo com sua orientação.
- **Loop de Tela (Screen Wrapping):** Tanto a nave do jogador quanto os asteroides reaparecem no lado oposto da tela ao saírem dos limites.
- **Gráficos:** Utiliza imagens customizadas para o fundo do jogo e para a nave do jogador, com fallback para formas simples caso as imagens não carreguem.
- **Asteroides (Temporariamente Desabilitados):** O jogo inclui uma classe para asteroides que aparecem em tamanhos e velocidades aleatórias, movendo-se pela tela. Esta funcionalidade está temporariamente desabilitada para focar em outros aspectos do desenvolvimento.
- Disparo
- Futuro criação de asteroides

## Arquitetura e Concorrência

O jogo utiliza mecanismos de concorrência para gerenciar tarefas de forma eficiente e responsiva:

### 1. Thread de Processamento de Entrada (`src/input_handler.py`)

- **Propósito:** Isolar o processamento de entrada do jogador (teclado) do loop principal do jogo para evitar bloqueios e manter a responsividade.
- **Funcionamento:**
    - Uma thread dedicada é iniciada para monitorar uma fila de entrada (`input_queue`).
    - O loop principal do jogo captura os eventos de teclado do Pygame e os adiciona a esta fila.
    - A thread de entrada consome os eventos da fila e atualiza um dicionário de estado compartilhado (`shared_input_state`), que reflete as ações atuais do jogador (ex: rotacionar, acelerar, atirar).
    - Para garantir a segurança no acesso concorrente ao `shared_input_state` (escrita pela thread de entrada e leitura pelo loop principal), um `threading.Lock` (`input_lock`) é utilizado.
    - Um `threading.Event` (`stop_input_thread_event`) é usado para sinalizar à thread de entrada que ela deve encerrar suas atividades quando o jogo está fechando.

### 2. Semáforo para Gerenciamento de Asteroides (`asteroids.py` e `src/game_entities.py`)

- **Propósito:** Controlar o número máximo de asteroides ativos simultaneamente na tela, prevenindo sobrecarga de processamento e mantendo o balanceamento do jogo.
- **Funcionamento:**
    - Um `threading.Semaphore` (`asteroid_semaphore`) é inicializado com um valor que define o limite máximo de asteroides.
    - **Criação de Asteroides:** Antes de um novo asteroide ser criado (seja no início do jogo ou quando um asteroide maior se divide), o jogo tenta adquirir o semáforo (`asteroid_semaphore.acquire()`).
        - Se o semáforo for adquirido com sucesso (ou seja, o número de asteroides ativos é menor que o limite), o novo asteroide é instanciado e adicionado ao jogo.
        - Se o semáforo não puder ser adquirido (limite atingido), o novo asteroide não é criado naquele momento.
    - **Destruição de Asteroides:** Quando um asteroide é destruído (por um tiro ou ao sair da tela), ele libera o semáforo (`asteroid_semaphore.release()`), decrementando a contagem de asteroides ativos e permitindo que um novo asteroide possa ser criado.

Esta abordagem ajuda a manter o jogo fluido e a gerenciar recursos de forma eficaz.

## Como Jogar (Controles)

- **Seta para Esquerda:** Rotacionar a nave para a esquerda.
- **Seta para Direita:** Rotacionar a nave para a direita.
- **Seta para Cima:** Aplicar impulso para frente.

## Como Executar

1.  Certifique-se de ter Python e Pygame instalados.
2.  Clone este repositório (ou baixe os arquivos).
3.  Navegue até o diretório do projeto no terminal.
4.  Execute o jogo com o comando: `python asteroides.py`

## Próximos Passos (Exemplos)

- Reativar e aprimorar os asteroides.
- Implementar sistema de tiros para a nave.
- Adicionar colisões entre nave, tiros e asteroides.
- Sistema de pontuação e vidas.
- Menus e telas de jogo (início, game over).
