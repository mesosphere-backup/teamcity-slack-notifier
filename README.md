# teamcity-slack-notifier
A python script that when run in TeamCity will post alerts to a Slack Channel

# Usage
The following environment variables must be set in TeamCity Build Configuration Parameters:
* **TC\_URL**: %teamcity.serverUrl%
* **TC\_AUTH\_USER**: %system.teamcity.auth.userId%:
* **TC\_AUTH\_PW**: %system.teamcity.auth.password%
* **SLACK\_URL**: Get this URL from setting up Slack Incoming Webhooks Integration
* **THIS\_BUILD\_TYPE**: %system.teamcity.buildType.id%
* **THIS\_BUILD\_NUM**: %system.build.number%
