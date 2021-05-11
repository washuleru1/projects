import logging, os
import googleapiclient
from googleapiclient import discovery
from google.oauth2 import service_account
from google.cloud import pubsub_v1
from google.auth import jwt

logging.basicConfig(level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class ProjectModule():

    def __init__(self, status):
        self.__status = status
        try:
            self.__envs = ['dev', 'uat']
            self.__topic_path = os.environ['TOPIC_PATH']
            logger.info('AUTENTICANDO PARA USO DE APIS DE GOOGLE')
            audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
            credentials_publisher = jwt.Credentials.from_service_account_file(
                filename=os.environ['SERVICE_ACCOUNT_PUBSUB'], audience=audience
            )
            self.__publisher = pubsub_v1.PublisherClient(credentials=credentials_publisher)
            credentials = service_account.Credentials.from_service_account_file(filename=os.environ['SERVICE_ACCOUNT_IAM'])
            self.service = googleapiclient.discovery.build('cloudresourcemanager', 'v1', credentials=credentials, cache_discovery=False)
            logger.info('AUTENTICADO')
        except Exception as e:
            logger.error('Exception {} '.format(e))

    def __getProjects(self):
        try:
            projectList = []
            logger.info('OBTENIENDO LOS PROYECTOS')
            projects = self.service.projects().list().execute()['projects']
            [projectList.append(project) for project in projects if project.get('lifecycleState') == 'ACTIVE']
            logger.info('Proyectos obtenidos')
            return projectList
        except Exception as e:
            logger.error('Exception: {} '.format(e))
            projectList = []
        finally:
            return projectList

    def __publishPubSub(self, projectID):
        try:
            payload = {
                'project_id':projectID,
                'cloudsql_status':self.__status
            }
            logger.info('Publishing to topic this event: {}'.format(payload))
            future = self.__publisher.publish(
                self.__topic_path, str(payload).encode('utf-8')
            )
            logger.info(future.result())
        except Exception as e:
            logger.error(e)

    def filterProjectsByLabels(self):
        projects = self.__getProjects()
        for project in projects:
            try:
                if project.get('labels', 'default').get('env', 'default') in self.__envs:
                    logger.info('El proyecto: {} cumple con las condiciones para apagar la(s) instancia(s) de cloudsql'.format(project.get('projectId')))
                    self.__publishPubSub(project.get('projectId'))          
            except Exception as e:
                print('Proyecto: {} no tiene label necesario'.format(project.get('projectId')))
                

             