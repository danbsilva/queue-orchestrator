from src.controllers.stepcontroller import StepResource, StepsResource


class StepRoutes:

    def __init__(self, api):

        # Endpoints for steps
        api.add_resource(StepsResource, '/<automation_uuid>/steps/',
                         methods=['POST', 'GET'])
        api.add_resource(StepResource, '/steps/<step_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])


