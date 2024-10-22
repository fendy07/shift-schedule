import json
import calendar
import random
import numpy as np
from deap import base, creator, tools
from datetime import datetime, date, timedelta

# List karyawan
#NAMES = ["Dimas", "Dinda", 
#         "Hikmah", "Riza", 
#         "Estu", "Antika", 
#         "Retno", "Sulis", 
#         "Dzaki", "Mugny", 
#         "Sri Wahyuni", "Rini",
#         "Putri", "Putra", "Reza"]

#MUSLIM_MEN = ["Dimas", "Dzaki", "Riza", "Mugny", "Reza", "Putra"]
with open('dataset/dataset.json', 'r') as file:
    data = json.load(file)

NAMES = data['names']
MUSLIM_MEN = data['muslim_men']

DAYS_OF_WEEK = ["Senin", "Selasa", 
                "Rabu", "Kamis", 
                "Jum'at", "Sabtu", "Minggu"]

SHIFTS = {
    1: ("10:00 AM", "18:00 PM"), # Shift 1
    2: ("14:00 PM", "22:00 PM"), # Shift 2
    3: ("12:00 PM", "20:00 PM"), # Shift 3
    4: ("10:00 AM", "20:00 PM"), # Shift 4
    5: ("10:00 AM", "19:00 PM"), # Shift 5
    6: ("10:00 AM", "22:00 PM"), # FULL SHIFT
    7: ("OFF", "OFF DAY") # LIBUR
}

# Berapa minggu dalam satu tahun?
def minggu_dalam_setahun(tahun):
    start_date = date(tahun, 1, 1)
    end_date = date(tahun, 12, 31)
    weeks = 0
    while start_date <= end_date:
        weeks += 1
        start_date += timedelta(days=7)
    return weeks

WEEKS_IN_YEAR = minggu_dalam_setahun(date.today().year)

# Tahun yang akan berubah secara otomatis
TAHUN_SEKARANG = datetime.now().year
# Jumlah hari dan shift (misal 7 hari, 7 shift per hari termasuk libur)
NUM_DAYS = 366 if calendar.isleap(TAHUN_SEKARANG) else 365
NUM_SHIFTS = len(SHIFTS)
NUM_EMPLOYEES = len(NAMES)

# Inisialisasi bobot fitness dengan nilai minimum atau maksimum
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

## Fungsi untuk inisialisasi individu (kromosom)
def create_individual():
    assigned_shifts = []
    for day in range(1, NUM_DAYS + 1):
        shift = random.randint(1, NUM_SHIFTS)
        while shift in assigned_shifts:
            shift = random.randint(1, NUM_SHIFTS)
        assigned_shifts.append(shift)
    return assigned_shifts
    #return [[random.randint(1, NUM_SHIFTS) for _ in range(NUM_DAYS)] for _ in range(NUM_EMPLOYEES)]

