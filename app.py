import os
import datetime
import json
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "study_planner_secret"

# Define the absolute path for tasks.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, 'tasks.json')

print(f"App started. Tasks file location: {TASKS_FILE}")

def load_tasks():
    try:
        if not os.path.exists(TASKS_FILE):
            print(f"Creating new tasks file at {TASKS_FILE}")
            with open(TASKS_FILE, 'w') as file:
                json.dump([], file)
                
        if os.path.getsize(TASKS_FILE) > 0:
            with open(TASKS_FILE, 'r') as file:
                tasks = json.load(file)
                print(f"Loaded {len(tasks)} tasks from file")
                return tasks
        else:
            print("Tasks file is empty, returning empty list")
            return []
    except Exception as e:
        print(f"ERROR loading tasks: {str(e)}")
        return []

def save_tasks(tasks):
    try:
        print(f"Attempting to save {len(tasks)} tasks to {TASKS_FILE}")
        with open(TASKS_FILE, 'w') as file:
            json.dump(tasks, file, indent=2)
        print(f"✅ Tasks saved successfully to {TASKS_FILE}")
        return True
    except Exception as e:
        print(f"❌ ERROR saving tasks: {str(e)}")
        return False

def parse_input(input_string, tasks):
    words = input_string.split()
    subject = ''
    task = ''
    due_date = ''

    if "study" in words:
        study_index = words.index("study")
        if study_index + 1 < len(words):
            subject = words[study_index + 1]
        if "by" in words:
            by_index = words.index("by")
            if by_index > study_index + 2:
                task = ' '.join(words[study_index + 2:by_index])
            if by_index + 1 < len(words):
                due_date = words[by_index + 1]
        else:
            task = ' '.join(words[study_index + 2:])
    else:
        print("❌ 'study' not found in input")

    return {
        "id": len(tasks) + 1,
        "subject": subject,
        "task": task,
        "due_date": due_date,
        "estimated_time": "1h",
        "status": "pending"
    }

def get_tasks_for_today(tasks):
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    return [task for task in tasks if task['due_date'] == today_date]

def get_pending_tasks(tasks):
    return [task for task in tasks if task['status'] == 'pending']

def suggest_schedule(tasks, available_time):
    suggest_schedule = []
    remaining_time = available_time
    
    for task in tasks:
        if task['status'] == 'pending':
            try:
                task_time = int(task['estimated_time'].replace('h', '').strip())
                if task_time <= remaining_time:
                    suggest_schedule.append(task)
                    remaining_time -= task_time
            except ValueError:
                print(f"Could not parse time from {task['estimated_time']}")
    
    return suggest_schedule, remaining_time

@app.route('/', methods=['GET', 'POST'])
def home():
    # Load tasks at the beginning of each request
    tasks = load_tasks()
    
    # Initialize variables for template
    today_tasks = []
    pending_tasks = []
    suggested_schedule = []
    remaining_time = 0
    command_result = None
    help_commands = []
    
    if request.method == 'POST':
        input_text = request.form.get('input', '').lower()
        print(f"Form submitted with input: '{input_text}'")

        if "add" in input_text:
            new_task = parse_input(input_text, tasks)
            print(f"✅ Parsed task: {new_task}")
            
            # Only add if we got valid data
            if new_task['subject'] or new_task['task']:
                tasks.append(new_task)
                
                if save_tasks(tasks):
                    command_result = f"I've added your task: {new_task['subject']} - {new_task['task']} due by {new_task['due_date']}"
                else:
                    command_result = "Sorry, I couldn't save your task. Please try again."
            else:
                command_result = "I couldn't understand that. Please use the format: add study [subject] [task] by [date]"

        elif "mark" in input_text:
            task_marked = False
            for word in input_text.split():
                if word.isdigit():
                    task_id = int(word)
                    for task in tasks:
                        if task['id'] == task_id:
                            task['status'] = 'completed'
                            task_marked = True
                            command_result = f"Great job! I've marked task #{task_id} ({task['subject']} - {task['task']}) as completed."
                            break
            
            if task_marked:
                save_tasks(tasks)
            else:
                command_result = f"I couldn't find task #{task_id}. Please check the task number and try again."

        elif "get" in input_text and "today" in input_text:
            today_tasks = get_tasks_for_today(tasks)
            if today_tasks:
                command_result = f"Found {len(today_tasks)} tasks for today."
            else:
                command_result = "You don't have any tasks scheduled for today."
        
        elif "pending" in input_text:
            pending_tasks = get_pending_tasks(tasks)
            if pending_tasks:
                command_result = f"Found {len(pending_tasks)} pending tasks."
            else:
                command_result = "You don't have any pending tasks. Well done!"
        
        elif "suggest" in input_text:
            words = input_text.split()
            for i, word in enumerate(words):
                if word.lower() == 'hour' and i > 0 and words[i - 1].isdigit():
                    available_time = int(words[i - 1])
                    suggested_schedule, remaining_time = suggest_schedule(tasks, available_time)
                    if suggested_schedule:
                        command_result = f"Suggested {len(suggested_schedule)} tasks for your {available_time}h time slot."
                    else:
                        command_result = f"I couldn't find suitable tasks for your {available_time}h time slot."
                    break
            else:
                command_result = "Please specify how many hours you have available, e.g., 'suggest 3 hour'"
        
        elif "help" in input_text:
            command_result = "Here's what I can help you with:"
            
            # Create a list of help commands for tabular display
            help_commands = [
                {"command": "add study Biology chapter 3 by Friday", "description": "Add a new task"},
                {"command": "mark 1 complete", "description": "Mark a task as completed"},
                {"command": "get today", "description": "See today's tasks"},
                {"command": "pending", "description": "See all pending tasks"},
                {"command": "suggest 3 hour", "description": "Get schedule suggestions"}
            ]        
        else:
            command_result = "I'm not sure what you're asking. Try 'help' to see what I can do."

    # Always update these lists for every request
    if not today_tasks:
        today_tasks = get_tasks_for_today(tasks)
    
    if not pending_tasks:
        pending_tasks = get_pending_tasks(tasks)

    return render_template(
        "index.html", 
        tasks=tasks,
        today_tasks=today_tasks,
        pending_tasks=pending_tasks,
        suggested_schedule=suggested_schedule,
        remaining_time=remaining_time,
        command_result=command_result,
        help_commands=help_commands
    )

if __name__ == "__main__":
    # Make sure tasks.json exists before starting the app
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as f:
            json.dump([], f)
    
    # Run the app with debugging enabled
    app.run(debug=True)