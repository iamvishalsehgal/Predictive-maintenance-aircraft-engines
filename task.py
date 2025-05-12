class Task:
    '''
        The Task class represents one engine's maintenance, which is performed by a single team.
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
