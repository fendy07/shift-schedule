from deap import algorithms, tools

def eaSimpleWithElitism(population, toolbox, cxpb, mutpb, ngen, stats = None, hallofFame = None, verbose = __debug__):
    """Algoritma ini memiliki kesamaan dengan DEAP eaSimple() dengan melakukan modifikasi pada fungsi 'hallofFame' yang digunakan untuk implementasi mekanisme sebuah algoritma elitism"""

    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluasi tiap individu dengan invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if hallofFame is None:
        raise ValueError("Hall of Fame parameter must not be empty")
    
    hallofFame.update(population)
    hof_size = len(hallofFame.items) if hallofFame.items else 0

    record = stats.compile(population) if stats else {}
    logbook.record(gen = 0, nevals = len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)
    
    # Memulai untuk proses generate
    for gen in range(1, ngen + 1):
        # Pilih generasi lanjutan dari individu
        offspring = toolbox.select(population, len(population) - hof_size)
        # Membuat varietas dari Individu
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)
        # Evaluasi pada tiap individu dengan invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # Tambahkan best back untuk populasi
        offspring.extend(hallofFame.items)
        # Update dari hall of fame dengan generated individual
        hallofFame.update(offspring)
        # Replace dari populasi saat ini berdasarkan offspring
        population[:] = offspring

        # Gabungkan dari generasi saat ini dengan perhitungan statistik dalam logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen = gen, nevals = len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook