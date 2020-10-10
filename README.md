# slack-to-xapi

## Purpose of this project

Using the [Slack Events API](https://api.slack.com/events-api) this custom Open Source Slack to xAPI connector should enable Slack workspace admins to configure and send customized xAPI statements for a specific workspace to an LRS.

Main system requirements:
 - Easy to set up
 - Easy to configure
 - Interoperable with any xAPI conformant LRS
 - Available for any xAPI professional or enthusiast

## Tested compatibility with the following LRS

- SCORM Cloud (SaaS free account)
- Watershed (SaaS free account)
- Veracity Learning (SaaS free account)
- Learning Locker (self-hosted open-source version)
- ADL LRS (self-hosted open-source version)

## Features:

- 

## TODOs

- Add `interaction_type` to Object
- Add `group` to Actor and Object
- Add logic for `mentions` (e.g. add extra xapi statement for a message that mentions other users)
- Add OAuth or JWT as authentication method (currently only BasicAuth available)
- Add sentiment analysis to analyse messages and reactions

## Preequisits

- docker & docker-compose
- Slack Workspace (and admin access)

## Slack Connector Setup

1) Create a new `.env` file in the root directory ([see here](https://github.com/stefdworschak/slack-to-xapi/wiki/.env))
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

## Slack App Setup

1) Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2) Create new app and select your workspace from the **Development Slack Workspace**
![Create App](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/create_app.png?raw=true)
3) Open your app and go to **Event Subscriptions**
4) Turn on **Event Subscriptions** and fill in your endpoint url (should end in "/xapi/slack/" and don't forget the "/" at the end)
    - e.g. https://c4fcf1f12854.ngrok.io/xapi/slack/
![Event Subscriptions Link](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/event_subscription_link.png?raw=true)
    - If the link to the endpoint is not correct or does for some reason not successfully return the authentication challenge, it will show an error message
![Event Subscriptions Link](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/event_subscription_link_error.png?raw=true)
5) Add whatever events you want to save xAPI statements for (both user and/or bot)
    - Most (if not all) of these events should already have been seeded in the previous setup steps
![Event Subscriptions](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/event_subscriptions_subscriptions.png?raw=true)
6) Add extra OAuth permissions if required
    - If you actors to be created automatically, you will need to enable `users:read.email` as well
7) (Re-)install your App and accept giving the app the requested permissions
![Oauth](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/oauth.png?raw=true)
8) Copy the **OAuth Access Token** to you `.env` file


## User Stories

- As a Learning Provider, I want to measure how much students engage on Slack, so that I can validate that Slack is a useful tool to support their learning and also measure the usage of Slack.
- As a Learning Provider, I want to know in what way my students engage with Slack, so that I can gauge which methods of interaction support their learning and enforce these methods.
- As a Learning Provider, I want to know what kind of content students share, pin, star and react to, so that I can better curate learning resources for them.

## System Architecture

![System Architecture Diagram](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/system_architecture.png?raw=true)

## Slack event to verb & object mapping

### Standard Types:

| Slack Event Type | Slack Event SubType | Verb | Object | 
| --- | --- | --- | --- |
| member_joined_channel | None | joined | Slack Conversation |
| member_left_channel | None | left | Slack Conversation |
| message | None | sent | Slack Message |
| message | message_changed | changed | Slack Message |
| message | message_deleted | deleted | Slack Message |
| message | file_share | shared | Slack File |
| pin_added | None | pinned | message/Slack File |
| pin_removed | None | unpinned | message/Slack File |
| reaction_added | None | reacted to | message/Slack File |
| reaction_removed | None | removed reaction to | message/Slack File |
| star_added | None | starred | message/Slack File |
| star_removed | None | unstarred | message/Slack File |
| file_change | None | changed | Slack File |
| file_deleted | None | deleled | Slack File |
| file_created | None | created | Slack File |
| file_public | None | made public | Slack File |
| file_shared | None | shared | Slack File |
| user_change | None | changed | Slack User Profile |
| dnd_updated_user | None | changed | Slack Do Not Disturb |
| message | channel_topic | set topic for | Slack Conversation |
| message | channel_purpose | set description for | Slack Conversation |
| message | channel_archive | changed | Slack Conversation |

### Special types: 
| Slack Event Type | Slack Event SubType | Verb | Object | Extra Slack Event Attr |
| --- | --- | --- | --- | ---| 
| message | None | shared | Slack Message | attachments != None |
| message | None | mentioned | actor | message contains `<@userid>` |
