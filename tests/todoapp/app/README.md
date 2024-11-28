# Nexio Application Setup

## Requirements
- Python 3.8 or later
- [Aerich](https://github.com/tortoise/aerich) for migrations
- [Uvicorn](https://www.uvicorn.org/) for running the app

## Setup Instructions

1. Install the required dependencies:
   ```bash
   ```
Migrate the database: Run the following command to create the initial migration files:

```bash

aerich init -t settings.migration
Then, run the following command to apply the migrations to the database:
```
bash
```
aerich migrate
aerich upgrade
```
To start the application, use Uvicorn:

``bash

uvicorn main:app --reload
```