toolbox = base.Toolbox()
#toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
#toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Fungsi aturan dalam shift pekerja 
def is_valid(individual):
    """
    Fungsi ini memeriksa apakah jadwal valid dengan aturan-aturan yang telah ditentukan.
    :param individual: Daftar mingguan, dimana setiap minggunya adalah daftar bilangan bulat yang mewakili pekerja atau karyawan.
    :return: True jika jadwal valid, False jika tidak.

    Aturan shift: 
    1. Tidak seorang pun yang dapat mengambil cuti atau pergi selama akhir pekan, libur hanya di weekday saja
    2. Sebelum mengambil cuti, karyawan biasanya akan diberikan shift 1 atau 4; setelah cuti, mereka akan diberikan shift 2
    3. Laki-laki yang beragama Islam tidak diperkenankan mengambil shift 1, 4 dan 3 setiap hari Jum'at dikarenakan ada ibadah shalat Jum'at
    4. Jika toko sedang ramai, khususnya weekend (Jum'at sampai Minggu), perusahaan tetapkan karyawan di shift 4
    5. Tidak mungkin hanya satu orang yang menutup toko, harus ada 1 orang lagi yang membantu untuk menutup toko 
    6. Jika karyawan memiliki shift malam, sebisa mungkin hindari bekerja shift pagi pada hari berikutnya
    """
    if not individual:
        return False

    for i, week in enumerate(individual[:-1]):
        # Ensure week has 7 elements
        while len(week) < 7:
            week.append(-1)  # Append a default value for off day if missing
        # Unpack the week into shifts and off day
        shift1, shift2, shift3, shift4, shift5, shift6, off = week

        # Aturan 1: Tidak diperkenankan mengambil libur atau cuti di akhir pekan (weekend) hanya boleh di weekday saja
        if off in [7, -1] and (i == 5 or i == 6): # i == 5 adalah hari Sabtu, 1 == 6 adalah hari Minggu
            return False

        # Aturan 2: Sebelum mengambil cuti atau libur karyawan akan diberikan shift 1 atau 4, dan setelah cuti/libur diberikan shift 2
        if off in [7, -1] and i > 0:
            hari_sebelumnya = individual[i - 1][-1] # Hari sebelum libur/cuti
            if hari_sebelumnya not in [1, 4]:
                return False

        if off in [7, -1] and i < len(individual) -1:
            hari_berikutnya = individual[i + 1][0] # Hari setelah libur/cuti
            if hari_berikutnya != 2:
                return False

        # Aturan 4: Pada weekend (Jumat, Sabtu, Minggu), pekerja harus di shift 4 (shift ramai)
        if i in [4, 5, 6] and shift4 == off: # Indeks 4, 5, 6 menunjukan hari Jum'at, Sabtu dan Minggu
            return False # Jika tidak ada pekerja di shift 4 pada hari ini, jadwal tidak valid

        # Aturan 5: Untuk menutup toko harus lebih dari 1 orang (misalnya shift 6)
        if shift6 != off and shift6 == shift1:
            return False 

        # Aturam 6: Apabila karyawan sudah mendapatkan shift malam maka tidak diperbolehkan ambil shift pagi di hari berikutnya
        if shift1 == shift2 or shift1 == shift3 or shift1 == shift4 or shift1 == shift5 or shift1 == shift6 or off == -1:
            return True
        
        if individual[i + 1][1] != shift2:
            return False
        
        if shift6 == shift1 or shift6 == shift3 or shift6 == shift2 or shift6 == shift4 or shift6 == shift5:
            return False
        
        if shift6 or shift2 in individual[i + 1]:
            return False
        
        if shift1 == shift2 or shift3 == shift4 or shift5 == shift6 or shift2 == shift1:
            return False
    # Aturan 3: Teruntuk karyawan laki-laki yang beragama Islam, tidak disarankan mengambil shift 1, 3 dan 4 pada hari Jum'at
    for i, week in enumerate(individual):
        if i == 4:
            if any(SHIFTS in [1, 3, 4] for SHIFTS in [shift1, shift3, shift4] if SHIFTS in MUSLIM_MEN):
            #if week[0] in [shift1, shift3, shift4] and week[0] in MUSLIM_MEN:
                return False
            
    
    return True


def backtrack(individual):
    """
    Fungsi ini melakukan backtrack pada individu yang tidak valid.
    :param individual: Daftar mingguan, dimana setiap minggunya adalah daftar bilangan bulat yang mewakili pekerja atau karyawan.
    :return: A new individual with the invalid parts modified.
    """
    if len(individual) == WEEKS_IN_YEAR:
        return True
    
    workers = list(range(len(NAMES)))
    random.shuffle(workers)

    for shift1 in workers:
        for shift2 in workers:
            for shift3 in workers:
                for shift4 in workers:
                    for shift5 in workers:
                        for shift6 in workers:
                            for off in workers:
                                # Periksa jika tiap pekerja berbeda untuk bagian shift di tiap minggunya
                                if shift1 != shift2 and shift1 != shift3 and shift2 != shift3 and shift4 != shift5 and shift6 != shift5 and shift1 != off and shift2 != off: 
                                    new_individual = individual + [[shift1, shift2, shift3, shift4, shift5, shift6, off]]
                                    # Periksa jika jadwal barunya valid 
                                    if is_valid(new_individual):
                                        # Jika jadwal barunya sudah valid maka dilanjutkan dengan minggu setelahnya
                                        if backtrack(new_individual):
                                            individual[:] = new_individual
                                            return True
                                        else:
                                            new_individual.pop()
    
    return False

def init_individual():
    """
    Fungsi ini digunakan untuk generate sebuah jadwal yang valid atau sesuai.
    Dengan menggunakan fungsi backtrack untuk generate jadwal yang valid dan jika fungsi tersebut tidak dapat di generate dalam jadwal
    yang sesuai atau valid setelah 10 kali di generate maka akan berhenti secara otomatis dan dikembalikan dalam tipe list yang kosong.
    :return: list untuk tiap minggu, dimana tiap minggunya adalah sebuah list dari karyawan atau pekerja. 
    """
    individual = []
    attempts = 0

    while not backtrack(individual):
        individual = []
        attempts += 1
        if attempts > 10:
            break
    # Ensure the individual has 7 elements: 6 shifts + 1 off day
    if len(individual) > 0 and len(individual[-1]) < 7:
        individual[-1].append(-1)  # Assuming -1 represents an off day or invalid shift

    return individual

