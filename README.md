# Machine Learning Deployment

Machine learning project covering model development, evaluation, deployment, and production integration.

## Project Overview

This project focuses on developing and deploying a Machine Learning model following a structured and reproducible workflow.

The project covers the different stages required to move from model development to a production-ready solution.

## Objectives

- Develop and evaluate Machine Learning models.
- Structure the project following software engineering best practices.
- Version and document the development process.
- Prepare the model for deployment.
- Ensure reproducibility and maintainability.

## Project Structure

```text
machine_learning_deployment/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── output/
│
├── src/
│
├── tests/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
├── README.md
└── requirements.txt

## Installation and Setup

### Prerequisites

- Python 3.12 or higher
- Git

### 1. Clone the repository

```bash
git clone https://github.com/rafadmgs/machine_learning_deployment.git
cd machine_learning_deployment
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the tests

```bash
python -m pytest