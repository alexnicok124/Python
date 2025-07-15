import numpy as np
import pygame
import random
import matplotlib.pyplot as plt

# Inicializamos Pygame
pygame.init()
# Configuración de la ventana
screenwidth = 800
screenheight = 600
screen = pygame.display.set_mode((screenwidth, screenheight))

# Constantes para la simulación
Fuerza_repulsion = 5000  # Fuerza de repulsión entre las partículas
Distancia_minima = 50  # Distancia mínima a la que se sienten las partículas
Disipacion_energia = 0.01  # Factor de disipación de energía

# Categorías de partículas según masa
Masa_pequena_max = 5
Masa_mediana_min = 5
Masa_mediana_max = 20
Masa_grande_min = 20

class Particula:
    def __init__(self, masa, posicion, radio, color, energia_interna):
        self.masa = masa  # Masa de la partícula
        self.posicion = posicion  # Posición inicial
        self.radio = radio  # Radio de la partícula
        self.color = color  # Color de la partícula
        self.movimiento = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])  # Dirección aleatoria
        self.energia_interna = energia_interna  # Energía interna de la partícula
        self.velocidad = np.sqrt(2 * self.energia_interna / self.masa)  # Cálculo de la velocidad a partir de la energía
        self.actualizar_velocidad()
        if masa >= 0 and masa <= 10:
            self.color = (0, 0, 255)
        elif masa > 10 and masa <= 20:
            self.color = (0, 255, 0)
        else: 
            self.color = (255, 0, 0)

    def actualizar_velocidad(self):
        norma = np.linalg.norm(self.movimiento) #Esto sirve para normalizar y que no hayan cosas raras...
        if norma > 0:
            self.movimiento = (self.movimiento / norma) * self.velocidad  # Mantener la dirección pero actualizar la magnitud

    def moverse(self, delta_time):
        nueva_posicion = self.posicion + self.movimiento * self.velocidad * delta_time * 70
        
        # Verificamos si la nueva posición es válida
        if np.any(np.isnan(nueva_posicion)):
            nueva_posicion = self.posicion  # Si hay NaN, mantenemos la posición original
            #Porque me ha pasado que mientras hacia la simulación me petaba y no entendía por qué

        self.posicion = nueva_posicion

        # Colisiones con las paredes (rebote)
        if self.posicion[0] <= self.radio or self.posicion[0] >= screenwidth - self.radio:
            self.movimiento[0] *= -1  # Rebotar en el eje X
        if self.posicion[1] <= self.radio or self.posicion[1] >= screenheight - self.radio:
            self.movimiento[1] *= -1  # Rebotar en el eje Y

        self.actualizar_velocidad()  # Actualizamos la velocidad en función de la energía interna

    def aplicar_colision(self, otra_particula):
        distancia = np.linalg.norm(self.posicion - otra_particula.posicion)

        if distancia < self.radio + otra_particula.radio:
            direccion = self.posicion - otra_particula.posicion
            direccion_normalizada = direccion / np.linalg.norm(direccion)
            velocidad_relativa = self.movimiento - otra_particula.movimiento
            velocidad_relativa_dot = np.dot(velocidad_relativa, direccion_normalizada)

            if velocidad_relativa_dot < 0:  # Si hay colisión
                energia_total = self.energia_interna + otra_particula.energia_interna

                # Verificamos qué partícula tiene más energía
                if self.energia_interna > otra_particula.energia_interna:
                    delta_energia = (self.energia_interna - otra_particula.energia_interna) * 0.1
                    self.energia_interna -= delta_energia
                    otra_particula.energia_interna += delta_energia
                else:
                    delta_energia = (otra_particula.energia_interna - self.energia_interna) * 0.1
                    self.energia_interna += delta_energia
                    otra_particula.energia_interna -= delta_energia

                #aplico todas las fórmulas necesarias para el choque inelástico
                energia_total_nueva = self.energia_interna + otra_particula.energia_interna
                self.energia_interna = (self.energia_interna / energia_total_nueva) * energia_total
                otra_particula.energia_interna = (otra_particula.energia_interna / energia_total_nueva) * energia_total

                self.velocidad = np.sqrt(2 * self.energia_interna / self.masa)
                otra_particula.velocidad = np.sqrt(2 * otra_particula.energia_interna / otra_particula.masa)

                v1_nueva = self.movimiento - (2 * otra_particula.masa / (self.masa + otra_particula.masa)) * np.dot(self.movimiento - otra_particula.movimiento, direccion_normalizada) * direccion_normalizada
                v2_nueva = otra_particula.movimiento - (2 * self.masa / (self.masa + otra_particula.masa)) * np.dot(otra_particula.movimiento - self.movimiento, direccion_normalizada) * direccion_normalizada

                self.movimiento = v1_nueva
                otra_particula.movimiento = v2_nueva

                self.actualizar_velocidad()
                otra_particula.actualizar_velocidad() #cambio la velocidad


