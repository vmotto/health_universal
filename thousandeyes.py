import requests
import os

class ThousandEyes:

    def __init__(self):
        self.host = "api.thousandeyes.com"
        self.username = os.environ['TE_USERNAME']
        self.key = os.environ['TE_KEY']
        self.event_id = None
        self.test_label_list = []
        self.rule_expression = None
        self.test_type = None
        self.agent_list = []
        self.test_targets_description = None
        self.date_start = None
        self.rule_name = None
        self.test_id = None
        self.alert_id = None
        self.rule_id = None
        self.permalink = None
        self.test_name = None
        self.event_type = None
        self.agent_ids_list = []
        self.first_agent_id = None
        self.first_agent_name = None
        self.first_metrics_at_start = None
        self.monitors = []
        self.agents_list = []
        self.interval = None
        self.alert_rules_list = []
        self.active_agent_list = []
        self.active_agent_ids = []
        self.alert_active = None

    def parse_event_data(self, event_data: object) -> object:
        self.event_id = event_data['eventId']
        self.test_label_list = event_data['alert']['testLabels']
        self.rule_expression = event_data['alert']['ruleExpression']
        self.test_type = event_data['alert']['type']
        self.agent_list = event_data['alert']['agents']
        self.test_targets_description = event_data['alert']['testTargetsDescription']
        self.date_start = event_data['alert']['dateStart']
        self.rule_name = event_data['alert']['ruleName']
        self.test_id = event_data['alert']['testId']
        self.alert_id = event_data['alert']['alertId']
        self.rule_id = event_data['alert']['ruleId']
        self.permalink = event_data['alert']['permalink']
        self.test_name = event_data['alert']['testName']
        self.event_type = event_data['eventType']

    def get_test_details(self):
        url = f'https://{self.host}/v6/tests/{str(self.test_id)}.json'
        try:
            result = requests.get(url, verify=False, auth=(self.username, self.key))
            if result.status_code == 200:
                self.agents_list = result.json()['test'][0]['agents']
                self.interval = result.json()['test'][0]['interval']
                self.alert_rules_list = result.json()['test'][0]['alertRules']
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_alert_details(self):
        url = f'https://{self.host}/v6/alerts/{str(self.alert_id)}.json'
        try:
            result = requests.get(url, verify=False, auth=(self.username, self.key))
            if result.status_code == 200:
                self.date_start = result.json()["alert"][0]["dateStart"]
                self.alert_active = result.json()["alert"][0]["active"]
                self.agent_list = result.json()["alert"][0]["agents"]
                for agent in self.agent_list:
                    if agent['active'] == 1:
                        self.active_agent_list.append(agent)
                        self.active_agent_ids.append(agent["agentId"])
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

