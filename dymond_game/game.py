import gc
import random
import time
import pygame
import sys

import main
import metodos
from dymond_game import dymond, game_data


class Game:
    """
    Clase principal del juego. Cuando se crea una instancia de la clase se crea un display de pygame. Contendra un 
    metodo llamado run() que lanzara el bucle principal del juego. 
    """

    # Constructor
    def __init__(self, player: str, conf: {}):
        pygame.init()
        dymond.create_variables(player, conf)

        self.running = True  # Controla se el juego se sigue ejecutando
        self.display = pygame.display.set_mode(game_data.RES)  # Display donde se va a renderizar el frame
        self.frame = pygame.Surface(game_data.FRAME_SIZE)  # Frame donde se va a dibujar

        self.previous_frame = None
        self.scenarios = ["andula_desert"]  # Lista de mapas
        self.pickable_list = []
        self.entity_list = []  # Lista de entidades
        self.proj_list = []  # Lista de proyectiles
        self.player = dymond.create_player('player_soldier', (0, 0), 100, (5, 12), 2, (0.12, 0), 10, 10, True, False)
        self.time_left = 0
        self.scenario = None  # Mapa del nivel
        self.true_scroll = [0, 0]  # Scroll (con valores decimales)
        self.clock = pygame.time.Clock()  # Reloj
        self.has_changed_level = True
        self.difficulty_multi = 0
        self.levels_per_scenario = 5
        self.level = 0

        self.change_map()  # Se carga un mapa
        game_data.drop_chances = dymond.load_drop_chances("dymond_game/info/drop_chances_info.json")
        game_data.animations = dymond.load_animations("dymond_game/info/animation_loader_info.json")  # Cargamos base de animaciones
        game_data.audio = dymond.load_audio("dymond_game/info/audio_loader_info.json")  # Se carga el audio

    def change_map(self):
        if self.level % self.levels_per_scenario == 0:
            self.scenario = dymond.create_scenario(random.choice(self.scenarios))
        self.has_changed_level = True
        self.player.states["RUNNING_RIGHT"] = False
        self.player.states["RUNNING_LEFT"] = False
        self.player.states["AIMING_UP"] = False
        self.player.states["SHOOTING"] = False
        self.difficulty_multi = 1 + 0.1 * self.level
        self.time_left = 60 + 2 * self.level
        self.level += 1
        self.scenario.choose_tile_map()
        self.true_scroll = [0, 0]
        self.pickable_list = []
        self.entity_list = []
        self.proj_list = []
        self.player.set_position(self.scenario.player_spawn)
        self.spawn_entities()

    def spawn_entities(self):
        enemies_to_spawn = round(10 * self.difficulty_multi)
        for i in range(enemies_to_spawn):
            to_x = self.scenario.get_tile_size()[0] * random.randint(8 + 8, self.scenario.length)
            to_y = 0
            while not self.scenario.check_collision((to_x, to_y), (32, 32)):
                to_y += 32
            print(str(to_x) + " " + str(to_y))
            self.entity_list.append(dymond.create_knifer((to_x - 32, to_y - 32), self.difficulty_multi))

    def end_level_transition(self):
        fade_in_timer = 120
        fade_out_timer = 120
        back = pygame.Surface((500, 350))
        offset = 0
        percent = int(fade_in_timer * 0.15)
        not_finished = True
        while not_finished:
            while fade_in_timer > 0:
                fade_in_timer -= 1
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)

    def new_level_transition(self, frames):
        gc.collect()
        timer = frames
        back = pygame.Surface((500, 350))
        offset = 0
        percent = int(frames*0.15)
        pygame.mixer.music.load(random.choice(self.scenario.music_tracks))
        pygame.mixer.music.set_volume(0.2 * game_data.MUSIC_VOLUME)
        pygame.mixer.music.play()
        while timer > 0:
            self.frame.blit(self.previous_frame, (0, 0))
            back.fill((0, 0, 0))
            back.set_colorkey(game_data.COLOR_KEY)
            self.frame.blit(pygame.transform.rotate(back, 75), (offset-460, -91))
            if timer > (frames-percent) or timer < percent:
                offset += 10
            else:
                self.frame.blit(dymond.text_data("Nivel: " + str(self.level), "GIGANTIC", "white"), (130, 110))
                self.frame.blit(dymond.text_data("Tiempo para la extracción:  " + str(round(self.time_left)) + "s",
                                                 "BIG", "white"), (120, 160))
            self.display.blit(pygame.transform.scale(self.frame, game_data.RES), (0, 0))
            if timer == 100:
                random.choice(game_data.audio["game"]["ready"]).play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)
            timer -= 1

    def scenario_transition(self):
        pass

    def scroll(self, player):
        player_pos = player.get_position()
        self.true_scroll[0] += (player_pos[0] - self.true_scroll[0] - game_data.CAMERA_OFFSET[0]) / 6
        self.true_scroll[1] += (player_pos[1] - self.true_scroll[1] - game_data.CAMERA_OFFSET[1]) / 6
        scroll = self.true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        return scroll

    def draw(self):
        scroll = self.scroll(self.player)
        self.scenario.render(self.frame, scroll, self.player)
        for obj in self.entity_list:
            obj.draw(self.frame, scroll)
        for proj in self.proj_list:
            proj.draw(self.frame, scroll)
        for pickable in self.pickable_list:
            pickable.draw(self.frame, scroll)
        self.player.draw(self.frame, scroll)
        self.previous_frame = dymond.render_frame(self.display, self.frame, scroll, self.clock, self.time_left,
                                                  game_data.points, self.player.hp, True, True)

    def update(self):
        self.player.update(self.player, self.scenario.collision_boxes, self.entity_list, self.proj_list,
                           self.pickable_list)
        for proj in self.proj_list:
            proj.update(self.scenario.collision_boxes, self.entity_list, self.proj_list)
        for obj in self.entity_list:
            obj.update(self.player, self.scenario.collision_boxes, self.entity_list, self.proj_list, self.pickable_list)
        for pickable in self.pickable_list:
            pickable.update(self.player, self.scenario.collision_boxes, self.entity_list, self.proj_list,
                            self.pickable_list)

    def check_end_level(self):
        if len(self.entity_list) == 0 or self.time_left <= 0:
            self.change_map()

    def check_player_death(self):
        if self.player.hp <= 0:
            self.exit_game()

    def exit_game(self):
        self.running = False
        data = metodos.buscar_jugador_nombre(game_data.PLAYER_NAME)
        if data:
            if data["puntos"] < game_data.points:
                metodos.modificar_jugador(game_data.PLAYER_NAME, game_data.points, self.level)
        main.abrir_ventana()
        pygame.quit()
        sys.exit()

    def run(self):
        while self.running:
            start = time.time()
            self.frame.fill((0, 0, 0))
            not_paused = self.event_handler()
            self.update()
            self.draw()
            self.clock.tick(game_data.CLK_TICKS)
            end = time.time()
            self.check_player_death()
            self.check_end_level()
            if not_paused:
                self.time_left -= end - start
            if self.has_changed_level:
                self.new_level_transition(300)
                self.has_changed_level = False

    def pause_menu(self):
        pygame.mixer.music.pause()
        self.player.states["RUNNING_RIGHT"] = False
        self.player.states["RUNNING_LEFT"] = False
        self.player.is_shooting = False
        self.player.is_aiming_up = False
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.unpause()
                        paused = False

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.player.states["RUNNING_RIGHT"] = True
                if event.key == pygame.K_a:
                    self.player.states["RUNNING_LEFT"] = True
                if event.key == pygame.K_SPACE:
                    self.player.start_jump()
                if event.key == pygame.K_w:
                    self.player.states["AIMING_UP"] = True
                if event.key == pygame.K_LSHIFT:
                    self.player.states["SHOOTING"] = True
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu()
                    return False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.player.states["RUNNING_RIGHT"] = False
                if event.key == pygame.K_a:
                    self.player.states["RUNNING_LEFT"] = False
                if event.key == pygame.K_w:
                    self.player.states["AIMING_UP"] = False
                if event.key == pygame.K_LSHIFT:
                    self.player.states["SHOOTING"] = False
        return True
