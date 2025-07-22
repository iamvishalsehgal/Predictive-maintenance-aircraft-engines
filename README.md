# Predictive Maintenance Scheduling for Airplane Engines

This project focuses on predicting the Remaining Useful Lifetime (RUL) of airplane engines and optimizing their maintenance schedules using predictive analytics and optimization techniques.

## Project Overview

The project consists of two main tasks:
1. **Prediction Task**: Build a model to predict the RUL of airplane engines using historical run-to-failure data.
2. **Optimization Task**: Schedule maintenance for the engines based on predicted RULs, optimizing team allocation and minimizing costs.

## Prediction Task

The goal of this task is to predict the RUL of engines using the dataset `DataTrain.csv`, which contains run-to-failure data for 100 engines with operational settings and sensor measurements.

- **Data Analysis**: 
  - Calculated RUL by subtracting the current cycle from the maximum cycle count per engine (e.g., an engine with a max cycle of 102 has RUL 1 at cycle 101).
  - Conducted variance analysis to identify and exclude low-variance features (e.g., `set1`, `sensor_val7`, `sensor_val8`, `sensor_val11`, `sensor_val14`, `sensor_val16`, `sensor_val20`).
- **Feature Engineering**: 
  - Selected key features with sufficient variability: `cycle`, `set2`, `set3`, `sensor_val1` to `sensor_val6`, `sensor_val9` to `sensor_val10`, `sensor_val12` to `sensor_val13`, `sensor_val15`, `sensor_val17` to `sensor_val19`, `sensor_val21`.
  - Visualized feature distributions to confirm their suitability.
- **Model Development**: 
  - Developed a Random Forest regression model.
  - Tuned hyperparameters using grid search with 5-fold cross-validation:
    - Number of trees: [50, 100, 200]
    - Maximum depth: [None, 10, 20, 30]
    - Minimum samples split: [2, 5, 10]
    - Minimum samples leaf: [1, 2, 4]
    - Max features: [sqrt, log2]
  - Evaluated performance using Mean Absolute Error (MAE), chosen for its linear error penalty and reduced sensitivity to outliers compared to MSE.
- **Results**: The model achieved reasonable accuracy on the test set, providing integer-valued RUL predictions for subsequent use.

## Optimization Task

This task involves scheduling maintenance for engines using the predicted RULs, considering constraints like team availability, maintenance durations, and costs. Two team types (A and B) are available, each with specific maintenance durations per engine.

- **Problem Formulation**: 
  - Formulated as a constrained optimization problem to minimize costs and balance workloads across teams.
  - Constraints include team availability, no overlapping maintenance on the same engine, and a planning horizon of 30 days.
- **Approach**: 
  - Implemented a genetic algorithm using the DEAP library.
  - Key parameters:
    - Population size: 100
    - Crossover probability: 0.9
    - Tournament size: 5
    - Elitism size: 10 (preserves top solutions)
    - Iterations: 100
    - Max daily cost: 250
    - Max imbalance: 5 days (for workload balancing)
- **Results**: The algorithm generates a maintenance schedule that assigns teams to engines, ensuring timely maintenance while optimizing costs and workload distribution.

## Usage

To run the project, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Prediction Script**:
   ```bash
   python predict_rul.py
   ```
   - This generates RUL predictions using the trained Random Forest model.
4. **Run the Optimization Script**:
   ```bash
   python optimize_schedule.py
   ```
   - This produces the maintenance schedule based on the predicted RULs.

## Dependencies

- Python 3.x
- pandas
- numpy
- scikit-learn
- DEAP (for genetic algorithm)

Ensure these are installed via:
```bash
pip install pandas numpy scikit-learn deap
```
