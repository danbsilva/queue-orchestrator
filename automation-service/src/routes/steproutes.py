from src import resources


class StepRoutes:

    def __init__(self, api):

        # Endpoints for steps
        api.add_resource(resources.StepsResource, '/<automation_uuid>/steps/',
                         methods=['POST', 'GET'])
        api.add_resource(resources.StepResource, '/steps/<step_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])


