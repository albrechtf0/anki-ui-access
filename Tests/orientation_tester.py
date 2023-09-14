import VisMapGenerator as vmg
from importlib import reload
from anki import TrackPieceTypes
import pygame
from math import cos, sin, pi

pygame.init()
DISPLAYSURF = pygame.display.set_mode((500,500))
FONT = pygame.font.SysFont("Arial",18)
CLOCK = pygame.time.Clock()
CURVE = pygame.image.load("Kurve.png")

def draw_coordinfo():
    orientations = (
        (1,0),
        (0,-1),
        (-1,0),
        (0,1)
    )
    for i, o in enumerate(orientations):
        surf = FONT.render(str(o),True,(0,0,0))
        rect = surf.get_rect()
        angle = i*pi/2
        rect.centerx = 250+200*cos(angle)
        rect.centery = 250-200*sin(angle)
        DISPLAYSURF.blit(
            surf,
            rect
        )
        pass
    pass

i = 0
flipping = False
while True:
    vmg = reload(vmg)

    DISPLAYSURF.fill((255,255,255))
    draw_coordinfo()

    a, b = list(vmg._CURVE_ROTATIONS_LOOKUP.keys())[i]
    if flipping:
        a, b = (b, a)

    r, f = vmg.orientation_to_rotation(TrackPieceTypes.CURVE,a,b)
    surf: pygame.Surface = pygame.transform.flip(
        pygame.transform.rotate(CURVE,r),
        f, False
    )
    rect = surf.get_rect()
    rect.center = (250,250)
    DISPLAYSURF.blit(surf,rect)
    DISPLAYSURF.blit(FONT.render(str((a,b)),True,(0,0,0)),(0,0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            i += 1
            if i >= len(vmg._CURVE_ROTATIONS_LOOKUP):
                i = 0
                flipping = not flipping
                if not flipping:
                    print("Round complete")
                pass
            pass
        pass
    pygame.display.update()
    CLOCK.tick(60)
    pass