# Sneaky Snake
A low-volume web scraper using your local Chrome profile. For those small scraping jobs where simple, serialized processing is good enough.
Sometimes you don't want to spend forever figuring out the perfect scraping profile to evade the scraping protection and anti-bot boobytraps. Sometimes you would be fine handing over your logged-in, cookified, very-identifiable browser to a robot to just get some tedious things done... and this is when you need `Sneaky Snake`.

![sneaky snake](sneaky_snake.gif)

## Chrome Profile Setup

The service requires access to your Chrome profile to avoid nickel-and-diming bot detection stragegies. You'll need to mount your local Chrome profile directory to `/root/google-chrome` in the container.

### Windows
```bash
docker run --rm -p 8000:8000 -v "C:\Users\<YourName>\AppData\Local\Google\Chrome\User Data:/root/google-chrome" sneaky_snake
```

### macOS
```bash
docker run --rm -p 8000:8000 -v "${HOME}/Library/Application Support/Google/Chrome:/root/google-chrome" sneaky_snake
```

### Linux
```bash
docker run --rm -p 8000:8000 -v "${HOME}/.config/google-chrome:/root/google-chrome" sneaky_snake
```

> [!WARNING]
> Make sure Chrome is **completely closed** before starting the container, or your browser will hold the state lock and the container startup will fail with ` No such file or directory: '/root/google-chrome/SingletonLock'`. Once the service has started the scraper will be running off a copy of your browser state, so you are free to use your browser again.

## Usage
1. Start the container (see appropriate command above)
2. request a page scrape and get back the request_id
```bash
    >> curl -X 'POST' 'http://localhost:8000/scrape' -H 'accept: application/json'  -H 'Content-Type: application/json' -d '{ "urls": [{"url": "https://google.com", "use_cache": false}]}'
    ## { "request_ids": [ "5b95e456-21fc-40f9-bfdb-6c9ed79550fd" ] }

```

You can see the endpoint breakdown at [localhost:8000/docs](http://localhost:8000/docs)

### Usage in docker-compose
You probably want to do more than just slurp html; Sneaky Snake really shines when used to abstract just the messy scraping parts!

```yaml
services:
    sneaky_snake:
        hostname: sneaky-snake
        image: ethanknox/sneaky_snake:latest
        volumes:
            - ~/Library/Application Support/Google/Chrome:/root/google-chrome
    business_logic:
        image: python:3.13
        volumes:
            - ./your_business_logic.py:/app/your_business_logic.py
            - ./outputs:/app/outputs
        cmd: python3 your_business_logic.py
```

```python

# your_business_logic.py
import requests

response = requests.post("sneaky-snake/scrape", data={"urls": [
    {"url": "https://google.com", "use_cache": False},
    {"url": "https://linkedin.com"},
    {"url": "https://potato.com"}
]})

request_ids = response.json()["request_ids"]

while request_ids:
    for id_ in request_ids:
        response = requests.get(f"sneaky-snake/result/{id_}").json()
        if response["processed"]:
            request_ids.pop(request_ids.index(id_))
            # do whatever bs4 parsing etc you want here
            process_html_response(response["html"])
```




## Other Envars and volume mounts

### Envars
- `LOG_LEVEL`: one of `INFO`, `WARNING`, `ERROR`, `DEBUG` (defaults to `INFO`)

### Volume Mounts
- `/app/scrape_results.db` is the sqlite cache backend, if you want to persist scrapes between uses you can mount this to the host.
