# Queue Orquestration

## Description
<p align="justify">This project is a simple implementation of a queue orquestration system. It was developed using the Python(Flask) programming language and the KAFKA message broker.</p>

## Services
<p align="justify">The project is composed of the following services:</p>

### FLASK - PYTHON3
- **api-gateway**: responsible for managing the requests of the users
- **auth**: responsible for managing the authentication of the users
- **automations**: responsible for managing the automations of the users
- **logs**: responsible for managing the logs of the users
- **notifications**: responsible for managing the notifications of the users

## Architecture
<p align="justify">The project is composed of the following architecture:</p>

### POSTGRESQL
- **dbservices**: responsible for managing the database of api-gateway
- **dbusers**: responsible for managing the database of users
- **dbautomations**: responsible for managing the database of automations
- **dblogs**: responsible for managing the database of logs



## Requirements
- Docker

## Installation
<p align="justify">To install the project, you must follow the steps below:</p>

1. Clone the repository
```bash
git clone
```
## Usage
<p align="justify">To use the project, you must follow the steps below:</p>

1. Enter the project folder
```bash
cd queue-orquestration
```

2. Execute the Docker Compose
```bash
docker-compose up -d
```
<p align="justify">The command above will create the containers and start the project. The containers created are:</p>

- **zoopkeeper**: responsible for managing the KAFKA cluster
- **kafka**: responsible for managing the KAFKA cluster
- **control-center**: responsible for managing the KAFKA cluster
- **topic-creator**: responsible for creating the topics of the KAFKA cluster
- **redis**: responsible for managing the Redis cluster
- **dbservices**: responsible for managing the database of api-gateway
- **api-gateway**: responsible for managing the api-gateway
- **dbusers**: responsible for managing the database of users
- **auth**: responsible for managing the authentication service
- **dbautomations**: responsible for managing the database of automations
- **automations**: responsible for managing the automations service
- **dblogs**: responsible for managing the database of logs
- **logs**: responsible for managing the logs service
- **notifications**: responsible for managing the notifications service

3. Access the api-gateway container
```bash
docker exec -it api-gateway bash
```

4. Create the migrations of the api-gateway
```bash
flask db init && flask db migrate && flask db upgrade
```

5. Create the migrations of the users
```bash
flask db init && flask db migrate && flask db upgrade
```

6. Create the migrations of the automations
```bash
flask db init && flask db migrate && flask db upgrade
```

7. Create the migrations of the logs
```bash
flask db init && flask db migrate && flask db upgrade
```

8. Restart the api-gateway container
```bash
docker restart api-gateway
```

9. Restart the users container
```bash
docker restart users
```

10. Restart the automations container
```bash
docker restart automations
```

11. Restart the logs container
```bash
docker restart logs
```

12. Restart the notifications container
```bash
docker restart notifications
```





