# Shenzhen Railway Database System

A SUSTech CS307 course project for managing railway stations and passenger records through a Flask web application backed by MySQL.

## Explore or run locally

The [project report](paper.pdf) describes the database design and the application. The server is in [project](project), with [models](project/app/models.py), [migrations](project/migrations), and [tests](project/tests).

From the repository root, install the dependencies in a Python virtual environment:

```bash
cd project
python -m pip install -r requirements.txt
```

Set up a local MySQL instance and adapt the [database configuration](project/config.py) before running `python run.py` from `project/`. You may need the MySQL client development libraries to install `mysqlclient`.
