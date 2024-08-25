FROM python:3.12.5-alpine

WORKDIR /app

ENV PATH=/venv/bin:/root/.local/bin:$PATH
ENV VIRTUAL_ENV=/venv

RUN apk --no-cache add curl chromium && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apk del curl && \
    python -m venv /venv

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root --without=dev

COPY ./data/styles/ data/styles/

RUN apk --no-cache add npm && \
    npm install -g sass && \
    sass --update data/styles:data/compiled_html_pages/styles && \
    apk del npm

COPY tgbot/locales/ tgbot/locales/

RUN poetry run pybabel compile -d tgbot/locales -D messages

COPY . .

ENTRYPOINT [ "/bin/sh", "-c" ]
