import requests
import json
import logging
import os


class ServiceNow:
    headers = {'Content-Type': 'application/json'}

    def __init__(self):
        self.host = "ciscodeliverysandbox.service-now.com"
        self.username = os.environ['SNOW_USERNAME']
        self.key = os.environ['SNOW_KEY']
        self.account = None
        self.ci_node_value = None
        self.ci_node_identifier_type = None
        self.event_additional_info = ""
        self.event_last_detected = ""
        self.event_message = ""
        self.event_message_short = None
        self.event_metric_name = None
        self.event_orgin_id = None
        self.event_source = None
        self.event_time = None
        self.event_type = None
        self.incident_ticket = ""
        self.severity = None
        self.event_source_link = None

    def get_cust_sysid(self, customer_name):
        # SXO uses a Global table var.
        # could use Parameter Store, or DynamoDB
        # here I'm just statically assigning
        self.account = 'eed4515e1b2dbcd0c1c6dd71ec4bcbd0'

    def create_event(self, te, mi, os):
        url = f'https://{self.host}/api/now/import/x_cims_cms_event_m_cms_actionable_events_staging'

        data = {
            "account": self.account,
            "ci_node": self.ci_node_value,
            "ci_node_identifier_type": "CI Name",
            "event_additional_info": "",
            "event_last_detected": "",
            "event_message": f"Critical Services Health Issue on target {te.test_targets_description} with {te.test_type} test \n\n\nPlease check incidents Work notes for detail  list of affected agents and useful alert information\n\n",
            "event_message_short": f"CMS_TE_{te.test_name} : {te.rule_name}",
            "event_metric_name": f"Critical Service Health_{mi.customer_name}",
            "event_orgin_id": te.alert_id,
            "event_source": "ThousandEyes",
            "event_time": "",
            "event_type": "Stateful",
            "incident_ticket": "",
            "severity": self.severity,
            "event_source_link": te.permalink
        }

        try:
            result = requests.post(url, verify=False, auth=(self.username, self.key), headers=self.headers, data=json.dumps(data))
            if result.status_code == 201:
                self.incident_ticket = result.json()['result'][0]["incident_ticket"]
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        data['response'] = result.json()
        os.send_to_opensearch('snow_event', data)


    def update_ticket_workinfo(self, os, work_notes, action):
        url = f'https://{self.host}/api/x_cims_cms_api_sui/cms/ve'

        if self.incident_ticket.startswith('INC'):
            data = {
                "incident_number": self.incident_ticket,
                "flow_name": "te_integration",
                "action": action,
                "work_notes": work_notes,
                "timesaved": "0"
            }

            try:
                result = requests.post(url, verify=False, auth=(self.username, self.key), headers=self.headers, data=json.dumps(data))
                if result.status_code == 201:
                    logging.info('Updated Ticket Workinfo successfully')
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)

            os.send_to_opensearch('snow_update', data)
