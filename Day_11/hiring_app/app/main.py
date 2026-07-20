from fastapi import FastAPI

app = FastAPI()

# @app.get("/")
# def home():
#     return {"Message": "Welcome to FastAPI"}

# '''
# @app.get("/")

# This is called a decorator.
# It tells FastAPI:
# "When someone sends a GET request to /, execute the function below."

# home() - python func
# return - FastAPI automatically converts the python dict into json
# '''


# @app.post("/jobs")
# def create_jobs():
#     return {"message":"Job created"}

# @app.get("/jobs")
# def get_jobs():
#     return {"message":"List of jobs"}

# @app.put("/jobs")
# def update_job():
#     return {"message" : "Job updated hogyi dost"}

# @app.patch("/jobs")
# def update_salary():
#     return {"message" : "Salary Updated"}

# @app.delete("/jobs")
# def delete():
#     return {"message" : "Job deleted"}

# #Path parameters - /jobs/1
# @app.get("/jobs/{job_id}")
# def get_job_path(job_id:int):
#     return {"job_id" : job_id}

# #Query parameters - http://127.0.0.1:8000/jobs?location=Chennai
# #searching, Filteration, sorting, specific search

# @app.get("/jobsQuery")
# def get_jobs_query(location:str):
#     return {"location" : location}

# @app.get("/jobslocation")
# def get_jobs_location(location: str, experience: int):
#     return {
#         "location": location,
#         "experience" : 3
#     }


# pyrefly: ignore [missing-import]
from app.models.job import Job
from app.schemas.job_schema import JobCreate

@app.get('/')
def home():
    job = Job(
        title = "Python Dev",
        des = "Develop fastAPI appl",
        salary = 750000,
        company = "ABC Technologies"
    )
    job_schema = JobCreate(
        title = job.title,
        description=job.des,
        salary=job.salary,
        company=job.company
    )
    return {
        "Model": job.__dict__,
        "Schema": job_schema.model_dump()
    }

@app.post("/jobs")
def create_jobs(job: JobCreate):
    #Convert schema to model
    job_model = Job(
        title = job.title,
        des = job.description,
        salary = job.salary,
        company = job.company
    )

    return {
        "message": "job Created successfully",
        "data": job_model.__dict__
    }