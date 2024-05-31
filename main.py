#!/usr/bin/env python3

# Main script for ToDoList API

import logging
from datetime import datetime

from flask import Flask, request, make_response, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists

from flask_swagger_ui import get_swaggerui_blueprint

from config import Config
from base_init import create_new_database, Task

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='flask_app.log'
)

swaggerui_blueprint = get_swaggerui_blueprint(Config.SWAGGER_URL,
                                              Config.API_URL,
                                              config={'app_name': 'ToDoList'})

db = SQLAlchemy(app)
with app.app_context():
    if not database_exists(Config.SQLALCHEMY_DATABASE_URI):
        create_new_database(Config.SQLALCHEMY_DATABASE_URI)
        app.logger.info('new database was created at %s', Config.SQLALCHEMY_DATABASE_URI)


@app.route('/tasks', methods=['GET', 'POST'])
def tasks_list() -> Response:
    if request.method == 'POST':
        # create new task and show it
        data = request.values
        title = str(data.get('title', ''))
        if title != '':
            try:
                if db.session.query(Task).filter(Task.title == title).first():
                    response = make_response({'msg': "Task with such title already exists"}, 409)
                    app.logger.debug('task with title %s already exists', title)
                else:
                    try:
                        task = Task(title=title, description=str(data.get('description', '')),
                                    created_at=datetime.now(), updated_at=datetime.now())
                        db.session.add(task)
                        db.session.commit()
                        result_task = db.session.query(Task).filter(Task.title == title).first()
                        response = make_response(result_task.to_json(), 201)
                        app.logger.info('%s task successfully created', task.title)
                    except ValueError as error:
                        response = make_response({'msg': error.args}, 400)
                        app.logger.debug('for task %s were given insufficient values', title)
                        return response
            except OperationalError as error:
                response = make_response({'msg': error.args}, 503)
                app.logger.error('connect with database was lost')
                return response
        else:
            response = make_response({'msg': "Request has no 'title' data"}, 400)
            app.logger.debug("request has no title data")

    elif request.method == 'GET':
        # show list of all tasks
        try:
            task_list = db.session.query(Task).order_by(Task.id).all()
            response = make_response([item.to_json() for item in task_list], 200)
            app.logger.debug('list of tasks was requested')
        except OperationalError as error:
            response = make_response({'msg': error.args}, 503)
            app.logger.error('connect with database was lost')
            return response
    else:
        # method doesn't defined
        response = make_response({'msg': "Request method isn't defined"}, 405)
        app.logger.debug('undefined method for /tasks was requested')
    return response


@app.route('/tasks/<id>', methods=['GET', 'PUT', 'DELETE'])
def tasks_operations(id: int) -> Response:
    try:
        task = db.session.query(Task).get_or_404(id)
        if request.method == 'PUT':
            # update existing task
            data = request.values
            if not data.get('title', 0) and not data.get('description', 0):
                response = make_response({'msg': "Request hasn't 'title' or 'description' data"}, 400)
                app.logger.debug('for update task %s not enough data', task.title)
                return response

            try:
                task.title = str(data.get('title', 0) or task.title)
                task.description = str(data.get('description', 0) or task.description)
                task.updated_at = datetime.now()
                db.session.commit()
                response = make_response(task.to_json(), 200)
                app.logger.info('%s task successfully updated', task.title)
            except ValueError as error:
                response = make_response({'msg': error}, 400)
                app.logger.debug('for task %s were given insufficient values', task.title)
                return response

        elif request.method == 'DELETE':
            # delete existing task
            db.session.delete(task)
            db.session.commit()
            response = make_response({'msg': "Task successfully deleted"}, 200)
            app.logger.info('%s task successfully deleted', task.title)
            return response

        elif request.method == 'GET':
            # return existing task
            response = make_response(task.to_json(), 200)
            app.logger.debug('task %s info was requested', task.title)

        else:
            # method doesn't defined
            response = make_response({'msg': "Request method isn't defined"}, 405)
            app.logger.debug('undefined method for /tasks/<id> was requested')
        return response

    except OperationalError as error:
        response = make_response({'msg': error.args}, 503)
        app.logger.error('connect with database was lost')
        return response


if __name__ == '__main__':
    app.register_blueprint(swaggerui_blueprint)
    app.run(debug=True)
