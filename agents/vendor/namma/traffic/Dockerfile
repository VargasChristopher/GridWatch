# ---------- Dockerfile ----------
# 1. use slim base with Python 3.12
FROM python:3.13-slim AS runtime

# 2. set working directory
WORKDIR /app

# 3. install system packages (just in case httpx/OpenSSL need build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# 4. copy dependency list & install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 5. copy project code
#    adjust the source path if your repo layout differs
COPY . .

# 6. environment variables
#    – model + temperature are read from agent_config.json
#    – supply your API key and credentials at runtime:
#      docker run \
#        -e GOOGLE_API_KEY=<API_KEY> \
#        -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
#        -v /local/path/to/key.json:/path/to/key.json \
ENV PYTHONUNBUFFERED=1 

# 7. default command

CMD ["functions-framework", "--target=runTrafficUpdateAgent", "--signature-type=cloudevent"]