import queue
import pygame
import numpy as np
import random
import time
import threading
import math
import Simulation as S


class Genetic_Algo:

    def __init__(self, gen, pop):
        self.generations = gen
        self.population_size = pop
        self.hnodes = 10
        self.inodes = 2
        self.onodes = 2
        self.weight_list = queue.Queue()  ### queue for round robin
        self.child_index = 0
        self.mutation_rate = 0.1
        self.max_child_time = 20

        for child in range(self.population_size):
            self.curr_weight = np.random.normal(0.0, 1,
                                                self.hnodes * self.inodes + self.onodes * self.hnodes).tolist()  ### randomly initiated array for all children
            self.weight_list.put(self.curr_weight + [self.child_index])
            self.child_index += 1
        self.genetic_algorithm(self.weight_list)

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def forward(self, theta1, theta2, input_x):
        a2 = self.sigmoid(np.dot(theta1, input_x))
        a3 = self.sigmoid(np.dot(theta2, a2))

        return a2, a3

    def create_new_generation(self, fitness):
        new_generation = queue.Queue()
        val = 0
        for i in range(len(fitness)):
            fitness[i][0] = fitness[i - 1][0] + 1

        max_val = fitness[self.population_size - 1][0]
        for _ in range(self.population_size // 2):
            x = random.randint(0, max_val)
            for i in range(len(fitness) // 2):
                x = random.randint(0, max_val)
                for i in range(len(fitness)):
                    if fitness[i][0] - x >= 0:
                        ans = i
                        break
            parent1 = fitness[ans][1:len(fitness[0])]

            x = random.randint(0, max_val)
            for i in range(len(fitness)):
                if fitness[i][0] - x >= 0:
                    ans = i
                    break
            parent2 = fitness[ans][1:len(fitness[0])]
            child1, child2 = self.mid_point_crossover(parent1, parent2)

            new_generation.put(child1 + [val])
            new_generation.put(child1 + [val + 1])
            val += 2
        new_generation = self.mutation(new_generation, self.mutation_rate)

        return new_generation

    def mid_point_crossover(self, parent1, parent2):
        size = len(parent1)
        child1 = parent1[0:size // 2] + parent2[size // 2:size]
        child2 = parent2[0:size // 2] + parent1[size // 2:size]

        return child1, child2

    def list_to_queue(self,list_input):
        q = queue.Queue()
        for i in list_input:
            q.put(i)
        return q

    def queue_to_list(self,queue_input):
        l = []
        while not queue_input.empty():
            l.append(queue_input.get())
        return l

    def mutation(self,generation, mutation_rate):
        generation_list = self.queue_to_list(generation)
        for child in generation_list:
            for gene_num in range(len(child) - 1):
                x = random.random()
                if x <= mutation_rate:
                    child[gene_num] = np.random.normal(0.0, 1)
        return self.list_to_queue(generation_list)

    def genetic_algorithm(self, weight_list):
        for generation in range(self.generations):
            print("GENERATIONS :",generation)
            fitness_list = []
            sim = S.Simulation(self.population_size)
            t1 = threading.Thread(target=sim.simulation)
            t1.start()
            time.sleep(.1)
            times = 0
            while (not weight_list.empty()):  ### while queue is not empty
                time.sleep(.01)
                if times==30000:
                    break
                print(times)
                curr_weight = weight_list.get()  ### get current top of the queue
                child_index = curr_weight[-1]  ### get corresponding child index
                input_x = sim.get_distances(child_index)

                if  sim.car_list[child_index].crashed==1:  ## if this child has crashed
                    fitness_list.append([sim.get_fitness(child_index)] + curr_weight[
                                                                     0:self.hnodes * self.inodes + self.onodes * self.hnodes])  ## get the fitness and don't append to queue

                    #weight_list.put(curr_weight)
                else:
                    weight_list.put(curr_weight)  ## else append the queue for next round

                    theta1 = np.array(curr_weight[0:self .hnodes * self.inodes]).reshape(self.hnodes, self.inodes)
                    theta2 = np.array(curr_weight[self.hnodes * self.inodes:self.hnodes * self.inodes + self.onodes * self.hnodes]).reshape(self.onodes,
                                                                                                              self.hnodes)

                    output = self.forward(theta1, theta2, input_x)
                    sim.send_direction(child_index, output)

                times+=1

            fitness_list.sort(reverse=True)
            print("Max fitness" + str(fitness_list[0][0]))
            t1.join
            weight_list = self.create_new_generation(fitness_list)
            print("end of gen",generation)
            del sim

           
