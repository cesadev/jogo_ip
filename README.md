🃏 Ouro e Cachaça — O Tabuleiro das Almas


Um roguelike deckbuilder de terror-psicológico inspirado em Inscryption, ambientado no folclore nordestino brasileiro.


Desenvolvido no Centro de Informática da Universidade Federal de Pernambuco (UFPE), como projeto da disciplina de Introdução à Programação.


📖 Sobre o jogo

Você se senta em um bar para jogar cartas contra o Matheus, um narrador que já perdeu a conta das almas que coleciona dos perdedores. Se vencer, explora o mapa em busca de novas criaturas. Se perder, sua alma passa a fazer parte de um cortejo fantasmagórico.

O jogo mistura TCG, roguelike deckbuilder e terror psicológico, em um formato Point & Click, com arte em Pixel Art e ilustrações inspiradas em xilogravura.

Objetivo final: derrotar os três bosses e conquistar os totens do Saci.


❤️ Vida: representada por dois copos de shot
⚖️ Pontuação/dano: medidos por tampinhas de cerveja em uma balança
💰 Cada criatura possui um custo em ouro para ser jogada



🃏 Criaturas

NomeAtaqueVidaCustoEfeitoAcauã232Dano diretoAnhangá374—Boitatá212Morte instantâneaCaboclo D'água111Se escondeCacto030—Capelobo121—Chupa Cabra111Dano de sangueCobra Coral221Morte instantâneaCuca222Shell (escudo)Comadre Fulozinha112Dano em 3 direçõesCurupira322—La Ursa463—Leão-do-Norte774—Mula Sem-Cabeça343—Perna Cabeluda010SacrifícioTimbu221Dano de volta


👥 Personagens

O Matheus — Narrador que já perdeu a conta de almas. Você o encontra em um bar e joga com ele. Se perder, você vira parte de sua lenda.

Bosses:


🗡️ Caboclo — fura e elimina suas cartas
🎭 Papa-figo — rouba suas criaturas
👹 Papangu — inverte seus ataques em dano direto (uma vez a cada 3 rodadas)


Matinta Pereira — Bruxa que oferece bênçãos para suas criaturas: asas, dano bifurcado ou imortalidade.

Cangaceiros — Aparecem em uma fogueira e oferecem +1 de ataque ou vida para uma de suas cartas.


🎒 Itens

ItemEfeito🔪 PeixeiraCorta instantaneamente a carta inimiga🥃 CantilRecupera +1 de vida🍺 Abridor de cervejaAbre uma tampinha extra para a balança🍾 Garrafa com cartaLibera uma Perna Cabeluda extra


🗺️ Mapas

O jogo é dividido em três grandes áreas, cada uma com sua própria ambientação:


Tutorial — batalhas introdutórias, coleta de cartas e itens
Território do Caboclo — muda a temática visual e as ameaças do mapa
Território do Papa-figo (véi do saco) — mapa final, com estilo visual mais aterrorizante


Eventos especiais espalhados pelo mapa incluem paradas com Matinta Pereira (selos de melhoria) e fogueiras com Cangaceiros (apostas de fortalecimento de cartas).


⚙️ Detalhes técnicos


Resolução base: 384x216 (zoom 4x)
Cartas: 36x44 px (144x176 em zoom 4x)
Itens: sprites de 20x20 px
Arte: Pixel Art + ilustrações inspiradas em xilogravura
Controle: Point & Click


Bibliotecas utilizadas

BibliotecaUso no projetoPygameMotor gráfico: janela, renderização, FPS, input do jogador e hitboxes (pygame.Rect)randomRNG para embaralhar decks, sortear itens e definir cartas disponíveismathCálculos geométricos para animações suaves das cartasosGerenciamento de caminhos de arquivo multiplataforma (os.path.join)


🧩 Mecânicas de carta

Efeitos passivos e ativos implementados: Voar, Mergulhador, Sangue, Escudo, Morte Instantânea (Mortal), Ataque Triplo, Espinho (Dano de volta).


👨‍💻 Equipe

IntegranteResponsabilidadeBruno CordeiroMenu principal, sistema de colecionáveis, cartas do narrador e eventos de CangaceirosMaria LuizaArte geral, interfaces, polimento visual e eventos da Matinta PereiraCaio CésarOrganização do projeto, arquitetura de programação do combate e estatísticasVicenteMapas, lore/narrativa, trilha sonora e boss "Caboclo"João LucasDocumentação técnica e correção de bugsMatheus LuizDesign de cartas, efeitos visuais, som, créditos e boss "Papa-figo"


🎓 Lições aprendidas


Reduzir o escopo inicial (bastante ambicioso) foi essencial para viabilizar a entrega
Divisão de tarefas precisa ser flexível — algumas funções naturalmente exigem mais tempo que outras
Organização de arquivos desde o início evita retrabalho quando o projeto cresce em complexidade



📌 Status do projeto


 Sistema de combate (dano, sacrifício, balança)
 Baralho de criaturas do folclore
 Roteiro e diálogos do Narrador
 Bosses Caboclo e Papa-figo
 Eventos de mapa (Matinta Pereira, Cangaceiros, mochilas)
 Itens consumíveis
 Interface gráfica e resolução final



Projeto acadêmico desenvolvido para a disciplina de Introdução à Programação — Centro de Informática, UFPE.
