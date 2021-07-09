# darqube_task
Darqube Test Task


Starting
----------

Create ``.env`` file in project root and add environment variables for application:
```sh
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=darqube
MONGO_USERS_COLLECTION=users
SECRET_KEY=test
```

Install dependencies:
```sh
pip install -r requirements.txt
```

To run the web application with hot reload use and local running mongo use:
```sh
uvicorn app.main:app --reload
```

To run the web application with docker-compose use:
```sh
 docker-compose up 
```

Tests
----------
All tests for this project are located in the tests/ folder.

To run all tests, use pytest
```sh
  pytest
```

Route docs
----------
Route docs are available at /docs

Project structure
----------
```sh
  app
├── api              - web part.
│   ├── dependencies - routes dependecies.
│   ├── errors       - errors for routes.
│   └── routes       - routes.
├── core             - configuration and startup/shutdown events.
├── db               - db files.
│   └── repositories - repository for user model.
├── models           - pydantic ( main)  models.
│   └── schemas      - request/response schemas.
├── resources        - errors messages.
├── services         - business /security / authentication logic.
└── main.py          - main file
tests
├── test_models      - models/schemas tests.
├── test_repositories - repositories tests.
├── test_routes      - routes tests.

```
