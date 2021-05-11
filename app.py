from fastapi import FastAPI
from pydantic import BaseModel
import logging
from modules.projectmodule import ProjectModule


logging.basicConfig(level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

class StatusModel(BaseModel):
    cloudsql_status: str

@app.get("/")
def healthcheck():
    return {"status":"Servicio Corriendo"}
    
@app.post("/api/v1/projects")
def changeCloudSqlStatus(statusModel: StatusModel):
    body = statusModel.dict()
    projectModule = ProjectModule(body.get('cloudsql_status'))
    projectModule.filterProjectsByLabels()
    return {"status":"ok"} 