def evaluate(individual, year=TAHUN_SEKARANG):
    """
    Fungsi evaluasi fitness ini digunakan untuk mengukur seberapa adil distribusi jadwal yang diberikan sepanjang tahun dan setiap bulan. Fungsi ini menghitung varians jumlah shift untuk setiap karyawan atau pekerja. Varians adalah ukuran seberapa menyebar angka-angka tersebut. 
    :param(individual) adalah daftar mingguan dimana setiap minggunya daftar dari 3 bilangan bulat yang mewakili pekerja 
    :param(year) dimana jadwal tersebut dioptimalkan
    :return dengan tipe data Tuple dengan satu elemen berfungsi untuk ukuran yang tidak seimbang dalam penjadwalan
    """
    def calculate_variance(counts, expected):
        return sum([(count - expected) ** 2 for count in counts.values()]) / len(NAMES) / len(MUSLIM_MEN)

    # Initialize shifts lists
    shift1, shift2, shift3, shift4, shift5, shift6, off = [], [], [], [], [], [], []

    for week in individual:
        # Ensure week has 7 elements
        while len(week) < 7:
            week.append(-1)  # Append a default value for missing shifts

        #shift1.append(week[0])
        #shift2.append(week[1])
        #shift3.append(week[2])
        #shift4.append(week[3])
        #shift5.append(week[4])
        #shift6.append(week[5])
        #off.append(week[6])

    # Separate day workers by shift type
    shift1 = [week[0] for week in individual]
    shift2 = [week[1] for week in individual]
    shift3 = [week[2] for week in individual]
    shift4 = [week[3] for week in individual]
    shift5 = [week[4] for week in individual]
    shift6 = [week[5] for week in individual]
    off = [week[6] for week in individual]

    expected_days = len(individual) / len(NAMES) / len(MUSLIM_MEN)
    year_variance = sum([
        calculate_variance({i: shift1.count(i) for i in set(shift1)}, expected_days),
        calculate_variance({i: shift2.count(i) for i in set(shift2)}, expected_days),
        calculate_variance({i: shift3.count(i) for i in set(shift3)}, expected_days),
        calculate_variance({i: shift4.count(i) for i in set(shift4)}, expected_days),
        calculate_variance({i: shift5.count(i) for i in set(shift5)}, expected_days),
        calculate_variance({i: shift6.count(i) for i in set(shift6)}, expected_days),
        calculate_variance({i: off.count(i) for i in set(off)}, expected_days)
    ])

    # Hitung varians dalam setiap bulan
    month_variances = []
    for month in range(1, 13):
        last_day = calendar.monthrange(year, month)[1]
        first_week = datetime(year, month, 1).isocalendar()[1]
        last_week = datetime(year, month, last_day).isocalendar()[1]

        month_shift1 = shift1[first_week-1:last_week]
        month_shift2 = shift2[first_week-1:last_week]
        month_shift3 = shift3[first_week-1:last_week]
        month_shift4 = shift4[first_week-1:last_week]
        month_shift5 = shift5[first_week-1:last_week]
        month_shift6 = shift6[first_week-1:last_week]
        month_off = off[first_week-1:last_week]

        weeks_in_month = last_week - first_week + 1
        expected_days_in_month = weeks_in_month / len(NAMES) / len(MUSLIM_MEN)

        month_variances.append(sum([
            calculate_variance({i: month_shift1.count(i) for i in set(month_shift1)}, expected_days_in_month),
            calculate_variance({i: month_shift2.count(i) for i in set(month_shift2)}, expected_days_in_month),
            calculate_variance({i: month_shift3.count(i) for i in set(month_shift3)}, expected_days_in_month),
            calculate_variance({i: month_shift4.count(i) for i in set(month_shift4)}, expected_days_in_month),
            calculate_variance({i: month_shift5.count(i) for i in set(month_shift5)}, expected_days_in_month),
            calculate_variance({i: month_shift6.count(i) for i in set(month_shift6)}, expected_days_in_month),
            calculate_variance({i: month_off.count(i) for i in set(month_off)}, expected_days_in_month)
        ]))

    # Hitung total variance berdasarkan tahun dan bulan
    total_variance = 2 * year_variance + sum(month_variances)

    return total_variance,

