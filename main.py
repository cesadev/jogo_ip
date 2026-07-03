import pygame
import random
from cena_base import CenaBase
from menu import Menu
from cartas import Carta
from cenas_tutorial.cena_introducao import CenaIntroducao
from cenas_tutorial.tutorial import CenaTutorial
from cenas_tutorial.fim_tutorial import CenaFimTutorial

from cenas_tutorial.mapa_tutorial import CenaMapa
from cenas_caboclo.mapa_caboclo import CenaMapa as CenaMapaCaboclo
from cenas_papafigo.mapa_papafigo import CenaMapa as CenaMapaPapafigo

from cenas_tutorial.combate_tutorial import CenaCombateTutorial

from cenas_tutorial.matinta_tutorial import CenaMatinta as CenaMatintaTutorial
from matinta import CenaMatinta

from batalha import CenaCombate
from cenas_tutorial.fases_tutorial import fases_do_tutorial
from cenas_caboclo.fases_caboclo import fases_do_jogo as fases_do_caboclo
from cenas_papafigo.fases_papafigo import fases_do_jogo as fases_do_papafigo
from comprar_cartas import CenaEscolhaCarta
from cenas_tutorial.creditos import CenaCreditos
from inventario import CenaInventario
from cenas_tutorial.mochila_tutorial import CenaMochila
from cenas_tutorial.cena_opcoes import CenaOpcoes
from cenas_tutorial.cena_pause import CenaPause
from cenas_tutorial.fogueira_tutorial import CenaFogueiraTutorial
from fogueira import CenaFogueira
from game_over import CenaGameOver

def efeito_transicao(tela, cena_nova):
    largura, altura = tela.get_size()
    superficie_fade = pygame.Surface((largura, altura))
    superficie_fade.fill((0, 0, 0))
    relogio = pygame.time.Clock()

    for alfa in range(0, 255, 10):
        superficie_fade.set_alpha(alfa)
        tela.blit(superficie_fade, (0, 0))
        pygame.display.update()
        relogio.tick(60)

    for alfa in range(255, 0, -10):
        cena_nova.desenhar()
        superficie_fade.set_alpha(alfa)
        tela.blit(superficie_fade, (0, 0))
        pygame.display.update()
        relogio.tick(60)


def mudar_cena(nova_cena_obj):
    """Helper pra transicionar entre cenas"""
    efeito_transicao(tela, nova_cena_obj)
    return nova_cena_obj


