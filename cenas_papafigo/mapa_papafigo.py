import pygame
from cena_base import CenaBase

class CenaMapa(CenaBase):
    def __init__(self, tela, nodo_atual=0):
        super().__init__(tela)

        self.nodo_atual = nodo_atual

        try:
            img = pygame.image.load("cenarios/mapa_papafigo.png").convert_alpha()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((50, 50, 50))

        self.nos_clicaveis = [
            {"id": 0, "rect": pygame.Rect(64, 397, 80, 80), "destino": "combate", "proximos": [1]},
            {"id": 1, "rect": pygame.Rect(198, 402, 80, 80), "destino": "fogueira", "proximos": [2,3]},
            {"id": 2, "rect": pygame.Rect(333, 193, 80, 80), "destino": "comprar_cartas", "proximos": [4]},
            {"id": 3, "rect": pygame.Rect(337, 611, 80, 80), "destino": "selos", "proximos": [4]},
            {"id": 4, "rect": pygame.Rect(472, 387, 80, 80), "destino": "combate", "proximos": [5]},
            {"id": 5, "rect": pygame.Rect(607, 392, 80, 80), "destino": "comprar_cartas", "proximos": [6,7]},
            {"id": 6, "rect": pygame.Rect(743, 211, 80, 80), "destino": "mochila", "proximos": [8]},
            {"id": 7, "rect": pygame.Rect(746, 595, 80, 80), "destino": "comprar_cartas", "proximos": [8]},
            {"id": 8, "rect": pygame.Rect(883, 393, 80, 80), "destino": "combate", "proximos": [9]},
            {"id": 9, "rect": pygame.Rect(1017, 399, 80, 80), "destino": "fogueira", "proximos": [10,11]},
            {"id": 10, "rect": pygame.Rect(1151, 203, 80, 80), "destino": "comprar_cartas", "proximos": [12]},
            {"id": 11, "rect": pygame.Rect(1149, 600, 80, 80), "destino": "fogueira", "proximos": [12]},
            {"id": 12, "rect": pygame.Rect(1300, 378, 200, 200), "destino": "combate", "proximos": []}
            ]
        
        largura_tela = tela.get_width()
        self.rect_inventario = pygame.Rect(largura_tela - 220, 30, 180, 50)
        self.fonte_btn = pygame.font.SysFont("Arial", 22, bold=True)
                

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()

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

        rect_atual = self.nos_clicaveis[self.nodo_atual]["rect"]
        ponto_x = rect_atual.centerx
        ponto_y = rect_atual.top - 10

        pygame.draw.polygon(self.tela, (255, 255, 0), [(ponto_x - 15, ponto_y - 20), (ponto_x + 15, ponto_y - 20),(ponto_x, ponto_y)])

        pygame.draw.rect(self.tela, (90, 50, 20), self.rect_inventario)
        pygame.draw.rect(self.tela, (218, 165, 32), self.rect_inventario, 3)
        
        txt_inv = self.fonte_btn.render("INVENTÁRIO", True, (255, 255, 255))
        self.tela.blit(txt_inv, (self.rect_inventario.centerx - txt_inv.get_width()//2, self.rect_inventario.centery - txt_inv.get_height()//2))