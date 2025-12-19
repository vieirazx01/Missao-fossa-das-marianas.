import pygame
import random
import sys

# --- INICIALIZAÇÃO ---
pygame.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Missao Mariana: MODO HARD")

FPS = 60
clock = pygame.time.Clock()

# --- VARIÁVEIS ---
profundidade = 0
recorde = 0
vidas = 3
estado = "descendo"
bolhas = []
obstaculos = []

def carregar_img(nome, tamanho):
    try:
        img = pygame.image.load(nome + ".png").convert_alpha()
        return pygame.transform.scale(img, tamanho)
    except:
        surf = pygame.Surface(tamanho)
        if nome == "submarino": surf.fill((0, 255, 0))
        elif nome == "coracao": surf.fill((255, 0, 0))
        else: surf.fill((150, 150, 150))
        return surf

# --- CARREGAMENTO (Tamanhos que ficaram bons) ---
SUBMARINO_IMG = carregar_img("submarino", (130, 70))
ROCHA_IMG = carregar_img("rocha", (90, 110))
AGUA_VIVA_IMG = carregar_img("aguaviva", (70, 80))
CORACAO_IMG = carregar_img("coracao", (40, 40))

submarino_rect = SUBMARINO_IMG.get_rect(center=(400, 150))
submarino_mask = pygame.mask.from_surface(SUBMARINO_IMG)

def resetar():
    global profundidade, vidas, estado, obstaculos, bolhas, recorde
    if profundidade > recorde: recorde = profundidade
    profundidade = 0
    vidas = 3
    estado = "descendo"
    obstaculos.clear()
    bolhas.clear()
    submarino_rect.center = (400, 150)

# --- LOOP PRINCIPAL ---
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()
    
    # MUDANÇA DE COR DO OCEANO (A que você gostou)
    azul = max(10, 180 - (profundidade // 25))
    verde = max(0, 80 - (profundidade // 50))
    tela.fill((0, verde, azul))

    if estado == "descendo":
        # CONTROLES (Sensibilidade aumentada)
        vel_sub = 9
        if teclas[pygame.K_LEFT] and submarino_rect.left > 0: submarino_rect.x -= vel_sub
        if teclas[pygame.K_RIGHT] and submarino_rect.right < LARGURA: submarino_rect.x += vel_sub
        if teclas[pygame.K_UP] and submarino_rect.top > 0: submarino_rect.y -= vel_sub
        if teclas[pygame.K_DOWN] and submarino_rect.bottom < ALTURA: submarino_rect.y += vel_sub

        profundidade += 4 # Descendo com velocidade!
        vel_queda = 6 + (profundidade // 800) # Obstáculos ficam muito rápidos depois

        # EFEITO DE BOLHAS
        if random.randint(1, 10) == 1:
            bolhas.append([random.randint(0, LARGURA), ALTURA + 10, random.randint(2, 5)])
        
        for b in bolhas[:]:
            b[1] -= b[2]
            pygame.draw.circle(tela, (255, 255, 255, 100), (b[0], b[1]), b[2], 1)
            if b[1] < -10: bolhas.remove(b)

        # GERADOR DE OBSTÁCULOS (Dificuldade aumentada para 1 em 18)
        if random.randint(1, 18) == 1:
            img = random.choice([ROCHA_IMG, AGUA_VIVA_IMG])
            rect = img.get_rect(topleft=(random.randint(0, 700), -150))
            mask = pygame.mask.from_surface(img)
            obstaculos.append({"rect": rect, "img": img, "mask": mask})

        # MOVIMENTO E COLISÃO PIXEL PERFECT
        for ob in obstaculos[:]:
            ob["rect"].y += vel_queda
            tela.blit(ob["img"], ob["rect"])
            
            offset = (ob["rect"].left - submarino_rect.left, ob["rect"].top - submarino_rect.top)
            if submarino_mask.overlap(ob["mask"], offset):
                vidas -= 1
                obstaculos.remove(ob)
                if vidas <= 0: estado = "fim"
            
            if ob["rect"].top > ALTURA:
                obstaculos.remove(ob)

        # DESENHAR SUBMARINO
        tela.blit(SUBMARINO_IMG, submarino_rect)

        # PLACAR (HUD)
        fonte = pygame.font.SysFont("Consolas", 28, bold=True)
        tela.blit(fonte.render(f"PROFUNDIDADE: {profundidade}m", True, (255, 255, 255)), (20, 20))
        tela.blit(fonte.render(f"RECORDE: {recorde}m", True, (255, 255, 0)), (20, 55))
        
        for i in range(vidas):
            tela.blit(CORACAO_IMG, (LARGURA - 55 - (i * 45), 20))

    elif estado == "fim":
        f_g = pygame.font.SysFont("Arial", 60, bold=True)
        tela.blit(f_g.render("FIM DA LINHA", True, (255, 50, 50)), (LARGURA//2 - 180, ALTURA//2 - 50))
        f_p = pygame.font.SysFont("Arial", 30)
        tela.blit(f_p.render("Pressione R para tentar de novo", True, (255, 255, 255)), (LARGURA//2 - 190, ALTURA//2 + 30))
        if teclas[pygame.K_r]: resetar()

    pygame.display.flip()