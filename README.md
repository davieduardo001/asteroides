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

---
*Este README foi gerado por Cascade, seu assistente de codificação AI.*
