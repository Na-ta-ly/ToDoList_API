#!/usr/bin/env python3

# Tests for ToDoList API

from json import loads

import requests

base_url = 'http://localhost:5000'

def test_get_tasks():
    url = base_url + '/tasks'
    print('test endpoint /tasks  GET method')

    response_1 = requests.request('GET', url)

    # Response structure check: list of jsonified Task objects
    data = loads(response_1.text)
    check = True
    if isinstance(data, list):
        for item in data:
            if not (isinstance(item, dict) and
                    'id' in item.keys() and
                    'title' in item.keys() and
                    'description' in item.keys() and
                    'created_at' in item.keys() and
                    'updated_at' in item.keys()):
                check = False
        if check:
            msg = 'PASS: Right response body structure'
        else:
            msg = 'FAIL: Wrong single object structure!!!'
    else:
        msg = 'FAIL: Wrong body structure!!!'
    print(msg)

    # Response equality check
    response_2 = requests.request('GET', url)
    if response_1.text == response_2.text:
        print('PASS: Bodies are equal')
    else:
        print('FAIL: Bodies are not equal!!!')

    # Response status codes check
    if response_1.status_code == response_2.status_code == 200:
        print('PASS: Status code is right')
    else:
        print('FAIL: Status code is wrong!!!')


def test_post_tasks():
    url = base_url + '/tasks'
    print('test endpoint /tasks  POST method')

    # Response status codes check
    test_data = [({'title': 'new task 888', 'description': 'new description', 'id': 1}, 201),
                 ({'description': 'new description'}, 400),
                 ({'title': '', 'description': 'new description'}, 400),
                 ({'title': 'new task 888', 'description': 'new description'}, 409),
                 ({'title': 'new task 889'}, 201),
                 ({'title': 888, 'description': 547}, 201),
                 ({'title': 'новая задача', 'description': 'описание задачи'}, 201),
                 ({'title': 'новая задача_1', 'description': 'длинное описание\r\nи еще одна строка'}, 201),
                 ({'title': 'новая задача_2', 'description': 'длинное описание\tи еще одна строка'}, 400)]

    check = True
    for test in test_data:
        response = requests.request('POST', url, data=test[0])
        if response.status_code != test[1]:
            check = False
    if check:
        print('PASS: Status codes are right')
    else:
        print('FAIL: Status codes are wrong!!!')

    # Response structure check: jsonified Task object
    correct_data = {'title': 'new task 887', 'description': 'new description'}
    response = requests.request('POST', url, data=correct_data)
    item = loads(response.text)
    if (isinstance(item, dict) and
            'id' in item.keys() and
            'title' in item.keys() and
            'description' in item.keys() and
            'created_at' in item.keys() and
            'updated_at' in item.keys()):
        print('PASS: Right response body structure')
    else:
        print('FAIL: Wrong response body structure!!!')

    # Response functionality check: new data added
    check = False
    response_text = loads(requests.request('GET', url).text)
    for item in response_text:
        if (isinstance(item, dict) and
                correct_data.get('title', '') == item.get('title', '') and
                correct_data.get('description', '') == item.get('description', '')):
            check = True
    if check:
        print('PASS: Request functions correctly')
    else:
        print("FAIL: Request doesn't work")


def test_put_tasks():
    url = base_url + '/tasks'
    print('test endpoint /tasks  PUT method')

    # Response status codes check
    response_1 = requests.request('PUT', url)

    if response_1.status_code == 405:
        print('PASS: Status code is right')
    else:
        print('FAIL: Status code is wrong!!!')


def test_get_tasks_id():
    url = base_url + '/tasks/'
    print('test endpoint /tasks/<id>  GET method')

    new_id = loads(requests.request('POST', base_url + '/tasks',
                                    data={'title': 'new task 877'}).text).get('id', 0)
    response_1 = requests.request('GET', url + str(new_id))

    # Response structure check: jsonified Task object
    item = loads(response_1.text)
    if (isinstance(item, dict) and
            'id' in item.keys() and
            'title' in item.keys() and
            'description' in item.keys() and
            'created_at' in item.keys() and
            'updated_at' in item.keys()):
        print('PASS: Right response body structure')
    else:
        print('FAIL: Wrong response body structure!!!')

    # Response equality check
    response_2 = requests.request('GET', url + str(new_id))
    if response_1.text == response_2.text:
        print('PASS: Bodies are equal')
    else:
        print('FAIL: Bodies are not equal!!!')

    # Response status codes check
    if response_1.status_code == response_2.status_code == 200:
        print('PASS: Status code is right')
    else:
        print('FAIL: Status code is wrong!!!')

    response_3 = requests.request('GET', url + '999')
    if response_3.status_code == 404:
        print('PASS: Status code for not existing data is right')
    else:
        print('FAIL: Status code for not existing data is wrong!!!')


