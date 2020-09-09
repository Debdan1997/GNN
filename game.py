import queue
import pygame
import numpy as np
import random
import time
import threading
import math

# global
movement = 5
generations = 100
population_size = 20
mutation_rate = 0.1
max_child_time = 20

hnodes = 20
inodes = 2
onodes = 2

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (255, 0, 255)
cx = np.zeros((population_size, 1)) + 335
cy = 400
dist = np.zeros((population_size))
left = np.zeros((population_size, 1)) + 335 - 300
right = np.zeros((population_size, 1)) + 370 - 335
screenWidth = 640
screenHeight = 480
turn = 0


# initialise
def printLR():
    while True:
        print(left, right);


def Simulation():
    global cx
    global left
    global right
    global turn
    global dist
    pygame.init()
    cx = np.zeros((population_size, 1)) + 335
    cy = 400
    dist = np.zeros((population_size))
    left = np.zeros((population_size, 1)) + 335 - 300
    right = np.zeros((population_size, 1)) + 370 - 335
    alpha = .002
    jump = 1
    crash_count = 0
    # jList = [2, 4, 6, 8, 10]
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption('Road Simulation')
    T = np.zeros((screenHeight, 1), float)
    t = np.random.randint(-50, 50, (screenHeight, 1))
    for i in range(1, screenHeight):
        T[i] = alpha * t[i] + (1 - alpha) * T[i - 1]

    t1 = time.time()
    # mainloop
    exitLoop = False
    tim = 10
    t[0] = random.choice(range(-50, 50, 20))
    while (not exitLoop):
        screen.fill(black)

        for i in range(0, screenHeight - jump, jump):
            pygame.draw.line(screen, white, (T[i] + 300, i), (T[i + jump] + 300, i + jump))
            pygame.draw.line(screen, white, (T[i] + 370, i), (T[i + jump] + 370, i + jump))
        # if turn == 0:

        for i in range(population_size):
            if cx[i] != -1:
                dist[i] += 1
                pygame.draw.circle(screen, yellow, (cx[i], cy), 5)
                # crash detection
                left[i] = cx[i] - T[cy] - 300
                right[i] = T[cy] + 370 - cx[i]
        for i in range(population_size):
            if (left[i] <= 0 or right[i] <= 0) and cx[i] != -1:
                cx[i] = -1
                # print("CRASHED", i, left[i], right[i])
                t2 = time.time()
                # print(i, t2 - t1)
                crash_count += 1
                if crash_count == population_size:
                    exitLoop = True

        # road transformation
        for i in range(screenHeight - 1, 0, -1):
            T[i] = T[i - 1]
            t[i] = t[i - 1]
        if tim % 50 == 0:
            t[0] = random.choice(range(-200, 200, 20))
            alpha += 0.0001

        tim += 1
        for i in range(1, screenHeight):
            T[i] = alpha * t[i] + (1 - alpha) * T[i - 1]

        # event management
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exitLoop = True
        # turn=1
        # print(cx)

        pygame.display.update()
    # turn=2
    pygame.quit()


def send_direction(index, dir):
    global cx
    if math.ceil(dir[1][0] + 0.5) == 1:
        cx[index] += movement
    elif math.ceil(dir[1][1] + 0.5) == 1:
        cx[index] -= movement


# NN
def get_distances(index):
    return [left[index], right[index]]


def get_fitness(index):
    # print(dist[index])
    return dist[index]


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def forward(theta1, theta2, input_x):
    a2 = sigmoid(np.dot(theta1, input_x))
    a3 = sigmoid(np.dot(theta2, a2))

    return a2, a3


def create_new_generation(fitness):
    new_generation = queue.Queue()
    val = 0
    for i in range(1, len(fitness)):
        fitness[i][0] = fitness[i - 1][0] + fitness[i][0]
    # print("HEREEEEEE")
    # print(len(fitness))
    max_val = fitness[population_size - 1][0]
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
        child1, child2 = mid_point_crossover(parent1, parent2)

        new_generation.put(child1 + [val])
        new_generation.put(child2 + [val + 1])
        val += 2
    new_generation = mutation(new_generation, mutation_rate)

    return new_generation


def mid_point_crossover(parent1, parent2):
    # print("parent")
    # print(parent1)
    size = len(parent1)
    child1 = parent1[0:size // 2] + parent2[size // 2:size]
    child2 = parent2[0:size // 2] + parent1[size // 2:size]

    return child1, child2


def list_to_queue(list_input):
    q = queue.Queue()
    for i in list_input:
        q.put(i)
    return q


def queue_to_list(queue_input):
    l = []
    while not queue_input.empty():
        l.append(queue_input.get())
    return l


def mutation(generation, mutation_rate):
    generation_list = queue_to_list(generation)
    for child in generation_list:
        for gene_num in range(len(child) - 1):
            x = random.random()
            if x <= mutation_rate:
                child[gene_num] = np.random.normal(0.0, 1)
    return list_to_queue(generation_list)


weight_list = queue.Queue()  ### queue for round robin
child_index = 0

for child in range(population_size):
    curr_weight = np.random.normal(0.0, 1,
                                   hnodes * inodes + onodes * hnodes).tolist()  ### randomly initiated array for all children
    weight_list.put(curr_weight + [child_index])
    child_index += 1


def genetic_algorithm(weight_list):
    for generation in range(generations):
        t1 = threading.Thread(target=Simulation)
        t1.start()
        fitness_list = []

        while not weight_list.empty():  ### while queue is not empty
            time.sleep(.01)

            curr_weight = weight_list.get()  ### get current top of the queue
            child_index = curr_weight[-1]  ### get corresponding child index
            input_x = get_distances(child_index)

            if input_x[0] <= 0 or input_x[1] <= 0:  ## if this child has crashed
                fitness_list.append([get_fitness(child_index)] + curr_weight[
                                                                 0:hnodes * inodes + onodes * hnodes])  ## get the fitness and don't append to queue

            else:
                weight_list.put(curr_weight)  ## else append the queue for next round

                theta1 = np.array(curr_weight[0:hnodes * inodes]).reshape(hnodes, inodes)
                theta2 = np.array(curr_weight[hnodes * inodes:hnodes * inodes + onodes * hnodes]).reshape(onodes,
                                                                                                          hnodes)

                output = forward(theta1, theta2, input_x)
                send_direction(child_index, output)
        fitness_list.sort(reverse=True)
        print("Max fitness" + str(fitness_list[0][0]))
        # print("WER")
        # print(len(fitness_list))
        weight_list = create_new_generation(fitness_list)

        t1.join
    # t1 = threading.Thread(target=Simulation)


genetic_algorithm(weight_list)