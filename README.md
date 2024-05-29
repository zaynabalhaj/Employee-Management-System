# Employee Management System

## Overview

The Employee Management System is a comprehensive platform designed to enhance project management and team collaboration within an organization. It allows managers to effectively match employee skills with project requirements, monitor progress, and provide feedback. Employees can view their own progress and set personal goals. This tool is built to support a diverse workplace by including a feature for Arabic translation, facilitating better communication among team members who are native Arabic speakers.

## Key Features

- **Skill Matching**: Automatically align employee skills with project needs to optimize resource allocation and project outcomes.
- **Progress Tracking**: Managers can monitor project timelines and supervisee contributions, while employees can track their personal progress and achievements.
- **Multilingual Support**: Includes an Arabic translation option to ensure all team members can communicate effectively in their preferred language.

## Intended Users

- **Managers**: For overseeing projects, matching employee skills to project needs, and tracking team progress.
- **Employees**: For viewing personal project involvement, progress, and receiving feedback.

This system is intended to streamline project management processes, enhance team collaboration, and support a multilingual workforce to foster an inclusive corporate culture.


## Setup Guide

1. Create a folder on your desktop 
2. Open this folder with VSCODE
3. Clone the project into the folder
4. Change password of SQL to reflect you own password
5. Open CMD LINE
6. Cd into 430
```bash
cd 430
```
6. Create a virtual environment  
```bash
py -3 -m venv venv
```
```bash
venv\Scripts\activate
```

7- run 
```bash
pip install -r requirements.txt
```

8-set app430 to be the default flask app 
```bash
set FLASK_APP=app430.py
```

9- run 
```bash
flask run
```

