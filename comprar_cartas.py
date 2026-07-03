import pygame
import random
from cena_base import CenaBase
from cartas import Carta

class CenaEscolhaCarta(CenaBase):
    def __init__(self, tela, imagens_versos, imagens_cartas, imagens_ui, proxima_depois="mapa"):
        super().__init__(tela)
        
        self.tela = tela
        self.proxima_depois = proxima_depois
        
        # imagem de fundo
        try:
            img = pygame.image.load("cenarios/fundo_draft.png").convert()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((30, 30, 40))
            
        # o verso da carta (jaja faço)
        self.img_verso = imagens_versos.get("carta_verso")
            
        self.fonte_titulo = pygame.font.SysFont("Arial", 50, bold=True)
        self.fonte_cartas = pygame.font.SysFont("Arial", 20)
        self.fonte_dialogo = pygame.font.SysFont("Arial", 30)
        self.fonte_vida = pygame.font.SysFont("Arial", 25, bold=True)


        todas_as_cartas = [
            Carta("Acauã", 2, 3, imagens_cartas.get("acaua"), 2, 1, selos=["voar"]),
            Carta("Anhangá", 3, 7, imagens_cartas.get("anhanga"), 4, 1),
            Carta("Boitatá", 2, 1, imagens_cartas.get("boitata"), 2, 1),
            Carta("Caboclo D'água", 1, 1, imagens_cartas.get("caboclo"), 1, 1, selos=["mergulhador"]),
            Carta("Capelobo", 1, 2, imagens_cartas.get("capelobo"), 1, 1),
            Carta("Chupa-Cabra", 1, 1, imagens_cartas.get("chupa-cabra"), 1, 3, selos=["sangue"]),
            Carta("Cobra Coral", 2, 2, imagens_cartas.get("cobra_coral"), 1, 1, selos=["mortal"]),
            Carta("Comadre Florzinha", 1, 1, imagens_cartas.get("comadre"), 2, 1, selos=["ataque_triplo"]),
            Carta("Cuca", 2, 2, imagens_cartas.get("cuca"), 2, 1, selos=["escudo"]),
            Carta("Curupira", 3, 2, imagens_cartas.get("curupira"), 2, 1),
            Carta("La Ursa", 3, 2, imagens_cartas.get("la_ursa"), 3, 1),
            Carta("Leão", 7, 7, imagens_cartas.get("leao"), 4, 1),
            Carta("Mula Sem-Cabeça", 3, 4, imagens_cartas.get("mula"), 3, 1),
            Carta("Timbu", 1, 1, imagens_cartas.get("timbu"), 1, 1, selos=["espinhos"])
        ]
        
        self.cartas_na_mesa = random.sample(todas_as_cartas, 3)
        self.cartas_reveladas = [False, False, False]
        
        self.estado = "dialogo_inicial"
        self.dialogo_atual = "Três bichos aparecem na tua frente"
        
        # animação de entrada
        self.progresso_animacao = 0.0
        self.y_inicial_cartas = -250  
        self.y_final_cartas = 350    
        self.y_atual_cartas = self.y_inicial_cartas
        
        largura_tela = self.tela.get_width()
        self.posicoes_x = [largura_tela//2 - 250, largura_tela//2, largura_tela//2 + 250]
        self.hitboxes = [pygame.Rect(x - 72, self.y_atual_cartas, 144, 176) for x in self.posicoes_x]
        
        self.index_foco = None 
        self.carta_escolhida = None

    def _carregar_img(self, nome):
        try:
            img = pygame.image.load(f"assets/{nome}.png").convert_alpha()
            return pygame.transform.scale(img, (144, 176))
        except FileNotFoundError:
            return None

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                
                if self.estado == "dialogo_inicial":
                    self.dialogo_atual = ""
                    self.estado = "animacao"
                    
                elif self.estado == "escolha":
                    if self.index_foco is not None:
                        i = self.index_foco
                        
                        # se a carta estiver virada para baixo, o clique DESVIRA ela
                        if not self.cartas_reveladas[i]:
                            self.cartas_reveladas[i] = True
                            
                        # se a carta já estiver desvirada, o clique ESCOLHE ela
                        else:
                            self.carta_escolhida = self.cartas_na_mesa[i]
                            self.dialogo_atual = "Alguns bichos do mato foram com a tua cara"
                            self.estado = "dialogo_final"
                        
                elif self.estado == "dialogo_final":
                    self.terminou = True
                    self.proxima_cena = self.proxima_depois

        if self.estado == "escolha":
            pos_mouse = pygame.mouse.get_pos()
            self.index_foco = None
            for i, rect in enumerate(self.hitboxes):
                if rect.collidepoint(pos_mouse):
                    self.index_foco = i
                    break

    def atualizar(self, dt):
        if self.estado == "animacao":
            self.progresso_animacao += dt * 0.0025  
            
            if self.progresso_animacao >= 1.0:
                self.progresso_animacao = 1.0
                self.estado = "escolha" 
            
            t = self.progresso_animacao
            fator_suave = 1 - pow(1 - t, 3)
            self.y_atual_cartas = self.y_inicial_cartas + (self.y_final_cartas - self.y_inicial_cartas) * fator_suave
            
            for i in range(3):
                self.hitboxes[i].y = self.y_atual_cartas

    def desenhar(self):
        self.tela.blit(self.fundo, (0, 0))
        
        
        if self.estado in ["animacao", "escolha", "dialogo_final"]:
            for i, carta in enumerate(self.cartas_na_mesa):
                rect_base = self.hitboxes[i].copy()
                
                if self.estado == "escolha" and i == self.index_foco:
                    rect_base.y -= 20 
                
                # DESENHA A CARTA VIRADA PARA BAIXO
                if not self.cartas_reveladas[i]:
                    if self.img_verso:
                        self.tela.blit(self.img_verso, rect_base)
                    else:
                        pygame.draw.rect(self.tela, (90, 50, 20), rect_base) 
                        pygame.draw.rect(self.tela, (218, 165, 32), rect_base, 3) 
                        txt = self.fonte_titulo.render("?", True, (218, 165, 32))
                        self.tela.blit(txt, (rect_base.centerx - txt.get_width()//2, rect_base.centery - txt.get_height()//2))
                
                # carta pos revelação :O
                else:
                    if carta.imagem:
                        self.tela.blit(carta.imagem, rect_base)
                    else:
                        pygame.draw.rect(self.tela, (200, 200, 200), rect_base)
                        pygame.draw.rect(self.tela, (255, 255, 255), rect_base, 3)
                        txt = self.fonte_cartas.render(carta.nome, True, (0,0,0))
                        self.tela.blit(txt, (rect_base.x + 10, rect_base.y + 10))
                    
                    #usando o rect base ao invés do rect carta
                    txt_vida = self.fonte_vida.render(str(carta.vida), True, (54, 32, 10))
                    self.tela.blit(txt_vida, (rect_base.x + rect_base.width - 30, rect_base.y + rect_base.height - 30))
        if self.dialogo_atual:
            largura, altura = self.tela.get_size()
            rect_caixa = pygame.Rect(100, altura - 180, largura - 200, 150)
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