import os
import datetime
import json

def load_tasks():
    if os.path.exists('tasks.json') and os.path.getsize('tasks.json') > 0:
        with open('tasks.json','r') as file:
            all_tasks = json.load(file)
            return all_tasks

def save_tasks(tasks):
    with open('tasks.json','w') as file:
       json.dump(tasks, file, indent=2)
    print('Tasks saved successfully!')

def parse_input(input_string):
    words = input_string.split()
    subject = ''
    task = ''
    due_date = ''
    global id
    if "study" in words:
        study_index = words.index("study")
        subject = words[study_index + 1]
        task = ' '.join(words[study_index + 2:])  # until "by"
        

    if "by" in words:
        by_index = words.index("by")
        due_date = words[by_index + 1]
        task = ' '.join(words[study_index + 2:by_index])  # exclude date
    
    return {
        "id": len(tasks) + 1,
        "subject": subject,
        "task": task,
        "due_date": due_date,
        "estimated_time": "1h",
        "status": "pending"
    }



def get_tasks_for_today():
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    today_task = []
    for task in tasks:
        if task['due_date'] == str(today_date):
            today_task.append(task)
    return today_task

def mark_task_complete(task_id):
    global tasks
    for task in tasks:
        if task['id'] == task_id:

            task['status'] = 'completed'
    save_tasks(tasks)

def get_pending_tasks():
    pending_task = []
    for task in tasks:
        if task['status'] == 'pending':
            pending_task.append(task)
    return pending_task

def suggest_schedule(time_available):
    suggest_schedule = []
    for task in tasks:
        if task['status'] == 'pending':
            task_time = task['estimated_time']
            task_time = int(task['estimated_time'].replace('h', '').strip())
            if task_time <= time_available:
                suggest_schedule.append(task)
                time_available -= task_time
    return suggest_schedule

def add_task():
    use_input = input('Enter the task: ')
    words = use_input.split()
    global tasks

    if "add" in words:
        new_task = parse_input(use_input) 
        tasks.append(new_task)
        save_tasks(tasks)

    elif "get" in words and "today" in words:
        for task in get_tasks_for_today():
            print(f"🗒️  [{task['id']}] {task['subject']} - {task['task']} (Due: {task['due_date']})")


    elif "mark" in words:
        for word in words:
            if word.isdigit():
                task_id = int(word)
                mark_task_complete(task_id)

    elif "pending" in words:
        print(get_pending_tasks())

    elif "suggest" in words:
        print(datetime.timedelta(hours=1))
        for i, word in enumerate(words):
            if word.lower() == 'hour' and i > 0 and words[i - 1].isdigit():
                time = int(words[i - 1])
                print(suggest_schedule(time))
    else:
        print("Invalid command. Try one of these:")
        print("- Add a task to study [subject] [details] by [date]")
        print("- Get today's tasks")
        print("- Mark [task ID] completed")
        print("- Show pending tasks")
        print("- Suggest for [X] hours")

                

if __name__ == "__main__":    
    tasks = load_tasks() or []
    ans = ''
    while ans != 'no':
        add_task()
        user_ans = input('Do you want to add another task? (yes/no)')
        if user_ans.lower() == 'yes':
            ans = 'yes'
        else:
            ans = 'no'
            print('Exiting the program...')
    print(load_tasks())
    print('Tasks loaded successfully!')
    
