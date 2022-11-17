FROM python:3.10-alpine
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app/"${BOT_NAME:-tg_bot}"

# Installing curl for poetry, chromium for pyppeteer, npm for sass
RUN apk -U add curl chromium udev npm
RUN npm install -g sass

# Installing poetry
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH=/root/.local/bin:$PATH

# Installing project dependencies from poetry.lock
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH \
    VIRTUAL_ENV=/venv
COPY pyproject.toml poetry.lock /usr/src/app/"${BOT_NAME:-tg_bot}"/
# Will install into the /venv virtualenv
RUN poetry install --no-root
