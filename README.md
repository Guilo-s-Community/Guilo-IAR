# Inteligência Artificial E Robótica
# Relatório do Projeto
O projeto está na pasta ProjetoCC7711 contendo:
 * Controller
 * World
 * Vídeo da simulação

## Professores Responsáveis:
 * Flávio Tonidandel
 * Ricardo de Carvalho Destro
   
## Nome dos integrantes:
 * Guilherme Marcato Mendes Justiça - 24.122.045-8
 * Paulo Vinicius Araujo Feitosa - 24.122.042-5


## Robô E-puck com Identificação de Objeto Leve (Webots)

Este projeto simula um robô E-puck em um ambiente 2D no Webots com o objetivo de encontrar e empurrar a caixa mais leve dentre várias distribuídas no cenário. Após detectar o deslocamento da caixa leve, o robô realiza uma ação, girando sobre seu próprio eixo enquanto pisca seus LEDs.

## 💡 Objetivo

Desenvolver um comportamento autônomo simples baseado em sensores, simulando capacidades de tomada de decisão em um robô móvel:

- Navegar livremente pelo ambiente.
- Detectar obstáculos utilizando sensores de proximidade.
- Empurrar objetos detectados à sua frente.
- Identificar qual caixa foi deslocada (indicando que é leve).
- Reconhecer essa caixa como alvo e reagir girando continuamente, com LEDs piscando.

## ⚙️ Tecnologias Utilizadas

- **Webots R2025a** — Simulador de robótica.
- **Python (controller)** — Lógica de controle do robô.
- **Supervisor API** — Para acompanhar o movimento das caixas.
- **Sensores de distância e encoders** — Para navegação e verificação de movimento.

## 📁 Estrutura do Projeto

- `my_controller.py` — Script principal do controlador do robô.
- `worlds/` — Contém o ambiente simulado com múltiplas caixas (de massas diferentes).
- `README.md` — Este arquivo.

## 🤖 Lógica do Robô

### Estados

O comportamento do robô é gerenciado por uma máquina de estados com quatro fases principais:

1. **MOVENDO**: O robô anda livremente até detectar um obstáculo.
2. **EMPURRANDO**: Ao encontrar uma caixa à sua frente, ele tenta empurrá-la.
3. **VIRANDO**: Caso fique travado, o robô executa manobras para mudar de direção.
4. **ENCONTRADO**: Se uma caixa se mover após o empurrão (detectado pelo Supervisor), ela é identificada como "leve" e o robô gira em comemoração.

### Identificação da Caixa Leve

O Supervisor compara a posição atual das caixas com suas posições iniciais. Se a diferença de posição ultrapassa um pequeno limiar (`_limite_movimento`), o robô reconhece a caixa como leve.

### LEDs e Gesto Final

Após encontrar a caixa leve, todos os LEDs do E-puck começam a piscar, enquanto ele gira continuamente sobre seu próprio eixo.

## 🧪 Teste Rápido

1. Abra o Webots.
2. Carregue o mundo `.wbt` fornecido.
3. Execute a simulação.
4. Observe o comportamento do robô ao explorar e detectar a caixa leve.

## 📌 Observações

- Apenas uma caixa no ambiente possui massa reduzida, tornando-a "empurrável".
- A posição inicial de todas as caixas é armazenada automaticamente ao iniciar a simulação.

