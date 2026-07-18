import time
import json
import os
from crewai import Agent, Task, Crew

# Ensure the directory exists for the worker
if not os.path.exists("task_queue"):
    os.makedirs("task_queue")

def run_worker():
    print("Worker watching for tasks...")
    while True:
        tasks = [f for f in os.listdir("task_queue") if f.endswith(".json")]
        for task_file in tasks:
            path = f"task_queue/{task_file}"
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                
                print(f"Processing task: {task_file}")
                # CrewAI logic isolated from FastAPI
                analyst = Agent(role="Expert Electrician", goal="Solve issues", backstory="Expert", llm="gpt-4o-mini")
                t = Task(description=f"Issue: {data['issue_description']}", expected_output="Summary", agent=analyst)
                Crew(agents=[analyst], tasks=[t]).kickoff()
                
                os.remove(path)
                print(f"Completed job: {task_file}")
            except Exception as e:
                print(f"Error processing {task_file}: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run_worker()
