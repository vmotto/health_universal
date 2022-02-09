from managedinsights import MI
from thousandeyes import ThousandEyes
from servicenow import ServiceNow
from opensearch import OpenSearch
from time import sleep
import json
import pprint


def get_snow_severity(agent_list, agents_list):
    # SXO returns a list if more than one agent, but no list if just one agent
    affected_agents = len(agent_list) if isinstance(agent_list, list) else 1
    total_agents = len(agents_list) if isinstance(agents_list, list) else 1

    affected_percentage = affected_agents / total_agents

    return "Major" if affected_percentage >= 0.5 else "Minor"


if __name__ == '__main__':
    # event normally comes from webhook .. here I am just reading a sample JSON payload
    with open('event2.json', 'r') as myfile:
        event_data = json.load(myfile)

    mi = MI('ACME', 'ACME Critical Health')
    te = ThousandEyes()
    snow = ServiceNow()
    os = OpenSearch()

    te.parse_event_data(event_data)

    snow.ci_node_value = te.test_label_list[0]['name'] if te.test_label_list else te.test_targets_description

    # customer_name currently comes in on webhook query param
    snow.get_cust_sysid('ACME')

    if te.event_type == "ALERT_NOTIFICATION_TRIGGER":
        te.get_test_details()
        snow_severity = get_snow_severity(te.agent_list, te.agents_list)
        snow.create_event(te, mi, os)
        work_notes = ("[code]"
                      f"<h1 style=\"color:#6495ED;\"> Critical Services Initial Alert on {te.test_type}</h1>"
                      "<b>!!! Additional info may follow if the alert hasn’t resolved in Max 5 minutes!!!</b>"
                      f"<br><br><br><b>Alert Id : </b> {te.alert_id}"
                      f"<br><b>Rule Expression : </b> {te.rule_expression}"
                      "<br><b> Alert URL : </b> "
                      f"<a href= {te.permalink} target=\\\"_blank\\\" rel=\\\"noopener noreferrer\\\" > {te.permalink} </a><br>"
                      "[/code]")
        snow.update_ticket_workinfo(os, work_notes, "add_external_work_notes")

        interval = max(te.interval, 120) if te.interval < 301 else 300
        #sleep(interval)

        te.get_alert_details()
        print("here")
    else:
        print('ALERT_NOTIFICATION_CLEAR')

    #pprint.pprint(vars(te))
    #pprint.pprint(vars(snow))

