import numpy as np

class EmployeeSchedulingProblem:
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
        self.shiftPreference =[[1, 0, 1, 1, 1, 1, 1], 
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
        [1, 1, 0, 1, 1, 1, 1]]

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
        
        employeeShiftDict= self.getEmployeeShifts(schedule)

        # Count the various violations
        consecutiveShiftViolations = self.countConsecutiveShiftViolations(employeeShiftDict)
        shiftsPerWeekViolations = self.countShiftsPerWeekViolations(employeeShiftDict)[1]
        employeesPerShiftViolations =  self.countEmployeesPerShiftViolations(employeeShiftDict)[1]
        shiftPreferenceViolations = self.countShiftPreferenceViolations(employeeShiftDict)

        # Calculate the cost of the violations
        hardConstraintViolations = consecutiveShiftViolations + employeesPerShiftViolations + shiftsPerWeekViolations
        softConstraintViolations = shiftPreferenceViolations
        
        return self.hardConstraintPenalty * hardConstraintViolations + softConstraintViolations
    

    def getEmployeeShifts(self, schedule):
        shiftPerEmployee = self.__len__() // len(self.employee)
        EmployeeShiftDict = {}
        shiftIndex = 0

        for employee in self.employee:
            EmployeeShiftDict[employee] = schedule[shiftIndex:shiftIndex + shiftPerEmployee]
            shiftIndex += shiftPerEmployee
        
        return EmployeeShiftDict
    
    def countConsecutiveShiftViolations(self, employeeShiftDict):
        violations = 0
        for employeeShifts in employeeShiftDict.values():
            for shift1, shift2 in zip(employeeShifts, employeeShifts[1:]):
                if shift1 == 1 and shift2 == 1:
                    violations += 1
        
        return violations
    
    def countShiftsPerWeekViolations(self, employeeShiftDict):
        violations = 0
        weeklyShiftsList = []
        for employeeShifts in employeeShiftDict.values():
            for i in range(0, self.weeks * self.shiftsPerWeek, self.shiftsPerWeek):
                weeklyShifts = sum(employeeShifts[i:i + self.shiftsPerWeek])
                weeklyShiftsList.append(weeklyShifts)
                if weeklyShifts > self.maxShiftsPerWeek:
                    violations += weeklyShifts - self.maxShiftsPerWeek

        return weeklyShiftsList, violations
    
    def countEmployeesPerShiftViolations(self, employeeShiftDict):
        totalShiftPerList = [sum(shift) for shift in zip(*employeeShiftDict.values())]
        violations = 0
        for shiftIndex, NumofEmployees in enumerate(totalShiftPerList):
            dailyShiftIndex = shiftIndex % self.shiftPerDay
            if (NumofEmployees > self.shiftMax[dailyShiftIndex]):
                violations += NumofEmployees - self.shiftMax[dailyShiftIndex]
            elif (NumofEmployees < self.shiftMin[dailyShiftIndex]):
                violations += self.shiftMin[dailyShiftIndex] - NumofEmployees
        
        return totalShiftPerList, violations
    
    def countShiftPreferenceViolations(self, employeeShiftDict):
        violations  = 0
        for shiftIndex, shiftPreference in enumerate(self.shiftPreference):
            preference = shiftPreference * (self.shiftsPerWeek // self.shiftPerDay)
            shifts = employeeShiftDict[self.employee[shiftIndex]]
            for pref, shift in zip(preference, shifts):
                if pref == 0 and shift == 1:
                    violations += 1
        
        return violations
    
    def printScheduleInfo(self, schedule):
        employeeShiftDict = self.getEmployeeShifts(schedule)

        print("Schedule for each Employee:")
        for employee in employeeShiftDict:
            print(employee, ":", employeeShiftDict[employee])

        print('Consecutive Shift Violations = ', self.countConsecutiveShiftViolations(employeeShiftDict))
        print()

        weeklyShiftList, violations = self.countShiftsPerWeekViolations(employeeShiftDict)
        print("Weekly Shifts = ", weeklyShiftList)
        print("Shift Per Week Violations = ", violations)
        print()

        totalPerShiftList, violations = self.countEmployeesPerShiftViolations(employeeShiftDict)
        print("Employee Per Shift = ", totalPerShiftList)
        print("Employees Per Shift Violations = ", violations)
        print()

        shiftPreferenceViolations = self.countShiftPreferenceViolations(employeeShiftDict)
        print("Shift Preference Violations = ", shiftPreferenceViolations)
        print()


# Testing for the class 
def main():
    # Membuat sebuah problem instance
    employee = EmployeeSchedulingProblem(20)


    randomSolution = np.random.randint(3, size = len(employee))
    print("Random Solution = ")
    print(randomSolution)
    print()
    
    employee.printScheduleInfo(randomSolution)


    print("Total Cost = ", employee.getCost(randomSolution))


if __name__ == "__main__":
    main()
