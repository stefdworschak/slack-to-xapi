docker run --rm -it -p "8000:8000" \
--mount "type=bind,src=/home/stefan/Documents/slack-to-xapi/src/slack/,dst=/app/slack" \
--name slack-to-xapi slack-to-xapi