class Simulacion:
    def __init__(self, n_particulas, delta_time=0.02): #clase "main" o principal del programa
        self.n_particulas = n_particulas
        self.delta_time = delta_time
        self.particulas = []
        self.crear_particulas()

    def crear_particulas(self): #aquí están todas las partículas que usaremos
        for _ in range(self.n_particulas):
            masa = random.uniform(1, 30)  # Masa aleatoria entre 1 y 30
            radio = random.uniform(5, 20)  # Radio entre 5 y 20
            posicion = np.array([random.uniform(0, screenwidth), random.uniform(0, screenheight)])
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            energia_interna = 0.5 * masa * np.linalg.norm(np.array([random.uniform(-1, 1), random.uniform(-1, 1)]))**2
            self.particulas.append(Particula(masa, posicion, radio, color, energia_interna)) #creo la lista "particulas"
            #nota: en python el self sirve para crear nuevas variables de toda la clase
    def separar_por_categoria(self):
        pequeñas = []
        medianas = []
        grandes = []
        
        for part in self.particulas:
            if part.masa <= Masa_pequena_max:
                pequeñas.append(part)
            elif Masa_mediana_min <= part.masa <= Masa_mediana_max:
                medianas.append(part)
            else:
                grandes.append(part)
                
        return pequeñas, medianas, grandes

    def energia_total(self):
        total_energia = 0
        for part in self.particulas:
            total_energia += part.energia_interna
        return total_energia

    def estadisticas(self):
        energias = [part.energia_interna for part in self.particulas]
        return energias

    def ejecutar(self):
        clock = pygame.time.Clock()
        running = True
        energia_total = []
        energia_media_pequenas = []
        energia_media_medianas = []
        energia_media_grandes = []

        # Separar las partículas en categorías al inicio
        pequenas, medianas, grandes = self.separar_por_categoria()

        # Guardamos las energías al inicio
        energias_iniciales = self.estadisticas()

        while running:
            delta_time = clock.tick(60) / 1000.0  # Tiempo en segundos desde el último fotograma 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))  

            # Procesar partículas y colisiones
            for part1 in self.particulas:
                part1.moverse(delta_time)
                for part2 in self.particulas:
                    if part1 != part2:
                        part1.aplicar_colision(part2)

                # Dibujar la partícula
                if not np.any(np.isnan(part1.posicion)):
                    pygame.draw.circle(screen, part1.color, (int(part1.posicion[0]), int(part1.posicion[1])), int(part1.radio))

            # Almacenar energía total y energía media por categoría
            energia_total.append(self.energia_total())
            energia_media_pequenas.append(np.mean([part.energia_interna for part in pequenas]))
            energia_media_medianas.append(np.mean([part.energia_interna for part in medianas]))
            energia_media_grandes.append(np.mean([part.energia_interna for part in grandes]))

            pygame.display.flip()  # cosas de pygame... no son importantes

        pygame.quit()  # Cerrar Pygame

        # guardamos los datos 
        energias_finales = self.estadisticas()

        # Graficar los resultados
        plt.figure(figsize=(10, 6))

        # Histograma inicial
        plt.subplot(2, 1, 1)
        plt.hist(energias_iniciales, bins=30, density=True, alpha=0.6, color='b', label='Energía Inicial')
        plt.xlabel('Energía Interna')
        plt.ylabel('Densidad de Probabilidad')
        plt.title('Distribución de Energías Iniciales')
        plt.legend()

        # Histograma de las energías finales
        plt.subplot(2, 1, 2)
        plt.hist(energias_finales, bins=30, density=True, alpha=0.6, color='r', label='Energía Final')
        plt.xlabel('Energía Interna')
        plt.ylabel('Densidad de Probabilidad')
        plt.title('Distribución de Energías Finales')
        plt.legend()

        plt.tight_layout()
        plt.show()

# Ejecutar la simulación y finalizar
simulacion = Simulacion(50)
simulacion.ejecutar()
