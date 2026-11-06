# NEURAL SENTRY — Predictive Maintenance for Industry

**Neural Storm 2026 | Track 01: Future Tech**  
**Problem Statement: FT-03 — Predictive Maintenance for Industry**

> An intelligent predictive maintenance system that estimates the Remaining Useful Life (RUL) of industrial equipment, detects abnormal sensor behaviour, and helps identify machines that may require maintenance.

---

## 1. Project Overview

Industrial machines operate under changing conditions and can gradually deteriorate over time. Unexpected equipment failures can lead to production downtime, increased maintenance costs, and operational risks.

Traditional maintenance approaches often rely on fixed schedules or react only after a fault occurs. These approaches may result in unnecessary maintenance or failures that could have been anticipated.

**Neural Sentry** aims to address this problem through machine-learning-based predictive maintenance. It analyses historical and sequential sensor readings to:

- Predict the Remaining Useful Life (RUL) of an engine.
- Estimate the machine's health using its predicted RUL.
- Detect abnormal sensor behaviour.
- Track machine conditions over successive operating cycles.
- Identify engines that may require maintenance through alert levels.
- Provide fleet-level monitoring through an interactive dashboard.

The current prototype uses the NASA C-MAPSS FD001 dataset, with a fleet simulation built from validation engine sequences.

## 2. Problem Statement and Our Approach

**Problem Statement FT-03: Predictive Maintenance for Industry**

The objective is to develop a system that can use equipment sensor data to anticipate potential failures and support timely maintenance decisions.

### Our approach

We divide the solution into five major stages:

1. **Data Preparation**
   - Use the NASA C-MAPSS FD001 dataset.
   - Prepare training and validation data.
   - Calculate Remaining Useful Life labels.
   - Split data by engine to prevent engine-level data leakage.
   - Remove constant sensor columns using the training partition.

2. **Feature Engineering**
   - Extract rolling means and standard deviations.
   - Calculate Exponential Moving Averages (EMA).
   - Calculate sensor trends over recent operating cycles.
   - Apply the same feature-generation logic during training and streaming inference.

3. **Machine Learning**
   - Train an XGBoost regression model to predict RUL.
   - Train an Isolation Forest model to detect abnormal sensor behaviour.
   - Apply a validation-calibrated safety margin to RUL predictions.

4. **Streaming Fleet Simulation**
   - Simulate multiple engines progressing through their operating cycles.
   - Process sensor readings sequentially.
   - Update predicted RUL, health index, anomaly status, and alert levels.

5. **Interactive Dashboard**
   - Display fleet health and engine status.
   - Provide simulation controls.
   - Present maintenance priorities and monitoring information.

## 3. Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Dashboard | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | XGBoost, Scikit-learn |
| Anomaly Detection | Isolation Forest |
| Data Visualization | Altair |
| Model Persistence | Joblib / Pickle |
| Dataset | NASA C-MAPSS FD001 |
| Version Control | Git and GitHub |

## 4. Machine Learning Models

### A. Remaining Useful Life Prediction — XGBoost

We use an XGBoost regression model to estimate the number of operating cycles remaining before an engine reaches its end-of-life condition.

**Model configuration:**
- Estimators: 400
- Maximum depth: 5
- Learning rate: 0.05
- Subsample: 0.8
- Column sampling: 0.8
- Random state: 42

**Validation performance:**

| Metric | Result |
|---|---:|
| Mean Absolute Error (MAE) | 11.41 cycles |
| Root Mean Squared Error (RMSE) | 15.82 cycles |

These metrics are measured on the held-out validation engines.

### B. Anomaly Detection — Isolation Forest

Isolation Forest identifies sensor patterns that differ from the learned healthy operating behaviour.

The model is trained using sensor observations from the healthy portion of the training data, where RUL is at least 100 cycles.

**Configuration:**
- Number of estimators: 200
- Contamination: 0.05
- Random state: 42

The anomaly detector provides an anomaly score and a binary anomaly flag.

### C. Safety-Calibrated RUL

To make RUL predictions more conservative, we calculate a safety margin using positive prediction errors in the low-RUL validation region.

- Low-RUL region: Actual RUL ≤ 50 cycles.
- Calibration percentile: 75th percentile.
- Selected safety margin: 14.1812 cycles.
- Maximum permitted margin: 15 cycles.

The final RUL is calculated as:

`Final RUL = clip(Raw Predicted RUL − Safety Margin, 0, 125)`

This margin is applied once during inference.

### D. Health Index

The Health Index represents the predicted remaining life as a percentage of the maximum RUL range.

`Health Index = clip((Final RUL / 125) × 100, 0, 100)`

