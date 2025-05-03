import pygame
from particle import *
from forces import *
from display import *



running = True


GRAVITY_SET = [GravityManager, CollisionManager, DragManager, ScreenCollisionManager]
GRAVITATION_SET = [GravAttractionManager, CollisionManager, DragManager, ScreenCollisionManager]
SPACE_SET = [CollisionManager, GravAttractionManager]
POINT_GRAVITATION_SET = [DragManager, GravAttractionManager]

particle_system = ParticleSystem()

particle_system.setup(SCREEN_DIMENSIONS, SPACE_SET)

particle_system.create_particles_random(75)


pygame.init()

clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS:
                particle_system.create_particles_random(1)
            if event.key == pygame.K_MINUS:
                particle_system.remove_particle(-1)
            if event.key == pygame.K_r:
                particle_system.clear()
                particle_system.create_particles_random(75)
            if event.key == pygame.K_p:
                particle_system.print_info()

    
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()
        particle_system.create_particle(mouse_pos[0], mouse_pos[1], color=(200, 200, 200))


    screen.fill(BG_COLOR)

    particle_system.update()
    particle_system.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)