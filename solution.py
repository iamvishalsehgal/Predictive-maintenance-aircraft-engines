from team import Team
import random
import constants

class Solution:
    '''
        The problem is solved by this class.
         Four teams make up the solution, and each team has a plan, which is a list of tasks.
         Teams two and four belong to type B, while teams one and three belong to type A.
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
            cleverly assigns a task to a random team.  We want the teams' workloads to be as evenly distributed as possible.
             As a result, we want to steer clear of scenarios in which some teams have a large number of tasks while others have a small number. 
             To achieve this, we only permit a task to be added to a team if the team's duration is not significantly longer than the minimum duration required for all teams.
        '''
        team_found = False
        while not team_found:
            best_team_idx = random.randint(0, len(self.teams) - 1)
            if self.teams[best_team_idx].duration <= self.min_duration + constants.RANDOM_INSERTION_MAXIMUM_INBALANCE:
                team_found = True
                self.teams[best_team_idx].add_task(task_obj)
    
    def add_task(self, task_obj, team_index):
        '''
            assigns a task to a particular group.
        '''
        if self.task_planned(task_obj):
            self.teams[team_index].add_empty_task()
        else:
            self.teams[team_index].add_task(task_obj)

        # Recompute the cost of the task.
        self.calculate_cost(task_obj)
    
    def task_planned(self, task_obj):
        '''
            Verify if one of the teams has a task scheduled already.  Preventing the same task from being planned more than once is crucial.
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
            task_obj.cost += min(daily_cost, constants.MAX_DAILY_COST)
        return task_obj.cost

    def calculate_total_cost(self):
        '''
            This approach determines the solution's overall cost.  It accomplishes this by adding up the costs of all the tasks.
             It also determines the minimum and maximum durations for all teams as well as the duration of each team.
             Since it is always best to plan tasks with increasing RUL, it begins by sorting the tasks according to RUL.        '''
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
            This method improves a solution by incorporating unplanned tasks into the teams' schedules. It does this in three steps: First, it fills any gaps or empty spots in the existing team plans with the unplanned tasks. Then, it assigns the remaining unplanned tasks to randomly selected teams while ensuring that the overall workload remains balanced. Finally, it removes any empty tasks that were added during the first step, in case they still remain.        '''
        # Step 1: Use the unplanned jobs to fill up the gaps in the teams' plans.
        for team_obj in self.teams:
            for task_obj in team_obj.plan:
                if task_obj.engine_id < 0:
                    if len(unplanned_tasks_list) > 0:
                        unplanned_task_obj = unplanned_tasks_list.pop()
                        task_obj.engine_id = unplanned_task_obj.engine_id
                        task_obj.rul = unplanned_task_obj.rul

        # Step 2: Assign the remaining tasks to a randomly selected team while maintaining a balanced burden for each team.
        for unplanned_task_obj in unplanned_tasks_list:
            self.add_task_to_random_team(unplanned_task_obj)

        # Step 3: If any empty tasks that were added in step 1 are still there, remove them.
        for team_obj in self.teams:
            new_plan = [task_obj for task_obj in team_obj.plan if task_obj.engine_id >= 0]
            team_obj.plan = new_plan
                
    def sort_tasks_on_RUL(self):
        '''
            Observing that it is always best to organize the jobs with increasing RUL is crucial for this puzzle.
             Using this strategy, all teams' tasks in the RUL plan are sorted.
        '''
        for team_obj in self.teams:
            team_obj.sort_tasks_on_RUL()
