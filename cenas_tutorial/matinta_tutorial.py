import pygame
from cena_base import CenaBase

DICIONARIO_SELOS = {
    "mergulhador": "mergulhador.png",
    "ataque_triplo": "ataque_triplo.png",
    "mortal": "mortal.png",
    "voar": "voar.png",
    "espinhos": "espinhos.png",
    "escudo": "escudo.png",
    "sangue": "sangue.png"
}

class CenaMatinta(CenaBase):
    def __init__(self, tela, imagens_cartas, deck_jogador_global, proxima_depois="mapa"):
        super().__init__(tela)
        self.tela = tela
        self.deck = deck_jogador_global
        self.proxima_depois = proxima_depois
        
        try:
            img = pygame.image.load("cenarios/fundo_draft.png").convert()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((30, 30, 40))
            
        self.fonte_dialogo = pygame.font.SysFont("Arial", 30)
        self.fonte_cartas = pygame.font.SysFont("Arial", 20)
        self.fonte_vida = pygame.font.SysFont("Arial", 25, bold=True)
        self.fonte_instrucao = pygame.font.SysFont("Arial", 22, italic=True)

        # dialogos
        self.textos_dialogo = [
            "Você vê uma casa com as portas abertas, e também ouve um barulho vindo de cima...",
            "E de lá desce uma bruxa repugnante...",
            "Ela é conhecida como Matinta Pereira.",
            "Matinta - Olá viajante...",
            "Matinta - Tô vendo que esses seus bichanos são meio frágeis...",
            "Matinta - Talvez umas asas cairiam bem neles...",
            "Matinta - Mas fica ao seu critério...",
            "Tu se sente obrigado a fazer um sacrifício marcante, um que não tem volta..."
        ]
        self.indice_dialogo = 0
        self.dialogo_atual = self.textos_dialogo[self.indice_dialogo]
        
        # estados de jogo
        # "dialogo", "escolha_sacrificio", "escolha_beneficio", "concluido", "dialogo_final"
        self.estado = "dialogo"
        
        largura, altura = self.tela.get_size()
        
        self.rect_beneficio = pygame.Rect(largura//2 - 72, 50, 144, 176)
        self.rect_sacrificio = pygame.Rect(largura//2 - 72, 250, 144, 176)
        
        self.carta_sacrificada = None
        self.carta_beneficiada = None
        
        self.indice_destaque = None
        self.hitboxes_mao = []
        self._organizar_deck()

        

    def _organizar_deck(self):
        self.hitboxes_mao.clear()
        largura, altura = self.tela.get_size()
        
        qtd_cartas = len(self.deck)
        if qtd_cartas == 0: return
        
        espacamento = min(150, (largura - 100) // qtd_cartas)
        inicio_x = (largura - (espacamento * qtd_cartas)) // 2
        y_deck = altura - 380
        
        for i, carta in enumerate(self.deck):
            rect = pygame.Rect(inicio_x + (i * espacamento), y_deck, 144, 176)
            self.hitboxes_mao.append((rect, carta, i))

    def processar_eventos(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        
        self.indice_destaque = None
        if self.estado in ["escolha_sacrificio", "escolha_beneficio"]:
            for rect_carta, carta, i in reversed(self.hitboxes_mao):
                if rect_carta.collidepoint(pos_mouse):
                    self.indice_destaque = i
                    break

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                
                if self.estado == "dialogo":
                    self.indice_dialogo += 1
                    if self.indice_dialogo < len(self.textos_dialogo):
                        self.dialogo_atual = self.textos_dialogo[self.indice_dialogo]
                    else:
                        self.estado = "escolha_sacrificio"
                        self.dialogo_atual = "Escolha a carta para SACRIFICAR (ela será destruída)."
                
                elif self.estado == "escolha_sacrificio":
                    if self.indice_destaque is not None:
                        _, carta_selecionada, idx = self.hitboxes_mao[self.indice_destaque]
                        
                        #verifica se tem selo
                        if not carta_selecionada.selos:
                            self.dialogo_atual = "Essa carta não tem selos para transferir! Escolha outra."
                            continue

                        self.carta_sacrificada = self.deck.pop(idx)
                        self._organizar_deck()
                        
                        self.estado = "escolha_beneficio"
                        self.dialogo_atual = "Agora escolha a carta que RECEBERÁ o selo."
                
                elif self.estado == "escolha_beneficio":
                    if self.indice_destaque is not None:
                        _, carta_selecionada, idx = self.hitboxes_mao[self.indice_destaque]
                        
                        self.carta_beneficiada = self.deck.pop(idx)
                        self._organizar_deck()
                        for selo in self.carta_sacrificada.selos:
                            nome_img = DICIONARIO_SELOS.get(selo)
                            
                            if nome_img:
                                self.carta_beneficiada.adicionar_novo_selo(selo, nome_img)
                        
                        self.deck.append(self.carta_beneficiada)
                        
                        self.estado = "dialogo_final"
                        self.dialogo_atual = "Matinta - Hehehe... um bom trato. A nova fera está pronta."


                elif self.estado == "dialogo_final":
                    self.terminou = True
                    self.proxima_cena = self.proxima_depois

    def atualizar(self, dt):
        pass

    def desenhar(self):
        self.tela.blit(self.fundo, (0, 0))
        
        if self.indice_dialogo >= 3 or self.estado != "dialogo":
            
            cor_borda_ben = (0, 255, 0) if self.carta_beneficiada else (255, 140, 0)
            if self.carta_beneficiada:
                if self.carta_beneficiada.imagem: self.tela.blit(self.carta_beneficiada.imagem, self.rect_beneficio)
            else:
                pygame.draw.rect(self.tela, (50, 30, 20), self.rect_beneficio)
                txt_ben = self.fonte_cartas.render("Benefício", True, (255, 255, 255))
                self.tela.blit(txt_ben, (self.rect_beneficio.centerx - txt_ben.get_width()//2, self.rect_beneficio.centery - 10))
            pygame.draw.rect(self.tela, cor_borda_ben, self.rect_beneficio, 4)

            cor_borda_sac = (255, 0, 0) if self.carta_sacrificada else (255, 140, 0)
            if self.carta_sacrificada:
                if self.carta_sacrificada.imagem: self.tela.blit(self.carta_sacrificada.imagem, self.rect_sacrificio)
            else:
                pygame.draw.rect(self.tela, (50, 30, 20), self.rect_sacrificio)
                txt_sac = self.fonte_cartas.render("Sacrifício", True, (255, 255, 255))
                self.tela.blit(txt_sac, (self.rect_sacrificio.centerx - txt_sac.get_width()//2, self.rect_sacrificio.centery - 10))
            pygame.draw.rect(self.tela, cor_borda_sac, self.rect_sacrificio, 4)

        if self.estado in ["escolha_sacrificio", "escolha_beneficio"]:
            for rect_carta, carta, i in self.hitboxes_mao:
                if i == self.indice_destaque: continue
                if carta.imagem: 
                    self.tela.blit(carta.imagem, rect_carta)
                else:
                    pygame.draw.rect(self.tela, (255, 255, 255), rect_carta)
                    txt = self.fonte_cartas.render(carta.nome, True, (0,0,0))
                    self.tela.blit(txt, (rect_carta.x + 5, rect_carta.y + 10))

            if self.indice_destaque is not None and self.indice_destaque < len(self.hitboxes_mao):
                rect_original, carta, i = self.hitboxes_mao[self.indice_destaque]
                
                rect_hover = rect_original.copy()
                rect_hover.y -= 20 
                
                if carta.imagem: 
                    self.tela.blit(carta.imagem, rect_hover)
                else:
                    pygame.draw.rect(self.tela, (255, 255, 255), rect_hover)
                    txt = self.fonte_cartas.render(carta.nome, True, (0,0,0))
                    self.tela.blit(txt, (rect_hover.x + 5, rect_hover.y + 10))
                
                txt_vida = self.fonte_vida.render(str(carta.vida), True, (54, 32, 10))
                self.tela.blit(txt_vida, (rect_hover.x + rect_hover.width - 30, rect_hover.y + rect_hover.height - 30))

        if self.dialogo_atual:
            largura_tela, altura_tela = self.tela.get_size()
            rect_caixa = pygame.Rect(100, altura_tela - 180, largura_tela - 200, 150)
            pygame.draw.rect(self.tela, (10, 10, 10), rect_caixa)
            pygame.draw.rect(self.tela, (200, 200, 200), rect_caixa, 4)
            
            img_texto = self.fonte_dialogo.render(self.dialogo_atual, True, (255, 255, 255))
            self.tela.blit(img_texto, (rect_caixa.x + 30, rect_caixa.y + 50))
            
            triangulo = [
                (rect_caixa.right - 40, rect_caixa.bottom - 40), 
                (rect_caixa.right - 20, rect_caixa.bottom - 40), 
                (rect_caixa.right - 30, rect_caixa.bottom - 20)
            ]
            pygame.draw.polygon(self.tela, (255, 255, 255), triangulo)

    def transferir_selos(carta_sacrificada, carta_alvo):
        for nome_selo in carta_sacrificada.selos:

            # Verifica se o selo existe no nosso dicionário de imagens
            if nome_selo in DICIONARIO_SELOS:
                nome_arquivo_imagem = DICIONARIO_SELOS[nome_selo]

                # Chama a função que criamos no cartas.py para carimbar a carta alvo!
                carta_alvo.adicionar_novo_selo(nome_selo, nome_arquivo_imagem)