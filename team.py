from task import Task
import copy

class Team:
    '''
        This class represents the planning of one team consisting of a sequence of tasks.
    '''
    def __init__(self, type, name):
        self.plan = []
        self.type = type
        self.name = name
        self.duration = 0

    def __repr__(self):
        return f'{self.name}, {self.type}, {self.duration}, {self.plan} \n'
    
    def add_task(self, task):
        '''
            Add a task to the end of the plan.
        '''
        self.plan.append(copy.deepcopy(task))
        self.sort_tasks_on_RUL()

    def add_empty_task(self):
        '''
            If crossover results in a situation where maintenance of an engine is planned multiple times, then this function can be used to add an empty task to the plan.
            This empty task can be replaced by a real task that is no longer part of the plan.
        '''
        task = Task(-1, -1)
        self.add_task(task)

    def sort_tasks_on_RUL(self):
        '''
            For this puzzle it is important to observe that it is always optimal to plan the tasks with increasing RUL.
            This method is used to sort the tasks in the plan on RUL.
        ''' 
        self.plan = sorted(self.plan, key=lambda x: x.rul, reverse=False)
    
