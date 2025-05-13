import json
import pandas as pd
import random
import copy

# Constants from constants.py
RANDOM_INSERTION_MAXIMUM_INBALANCE = 5
ELITISM_SIZE = 10
MAX_DAILY_COST = 250
TOURNAMENT_SIZE = 5
CROSSOVER_PROBABILITY = 0.9
NUMBER_OF_ITERATIONS = 100
POPULATION_SIZE = 100
MAX_PLAN_DURATION = 30

# Task class from task.py
class Task:
    '''
    Represents maintenance of one engine handled by a single team.
    '''
    def __init__(self, engine_identifier, remaining_useful_life):
        self.engine_id = engine_identifier
        self.rul = remaining_useful_life
        self.duration = 0
        self.start_time = 0
        self.end_time = 0
        self.days_late = 0
        self.cost = 0

    def __repr__(self):
        return f'({self.engine_id}, {self.rul}, {self.start_time}, {self.end_time}, {self.days_late}, {self.cost})'

# Team class from team.py
class Team:
    '''
    Represents a set of tasks planned for one team
    '''
    def __init__(self, team_type, team_name):
        self.plan = []
        self.type = team_type
        self.name = team_name
        self.duration = 0

    def __repr__(self):
        return f'{self.name}, {self.type}, {self.duration}, {self.plan} \n'
    
    def add_task(self, task_item):
        '''
        Appends a task to the end of the plan.
        '''
        self.plan.append(copy.deepcopy(task_item))
        self.sort_tasks_on_RUL()

    def add_empty_task(self):
        '''
        Adds a placeholder job if crossover duplicates engine maintenance; can be replaced by a valid task later.
        '''
        dummy_task = Task(-1, -1)
        self.add_task(dummy_task)

    def sort_tasks_on_RUL(self):
        '''
        Sorts tasks in the plan by increasing RUL, as it's optimal for this puzzle.
        ''' 
        self.plan = sorted(self.plan, key=lambda task_obj: task_obj.rul, reverse=False)

