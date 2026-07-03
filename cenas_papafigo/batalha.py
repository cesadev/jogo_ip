import pygame
import math
import random
from cena_base import CenaBase
from cartas import Carta

class CenaCombate(CenaBase):
    def __init__(self, tela, deck_jogador, dados_da_fase, vida_player, imagens_versos, imagens_cartas):
        super().__init__(tela) 
        self.imagens_cartas = imagens_cartas
        tamanho_copo = (80, 96) 

        try:
            self.img_copo1 = pygame.transform.scale(pygame.image.load("assets/copo1.png").convert_alpha(), tamanho_copo)
            self.img_copo2 = pygame.transform.scale(pygame.image.load("assets/copo2.png").convert_alpha(), tamanho_copo)
        except FileNotFoundError:
            self.img_copo1 = None
            self.img_copo2 = None

        self.img_verso_deck = imagens_versos.get("verso_deck")
        self.img_verso_pernas = imagens_versos.get("verso_pernas")
        self.img_campainha = self._carregar_img("campainha", scale=(120, 120))


        self.deck_jogador = [
            Carta(c["nome"], c.get("dano", c.get("poder", 0)), c["vida"], c.get("imagem"), c.get("custo_sangue", 0), c.get("valor_sacrificio", 1))
            if isinstance(c, dict) else c
            for c in deck_jogador
        ]
        self.mao_jogador = [] 
        self.mao_jogador.append(Carta("Perna Cabeluda", 0, 1, imagens_cartas.get("perna"), 0, 1))
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
        

        self.id_combate = dados_da_fase.get("nome", "Combate Desconhecido")
        self.script_inimigo = dados_da_fase.get("script_inimigo", {})
        
        self.turno_atual = "jogador"
        self.turno_global = 1 
        self.ja_comprou_neste_turno = False 
        self.estado_atual = "fase_compra" 
        
        self.carta_selecionada = None
        self.index_carta_selecionada = None
        self.sangue_necessario = 0
        
        self.slots_sacrificados_pendentes = [] 
        self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]
        
        self.fase_resolucao = None       
        self.idx_atacante_atual = 0     
        self.progresso_ataque = 0.0     
        self.dano_aplicado = False      
        self.velocidade_ataque = 0.004
        
        self.flash_aliado = [0, 0, 0, 0]
        self.flash_inimigo = [0, 0, 0, 0]
        self.animacoes = []
        
        self.slots_aliados = [None, None, None, None]
        self.slots_inimigos = [None, None, None, None]
        self.filas_espera_inimigas = [[], [], [], []]
        self._tocar_musica_da_cena("Musicas/Papafigo.mp3")
        
        for obstaculo in dados_da_fase.get("obstaculos_iniciais", []):
            nome_obs = obstaculo["nome"]
            imagem_obs = obstaculo.get("imagem") or imagens_cartas.get(nome_obs)
                    
            carta_obs = Carta(nome_obs, obstaculo.get("dano", 0), obstaculo["vida"], imagem_obs, obstaculo.get("custo_sangue", 0), obstaculo.get("valor_sacrificio", 0))
            self.slots_inimigos[obstaculo["slot"]] = carta_obs            
        self._carregar_intencoes_inimigas_do_turno(1)
        
        self.pernas_disponiveis = 10 
        self.vida_player = vida_player
        self.peso_balanca = 0 
        
        def gerar_bagunca(quantidade):
            return [(random.randint(-2, 2), random.randint(-2, 2), random.uniform(-5, 5)) for _ in range(quantidade)]
            
        self.bagunca_pernas = gerar_bagunca(15)
        self.bagunca_deck = gerar_bagunca(40)
        
        largura_tela, altura_tela = tela.get_size()
        try:
            imagem_original = pygame.image.load("assets/combate.png").convert()
            self.imagem_fundo = pygame.transform.scale(imagem_original, (largura_tela, altura_tela))
        except FileNotFoundError:
            self.imagem_fundo = pygame.Surface((largura_tela, altura_tela))
            self.imagem_fundo.fill((30, 30, 30))
        
        self.campainha_rect = pygame.Rect(172, 50, 120, 120)
        self.comprar_pernas_rect = pygame.Rect(1190, 465, 144, 176)
        self.comprar_deck_rect = pygame.Rect(1350, 465, 144, 176)
        
        self.descricao_left_rect = pygame.Rect(1150, 130, 40, 40) 
        self.descricao_right_rect = pygame.Rect(1450, 130, 40, 40)

        self.hitboxes_mao = [] 
        self.hitboxes_slots_aliados = [] 
        self.hitboxes_slots_inimigos = []
        self.hitboxes_slots_espera = [] 
        self.hitboxes_vida = [] 
        self.hitboxes_itens = []
        self.itens_jogador = [{"nome": "Abridor de Lata"}, {"nome": "Peixeira"}]

        self.mensagem_debug = dados_da_fase.get("mensagem_inicio", "Início do Turno: Jogue suas cartas!")
        self.debug = pygame.font.SysFont("Arial", 36)
        self.fonte_cartas = pygame.font.SysFont("Arial", 20) 
        self.fonte_vida = pygame.font.SysFont("Arial", 30, bold=True)
        self.fonte_mini = pygame.font.SysFont("Arial", 14) 
        self.index_foco = None 
        

    def _carregar_img(self, nome, scale=(144, 176), convert=False):
        try:
            img = pygame.image.load(f"assets/{nome}.png")
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
        """Varre o script do turno e adiciona spawns de objetos Carta na fila correspondente"""
        acoes = self.script_inimigo.get(turno, [])
        for comando in acoes:
            if comando["acao"] == "jogar_carta":
                slot = comando["slot"]
                c = comando["carta"]
                if isinstance(c, dict):
                    nome_inimigo = c["nome"]
                    imagem_inimigo = c.get("imagem")
                    
                    # carregamento automatico das imagens dos inimigos
                    if imagem_inimigo is None:
                        try:
                            img_original = pygame.image.load(f"assets/{nome_inimigo}.png").convert_alpha()
                            imagem_inimigo = pygame.transform.scale(img_original, (144, 176))
                        except FileNotFoundError:
                            imagem_inimigo = None
                            
                    carta_obj = Carta(nome_inimigo, c.get("dano", c.get("poder", 0)), c["vida"], imagem_inimigo, c.get("custo_sangue", 0), c.get("valor_sacrificio", 1))
                else:
                    carta_obj = c.copy()
                self.filas_espera_inimigas[slot].append(carta_obj)

    def processar_eventos(self, eventos):
        for event in eventos:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos_mouse = pygame.mouse.get_pos()

            # CANCELAR AÇÃO
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

            if self.turno_atual != "jogador":
                continue

            # ==========================
            # COMPRA DE CARTAS
            # ==========================

            if self.comprar_pernas_rect.collidepoint(pos_mouse):

                if self.ja_comprou_neste_turno:
                    self.mensagem_debug = "Só pode comprar uma carta por turno."
                    continue

                if self.pernas_disponiveis > 0:
                    self.mao_jogador.append(
                        Carta(
                            "Perna Cabeluda",
                            0,
                            1,
                            self.img_perna,
                            0,
                            1
                        )
                    )

                    self.pernas_disponiveis -= 1
                    self.ja_comprou_neste_turno = True
                    self.estado_atual = "normal"
                    self.mensagem_debug = "Comprou uma Perna."

                continue

            elif self.comprar_deck_rect.collidepoint(pos_mouse):

                if self.ja_comprou_neste_turno:
                    self.mensagem_debug = "Só pode comprar uma carta por turno."
                    continue

                if len(self.deck_jogador) > 0:
                    carta = self.deck_jogador.pop(0)

                    self.mao_jogador.append(carta)

                    self.ja_comprou_neste_turno = True
                    self.estado_atual = "normal"
                    self.mensagem_debug = f"Comprou {carta.nome}"

                continue

            # ==========================
            # CAMPAINHA
            # ==========================

            if self.campainha_rect.collidepoint(pos_mouse):

                if self.estado_atual == "fase_compra":
                    self.mensagem_debug = "Compre uma carta antes."
                    continue

                if not self.ja_comprou_neste_turno and self.turno_global > 1:
                    self.mensagem_debug = "Você precisa comprar uma carta primeiro."
                    continue

                self.turno_atual = "resolvendo_combate"

                self.fase_resolucao = "aliados"

                self.idx_atacante_atual = 0
                self.progresso_ataque = 0.0
                self.dano_aplicado = False

                self.mensagem_debug = "Combate iniciado."

                continue

            # ==========================
            # BLOQUEIO DA FASE DE COMPRA
            # ==========================

            if self.estado_atual == "fase_compra":
                self.mensagem_debug = "Compre uma carta primeiro."
                continue

            # ==========================
            # ESTADO NORMAL
            # ==========================

            if self.estado_atual == "normal":

                if not self.ja_comprou_neste_turno and self.turno_global > 1:
                    self.mensagem_debug = "Você precisa comprar uma carta primeiro."
                    continue

                if self.index_foco is None:
                    continue

                if self.index_foco >= len(self.mao_jogador):
                    continue

                carta_tentativa = self.mao_jogador[self.index_foco]

                custo = carta_tentativa.custo_sangue

                sangue_disponivel = sum(
                    carta.valor_sacrificio
                    for carta in self.slots_aliados
                    if carta is not None
                )

                if custo > sangue_disponivel:
                    self.mensagem_debug = (
                        f"Necessário {custo} sangue."
                    )
                    continue

                if custo > 0:

                    self.index_carta_selecionada = self.index_foco
                    self.carta_selecionada = carta_tentativa

                    self.estado_atual = "sacrificio"

                    self.sangue_necessario = custo

                    self.slots_sacrificados_pendentes.clear()

                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

                    self.mensagem_debug = (
                        f"Selecione sacrifícios ({custo})"
                    )

                else:

                    self.index_carta_selecionada = self.index_foco
                    self.carta_selecionada = carta_tentativa

                    self.estado_atual = "posicionamento"

                    self.mensagem_debug = (
                        "Escolha um slot."
                    )

            # ==========================
            # SACRIFÍCIO
            # ==========================

            elif self.estado_atual == "sacrificio":

                clicou_valido = False

                for rect_slot, i in self.hitboxes_slots_aliados:

                    if rect_slot.collidepoint(pos_mouse):

                        clicou_valido = True

                        if (
                            self.slots_aliados[i] is not None
                            and i not in self.slots_sacrificados_pendentes
                        ):

                            self.slots_sacrificados_pendentes.append(i)

                            sangue_acumulado = sum(
                                self.slots_aliados[idx].valor_sacrificio
                                for idx in self.slots_sacrificados_pendentes
                            )

                            if sangue_acumulado >= self.sangue_necessario:

                                self.estado_atual = "posicionamento"

                                self.mensagem_debug = (
                                    "Sacrifício concluído."
                                )

                        break

                if not clicou_valido:

                    self.estado_atual = "normal"

                    self.carta_selecionada = None
                    self.index_carta_selecionada = None

                    self.slots_sacrificados_pendentes.clear()

                    self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

            # ==========================
            # POSICIONAMENTO
            # ==========================

            elif self.estado_atual == "posicionamento":

                clicou_valido = False

                for rect_slot, i in self.hitboxes_slots_aliados:

                    if rect_slot.collidepoint(pos_mouse):

                        clicou_valido = True

                        slot_valido = (
                            self.slots_aliados[i] is None
                            or i in self.slots_sacrificados_pendentes
                        )

                        if (
                            slot_valido
                            and not any(
                                anim["slot_destino"] == i
                                for anim in self.animacoes
                            )
                        ):

                            rect_mao, _, _ = (
                                self.hitboxes_mao[
                                    self.index_carta_selecionada
                                ]
                            )

                            for idx in self.slots_sacrificados_pendentes:
                                self.slots_aliados[idx] = None
                                self.fade_sacrificio[idx] = 0.0

                            self.slots_sacrificados_pendentes.clear()

                            self.animacoes.append({
                                "carta": self.carta_selecionada.copy(),
                                "pos_inicial": (
                                    rect_mao.x,
                                    rect_mao.y
                                ),
                                "pos_final": (
                                    rect_slot.x,
                                    rect_slot.y
                                ),
                                "pos_atual": [
                                    rect_mao.x,
                                    rect_mao.y
                                ],
                                "progresso": 0.0,
                                "slot_destino": i
                            })

                            self.mao_jogador.pop(
                                self.index_carta_selecionada
                            )

                            self.estado_atual = "normal"

                            self.carta_selecionada = None
                            self.index_carta_selecionada = None

                            self.mensagem_debug = (
                                "Carta posicionada."
                            )

                        break

            if not clicou_valido:

                self.estado_atual = "normal"

                self.carta_selecionada = None
                self.index_carta_selecionada = None

                self.slots_sacrificados_pendentes.clear()

                self.fade_sacrificio = [0.0, 0.0, 0.0, 0.0]

    def atualizar(self, dt):

        for idx in range(4):
            if self.flash_aliado[idx] > 0: self.flash_aliado[idx] -= dt
            if self.flash_inimigo[idx] > 0: self.flash_inimigo[idx] -= dt
            if idx in self.slots_sacrificados_pendentes:
                self.fade_sacrificio[idx] = min(255.0, self.fade_sacrificio[idx] + dt * 0.25)
            else:
                self.fade_sacrificio[idx] = 0.0

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

        if self.turno_atual == "resolvendo_combate":
            if self.fase_resolucao == "aliados":
                while self.idx_atacante_atual < 4:
                    card = self.slots_aliados[self.idx_atacante_atual]
                    if card is not None and card.dano > 0:
                        break
                    self.idx_atacante_atual += 1
                    self.progresso_ataque = 0.0
                    self.dano_aplicado = False

                if self.idx_atacante_atual >= 4:
                    self.mensagem_debug = "Turno Aliado encerrado. Inimigo preparando jogadas..."
                    self.fase_resolucao = "pre_inimigo"
                    
                    for i in range(4):
                        if self.slots_inimigos[i] is None and len(self.filas_espera_inimigas[i]) > 0:
                            self.slots_inimigos[i] = self.filas_espera_inimigas[i].pop(0)
                    return

                card_atacante = self.slots_aliados[self.idx_atacante_atual]
                self.progresso_ataque += dt * self.velocidade_ataque
                
                if self.progresso_ataque >= 0.5 and not self.dano_aplicado:
                    tem_alvo = self.slots_inimigos[self.idx_atacante_atual] is not None
                    if tem_alvo:
                        self.slots_inimigos[self.idx_atacante_atual].vida -= card_atacante.dano
                        self.flash_inimigo[self.idx_atacante_atual] = 200 
                        if self.slots_inimigos[self.idx_atacante_atual].vida <= 0:
                            self.slots_inimigos[self.idx_atacante_atual] = None
                    else:
                        self.peso_balanca += card_atacante.dano
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
                while self.idx_atacante_atual < 4:
                    card = self.slots_inimigos[self.idx_atacante_atual]
                    if card is not None and card.dano > 0:
                        break
                    self.idx_atacante_atual += 1
                    self.progresso_ataque = 0.0
                    self.dano_aplicado = False

                if self.idx_atacante_atual >= 4:
                    if self.peso_balanca <= -5:
                        self.vida_player -= 1
                        self.mensagem_debug = "Você perdeu."
                        if self.vida_player <= 0:
                            self.mensagem_debug = "Você sucumbiu..."
                            self.terminou = True
                            self.proxima_cena = "game_over"
                            return
                        else:
                            self.mensagem_debug = "Você perdeu a rodada, retornando ao mapa..."
                            self.terminou = True
                            self.proxima_cena = "mapa"
                            

                    self.turno_global += 1
                    self.turno_atual = "jogador"
                    self.ja_comprou_neste_turno = False 
                    self.estado_atual = "fase_compra"
                    self.fase_resolucao = None
                    
                    return

                card_atacante = self.slots_inimigos[self.idx_atacante_atual]
                self.progresso_ataque += dt * self.velocidade_ataque
                
                if self.progresso_ataque >= 0.5 and not self.dano_aplicado:
                    tem_alvo = self.slots_aliados[self.idx_atacante_atual] is not None
                    if tem_alvo:
                        self.slots_aliados[self.idx_atacante_atual].vida -= card_atacante.dano
                        self.flash_aliado[self.idx_atacante_atual] = 200
                        if self.slots_aliados[self.idx_atacante_atual].vida <= 0:
                            self.slots_aliados[self.idx_atacante_atual] = None
                    else:
                        self.peso_balanca -= card_atacante.dano
                    self.dano_aplicado = True

                if self.progresso_ataque >= 1.0:
                    self.idx_atacante_atual += 1
                    self.progresso_ataque = 0.0
                    self.dano_aplicado = False

        self.hitboxes_vida.clear()
        pos_x_vida, pos_y_vida, tamanho_vida, espacamento_vida = 145, 505, 80, 20
        for i in range(self.vida_player):
            rect = pygame.Rect(pos_x_vida + (i * (tamanho_vida + espacamento_vida)), pos_y_vida, tamanho_vida, tamanho_vida)
            self.hitboxes_vida.append(rect)

        self.hitboxes_slots_aliados.clear()
        self.hitboxes_slots_inimigos.clear()
        self.hitboxes_slots_espera.clear()
        
        # alinhamento das cartas
        pos_x_slot = 458
        y_espera = 32
        y_inimigos = 158
        y_aliados = 408
        
        espacamento_horizontal = 160
        largura_padrao, altura_padrao = 144, 176 
        altura_mini = 101
        
        for i in range(4):
            self.hitboxes_slots_espera.append((pygame.Rect(pos_x_slot, y_espera, largura_padrao, altura_mini), i))
            self.hitboxes_slots_inimigos.append((pygame.Rect(pos_x_slot, y_inimigos, largura_padrao, altura_padrao), i))
            self.hitboxes_slots_aliados.append((pygame.Rect(pos_x_slot, y_aliados, largura_padrao, altura_padrao), i))
            pos_x_slot += espacamento_horizontal
            
        self.hitboxes_itens.clear()
        pos_x_inicial_item = 1190
        for item in self.itens_jogador[:2]:
            self.hitboxes_itens.append((pygame.Rect(pos_x_inicial_item, 330, 120, 120), item))
            pos_x_inicial_item += 140

        self.hitboxes_mao.clear() 
        qtd_cartas = len(self.mao_jogador)
        if qtd_cartas > 0:
            largura_tela, margem_tela = self.tela.get_width(), 400 
            espacamento = 0 if qtd_cartas == 1 else max(30, min(80, (largura_tela - margem_tela - largura_padrao) // (qtd_cartas - 1)))
            largura_total_mao = (qtd_cartas - 1) * espacamento + largura_padrao
            pos_x_inicial_mao = (largura_tela - largura_total_mao) // 2 
            
            pos_mouse = pygame.mouse.get_pos()
            self.index_foco = None
            
            rects_virtuais = []
            for i in range(qtd_cartas):
                rect = pygame.Rect(pos_x_inicial_mao + (i * espacamento), 650, largura_padrao, altura_padrao)
                rects_virtuais.append(rect)
                
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

    def desenhar(self):
        self.tela.blit(self.imagem_fundo, (0, 0))

        centro_x, centro_y, raio = 240, 350, 128
        angulo_rad = math.radians(self.peso_balanca * 2.5)
        dx, dy = math.cos(angulo_rad) * raio, math.sin(angulo_rad) * raio
        esq_x, esq_y = centro_x - dx, centro_y + dy  
        dir_x, dir_y = centro_x + dx, centro_y - dy  

        pygame.draw.rect(self.tela, (90, 60, 30), (centro_x - 10, centro_y, 20, 80)) 
        pygame.draw.polygon(self.tela, (70, 40, 20), [(centro_x-30, centro_y+80), (centro_x+30, centro_y+80), (centro_x+15, centro_y+50), (centro_x-15, centro_y+50)]) 
        pygame.draw.line(self.tela, (200, 180, 50), (esq_x, esq_y), (dir_x, dir_y), 8) 
        pygame.draw.circle(self.tela, (255, 215, 0), (centro_x, centro_y), 10) 

        comp_corda = 40
        pygame.draw.line(self.tela, (200, 200, 200), (esq_x, esq_y), (esq_x, esq_y + comp_corda), 2)
        pygame.draw.polygon(self.tela, (180, 180, 180), [(esq_x-40, esq_y+comp_corda), (esq_x+40, esq_y+comp_corda), (esq_x+25, esq_y+comp_corda+15), (esq_x-25, esq_y+comp_corda+15)])
        pygame.draw.line(self.tela, (200, 200, 200), (dir_x, dir_y), (dir_x, dir_y + comp_corda), 2)
        pygame.draw.polygon(self.tela, (180, 180, 180), [(dir_x-40, dir_y+comp_corda), (dir_x+40, dir_y+comp_corda), (dir_x+25, dir_y+comp_corda+15), (dir_x-25, dir_y+comp_corda+15)])

        txt_balanca = self.debug.render(f"{self.peso_balanca}", True, (255, 255, 255))
        self.tela.blit(txt_balanca, (centro_x - txt_balanca.get_width()//2, centro_y - 30))

        if hasattr(self, 'img_campainha') and self.img_campainha is not None:
            self.tela.blit(self.img_campainha, self.campainha_rect)
        else:
            pygame.draw.rect(self.tela, (200, 50, 50), self.campainha_rect)
        
        piscar = self.estado_atual == "fase_compra" and (pygame.time.get_ticks() % 1000 < 500)
        cor_pernas_base = (200, 50, 50) if piscar else (255, 105, 97)
        cor_deck_base = (120, 150, 160) if piscar else (174, 198, 207)

        def desenhar_pilha(pos_rect, qtd_itens, lista_bagunca, cor_base, bloqueado, img_verso=None):
            for i in range(qtd_itens):
                off_x, off_y, angulo = lista_bagunca[i % len(lista_bagunca)]
                
                if img_verso is not None:
                    surf_carta = img_verso.copy()
                    if bloqueado:
                        # Aplica uma película escura se não puder comprar
                        surf_escura = pygame.Surface(surf_carta.get_size(), pygame.SRCALPHA)
                        surf_escura.fill((0, 0, 0, 128))
                        surf_carta.blit(surf_escura, (0, 0))
                else:
                    # Fallback clássico caso falte a imagem
                    surf_carta = pygame.Surface((144, 176), pygame.SRCALPHA)
                    cor = (100, 100, 100) if bloqueado else cor_base
                    surf_carta.fill(cor)
                
                carta_rot = pygame.transform.rotate(surf_carta, angulo)
                rect_final = carta_rot.get_rect(center=pos_rect.center)
                rect_final.x += off_x
                rect_final.y += (off_y - (i * 2)) 
                self.tela.blit(carta_rot, rect_final)
        
        if self.pernas_disponiveis > 0:
            desenhar_pilha(self.comprar_pernas_rect, self.pernas_disponiveis, self.bagunca_pernas, cor_pernas_base, self.ja_comprou_neste_turno, img_verso=self.img_verso_pernas)
        else:
            pygame.draw.rect(self.tela, (50, 50, 50), self.comprar_pernas_rect)

        if len(self.deck_jogador) > 0:
            desenhar_pilha(self.comprar_deck_rect, len(self.deck_jogador), self.bagunca_deck, cor_deck_base, self.ja_comprou_neste_turno, img_verso=self.img_verso_deck)
        else:
            pygame.draw.rect(self.tela, (50, 50, 50), self.comprar_deck_rect)

        pygame.draw.rect(self.tela, (75, 0, 130), self.descricao_left_rect)   
        pygame.draw.rect(self.tela, (200, 162, 200), self.descricao_right_rect) 

        for i, rect_vida in enumerate(self.hitboxes_vida):
            if i == 0 and self.img_copo1 is not None:
                self.tela.blit(self.img_copo1, rect_vida)
            elif i == 1 and self.img_copo2 is not None:
                self.tela.blit(self.img_copo2, rect_vida)
            else:
                pygame.draw.rect(self.tela, (255, 182, 193), rect_vida) 
                pygame.draw.rect(self.tela, (255, 255, 255), rect_vida, 3)

        for rect_item, item in self.hitboxes_itens:
            pygame.draw.rect(self.tela, (46, 111, 64), rect_item)
            pygame.draw.rect(self.tela, (255, 255, 255), rect_item, 2) 
            
        # mini cartas
        for rect_mini, i in self.hitboxes_slots_espera:
            pygame.draw.rect(self.tela, (60, 45, 45), rect_mini, 1)
            
            fila = self.filas_espera_inimigas[i]
            if len(fila) > 0:
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
                    
                    txt_status = self.fonte_mini.render(f"ATK:{proxima_carta.dano}  HP:{proxima_carta.vida}", True, (160, 140, 140))
                    self.tela.blit(txt_status, (rect_mini.x + 8, rect_mini.y + 45))

        # cartas inimigos
        for rect_slot, i in self.hitboxes_slots_inimigos:
            rect_desenho = rect_slot.copy()
            
            if self.turno_atual == "resolvendo_combate" and self.fase_resolucao == "inimigos" and self.idx_atacante_atual == i:
                fator_onda = math.sin(self.progresso_ataque * math.pi)
                alvo_vazio = self.slots_aliados[i] is None
                dist_max = 240 if alvo_vazio else 170
                rect_desenho.y += int(dist_max * fator_onda) 
            
            if self.slots_inimigos[i]:
                if self.slots_inimigos[i].imagem is not None:
                    self.tela.blit(self.slots_inimigos[i].imagem, (rect_desenho.x, rect_desenho.y))
                else:
                    cor_corpo = (255, 30, 30) if self.flash_inimigo[i] > 0 else (200, 100, 100)
                    pygame.draw.rect(self.tela, cor_corpo, rect_desenho.inflate(-10, -10))
                    txt = self.fonte_cartas.render(self.slots_inimigos[i].nome, True, (255,255,255))
                    self.tela.blit(txt, (rect_desenho.x + 10, rect_desenho.y + 20))

                txt_vida = self.fonte_vida.render(f"{self.slots_inimigos[i].vida}", True, (54, 32, 10))
                self.tela.blit(txt_vida, (rect_desenho.x + 112, rect_desenho.y + 144))
                
        # cartas do player no tabuleiro
        for rect_slot, i in self.hitboxes_slots_aliados:
            rect_desenho = rect_slot.copy()
            esta_em_panico = False
            prometida_ao_abate = i in self.slots_sacrificados_pendentes

            if self.turno_atual == "resolvendo_combate" and self.fase_resolucao == "aliados" and self.idx_atacante_atual == i:
                fator_onda = math.sin(self.progresso_ataque * math.pi)
                alvo_vazio = self.slots_inimigos[i] is None
                dist_max = 240 if alvo_vazio else 170
                rect_desenho.y -= int(dist_max * fator_onda) 

            if prometida_ao_abate:
                cor_borda = (0, 0, 0) 
                pygame.draw.rect(self.tela, cor_borda, rect_desenho, 8)
                
            elif self.estado_atual == "sacrificio" and self.slots_aliados[i] is not None:
                if esta_em_panico:
                    tempo_ticks = pygame.time.get_ticks()
                    rect_desenho.x += int(math.sin(tempo_ticks * 0.03 + i * 12) * 3)
                    rect_desenho.y += int(math.cos(tempo_ticks * 0.03 + i * 7) * 3)
                    pulso_alfa = int(140 + 115 * math.sin(tempo_ticks * 0.015))
                    pygame.draw.rect(self.tela, (pulso_alfa, 0, 0), rect_desenho, 8)
                    
                elif self.estado_atual == "posicionamento" and (self.slots_aliados[i] is None or prometida_ao_abate):
                    pygame.draw.rect(self.tela, (0, 255, 0), rect_desenho, 8)

                # Desenho da carta
                if self.slots_aliados[i]:
                    alpha_imagem = 255
                    if prometida_ao_abate:
                        alpha_imagem = max(0, 255 - int(self.fade_sacrificio[i]))
                        
                    if alpha_imagem > 0:
                        cor_texto = (255,255,255) if esta_em_panico else (0,0,0)
                        
                        if self.slots_aliados[i].imagem is not None:
                            img_render = self.slots_aliados[i].imagem.copy()
                            if prometida_ao_abate:
                                escurecimento = min(200, int(self.fade_sacrificio[i] * 1.5))
                                surf_preta = pygame.Surface((144, 176), pygame.SRCALPHA)
                                surf_preta.fill((0, 0, 0, escurecimento))
                                img_render.blit(surf_preta, (0, 0))
                                img_render.set_alpha(alpha_imagem)
                            self.tela.blit(img_render, rect_desenho)
                        else:
                            cor_fundo = (160, 80, 80) if esta_em_panico else (100, 200, 100)
                            if self.flash_aliado[i] > 0: cor_fundo = (255, 30, 30)
                            
                            surf_fallback = pygame.Surface((144, 176), pygame.SRCALPHA)
                            surf_fallback.fill((*cor_fundo, alpha_imagem))
                            
                            if prometida_ao_abate:
                                pygame.draw.rect(surf_fallback, (0, 0, 0, min(200, int(self.fade_sacrificio[i] * 1.5))), (0,0,144,176))
                            
                            self.tela.blit(surf_fallback, rect_desenho)
                            txt = self.fonte_cartas.render(self.slots_aliados[i].nome, True, cor_texto)
                            txt.set_alpha(alpha_imagem)
                            self.tela.blit(txt, (rect_desenho.x + 10, rect_desenho.y + 20))
                        
                        cor_vida = (200, 0, 0) if esta_em_panico else (54, 32, 10)
                        txt_vida = self.fonte_vida.render(f"{self.slots_aliados[i].vida}", True, cor_vida)
                        if prometida_ao_abate:
                            txt_vida.set_alpha(alpha_imagem)
                        self.tela.blit(txt_vida, (rect_desenho.x + 112, rect_desenho.y + 140))
    
        # mão do player
        for rect_carta, carta, i in self.hitboxes_mao:
            if i != self.index_foco:
                if carta.imagem is not None:
                    self.tela.blit(carta.imagem, rect_carta)
                else:
                    cor_fundo = (255, 255, 200) if (self.estado_atual != "normal" and self.estado_atual != "fase_compra" and i == self.index_carta_selecionada) else (255, 255, 255)
                    pygame.draw.rect(self.tela, cor_fundo, rect_carta) 
                    txt_nome = self.fonte_cartas.render(carta.nome, True, (0,0,0))
                    txt_custo = self.fonte_cartas.render(f"Custo: {carta.custo_sangue}", True, (200,0,0))
                    self.tela.blit(txt_nome, (rect_carta.x + 5, rect_carta.y + 10))
                    self.tela.blit(txt_custo, (rect_carta.x + 5, rect_carta.y + 40))

                txt_vida_mao = self.fonte_vida.render(f"{carta.vida}", True, (54, 32, 10))
                self.tela.blit(txt_vida_mao, (rect_carta.x + 112, rect_carta.y + 144))
                
        if self.index_foco is not None and self.index_foco < len(self.hitboxes_mao):
            rect_foco, carta_foco, _ = self.hitboxes_mao[self.index_foco]
            if carta_foco.imagem is not None:
                self.tela.blit(carta_foco.imagem, rect_foco)
            else:
                pygame.draw.rect(self.tela, (255, 255, 220), rect_foco) 
                txt_nome = self.fonte_cartas.render(carta_foco.nome, True, (0,0,0))
                txt_custo = self.fonte_cartas.render(f"Custo: {carta_foco.custo_sangue}", True, (200,0,0))
                self.tela.blit(txt_nome, (rect_foco.x + 5, rect_foco.y + 10))
                self.tela.blit(txt_custo, (rect_foco.x + 5, rect_foco.y + 40))
            
            txt_vida_foco = self.fonte_vida.render(f"{carta_foco.vida}", True, (54, 32, 10))
            self.tela.blit(txt_vida_foco, (rect_foco.x + 112, rect_foco.y + 144))
            
        # trajetoria de entrada
        for anim in self.animacoes:
            x_anim, y_anim = anim["pos_atual"]
            rect_render_anim = pygame.Rect(x_anim, y_anim, 144, 176)
            carta_anim = anim["carta"]
            if carta_anim.imagem is not None:
                self.tela.blit(carta_anim.imagem, rect_render_anim)
            else:
                pygame.draw.rect(self.tela, (240, 240, 240), rect_render_anim)
                pygame.draw.rect(self.tela, (0, 0, 0), rect_render_anim, 6)
                txt_nome = self.fonte_cartas.render(carta_anim.nome, True, (0,0,0))
                self.tela.blit(txt_nome, (rect_render_anim.x + 5, rect_render_anim.y + 10))

        texto_surface = self.debug.render(self.mensagem_debug, True, (255, 255, 255))
        rect_texto = texto_surface.get_rect(center=(self.tela.get_width() // 2, 825))
        pygame.draw.rect(self.tela, (0, 0, 0), rect_texto.inflate(20, 10)) 
        self.tela.blit(texto_surface, rect_texto)

if __name__ == "__main__":
    pygame.init()
    
    LARGURA, ALTURA = 1536, 864
    tela_teste = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Inscryption Engine - Sistema de Antecipação de Turnos")
    relogio = pygame.time.Clock()

    # leitura do fases
    try:
        from cenas_caboclo.fases_caboclo import fases_do_jogo
        mock_dados_fase = fases_do_jogo["boss_1"]
    except ModuleNotFoundError:
        mock_dados_fase = {
            "nome": "o lenhador brabo (Failsafe)",
            "obstaculos_iniciais": [{"slot": 2, "nome": "Cacto", "vida": 5, "dano": 0, "valor_sacrificio": 0}],
            "script_inimigo": {
                1: [{"acao": "jogar_carta", "carta": {"nome": "Capelobo", "vida": 3, "dano": 1}, "slot": 0}],
                2: [{"acao": "jogar_carta", "carta": {"nome": "timbu", "vida": 1, "dano": 1}, "slot": 3}],
                4: [{"acao": "ataque_especial", "nome": "Puxão master das trevas", "dano_direto": 1}]
            }
        }

    # cartas do baralho
    tamanho_carta = (144, 176)
    try:
        img_capelobo = pygame.transform.scale(pygame.image.load("assets/Capelobo.png").convert_alpha(), tamanho_carta)
    except FileNotFoundError:
        img_capelobo = None
        
    try:
        img_la_ursa = pygame.transform.scale(pygame.image.load("assets/LaUrsa.png").convert_alpha(), tamanho_carta)
    except FileNotFoundError:
        img_la_ursa = None

    try:
        img_comadre = pygame.transform.scale(pygame.image.load("assets/comadre.png").convert_alpha(), tamanho_carta)
    except:
        img_comadre = None

    mock_deck_jogador = [
        Carta(nome="Capelobo", poder=1, vida=3, imagem=img_capelobo, custo_sangue=1, valor_sacrificio=1),
        Carta(nome="La Ursa", poder=4, vida=6, imagem=img_la_ursa, custo_sangue=3, valor_sacrificio=1),
        Carta(nome="Comadre", poder=1, vida=1, imagem= img_comadre, custo_sangue=2, valor_sacrificio=1)
    ]
    
    cena_teste = CenaCombate(tela_teste, mock_deck_jogador, mock_dados_fase)
    
    rodando = True
    while rodando:
        dt = relogio.tick(60) 
        eventos = pygame.event.get() 
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False

        cena_teste.processar_eventos(eventos)
        cena_teste.atualizar(dt)
        cena_teste.desenhar()

        pygame.display.flip()

    pygame.quit()