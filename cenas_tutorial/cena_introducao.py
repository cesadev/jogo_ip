import pygame
import cv2
import numpy as np
from cena_base import CenaBase

class CenaIntroducao(CenaBase):
    def __init__(self, tela):
        super().__init__(tela)

        self.dialogos = ["Outro atrevido. Já faz um tempo...", "Talvez tu não te lembre dessa história...", "Deixa eu refrescar a tua memória..."]
        self.indice_atual = 0
        
        # Carrega o vídeo
        self.video = None
        self.frame_atual = None
        self.frame_counter = 0
        self.fps_video = 24
        
        try:
            self.video = cv2.VideoCapture("cenarios/video tutorial.mp4")
            if self.video.isOpened():
                self.fps_video = self.video.get(cv2.CAP_PROP_FPS)
            else:
                raise Exception("Não conseguiu abrir o vídeo")
        except Exception:
            self.video = None

    
    def processar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    self.indice_atual += 1

                    if self.indice_atual >= len(self.dialogos):
                        self.terminou = True
                        self.proxima_cena = "tutorial"

    def atualizar(self, dt):
        # Atualiza o frame do vídeo sincronizado com tempo real
        if self.video and self.video.isOpened():
            self.frame_counter += 1
            
            # Sincroniza com 60 FPS do jogo
            fps_game = 60
            atualizacoes_por_frame_video = fps_game / self.fps_video
            
            if self.frame_counter >= atualizacoes_por_frame_video:
                ret, frame = self.video.read()
                
                if ret:
                    # Converte BGR para RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Redimensiona diretamente para a resolução da tela com interpolação de alta qualidade
                    frame_resized = cv2.resize(frame_rgb, (self.tela.get_width(), self.tela.get_height()), interpolation=cv2.INTER_LANCZOS4)
                    
                    # Converte para surface do Pygame
                    frame_surface = pygame.image.fromstring(
                        frame_resized.tobytes(),
                        (self.tela.get_width(), self.tela.get_height()),
                        "RGB"
                    )
                    
                    self.frame_atual = frame_surface
                else:
                    # Reinicia o vídeo quando chega ao fim
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                self.frame_counter = 0

    def desenhar(self):
        # Desenha o vídeo como fundo
        if self.frame_atual:
            self.tela.blit(self.frame_atual, (0, 0))
        else:
            self.tela.fill((30, 30, 30))
        
        if self.indice_atual < len(self.dialogos):
            largura, altura = self.tela.get_size()
            

            rect_caixa = pygame.Rect(100, altura - 180, largura - 200, 150)
            pygame.draw.rect(self.tela, (10, 10, 10), rect_caixa)
            pygame.draw.rect(self.tela, (200, 200, 200), rect_caixa, 4)

            texto = self.dialogos[self.indice_atual]
            fonte = pygame.font.SysFont("Arial", 40)
            img_texto = fonte.render(texto, True, (255, 255, 255))
            self.tela.blit(img_texto, (rect_caixa.x + 30, rect_caixa.y + 50))

            triangulo = [
                (rect_caixa.right - 40, rect_caixa.bottom - 40), 
                (rect_caixa.right - 20, rect_caixa.bottom - 40), 
                (rect_caixa.right - 30, rect_caixa.bottom - 20)
            ]
            pygame.draw.polygon(self.tela, (255, 255, 255), triangulo)
