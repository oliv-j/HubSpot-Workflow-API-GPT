# HubSpot-Workflow-API-GPT

## Overview

**HubSpot-Workflow-API-GPT** is a comprehensive tool designed to analyze and manage HubSpot workflows with technical precision and detail. Leveraging the HubSpot Automation API v4, this repository provides scripts to fetch, process, and export workflow data, as well as a custom GPT model configuration tailored for in-depth analysis of HubSpot workflows.

## Features

- **Automated Workflow Retrieval**: Fetch all workflows from your HubSpot portal, handling pagination seamlessly.
- **Detailed Data Export**: Export workflow details into structured CSV files for easy analysis.
- **Secure Authentication**: Utilize macOS Keychain for secure storage and retrieval of HubSpot API tokens via the `keyring` library.
- **Custom GPT Integration**: Analyze and interpret workflows with the integrated HubSpot Workflow Analyzer GPT.
- **Comprehensive Documentation**: Detailed README and supporting documentation to guide setup and usage.

## Prerequisites

- **macOS**: This tool is specifically designed for macOS environments.
- **Homebrew**: Package manager for macOS to install Python and other dependencies.
- **Python 3.7+**: Ensure Python is installed via Homebrew.
- **Git**: To clone the repository.
- **HubSpot API Access**: A HubSpot account with access to the Automation API v4 and necessary permissions.

## Installation

### 1. Install Homebrew (If Not Already Installed)

Homebrew is essential for managing packages on macOS.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python via Homebrew
Ensure Python is installed using Homebrew to manage dependencies effectively.

```bash
brew install python
```

...and verify the installation:

```bash
python3 --version
```

### 3. Clone the Repository
```bash
git clone https://github.com/yourusername/HubSpot-Workflow-API-GPT.git
cd HubSpot-Workflow-API-GPT
```

### 4. Set Up a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies
Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

> **Note**: If you encounter permission issues during installation, ensure you're operating within the virtual environment.

### 6. Configure Authentication
Store your HubSpot API token securely using macOS Keychain.

#### a. Install `keyring`
Ensure `keyring` is installed in your virtual environment.

```bash
pip install keyring
```

#### b. Store the API Token
Run the following Python commands to store your API token securely:

```python
import keyring

service_name = "keychain-item-name"
username = "username"
api_token = "your_actual_private_app_token_here"

keyring.set_password(service_name, username, api_token)
```

## Usage

### 1. Fetch and Export Workflows
Run the Python script to fetch all workflows from your HubSpot portal and export them to a CSV file.

```bash
python export_flows_to_csv.py
```

Upon successful execution, the workflow data will be saved to `~/Downloads/flows/all_flow_content.csv`.

### 2. Analyze Workflows with Custom GPT
Utilize the integrated **HubSpot Workflow Analyzer GPT** to interpret and analyze your workflows. Provide workflow documentation, JSON examples, or CSV exports, and receive detailed technical explanations.

### GPT Instructions:
Instructions: This GPT is designed to analyze HubSpot workflows. The user will provide workflow documentation, JSON examples, and exports (such as CSV files) from a HubSpot portal, which contain workflow details. This GPT will interpret, understand, and explain these workflows with a detailed and technical approach. When the user provides a workflow name or ID, it will generate a summary followed by a detailed breakdown of the workflow's triggers, steps, branching logic, and actions. Additionally, users can ask about all workflows in the HubSpot portal to identify workflows triggered by specific conditions, or which perform certain actions (e.g., send an email or trigger based on a change in a field). The GPT will reference HubSpot API documentation and examples provided by the user. Responses will prioritize detailed technical explanations over simplicity to ensure the user has a full understanding of the workflow architecture and logic. Communication will be precise and formal.

#### Conversation Starters:
- What does workflow XYZ do in HubSpot?
- Can you list all workflows triggered by X?
- Which workflows in HubSpot send emails?
- Break down the steps and actions of workflow ABC.

## Repository Structure

```bash
HubSpot-Workflow-API-GPT/
├── export_flows_to_csv.py
├── requirements.txt
├── README.md
├── config/
│   └── customGPT_config.txt
├── gpt-training-files/
│   └── json-workflow-examples.txt
└── flows/
    ├── all_flows.txt
    └── all_flow_content.csv
```
- **export_flows_to_csv.py**: Python script to fetch and export HubSpot workflows.
- **requirements.txt**: List of Python dependencies.
- **config/customGPT_config.txt**: Configuration for the custom GPT model.
- **flows/**: Directory to store workflow data and exports.
- **gpt-training-files/**: Directory of json workflow code examples and PDF of HubSpot web page for automation API documentation.