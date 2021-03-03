import gc
import random
import time
import pygame

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
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        pygame.init()
        dymond.create_variables(player, conf)
        game_data.points = 0

        self.running = True  # Controla se el juego se sigue ejecutando
        self.display = pygame.display.set_mode(game_data.RES)  # Display donde se va a renderizar el frame
        self.frame = pygame.Surface(game_data.FRAME_SIZE)  # Frame donde se va a dibujar

        self.previous_frame = None  # Frame anterior (para rellenar el buffer en las escenas)
        self.scenarios = ["andula_desert"]  # Lista de escenarios
        self.played_scenarios = []  # Escenarios ya jugados
        self.pickable_list = []  # Lista de elementos que se pueden recoger
        self.entity_list = []  # Lista de entidades
        self.proj_list = []  # Lista de proyectiles
        self.player = dymond.create_player('player_soldier', (0, 0), 100, (5, 12), 2, (0.12, 0), 10, 10, True, False)
        self.scenario = None  # Escenario actual
        self.true_scroll = [0, 0]  # Scroll (con valores decimales)
        self.clock = pygame.time.Clock()  # Reloj
        self.time_left = 0  # Tiempo restante en el nivel
        self.has_changed_level = True  # Variable que guarda si se ha cambiado de nivel
        self.has_changed_scenario = True  # Variable que guarda si se ha cambiado de escenario
        self.levels_per_scenario = 5  # Niveles por escenario
        self.level = 0  # Nivel actual
        self.difficulty_multi = 0  # Multiplicador de dificultad
        self.number_of_enemies = 0  # Numero de enemigos de un nivel

        self.change_map()  # Se selecciona un mapa
        game_data.drop_chances = dymond.load_drop_chances("res/info/drop_chances_info.json")
        game_data.animations = dymond.load_animations("res/info/animation_loader_info.json")
        game_data.audio = dymond.load_audio("res/info/audio_loader_info.json")

    def change_map(self):
        """

        Resetea los estados del jugador y cambia el mapa del juego. Cada 5 niveles escoge un nuevo escenario de la lista
        de escenarios, quitandolo de la lista y metiendolo en la lista de escenarios jugados. Cuando se han jugado todos
        los escenarios se vuelcan de la lista de escenarios jugados a la de escenarios disponibles.

        Cuando cambia de nivel aumenta el multiplicador de dificultad y el nivel, spawnea el jugador en la posicion de
        spawn del escenario e injecta los enemigos de forma aleatoria.

        :return:
        """
        if self.level % self.levels_per_scenario == 0:
            if len(self.scenarios) == 0:
                self.scenarios = self.played_scenarios.copy()
                self.played_scenarios.clear()
            scenario = random.choice(self.scenarios)
            self.scenarios.remove(scenario)
            self.played_scenarios.append(scenario)
            self.scenario = dymond.create_scenario(scenario)

        self.has_changed_level = True
        self.player.states["RUNNING_RIGHT"] = False
        self.player.states["RUNNING_LEFT"] = False
        self.player.states["AIMING_UP"] = False
        self.player.states["AIMING_DOWN"] = False
        self.player.states["SHOOTING"] = False
        self.difficulty_multi = 1 + 0.1 * self.level
        self.time_left = 60 + 2 * self.level
        self.level += 1

        self.scenario.choose_tile_map()
        self.pickable_list = []
        self.entity_list = []
        self.proj_list = []
        self.true_scroll = [self.scenario.player_spawn[0]/2, self.scenario.player_spawn[1]/2]
        self.player.set_position(self.scenario.player_spawn)
        self.entity_injector()
        self.number_of_enemies = len(self.entity_list)
        game_data.killed_enemies = 0

    def new_level_transition(self, frames):
        """

        Transicion entre niveles. Es una escena scripteada en la que se dibuja un rect rotado para hacer de slider donde
        hacer el blit del texto del nuevo nivel.

        :param frames:
        :return:
        """
        timer = frames
        back = pygame.Surface((500, 350))
        offset = 0
        percent = int(frames * 0.15)
        pygame.mixer.music.load(random.choice(self.scenario.music_tracks))
        pygame.mixer.music.set_volume(0.2 * game_data.MUSIC_VOLUME)
        pygame.mixer.music.play()
        while timer > 0:
            self.frame.blit(self.previous_frame, (0, 0))
            back.fill((0, 0, 0))
            back.set_colorkey(game_data.COLOR_KEY)
            self.frame.blit(pygame.transform.rotate(back, 75), (offset - 460, -90))
            if timer > (frames - percent) or timer < percent:
                offset += 10
            else:
                texto = dymond.text_data(str(self.scenario.name), "GIMONGUS", "white")
                rect: pygame.rect.Rect = texto.get_rect()
                rect.center = self.frame.get_rect().center
                rect.y = 70
                self.frame.blit(texto, rect)
                self.frame.blit(dymond.text_data("Nivel: " + str(self.level), "GIGANTIC", "white"), (130, 110))
                self.frame.blit(dymond.text_data("Tiempo para la extracción:  " + str(round(self.time_left)) + "s",
                                                 "BIG", "white"), (120, 160))
            self.display.blit(pygame.transform.scale(self.frame, game_data.RES), (0, 0))
            if timer == 100:
                random.choice(game_data.audio["game"]["ready"]).play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    timer = -1
                    self.running = False
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)
            timer -= 1

    def end_level_transition(self):
        """

        Escena de fin de nivel. Reduce la musica, y a traves de varias fases, muestra los resultados del final del nivel
        en una pantalla que se abre con un rect slider inclinado. Si el jugador ha terminado a traves de eliminar a
        todos los enemigos la escena le muestra el tiempo restante y se lo suma (1 punto por 0.1 segundos), mostrandole
        al usuario el proceso.

        :return:
        """
        self.entity_list.clear()
        pygame.mixer.music.fadeout(1000)
        fade_in_timer = 60
        after_fade_in_timer = 30
        mid_timer = 60
        fade_out_timer = 60
        after_level_points_timer = 120
        level_points = 100 * self.level
        if len(self.entity_list) == 0:
            enemies_eliminated = True
            points_print_height = 120
        else:
            enemies_eliminated = False
            points_print_height = 100
        back = pygame.Surface((1000, 700))
        offset = 0
        finished = False
        time_left_sound = True
        level_points_sound = True
        while not finished:
            self.frame.blit(self.previous_frame, (0, 0))
            back.fill((0, 0, 0))
            back.set_colorkey(game_data.COLOR_KEY)
            self.frame.blit(pygame.transform.rotate(back, -15), (offset - 1200, -300))
            if fade_in_timer > 0:
                fade_in_timer -= 1
                offset += 12
            if fade_in_timer == 0 and after_level_points_timer > 0:
                self.frame.blit(dymond.text_data("[Extraccion exitosa]", "GIMONGUS", "white"),
                                (30, 30))
                if enemies_eliminated:
                    self.frame.blit(dymond.text_data("Todos los enemigos han sido eliminados", "SMALL", "white"),
                                    (30, 60))
                    self.frame.blit(dymond.text_data("Tiempo restante:", "BIG", "white"), (30, 100))
                    self.frame.blit(dymond.text_data(str(round(self.time_left)) + "s", "BIG", "white"), (160, 100))
                    if after_fade_in_timer > 0:
                        after_fade_in_timer -= 1
                    if round(self.time_left, 1) > 0 and after_fade_in_timer == 0:
                        if time_left_sound:
                            pygame.mixer.music.load("res/sfx/game/swoop.wav")
                            pygame.mixer.music.play(-1)
                            time_left_sound = False
                        self.time_left -= 0.4
                        game_data.points += 4
                if round(self.time_left, 1) <= 0.0 and mid_timer > 0:
                    mid_timer -= 1
                    pygame.mixer.music.stop()
                if level_points > 0 and mid_timer == 0:
                    if level_points_sound:
                        pygame.mixer.music.load("res/sfx/game/swoop.wav")
                        pygame.mixer.music.play(-1)
                        level_points_sound = False
                    level_points -= self.level
                    game_data.points += self.level
                self.frame.blit(dymond.text_data("Nivel: ", "BIG", "white"), (30, 80))
                self.frame.blit(dymond.text_data(str(level_points) + "p", "BIG", "white"), (160, 80))
                self.frame.blit(dymond.text_data("Puntos:", "BIG", "white"), (30, points_print_height))
                self.frame.blit(dymond.text_data(str(game_data.points) + "p", "BIG", "white"),
                                (160, points_print_height))
            if level_points <= 0 and after_level_points_timer > 0:
                pygame.mixer.music.stop()
                after_level_points_timer -= 1
            if after_level_points_timer == 0:
                fade_out_timer -= 1
                offset += 16
            if fade_out_timer == 0:
                finished = True
            self.display.blit(pygame.transform.scale(self.frame, game_data.RES), (0, 0))
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)

    def create_enemy(self, pos: [int, int], e_type):
        """

        Metodo que crea una entidad enemiga de un tipo predefinido segun el tipo que se le pasa como parametro. Si se
        el tipo de entidad esta implementado, le asigna la posicion pasada por parametro.

        :param pos:
        :param e_type:
        :return:
        """
        if e_type == "knifer":
            return dymond.create_knifer((pos[0], pos[1]), self.difficulty_multi)
        else:
            return None

    def entity_injector(self):
        """

        Metodo que inyecta entidades de forma aleatoria en el mapa. Lo hace a traves de calcular una posicion aleatoria
        dentro del mapa (una posicion multiplo del tamaño del tile del mapa). Proyecta un rectangulo en el mapa, si
        detecta colision, entonces puede inyectar la entidad si tiene hueco encima de ese tile. Para comprobarlo,
        proyecta otro rect y comprueba si hay colision con ese segundo rectangulo con algun tile. Si no encuentra
        colision inyecta la entidad encima del primer tile y si no, genera nuevas posiciones y lo vuelve a intentar.

        :return:
        """
        enemies_to_spawn = round(10 * self.difficulty_multi)
        while enemies_to_spawn > 0:
            injected = False
            while not injected:
                chance = random.randint(0, 100)
                new_entity = None
                for entity in self.scenario.enemies:
                    if chance <= self.scenario.enemies[entity]:
                        new_entity = entity
                if new_entity is not None:
                    to_x = self.scenario.get_tile_size()[0] * random.randint(8 + 8, self.scenario.length)
                    to_y = self.scenario.get_tile_size()[1] * random.randint(0, self.scenario.height)
                    has_box_below = self.scenario.check_collision([to_x, to_y], [32, 32])
                    is_blocked = self.scenario.check_collision([to_x - 16, to_y - 32], [64, 32])
                    # self.entity_list.append(dymond.create_entity("test_box", to_x, to_y, 32, 32, 0, True, True))
                    if not is_blocked and has_box_below:
                        self.entity_list.append(self.create_enemy((to_x, to_y - 32), new_entity))
                        enemies_to_spawn -= 1
                        injected = True

    def scroll(self, player):
        """

        Calcula el scroll real del juego (float) y retorna los valores truncados (int) por el hecho de ser pixel art de
        32 pixeles (para evitar pixeles montados). Añade un offset al scroll para ajustar la "camara" que varia segun
        donde esta apuntando el jugador.

        :param player:
        :return:
        """
        player_pos = player.get_position()
        aiming_offset = 0
        if self.player.states["AIMING_UP"]:
            aiming_offset = -50
        if self.player.states["AIMING_DOWN"]:
            aiming_offset = 50
        self.true_scroll[0] += (player_pos[0] - self.true_scroll[0] - game_data.CAMERA_OFFSET[0]) / 6
        self.true_scroll[1] += (player_pos[1] - self.true_scroll[1] - game_data.CAMERA_OFFSET[1] + aiming_offset) / 6
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
                                                  game_data.points, self.player.hp, self.player.max_hp)

    def update(self):
        self.player.update(self.player, self.scenario.active_tiles, self.entity_list, self.proj_list,
                           self.pickable_list)
        for proj in self.proj_list:
            proj.update(self.scenario.active_tiles, self.entity_list, self.proj_list)
        for obj in self.entity_list:
            obj.update(self.player, self.scenario.active_tiles, self.entity_list, self.proj_list,
                       self.pickable_list)
        for pickable in self.pickable_list:
            pickable.update(self.player, self.scenario.active_tiles, self.entity_list, self.proj_list,
                            self.pickable_list)

    def check_end_level(self):
        if game_data.killed_enemies == self.number_of_enemies:
            self.end_level_transition()
            self.change_map()

    def check_player_death(self):
        if self.player.hp <= 0:
            self.player_death_screen()

    def exit_game(self):
        data = metodos.buscar_jugador_nombre(game_data.PLAYER_NAME)
        if data:
            if data["puntos"] < game_data.points:
                metodos.modificar_jugador(game_data.PLAYER_NAME, game_data.points, self.level)
        game_data.FONTS = {}
        main.abrir_ventana()
        pygame.quit()
        pygame.display.quit()
        gc.collect()

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
            if not self.running:
                self.exit_game()

    def player_death_screen(self):
        fade_in_timer = 60
        exit_delay = 120
        pygame.mixer.music.fadeout(1000)
        back = pygame.Surface((1000, 700))
        offset = 0
        play_sound = True
        while self.running:
            self.frame.blit(self.previous_frame, (0, 0))
            back.fill((0, 0, 0))
            back.set_colorkey(game_data.COLOR_KEY)
            self.frame.blit(pygame.transform.rotate(back, -15), (offset - 1200, -300))
            if fade_in_timer > 0:
                fade_in_timer -= 1
                offset += 12
            if fade_in_timer == 0:
                if play_sound:
                    random.choice(game_data.audio["game"]["death_screen"]).play()
                    play_sound = False
                self.frame.blit(dymond.text_data("[MISION FALLIDA]", "GIMONGUS", "white"), (30, 30))
                self.frame.blit(dymond.text_data("Has muerto", "HUGE", "white"), (30, 60))
                self.frame.blit(dymond.text_data("Llegaste al nivel " + str(self.level), "HUGE", "white"), (30, 90))
                self.frame.blit(dymond.text_data("Tus puntos: " + str(game_data.points) + "p", "HUGE", "white"),
                                (30, 120))
                if exit_delay > 0:
                    exit_delay -= 1
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and exit_delay == 0:
                        self.running = False
                if exit_delay == 0:
                    self.frame.blit(dymond.text_data("Pulsa cualquier tecla ->", "SMALL", "white"),
                                    (350, 240))
            self.display.blit(pygame.transform.scale(self.frame, game_data.RES), (0, 0))
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)

    def pause_screen(self):
        pygame.mixer.music.pause()
        self.player.states["RUNNING_RIGHT"] = False
        self.player.states["RUNNING_LEFT"] = False
        self.player.states["AIMING_DOWN"] = False
        self.player.states["AIMING_UP"] = False
        self.player.states["SHOOTING"] = False
        paused = True
        back = pygame.Surface(game_data.FRAME_SIZE, flags=pygame.SRCALPHA)
        while paused:
            self.frame.blit(self.previous_frame, (0, 0))
            back.fill((100, 100, 100, 150))
            back.set_colorkey(game_data.COLOR_KEY)
            self.frame.blit(back, (0, 0))
            texto = dymond.text_data("[PAUSA]", "GIMONGUS", "black")
            rect: pygame.rect.Rect = texto.get_rect()
            rect.center = self.frame.get_rect().center
            self.frame.blit(texto, rect)
            texto = dymond.text_data("Pulsa [ESC] para salir", "SMALL", "black")
            rect: pygame.rect.Rect = texto.get_rect()
            rect.center = self.frame.get_rect().center
            rect.y += 30
            self.frame.blit(texto, rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    paused = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pygame.mixer.music.unpause()
                        paused = False
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                        self.running = False
            self.display.blit(pygame.transform.scale(self.frame, game_data.RES), (0, 0))
            pygame.display.update()
            self.clock.tick(game_data.CLK_TICKS)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.player.states["RUNNING_RIGHT"] = True
                if event.key == pygame.K_a:
                    self.player.states["RUNNING_LEFT"] = True
                if event.key == pygame.K_SPACE:
                    self.player.start_jump()
                if event.key == pygame.K_w:
                    self.player.states["AIMING_UP"] = True
                if event.key == pygame.K_s:
                    self.player.states["AIMING_DOWN"] = True
                if event.key == pygame.K_LSHIFT:
                    self.player.states["SHOOTING"] = True
                if event.key == pygame.K_p:
                    self.pause_screen()
                    return False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.player.states["RUNNING_RIGHT"] = False
                if event.key == pygame.K_a:
                    self.player.states["RUNNING_LEFT"] = False
                if event.key == pygame.K_w:
                    self.player.states["AIMING_UP"] = False
                if event.key == pygame.K_s:
                    self.player.states["AIMING_DOWN"] = False
                if event.key == pygame.K_LSHIFT:
                    self.player.states["SHOOTING"] = False
        return True
