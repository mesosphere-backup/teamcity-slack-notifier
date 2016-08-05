#!/usr/bin/env python3
import json
import os
import re
import sys
from subprocess import check_call, check_output

from urllib.parse import urlparse

# Hard fails if these are not present
TC_URL = os.environ['TC_URL']
TC_USER = os.environ['TC_AUTH_USER']
TC_PW = os.environ['TC_AUTH_PW']
SLACK_URL = os.environ['SLACK_URL']
THIS_BUILD_TYPE = os.environ['THIS_BUILD_TYPE']
THIS_BUILD_NUM = os.environ['THIS_BUILD_NUM']


def get_json_from_tc(endpoint):
    return json.loads(check_output([
        'curl', '-fLsSv', '-H', 'accept: application/json',
        '-u', ':'.join[TC_USER, TC_PW],
        urlparse(TC_URL+endpoint).geturl()]).decode())


def post_to_slack(json_str):
    with open('upload.json', 'w') as fh:
        fh.write(json_str)
        check_call([
            'curl', '-X', 'POST', '--upload-file', 'upload.json', SLACK_URL])
    check_call(['rm', 'upload.json'])


def create_attachment(heading, test_data):
    return {
            'fallback': test_data,
            'color': 'danger',
            'fields': [{
                'title': heading,
                'value': test_data,
                'short': False}]
            }


def parse_value(regex, target):
    return re.search(regex, target).group(0).split('=')[1].strip("'")


def main():
    # Get this build's info
    build_endpoint = '/httpAuth/app/rest/builds/running:true,' \
        'buildType:{},number:{}'.format(THIS_BUILD_TYPE, THIS_BUILD_NUM)
    # Use info to find what triggered this build
    build_details = get_json_from_tc(build_endpoint)['triggered']['details']
    trigger_type = parse_value(r"triggeredByBuildType='bt\d*'", build_details)
    trigger_number = parse_value(r"triggeredByBuild='\d*'", build_details)
    trigger_endpoint = '/httpAuth/app/rest/builds/' \
        'buildType:{},number:{}'.format(trigger_type, trigger_number)
    trigger_json = get_json_from_tc(trigger_endpoint)
    trigger_status = trigger_json['status']
    if trigger_status.upper() == 'SUCCESS':
        # Trigger build was successful; no notification needed
        sys.exit(0)
    msg_body = """Build Failed: {}
Status: {}
<{}/viewLog.html?buildId={}|More Details>
    """.format(trigger_json['buildType']['name'], trigger_json['statusText'],
               TC_URL, trigger_json['id'])
    slack_payload = {'text': msg_body}
    if 'testOccurrences' in trigger_json:
        attachments = []
        test_details = get_json_from_tc(trigger_json['testOccurrences']['href'])
        for t in test_details['testOccurrence']:
            if t['status'].upper() != 'SUCCESS':
                if 'currentlyMuted' in t:
                    if t['currentlyMuted'] is True:
                        continue
                t_fail_details = get_json_from_tc(t['href'])['details']
                break
                attachments.append(create_attachment(t['name'], t_fail_details))
        if len(attachments) > 0:
            slack_payload['attachemnts'] = attachments
    post_to_slack(json.dumps(slack_payload))


if __name__ == '__main__':
    main()
