# Shenzhen Railway Database System

A course project for SUSTech's [CS307 Principles of Database Systems](https://mirrors.sustech.edu.cn/courses/syllabus/html/CS307.html). It uses MySQL and Flask to manage railway stations, lines, and passenger records.

## Explore or run locally

The [project report](paper.pdf) describes the database design and the application. The server is in [project](project), with [models](project/app/models.py), [migrations](project/migrations), and [tests](project/tests).

From the repository root, install the dependencies in a Python virtual environment:

```bash
cd project
python -m pip install -r requirements.txt
```

Create a local MySQL database and export `DATABASE_URL` and a private `SECRET_KEY` in your shell using [.env.example](.env.example) as a reference. From `project/`, run `flask --app run init-db` to create the tables, then `python run.py`. You may need the MySQL client development libraries to install `mysqlclient`.

To run the tests, set `TEST_DATABASE_URL` to a separate MySQL database and run `python -m unittest discover -s tests` from `project/`.
