docker run --rm -it \
-p "8000:8000" \
--mount "type=bind,src=/home/stefan/Documents/slack-to-xapi/src/slack_events/,dst=/app/slack_events/" \
--mount "type=bind,src=/home/stefan/Documents/slack-to-xapi/src/xapi/,dst=/app/xapi/" \
--mount "type=bind,src=/home/stefan/Documents/slack-to-xapi/data/,dst=/app/data/" \
--name slack-to-xapi slack-to-xapi
