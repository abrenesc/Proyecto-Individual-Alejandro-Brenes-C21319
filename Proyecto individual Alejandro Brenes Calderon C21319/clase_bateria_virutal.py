
"""
@author: Alejandro pc
"""

import pygame
from pygame import mixer

class Bateria_virtual:
    def __init__(self, ancho=1400, alto=800, colores=None):
        
        """
        Inicializa la clase Bateria_virtual.
        
        Args:
            ancho (int): Ancho de la ventana de la aplicación. Default de 1400.
            alto (int): Alto de la ventana de la aplicación. Default de 800.
            colores (dict): Diccionario con los colores utilizados en la aplicación. Si no se proporciona, se usan los valores por defecto.
        """
        
        pygame.init()
        self.ancho = ancho
        self.alto = alto
        self.colores = colores if colores else {
            'negro': (0, 0, 0),
            'blanco': (255, 255, 255),
            'gris': (128, 128, 128),
            'gris_oscuro': (50, 50, 50),
            'gris_claro': (170, 170, 170),
            'azul': (0, 255, 255),
            'rojo': (255, 0, 0),
            'verde': (0, 255, 0),
            'dorado': (212, 175, 55)
        }
        self.longitud_activa = 0
        self.beat_activos = 0

        self.hi_hat = mixer.Sound('data\hi hat.wav')
        self.snare = mixer.Sound('data/snare.wav')
        self.kick = mixer.Sound('data/kick.wav')
        self.crash = mixer.Sound('data/crash.wav')
        self.clap = mixer.Sound('data/clap.wav')
        self.tom = mixer.Sound('data/tom.wav')

        self.pantalla = pygame.display.set_mode([self.ancho, self.alto])
        pygame.display.set_caption('Bateria Virtual')
        self.label_font = pygame.font.Font('data/Advert Regular.ttf', 32)
        self.medium_font = pygame.font.Font('data/Advert Regular.ttf', 24)
        self.cambio_en_beats = True
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.beats = 8
        self.bpm = 240
        self.instrumentos = 6
        self.tocando = True
        self.pulsados = [[-1 for _ in range(self.beats)] for _ in range(self.instrumentos)]
        self.lista_activos = [1 for _ in range(self.instrumentos)]
        pygame.mixer.set_num_channels(self.instrumentos * 3)
        self.menu_guardar = False
        self.load_menu = False
        self.saved_beats = []
        self.cargar_ritmos_guardados()
        self.beat_name = ''
        self.escribiendo = False
        self.index = 100
        self.corriendo = True

    def cargar_ritmos_guardados(self):
        
        """
        Carga los ritmos guardados desde un archivo de texto.
        """
        
        try:
            with open('saved_beats.txt', 'r') as file:
                for line in file:
                    self.saved_beats.append(line)
        except FileNotFoundError:
            pass

    def dibujar_cuadricula(self, clicks, beat, actives):
        
        """
        Dibuja la cuadrícula de la interfaz de la batería.

        Args:
            clicks (list): Matriz que representa los estados de cada celda de la cuadrícula.
            beat (int): El beat actual que se está reproduciendo.
            actives (list): Lista que indica qué instrumentos están activos.

        Returns:
            cuadricula (list): Lista de tuplas que contienen los rectángulos de la cuadrícula y sus coordenadas.
        """        
        
        cuadricula = []
        left_box = pygame.draw.rect(self.pantalla, self.colores['blanco'], [0, 0, 200, self.alto - 200], 3)
        bottom_box = pygame.draw.rect(self.pantalla, self.colores['blanco'], [0, 0, self.ancho, 200], 3)
        for i in range(self.instrumentos + 1):
            pygame.draw.line(self.pantalla, self.colores['gris'], (0, i * 100), (200, i * 100), 4)
        colors = [self.colores['gris'], self.colores['blanco'], self.colores['gris']]
        hi_hat_text = self.label_font.render('     Hi Hat', True, colors[actives[0]])
        self.pantalla.blit(hi_hat_text, (30, 50))
        snare_text = self.label_font.render('      Caja', True, colors[actives[1]])
        self.pantalla.blit(snare_text, (30, 130))
        kick_text = self.label_font.render('     Tom', True, colors[actives[2]])
        self.pantalla.blit(kick_text, (30, 230))
        crash_text = self.label_font.render('    Crash', True, colors[actives[3]])
        self.pantalla.blit(crash_text, (30, 330))
        aplauso_text = self.label_font.render('    Aplauso', True, colors[actives[4]])
        self.pantalla.blit(aplauso_text, (30, 430))
        tom_text = self.label_font.render('     Bombo', True, colors[actives[5]])
        self.pantalla.blit(tom_text, (30, 530))
        for i in range(self.beats):
            for j in range(self.instrumentos):
                if clicks[j][i] == -1:
                    color = self.colores['gris_oscuro']
                else:
                    if actives[j] == 1:
                        color = self.colores['blanco']
                    else:
                        color = self.colores['negro']
                rect = pygame.draw.rect(self.pantalla, color,
                                        [i * ((self.ancho - 200) // self.beats) + 205, (j * 100) + 5,
                                         ((self.ancho - 200) // self.beats) - 10, 90], 0, 3)
                pygame.draw.rect(self.pantalla, self.colores['dorado'],
                                 [i * ((self.ancho - 200) // self.beats) + 200, j * 100,
                                  ((self.ancho - 200) // self.beats), 100], 5, 5)
                pygame.draw.rect(self.pantalla, self.colores['negro'],
                                 [i * ((self.ancho - 200) // self.beats) + 200, j * 100,
                                  ((self.ancho - 200) // self.beats), 100], 2, 5)
                cuadricula.append((rect, (i, j)))
        active = pygame.draw.rect(self.pantalla, self.colores['verde'],
                                  [beat * ((self.ancho - 200) // self.beats) + 200, 0,
                                   ((self.ancho - 200) // self.beats), self.instrumentos * 100], 5, 2)
        return cuadricula

    def tocar_instrumentos(self):
        
        """
        Reproduce los sonidos de los instrumentos activos en el beat actual.
        """        
        
        for i in range(len(self.pulsados)):
            if self.pulsados[i][self.beat_activos] == 1 and self.lista_activos[i] == 1:
                if i == 0:
                    self.hi_hat.play()
                if i == 1:
                    self.snare.play()
                if i == 2:
                    self.kick.play()
                if i == 3:
                    self.crash.play()
                if i == 4:
                    self.clap.play()
                if i == 5:
                    self.tom.play()

    def menu_guardados(self, beat_name, escribiendo):
        
        """
        Dibuja el menú de guardado de ritmos.

        Args:
            beat_name (str): Nombre del ritmo que se está guardando.
            escribiendo (bool): Indica si el usuario está escribiendo el nombre del ritmo.

        Returns:
            tuple: Botones de salida y guardado, nombre del ritmo y rectángulo de entrada de texto.
        """        
        
        pygame.draw.rect(self.pantalla, self.colores['negro'], [0, 0, self.ancho, self.alto])
        menu_text = self.label_font.render('Nombre del ritmo', True, self.colores['blanco'])
        self.pantalla.blit(menu_text, (400, 40))
        exit_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [self.ancho - 200, self.alto - 100, 180, 90], 0, 5)
        exit_text = self.label_font.render('Cerrar', True, self.colores['blanco'])
        self.pantalla.blit(exit_text, (self.ancho - 160, self.alto - 70))
        saving_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [self.ancho // 2 - 100, self.alto * 0.75, 200, 100], 0, 5)
        saving_text = self.label_font.render('Guardar ritmo', True, self.colores['blanco'])
        self.pantalla.blit(saving_text, (self.ancho // 2 - 20, self.alto * 0.75 + 30))
        if escribiendo:
            pygame.draw.rect(self.pantalla, self.colores['gris_oscuro'], [400, 200, 800, 200], 0, 5)
        entry_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [400, 200, 600, 200], 5, 5)
        entry_text = self.label_font.render(f'{beat_name}', True, self.colores['blanco'])
        self.pantalla.blit(entry_text, (430, 250))
        return exit_btn, saving_btn, beat_name, entry_rect

    def menu_cargados(self, index):
        
        """
        Método para manejar el menú de ritmos guardados. Permite al usuario ver y seleccionar ritmos 
        previamente guardados.
    
        Manejo de eventos:
        - Detecta clics del ratón y determina si un ritmo guardado ha sido seleccionado.
        - Carga el ritmo seleccionado en la secuencia de beats actual.
    
        Interfaz de usuario:
        - Dibuja el menú de ritmos guardados en la pantalla.
        - Muestra los nombres de los ritmos guardados y permite al usuario desplazarse por la lista si hay 
          más ritmos de los que caben en la pantalla.
        """        
        
        cargado_pulsados = []
        cargado_beats = 0
        cargado_bpm = 0
        pygame.draw.rect(self.pantalla, self.colores['negro'], [0, 0, self.ancho, self.alto])
        menu_text = self.label_font.render('Ritmos cargados: Seleccione un ritmo', True, self.colores['blanco'])
        self.pantalla.blit(menu_text, (400, 40))
        exit_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [self.ancho - 200, self.alto - 100, 180, 90], 0, 5)
        exit_text = self.label_font.render('Cerrar', True, self.colores['blanco'])
        self.pantalla.blit(exit_text, (self.ancho - 160, self.alto - 70))
        loading_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [self.ancho // 2 - 100, self.alto * 0.75, 200, 100], 0, 5)
        loading_text = self.label_font.render('Cargar ritmo', True, self.colores['blanco'])
        self.pantalla.blit(loading_text, (self.ancho // 2 - 60, self.alto * 0.75 + 30))
        loaded_rectangle = pygame.draw.rect(self.pantalla, self.colores['gris'], [190, 90, 1000, 600], 5, 5)
        if 0 <= index < len(self.saved_beats):
            pygame.draw.rect(self.pantalla, self.colores['gris_claro'], [190, 90 + index * 50, 1000, 50])
        for beat in range(len(self.saved_beats)):
            if beat < 10:
                beat_clicked = []
                row_text = self.medium_font.render(f'{beat + 1}', True, self.colores['blanco'])
                self.pantalla.blit(row_text, (200, 100 + beat * 50))
                name_index_start = self.saved_beats[beat].index('nombre: ') + 8
                name_index_end = self.saved_beats[beat].index(', pulsados:')
                name_text = self.medium_font.render(self.saved_beats[beat][name_index_start:name_index_end], True, self.colores['blanco'])
                self.pantalla.blit(name_text, (240, 100 + beat * 50))
        return exit_btn, loading_btn, cargado_pulsados, cargado_beats, cargado_bpm

    def main_loop(self):
        
        """
        Método principal del bucle de la aplicación. Maneja eventos, actualiza el estado de la aplicación 
        y renderiza la pantalla en cada iteración del bucle. Este método se ejecuta continuamente mientras
        la aplicación esté corriendo.
    
        Manejo de eventos:
        - Detecta eventos de cierre de ventana y teclas presionadas.
        - Cambia el estado de reproducción y la velocidad de BPM en respuesta a entradas del usuario.
    
        Actualización del estado:
        - Actualiza el índice del beat activo basado en el tiempo y el BPM.
        - Reproduce sonidos si el beat activo coincide con los beats pulsados.
    
        Renderización:
        - Dibuja la interfaz de usuario y los beats en la pantalla.
        """
        
        while self.corriendo:
            self.timer.tick(self.fps)
            self.pantalla.fill(self.colores['negro'])
            cuadricula = self.dibujar_cuadricula(self.pulsados, self.beat_activos, self.lista_activos)
            play_pause = pygame.draw.rect(self.pantalla, self.colores['gris'], [50, self.alto - 150, 200, 100], 0, 5)
            play_text = self.label_font.render('Tocar/Pausar', True, self.colores['blanco'])
            self.pantalla.blit(play_text, (70, self.alto - 130))
            if self.tocando:
                play_text2 = self.medium_font.render('Tocando', True, self.colores['verde'])
            else:
                play_text2 = self.medium_font.render('Pausado', True, self.colores['rojo'])
            self.pantalla.blit(play_text2, (70, self.alto - 100))
            bpm_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [300, self.alto - 150, 200, 100], 5, 5)
            bpm_text = self.medium_font.render('BPM', True, self.colores['blanco'])
            self.pantalla.blit(bpm_text, (370, self.alto - 130))
            bpm_text2 = self.label_font.render(f'{self.bpm}', True, self.colores['blanco'])
            self.pantalla.blit(bpm_text2, (370, self.alto - 100))
            bpm_add_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [510, self.alto - 150, 48, 48], 0, 5)
            bpm_sub_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [510, self.alto - 100, 48, 48], 0, 5)
            add_text = self.medium_font.render('+5', True, self.colores['blanco'])
            sub_text = self.medium_font.render('-5', True, self.colores['blanco'])
            self.pantalla.blit(add_text, (520, self.alto - 140))
            self.pantalla.blit(sub_text, (520, self.alto - 90))
            beats_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [600, self.alto - 150, 200, 100], 5, 5)
            beats_text = self.medium_font.render('Beats en Loop', True, self.colores['blanco'])
            self.pantalla.blit(beats_text, (620, self.alto - 130))
            beats_text2 = self.label_font.render(f'{self.beats}', True, self.colores['blanco'])
            self.pantalla.blit(beats_text2, (680, self.alto - 100))
            beats_add_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [810, self.alto - 150, 48, 48], 0, 5)
            beats_sub_rect = pygame.draw.rect(self.pantalla, self.colores['gris'], [810, self.alto - 100, 48, 48], 0, 5)
            add_text2 = self.medium_font.render('+1', True, self.colores['blanco'])
            sub_text2 = self.medium_font.render('-1', True, self.colores['blanco'])
            self.pantalla.blit(add_text2, (820, self.alto - 140))
            self.pantalla.blit(sub_text2, (820, self.alto - 90))
            clear = pygame.draw.rect(self.pantalla, self.colores['gris'], [900, self.alto - 150, 200, 100], 0, 5)
            clear_text = self.label_font.render('Limpiar todo', True, self.colores['blanco'])
            self.pantalla.blit(clear_text, (920, self.alto - 120))
            guardar_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [1150, self.alto - 150, 200, 48], 0, 5)
            guardar_text = self.label_font.render('Guardar', True, self.colores['blanco'])
            self.pantalla.blit(guardar_text, (1160, self.alto - 140))
            cargar_btn = pygame.draw.rect(self.pantalla, self.colores['gris'], [1150, self.alto - 100, 200, 48], 0, 5)
            cargar_text = self.label_font.render('Cargar', True, self.colores['blanco'])
            self.pantalla.blit(cargar_text, (1160, self.alto - 90))
            if self.cambio_en_beats:
                self.tocar_instrumentos()
                self.cambio_en_beats = False
            if self.tocando:
                if self.longitud_activa < self.bpm:
                    self.longitud_activa += 1
                else:
                    self.longitud_activa = 0
                    if self.beat_activos < self.beats - 1:
                        self.beat_activos += 1
                        self.cambio_en_beats = True
                    else:
                        self.beat_activos = 0
                        self.cambio_en_beats = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.corriendo = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(cuadricula)):
                        if cuadricula[i][0].collidepoint(event.pos):
                            coords = cuadricula[i][1]
                            self.pulsados[coords[1]][coords[0]] *= -1
                    if play_pause.collidepoint(event.pos):
                        if self.tocando:
                            self.tocando = False
                        elif not self.tocando:
                            self.tocando = True
                    elif bpm_add_rect.collidepoint(event.pos):
                        self.bpm += 5
                    elif bpm_sub_rect.collidepoint(event.pos):
                        self.bpm -= 5
                    elif beats_add_rect.collidepoint(event.pos):
                        self.beats += 1
                        for i in range(len(self.pulsados)):
                            self.pulsados[i].append(-1)
                    elif beats_sub_rect.collidepoint(event.pos):
                        self.beats -= 1
                        for i in range(len(self.pulsados)):
                            self.pulsados[i].pop(-1)
                    elif clear.collidepoint(event.pos):
                        self.pulsados = [[-1 for _ in range(self.beats)] for _ in range(self.instrumentos)]
                    elif guardar_btn.collidepoint(event.pos):
                        self.menu_guardar = True
                    elif cargar_btn.collidepoint(event.pos):
                        self.load_menu = True
                if event.type == pygame.TEXTINPUT and self.escribiendo:
                    self.beat_name += event.text
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.menu_guardar:
                        self.guardar_ritmo()
                    if event.key == pygame.K_BACKSPACE and len(self.beat_name) > 0:
                        self.beat_name = self.beat_name[:-1]
            if self.menu_guardar:
                exit_btn, saving_btn, self.beat_name, entry_rect = self.menu_guardados(self.beat_name, self.escribiendo)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(event.pos):
                        self.menu_guardar = False
                        self.escribiendo = False
                        self.beat_name = ''
                    if entry_rect.collidepoint(event.pos):
                        if self.escribiendo:
                            self.escribiendo = False
                        elif not self.escribiendo:
                            self.escribiendo = True
                    if saving_btn.collidepoint(event.pos):
                        self.guardar_ritmo()
                        self.menu_guardar = False
                        self.escribiendo = False
                        self.beat_name = ''
            if self.load_menu:
                exit_btn, loading_btn, self.pulsados, self.beats, self.bpm = self.menu_cargados(self.index)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(event.pos):
                        self.load_menu = False
                        self.tocando = True
                    if loading_btn.collidepoint(event.pos):
                        self.cargar_ritmo(self.index)
                        self.load_menu = False
                        self.tocando = True
                    for i in range(len(self.saved_beats)):
                        if pygame.Rect(190, 100 + i * 50, 1000, 50).collidepoint(event.pos):
                            self.index = i
            pygame.display.flip()
        pygame.quit()

    def guardar_ritmo(self):
        
        """
        Guarda el ritmo actual en el archivo de ritmos guardados.

        Args:
            nombre (str): Nombre del ritmo a guardar.
        """        
        
        if self.beat_name:
            with open('saved_beats.txt', 'w') as file:
                self.saved_beats.append(
                    f'nombre: {self.beat_name}, pulsados: {self.pulsados}, beats: {self.beats}, bpm: {self.bpm}\n')
                for i in range(len(self.saved_beats)):
                    file.write(str(self.saved_beats[i]))

    def cargar_ritmo(self, index):
        
        """
        Dibuja el menú de carga de ritmos guardados.

        Args:
            index (int): Índice del ritmo seleccionado para cargar.
        """    
        
        self.pulsados = []
        if 0 <= index < len(self.saved_beats):
            self.beat_name = self.saved_beats[index]
            beat_string = self.beat_name.split(', pulsados: ')[1]
            beat_string = beat_string.split(', beats: ')
            beat_beats = int(beat_string[1].split(', bpm: ')[0])
            beat_bpm = int(beat_string[1].split(', bpm: ')[1].split('\n')[0])
            beat_clicks = beat_string[0].split('], [')
            for x in range(len(beat_clicks)):
                beat_clicks[x] = beat_clicks[x].replace('[', '')
                beat_clicks[x] = beat_clicks[x].replace(']', '')
                beat_clicks[x] = beat_clicks[x].split(', ')
            for x in range(len(beat_clicks)):
                for y in range(len(beat_clicks[x])):
                    beat_clicks[x][y] = int(beat_clicks[x][y])
            self.pulsados = beat_clicks
            self.beats = beat_beats
            self.bpm = beat_bpm

    #A continuación, los métodos get set y str de la clase
    
    def get_ancho(self):
        return self.ancho

    def set_ancho(self, nuevo_ancho):
        self.ancho = nuevo_ancho

    def get_alto(self):
        return self.alto

    def set_alto(self, nuevo_alto):
        self.alto = nuevo_alto

    def get_colores(self):
        return self.colores

    def set_colores(self, nuevos_colores):
        self.colores = nuevos_colores

    def get_longitud_activa(self):
        return self.longitud_activa

    def set_longitud_activa(self, nueva_longitud_activa):
        self.longitud_activa = nueva_longitud_activa

    def get_beat_activos(self):
        return self.beat_activos

    def set_beat_activos(self, nuevos_beat_activos):
        self.beat_activos = nuevos_beat_activos

    def get_hi_hat(self):
        return self.hi_hat

    def set_hi_hat(self, nuevo_hi_hat):
        self.hi_hat = nuevo_hi_hat

    def get_snare(self):
        return self.snare

    def set_snare(self, nuevo_snare):
        self.snare = nuevo_snare

    def get_kick(self):
        return self.kick

    def set_kick(self, nuevo_kick):
        self.kick = nuevo_kick

    def get_crash(self):
        return self.crash

    def set_crash(self, nuevo_crash):
        self.crash = nuevo_crash

    def get_clap(self):
        return self.clap

    def set_clap(self, nuevo_clap):
        self.clap = nuevo_clap

    def get_tom(self):
        return self.tom

    def set_tom(self, nuevo_tom):
        self.tom = nuevo_tom

    def get_pantalla(self):
        return self.pantalla

    def set_pantalla(self, nueva_pantalla):
        self.pantalla = nueva_pantalla

    def get_label_font(self):
        return self.label_font

    def set_label_font(self, nueva_label_font):
        self.label_font = nueva_label_font

    def get_medium_font(self):
        return self.medium_font

    def set_medium_font(self, nueva_medium_font):
        self.medium_font = nueva_medium_font

    def get_cambio_en_beats(self):
        return self.cambio_en_beats

    def set_cambio_en_beats(self, nuevo_cambio_en_beats):
        self.cambio_en_beats = nuevo_cambio_en_beats

    def get_timer(self):
        return self.timer

    def set_timer(self, nuevo_timer):
        self.timer = nuevo_timer

    def get_fps(self):
        return self.fps

    def set_fps(self, nuevo_fps):
        self.fps = nuevo_fps

    def get_beats(self):
        return self.beats

    def set_beats(self, nuevos_beats):
        self.beats = nuevos_beats

    def get_bpm(self):
        return self.bpm

    def set_bpm(self, nuevo_bpm):
        if nuevo_bpm > 0:
            self.bpm = nuevo_bpm
        else:
            raise ValueError("BPM debe ser un valor positivo.")

    def get_instrumentos(self):
        return self.instrumentos

    def set_instrumentos(self, nuevos_instrumentos):
        self.instrumentos = nuevos_instrumentos

    def get_tocando(self):
        return self.tocando

    def set_tocando(self, nuevo_tocando):
        self.tocando = nuevo_tocando

    def get_pulsados(self):
        return self.pulsados

    def set_pulsados(self, nuevos_pulsados):
        self.pulsados = nuevos_pulsados

    def get_lista_activos(self):
        return self.lista_activos

    def set_lista_activos(self, nueva_lista_activos):
        self.lista_activos = nueva_lista_activos

    def get_menu_guardar(self):
        return self.menu_guardar

    def set_menu_guardar(self, nuevo_menu_guardar):
        self.menu_guardar = nuevo_menu_guardar

    def get_load_menu(self):
        return self.load_menu

    def set_load_menu(self, nuevo_load_menu):
        self.load_menu = nuevo_load_menu

    def get_saved_beats(self):
        return self.saved_beats

    def set_saved_beats(self, nuevos_saved_beats):
        self.saved_beats = nuevos_saved_beats

    def get_beat_name(self):
        return self.beat_name

    def set_beat_name(self, nuevo_beat_name):
        self.beat_name = nuevo_beat_name

    def get_escribiendo(self):
        return self.escribiendo

    def set_escribiendo(self, nuevo_escribiendo):
        self.escribiendo = nuevo_escribiendo

    def get_index(self):
        return self.index

    def set_index(self, nuevo_index):
        self.index = nuevo_index

    def get_corriendo(self):
        return self.corriendo

    def set_corriendo(self, nuevo_corriendo):
        self.corriendo = nuevo_corriendo

    def __str__(self):
        return (f'Bateria_virtual(ancho={self.ancho}, alto={self.alto}, colores={self.colores}, '
                f'longitud_activa={self.longitud_activa}, beat_activos={self.beat_activos}, '
                f'hi_hat={self.hi_hat}, snare={self.snare}, kick={self.kick}, crash={self.crash}, '
                f'clap={self.clap}, tom={self.tom}, pantalla={self.pantalla}, label_font={self.label_font}, '
                f'medium_font={self.medium_font}, cambio_en_beats={self.cambio_en_beats}, timer={self.timer}, '
                f'fps={self.fps}, beats={self.beats}, bpm={self.bpm}, instrumentos={self.instrumentos}, '
                f'tocando={self.tocando}, pulsados={self.pulsados}, lista_activos={self.lista_activos}, '
                f'menu_guardar={self.menu_guardar}, load_menu={self.load_menu}, saved_beats={self.saved_beats}, '
                f'beat_name={self.beat_name}, escribiendo={self.escribiendo}, index={self.index}, '
                f'corriendo={self.corriendo})')

if __name__ == "__main__":
    bateria = Bateria_virtual()
    bateria.main_loop()
