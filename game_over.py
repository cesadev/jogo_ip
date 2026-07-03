import pygame
import cv2
from cena_base import CenaBase


class CenaGameOver(CenaBase):
    def __init__(self, tela):
        super().__init__(tela)
        self.terminou = False
        self.proxima_cena = "menu"

        self.video = None
        self.frame_atual = None
        self.frame_counter = 0
        self.fps_video = 24
        self.fundo = None

        try:
            self.video = cv2.VideoCapture("cenarios/gameover screen.mp4")
            if self.video.isOpened():
                self.fps_video = self.video.get(cv2.CAP_PROP_FPS)
                print("✓ Tela de game over carregada com sucesso!")
            else:
                raise Exception("Não conseguiu abrir o vídeo")
        except Exception as e:
            print(f"⚠ Não foi possível carregar a tela de game over: {e}")
            self.video = None
            self.fundo = pygame.Surface(tela.get_size())
            self.fundo.fill((0, 0, 0))

        # Carrega a logo do canto inferior direito
        try:
            self.logo = pygame.image.load("cenarios/logo cdu disco de makita.png").convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (100, 100))
        except FileNotFoundError:
            self.logo = None

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                self.terminou = True
                self.proxima_cena = "menu"
                return

    def atualizar(self, dt):
        if self.video and self.video.isOpened():
            self.frame_counter += 1
            fps_game = 60
            atualizacoes_por_frame_video = fps_game / max(self.fps_video, 1)

            if self.frame_counter >= atualizacoes_por_frame_video:
                ret, frame = self.video.read()

                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(
                        frame_rgb,
                        (self.tela.get_width(), self.tela.get_height()),
                        interpolation=cv2.INTER_LANCZOS4,
                    )
                    frame_surface = pygame.image.fromstring(
                        frame_resized.tobytes(),
                        (self.tela.get_width(), self.tela.get_height()),
                        "RGB",
                    )
                    self.frame_atual = frame_surface
                else:
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

                self.frame_counter = 0

    def desenhar(self):
        if self.frame_atual:
            self.tela.blit(self.frame_atual, (0, 0))
        elif self.fundo:
            self.tela.blit(self.fundo, (0, 0))
        else:
            self.tela.fill((0, 0, 0))

        fonte_pequena = pygame.font.SysFont("Arial", 28)
        texto_pequeno = fonte_pequena.render("Clique ou pressione qualquer tecla para voltar ao menu", True, (255, 255, 255))
        rect_pequeno = texto_pequeno.get_rect(center=(self.tela.get_width() // 2, self.tela.get_height() // 2 + 320))
        self.tela.blit(texto_pequeno, rect_pequeno)

        if self.logo:
            logo_rect = self.logo.get_rect(bottomright=(self.tela.get_width() - 90, self.tela.get_height() - 80))
            self.tela.blit(self.logo, logo_rect)