# Solution class from solution.py
class Solution:
    '''
    Solves the problem using four teams, each with a task plan; teams 1 & 3 are type A, teams 2 & 4 are type B
    '''
    def __init__(self):
        self.teams = []
        self.add_team(Team('A', 'Team1'))
        self.add_team(Team('B', 'Team2'))
        self.add_team(Team('A', 'Team3'))
        self.add_team(Team('B', 'Team4'))
        self.total_cost = 0
        self.min_duration = 0
        self.max_duration = 0

    def __repr__(self):
        return f'{self.teams}, {self.total_cost}'
    
    def add_team(self, team_obj):
        self.teams.append(team_obj)

    def add_task_to_random_team(self, task_obj):
        '''
        Assigns a task to a random team while balancing workloads; avoids teams having much longer total durations than others.
        '''
        team_found = False
        while not team_found:
            best_team_idx = random.randint(0, len(self.teams) - 1)
            if self.teams[best_team_idx].duration <= self.min_duration + RANDOM_INSERTION_MAXIMUM_INBALANCE:
                team_found = True
                self.teams[best_team_idx].add_task(task_obj)
    
    def add_task(self, task_obj, team_index):
        '''
        Assigns a task to a specific team.
        '''
        if self.task_planned(task_obj):
            self.teams[team_index].add_empty_task()
        else:
            self.teams[team_index].add_task(task_obj)
        self.calculate_cost(task_obj)
    
    def task_planned(self, task_obj):
        '''
        Checks if any team has already scheduled the task to prevent duplicates.
        '''
        for team_obj in self.teams:
            for planned_task_obj in team_obj.plan:
                if planned_task_obj.engine_id == task_obj.engine_id:
                    return True
        return False

    def calculate_cost(self, task_obj):
        task_obj.cost = 0
        if task_obj.days_late <= 0:
            return 0
        for day_num in range(1, task_obj.days_late + 1):
            cost_factor = 0
            if 1 <= task_obj.engine_id <= 25:
                cost_factor = 4
            elif 26 <= task_obj.engine_id <= 45:
                cost_factor = 2
            elif 46 <= task_obj.engine_id <= 75:
                cost_factor = 5
            else:  # 76-100
                cost_factor = 6
            daily_cost = cost_factor * (day_num ** 2)
            task_obj.cost += min(daily_cost, MAX_DAILY_COST)
        return task_obj.cost

    def calculate_total_cost(self):
        '''
        Calculates the solution's total cost by summing task costs; also computes each team's duration, and the overall min/max durations. Tasks are sorted by increasing RUL first.
        '''
        self.sort_tasks_on_RUL()
        self.total_cost = 0
        for team_obj in self.teams:
            start_day = 1
            for task_obj in team_obj.plan:
                task_obj.cost = 0
                task_obj.duration = self.calculate_duration(team_obj.type, task_obj.engine_id)
                task_obj.start_time = start_day
                start_day += task_obj.duration
                task_obj.end_time = start_day - 1
                task_obj.days_late = max(task_obj.end_time - task_obj.rul, 0)
                task_obj.cost = self.calculate_cost(task_obj)
                self.total_cost += task_obj.cost     
            team_obj.duration = start_day - 1
        self.min_duration = float('inf')
        self.max_duration = 0
        for team_obj in self.teams:
            if team_obj.duration < self.min_duration:
                self.min_duration = team_obj.duration
            if team_obj.duration > self.max_duration:
                self.max_duration = team_obj.duration
        return self.total_cost

    def calculate_duration(self, team_type, engine_identifier):
        maintenance_time_a = 0
        if 1 <= engine_identifier <= 20:
            maintenance_time_a = 5
        elif 21 <= engine_identifier <= 55:
            maintenance_time_a = 3
        elif 56 <= engine_identifier <= 80:
            maintenance_time_a = 4
        else:  # 81-100
            maintenance_time_a = 5
        if team_type == 'A':
            return maintenance_time_a
        elif team_type == 'B':
            if 1 <= engine_identifier <= 25:
                return maintenance_time_a - 1
            elif 26 <= engine_identifier <= 70:
                return maintenance_time_a + 3
            else:  # 71-100
                return maintenance_time_a + 2

    def fix_solution(self, unplanned_tasks_list):
        '''
        Improves the solution by adding unplanned tasks to team schedules in three steps: filling gaps, assigning remaining tasks while balancing workloads, and removing any empty tasks.
        '''
        for team_obj in self.teams:
            for task_obj in team_obj.plan:
                if task_obj.engine_id < 0:
                    if len(unplanned_tasks_list) > 0:
                        unplanned_task_obj = unplanned_tasks_list.pop()
                        task_obj.engine_id = unplanned_task_obj.engine_id
                        task_obj.rul = unplanned_task_obj.rul
        for unplanned_task_obj in unplanned_tasks_list:
            self.add_task_to_random_team(unplanned_task_obj)
        for team_obj in self.teams:
            new_plan = [task_obj for task_obj in team_obj.plan if task_obj.engine_id >= 0]
            team_obj.plan = new_plan
                
    def sort_tasks_on_RUL(self):
        '''
        Sorts all teams tasks in the RUL plan by increasing RUL, as it is the optimal strategy for this puzzle.
        '''
        for team_obj in self.teams:
            team_obj.sort_tasks_on_RUL()

