FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./

# In compose the agent runs over HTTP so `task up` shows all three experiences
# live. Locally it is normally spawned over stdio by an agent host (see README).
ENV MCP_TRANSPORT=streamable-http
ENV DOMAIN_API_URL=http://behaviour-service:8000
EXPOSE 3001

CMD ["python", "server.py"]
