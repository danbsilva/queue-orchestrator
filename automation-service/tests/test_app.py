import json
import unittest
from src.app import create_app

main_app = create_app()


class TestAutomations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main_app.test_client()
        cls.app.testing = True
        cls.headers = {
            'Content-Type': 'application/json',
            'X-ORIGIN': 'automations'
        }
        cls.service = '/automations'

        # Data to create a new automation
        cls.data_automation = {
            "name": "Automation 0",
            "acronym": "AT0",
            "description": "Automation 0 description"
        }

        # Data to create a new step
        cls.data_step = {
            "name": "Step 0",
            "description": "Step 0 description",
            "step": 1,
            "topic": "topic_0",
            "try_count": 1
        }

        # Data to create a new item
        cls.data_item = {
          "data": {
             "key": "value"
           }
        }


    def setUp(self):
        # Delete all data from the database and re-create the tables before each test
        with main_app.app_context():
            main_app.db.drop_all()
            main_app.db.create_all()

    def tearDown(self):
        ...
        # Rollback the database session after each test
        #with main_app.app_context():
        #    main_app.db.drop_all()

    ## Tests to automations routes
    def test_post_automation(self):
        # Test to the route that creates a new automation

        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)

        self.assertEqual(response.status_code, 201)

    def test_delete_automation(self):
        # Test to the route that deletes a automation

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second delete the automation and be sure that the response is 204
        response = self.app.delete(f'{self.service}/{automation_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_automations(self):
        # Test to the route that returns all automations

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Second get all automations and be sure that the response is 200
        response = self.app.get(f'{self.service}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_automation(self):
        # Test to the route that returns a single automation

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second get the automation and be sure that the response is 200
        response = self.app.get(f'{self.service}/{automation_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_automation_not_found(self):
        # Test to the route that returns a single automation when the automation is not found

        automation_uuid = '6f53ce49-d253-4a95-8e22-aab09e67e3d5'
        response = self.app.get(f'{self.service}/{automation_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_post_automation_already_exists(self):
        # Test to the route that creates a new automation when an automation with the same acronym already exists

        # First request should be successful
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Second request with the same acronym should return 400
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        self.assertEqual(response.status_code, 400)


    # Tests to steps routes
    def test_post_step(self):
        # Test to the route that creates a new step

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_delete_step(self):
        # Test to the route that deletes a step

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        step_uuid = json.loads(response.data.decode('utf-8'))['step']['uuid']
        self.assertEqual(response.status_code, 201)

        # Third delete the step and be sure that the response is 204
        response = self.app.delete(f'{self.service}/steps/{step_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_steps(self):
        # Test to the route that returns all steps

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Third get all steps and be sure that the response is 200
        response = self.app.get(f'{self.service}/{automation_uuid}/steps/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_step(self):
        # Test to the route that returns a single step

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        step_uuid = json.loads(response.data.decode('utf-8'))['step']['uuid']
        self.assertEqual(response.status_code, 201)

        # Third get the step and be sure that the response is 200
        response = self.app.get(f'{self.service}/steps/{step_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_step_not_found(self):
        # Test to the route that returns a single step when the step is not found

        step_uuid = '6f53ce49-d253-4a95-8e22-aab09e67e3d5'
        response = self.app.get(f'{self.service}/steps/{step_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_post_step_already_exists(self):
        # Test to the route that creates a new step when a step with the same acronym already exists

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Third request with the same acronym should return 400
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 400)


    # Tests to items routes
    def test_post_item_by_automation(self):
        # Test to the route that creates a new item

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Third create an item and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/items/', json=self.data_item, headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_post_item_by_step(self):
        # Test to the route that creates a new item

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        step_uuid = json.loads(response.data.decode('utf-8'))['step']['uuid']
        self.assertEqual(response.status_code, 201)

        # Third create an item and be sure that the response is 201
        response = self.app.post(f'{self.service}/steps/{step_uuid}/items/', json=self.data_item, headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_get_items_by_automation(self):
        # Test to the route that returns all items by automation

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Third create an item and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/items/', json=self.data_item, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Fourth get all items by automation and be sure that the response is 200
        response = self.app.get(f'{self.service}/{automation_uuid}/items/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_items_by_step(self):
        # Test to the route that returns all items by step

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        step_uuid = json.loads(response.data.decode('utf-8'))['step']['uuid']
        self.assertEqual(response.status_code, 201)

        # Third create an item and be sure that the response is 201
        response = self.app.post(f'{self.service}/steps/{step_uuid}/items/', json=self.data_item, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Fourth get all items and be sure that the response is 200
        response = self.app.get(f'{self.service}/steps/{step_uuid}/items/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_item(self):
        # Test to the route that returns a single item

        # First create an automation and be sure that the response is 201
        response = self.app.post(f'{self.service}/', json=self.data_automation, headers=self.headers)
        automation_uuid = json.loads(response.data.decode('utf-8'))['automation']['uuid']
        self.assertEqual(response.status_code, 201)

        # Second create a step and be sure that the response is 201
        response = self.app.post(f'{self.service}/{automation_uuid}/steps/', json=self.data_step, headers=self.headers)
        step_uuid = json.loads(response.data.decode('utf-8'))['step']['uuid']
        self.assertEqual(response.status_code, 201)

        # Third create an item and be sure that the response is 201
        response = self.app.post(f'{self.service}/steps/{step_uuid}/items/', json=self.data_item, headers=self.headers)
        item_uuid = json.loads(response.data.decode('utf-8'))['item']['uuid']
        self.assertEqual(response.status_code, 201)

        # Fourth get the item and be sure that the response is 200
        response = self.app.get(f'{self.service}/items/{item_uuid}/', headers=self.headers)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