# Population class from population.py
class Population:
    '''
    This class optimizes team planning using a Genetic Algorithm, with a population of solutions. The size parameter sets the population size, all_tasks contains tasks to be planned, and best_score tracks the best score.
    '''
    def __init__(self, population_size, task_list):
        self.solutions = []
        self.size = population_size
        self.all_tasks = task_list
        self.best_score = 0
        self.all_tasks.sort(key=lambda task_obj: task_obj.rul, reverse=False)

    def __repr__(self):
        return f'{self.solutions}'
    
    def initialize(self):
        ''' 
        Randomly assigns tasks to teams while balancing workloads to create the initial population of solutions
        '''
        for solution_idx in range(self.size):
            solution_obj = Solution()
            for task_obj in self.all_tasks:
                solution_obj.add_task_to_random_team(copy.deepcopy(task_obj))
            self.solutions.append(solution_obj)

    def print_population(self):
        for solution_obj in self.solutions:
            print(solution_obj)
            print('')
    
    def print_population_statistics(self):
        '''
        Prints the best, worst, and average scores of the population during a run to monitor the algorithm's progress and convergence.
        '''
        best_score = float('inf')
        worst_score = 0
        total_score = 0
        for solution_obj in self.solutions:
            total_score += solution_obj.total_cost
            if solution_obj.total_cost < best_score:
                best_score = solution_obj.total_cost
            if solution_obj.total_cost > worst_score:
                worst_score = solution_obj.total_cost
        print(f'Best score: {best_score} Worst score: {worst_score} Average score: {total_score / self.size}')

    def create_children_with_crossover(self, parent_1, parent_2):
        '''
        Generates two child solutions through crossover between two parent solutions.
        '''
        selected_team_1_idx = random.randint(0, 3)
        selected_team_2_idx = random.randint(0, 3)
        if len(parent_1.teams[selected_team_1_idx].plan) < 2 or len(parent_2.teams[selected_team_2_idx].plan) < 2:
            return parent_1, parent_2
        crossover_point = random.randint(0, min(len(parent_1.teams[selected_team_1_idx].plan), len(parent_2.teams[selected_team_2_idx].plan)) - 2)
        crossover_point_1_idx = crossover_point
        crossover_point_2_idx = crossover_point
        if parent_1.teams[selected_team_1_idx].duration < parent_2.teams[selected_team_2_idx].duration:
            if random.random() < 0.5 and len(parent_2.teams[selected_team_2_idx].plan) > crossover_point + 2:
                crossover_point_2_idx += 1
        child_1 = Solution()
        child_2 = Solution()
        for task_idx in range(0, crossover_point_1_idx + 1):
            child_1.add_task(parent_1.teams[selected_team_1_idx].plan[task_idx], selected_team_1_idx)
        for task_idx in range(0, crossover_point_2_idx + 1):
            child_2.add_task(parent_2.teams[selected_team_2_idx].plan[task_idx], selected_team_2_idx)
        for task_idx in range(crossover_point_2_idx + 1, len(parent_2.teams[selected_team_2_idx].plan)):
            child_1.add_task(parent_2.teams[selected_team_2_idx].plan[task_idx], selected_team_1_idx)
        for task_idx in range(crossover_point_1_idx + 1, len(parent_1.teams[selected_team_1_idx].plan)):
            child_2.add_task(parent_1.teams[selected_team_1_idx].plan[task_idx], selected_team_2_idx)
        for team_idx in range(0, 4):
            if team_idx != selected_team_1_idx:
                for task_obj in parent_1.teams[team_idx].plan:
                    child_1.add_task(task_obj, team_idx)
            if team_idx != selected_team_2_idx:
                for task_obj in parent_2.teams[team_idx].plan:
                    child_2.add_task(task_obj, team_idx)
        unplaced_tasks_1 = self.find_unplanned_tasks(child_1)
        child_1.fix_solution(unplaced_tasks_1)
        unplaced_tasks_2 = self.find_unplanned_tasks(child_2)
        child_2.fix_solution(unplaced_tasks_2)
        child_1.sort_tasks_on_RUL()
        child_2.sort_tasks_on_RUL()
        child_1.calculate_total_cost()
        child_2.calculate_total_cost()
        return child_1, child_2
    
    def calculate_all_costs(self):
        '''
        Calculate the overall cost for each solution in the population.
        '''
        for solution_obj in self.solutions:
            solution_obj.calculate_total_cost()
            
    def find_unplanned_tasks(self, solution_obj):
        '''
        Identify the unplanned jobs within the solution.
        '''
        unplanned_tasks_list = []
        for task_obj in self.all_tasks:
            if not solution_obj.task_planned(task_obj):
                unplanned_tasks_list.append(task_obj)
        return unplanned_tasks_list

    def select_parents(self):
        '''
        Select two parent solutions for crossover using tournament selection.
        '''	
        randomly_sorted_solutions = self.solutions.copy()
        random.shuffle(randomly_sorted_solutions)
        tournament_candidates = randomly_sorted_solutions[:TOURNAMENT_SIZE]
        tournament_candidates.sort(key=lambda solution_obj: solution_obj.total_cost)
        return tournament_candidates[0], tournament_candidates[1]
    
    def create_children(self, amount):
        '''
        Generate a set of child solutions through crossover operations across the population.
        '''    
        number_created = 0
        new_solutions = []
        while number_created < amount:
            parent_1, parent_2 = self.select_parents()
            if random.random() > CROSSOVER_PROBABILITY:
                child_1 = copy.deepcopy(parent_1)
                child_2 = copy.deepcopy(parent_2)
            else:
                child_1, child_2 = self.create_children_with_crossover(parent_1, parent_2)
            new_solutions.append(child_1)
            new_solutions.append(child_2)
            number_created += 2
        return new_solutions

    def give_best_solutions(self, amount):
        self.solutions.sort(key=lambda solution_obj: solution_obj.total_cost)
        return copy.deepcopy(self.solutions[:amount])

    def create_next_generation(self):
        '''
        Create the next generation by applying elitism and crossover.
        '''
        new_solutions = self.give_best_solutions(ELITISM_SIZE)
        new_solutions.extend(self.create_children(POPULATION_SIZE - ELITISM_SIZE))
        self.solutions = copy.deepcopy(new_solutions)
        self.solutions.sort(key=lambda solution_obj: solution_obj.total_cost)

    def give_best_feasiible_solution(self):
        '''
        Identify the optimal solution that meets the 30-day maximum duration.
        '''
        for solution_obj in self.solutions:
            if solution_obj.max_duration <= MAX_PLAN_DURATION:
                return solution_obj
        return None

