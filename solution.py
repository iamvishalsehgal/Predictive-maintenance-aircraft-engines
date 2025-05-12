from team import Team
import random
import constants

class Solution:
    '''
        This class represents a solution to the problem.
        A solution consists of a list of four teams, each team has a plan, which is a sequence of tasks.
        Teams 1 and 3 are of type A, teams 2 and 4 are of type B.
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
    
    def add_team(self, team):
        self.teams.append(team)

    def add_task_to_random_team(self, task):
        '''
            Adds a task to a random team in a smart way. We want the workload of the teams to be balanced as much as possible.
            Therefore, we want to avoid situations where some teams have a lot of tasks and others have only a few. 
            We do this by only allowing a task to be added to a team if the duration of the team is not too much larger than the minimum duration of all teams.
        '''
        team_found = False
        while not team_found:
            best_team = random.randint(0, len(self.teams) - 1)
            if self.teams[best_team].duration <= self.min_duration + constants.RANDOM_INSERTION_MAXIMUM_INBALANCE:
                team_found = True
                self.teams[best_team].add_task(task)
    
    def add_task(self, task, team_index):
        '''
            Adds a task to a specific team.
        '''
        if self.task_planned(task):
            self.teams[team_index].add_empty_task()
        else:
            self.teams[team_index].add_task(task)

        # Recompute the cost of the task.
        self.calculate_cost(task)
    
    def task_planned(self, task):
        '''
            Check if a task is already planned in one of the teams. This is important to avoid planning the same task multiple times.
        '''
        for team in self.teams:
            for planned_task in team.plan:
                if planned_task.engine_id == task.engine_id:
                    return True
        return False

    def calculate_cost(self, task):
        task.cost = 0
        if task.days_late <= 0:
            return 0
        
        for day in range(1, task.days_late + 1):
            cj = 0
            if 1 <= task.engine_id <= 25:
                cj = 4
            elif 26 <= task.engine_id <= 45:
                cj = 2
            elif 46 <= task.engine_id <= 75:
                cj = 5
            else:  # 76-100
                cj = 6
                
            daily_cost = cj * (day ** 2)
            task.cost += min(daily_cost, constants.MAX_DAILY_COST)
        return task.cost

    def calculate_total_cost(self):
        '''
            This method calculates the total cost of the solution. It does this by calculating the cost of each task and summing them.
            Additionally, it calculates the duration of each team and the minimum and maximum duration of all teams.
            It starts by sorting the tasks on RUL, because it is always optimal to plan the tasks with increasing RUL.
        '''
        self.sort_tasks_on_RUL()
        self.total_cost = 0

        for team in self.teams:
            start = 1
            for task in team.plan:
                task.cost = 0
                task.duration = self.calculate_duration(team.type, task.engine_id)
                task.start_time = start
                start += task.duration
                task.end_time = start - 1
                task.days_late = max(task.end_time - task.rul, 0)
                task.cost = self.calculate_cost(task)
                self.total_cost += task.cost     
            team.duration = start - 1

        self.min_duration = float('inf')
        self.max_duration = 0

        for team in self.teams:
            if team.duration < self.min_duration:
                self.min_duration = team.duration
            if team.duration > self.max_duration:
                self.max_duration = team.duration
        
        return self.total_cost

    def calculate_duration(self, type, engine_id):

        mu_a = 0
        if 1 <= engine_id <= 20:
            mu_a = 5
        elif 21 <= engine_id <= 55:
            mu_a = 3
        elif 56 <= engine_id <= 80:
            mu_a = 4
        else:  # 81-100
            mu_a = 5
            
        if type == 'A':
            return mu_a
        elif type == 'B':
            if 1 <= engine_id <= 25:
                return mu_a - 1
            elif 26 <= engine_id <= 70:
                return mu_a + 3
            else:  # 71-100
                return mu_a + 2

    def fix_solution(self, unplanned_tasks):
        '''
            This method fixes a solution by adding the unplanned tasks to the teams. 
            It does this in three steps: 
                1) First, by filling the gaps in the plans of the teams with the unplanned tasks.
                2) Then, by adding the remaining tasks to a random team while keeping the workload of the teams balanced.
                3) Finally, by removing the remaining empty tasks that were added in step 1, if they stil exist.
        '''
        # Step 1: Fill the gaps in the plans of the teams with the unplanned tasks.
        for team in self.teams:
            for task in team.plan:
                if task.engine_id < 0:
                    if len(unplanned_tasks) > 0:
                        unplanned_task = unplanned_tasks.pop()
                        task.engine_id = unplanned_task.engine_id
                        task.rul = unplanned_task.rul

        # Step 2: Add the remaining tasks to a random team while keeping the workload of the teams balanced.
        for unplanned_task in unplanned_tasks:
            self.add_task_to_random_team(unplanned_task)

        # Step 3: Remove the remaining empty tasks that were added in step 1, if they stil exist.
        for team in self.teams:
            new_plan = [task for task in team.plan if task.engine_id >= 0]
            team.plan = new_plan
                
    def sort_tasks_on_RUL(self):
        '''
            For this puzzle it is important to observe that it is always optimal to plan the tasks with increasing RUL.
            This method is used to sort the tasks in the plan on RUL, for all the teams.
        '''
        for team in self.teams:
            team.sort_tasks_on_RUL()