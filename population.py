from solution import Solution
from task import Task
import random
import copy
import constants

class Population:
    '''
        This class optimizes the teams' planning by representing a population of solutions and the primary Genetic Algorithm loop.
         The solutions list contains the many solutions.
         The size parameter determines the population's size.
         A list of tasks that require planning is contained in the all_tasks argument.
         The population's best score is tracked using the best_score option. '''
    def __init__(self, population_size, task_list):
        self.solutions = []
        self.size = population_size
        self.all_tasks = task_list
        self.best_score = 0
        # It makes sense to schedule the tasks with the lowest RUL first in this challenge, thus sort the tasks according to RUL.
        self.all_tasks.sort(key=lambda task_obj: task_obj.rul, reverse=False)

    def __repr__(self):
        return f'{self.solutions}'
    
    def initialize(self):
        ''' 
            Assign tasks to teams at random while maintaining a balanced workload to generate the initial population of solutions.
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
            During a run, print the population's best, worst, and average scores to observe how the algorithm is executing and convergent.
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
            This method generates two child solutions by applying a crossover operation on two parent solutions. The crossover allows for the exchange of task sequences between parents while maintaining team structure and workload balance.

Steps:
1.Select Teams for Crossover: Choose one team from each parent for crossover. These teams may differ between the two parents to allow tasks to be transferred across teams.
2. Determine Crossover Point: Select a crossover point in the selected team’s plan from each parent.
2.1 To maintain workload balance, the crossover point should be at the same position in both plans, or one position further in the longer of the two plans (based on total duration).
3. Perform Crossover: Create two child solutions by exchanging the task segments between the selected teams at the determined crossover points.
4. Copy Remaining Teams: Copy the unselected teams from each parent into the corresponding child solution, ensuring no duplicate tasks are introduced.
5. Fill Empty Spots: Fill any empty positions created during crossover with appropriate placeholder or idle tasks, if necessary.
6. Finalize and Return Children: Update the child solutions to ensure validity and return them as new candidate solutions.
        '''
        # Step 1: Choose a team to perform crossover on in both parent solutions.
        selected_team_1_idx = random.randint(0, 3)
        selected_team_2_idx = random.randint(0, 3)

        if len(parent_1.teams[selected_team_1_idx].plan) < 2 or len(parent_2.teams[selected_team_2_idx].plan) < 2:
            return parent_1, parent_2
        
        # Step 2) Identify a crossover point within the plan of the selected team.
        crossover_point = random.randint(0, min(len(parent_1.teams[selected_team_1_idx].plan), len(parent_2.teams[selected_team_2_idx].plan)) - 2)
        crossover_point_1_idx = crossover_point
        crossover_point_2_idx = crossover_point

        if parent_1.teams[selected_team_1_idx].duration < parent_2.teams[selected_team_2_idx].duration:
            if random.random() < 0.5 and len(parent_2.teams[selected_team_2_idx].plan) > crossover_point + 2:
                crossover_point_2_idx += 1

        # Step 3) Perform crossover by creating two child teams using the selected crossover point.
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

        # Step 4) Copy the remaining teams, ensuring no duplicates are included.
        for team_idx in range(0, 4):
            if team_idx != selected_team_1_idx:
                for task_obj in parent_1.teams[team_idx].plan:
                    child_1.add_task(task_obj, team_idx)
            if team_idx != selected_team_2_idx:
                for task_obj in parent_2.teams[team_idx].plan:
                    child_2.add_task(task_obj, team_idx)

        # Step 5) Populate the remaining positions in the teams.
        unplaced_tasks_1 = self.find_unplanned_tasks(child_1)
        child_1.fix_solution(unplaced_tasks_1)
        unplaced_tasks_2 = self.find_unplanned_tasks(child_2)
        child_2.fix_solution(unplaced_tasks_2)

        # Step 6) Update the child teams and return 
        child_1.sort_tasks_on_RUL()
        child_2.sort_tasks_on_RUL()
        child_1.calculate_total_cost()
        child_2.calculate_total_cost()
        
        return child_1, child_2
    
    def calculate_all_costs(self):
        '''
            Determine the overall cost of every population solution.
        '''
        for solution_obj in self.solutions:
            solution_obj.calculate_total_cost()
            
    def find_unplanned_tasks(self, solution_obj):
        '''
            Look for the unplanned jobs in the solution.
        '''
        unplanned_tasks_list = []
        for task_obj in self.all_tasks:
            if not solution_obj.task_planned(task_obj):
                unplanned_tasks_list.append(task_obj)
        return unplanned_tasks_list


    def select_parents(self):
        '''
            Select two parent solutions for the crossover operation. This is done by conducting a tournament selection, where a subset of solutions is randomly chosen, and the two best solutions are selected from this group.
        '''	
        # Step 1) Select randomly a number of solutions for the tournament
        randomly_sorted_solutions = self.solutions.copy()
        random.shuffle(randomly_sorted_solutions)
        tournament_candidates = randomly_sorted_solutions[:constants.TOURNAMENT_SIZE]

        # Step 2) Select the best two solutions from the tournament
        tournament_candidates.sort(key=lambda solution_obj: solution_obj.total_cost)
        return tournament_candidates[0], tournament_candidates[1]
    
    def create_children(self, amount):
        '''
            Produce a set of child solutions via crossover operations across the population. These children form the basis of the subsequent generation, ensuring genetic diversity and iterative optimization.
        '''    
        number_created = 0
        new_solutions = []
        while number_created < amount:

            parent_1, parent_2 = self.select_parents()

            if random.random() > constants.CROSSOVER_PROBABILITY:
                child_1 = copy.deepcopy(parent_1)
                child_2 = copy.deepcopy(parent_2)
            else:
                child_1, child_2 = self.create_children_with_crossover(parent_1, parent_2)

            # Add child to population
            new_solutions.append(child_1)
            new_solutions.append(child_2)
            number_created += 2
    
        return new_solutions

    def give_best_solutions(self, amount):
        self.solutions.sort(key=lambda solution_obj: solution_obj.total_cost)
        return copy.deepcopy(self.solutions[:amount])

    def create_next_generation(self):
        '''
            Create the next generation of the population by applying elitism and crossover.
        '''
        # apply elitism by taking the best solutions. 
        new_solutions = self.give_best_solutions(constants.ELITISM_SIZE)

        # create new children with crossover.
        new_solutions.extend(self.create_children(constants.POPULATION_SIZE - constants.ELITISM_SIZE))
        self.solutions = copy.deepcopy(new_solutions)
        self.solutions.sort(key=lambda solution_obj: solution_obj.total_cost)

    def give_best_feasiible_solution(self):
        '''
            Identify the optimal solution that adheres to a 30-day maximum duration. While the algorithm permits the inclusion of infeasible solutions within the population during intermediate steps, it ensures that the final output is a feasible solution.
        '''
        for solution_obj in self.solutions:
            if solution_obj.max_duration <= constants.MAX_PLAN_DURATION:
                return solution_obj
        return None