# Functions from main.py
def choose_consultancy_dataset(use_consultancy):
    '''
    Select either the anticipated RULs dataset or the consultancy dataset based on the use_consultancy flag.
    '''
    if use_consultancy == True:
        df_consultancy_predictions = pd.read_csv('RUL_consultancy_predictions_A3.csv', sep=';')
        df_consultancy_predictions = df_consultancy_predictions.sort_values(by='RUL', ascending=True)
        all_tasks_consultancy = []
        for engine_identifier in df_consultancy_predictions.id.unique():
            if df_consultancy_predictions[df_consultancy_predictions.id == engine_identifier].RUL.values[0] < MAX_PLAN_DURATION:
                task_obj = Task(engine_identifier, df_consultancy_predictions[df_consultancy_predictions.id == engine_identifier].RUL.values[0])
                all_tasks_consultancy.append(task_obj)
        return all_tasks_consultancy
    else:
        file_path = 'predicted_RUL_dict.txt'
        with open(file_path, 'r') as file:
            json_string = file.read()
        prediction_data = json.loads(json_string)
        all_tasks_prediction = []
        for engine_id_str, rul_value in prediction_data.items():
            if rul_value < MAX_PLAN_DURATION:
                task_obj = Task(int(engine_id_str), rul_value)
                all_tasks_prediction.append(task_obj)
        return all_tasks_prediction

def run_genetic_algorithm_x_times(num_runs):
    '''
    Print the average cost of the optimal solution after running the Genetic Algorithm multiple times.
    '''
    total_costs = 0
    times_score_of_30 = 0
    for run_idx in range(num_runs):
        population_obj = Population(POPULATION_SIZE, all_tasks)
        population_obj.initialize()
        population_obj.calculate_all_costs()
        population_obj.print_population_statistics()
        for gen_idx in range(NUMBER_OF_ITERATIONS):
            population_obj.create_next_generation()
            population_obj.calculate_all_costs()
            population_obj.print_population_statistics()
        best_solution = population_obj.give_best_feasiible_solution()
        total_costs += best_solution.total_cost
        if best_solution.total_cost == 30:
            times_score_of_30 += 1
    print('Average best cost:', total_costs / num_runs)
    print('Times score of 30:', times_score_of_30)
    return population_obj

def convert_best_solution_to_csv(best_solution):
    '''
    Convert the best solution into a CSV file to submit to the consultancy.
    '''
    results_df = pd.DataFrame()
    for team_obj in best_solution.teams:
        for task_obj in team_obj.plan:
            csv_data = {'Team': [team_obj.name], 'Type': [team_obj.type], 'DaysOfWork': [team_obj.duration], 'EngineID': [task_obj.engine_id], 'RUL': [task_obj.rul], 'StartDay': [task_obj.start_time], 'EndDay': [task_obj.end_time], 'DaysLate': [task_obj.days_late], 'Cost': [task_obj.cost]}
            results_df = pd.concat([results_df, pd.DataFrame(data=csv_data)], ignore_index=True)
    results_df.to_csv('BestSolution.csv', index=False, sep=';' )

if __name__ == '__main__':
    '''
    The program's primary purpose is to generate a population of solutions, run the Genetic Algorithm, and read the predicted RULs from a file.
    '''
    all_tasks = choose_consultancy_dataset(True)
    population_obj = run_genetic_algorithm_x_times(1)
    best_solution = population_obj.give_best_feasiible_solution()
    print(best_solution)
    convert_best_solution_to_csv(best_solution)