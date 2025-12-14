# Python Docker Manager

This is a Python application that connects to Docker Desktop to manage Docker containers.

## Prerequisites

- Docker Desktop installed and running
- Python 3.x

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Local Execution

Run the script directly:
```
python main.py
```

### Running with Docker

To run the application in a Docker container:

1. Build the image:
   ```
   docker build -t docker-manager .
   ```

2. Run the container with access to the Docker socket:
   ```
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker-manager
   ```

Note: On Windows, the Docker socket path may be different (e.g., `//./pipe/docker_engine`). Ensure Docker Desktop is running.

This will list all running containers.

## Features

- List running containers
  (Placeholder for more features)