# Everest Bot

Our Slack bot, _Everest bot_ runs inside one of our Azure vm:s and can talk with the cluster and applications inside. The bot also does UptimeRobot checking.

## Usage:

`/invite @Everest Bot` to your team channel or talk using direct message with the bot. Also invite the bot to the channel that gets your application UptimeRobot alerts.

### Commands you can ask

_Examples:_

`@Everest Bot` help

`@Everest Bot` tasks active search-web_web

```
Command             Parameters                              Description
------------------------------------------------------------------------
status                                                      Shows the status of all clusters
health              cluster service_name                    Runs a healthcheck for a given service and cluster
services            cluster                                 Show services running on the given cluster
tasks               cluster service_name                    Show the tasks associated with the given service
logs                cluster service_name nr_of_rows         Show the last nr_of_rows rows of log for a service
management                                                  Shows info on containers running on the management vm
who                                                         Who is online in this channel?

Explanation of parameters:
cluster             - Cluster status (development, stage, active..)
service_name        - Part of the name of a service (niseko, places..)
nr_of_rows          - The number of rows to tail from logs
```

## The bot is also a watching the channel communication

### UptimeRobot alerts

When an alerts is written in the teams alert channel and the Everst bot is a member of that channel Everest bot will validate the alert.

_Example:_
`Monitor is DOWN: Course and Programme Directory ( https://app.kth.se/kopps-public/_monitor ) - Reason: Keyword Does Not Exist`

_When its a glitch (network issue or so)_

````bash
Everest BotAPP [16:33]
I think that was a temporary glitch https://app.kth.se/kopps-public/_monitor works for me.
APPLICATION_STATUS: OK
KOPPS_API_STATUS: OK version: 2019.1
HEAP_USAGE: OK 1.7 GB of 1.8 GB max 1.8 GB
NON_HEAP_USAGE: OK 148.1 MB of 150.6 MB max 732.0 MB```
````

_When its a real problem_
When a proper error has occured the `@channel` is notified, and a link to Graylog with the correct time period is generated

````bash
Everest BotAPP [04:44]
@channel UpTimeRobot is correct. The url https://api.kth.se/api/timetable/_monitor gave status 200 and response:
APPLICATION_STATUS: ERROR
SYNC_STATUS: OK
DATABASE_STATUS: ERROR ElasticSearch index failure: java.n ...```
````

:mag: See _2 minutes of logs_ for timetable-api.

```bash
https://graycloud.ite.kth.se/search?rangetype=absolute&fields=message%2Csource&from=2019-06-11T02%3A42%3A11.738Z&to=2019-06-11T02%3A44%3A11.738Z&q=source%3Aactive+AND+image_name%3A/.%2Atimetable-api%3A2.1.43_cabb0a1.%2A/
```
