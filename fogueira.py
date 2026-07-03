import pygame
from cena_base import CenaBase

class CenaFogueira(CenaBase):
    def __init__(self, tela, deck_jogador_global, proxima_depois="mapa"):
        super().__init__(tela)
        self.tela = tela
        self.deck = deck_jogador_global
        self.proxima_depois = proxima_depois
        
        try:
            img = pygame.image.load("cenarios/tela cangaceiro.png").convert()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((30, 20, 20))
            
        self.fonte_dialogo = pygame.font.SysFont("Arial", 30)
        self.fonte_cartas = pygame.font.SysFont("Arial", 20)
        self.fonte_vida = pygame.font.SysFont("Arial", 25, bold=True)

        self.textos_final = [
            "Seu bicho se aconchega na fogueira...",
            "Um dos cangaceiros chega perto dele...",
            "Outro mostra os dentes.",
            "Acanhado, você tira o bicho de perto do fogo e lavra."
        ]
        
        self.indice_dialogo = 0
        
        #diferente do tutorial, aqui pula direto pra ação (pensei em modularizar isso, mas tamo correndo contra o tempo.)
        self.estado = "escolha_carta"
        self.dialogo_atual = "Escolha um bicho para jogar na fogueira e aquecer."
        
        largura, altura = self.tela.get_size()
        
        self.rect_fogueira = pygame.Rect(largura//2 - 72, altura//2 - 120, 144, 176)
        
        self.carta_escolhida = None
        self.indice_destaque = None
        self.hitboxes_mao = []
        self._organizar_deck()

    def _organizar_deck(self):
        self.hitboxes_mao.clear()
        largura, altura = self.tela.get_size()
        
        qtd_cartas = len(self.deck)
        if qtd_cartas == 0: return
        
        espacamento = min(150, (largura - 100) // max(1, qtd_cartas))
        inicio_x = (largura - (espacamento * qtd_cartas)) // 2
        y_deck = altura - 380
        
        for i, carta in enumerate(self.deck):
            rect = pygame.Rect(inicio_x + (i * espacamento), y_deck, 144, 176)
            self.hitboxes_mao.append((rect, carta, i))

    def processar_eventos(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        
        self.indice_destaque = None
        if self.estado == "escolha_carta":
            for rect_carta, carta, i in reversed(self.hitboxes_mao):
                if rect_carta.collidepoint(pos_mouse):
                    self.indice_destaque = i
                    break

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                
                if self.estado == "escolha_carta":
                    if self.indice_destaque is not None:
                        _, carta_selecionada, idx = self.hitboxes_mao[self.indice_destaque]
                        
                        self.carta_escolhida = self.deck.pop(idx)
                        self.carta_escolhida.vida += 1
                        
                        self._organizar_deck()
                        
                        self.estado = "dialogo_final"
                        self.indice_dialogo = 0
                        self.dialogo_atual = self.textos_final[self.indice_dialogo]

                elif self.estado == "dialogo_final":
                    self.indice_dialogo += 1
                    if self.indice_dialogo < len(self.textos_final):
                        self.dialogo_atual = self.textos_final[self.indice_dialogo]
                    else:
                        self.deck.append(self.carta_escolhida)
                        self.terminou = True
                        self.proxima_cena = self.proxima_depois

    def atualizar(self, dt):
        pass

    def desenhar(self):
        self.tela.blit(self.fundo, (0, 0))
        
        cor_borda = (255, 69, 0)
        
        if self.carta_escolhida:
            if self.carta_escolhida.imagem: 
                self.tela.blit(self.carta_escolhida.imagem, self.rect_fogueira)
            else:
                pygame.draw.rect(self.tela, (255, 255, 255), self.rect_fogueira)
                txt = self.fonte_cartas.render(self.carta_escolhida.nome, True, (0,0,0))
                self.tela.blit(txt, (self.rect_fogueira.x + 5, self.rect_fogueira.y + 10))
            
            txt_vida = self.fonte_vida.render(str(self.carta_escolhida.vida), True, (54, 32, 10))
            self.tela.blit(txt_vida, (self.rect_fogueira.x + self.rect_fogueira.width - 30, self.rect_fogueira.y + self.rect_fogueira.height - 30))
        else:
            pygame.draw.rect(self.tela, (60, 20, 10), self.rect_fogueira)
            txt_fog = self.fonte_cartas.render("Fogueira", True, (255, 150, 50))
            self.tela.blit(txt_fog, (self.rect_fogueira.centerx - txt_fog.get_width()//2, self.rect_fogueira.centery - 10))
            
        pygame.draw.rect(self.tela, cor_borda, self.rect_fogueira, 4)

        if self.estado == "escolha_carta":
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