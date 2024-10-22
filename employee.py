import numpy as np

class Employee:
    SHIFTS = {
        1: ("10:00 AM", "18:00 PM"), # Shift 1
        2: ("14:00 PM", "22:00 PM"), # Shift 2
        3: ("12:00 PM", "20:00 PM"), # Shift 3
        4: ("10:00 AM", "20:00 PM"), # Shift 4
        5: ("10:00 AM", "19:00 PM"), # Shift 5
        6: ("10:00 AM", "22:00 PM"), # FULL SHIFT
        7: ("OFF", "OFF DAY") # LIBUR
    }

    def __init__(self, hardConstraintPenalty):
        self.hardConstraintPenalty = hardConstraintPenalty
        # List employee
        self.employee = ["Dimas", "Dinda", "Hikmah", 
                         "Riza", "Estu", "Antika", 
                         "Retno", "Sulis", "Dzaki", 
                         "Mugny", "Sri Wahyuni", "Rini", 
                         "Putri", "Putra", "Reza"]
        
        # perspective shift in - 6 shifts
        self.shiftPreference = [
            [1, 0, 1, 1, 1, 1, 1], 
            [1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 0, 1],
            [1, 1, 0, 1, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1],
            [1, 0, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1],
            [1, 1, 0, 1, 1, 1, 1]
        ]

        # min and max number of employee allowed for each shift:
        self.shiftMin = [2, 2, 2, 1, 1, 1]
        self.shiftMax = [3, 4, 2, 5, 6, 3]

        # max shifts per week allowed for each employee
        self.maxShiftsPerWeek = 6

        # number of weeks we create a schedule for:
        self.weeks = 1

        # useful values:
        self.shiftPerDay = len(self.shiftMin)
        self.shiftsPerWeek = 7 * self.shiftPerDay

    def __len__(self):
        return len(self.employee) * self.shiftsPerWeek * self.weeks
    
    def getCost(self, schedule):
        if len(schedule) != self.__len__():
            raise ValueError("Size of schedule lish should to be equal to", self.__len__())
        
        employeeShiftDict= self.getEmployeeShift(schedule)

        # Count the various violations
        consecutiveShiftViolations = self.countConsecutiveShiftViolations(employeeShiftDict)
        shiftsPerWeekViolations = self.countShiftsPerWeekViolations(employeeShiftDict)[1]
        
