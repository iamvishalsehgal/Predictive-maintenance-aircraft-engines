from team import Team
from task import Task
from solution import Solution
from population import Population
import pandas as pd
import random
import json
import constants

def choose_consultancy_dataset(choice):
    '''
        Choose the consultancy dataset or the predicted RULs dataset.
        If choice is True, the consultancy dataset is chosen, else the predicted RULs dataset is chosen.
    '''
    if choice == True:
        # Read the consultancy predictions from a CSV file
        df_consultancy_predictions = pd.read_csv('RUL_consultancy_predictions_A3.csv', sep=';')
        df_consultancy_predictions = df_consultancy_predictions.sort_values(by='RUL', ascending=True)
        
        all_tasks_A3 = []
        for engine_id in df_consultancy_predictions.id.unique():
            if df_consultancy_predictions[df_consultancy_predictions.id == engine_id].RUL.values[0] < constants.MAX_PLAN_DURATION:
                task = Task(engine_id, df_consultancy_predictions[df_consultancy_predictions.id == engine_id].RUL.values[0])
                all_tasks_A3.append(task)
        return all_tasks_A3
    else:
        # The path to the file containing the predicted RULs
        file_path = 'predicted_RUL_dict.txt'

        with open(file_path, 'r') as file:
            json_string = file.read()

        # Parse the JSON string into a Python dictionary
        prediction_data = json.loads(json_string)
        all_tasks_prediction = []
        for engine_id, rul in prediction_data.items():
            if rul < constants.MAX_PLAN_DURATION:
                task = Task(int(engine_id), rul)
                all_tasks_prediction.append(task)
        return all_tasks_prediction

def run_genetic_algorithm_x_times(runs):
    '''
        Run the Genetic Algorithm a number of times and print the average cost of the best solution over the runs.
    '''
    # Run the Genetic Algorithm 30 times to see how the algorithm performs on average.
    total_costs = 0
    times_score_of_30 = 0
    for i in range(runs):
        # Start the algorithm, by creating a population of solutions and running the Genetic Algorithm.
        population = Population(constants.POPULATION_SIZE, all_tasks)
        population.initialize()
        population.calculate_all_costs()

        population.print_population_statistics()
    
        # Run the Genetic Algorithm for 100 generations. So, the determination condition is the number of generations.
        for i in range(constants.NUMBER_OF_ITERATIONS):
            # Every iteration a new generation is created, based on the current population.
            population.create_next_generation()
            population.calculate_all_costs()
            population.print_population_statistics()
        
        best_solution = population.give_best_feasiible_solution()
        total_costs += best_solution.total_cost
        if best_solution.total_cost == 30:
            times_score_of_30 += 1
    
    # Print the average cost of the best solution over the 30 runs.
    print('Average best cost:', total_costs / runs)
    print('Times score of 30:', times_score_of_30)
    return population

def convert_best_solution_to_csv(best_solution):
    '''
        Convert the best solution to a CSV file, which can be used to submit the solution to the consultancy.
    '''
    df = pd.DataFrame()
    for team in best_solution.teams:
        for task in team.plan:
            csv_data = {'Team': [team.name], 'Type': [team.type], 'DaysOfWork': [team.duration], 'EngineID': [task.engine_id], 'RUL': [task.rul], 'StartDay': [task.start_time], 'EndDay': [task.end_time], 'DaysLate': [task.days_late], 'Cost': [task.cost]}
            df = pd.concat([df, pd.DataFrame(data=csv_data)], ignore_index=True)
    df.to_csv('BestSolution.csv', index=False, sep=';' )

if __name__ == '__main__':
    '''
        This is the main function of the program. It reads the predicted RULs from a file, creates a population of solutions and runs the Genetic Algorithm.
    '''
    # Now decide which RUL values to use for the Genetic Algorithm, either the predicted RULs or the consultancy predictions.
    # To choose the consultancy predictions, set the parameter to True, else set it to False.
    all_tasks = choose_consultancy_dataset(True)
    
    population = run_genetic_algorithm_x_times(1)

    # Finally, we print the solution to this optimalization problem. 
    best_solution = population.give_best_feasiible_solution()
    print(best_solution)

    # Extract the results in a csv file. The file is saved in the data folder with the name BestSolution.csv.
    convert_best_solution_to_csv(best_solution)