import Car as C
import queue
import pygame
import numpy as np
import random
import time
import threading
import math


class Simulation:
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (200, 100, 0),
             (100, 200, 0), (100, 0, 200), (200, 0, 100)]

    def __init__(self, psize):
        self.screen_width = 640
        self.screen_height = 480
        self.alpha = 0.002
        self.car_list = []
        self.ps = psize
        self.crash_count = 0

    def simulation(self):
        pygame.init()
        T = np.zeros((self.screen_height, 1), float)
        t = np.random.randint(-50, 50, (self.screen_height, 1))
        T1 = np.zeros((self.screen_height, 1), float)
        t1 = np.random.randint(-50, 50, (self.screen_height, 1))
        for i in range(1, self.screen_height):
            T[i] = self.alpha * t[i] + (1 - self.alpha) * T[i - 1]
            T1[i] = self.alpha * t1[i] + (1 - self.alpha) * T1[i - 1]
        for  i in range(self.ps):
            self.car_list.append(C.Car(self.color[i%10]))
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        #self.screen.fill((255,255,255))
        #pygame.display.update()
        pygame.display.set_caption('Road Simulation')
        exitLoop = False
        tim = 1
        t[0] = random.choice(range(-50, 50, 20))
        t1[0] = random.choice(range(-50, 50, 20))
        #x=np.zeros((self.screen_height, 1), float)+70
        while not exitLoop:
            pygame.event.get()
            #print(tim)
            self.screen.fill((255, 255, 255))
            for i in range(0, self.screen_height - 1, 1):
                # print(T[i],T[i+1],t[i])
                pygame.draw.line(self.screen, (0, 0, 0), (T[i] + 250, i), (T[i + 1] + 250, i + 1))
                pygame.draw.line(self.screen, (0, 0, 0), (T1[i] + 350, i), (T1[i + 1] + 350, i + 1))
                #pygame.draw.line(self.screen, (255, 255, 255), (T[i] + 300+x[i], i), (T[i + 1] + 300+x[i+1], i + 1))
            # if turn == 0:

            for i in range(self.ps):
                if self.car_list[i].crashed == 0:
                    self.car_list[i].dist += 1
                    pygame.draw.circle(self.screen, self.car_list[i].color, (self.car_list[i].cx, self.car_list[i].cy),
                                       5)
                    # crash detection
                    self.car_list[i].left = self.car_list[i].cx - T[self.car_list[i].cy] - 250
                    self.car_list[i].right = T1[self.car_list[i].cy] + 350 - self.car_list[i].cx
            for i in range(self.ps):
                if (self.car_list[i].left <= 0 or self.car_list[i].right <= 0) and self.car_list[i].crashed == 0:
                    self.car_list[i].crashed = 1
                    print("CRASHED", i, self.car_list[i].left, self.car_list[i].right)
                    self.crash_count += 1
            if self.crash_count == self.ps:
                exitLoop=1
                break

            for i in range(self.screen_height - 1, 0, -1):
                T[i] = T[i - 1]
                t[i] = t[i - 1]
                T1[i] = T1[i - 1]
                t1[i] = t1[i - 1]
                #x[i] = x[i-1]
            if tim % 100 == 0:
                t[0] = random.choice(range(-200, 200, 20))
                t1[0] = random.choice(range(-200, 200, 20))
                self.alpha += 0.00001
                #x[0] = random.choice(range(70,100,1))

            tim += 1
            for i in range(1, self.screen_height):
                T[i] = self.alpha * t[i] + (1 - self.alpha) * T[i - 1]
                T1[i] = self.alpha * t1[i] + (1 - self.alpha) * T1[i - 1]

            pygame.display.update()
        pygame.quit()

    def send_direction(self, index, dir):
        # print(index)
        if math.ceil(dir[1][0] + 0.5) == 1:
            self.car_list[index].cx += 1
        elif math.ceil(dir[1][1] + 0.5) == 1:
            self.car_list[index].cx -= 1

    def get_distances(self, index):
        #print(index)
        return [self.car_list[index].left, self.car_list[index].right]

    def get_fitness(self, index):
        return self.car_list[index].dist
#sim=Simulation(5)
#sim.simulation()