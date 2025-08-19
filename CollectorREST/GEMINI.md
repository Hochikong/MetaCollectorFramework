# CollectorREST Project

## Project Overview

This project, "CollectorREST," is a FastAPI-based web service that acts as a backend for the "MetaCollectorFramework" (MCF), a data collection framework. The service provides a RESTful API for managing data collection tasks and controlling collector agents. It utilizes SQLAlchemy for database operations with a MySQL backend and Pydantic for data validation and serialization.

The architecture is layered, separating concerns into controllers, domains, services, repositories, and entities. This structure promotes modularity and maintainability.

## Key Functionalities

*   **Task Management:**
    *   Receive single or bulk tasks (URLs) for data collection.
    *   Process tasks using "drivers" tailored for specific websites or data sources.
    *   Store and track task status in a database.
    *   Manage task execution through a task queue.

*   **MCF Agent Management:**
    *   Create, stop, and monitor MCF agents.
    *   Launch and control remote Chrome instances for web scraping.
    *   Execute collection drivers within the agents.

## Building and Running

To run the application, use the following command in the project's root directory:

```bash
uvicorn CollectorREST.main:app --reload --log-config .\uvicorn_conf.yaml
```

**Note:** You may need to create a `uvicorn_conf.yaml` file for logging configuration if it doesn't exist.

## Development Conventions

*   **Framework:** The project is built using the [FastAPI](https://fastapi.tiangolo.com/) web framework.
*   **Database:** [SQLAlchemy](https://www.sqlalchemy.org/) is used as the ORM for interacting with the MySQL database.
*   **Data Validation:** [Pydantic](https://pydantic-docs.helpmanual.io/) is used for data validation and serialization.
*   **Architecture:** The project follows a layered architecture, separating concerns into:
    *   `controller`: API endpoints.
    *   `domains`: Pydantic models for request/response data.
    *   `entities`: SQLAlchemy models for database tables.
    *   `services`: Business logic.
    *   `repository`: Data access layer.
*   **Dependencies:** Project dependencies are likely managed in a `requirements.txt` file (though not explicitly found, this is a standard convention for Python projects).
