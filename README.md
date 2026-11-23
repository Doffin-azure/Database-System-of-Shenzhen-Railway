# Shenzhen Railway Database System

A SUSTech CS307 course project for managing railway stations and passenger records through a Flask web application backed by MySQL.

## Explore or run locally

The [project report](paper.pdf) describes the database design and the application. The server is in [project](project), with [models](project/app/models.py), [migrations](project/migrations), and [tests](project/tests).

From the repository root, install the dependencies in a Python virtual environment:

```bash
cd project
python -m pip install -r requirements.txt
```

Set up local MySQL and export `DATABASE_URL` and a private `SECRET_KEY` in your shell using [.env.example](.env.example) as a reference. From `project/`, run `flask --app run db upgrade`, then `python run.py`. You may need the MySQL client development libraries to install `mysqlclient`.

Tests require `TEST_DATABASE_URL` for a separate disposable database.