def mutate_individual(ind, year=TAHUN_SEKARANG):
    """
    Fungsi ini digunakan untuk mengubah jadwal. Mutasi adalah operator evolusi yang memperkenalkan keragaman dalam populasi. Fungsinya sebagai memilih bagian minggu secara acak dan mengubah pekerja untuk minggu tersebut. Apabila jadwalnya tidak valid maka fungsi ini akan mencoba hingga 10 kali.
    :param(ind) adalah daftar mingguan dimana setiap minggunya adalah list dari bilangan bulat yang mewakili pekerja
    :param(year) adalah tahun yang dimana jadwal dioptimasi
    :return dengan tipe data Tuple satu elemen adalah jadwal yang diubah.
    """
    # Random select a week to mutate
    day_to_mutate = random.randint(0, len(ind) - 1) 
    attempts = 0 
    mutated = False
    while not mutated:
        # Correctly combine the two lists
        new_day_schedule = random.sample(range(len(NAMES) + len(MUSLIM_MEN)), 5)  # Use + to combine lengths
        ind[day_to_mutate] = new_day_schedule  # Use assignment instead of indexing with brackets
        # Cek jika jadwal baru telah sesuai atau valid
        if is_valid(ind):
            mutated = True
        attempts += 1
        # Limit the attempts to avoid infinite loops
        if attempts > 10:
            break

    return ind,

def setup_toolbox():
    """
    Fungsi ini digunakan untuk DEAP toolbox.
    Bagian fungsi ini untuk membuat individu dan populasi, dan untuk operator evolusi algoritma genetika
    """
    global toolbox
    toolbox = base.Toolbox()

    toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_individual)
    toolbox.register("select", tools.selTournament, tournsize=5)
    toolbox.register("evaluate", evaluate)

def convert_to_names(individual, NAMES):
    """
    Fungsi ini mengubah jadwal dari daftar indeks menjadi daftar nama.
    :param(individual) -> daftar minggu, dimana setiap minggu adalah daftar bilangan bulat yang mewakili pekerja
    :return: daftar mingguan
    """
    named_schedule = []
    for week in individual:
        named_week = []
        for shift in week:
            # Check if shift is a valid index
            if shift >= 0 and shift < len(NAMES):  
                named_week.append(NAMES[shift])
            #else:
            #    named_week.append(NAMES)
        named_schedule.append(named_week)
    return named_schedule

def optimized_schedule(names=NAMES, year=TAHUN_SEKARANG, generations=200, population_size=100):
    """
    Fungsi ini digunakan untuk mengoptimalkan jadwal shift dengan menggunakan algoritma genetika dalam penentuan jadwal terbaik. Algoritma ini mengembangkan populasi jadwal selama beberapa generasi dan tiap generasinya, memilih jadwal terbaik lalu menerapkan metode crossover atau persilangan dan mutasi, dan membuat populasi sampel baru. 
    :param(names) -> daftar nama pekerja
    :param(year) -> tahun saat jadwal dioptimalkan
    :param(generations) -> jumlah generasi populasi
    :param(population_size) -> ukuran dari populasi
    :return: daftar mingguan, dimana setiap minggunya adalah daftar dari 3 nama yang mewakili pekerja.
    """
    global NAMES
    global MUSLIM_MEN

    NAMES = names
    setup_toolbox()
    # CXPB -> CrossOver Probabilty dengan nilai minimal 70%
    # MUTPB -> Mutation Probability dengan nilai 20%
    pop = toolbox.population(n=population_size)
    CXPB, MUTPB, NGEN = 0.7, 0.2, generations

    # Setting up the statistics to gather during evolution
    stats = tools.Statistics(lambda ind:ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbook = tools.Logbook()  # This will store the stats for each generation
    logbook.header = ["gen", "nevals"] + stats.fields

    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit 

    for gen in range(NGEN):
        print(f"-- Generation {gen} --")
        # Pilih untuk generasi selanjutnya dari individu
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                if len(child1) > 1 and len(child2) > 1:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
        
        # Mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Periksa dan koreksi pada jadwal yang invalid 
        for child in offspring:
            if not is_valid(child):
                child[:] = init_individual()
        
        # Evaluasi jadwal setelah metode crossover dan mutasi
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update dari metode populasi
        pop[:] = offspring

        # Mengumpulkan secara keseluruhan dari perhitungan statistik tiap fitness untuk generasi 
        record = stats.compile(pop)
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        print(logbook.stream)
    
    best_ind = tools.selBest(pop, 1)[0]
    # Pass NAMES as an argument
    best_named_ind = convert_to_names(best_ind, NAMES)
    print(best_named_ind)  

    return best_named_ind