def main():
    pygame.init()
    pygame.mixer.init()
    musica_pausada = False

    try:
        pygame.mixer.music.load("Musicas/Instrumental game.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    LARGURA, ALTURA = 1536, 864
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Ouro e Cachaça")

    # --- Carregamento de imagens de cartas ---
    nomes_cartas = [
        "acaua", "anhanga", "boitata", "caboclo", "capelobo",
        "chupa-cabra", "cobra_coral", "comadre", "cuca",
        "curupira", "la_ursa", "leao", "mula", "timbu", "perna", "cacto"
    ]
    imagens_cartas = {}
    for nome in nomes_cartas:
        try:
            img_original = pygame.image.load(f"cartas/{nome}.png").convert_alpha()
            imagens_cartas[nome] = pygame.transform.scale(img_original, (144, 176))
        except FileNotFoundError:
            imagens_cartas[nome] = None

    # --- Carregamento de versos ---
    nomes_versos = ["verso_carta", "verso_perna"]
    imagens_versos = {}
    for nome in nomes_versos:
        try:
            img_original = pygame.image.load(f"verso/{nome}.png").convert_alpha()
            imagens_versos[nome] = pygame.transform.scale(img_original, (144, 176))
        except FileNotFoundError:
            imagens_versos[nome] = None

    # --- Elementos de interface ---
    imagens_ui = {
        "campainha": pygame.transform.scale(
            pygame.image.load("assets/campainha.png").convert_alpha(), (120, 120)),
        "copo1": pygame.transform.scale(
            pygame.image.load("assets/copo1.png").convert_alpha(), (80, 96)),
        "copo2": pygame.transform.scale(
            pygame.image.load("assets/copo2.png").convert_alpha(), (80, 96)),
        "combate": pygame.transform.scale(
            pygame.image.load("cenarios/combate.png").convert(), (LARGURA, ALTURA)),
    }

    relogio = pygame.time.Clock()
    cena_atual = Menu(tela)

    # --- Estados globais ---
    vida_player_global = 2
    nivel_batalha_global = 1
    nodo_atual_tutorial_global = 0
    nodo_atual_caboclo_global = 0
    nodo_atual_papafigo_global = 0
    mapa_atual = "tutorial"
    deck_jogador_global = []
    itens_jogador_global = []

    def reiniciar_estado_jogo():
        nonlocal vida_player_global, nivel_batalha_global
        nonlocal nodo_atual_tutorial_global, nodo_atual_caboclo_global, nodo_atual_papafigo_global
        nonlocal mapa_atual, deck_jogador_global, itens_jogador_global

        vida_player_global = 2
        nivel_batalha_global = 1
        nodo_atual_tutorial_global = 0
        nodo_atual_caboclo_global = 0
        nodo_atual_papafigo_global = 0
        mapa_atual = "tutorial"

        deck_jogador_global = [
            Carta("Capelobo", 1, 2, imagens_cartas["capelobo"], 1, 1),
            Carta("Curupira", 3, 2, imagens_cartas["curupira"], 2, 1),
            Carta("Capelobo", 1, 2, imagens_cartas["capelobo"], 1, 1),
            Carta("Caboclo", 1, 1, imagens_cartas["caboclo"], 1, 1, selos=["mergulhador"]),
        ]
        itens_jogador_global = []

    reiniciar_estado_jogo()

    rodando = True
    proxima = None

    while rodando:
        dt = relogio.tick(60)
        eventos = pygame.event.get()
        pausa_pedido = False

        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    if musica_pausada:
                        pygame.mixer.music.unpause()
                        musica_pausada = False
                    else:
                        pygame.mixer.music.pause()
                        musica_pausada = True
                elif evento.key == pygame.K_ESCAPE:
                    if not isinstance(cena_atual, (Menu, CenaPause)):
                        pausa_pedido = True

        if pausa_pedido:
            cena_atual = CenaPause(tela, cena_atual)
            eventos = []

        cena_atual.processar_eventos(eventos)
        cena_atual.atualizar(dt)
        cena_atual.desenhar()

        # --- Transições ao terminar uma cena ---
        if hasattr(cena_atual, 'terminou') and cena_atual.terminou:

            # Salva vida ao sair de combate
            if isinstance(cena_atual, CenaCombate):
                try:
                    posicao_musica = getattr(cena_atual, "posicao_musica_anterior_ms", 0)
                    pygame.mixer.music.load("Musicas/Instrumental game.mp3")
                    pygame.mixer.music.set_volume(0.6)
                    pygame.mixer.music.play(-1, start=posicao_musica / 1000.0)
                except pygame.error:
                    pass

                vida_player_global = cena_atual.vida_player
                if getattr(cena_atual, 'resultado', None) == "vitoria":
                    nivel_batalha_global += 1

            # Salva posição do mapa atual
            if isinstance(cena_atual, CenaMapa) and hasattr(cena_atual, 'nodo_atual'):
                nodo_atual_tutorial_global = cena_atual.nodo_atual
                mapa_atual = "tutorial"
            elif isinstance(cena_atual, CenaMapaCaboclo) and hasattr(cena_atual, 'nodo_atual'):
                nodo_atual_caboclo_global = cena_atual.nodo_atual
                mapa_atual = "caboclo"
            elif isinstance(cena_atual, CenaMapaPapafigo) and hasattr(cena_atual, 'nodo_atual'):
                nodo_atual_papafigo_global = cena_atual.nodo_atual
                mapa_atual = "papafigo"
 
            # Adiciona carta escolhida ao deck
            if hasattr(cena_atual, 'carta_escolhida') and cena_atual.carta_escolhida is not None:
                deck_jogador_global.append(cena_atual.carta_escolhida)
                cena_atual.carta_escolhida = None

            #agr dá um shuffle no deck atual, pra deixar mais dinamica a escolha de cartas round a round
            random.shuffle(deck_jogador_global)
            
            # Adiciona itens adquiridos
            if hasattr(cena_atual, 'itens_adquiridos') and cena_atual.itens_adquiridos:
                for item in cena_atual.itens_adquiridos:
                    itens_jogador_global.append(item)
                cena_atual.itens_adquiridos = []

            proxima = cena_atual.proxima_cena
            cena_atual.terminou = False

        # Instância direta da CenaBase
        if isinstance(proxima, CenaBase):
            cena_atual = proxima
            proxima = None

        # Roteamento por string (O controle vai ser principalmente através da string "proxima")
        # Modularizar isso em breve se possível.
        elif proxima == "introducao":
            reiniciar_estado_jogo()
            nova_cena = CenaIntroducao(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "tutorial":
            nova_cena = CenaTutorial(tela, imagens_versos, imagens_cartas, imagens_ui)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "fim_tutorial":
            nova_cena = CenaFimTutorial(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        elif proxima == "mapa":
            if mapa_atual == "caboclo":
                nova_cena = CenaMapaCaboclo(tela, nodo_atual_caboclo_global)
            
            elif mapa_atual == "papafigo":
                nova_cena = CenaMapaPapafigo(tela, nodo_atual_papafigo_global)

            else:
                nova_cena = CenaMapa(tela, nodo_atual_tutorial_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "mapa_caboclo":
            mapa_atual = "caboclo"
            nova_cena = CenaMapaCaboclo(tela, nodo_atual_caboclo_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "mapa_papafigo":
            mapa_atual = "papafigo"
            nova_cena = CenaMapaPapafigo(tela, nodo_atual_papafigo_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
            
        elif proxima == "inventario":
            nova_cena = CenaInventario(tela, deck_jogador_global, itens_jogador_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "comprar_cartas":
            nova_cena = CenaEscolhaCarta(tela, imagens_versos, imagens_cartas, imagens_ui)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        # ==== SEÇÃO DE EVENTOS ====
        elif proxima == "comprar_cartas_caboclo":
            nova_cena = CenaEscolhaCarta(
                tela, imagens_versos, imagens_cartas, imagens_ui,
                proxima_depois="mapa_caboclo"
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "mochila":
            nova_cena = CenaMochila(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        elif proxima == "fogueira":
            nova_cena = CenaFogueira(tela, deck_jogador_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "fogueira_tutorial":
            nova_cena = CenaFogueiraTutorial(tela, deck_jogador_global)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "matinta":
            if mapa_atual == "caboclo":
                destino_volta = "mapa_caboclo"

            elif mapa_atual == "papafigo":
                destino_volta = "mapa_papafigo"
            else:
                destino_volta = "mapa"

            nova_cena = CenaMatinta(tela, imagens_cartas, deck_jogador_global, destino_volta)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "matinta_tutorial":
            destino_volta = "mapa"
            nova_cena = CenaMatinta(tela, imagens_cartas, deck_jogador_global, destino_volta)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        #==============SEÇÃO DE LUTAS =============
        #1. LUTAS DO TUTORIAL
        elif proxima == "luta_1_tutorial":
            dados_fase = fases_do_tutorial.get("luta_1_tutorial")
            nome_fase = "luta_1_tutorial"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )            
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "luta_2_tutorial":
            dados_fase = fases_do_tutorial.get("luta_2_tutorial")
            nome_fase = "luta_2_tutorial"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "luta_3_tutorial":
            dados_fase = fases_do_tutorial.get("luta_3_tutorial")
            nome_fase = "luta_3_tutorial"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )

            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        #2. LUTAS DO MAPA_CABOCLO

        elif proxima == "luta_1_mapa_1":
            dados_fase = fases_do_caboclo.get("luta_1_mapa_1")
            nome_fase = "luta_1_mapa_1"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        elif proxima == "luta_2_mapa_1":
            dados_fase = fases_do_caboclo.get("luta_2_mapa_1")
            nome_fase = "luta_2_mapa_1"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        elif proxima == "luta_3_mapa_1":
            dados_fase = fases_do_caboclo.get("luta_3_mapa_1")
            nome_fase = "luta_3_mapa_1"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        elif proxima == "boss_1":
            dados_fase = fases_do_caboclo.get("boss_1")
            nome_fase = "boss_1"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        
        #3. LUTAS DO MAPA_PAPAFIGO

        elif proxima == "luta_1_mapa_2":
            dados_fase = fases_do_papafigo.get("luta_1_mapa_2")
            nome_fase = "luta_1_mapa_2"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        elif proxima == "luta_2_mapa2":
            dados_fase = fases_do_papafigo.get("luta_2_mapa2")
            nome_fase = "luta_2_mapa2"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None
        elif proxima == "boss_2":
            dados_fase = fases_do_papafigo.get("boss_2")
            nome_fase = "boss_2"
            nova_cena = CenaCombate(
                tela, deck_jogador_global, dados_fase,
                itens_jogador_global, vida_player_global,
                imagens_versos, imagens_cartas, imagens_ui, nome_fase
            )
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        #fim da parte das lutas, vou ter que modularizar isso pq ficou mt grande...
        #=============================================================

        # ====== CENAS DO MENU ===========
        elif proxima == "creditos":
            nova_cena = CenaCreditos(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif isinstance(proxima, tuple) and len(proxima) == 2 and proxima[0] == "opcoes":
            cena_anterior = proxima[1]
            nova_cena = CenaOpcoes(tela, cena_anterior=cena_anterior)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "opcoes":
            nova_cena = CenaOpcoes(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "pause":
            cena_atual = CenaPause(tela, cena_atual)
            proxima = None

        elif proxima == "menu":
            reiniciar_estado_jogo()
            nova_cena = Menu(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None

        elif proxima == "game_over":
            nova_cena = CenaGameOver(tela)
            efeito_transicao(tela, nova_cena)
            cena_atual = nova_cena
            proxima = None


        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()