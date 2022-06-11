# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# install the OS build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.6 \
    libffi-dev=3.2.1-9 \
    libssl-dev=1.1.1n-0+deb10u2 \
    python-dev=2.7.16-1 \
    python3-dev=3.7.3-1 \
    openssl=1.1.1n-0+deb10u2 \
    cargo=0.43.1-3~deb10u1 \
 && rm -rf /var/lib/apt/lists/*

# Update pip and install pip requirements
COPY src/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==22.1.2 && pip install --no-cache-dir -r requirements.txt
 
WORKDIR /app
COPY . /app

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "./src/teslamte_telegram_bot.py"]
