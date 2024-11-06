import random
import elitism
import employee
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from deap import base, creator, tools

# Problem Constraints
HARD_CONSTRAINT_PENALTY = 20

# Constraint untuk Algoritma Genetika
POPULATION_SIZE = 100
CROSSOVER = 0.7
MUTATION = 0.2
MAX_GENERATIONS = 200
HALL_OF_FAME_SIZE = 30

# Atur untuk Random seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

toolbox = base.Toolbox()

# Buat sebuah problem dari shift pekerja yang digunakan 
employee = employee.EmployeeSchedulingProblem(HARD_CONSTRAINT_PENALTY)

# Define a single objective, maximizing optimize strategy:
creator.create("FitnessMin", base.Fitness, weights = (-1.0,))

# Create the individual list based on class
creator.create("Individual", list, fitness = creator.FitnessMin)

# Membuat sebuah operator secara acak dan mengembalikan nilai 0 atau 1
toolbox.register("zeroOrOne", random.randint, 0, 1)

# Membuat operator individual untuk mengisi keseluruhan di Individual Instance
toolbox.register("IndividualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, len(employee))

# Membuat operator populasi dalam generate list untuk tiap individual
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.IndividualCreator)

# Kalkulasi fitness
def getCost(individual):
    return employee.getCost(individual), # dikembalikan dalam tipe data tuple

toolbox.register("evaluate", getCost)
# Operator genetika
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb = 1.0/len(employee))

def convertToSchedule(individual):
    schedule = []
    for i, bit in enumerate(individual):
        day = i // 3
        shift = i % 3
        if bit == 1:
            schedule.append(f"Day {day + 1}, Shift {shift + 1}")
    return schedule


# Genetic Algorithm flow:
def main():
    # Membuat inisial populasi (dari generate awal)
    population = toolbox.populationCreator(n = POPULATION_SIZE)
    # Objek perhitungan metode statistik
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("avg", np.mean)
    stats.register("max", np.max)

    # define objek hall of Fame
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # Penambahan performa algoritma genetika untuk fitur HOF yang ditambahkan 
    population, logbook = elitism.eaSimpleWithElitism(population, toolbox, cxpb = CROSSOVER,
                                                      mutpb = MUTATION, ngen = MAX_GENERATIONS, 
                                                      stats = stats, hallofFame = hof, verbose = True)
    
    # Mencetak hasil solusi terbaik yang ditemukan
    best = hof.items[0]
    print("-- Best Individual = ", best)
    print("-- Best Fitness = ", best.fitness.values[0])
    print()
    print("-- Schedule = ")
    employee.printScheduleInfo(best)

    # Ekstrak kalkulasi dari metode statistik
    minFitnessValues, meanFitnessValues, maxFitnessValues = logbook.select("min", "avg", "max")

    # Convert the best individual to a readable schedule
    schedule = convertToSchedule(best)
    print("-- Converted Schedule = ")
    for entry in schedule:
        print(entry)
    
    # Plot Statistik
    sns.set_style("whitegrid")
    plt.plot(minFitnessValues, color = 'red')
    plt.plot(meanFitnessValues, color = 'green')
    plt.plot(maxFitnessValues, color = 'blue')
    plt.xlabel("Generations")
    plt.ylabel("Min/Average/Max Fitness")
    plt.title("Min, Average and Max Fitness Over Generations")
    plt.show()


if __name__ == "__main__":
    main()