def test_put_tasks_id():
    url = base_url + '/tasks/'
    print('test endpoint /tasks/<id>  PUT method')

    new_id = loads(requests.request('POST', base_url + '/tasks',
                                    data={'title': 'new task 777'}).text).get('id', 0)

    # structure: task_id, data for request, status code
    test_data = [(str(new_id), {'title': 'new task 888', 'description': 'changed description'}, 200),
                 ('99', {'title': 'new task 888', 'description': 'new description'}, 404),
                 (str(new_id), {}, 400),
                 (str(new_id), {'description': 'changed description'}, 200)]

    # Correct request
    test = test_data[0]
    response_before = requests.request('GET', url + test[0])
    target_response = requests.request('PUT', url + test[0], data=test[1])
    response_after = requests.request('GET', url + test[0])

    # Response functionality check: data were changed
    data_initial = loads(response_before.text)
    data_final = loads(response_after.text)
    if (isinstance(data_initial, dict) and isinstance(data_final, dict) and
            data_initial.get('id', 0) == data_final.get('id', 0) and
            test[1].get('title', '') == data_final.get('title', '') and
            test[1].get('description', '') == data_final.get('description', '')):
        print('PASS: Request functions correctly')
    else:
        print("FAIL: Request doesn't work")
    back_response = requests.request('PUT', url + test[0], data=data_initial)

    # Response structure check: jsonified Task object
    item = loads(back_response.text)
    if (isinstance(item, dict) and
            'id' in item.keys() and
            'title' in item.keys() and
            'description' in item.keys() and
            'created_at' in item.keys() and
            'updated_at' in item.keys()):
        print('PASS: Right response body structure')
    else:
        print('FAIL: Wrong response body structure!!!')

    # Response status codes check
    if back_response.status_code == 200:
        print('PASS: Status code for correct request is right')
    else:
        print('FAIL: Status code for correct request is wrong!!!')

    check = True
    for test in test_data[1:]:
        response = requests.request('PUT', url + test[0], data=test[1])
        if response.status_code != test[2]:
            check = False
    if check:
        print('PASS: Status codes are right')
    else:
        print('FAIL: Status codes are wrong!!!')


def test_delete_tasks_id():
    url = base_url + '/tasks/'
    print('test endpoint /tasks/<id>  DELETE method')

    response_post = requests.request('POST', base_url + '/tasks',
                                     data={'title': 'unique_title',
                                           'description': 'new description'})
    task_id = loads(response_post.text).get('id', None)

    assert task_id is not None, "Task wasn't created"
    response_before = requests.request('GET', url + str(task_id))
    target_response = requests.request('DELETE', url + str(task_id))
    response_after = requests.request('GET', url + str(task_id))

    # Response functionality check: data were deleted
    if response_before.status_code == 200 and response_after.status_code == 404:
        print('PASS: Request works correctly')
    else:
        print("FAIL: Request doesn't work!!!")

    item = loads(target_response.text)
    if isinstance(item, dict) and 'msg' in item.keys():
        print('PASS: Right response body structure')
    else:
        print('FAIL: Wrong response body structure!!!')

    # Response status codes check
    if target_response.status_code == 200:
        print('PASS: Status code for correct request is right')
    else:
        print('FAIL: Status code for correct request is wrong!!!')

    response_3 = requests.request('DELETE', url + '999')
    if response_3.status_code == 404:
        print('PASS: Status code for not existing data is right')
    else:
        print('FAIL: Status code for not existing data is wrong!!!')
    pass


def test_post_tasks_id():
    url = base_url + '/tasks/'
    print('test endpoint /tasks/<id>  POST method')

    # Response status codes check
    response_1 = requests.request('POST', url + '1')

    if response_1.status_code == 405:
        print('PASS: Status code is right')
    else:
        print('FAIL: Status code is wrong!!!')


def cleaning():
    titles_for_clean = ['new task 888', 'new task 889', '888', 'new task 887', 'новая задача',
                        'новая задача_1', 'новая задача_2', 'new task 877', 'new task 777']
    all_tasks = loads(requests.request('GET', base_url + '/tasks').text)
    for task in all_tasks:
        if task['title'] in titles_for_clean:
            requests.request('DELETE', base_url + '/tasks/' + str(task['id']))
    print('Base was cleaned')


if __name__ == '__main__':
    test_post_tasks()
    print('------------------')
    test_get_tasks()
    print('------------------')
    test_put_tasks()
    print('------------------')
    print()
    print('------------------')
    test_get_tasks_id()
    print('------------------')
    test_put_tasks_id()
    print('------------------')
    test_delete_tasks_id()
    print('------------------')
    test_post_tasks_id()
    print('------------------')
    print()
    cleaning()
