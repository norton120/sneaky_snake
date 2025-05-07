FROM python:3.11
COPY ./app /src/app
WORKDIR /src
ENV PYTHONPATH=/src
RUN apt update && apt install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    xvfb \
    xauth \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    libgbm-dev \
    libgtk-3-0 \
    fonts-liberation \
    sqlite3 && \
    apt-get clean
COPY ./requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

RUN playwright install-deps
RUN playwright install

ENV DISPLAY=:99
CMD ["/bin/bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & uvicorn app.main:app --host 0.0.0.0 --port 8000"]