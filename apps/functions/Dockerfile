FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Working directory inside the container for the function app
WORKDIR /home/site/wwwroot

# Pre-copy requirements to leverage docker layer caching
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip cache purge || true

# Copy function app code
COPY . .

# Azure Functions host in the base image uses /azure-functions-host start script.
# Expose default port
EXPOSE 80

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# For local dev you can override settings by mounting local.settings.json
# or injecting environment variables at run time.

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:80/api/health || exit 1

# Provide a simple optional health function path placeholder (not implemented yet)
# If you later add a health function, ensure route matches above.
