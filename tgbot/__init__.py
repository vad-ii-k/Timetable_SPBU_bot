"""
### The main module for bot development

### Documentation generation
```shell
pdoc tgbot/
```
```dark theme:  -t data/pdoc_templates/```

### Project installation
1. Clone this GitHub repository
```shell
    git clone [url]
```
2. Edit .env.dist file and rename it to .env
```shell
    mv .env.dist .env
```
3. Create and start docker containers
```shell
    docker-compose up
```

### How to update program after changes?
1. Before uploading code to GitHub
    - run
```shell
    pybabel extract --input-dirs=tgbot -o tgbot/locales/messages.pot -w 100
    pybabel update -d tgbot/locales -D messages -i tgbot/locales/messages.pot -w 100
```
    - Change translations in tgbot/locales/en/LC_MESSAGES/messages.po, if necessary
2. Download code from GitHub to your server
```shell
    git pull
```
3. Restart bot container
    - If you have updated or added libraries
```shell
    docker-compose -d --build
```
    - Otherwise
```shell
    docker-compose restart
```
"""
