import pygame
import math
import random
from cena_base import CenaBase
from cartas import Carta
from itens import lista_itens


class CenaCombate(CenaBase):
    def __init__(self, tela, deck_jogador, dados_da_fase, itens_jogador_global,
                 vida_player, imagens_versos, imagens_cartas, imagens_ui, nome_fase):
        super().__init__(tela)
        self.imagens_cartas = imagens_cartas
        self.imagens_versos = imagens_versos
        self.imagens_ui = imagens_ui

        self.indice_dicionario = 0

        self.paginas_dicionario = [
            pygame.transform.scale(pygame.image.load("dicionario/abridor.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/cantil.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/peixeira.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/garrafa.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/ataquetriplo.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/escudo.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/espinho.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/mergulhador.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/mortal.png").convert_alpha(),(321, 240)),
            pygame.transform.scale(pygame.image.load("dicionario/sangue.png").convert_alpha(),(321, 240))
        ]


        # --- Dados da fase ---
        self.script_inimigo = dados_da_fase.get("script_inimigo", {})
        self.nome_fase = nome_fase

        # --- Imagens ---
        self.img_verso_deck = imagens_versos.get("verso_carta")
        self.img_verso_pernas = imagens_versos.get("verso_perna")
        self.img_campainha = imagens_ui.get("campainha")
        self.img_copo1 = imagens_ui.get("copo1")
        self.img_copo2 = imagens_ui.get("copo2")

        # --- Deck e mão inicial ---
        self.deck_jogador = [
            Carta(c["nome"], c.get("dano", c.get("poder", 0)), c["vida"],
                  c.get("imagem"), c.get("custo_sangue", 0), c.get("valor_sacrificio", 1), c.get("selos", []))
            if isinstance(c, dict) else c
            for c in deck_jogador
        ]

        self.mao_jogador = []
        # ele começa com uma perna cabeluda sempre, na main rola um embaralhamento com a biblioteca random no deck global, assim, as cartas ficam dinamicas e a gente consegue aplicar essa diferenciação
        self.mao_jogador.append(Carta("Perna Cabeluda", 0, 1, imagens_cartas.get("perna"), 0, 1))
        # Tenta puxar uma carta de custo 1 do deck
        carta_custo_1 = None
        for i, carta in enumerate(self.deck_jogador):
            if carta.custo_sangue == 1:
                carta_custo_1 = self.deck_jogador.pop(i)
                break
        if carta_custo_1 is not None:
            self.mao_jogador.append(carta_custo_1)
        elif len(self.deck_jogador) > 0:
            self.mao_jogador.append(self.deck_jogador.pop(0))
        if len(self.deck_jogador) > 0:
            self.mao_jogador.append(self.deck_jogador.pop(0))

        # --- Estado do turno ---
        self.turno_atual = "jogador"
        self.turno_global = 1
        self.ja_comprou_neste_turno = False
        self.estado_atual = "fase_compra"

        # --- Seleção de carta ---
        self.carta_selecionada = None
        self.index_carta_selecionada = None
        self.sangue_necessario = 0
        self.slots_sacrificados_pendentes = []
        self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

        # --- Resolução de combate ---
        self.fase_resolucao = None
        self.idx_atacante_atual = 0
        self.progresso_ataque = 0.0
        self.dano_aplicado = False
        self.velocidade_ataque = 0.004

        # --- Efeitos visuais ---
        self.flash_aliado = [0, 0, 0, 0]
        self.flash_inimigo = [0, 0, 0, 0]
        self.animacoes = []

        # --- Slots e filas ---
        self.slots_aliados = [None, None, None, None]
        self.slots_inimigos = [None, None, None, None]
        self.filas_espera_inimigas = [[], [], [], []]

        # --- Itens ---
        self.itens_jogador = itens_jogador_global
        self.imagens_itens = {}
        for nome, dados in lista_itens.items():
            caminho = dados.get("imagem")
            if caminho:
                try:
                    img = pygame.image.load(caminho).convert_alpha()
                    self.imagens_itens[nome] = pygame.transform.scale(img, (80, 80))
                except FileNotFoundError:
                    self.imagens_itens[nome] = None
        self.aguardando_alvo_peixeira = False

        # --- Progresso do jogo ---
        self.pernas_disponiveis = 10
        self.vida_player = vida_player
        self.peso_balanca = 0

        # --- Obstáculos iniciais ---
        for obstaculo in dados_da_fase.get("obstaculos_iniciais", []):
            nome_obs = obstaculo["nome"]
            imagem_obs = obstaculo.get("imagem") or imagens_cartas.get(nome_obs)
            carta_obs = Carta(
                nome_obs, obstaculo.get("dano", 0), obstaculo["vida"],
                imagem_obs, obstaculo.get("custo_sangue", 0), obstaculo.get("valor_sacrificio", 0), obstaculo.get("selos", []))
            self.slots_inimigos[obstaculo["slot"]] = carta_obs

        self._carregar_intencoes_inimigas_do_turno(1)
        try:
            self.posicao_musica_anterior_ms = pygame.mixer.music.get_pos()
        except pygame.error:
            self.posicao_musica_anterior_ms = 0
        self._tocar_musica_da_cena("Musicas/Cabloco.mp3")

        # --- Dados visuais aleatórios (bagunça das pilhas) ---
        def gerar_bagunca(quantidade):
            return [(random.randint(-2, 2), random.randint(-2, 2), random.uniform(-5, 5))
                    for _ in range(quantidade)]

        self.bagunca_pernas = gerar_bagunca(15)
        self.bagunca_deck = gerar_bagunca(40)

        # --- Fundo ---
        largura_tela, altura_tela = tela.get_size()
        try:
            imagem_original = pygame.image.load("cenarios/combate.png").convert()
            self.imagem_fundo = pygame.transform.scale(imagem_original, (largura_tela, altura_tela))
        except FileNotFoundError:
            self.imagem_fundo = pygame.Surface((largura_tela, altura_tela))
            self.imagem_fundo.fill((30, 30, 30))

        # --- Rects fixos de UI ---
        self.campainha_rect = pygame.Rect(172, 50, 120, 120)
        self.comprar_pernas_rect = pygame.Rect(1190, 465, 144, 176)
        self.comprar_deck_rect = pygame.Rect(1350, 465, 144, 176)

        # BOTOES DO DICIONARIO
        self.descricao_left_rect = pygame.Rect(1150, 130, 40, 40)
        self.descricao_right_rect = pygame.Rect(1450, 130, 40, 40)

        # --- Hitboxes (preenchidas em atualizar()) ---
        self.hitboxes_mao = []
        self.hitboxes_slots_aliados = []
        self.hitboxes_slots_inimigos = []
        self.hitboxes_slots_espera = []
        self.hitboxes_vida = []
        self.hitboxes_itens = []

        # --- Fontes e mensagem ---
        self.mensagem_debug = dados_da_fase.get("mensagem_inicio", "Início do Turno: Jogue suas cartas!")
        self.debug = pygame.font.SysFont("Arial", 36)
        self.fonte_cartas = pygame.font.SysFont("Arial", 20)
        self.fonte_vida = pygame.font.SysFont("Arial", 30, bold=True)
        self.fonte_mini = pygame.font.SysFont("Arial", 14)
        self.index_foco = None

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _carregar_img(self, nome, scale=(144, 176), convert=False):
        try:
            img = pygame.image.load(f"cartas/{nome}.png")
            img = img.convert() if convert else img.convert_alpha()
            return pygame.transform.scale(img, scale)
        except FileNotFoundError:
            return None

    def _tocar_musica_da_cena(self, caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _carregar_intencoes_inimigas_do_turno(self, turno):
        """Lê o script do turno e organiza tudo"""
        acoes = self.script_inimigo.get(turno, [])
        for comando in acoes:
            if not isinstance(comando, dict):
                continue
            if comando.get("acao") != "jogar_carta":
                continue
            slot = comando["slot"]
            c = comando["carta"]
            if isinstance(c, dict):
                nome_inimigo = c["nome"]
                imagem_inimigo = c.get("imagem")
                if imagem_inimigo is None:
                    try:
                        img_original = pygame.image.load(f"cartas/{nome_inimigo}.png").convert_alpha()
                        imagem_inimigo = pygame.transform.scale(img_original, (144, 176))
                    except FileNotFoundError:
                        imagem_inimigo = None
                carta_obj = Carta(
                    nome_inimigo, c.get("dano", c.get("poder", 0)), c["vida"],
                    imagem_inimigo, c.get("custo_sangue", 0), c.get("valor_sacrificio", 1), c.get("selos", [])
                )
            else:
                carta_obj = c.copy()
            self.filas_espera_inimigas[slot].append(carta_obj)

    # -------------------------------------------------------------------------
    # Lógica de combate
    # -------------------------------------------------------------------------

    def processar_ataque(self, carta_atacante, carta_alvo):
        """Aplica dano de uma carta atacante em uma carta alvo, respeitando selos."""
        if "escudo" in carta_alvo.selos:
            carta_alvo.selos.remove("escudo")
            return

        dano = carta_atacante.dano

        if "mortal" in carta_atacante.selos:
            dano = 999

        # mergulhador e voar atacam direto a balança, independente de alvo
        if "mergulhador" in carta_atacante.selos or "voar" in carta_atacante.selos:
            self.peso_balanca += dano
            return

        carta_alvo.vida -= dano

        if "espinhos" in carta_alvo.selos:
            carta_atacante.vida -= 1

    def aplicar_efeito_item(self, nome_item):
        """Ativa o efeito do item consumível e atualiza a mensagem."""
        item_para_remover = None
        for item in self.itens_jogador:
            nome_atual = item["nome"] if isinstance(item, dict) else item.nome
            if nome_atual == nome_item:
                item_para_remover = item
                break
        if item_para_remover is not None:
            self.itens_jogador.remove(item_para_remover)

        if nome_item == "peixeira":
            self.aguardando_alvo_peixeira = True
            self.mensagem_debug = "Peixeira pronta! Clique em uma carta inimiga para destruir."
            return  # item só é removido após escolher o alvo

        elif nome_item == "cantil":
            self.vida_player += 1
            self.mensagem_debug = "Glup! +1 de vida."

        elif nome_item == "abridor":
            self.peso_balanca += 5
            self.mensagem_debug = "Balança puxou 5 pontos!"

        elif nome_item == "garrafa":
            self.pernas_disponiveis += 1
            self.mensagem_debug = "Uma perna extra adicionada!"

        # Remove o item após uso (exceto Peixeira, que espera o alvo)
        if {"nome": nome_item} in self.itens_jogador:
            self.itens_jogador.remove({"nome": nome_item})

    # Processamento de evento
    def processar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos_mouse = event.pos

                # Checa se o jogador clicou para passar a página do dicionário
                if self.descricao_left_rect.collidepoint(pos_mouse):
                    if self.indice_dicionario > 0:
                        self.indice_dicionario -= 1
                # O continue garante que esse clique não afete outras coisas na tela
                        continue 
            
        # Verifica colisão com a seta da direita (para avançar página)
                elif self.descricao_right_rect.collidepoint(pos_mouse):
                    if self.indice_dicionario < len(self.paginas_dicionario) - 1:
                        self.indice_dicionario += 1
                    continue

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos_mouse = pygame.mouse.get_pos()
            # --- Botão direito: cancelar ação atual ---
            if event.button == 3:
                if self.estado_atual in ["sacrificio", "posicionamento"]:
                    self.estado_atual = "normal"
                    self.carta_selecionada = None
                    self.index_carta_selecionada = None
                    self.slots_sacrificados_pendentes.clear()
                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]
                    self.mensagem_debug = "Ação cancelada."
                continue

            if event.button != 1:
                continue

            # --- Peixeira aguardando alvo ---
            if self.aguardando_alvo_peixeira:
                for rect_slot, i in self.hitboxes_slots_inimigos:
                    if rect_slot.collidepoint(pos_mouse):
                        if self.slots_inimigos[i] is not None:
                            self.slots_inimigos[i] = None
                            self.aguardando_alvo_peixeira = False
                            self.mensagem_debug = "Peixeira usada! Inimigo eliminado."
                            if {"nome": "Peixeira"} in self.itens_jogador:
                                self.itens_jogador.remove({"nome": "Peixeira"})
                        else:
                            self.mensagem_debug = "Slot vazio. Tente novamente."
                        return
                return  # clicou fora dos slots — ignora enquanto aguarda alvo

            # --- Clique em itens ---
            for rect, nome_item in self.hitboxes_itens:
                if rect.collidepoint(pos_mouse):
                    self.aplicar_efeito_item(nome_item)
                    return

            # --- Fora do turno do jogador: ignora ---
            if self.turno_atual != "jogador":
                continue

            # --- Comprar Perna ---
            if self.comprar_pernas_rect.collidepoint(pos_mouse):
                if self.ja_comprou_neste_turno:
                    self.mensagem_debug = "Só pode comprar uma carta por turno."
                elif self.pernas_disponiveis > 0:
                    self.mao_jogador.append(
                        Carta("Perna Cabeluda", 0, 1, self.imagens_cartas.get("perna"), 0, 1)
                    )
                    self.pernas_disponiveis -= 1
                    self.ja_comprou_neste_turno = True
                    self.estado_atual = "normal"
                    self.mensagem_debug = "Comprou uma Perna."
                continue

            # --- Comprar do Deck ---
            if self.comprar_deck_rect.collidepoint(pos_mouse):
                if self.ja_comprou_neste_turno:
                    self.mensagem_debug = "Só pode comprar uma carta por turno."
                elif len(self.deck_jogador) > 0:
                    carta = self.deck_jogador.pop(0)
                    self.mao_jogador.append(carta)
                    self.ja_comprou_neste_turno = True
                    self.estado_atual = "normal"
                    self.mensagem_debug = f"Comprou {carta.nome}"
                continue

            # --- Campainha: iniciar combate ---
            if self.campainha_rect.collidepoint(pos_mouse):
                if self.estado_atual == "fase_compra":
                    self.mensagem_debug = "Compre uma carta antes."
                elif not self.ja_comprou_neste_turno and self.turno_global > 1:
                    self.mensagem_debug = "Você precisa comprar uma carta primeiro."
                else:
                    self.turno_atual = "resolvendo_combate"
                    self.fase_resolucao = "aliados"
                    self.idx_atacante_atual = 0
                    self.progresso_ataque = 0.0
                    self.dano_aplicado = False
                    self.mensagem_debug = "Combate iniciado."
                continue

            # --- Ações durante fase_compra ---
            if self.estado_atual == "fase_compra":
                self.mensagem_debug = "Compre uma carta primeiro."
                continue

            # --- Estado: normal (selecionar carta da mão) ---
            if self.estado_atual == "normal":
                if not self.ja_comprou_neste_turno and self.turno_global > 1:
                    self.mensagem_debug = "Você precisa comprar uma carta primeiro."
                    continue
                if self.index_foco is None or self.index_foco >= len(self.mao_jogador):
                    continue

                carta_tentativa = self.mao_jogador[self.index_foco]
                custo = carta_tentativa.custo_sangue
                sangue_disponivel = sum(
                    (3 if "sangue" in carta.selos else carta.valor_sacrificio)
                    for carta in self.slots_aliados if carta is not None
                )   

                if custo > sangue_disponivel:
                    self.mensagem_debug = f"Necessário {custo} sangue."
                    continue

                self.index_carta_selecionada = self.index_foco
                self.carta_selecionada = carta_tentativa

                if custo > 0:
                    self.estado_atual = "sacrificio"
                    self.sangue_necessario = custo
                    self.slots_sacrificados_pendentes.clear()
                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]
                    self.mensagem_debug = f"Selecione sacrifícios ({custo})"
                else:
                    self.estado_atual = "posicionamento"
                    self.mensagem_debug = "Escolha um slot."

            # --- Estado: sacrifício ---
            elif self.estado_atual == "sacrificio":
                clicou_valido = False
                for rect_slot, i in self.hitboxes_slots_aliados:
                    if rect_slot.collidepoint(pos_mouse):
                        clicou_valido = True
                        if (self.slots_aliados[i] is not None
                                and i not in self.slots_sacrificados_pendentes):
                            self.slots_sacrificados_pendentes.append(i)
                            sangue_acumulado = sum(
                                (3 if "sangue" in self.slots_aliados[idx].selos else self.slots_aliados[idx].valor_sacrificio)
                                for idx in self.slots_sacrificados_pendentes
                            )
                            if sangue_acumulado >= self.sangue_necessario:
                                self.estado_atual = "posicionamento"
                                self.mensagem_debug = "Sacrifício concluído."
                        break

                if not clicou_valido:
                    self.estado_atual = "normal"
                    self.carta_selecionada = None
                    self.index_carta_selecionada = None
                    self.slots_sacrificados_pendentes.clear()
                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

            # --- Estado: posicionamento ---
            elif self.estado_atual == "posicionamento":
                clicou_valido = False
                for rect_slot, i in self.hitboxes_slots_aliados:
                    if rect_slot.collidepoint(pos_mouse):
                        clicou_valido = True
                        slot_valido = (
                            self.slots_aliados[i] is None
                            or i in self.slots_sacrificados_pendentes
                        )
                        animacao_no_slot = any(
                            anim["slot_destino"] == i for anim in self.animacoes
                        )
                        if slot_valido and not animacao_no_slot:
                            rect_mao, _, _ = self.hitboxes_mao[self.index_carta_selecionada]

                            for idx in self.slots_sacrificados_pendentes:
                                self.slots_aliados[idx] = None
                                self.fade_sacrificio[idx] = 0.0
                            self.slots_sacrificados_pendentes.clear()

                            self.animacoes.append({
                                "carta": self.carta_selecionada.copy(),
                                "pos_inicial": (rect_mao.x, rect_mao.y),
                                "pos_final": (rect_slot.x, rect_slot.y),
                                "pos_atual": [rect_mao.x, rect_mao.y],
                                "progresso": 0.0,
                                "slot_destino": i
                            })

                            self.mao_jogador.pop(self.index_carta_selecionada)
                            self.estado_atual = "normal"
                            self.carta_selecionada = None
                            self.index_carta_selecionada = None
                            self.mensagem_debug = "Carta posicionada."
                        break

                if not clicou_valido:
                    self.estado_atual = "normal"
                    self.carta_selecionada = None
                    self.index_carta_selecionada = None
                    self.slots_sacrificados_pendentes.clear()
                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

    # -------------------------------------------------------------------------
    # Atualização
    # -------------------------------------------------------------------------

    def atualizar(self, dt):
        # Flashs e fade de sacrifício
        for idx in range(4):
            if self.flash_aliado[idx] > 0:
                self.flash_aliado[idx] -= dt
            if self.flash_inimigo[idx] > 0:
                self.flash_inimigo[idx] -= dt
            if idx in self.slots_sacrificados_pendentes:
                self.fade_sacrificio[idx] = min(255.0, self.fade_sacrificio[idx] + dt * 0.25)
            else:
                self.fade_sacrificio[idx] = 0.0

        # Animações de carta voando para o slot
        for anim in self.animacoes[:]:
            anim["progresso"] += dt * 0.0035
            if anim["progresso"] >= 1.0:
                self.slots_aliados[anim["slot_destino"]] = anim["carta"]
                self.animacoes.remove(anim)
            else:
                t = anim["progresso"]
                fator_suave = 1 - pow(1 - t, 3)
                x0, y0 = anim["pos_inicial"]
                x1, y1 = anim["pos_final"]
                anim["pos_atual"][0] = x0 + (x1 - x0) * fator_suave
                anim["pos_atual"][1] = y0 + (y1 - y0) * fator_suave

        # Resolução de combate
        if self.turno_atual == "resolvendo_combate":
            self._atualizar_resolucao(dt)

        # Hitboxes de vida
        self.hitboxes_vida.clear()
        pos_x_vida, pos_y_vida, tamanho_vida, espacamento_vida = 145, 505, 80, 20
        for i in range(self.vida_player):
            rect = pygame.Rect(
                pos_x_vida + i * (tamanho_vida + espacamento_vida),
                pos_y_vida, tamanho_vida, tamanho_vida
            )
            self.hitboxes_vida.append(rect)

        # Hitboxes dos slots
        self.hitboxes_slots_aliados.clear()
        self.hitboxes_slots_inimigos.clear()
        self.hitboxes_slots_espera.clear()
        pos_x_slot = 458
        y_espera, y_inimigos, y_aliados = 32, 158, 408
        espacamento_horizontal = 160
        largura_padrao, altura_padrao, altura_mini = 144, 176, 101

        for i in range(4):
            self.hitboxes_slots_espera.append(
                (pygame.Rect(pos_x_slot, y_espera, largura_padrao, altura_mini), i)
            )
            self.hitboxes_slots_inimigos.append(
                (pygame.Rect(pos_x_slot, y_inimigos, largura_padrao, altura_padrao), i)
            )
            self.hitboxes_slots_aliados.append(
                (pygame.Rect(pos_x_slot, y_aliados, largura_padrao, altura_padrao), i)
            )
            pos_x_slot += espacamento_horizontal

        # Hitboxes de itens
        self.hitboxes_itens.clear()
        pos_x_item = 1190
        for item in self.itens_jogador[:4]:  # aumenta o limite pra ver quantos chegam
            nome_item = item["nome"] if isinstance(item, dict) else item.nome
            self.hitboxes_itens.append((pygame.Rect(pos_x_item, 330, 100, 100), nome_item))
            pos_x_item += 140

        # Hitboxes da mão
        self.hitboxes_mao.clear()
        qtd_cartas = len(self.mao_jogador)
        if qtd_cartas > 0:
            largura_tela = self.tela.get_width()
            margem_tela = 400
            espacamento = 0 if qtd_cartas == 1 else max(
                30, min(80, (largura_tela - margem_tela - largura_padrao) // (qtd_cartas - 1))
            )
            largura_total_mao = (qtd_cartas - 1) * espacamento + largura_padrao
            pos_x_inicial_mao = (largura_tela - largura_total_mao) // 2

            pos_mouse = pygame.mouse.get_pos()
            self.index_foco = None

            rects_virtuais = [
                pygame.Rect(pos_x_inicial_mao + i * espacamento, 650, largura_padrao, altura_padrao)
                for i in range(qtd_cartas)
            ]

            if self.turno_atual == "jogador" and self.estado_atual == "normal":
                for i in reversed(range(qtd_cartas)):
                    if rects_virtuais[i].collidepoint(pos_mouse):
                        self.index_foco = i
                        break

            for i, carta in enumerate(self.mao_jogador):
                rect = rects_virtuais[i].copy()
                if i == self.index_foco:
                    rect.y -= 40
                self.hitboxes_mao.append((rect, carta, i))

    def _atualizar_resolucao(self, dt):
        """Gerencia as fases aliados → pre_inimigo → inimigos."""
        if self.fase_resolucao == "aliados":
            # Avança até o próximo aliado que ataca
            while self.idx_atacante_atual < 4:
                card = self.slots_aliados[self.idx_atacante_atual]
                if card is not None and card.dano > 0:
                    break
                self.idx_atacante_atual += 1
                self.progresso_ataque = 0.0
                self.dano_aplicado = False

            if self.idx_atacante_atual >= 4:
                # Fase aliada encerrada: coloca reforços inimigos
                for i in range(4):
                    if self.slots_inimigos[i] is None and self.filas_espera_inimigas[i]:
                        self.slots_inimigos[i] = self.filas_espera_inimigas[i].pop(0)
                self.fase_resolucao = "pre_inimigo"
                self.mensagem_debug = "Turno Aliado encerrado. Inimigo preparando jogadas..."
                return

            card_atacante = self.slots_aliados[self.idx_atacante_atual]
            self.progresso_ataque += dt * self.velocidade_ataque

            if self.progresso_ataque >= 0.5 and not self.dano_aplicado:
                # Transforma todos os selos do atacante em minúsculas e sem espaços para a verificação
                selos_atk = [s.lower().strip() for s in card_atacante.selos]
                
                alvos = [self.idx_atacante_atual]
                if "ataque_triplo" in selos_atk:
                    alvos = [i for i in [self.idx_atacante_atual - 1, self.idx_atacante_atual, self.idx_atacante_atual + 1] if 0 <= i <= 3]
                
                for alvo_idx in alvos:
                    if card_atacante.vida <= 0:
                        break  
                        
                    card_alvo = self.slots_inimigos[alvo_idx]
                    
                    # Selo Voar ou Mergulhador
                    if "voar" in selos_atk or "mergulhador" in selos_atk:
                        self.peso_balanca += card_atacante.dano
                        
                    elif card_alvo is not None:
                        selos_alvo = [s.lower().strip() for s in card_alvo.selos]
                        
                        if "mergulhador" not in selos_alvo:
                            dano_causado = 999 if "mortal" in selos_atk else card_atacante.dano
                            
                            # Selo Escudo
                            if "escudo" in selos_alvo:
                                selo_exato = next((s for s in card_alvo.selos if s.lower().strip() == "escudo"), None)
                                if selo_exato:
                                    card_alvo.selos.remove(selo_exato)
                                dano_causado = 0
                                
                            card_alvo.vida -= dano_causado
                            self.flash_inimigo[alvo_idx] = 200
                            
                            # Selo Espinhos
                            if "espinhos" in selos_alvo and dano_causado > 0:
                                card_atacante.vida -= 1
                                
                            if card_alvo.vida <= 0:
                                self.slots_inimigos[alvo_idx] = None
                        else:
                            # Se o alvo é mergulhador, ignora e bate na balança
                            self.peso_balanca += card_atacante.dano
                    else:
                        self.peso_balanca += card_atacante.dano
                        
                if card_atacante.vida <= 0:
                    self.slots_aliados[self.idx_atacante_atual] = None
                
    
                if self.peso_balanca >= 5:
                    self.mensagem_debug = "VITÓRIA! A balança tombou totalmente."
                    self.terminou = True
                    self.proxima_cena = "mapa"
                    return
                
                    
                
                    
                self.dano_aplicado = True

            if self.progresso_ataque >= 1.0:
                self.idx_atacante_atual += 1
                self.progresso_ataque = 0.0
                self.dano_aplicado = False

        elif self.fase_resolucao == "pre_inimigo":
            self.fase_resolucao = "inimigos"
            self.idx_atacante_atual = 0
            self.progresso_ataque = 0.0
            self.dano_aplicado = False
            self.mensagem_debug = "Inimigos avançam para atacar!"

        elif self.fase_resolucao == "inimigos":
            # Avança até o próximo inimigo que ataca
            while self.idx_atacante_atual < 4:
                card = self.slots_inimigos[self.idx_atacante_atual]
                if card is not None and card.dano > 0:
                    break
                self.idx_atacante_atual += 1
                self.progresso_ataque = 0.0
                self.dano_aplicado = False

            if self.idx_atacante_atual >= 4:
                # Fase inimiga encerrada: verifica derrota
                if self.peso_balanca <= -5:
                    self.vida_player -= 1

                    if "tutorial" in self.nome_fase:
                        if self.vida_player <= 0:
                            self.mensagem_debug = "Você perdeu as duas vidas do tutorial."
                            self.terminou = True
                            self.proxima_cena = "fim_tutorial"
                            return

                        self.mensagem_debug = "Você perdeu uma vida no tutorial. Voltando ao mapa..."
                        self.terminou = True
                        self.proxima_cena = "mapa"
                        return

                    if self.vida_player <= 0:
                        self.mensagem_debug = "Você sucumbiu..."
                        self.terminou = True
                        self.proxima_cena = "game_over"
                        return
                    else:
                        self.mensagem_debug = "Você perdeu a rodada, retornando ao mapa..."
                        self.terminou = True
                        self.proxima_cena = "mapa"
                        return

                # Próximo turno do jogador
                self._carregar_intencoes_inimigas_do_turno(self.turno_global + 1)
                self.turno_global += 1
                self.turno_atual = "jogador"
                self.ja_comprou_neste_turno = False
                self.estado_atual = "fase_compra"
                self.fase_resolucao = None
                return

            card_atacante = self.slots_inimigos[self.idx_atacante_atual]
            self.progresso_ataque += dt * self.velocidade_ataque

            if self.progresso_ataque >= 0.5 and not self.dano_aplicado:
                selos_atk = [s.lower().strip() for s in card_atacante.selos]
                
                alvos = [self.idx_atacante_atual]
                if "ataque_triplo" in selos_atk:
                    alvos = [i for i in [self.idx_atacante_atual - 1, self.idx_atacante_atual, self.idx_atacante_atual + 1] if 0 <= i <= 3]
                
                for alvo_idx in alvos:
                    if card_atacante.vida <= 0:
                        break 
                        
                    card_alvo = self.slots_aliados[alvo_idx]
                    
                    if "voar" in selos_atk or "mergulhador" in selos_atk:
                        self.peso_balanca -= card_atacante.dano
                        
                    elif card_alvo is not None:
                        selos_alvo = [s.lower().strip() for s in card_alvo.selos]
                        
                        if "mergulhador" not in selos_alvo:
                            dano_causado = 999 if "mortal" in selos_atk else card_atacante.dano
                            
                            if "escudo" in selos_alvo:
                                selo_exato = next((s for s in card_alvo.selos if s.lower().strip() == "escudo"), None)
                                if selo_exato:
                                    card_alvo.selos.remove(selo_exato)
                                dano_causado = 0
                                
                            card_alvo.vida -= dano_causado
                            self.flash_aliado[alvo_idx] = 200
                            
                            if "espinhos" in selos_alvo and dano_causado > 0:
                                card_atacante.vida -= 1
                                
                            if card_alvo.vida <= 0:
                                self.slots_aliados[alvo_idx] = None
                        else:
                            self.peso_balanca -= card_atacante.dano
                    else:
                        self.peso_balanca -= card_atacante.dano
                        
                if card_atacante.vida <= 0:
                    self.slots_inimigos[self.idx_atacante_atual] = None

                self.dano_aplicado = True

            if self.progresso_ataque >= 1.0:
                self.idx_atacante_atual += 1
                self.progresso_ataque = 0.0
                self.dano_aplicado = False


    def desenhar(self):
        self.tela.blit(self.imagem_fundo, (0, 0))
        # dicionario
        img_atual = self.paginas_dicionario[self.indice_dicionario]
        rect_img = img_atual.get_rect(center=(1320, 170)) 
        self.tela.blit(img_atual, rect_img)


        # Balança
        centro_x, centro_y, raio = 240, 350, 128
        angulo_rad = math.radians(self.peso_balanca * 2.5)
        dx, dy = math.cos(angulo_rad) * raio, math.sin(angulo_rad) * raio
        esq_x, esq_y = centro_x - dx, centro_y + dy
        dir_x, dir_y = centro_x + dx, centro_y - dy

        pygame.draw.rect(self.tela, (90, 60, 30), (centro_x - 10, centro_y, 20, 80))
        pygame.draw.polygon(self.tela, (70, 40, 20), [
            (centro_x - 30, centro_y + 80), (centro_x + 30, centro_y + 80),
            (centro_x + 15, centro_y + 50), (centro_x - 15, centro_y + 50)
        ])
        pygame.draw.line(self.tela, (200, 180, 50), (esq_x, esq_y), (dir_x, dir_y), 8)
        pygame.draw.circle(self.tela, (255, 215, 0), (centro_x, centro_y), 10)

        comp_corda = 40
        for px, py in [(esq_x, esq_y), (dir_x, dir_y)]:
            pygame.draw.line(self.tela, (200, 200, 200), (px, py), (px, py + comp_corda), 2)
            pygame.draw.polygon(self.tela, (180, 180, 180), [
                (px - 40, py + comp_corda), (px + 40, py + comp_corda),
                (px + 25, py + comp_corda + 15), (px - 25, py + comp_corda + 15)
            ])

        txt_balanca = self.debug.render(f"{self.peso_balanca}", True, (255, 255, 255))
        self.tela.blit(txt_balanca, (centro_x - txt_balanca.get_width() // 2, centro_y - 30))

        # Campainha
        if self.img_campainha is not None:
            self.tela.blit(self.img_campainha, self.campainha_rect)
        else:
            pygame.draw.rect(self.tela, (200, 50, 50), self.campainha_rect)

        # Pilhas de compra
        piscar = self.estado_atual == "fase_compra" and (pygame.time.get_ticks() % 1000 < 500)
        cor_pernas_base = (200, 50, 50) if piscar else (255, 105, 97)
        cor_deck_base = (120, 150, 160) if piscar else (174, 198, 207)

        def desenhar_pilha(pos_rect, qtd_itens, lista_bagunca, cor_base, bloqueado, img_verso=None):
            for i in range(qtd_itens):
                off_x, off_y, angulo = lista_bagunca[i % len(lista_bagunca)]
                if img_verso is not None:
                    surf_carta = img_verso.copy()
                    if bloqueado:
                        surf_escura = pygame.Surface(surf_carta.get_size(), pygame.SRCALPHA)
                        surf_escura.fill((0, 0, 0, 128))
                        surf_carta.blit(surf_escura, (0, 0))
                else:
                    surf_carta = pygame.Surface((144, 176), pygame.SRCALPHA)
                    surf_carta.fill((100, 100, 100) if bloqueado else cor_base)
                carta_rot = pygame.transform.rotate(surf_carta, angulo)
                rect_final = carta_rot.get_rect(center=pos_rect.center)
                rect_final.x += off_x
                rect_final.y += off_y - i * 2
                self.tela.blit(carta_rot, rect_final)

        if self.pernas_disponiveis > 0:
            desenhar_pilha(self.comprar_pernas_rect, self.pernas_disponiveis,
                           self.bagunca_pernas, cor_pernas_base,
                           self.ja_comprou_neste_turno, img_verso=self.img_verso_pernas)
        else:
            pygame.draw.rect(self.tela, (50, 50, 50), self.comprar_pernas_rect)

        if len(self.deck_jogador) > 0:
            desenhar_pilha(self.comprar_deck_rect, len(self.deck_jogador),
                           self.bagunca_deck, cor_deck_base,
                           self.ja_comprou_neste_turno, img_verso=self.img_verso_deck)
        else:
            pygame.draw.rect(self.tela, (50, 50, 50), self.comprar_deck_rect)

        # Botões de descrição
        pygame.draw.rect(self.tela, (75, 0, 130), self.descricao_left_rect)
        pygame.draw.rect(self.tela, (200, 162, 200), self.descricao_right_rect)

        # Vida do jogador
        for i, rect_vida in enumerate(self.hitboxes_vida):
            if i == 0 and self.img_copo1 is not None:
                self.tela.blit(self.img_copo1, rect_vida)
            elif i == 1 and self.img_copo2 is not None:
                self.tela.blit(self.img_copo2, rect_vida)
            else:
                pygame.draw.rect(self.tela, (255, 182, 193), rect_vida)
                pygame.draw.rect(self.tela, (255, 255, 255), rect_vida, 3)

        # Itens do jogador
        for rect_item, nome_item in self.hitboxes_itens:
            img_item = self.imagens_itens.get(nome_item)
            if img_item:
                self.tela.blit(img_item, (rect_item.x + 10, rect_item.y + 10))
            else:
                # fallback: nome do item em texto se imagem faltar
                txt = self.fonte_mini.render(nome_item, True, (255, 255, 255))
                self.tela.blit(txt, (rect_item.x + 5, rect_item.y + 50))
            pygame.draw.rect(self.tela, (255, 255, 255), rect_item, 2) 

            if img_item:
                img_item = pygame.transform.scale(img_item, (rect_item.width - 20, rect_item.height - 20))
                self.tela.blit(img_item, (rect_item.x + 10, rect_item.y + 10))

        # Mini cartas (fila de espera inimiga)
        for rect_mini, i in self.hitboxes_slots_espera:
            pygame.draw.rect(self.tela, (60, 45, 45), rect_mini, 1)
            fila = self.filas_espera_inimigas[i]
            if fila:
                proxima_carta = fila[0]
                if proxima_carta.imagem is not None:
                    topo_carta = proxima_carta.imagem.subsurface((0, 75, 144, 101))
                    self.tela.blit(topo_carta, rect_mini)
                    pygame.draw.rect(self.tela, (100, 80, 80), rect_mini, 2)
                else:
                    pygame.draw.rect(self.tela, (45, 45, 50), rect_mini.inflate(-4, -4))
                    pygame.draw.rect(self.tela, (100, 80, 80), rect_mini.inflate(-4, -4), 2)
                    txt_nome = self.fonte_mini.render(proxima_carta.nome, True, (200, 200, 200))
                    self.tela.blit(txt_nome, (rect_mini.x + 8, rect_mini.y + 8))
                    txt_status = self.fonte_mini.render(
                        f"ATK:{proxima_carta.dano}  HP:{proxima_carta.vida}", True, (160, 140, 140)
                    )
                    self.tela.blit(txt_status, (rect_mini.x + 8, rect_mini.y + 45))

        # Cartas inimigas
        for rect_slot, i in self.hitboxes_slots_inimigos:
            rect_desenho = rect_slot.copy()

            if self.aguardando_alvo_peixeira and self.slots_inimigos[i] is not None:
                tremor = math.sin(pygame.time.get_ticks() * 0.02) * 5
                rect_desenho.x += int(tremor)

            if (self.turno_atual == "resolvendo_combate"
                    and self.fase_resolucao == "inimigos"
                    and self.idx_atacante_atual == i):
                fator_onda = math.sin(self.progresso_ataque * math.pi)
                dist_max = 240 if self.slots_aliados[i] is None else 170
                rect_desenho.y += int(dist_max * fator_onda)

            if self.slots_inimigos[i]:
                carta_inimiga = self.slots_inimigos[i]
                if carta_inimiga.imagem is not None:
                    self.tela.blit(carta_inimiga.imagem, (rect_desenho.x, rect_desenho.y))
                else:
                    cor_corpo = (255, 30, 30) if self.flash_inimigo[i] > 0 else (200, 100, 100)
                    pygame.draw.rect(self.tela, cor_corpo, rect_desenho.inflate(-10, -10))
                    txt = self.fonte_cartas.render(carta_inimiga.nome, True, (255, 255, 255))
                    self.tela.blit(txt, (rect_desenho.x + 10, rect_desenho.y + 20))
                txt_vida = self.fonte_vida.render(f"{carta_inimiga.vida}", True, (54, 32, 10))
                self.tela.blit(txt_vida, (rect_desenho.x + 112, rect_desenho.y + 144))

        # Cartas aliadas no tabuleiro
        for rect_slot, i in self.hitboxes_slots_aliados:
            rect_desenho = rect_slot.copy()
            prometida_ao_abate = i in self.slots_sacrificados_pendentes

            if (self.turno_atual == "resolvendo_combate"
                    and self.fase_resolucao == "aliados"
                    and self.idx_atacante_atual == i):
                fator_onda = math.sin(self.progresso_ataque * math.pi)
                dist_max = 240 if self.slots_inimigos[i] is None else 170
                rect_desenho.y -= int(dist_max * fator_onda)

            # Borda de posicionamento disponível
            if self.estado_atual == "posicionamento" and (
                    self.slots_aliados[i] is None or prometida_ao_abate):
                pygame.draw.rect(self.tela, (0, 255, 0), rect_desenho, 8)

            # Borda de sacrifício selecionado
            if prometida_ao_abate:
                pygame.draw.rect(self.tela, (0, 0, 0), rect_desenho, 8)

            if self.slots_aliados[i]:
                carta_aliada = self.slots_aliados[i]
                alpha_imagem = max(0, 255 - int(self.fade_sacrificio[i])) if prometida_ao_abate else 255

                if alpha_imagem > 0:
                    if carta_aliada.imagem is not None:
                        img_render = carta_aliada.imagem.copy()
                        if prometida_ao_abate:
                            escurecimento = min(200, int(self.fade_sacrificio[i] * 1.5))
                            surf_preta = pygame.Surface((144, 176), pygame.SRCALPHA)
                            surf_preta.fill((0, 0, 0, escurecimento))
                            img_render.blit(surf_preta, (0, 0))
                            img_render.set_alpha(alpha_imagem)
                        self.tela.blit(img_render, rect_desenho)
                    else:
                        cor_fundo = (100, 200, 100)
                        if self.flash_aliado[i] > 0:
                            cor_fundo = (255, 30, 30)
                        surf_fallback = pygame.Surface((144, 176), pygame.SRCALPHA)
                        surf_fallback.fill((*cor_fundo, alpha_imagem))
                        if prometida_ao_abate:
                            pygame.draw.rect(
                                surf_fallback, (0, 0, 0, min(200, int(self.fade_sacrificio[i] * 1.5))),
                                (0, 0, 144, 176)
                            )
                        self.tela.blit(surf_fallback, rect_desenho)
                        txt = self.fonte_cartas.render(carta_aliada.nome, True, (0, 0, 0))
                        txt.set_alpha(alpha_imagem)
                        self.tela.blit(txt, (rect_desenho.x + 10, rect_desenho.y + 20))

                    txt_vida = self.fonte_vida.render(f"{carta_aliada.vida}", True, (54, 32, 10))
                    if prometida_ao_abate:
                        txt_vida.set_alpha(alpha_imagem)
                    self.tela.blit(txt_vida, (rect_desenho.x + 112, rect_desenho.y + 140))

        # Mão do jogador (cartas não em foco)
        for rect_carta, carta, i in self.hitboxes_mao:
            if i == self.index_foco:
                continue
            if carta.imagem is not None:
                self.tela.blit(carta.imagem, rect_carta)
            else:
                pygame.draw.rect(self.tela, (255, 255, 255), rect_carta)
                self.tela.blit(
                    self.fonte_cartas.render(carta.nome, True, (0, 0, 0)),
                    (rect_carta.x + 5, rect_carta.y + 10)
                )
                self.tela.blit(
                    self.fonte_cartas.render(f"Custo: {carta.custo_sangue}", True, (200, 0, 0)),
                    (rect_carta.x + 5, rect_carta.y + 40)
                )
            txt_vida_mao = self.fonte_vida.render(f"{carta.vida}", True, (54, 32, 10))
            self.tela.blit(txt_vida_mao, (rect_carta.x + 112, rect_carta.y + 144))

        # Carta em foco (desenhada por último para ficar sobre as outras)
        if self.index_foco is not None and self.index_foco < len(self.hitboxes_mao):
            rect_foco, carta_foco, _ = self.hitboxes_mao[self.index_foco]
            if carta_foco.imagem is not None:
                self.tela.blit(carta_foco.imagem, rect_foco)
            else:
                pygame.draw.rect(self.tela, (255, 255, 220), rect_foco)
                self.tela.blit(
                    self.fonte_cartas.render(carta_foco.nome, True, (0, 0, 0)),
                    (rect_foco.x + 5, rect_foco.y + 10)
                )
                self.tela.blit(
                    self.fonte_cartas.render(f"Custo: {carta_foco.custo_sangue}", True, (200, 0, 0)),
                    (rect_foco.x + 5, rect_foco.y + 40)
                )
            txt_vida_foco = self.fonte_vida.render(f"{carta_foco.vida}", True, (54, 32, 10))
            self.tela.blit(txt_vida_foco, (rect_foco.x + 112, rect_foco.y + 144))

        # Animações de carta voando
        for anim in self.animacoes:
            x_anim, y_anim = anim["pos_atual"]
            rect_render_anim = pygame.Rect(x_anim, y_anim, 144, 176)
            carta_anim = anim["carta"]
            if carta_anim.imagem is not None:
                self.tela.blit(carta_anim.imagem, rect_render_anim)
            else:
                pygame.draw.rect(self.tela, (240, 240, 240), rect_render_anim)
                pygame.draw.rect(self.tela, (0, 0, 0), rect_render_anim, 6)
                self.tela.blit(
                    self.fonte_cartas.render(carta_anim.nome, True, (0, 0, 0)),
                    (rect_render_anim.x + 5, rect_render_anim.y + 10)
                )

        # Mensagem de debug
        texto_surface = self.debug.render(self.mensagem_debug, True, (255, 255, 255))
        rect_texto = texto_surface.get_rect(center=(self.tela.get_width() // 2, 825))
        pygame.draw.rect(self.tela, (0, 0, 0), rect_texto.inflate(20, 10))
        self.tela.blit(texto_surface, rect_texto)