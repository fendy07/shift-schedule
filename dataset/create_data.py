import pandas as pd
import numpy as np
from datetime import datetime
import calendar


# Define the shifts
SHIFTS = {
    1: ("10:00 AM", "18:00 PM"), # Shift 1
    2: ("14:00 PM", "22:00 PM"), # Shift 2
    3: ("12:00 PM", "20:00 PM"), # Shift 3
    4: ("10:00 AM", "20:00 PM"), # Shift 4
    5: ("10:00 AM", "19:00 PM"), # Shift 5
    6: ("10:00 AM", "22:00 PM"), # FULL SHIFT
    7: ("OFF", "OFF DAY") # LIBUR
}

# Define the employees
EMPLOYEES = [
    {"name": "Dimas", "gender": "Laki-laki", "religion": "Islam"},
    {"name": "Dinda", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Riza", "gender": "Laki-Laki", "religion": "Islam"},
    {"name": "Estu", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Hikmah", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Retno", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Antika", "gender": "Perempuan", "religion": "Kristen"},
    {"name": "Sulis", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Dzaki", "gender": "Laki-laki", "religion": "Islam"},
    {"name": "Mugny", "gender": "Laki-laki", "religion": "Islam"},
    {"name": "Rini", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Putri", "gender": "Perempuan", "religion": "Islam"},
    {"name": "Sri Wahyuni", "gender": "Perempuan", "religion": "Islam"} 
]

# Define of Year and Month
YEAR = datetime.now().year
MONTH = datetime.now().month

# Total days 
TOTAL_DAYS_IN_MONTH = calendar.monthrange(YEAR, MONTH)[1]

# Define the days of the week
DAYS_OF_WEEK = ["Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Minggu"]

# Create a list to store the dataset
dataset = []

# Generate the dataset
for employee in EMPLOYEES:
    for day in range(1, TOTAL_DAYS_IN_MONTH + 1):
        # Get the day of the week
        day_of_week = DAYS_OF_WEEK[calendar.weekday(YEAR, MONTH, day) % 7]
        # Randomly select a shift for the employee on this day
        shift_id = np.random.choice(list(SHIFTS.keys()))
        dataset.append((employee['name'], day, day_of_week, employee['gender'], employee['religion'],shift_id))

# Convert the list to a Pandas DataFrame
df = pd.DataFrame(dataset, columns=["Employee_Name", "Day_of_the_Month", "Day_of_the_Week", "Gender", "Religion", "Shift_ID"])

# Print the dataset
print(df)

# Save and convert to csv
df.to_csv('employee_shift_August.csv', index=False)

# Save and convert to json
df.to_json('employee_shift_August.json', orient='records')