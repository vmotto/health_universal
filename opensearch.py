import requests
import json
import logging
import os


class OpenSearch:
    headers = {'Content-Type': 'application/json'}

    def __init__(self):
        self.host = "search-managed-insights-dev-px5ivomxqodsqayklrvsk3g2uu.us-east-1.es.amazonaws.com"
        self.username = os.environ['OS_USERNAME']
        self.key = os.environ['OS_KEY']


    def send_to_opensearch(self, index, data):
        url = f'https://{self.host}/{index}/_doc/?pipeline=indexed_at'
        try:
            result = requests.post(url, verify=False, auth=(self.username, self.key), headers=self.headers, data=json.dumps(data))
            if result.status_code == 200:
                logging.info("Data successfully sent to OpenSearch")
                logging.debug("Data sent to Opensearch")
                logging.debug(data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
