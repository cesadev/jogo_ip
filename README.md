# 🃏 Ouro e Cachaça — O Tabuleiro das Almas

> Um roguelike deckbuilder de terror-psicológico inspirado em **Inscryption**, ambientado no folclore nordestino brasileiro.

Desenvolvido no Centro de Informática da **Universidade Federal de Pernambuco (UFPE)**, como projeto da disciplina de Introdução à Programação.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=pygame&logoColor=white)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-educational-lightgrey)

---

## 📖 Sobre o jogo

Você se senta em um bar para jogar cartas contra **o Matheus**, um narrador que já perdeu a conta das almas que coleciona dos perdedores. Se vencer, explora o mapa em busca de novas criaturas. Se perder, sua alma passa a fazer parte de um cortejo fantasmagórico.

O jogo mistura **TCG**, **roguelike deckbuilder** e **terror psicológico**, em um formato *Point & Click*, com arte em **Pixel Art** e ilustrações inspiradas em **xilogravura**.

**Objetivo final:** derrotar os três bosses e conquistar os totens do Saci.

- ❤️ Vida: representada por **dois copos de shot**
- ⚖️ Pontuação/dano: medidos por **tampinhas de cerveja** em uma balança
- 💰 Cada criatura possui um custo em ouro para ser jogada

---

## 🃏 Criaturas

| Nome | Ataque | Vida | Custo | Efeito |
|---|---|---|---|---|
| Acauã | 2 | 3 | 2 | Dano direto |
| Anhangá | 3 | 7 | 4 | — |
| Boitatá | 2 | 1 | 2 | Morte instantânea |
| Caboclo D'água | 1 | 1 | 1 | Se esconde |
| Cacto | 0 | 3 | 0 | — |
| Capelobo | 1 | 2 | 1 | — |
| Chupa Cabra | 1 | 1 | 1 | Dano de sangue |
| Cobra Coral | 2 | 2 | 1 | Morte instantânea |
| Cuca | 2 | 2 | 2 | Shell (escudo) |
| Comadre Fulozinha | 1 | 1 | 2 | Dano em 3 direções |
| Curupira | 3 | 2 | 2 | — |
| La Ursa | 4 | 6 | 3 | — |
| Leão-do-Norte | 7 | 7 | 4 | — |
| Mula Sem-Cabeça | 3 | 4 | 3 | — |
| Perna Cabeluda | 0 | 1 | 0 | Sacrifício |
| Timbu | 2 | 2 | 1 | Dano de volta |

---

## 👥 Personagens

**O Matheus** — Narrador que já perdeu a conta de almas. Você o encontra em um bar e joga com ele. Se perder, você vira parte de sua lenda.

**Bosses:**
- 🗡️ **Caboclo** — fura e elimina suas cartas
- 🎭 **Papa-figo** — rouba suas criaturas

**Matinta Pereira** — Bruxa que oferece bênçãos para suas criaturas: asas, dano bifurcado ou imortalidade.

**Cangaceiros** — Aparecem em uma fogueira e oferecem +1 de ataque ou vida para uma de suas cartas.

---

## 🎒 Itens

| Item | Efeito |
|---|---|
| 🔪 Peixeira | Corta instantaneamente a carta inimiga |
| 🥃 Cantil | Recupera +1 de vida |
| 🍺 Abridor de cerveja | Abre uma tampinha extra para a balança |
| 🍾 Garrafa com carta | Libera uma Perna Cabeluda extra |

---

## 🗺️ Mapas

O jogo é dividido em três grandes áreas, cada uma com sua própria ambientação:

1. **Tutorial** — batalhas introdutórias, coleta de cartas e itens
2. **Território do Caboclo** — muda a temática visual e as ameaças do mapa
3. **Território do Papa-figo (véi do saco)** — mapa final, com estilo visual mais aterrorizante

Eventos especiais espalhados pelo mapa incluem paradas com **Matinta Pereira** (selos de melhoria) e fogueiras com **Cangaceiros** (apostas de fortalecimento de cartas).

---

## ⚙️ Detalhes técnicos

- **Resolução base:** 384x216 (zoom 4x)
- **Cartas:** 36x44 px (144x176 em zoom 4x)
- **Itens:** sprites de 20x20 px
- **Arte:** Pixel Art + ilustrações inspiradas em xilogravura
- **Controle:** Point & Click

### Bibliotecas utilizadas

| Biblioteca | Uso no projeto |
|---|---|
| **Pygame** | Motor gráfico: janela, renderização, FPS, input do jogador e hitboxes (`pygame.Rect`) |
| **random** | RNG para embaralhar decks, sortear itens e definir cartas disponíveis |
| **math** | Cálculos geométricos para animações suaves das cartas |
| **os** | Gerenciamento de caminhos de arquivo multiplataforma (`os.path.join`) |

---

## 🧩 Mecânicas de carta

Efeitos passivos e ativos implementados: `Voar`, `Mergulhador`, `Sangue`, `Escudo`, `Morte Instantânea (Mortal)`, `Ataque Triplo`, `Espinho (Dano de volta)`.

---

## 👨‍💻 Equipe

| Integrante | Responsabilidade |
|---|---|
| **Bruno Cordeiro** | Menu principal, sistema de colecionáveis, cartas do narrador e eventos de Cangaceiros |
| **Maria Luiza** | Arte geral, interfaces, polimento visual e eventos da Matinta Pereira |
| **Caio César** | Organização do projeto, arquitetura de programação do combate e estatísticas |
| **Vicente** | Mapas, lore/narrativa, trilha sonora e boss "Caboclo" |
| **João Lucas** | Documentação técnica e correção de bugs |
| **Matheus Luiz** | Design de cartas, efeitos visuais, som, créditos e boss "Papa-figo" |

---

## 🎓 Lições aprendidas

- Reduzir o escopo inicial (bastante ambicioso) foi essencial para viabilizar a entrega
- Divisão de tarefas precisa ser flexível — algumas funções naturalmente exigem mais tempo que outras
- Organização de arquivos desde o início evita retrabalho quando o projeto cresce em complexidade

---

## 📌 Status do projeto

- [x] Sistema de combate (dano, sacrifício, balança)
- [x] Baralho de criaturas do folclore
- [x] Roteiro e diálogos do Narrador
- [x] Bosses Caboclo e Papa-figo
- [x] Eventos de mapa (Matinta Pereira, Cangaceiros, mochilas)
- [x] Itens consumíveis
- [x] Interface gráfica e resolução final

---

*Projeto acadêmico desenvolvido para a disciplina de Introdução à Programação — Centro de Informática, UFPE.*
