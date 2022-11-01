FROM python:3.10-alpine
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app/"${BOT_NAME:-tg_bot}"

COPY requirements.txt /usr/src/app/"${BOT_NAME:-tg_bot}"
RUN pip install --upgrade pip -r /usr/src/app/"${BOT_NAME:-tg_bot}"/requirements.txt
COPY . /usr/src/app/"${BOT_NAME:-tg_bot}"

#Installing chromium for pyppeteer
RUN apk -U add chromium udev npm
RUN npm install -g sass

# Updating locales
# pybabel extract --input-dirs=tgbot -o tgbot/locales/messages.pot -w 100
# pybabel update -d tgbot/locales -D messages -i tgbot/locales/messages.pot -w 100