from solution import Solution
from task import Task
import random
import copy
import constants

class Population:
    '''
        This class represents a population of solutions and the main Genetic Algorithm loop, optimizing the planning of the teams.
        The multiple solutions are stored in the solutions list.
        The size of the population is determined by the size parameter.
        The all_tasks parameter is a list of tasks that need to be planned.
        The best_score parameter is used to keep track of the best score of the population.
    '''
    def __init__(self, size, all_tasks):
        self.solutions = []
        self.size = size
        self.all_tasks = all_tasks
        self.best_score = 0
        # Sort the tasks on RUL, because in this problem it is logical to plan the tasks with the lowest RUL first.
        self.all_tasks.sort(key=lambda x: x.rul, reverse=False)

    def __repr__(self):
        return f'{self.solutions}'
    
    def initialize(self):
        ''' 
            Create the initial population of solutions, by adding tasks to random teams, while keeping the workload balanced.
        '''
        for i in range(self.size):
            solution = Solution()
            for task in self.all_tasks:
                solution.add_task_to_random_team(copy.deepcopy(task))
            self.solutions.append(solution)
    
    def print_population_statistics(self):
        '''
            Print the best, worst and average score of the population, to see how the algorithm is performing / converging during a run.
        '''
        best_score = float('inf')
        worst_score = 0
        total_score = 0

        for solution in self.solutions:
            total_score += solution.total_cost
            if solution.total_cost < best_score:
                best_score = solution.total_cost
            if solution.total_cost > worst_score:
                worst_score = solution.total_cost

        print(f'Best score: {best_score} Worst score: {worst_score} Average score: {total_score / self.size}')

    def print_population(self):
        for solution in self.solutions:
            print(solution)
            print('')

    def calculate_all_costs(self):
        '''
            Calculate the total cost of each solution in the population.
        '''
        for solution in self.solutions:
            solution.calculate_total_cost()
            
    def find_unplanned_tasks(self, solution):
        '''
            Find the tasks that are not planned in the solution.
        '''
        unplanned_tasks = []
        for task in self.all_tasks:
            if not solution.task_planned(task):
                unplanned_tasks.append(task)
        return unplanned_tasks

    def create_children_with_crossover(self, parent_1, parent_2):
        '''
            Create two children by performing crossover on two parents. 
            This is done by selecting a crossover point in one of the teams of each parent. 
            These teams can be different for the two parents, which is important to make sure tasks can move between teams.
            This method consists of the following steps:
                1) Select a team for crossover in both parents. 
                2) Select a crossover point in the plan of the selected team.
                    In order to keep the teams balanced in terms of workload, 
                    we want the crossover point to be at the same position in the plan of both parents or one position further for the team with the longest duration.
                3) Create two children and do the crossover for the teams with the crossover point.
                4) Copy the other teams while making sure we are avoiding duplicates.
                5) Fill the empty spots in the teams.
                6) Update the children and return them.
        '''
        # Step 1) Select a team for crossover in both parents.
        selected_team_1 = random.randint(0, 3)
        selected_team_2 = random.randint(0, 3)

        if len(parent_1.teams[selected_team_1].plan) < 2 or len(parent_2.teams[selected_team_2].plan) < 2:
            return parent_1, parent_2
        
        # Step 2) Select a crossover point in the plan of the selected team.
        crossover_point = random.randint(0, min(len(parent_1.teams[selected_team_1].plan), len(parent_2.teams[selected_team_2].plan)) - 2)
        crossover_point_1 = crossover_point
        crossover_point_2 = crossover_point

        if parent_1.teams[selected_team_1].duration < parent_2.teams[selected_team_2].duration:
            if random.random() < 0.5 and len(parent_2.teams[selected_team_2].plan) > crossover_point + 2:
                crossover_point_2 += 1

        # Step 3) Create two children and do the crossover for the teams with the crossover point.
        child_1 = Solution()
        child_2 = Solution()
        
        for task in range(0, crossover_point_1 + 1):
            child_1.add_task(parent_1.teams[selected_team_1].plan[task], selected_team_1)
        
        for task in range(0, crossover_point_2 + 1):
            child_2.add_task(parent_2.teams[selected_team_2].plan[task], selected_team_2)
        
        for task in range(crossover_point_2 + 1, len(parent_2.teams[selected_team_2].plan)):
            child_1.add_task(parent_2.teams[selected_team_2].plan[task], selected_team_1)
        
        for task in range(crossover_point_1 + 1, len(parent_1.teams[selected_team_1].plan)):
            child_2.add_task(parent_1.teams[selected_team_1].plan[task], selected_team_2)

        # Step 4) Copy the other teams while making sure we are avoiding duplicates.
        for team in range(0, 4):
            if team != selected_team_1:
                for task in parent_1.teams[team].plan:
                    child_1.add_task(task, team)
            if team != selected_team_2:
                for task in parent_2.teams[team].plan:
                    child_2.add_task(task, team)

        # Step 5) Fill the empty spots in the teams.
        unplaced_tasks_1 = self.find_unplanned_tasks(child_1)
        child_1.fix_solution(unplaced_tasks_1)
        unplaced_tasks_2 = self.find_unplanned_tasks(child_2)
        child_2.fix_solution(unplaced_tasks_2)

        # Step 6) Update the children and return them.
        child_1.sort_tasks_on_RUL()
        child_2.sort_tasks_on_RUL()
        child_1.calculate_total_cost()
        child_2.calculate_total_cost()
        
        return child_1, child_2

    def select_parents(self):
        '''
            Select two parents for the crossover operation.
            This is done by selecting a number of solutions for a tournament and selecting the best two solutions from this tournament.
        '''	
        # Step 1) Select randomly a number of solutions for the tournament
        randomly_sorted_solutions = self.solutions.copy()
        random.shuffle(randomly_sorted_solutions)
        tournament = randomly_sorted_solutions[:constants.TOURNAMENT_SIZE]

        # Step 2) Select the best two solutions from the tournament
        tournament.sort(key=lambda x: x.total_cost)
        return tournament[0], tournament[1]
    
    def create_children(self, amount):
        '''
            Create a number of children by performing crossover on the population.
            These children are used to create a new generation of the population.
        '''    
        number_created = 0
        new_solutions = []
        while number_created < amount:
            # Select two parents
            parent_1, parent_2 = self.select_parents()

            # In a small number of cases, we do not perform crossover and just copy the parents.
            if random.random() > constants.CROSSOVER_PROBABILITY:
                child_1 = copy.deepcopy(parent_1)
                child_2 = copy.deepcopy(parent_2)
            else:
                child_1, child_2 = self.create_children_with_crossover(parent_1, parent_2)

            # Add the child to the population
            new_solutions.append(child_1)
            new_solutions.append(child_2)
            number_created += 2
    
        return new_solutions

    def give_best_solutions(self, amount):
        self.solutions.sort(key=lambda x: x.total_cost)
        return copy.deepcopy(self.solutions[:amount])

    def create_next_generation(self):
        '''
            Create the next generation of the population by applying elitism and crossover.
        '''
        # Lets first apply Elitism by taking the best solutions. 
        new_solutions = self.give_best_solutions(constants.ELITISM_SIZE)

        # Then we create new children with crossover.
        new_solutions.extend(self.create_children(constants.POPULATION_SIZE - constants.ELITISM_SIZE))
        self.solutions = copy.deepcopy(new_solutions)
        self.solutions.sort(key=lambda x: x.total_cost)

    def give_best_feasiible_solution(self):
        '''
            Return the best solution that has a maximum duration of 30 days.
            It is no hard constraint for the population to only contain feasible solutions, however, at the end of the run we want to return a feasible solution.
        '''
        for solution in self.solutions:
            if solution.max_duration <= constants.MAX_PLAN_DURATION:
                return solution
        return None