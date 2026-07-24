FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/server
ENV PORT=8080
ENV PULSE_STATE=/app/data/pulse_state.json
EXPOSE 8080
CMD ["python", "mcp_server.py"]
