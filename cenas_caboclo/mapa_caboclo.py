import pygame
from cena_base import CenaBase

class CenaMapa(CenaBase):
    def __init__(self, tela, nodo_atual=0):
        super().__init__(tela)

        self.nodo_atual = nodo_atual

        try:
            img = pygame.image.load("cenarios/mapa_caboclo.png").convert_alpha()
            self.fundo = pygame.transform.scale(img, tela.get_size())
        except FileNotFoundError:
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((50, 50, 50))

          
        self.nos_clicaveis = [
            {"id": 0, "rect": pygame.Rect(46, 420, 80, 80), "destino": "combate", "proximos": [1]},
            {"id": 1, "rect": pygame.Rect(190, 415, 80, 80), "destino": "comprar_cartas_caboclo", "proximos": [2,3]},
            {"id": 2, "rect": pygame.Rect(212, 128, 80, 80), "destino": "mochila", "proximos": [4]},
            {"id": 3, "rect": pygame.Rect(209, 551, 80, 80), "destino": "fogueira", "proximos": [5]},
            {"id": 4, "rect": pygame.Rect(396, 109, 80, 80), "destino": "luta_1_mapa_1", "proximos": [8]},
            {"id": 5, "rect": pygame.Rect(410, 542, 80, 80), "destino": "luta_2_mapa_1", "proximos": [6,7]},
            {"id": 6, "rect": pygame.Rect(538, 399, 80, 80), "destino": "selos", "proximos": [9]},
            {"id": 7, "rect": pygame.Rect(519, 703, 80, 80), "destino": "mochila", "proximos": [10]},
            {"id": 8, "rect": pygame.Rect(649, 116, 80, 80), "destino": "comprar_cartas_caboclo", "proximos": [11]},
            {"id": 9, "rect": pygame.Rect(744, 436, 80, 80), "destino": "comprar_cartas_caboclo", "proximos": [12]},
            {"id": 10, "rect": pygame.Rect(745, 694, 80, 80), "destino": "fogueira", "proximos": [12]},
            {"id": 11, "rect": pygame.Rect(843, 117, 80, 80), "destino": "fogueira", "proximos": [12]},
            {"id": 12, "rect": pygame.Rect(882, 414, 80, 80), "destino": "luta_3_mapa_1", "proximos": [13, 14]},
            {"id": 13, "rect": pygame.Rect(925, 257, 80, 80), "destino": "comprar_cartas_caboclo", "proximos": [15]},
            {"id": 14, "rect": pygame.Rect(970, 532, 80, 80), "destino": "fogueira", "proximos": [16]},
            {"id": 15, "rect": pygame.Rect(1118, 257, 80, 80), "destino": "fogueira", "proximos": [17]},
            {"id": 16, "rect": pygame.Rect(1140, 524, 80, 80), "destino": "selos", "proximos": [17]},
            {"id": 17, "rect": pygame.Rect(1260, 375, 200, 200), "destino": "boss_1", "proximos": []}]
        
        largura_tela = tela.get_width()
        self.rect_inventario = pygame.Rect(largura_tela - 220, 30, 180, 50)
        self.rect_pular_mapa = pygame.Rect(50, 20, 300, 52)
        self.fonte_btn = pygame.font.SysFont("Arial", 22, bold=True)
                

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()

                if self.rect_pular_mapa.collidepoint(pos_mouse):
                    self.proxima_cena = "mapa_papafigo"
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