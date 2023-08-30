FROM python:3.11.4-alpine

WORKDIR /usr/src/app/timetable_bot

ENV PATH=/venv/bin:/root/.local/bin:$PATH
ENV VIRTUAL_ENV=/venv

RUN apk --no-cache add curl chromium npm && \
    npm install -g sass && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    python -m venv /venv

COPY . .

RUN sass --update data/styles:data/compiled_html_pages/styles

RUN apk del curl npm

RUN poetry install --no-interaction --no-ansi --no-root --without=dev

RUN poetry run pybabel compile -d tgbot/locales -D messages
