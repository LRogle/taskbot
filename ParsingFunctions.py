import subprocess
import json
import datetime


def parsin_json():
    """Take the list of all task and find only the task with status:pending. return list"""
    cmd = "task export"
    completed_process = subprocess.run(args=cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    json_dict = json.loads(completed_process.stdout)
    pending_task = []
    completed_task = []
    deleted_task = []
    recurring_task = []
    waiting_task = []
    for iterator in json_dict:
        if iterator['status'] == 'pending':
            pending_task.append(dict(iterator))
        elif iterator['status'] == 'completed':
            completed_task.append(dict(iterator))
        elif iterator['status'] == 'deleted':
            deleted_task.append(dict(iterator))
        elif iterator['status'] == 'recurring':
            recurring_task.append(dict(iterator))
        elif iterator['status'] == 'waiting':
            waiting_task.append(dict(iterator))
    all_task = [pending_task, completed_task, deleted_task, recurring_task, waiting_task]
    return all_task


def parsing_date(date_format):
    Y = int(date_format[0:4])
    M = int(date_format[4:6])
    D = int(date_format[6:8])
    h = int(date_format[9:11])
    m = int(date_format[11:13])
    s = int(date_format[13:15])
    date = str(datetime.datetime(Y, M, D, h, m, s))
    return date


def find_task(task_number):
    """Find the task identified in the list of pending task. return list of dictionary"""
    all_task_list = parsin_json()
    task_list = all_task_list[0]
    task = {}
    for flowing_task in task_list:
        if flowing_task['id'] == int(task_number):
            task = [flowing_task]
    return task


def select_output(task_list):
    message_out = ''
    date_tuple = ('entry', 'end', 'due', 'wait', 'until', 'start', 'modified')
    string_tuple = ('description', 'recur', 'id', 'tags', 'project')
    MAX_LENGTH = 2048
    message_list = []
    for flowing_dict_task in task_list:
        message_out = message_out + '\n'
        if len(message_out) <= MAX_LENGTH:
            for key in flowing_dict_task:
                for flow_val in date_tuple:
                    if key == flow_val:
                        message_out = '{}<b>{}</b>:\t{}\n'.format(message_out, key, parsing_date(str(flowing_dict_task[key])))
                for flow_val in string_tuple:
                    if key == flow_val:
                        message_out = '{}<b>{}</b>:\t{}\n'.format(message_out, key, str(flowing_dict_task[key]))
                if key == 'annotations':
                    for iterator in flowing_dict_task['annotations']:
                        for key in iterator:
                            if key == 'entry':
                                message_out = '{}<b>{} annotations</b>:\t{}\n'.format(message_out, key, parsing_date(str(iterator[key])))
                            elif key == 'description':
                                message_out = '{}<b>{} annotations</b>:\t{}\n'.format(message_out, key, str(iterator[key]))
                else:
                    pass
        else:
            message_list.append(message_out)
            message_out = ''
    message_list.append(message_out)
    return message_list