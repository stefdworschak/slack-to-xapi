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

## Todo

- Add `interaction_type` to Object
- Add `group` to Actor and Object
- Add logic for `mentions` (e.g. add extra xapi statement for a message that mentions other users)
- Add OAuth or JWT as authentication method (currently only BasicAuth available)
    - For extra security the project automatically encrypts the password (using the Django `SECRET_KEY`) when saving an LRS config and only decrypts it to send an xAPI statement to the LRS
- Add sentiment analysis to analyse messages and reactions

## Prerequisits

- Linux/Mac OS or WSL on Windows
    - [Install WSL on Windows](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- docker & docker-compose
    - [Get docker](https://docs.docker.com/get-docker/)
    - [Install compose](https://docs.docker.com/compose/install/)
- Slack Workspace and admin access (to create and install a Slack app)

## Slack Connector Setup

### Development Setup

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
5) Run the migrations and seed the xAPI fixtures
```
scripts/setup.sh
```
6) Use ngrok to create a publicly accessible URL
``` 
sudo apt install ngrok
ngrok http 80
```
7) Access start page via localhost

### For Production Setup

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
    - Configurations for most (if not all) of these events should already have been seeded in the previous setup steps

![Event Subscriptions](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/event_subscriptions_subscriptions.png?raw=true)

6) Add extra OAuth permissions if required
    - If you want actors to be created automatically, you will need to enable `users:read.email` as well
7) (Re-) Install your App and accept giving the app the requested permissions

![Oauth](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/img/oauth.png?raw=true)

8) Add the **OAuth Access Token** as `SLACK_OAUTH_TOKEN` to your `.env` file 

## Available Configurations

### How to access the configurations

This project does not have any custom UI. All configurations can be performed through the standard Django Admin console by accessing `/admin` on your host (e.g. for local development http://localhost/admin)

### Object ID field

If permalinks are not enabled, the object's id will default to the object's iri and the value of the SlackEvent's field that is specified in the object's `id_field`.

If permalinks are enabled, the permalink will become the id and will default to the same as above if no permalink is found.
For example:

``` 
SlackEvent.id = '123'

XApiObjec.iri = 'http://example.com/message'

Then the statement's object id value will be `http://example.com/Slack Message/123`.
```

For Slack Message and Slack DoNotDisturb the default is `event_id`.

For Slack File the default is the first value in `file_ids`.

For Slack Conversation the default is `channel`.

For Slack User Profile the default is `user_id`.

### Extensions

If you want to add extra extensions to your xAPI statements, add the SlackEvent's field you want to include in the object's extensions field.

All objects have `event_id` and `team_id` extensions by default.

### Permalinks

You can enable/disable the feature to retrieve permalinks for all messages, files and conversations and add them to the SlackEvent and xAPI statement by adding the `ENABLE_PERMALINKS` key to the `.env` file.

If you copy the `.env` template provided in the wiki, this will default to `True`.

### Actor creation

You can enable/disable the feature to automatically create Actors by adding the `ACTOR_CREATION_ENABLED` key to the `.env` file.

If you copy the `.env` template provided in the wiki, this will default to `True`.

You will also need to set the `ACTOR_IRI_TYPE` key in the `.env` file to choose which type of actor should be created.

You can choose from `mbox` which will retrieve the users's email from the Slack workspace, `mbox_sha1sum` which will retrieve the email and then hash it and `account` which will use the Slack user_id.

If this is not specified it will default to `account`.

You can also manually create Actors with OpenID on the Django admin console.

## System Design

### User Stories

- As a Learning Provider, I want to measure how much students engage on Slack, so that I can validate that Slack is a useful tool to support their learning and also measure the usage of Slack.
- As a Learning Provider, I want to know in what way my students engage with Slack, so that I can gauge which methods of interaction support their learning and enforce these methods.
- As a Learning Provider, I want to know what kind of content students share, pin, star and react to, so that I can better curate learning resources for them.

### System Architecture

![System Architecture Diagram](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/system_architecture.png?raw=true)

## Slack event to verb & object mapping

### Logic

![Slack Events Mapping](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/slack_events_mapping.png?raw=true)

### Standard Types:

| Slack Event Type | Slack Event SubType | Verb | Object | 
| --- | --- | --- | --- |
| member_joined_channel | None | completed | Join Slack Conversation |
| member_left_channel | None | completd | Leave Slack Conversation |
| message | None | completed | Send Slack Message |
| message | message_changed | completed | Change Slack Message |
| message | message_deleted | completed | Delete Slack Message |
| message | file_share | completed | Share Slack File(s) |
| pin_added | None | completed | Pin Slack Message |
| pin_added | None | completed | Pin Slack File |
| pin_removed | None | completed | Unpin Slack Message |
| pin_removed | None | completed | Unpin Slack File |
| reaction_added | None | completed | React to Slack Message |
| reaction_added | None | completed | React to Slack File |
| reaction_removed | None | completed | Remove Reaction to Slack Message |
| reaction_removed | None | completed | Remove Reaction to Slack File |
| star_added | None | completed | Save Slack Message for later |
| star_added | None | completed | Save Slack File for later |
| star_removed | None | completed | Remove saved Slack Message |
| star_removed | None | completed | Remove saved Slack File |
| file_change | None | completed | Change Slack File |
| file_deleted | None | completed | Delele Slack File |
| file_created | None | completed | Create Slack File |
| file_public | None | completed | Make Slack File public |
| file_shared | None | completed | Share Slack File |
| user_change | None | completed | Change Slack User Profile |
| dnd_updated_user | None | completed | Change Slack DoNotDisturb |
| message | channel_topic | completed | Set Slack Conversation topic |
| message | channel_purpose | completed | Set Slack Conversation description |
| message | channel_archive | completed | Archive Slack Conversation |

### Special types:

| Slack Event Type | Slack Event SubType | Verb | Object | Extra Slack Event Attr |
| --- | --- | --- | --- | ---|
| message | None | shared | Slack Message | attachments != None |

### Special types (currently not covered):

| Slack Event Type | Slack Event SubType | Verb | Object | Extra Slack Event Attr |
| --- | --- | --- | --- | ---| 
| message | None | mentioned | Slack User | message contains `<@userid>` |
