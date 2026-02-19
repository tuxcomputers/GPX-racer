# Agents.md

This is an basic agents.md file used to provide a baseline for a project developed in Python / Streamlit.  
This has not been optimised for any specific project, instead intended to be dropped into a new project to get started. 
As such it is not intended to override any other instruction in the project.

## Code Style
* Code should be written in Python 3.12 or later
* Type hints should be used where possible
* Follow PEP 8 style guide for code formatting
* Use meaningful variable and function names
* Keep functions small and focused on a single task
* Use docstrings to document functions and classes
* Use exception handling to handle errors gracefully
* Use logging to track program execution
* Use unit tests to ensure code quality
* Use ruff for linting

## Technology
* Use Streamlit unless a different approach is required.
* Build a multi-page application, even if not required for initial development. Additional pages may be added later. 
* Use sqlite when persistence is required.
* If multiple workflows are required, they should be implemented as seperate streamlit pages. 

## Deployment
* Application will be run locally using Docker, and kubernetes for deployment.
* Authentication will be handled by an downstream proxy server. All users are assumed to be authenticated.
* Auth group membership will be added later, but will be visible to the application via a HTTP header. 

## Local Development
* scripts should be created under the /scripts directory to simplify running the application locally.
* a run.sh script should be created which will build and run the application via docker.

## Proof of Concept
* This project will be a proof of concept level application. As such it will be optimised for a ideation. 
* Use Libraries to simplify the code
  * Aim for well supported, maintained / documented libraries, that are popular in the python ecosystem.

