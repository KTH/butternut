#
# To run localy you need to have a 
# SLACK_BOT_TOKEN="abcdef" set in your local .env file
#
docker compose up \
        --force-recreate \
        --abort-on-container-exit \
        --always-recreate-deps \
        --no-log-prefix \
        --quiet-pull \
        --build