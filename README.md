# slack-to-xapi

## Purpose of this project

Using the [Slack Events API](https://api.slack.com/events-api) this custom Open Source Slack to xAPI connector should enable Slack workspace admins to configure and send customized xAPI statements for a specific workspace to an LRS.

Main system requirements:
 - Easy to set up
 - Easy to configure
 - Interoperable with any xAPI conformant LRS
 - Available for any xAPI professional or enthusiast

## System Architecture

![System Architecture Diagram](https://github.com/stefdworschak/slack-to-xapi/blob/master/misc/system_architecture.png?raw=true)

## Slack event to verb & object mapping

### Standard Types:

| Slack Event Type | Slack Event SubType | Verb | Object | 
| --- | --- | --- | --- | --- |
| message | message_changed | changed | message uri |
| member_left_channel | None | left | channel uri |
| message | message_deleted | deleted | message uri |
| pin_removed | None | unpinned | message/file uri |
| star_added | None | starred | message uri |
| file_change | None | changed | file uri |
| file_deleted | None | deleled | file uri |
| pin_added | None | pinned | message/file uri |
| file_created | None | created | file uri |
| message | file_share | shared | file uri |
| file_public | None | made public | file uri |
| member_joined_channel | None | joined | channel uri |
| file_shared | None | shared | file uri |
| reaction_added | None | reacted to | message/file uri |
| reaction_removed | None | removed reaction to | message/file uri |
| message | None | sent | message uri |

### Special types: 
| Slack Event Type | Slack Event SubType | Verb | Object | Extra Slack Event Attr |
| --- | --- | --- | --- | ---| 
| message | None | shared | message uri | attachments != None |
