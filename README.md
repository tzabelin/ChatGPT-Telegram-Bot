# ChatGPT Telegram Bot

## ffly.io Remote Deployment

Official documentation: ：https://fly.io/docs/

Deploy fly.io application using Docker image

Enter the name of the application, and if prompted to initialize Postgresql or Redis, always select No.

Follow the prompts to deploy. The control panel on the official website will provide a secondary domain name that can be used to access the service.

Set the environment variables

```bash
flyctl secrets set WEB_HOOK=https://flyio-app-name.fly.dev/
flyctl secrets set BOT_TOKEN=bottoken
flyctl secrets set EMAIL=
flyctl secrets set PASSWORD=
# flyctl secrets set session_token=

# Optional
flyctl secrets set NICK=javis
```

View all environment variables

flyctl secrets list

Remove environment variables

flyctl secrets unset MY_SECRET DATABASE_URL

ssh connect to the fly.io container

# Generate the key
flyctl ssh issue --agent
# ssh connection
flyctl ssh establish

Check if the webhook url is correct

https://api.telegram.org/bot<token>/getWebhookInfo
```

## Reference

https://github.com/acheong08/ChatGPT

https://github.com/franalgaba/chatgpt-telegram-bot-serverless
