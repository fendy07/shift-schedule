import random
import calendar
import pandas as pd
from datetime import datetime as dt
from datetime import date, datetime, timedelta
from deap import base, creator, tools, algorithms

# Load dataset
file_path = 'dataset/employee_shift_August.csv'
data = pd.read_csv(file_path)

# Print the column names to debug
print("Columns in the dataset:", data.columns)

# Strip whitespace from column names
data.columns = data.columns.str.strip()

# Extracting names and shifts from the DataFrame
NAMES = data['Employee_Name'].tolist()  # Replace 'Employee Name' with the actual column name
MUSLIM_MEN = data[data['Religion'] == 'Islam']['Employee_Name'].tolist()  # Replace 'Religion' with the actual column name

# Shift identifiers dengan waktu spesifik
SHIFTS = {
    1: ("10:00 AM", "18:00 PM"), # Shift 1
    2: ("14:00 PM", "22:00 PM"), # Shift 2
    3: ("12:00 PM", "20:00 PM"), # Shift 3
    4: ("10:00 AM", "20:00 PM"), # Shift 4
    5: ("10:00 AM", "19:00 PM"), # Shift 5
    6: ("10:00 AM", "22:00 PM"), # Full Shift
    7: ("OFF", "OFF DAY") # Libur
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
BULAN = datetime.now().month

# Jumlah hari dan shift (misal 7 hari, 7 shift per hari termasuk libur)
#NUM_DAYS = 366 if calendar.isleap(TAHUN_SEKARANG) else 365
NUM_DAYS = calendar.monthrange(TAHUN_SEKARANG, BULAN)[1]
NUM_SHIFTS = len(SHIFTS)
NUM_EMPLOYEES = len(NAMES)  # Jumlah karyawan disesuaikan dengan panjang NAMES

# Membuat kelas Fitness
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Fungsi untuk inisialisasi individu (kromosom)
def create_individual():
    return [[random.randint(1, NUM_SHIFTS) for _ in range(NUM_DAYS)] for _ in range(NUM_EMPLOYEES)]

# Membuat toolbox
toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Fungsi backtrack
def backtrack(individual):
    if len(individual) == NUM_DAYS:
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
                                if shift1 != shift2 and shift1 != shift3 and shift2 != shift3 and shift4 != shift5 and shift6 != shift5: 
                                    new_individual = individual + [[shift1, shift2, shift3, shift4, shift5, shift6, off]]
                                    if is_valid(new_individual):
                                        if backtrack(new_individual):
                                            individual[:] = new_individual
                                        return True
                                    else:
                                        new_individual.pop()
    
    return True

# Fungsi inisialisasi individu
def init_individual():
    individual = []
    attempts = 0

    while not backtrack(individual):
        individual = []
        attempts += 1
        if attempts > 10:
            break
    
    return individual

# Fungsi evaluasi
def is_valid(individual):
    for i, week in enumerate(individual[:-1]):
        # Ensure week has 7 elements
        while len(week) < 7:
            week.append(-1)  # Append a default value for off day if missing

        # Unpack the week into shifts and off day
        shift1, shift2, shift3, shift4, shift5, shift6, off = week
        
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

    for i, week in enumerate(individual):
        if i == 4:
            if week[0] in [shift1, shift3, shift4] and week[0] in MUSLIM_MEN:
                return False
    return True

# Fungsi mutasi khusus untuk struktur individu (jadwal shift)
def mutShift(individual, indpb=0.05):
    for emp_schedule in individual:
        # Untuk setiap karyawan, iterasi setiap hari
        for i in range(len(emp_schedule)):
            if random.random() < indpb:
                # Ganti shift di hari tersebut dengan shift acak
                emp_schedule[i] = random.randint(1, NUM_SHIFTS)
    return individual,

# Fungsi fitness
def eval_shift_schedule(individual):
    fitness = 0

    for emp_idx, schedule in enumerate(individual):
        name = NAMES[emp_idx]  # Mengakses nama karyawan

        # Rule dan evaluasi fitness di sini (sama seperti sebelumnya)
        # Rule 1: Tidak ada yang cuti di akhir pekan (Sabtu-Minggu)
        if schedule[-2] == 7 or schedule[-1] == 7:  # Hari ke-6 dan ke-7 (Sabtu-Minggu)
            fitness -= 10

        # Rule 2: Cuti di weekday, shift 1 sebelum cuti, shift 2 setelah cuti
        for i in range(NUM_DAYS):
            if schedule[i] == 7 and i > 0:
                if schedule[i-1] != 1:
                    fitness -= 5
                if i < NUM_DAYS-1 and schedule[i+1] != 2:
                    fitness -= 5

        # Rule 3: Laki-laki Muslim tidak disarankan bekerja shift 1, 3, 4 di hari Jumat
        if name in MUSLIM_MEN and schedule[4] in [1, 3, 4]:  # Hari Jumat (hari ke-5)
            fitness -= 10

        # Rule 4: Karyawan harus di shift 4 atau 6 saat weekend (toko ramai)
        if schedule[-3] not in [4, 6] or schedule[-2] not in [4, 6] or schedule[-1] not in [4, 6]:
            fitness -= 10

        # Rule 5: Ada lebih dari 1 karyawan untuk shift malam (tutup toko)
        if schedule[-1] == 6:  # Full Shift terakhir
            fitness -= 5

        # Rule 6: Hindari shift pagi setelah shift malam
        for i in range(1, NUM_DAYS):
            if schedule[i] in [1, 2] and schedule[i-1] == 6:
                fitness -= 5

    return fitness,

# Mendaftarkan fungsi ke toolbox
toolbox.register("individual", init_individual)
toolbox.register("evaluate", eval_shift_schedule)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutShift)
toolbox.register("select", tools.selTournament, tournsize=3)

# Membuat populasi
# Fungsi utama
def main():
    random.seed(64)
    population = toolbox.population(n=50)  # Populasi awal

    # Algoritma genetika
    algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.3, ngen=200, verbose=True)

    # Mengambil individu terbaik
    best_individual = tools.selBest(population, k=1)[0]
    
    # Menampilkan jadwal terbaik
    #month = 8  # August
    #year = datetime.now().year
    num_days = calendar.monthrange(TAHUN_SEKARANG, BULAN)[1]
    days_of_week = ["Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Minggu"]
    for emp_idx, schedule in enumerate(best_individual):
        name = NAMES[emp_idx]
        print(f"{name}'s schedule:")
        for day, shift in enumerate(schedule):
            day_of_week = days_of_week[calendar.weekday(TAHUN_SEKARANG, BULAN, day + 1) % 7]
            print(f"  {day_of_week} {day + 1} {calendar.month_name[BULAN]} {TAHUN_SEKARANG}: Shift {shift}, Time: {SHIFTS[shift]}")
        print()
    
    # Menyimpan jadwal terbaik ke dalam file TXT
    with open("jadwal_shift.txt", "w") as file:
        tanggal = dt.now().strftime("%d-%m-%Y")
        file.write(f"Jadwal Shift {tanggal}\n\n")
        for emp_idx, schedule in enumerate(best_individual):
            name = NAMES[emp_idx]
            file.write(f"{name}'s schedule:\n")
            for day, shift in enumerate(schedule):
                day_of_week = days_of_week[calendar.weekday(TAHUN_SEKARANG, BULAN, day + 1) % 7]
                file.write(f"  {day_of_week} {day + 1} {calendar.month_name[BULAN]} {TAHUN_SEKARANG}: Shift {shift}, Time: {SHIFTS[shift]}\n")
            file.write("\n")

if __name__ == "__main__":
    main()