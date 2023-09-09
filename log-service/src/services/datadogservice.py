from decouple import config as config_env
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

class DataDogService:

        def __init__(self):
            self.configuration = Configuration()
            self.configuration.api_key["apiKeyAuth"] = config_env('DD_API_KEY')
            self.configuration.server_variables["site"] = config_env('DD_SITE')

        def submit_log(self, msg):
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource=msg['service_name'],
                        ddtags=f"env:{config_env('FLASK_ENV')},logs",
                        hostname=msg['service_name'],
                        datetime=msg['datetime'],
                        service=msg['service_name'],
                        module_name=msg['module_name'],
                        function_name=msg['function_name'],
                        message=msg['message'],
                        status=msg['level'],
                        trace_id=msg['transaction_id'],

                    ),
                ]
            )
            with ApiClient(self.configuration) as api_client:
                api_instance = LogsApi(api_client)
                response = api_instance.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)
