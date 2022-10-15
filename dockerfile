FROM python:3.10-alpine
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app/"${BOT_NAME:-tg_bot}"

COPY requirements.txt /usr/src/app/"${BOT_NAME:-tg_bot}"
RUN pip install --upgrade pip -r /usr/src/app/"${BOT_NAME:-tg_bot}"/requirements.txt
COPY . /usr/src/app/"${BOT_NAME:-tg_bot}"

#Installing chromium for pyppeteer
RUN apk -U add chromium udev ttf-freefont

# Compiling locales
# cd tgbot/
# pybabel extract --input-dirs=. -o locales/messages.pot -w 100
# pybabel update -d locales -D messages -i locales/messages.pot -w 100
# pybabel compile -d locales -D messages