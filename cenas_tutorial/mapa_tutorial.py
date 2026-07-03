import pygame
from cena_base import CenaBase

class CenaMapa(CenaBase):
    def __init__(self, tela, nodo_atual=0):
        super().__init__(tela)

        self.nodo_atual = nodo_atual

        try:
            img = pygame.image.load("cenarios/fundo_tutorial_mapa.png").convert_alpha()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((50, 50, 50))

        self.nos_clicaveis = [
        {"id": 0, "rect": pygame.Rect(65, 400, 80, 80), "destino": "combate", "proximos": [1]},
        {"id": 1, "rect": pygame.Rect(250, 470, 80, 80), "destino": "comprar_cartas", "proximos": [2]},
        {"id": 2, "rect": pygame.Rect(390, 310, 80, 80), "destino": "mochila", "proximos": [3]},
        {"id": 3, "rect": pygame.Rect(535, 510, 80, 80), "destino": "luta_1_tutorial", "proximos": [4]},
        {"id": 4, "rect": pygame.Rect(665, 355, 80, 80), "destino": "comprar_cartas", "proximos": [5]},
        {"id": 5, "rect": pygame.Rect(740, 510, 80, 80), "destino": "matinta_tutorial", "proximos": [6]},
        {"id": 6, "rect": pygame.Rect(895, 395, 80, 80), "destino": "luta_2_tutorial", "proximos": [7,8]},
        {"id": 7, "rect": pygame.Rect(1040, 260, 80, 80), "destino": "matinta_tutorial", "proximos": [9]},
        {"id": 8, "rect": pygame.Rect(1040, 530, 80, 80), "destino": "fogueira_tutorial", "proximos": [9]},
        {"id": 9, "rect": pygame.Rect(1190, 400, 80, 80), "destino": "luta_3_tutorial", "proximos": []}]
        
        largura_tela = tela.get_width()
        self.rect_inventario = pygame.Rect(largura_tela - 220, 30, 180, 50)
        self.fonte_btn = pygame.font.SysFont("Arial", 22, bold=True)
        self.rect_pular_mapa = pygame.Rect(50, 20, 300, 52)
                

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()

                if self.rect_pular_mapa.collidepoint(pos_mouse):
                    self.proxima_cena = "fim_tutorial"
                    self.terminou = True
                    return

                if self.rect_inventario.collidepoint(pos_mouse):
                    self.proxima_cena = "inventario"
                    self.terminou = True
                    return

                opcoes_validas = self.nos_clicaveis[self.nodo_atual]["proximos"]
                
                for no in self.nos_clicaveis:
                    if no["rect"].collidepoint(pos_mouse):
                        if no["id"] in opcoes_validas:
                            self.nodo_atual = no["id"]
                            self.proxima_cena = no["destino"] 
                            self.terminou = True 
                            return

    def atualizar(self, dt):
            pass

    def desenhar(self):
        self.tela.blit(self.fundo, (0, 0))
        opcoes_validas = self.nos_clicaveis[self.nodo_atual]["proximos"]


        rect_atual = self.nos_clicaveis[self.nodo_atual]["rect"]
        ponto_x = rect_atual.centerx
        ponto_y = rect_atual.top - 10

        pygame.draw.polygon(self.tela, (255, 255, 0), [(ponto_x - 15, ponto_y - 20), (ponto_x + 15, ponto_y - 20),(ponto_x, ponto_y)])

        pygame.draw.rect(self.tela, (225, 180, 50), self.rect_pular_mapa)
        pygame.draw.rect(self.tela, (255, 255, 255), self.rect_pular_mapa, 3)
        txt_pular = self.fonte_btn.render("PULAR MAPA", True, (30, 30, 30))
        self.tela.blit(txt_pular, (
            self.rect_pular_mapa.centerx - txt_pular.get_width()//2,
            self.rect_pular_mapa.centery - txt_pular.get_height()//2
        ))

        pygame.draw.rect(self.tela, (90, 50, 20), self.rect_inventario)
        pygame.draw.rect(self.tela, (218, 165, 32), self.rect_inventario, 3)
        
        txt_inv = self.fonte_btn.render("INVENTÁRIO", True, (255, 255, 255))
        self.tela.blit(txt_inv, (self.rect_inventario.centerx - txt_inv.get_width()//2, self.rect_inventario.centery - txt_inv.get_height()//2))