The Fleet Health Score is calculated as the average Health Index across the simulated engines.

## 5. Alert and Maintenance Logic

The prototype combines predicted RUL zones with persistent anomaly detection to help identify engines that may require attention.

**RUL-based zones:**

| Condition | RUL |
|---|---:|
| Critical Zone | ≤ 20 cycles |
| Warning Zone | ≤ 50 cycles |
| Normal RUL Zone | > 50 cycles |

**Anomaly persistence levels:**

| Consecutive anomalous cycles | Persistence Level |
|---|---|
| 1 | Watch |
| 3 | Warning |
| 5 | Critical |

The alert system also considers RUL risk when determining the combined alert level. This helps avoid treating every isolated anomalous reading as an immediate critical event.

## 6. Dashboard Features

The dashboard is being developed using Streamlit with an industrial monitoring interface.

### Overview
- Total engine count.
- Healthy, Warning, and Critical engine counts.
- Fleet Health Score.
- Status distribution.
- Maintenance priority list.
- Predicted RUL distribution.

### Live Monitoring
- Sequential fleet simulation.
- Start, Pause, and Reset controls.
- Simulation speed control.
- Simulation progress indicator.
- Engine-level monitoring information.

### Alerts
- Engine alert levels.
- Anomaly persistence information.
- Maintenance-related alert activity.

**Note:** Features that are still under development will be marked as planned or in progress in the final submission.

## 7. Dataset

This project uses the **NASA Commercial Modular Aero-Propulsion System Simulation (C-MAPSS), FD001** dataset.

FD001 contains simulated turbofan engine run-to-failure data with multiple operating and sensor measurements.

The dataset is used to train and validate the RUL prediction and anomaly detection models.

### Data preparation summary

- Training engines: 80
- Validation engines: 20
- Cleaned training observations: 16,561
- Cleaned validation observations: 4,070
- Retained sensor measurements: 15
- RUL values capped at 125 cycles for training and evaluation.

The train-validation split is performed by engine ID to prevent observations from the same engine appearing in both partitions.

## 8. Setup and Installation

### Prerequisites

- Python 3.14 (the development environment used for this project).
- Git.
- pip.
- A Windows, Linux, or macOS environment.

### Step 1: Clone the repository

```bash
git clone https://github.com/nihaverse/neural-storm-ft03.git
cd neural-storm-ft03
```

### Step 2: Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

If the repository contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages:

```bash
pip install streamlit pandas numpy scikit-learn xgboost joblib altair
```

## 9. Running the Project Locally

After installing the dependencies and ensuring that the required processed dataset and trained model artifacts are present in their expected project locations:

```bash
streamlit run dashboard/app.py
```

Streamlit will provide a local URL, generally:

```text
http://localhost:8501
```

Open the URL in a browser to access the dashboard.

**Important:** The trained model files and processed datasets are not necessarily included in the Git repository. Make sure the required artifacts are generated or placed in the expected locations before starting the application.

## 10. Screenshots and Demo

Add screenshots or a short GIF demonstrating the working application.

Suggested screenshots:

1. **Fleet Overview** — fleet KPIs, health score, status distribution, and RUL distribution.
2. **Live Monitoring** — simulation controls, progress, and engine-level updates.
3. **Alerts** — warning and critical engine alerts.
4. **Model Results** — actual versus predicted RUL and model performance metrics.

<!-- Replace the placeholders below with actual repository image paths. -->

```markdown
![Fleet Overview](docs/images/fleet-overview.png)

![Live Monitoring](docs/images/live-monitoring.png)

![Alerts](docs/images/alerts.png)
```

Demo video/GIF: **[Add demo link here]**

## 11. AI Tools Used

AI tools were used as development assistance during the project.

- **ChatGPT:** Used for technical explanations, debugging assistance, implementation planning, code review discussions, and understanding machine-learning concepts.
- All implementation decisions, code integration, testing, and project validation were carried out as part of the project development process.

Add any other AI tools used by the team here, if applicable.

## 12. Team

**Team Name:** DEV


## 13. Future Enhancements

The following improvements are planned beyond the currently implemented prototype:

- Optimize inference and simulation throughput for faster fleet processing.
- Improve dashboard refresh behaviour and real-time visualization consistency.
- Complete and refine the Live Monitoring and Alerts pages.
- Extend the system to additional NASA C-MAPSS operating conditions and datasets.
- Explore more advanced failure prediction and maintenance scheduling strategies.
- Add richer engine-level diagnostic information and maintenance recommendations.

## 14. Project Repository

**GitHub:** https://github.com/nihaverse/neural-storm-ft03

---

**Neural Sentry — Turning sensor data into proactive maintenance insights.**