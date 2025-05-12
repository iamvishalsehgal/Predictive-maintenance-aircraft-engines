from team import Team
import json
from solution import Solution
import constants
import random
from task import Task
from population import Population
import pandas as pd
def choose_consultancy_dataset(use_consultancy):
    '''
        Select either the anticipated RULs dataset or the consultancy dataset.
         The consulting dataset is selected if use_consultancy is True; if not, the projected RULs dataset is selected.
    '''
    if use_consultancy == True:
        # Read consultancy predictions 
        df_consultancy_predictions = pd.read_csv('RUL_consultancy_predictions_A3.csv', sep=';')
        df_consultancy_predictions = df_consultancy_predictions.sort_values(by='RUL', ascending=True)
        
        all_tasks_consultancy = []
        for engine_identifier in df_consultancy_predictions.id.unique():
            if df_consultancy_predictions[df_consultancy_predictions.id == engine_identifier].RUL.values[0] < constants.MAX_PLAN_DURATION:
                task_obj = Task(engine_identifier, df_consultancy_predictions[df_consultancy_predictions.id == engine_identifier].RUL.values[0])
                all_tasks_consultancy.append(task_obj)
        return all_tasks_consultancy
    else:
        
        file_path = 'predicted_RUL_dict.txt'

        with open(file_path, 'r') as file:
            json_string = file.read()

        # Parse JSON into a dictionary
        prediction_data = json.loads(json_string)
        all_tasks_prediction = []
        for engine_id_str, rul_value in prediction_data.items():
            if rul_value < constants.MAX_PLAN_DURATION:
                task_obj = Task(int(engine_id_str), rul_value)
                all_tasks_prediction.append(task_obj)
        return all_tasks_prediction

def run_genetic_algorithm_x_times(num_runs):
    '''
        Print the average cost of the optimal solution after running the Genetic Algorithm several times.
    '''
    # To see the average performance of the Genetic Algorithm, run it 30times.
    total_costs = 0
    times_score_of_30 = 0
    for run_idx in range(num_runs):
        # For 100 generations, run the genetic algorithm.  Therefore, the number of generations is the determining requirement.
        population_obj = Population(constants.POPULATION_SIZE, all_tasks)
        population_obj.initialize()
        population_obj.calculate_all_costs()

        population_obj.print_population_statistics()
    
        # For 100 generations, run the genetic algorithm.  Therefore, the number of generations is the determining requirement.
        for gen_idx in range(constants.NUMBER_OF_ITERATIONS):
            # Based on the current population, a new generation is produced with each repetition.
            population_obj.create_next_generation()
            population_obj.calculate_all_costs()
            population_obj.print_population_statistics()
        
        best_solution = population_obj.give_best_feasiible_solution()
        total_costs += best_solution.total_cost
        if best_solution.total_cost == 30:
            times_score_of_30 += 1
    
    # Print the best solution's average cost over the course of 30 runs.
    print('Average best cost:', total_costs / num_runs)
    print('Times score of 30:', times_score_of_30)
    return population_obj

def convert_best_solution_to_csv(best_solution):
    '''
        To submit the solution to the consultancy, convert the best solution into a CSV file.
    '''
    results_df = pd.DataFrame()
    for team_obj in best_solution.teams:
        for task_obj in team_obj.plan:
            csv_data = {'Team': [team_obj.name], 'Type': [team_obj.type], 'DaysOfWork': [team_obj.duration], 'EngineID': [task_obj.engine_id], 'RUL': [task_obj.rul], 'StartDay': [task_obj.start_time], 'EndDay': [task_obj.end_time], 'DaysLate': [task_obj.days_late], 'Cost': [task_obj.cost]}
            results_df = pd.concat([results_df, pd.DataFrame(data=csv_data)], ignore_index=True)
    results_df.to_csv('BestSolution.csv', index=False, sep=';' )

if __name__ == '__main__':
    '''
This is the program's primary purpose.  It generates a population of solutions, executes the Genetic Algorithm, and reads the predicted RULs from a file.    '''
    # Choose between using the consultancy's predictions or the predicted RULs for the Genetic Algorithm.
    # Set the parameter to True or False to select the consultancy predictions.
    all_tasks = choose_consultancy_dataset(True)
    
    population_obj = run_genetic_algorithm_x_times(1)

    # Lastly, we print the optimalization problem's solution.
    best_solution = population_obj.give_best_feasiible_solution()
    print(best_solution)

    # The results are extracted into a CSV file.  The BestSolution.csv file is stored in the data folder.
    convert_best_solution_to_csv(best_solution)
