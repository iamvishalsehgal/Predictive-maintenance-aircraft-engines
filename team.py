from task import Task
import copy

class Team:
    '''
This class consists of a series of tasks that represent the planning of a single team.    '''
    def __init__(self, team_type, team_name):
        self.plan = []
        self.type = team_type
        self.name = team_name
        self.duration = 0

    def __repr__(self):
        return f'{self.name}, {self.type}, {self.duration}, {self.plan} \n'
    
    def add_task(self, task_item):
        '''
            Add a task to the plan's end.
        '''
        self.plan.append(copy.deepcopy(task_item))
        self.sort_tasks_on_RUL()

    def add_empty_task(self):
        '''
            This function can be used to add an empty job to the plan if crossover causes an engine's maintenance to be scheduled more than once.
            A genuine task that is no longer included in the plan can take the place of this empty one.        '''
        dummy_task = Task(-1, -1)
        self.add_task(dummy_task)

    def sort_tasks_on_RUL(self):
        '''
            Observing that it is always best to organize the jobs with increasing RUL is crucial for this puzzle.
             On RUL, the tasks in the plan are arranged using this way.
        ''' 
        self.plan = sorted(self.plan, key=lambda task_obj: task_obj.rul, reverse=False)
