# slack-to-xapi

## Purpose of this project

Using the [Slack Events API](https://api.slack.com/events-api) this custom Open Source Slack to xAPI connector should enable Slack workspace admins to configure and send customized xAPI statements for a specific workspace to an LRS.

Main system requirements:
 - Easy to set up
 - Easy to configure
 - Interoperable with any xAPI conformant LRS
 - Available for any xAPI professional or enthusiast

## TODOs

- Add `interaction_type` to Object
- Add `group` to Actor and Object
- Add logic for `mentions` (e.g. add extra xapi statement for a message that mentions other users)
- Add OAuth or JWT as authentication method (currently only BasicAuth available)
- Add sentiment analysis to analyse messages and reactions

## Development Setup

1) Create a new `.env` file in the root directory ([see here]())
2) Create the data folder (in root) and the SQLite database.
```
mkdir data
touch data/db.sqlite3
```
3) Build the docker image
```
docker build . -t slack-to-xapi
```
4) Bring the docker containers up using `docker-compose`
```
docker-compose up -d
```
5) Run the migrations and see the xAPI fixtures
```
scripts/setup.sh
```
6) Use ngrok to create a publicly accessible URL
``` 
sudo apt install ngrok
ngrok http 80
```
7) Access start page via localhost

## For Production Setup

- Make sure you serve via HTTPS

## User Stories

- As a Learning Provider, I want to measure how much students engage on Slack, so that I can validate that Slack is a useful tool to support their learning and also measure the usage of Slack.
- As a Learning Provider, I want to know in what way my students engage with Slack, so that I can gauge which methods of interaction support their learning and enforce these methods.
- As a Learning Provider, I want to know what kind of content students share, pin, star and react to, so that I can better curate learning resources for them.

## Tested compatibility with the following LRS

- SCORM Cloud (SaaS free account)
- Watershed (SaaS free account)
- Veracity Learning (SaaS free account)
- Learning Locker (self-hosted open-source version)
- ADL LRS (self-hosted open-source version)

## System Architecture

![System Architecture Diagram](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/system_architecture.png?raw=true)

## Slack event to verb & object mapping

### Standard Types:

| Slack Event Type | Slack Event SubType | Verb | Object | 
| --- | --- | --- | --- |
| member_joined_channel | None | joined | channel uri |
| member_left_channel | None | left | channel uri |
| message | None | sent | message uri |
| message | message_changed | changed | message uri |
| message | message_deleted | deleted | message uri |
| message | file_share | shared | file uri |
| pin_added | None | pinned | message/file uri |
| pin_removed | None | unpinned | message/file uri |
| reaction_added | None | reacted to | message/file uri |
| reaction_removed | None | removed reaction to | message/file uri |
| star_added | None | starred | message/file uri |
| star_removed | None | unstarred | message/file uri |
| file_change | None | changed | file uri |
| file_deleted | None | deleled | file uri |
| file_created | None | created | file uri |
| file_public | None | made public | file uri |
| file_shared | None | shared | file uri |

### Special types: 
| Slack Event Type | Slack Event SubType | Verb | Object | Extra Slack Event Attr |
| --- | --- | --- | --- | ---| 
| message | None | shared | message uri | attachments != None |
| message | None | mentioned | actor | message contains `<@userid>` |
