FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY bench ./bench
COPY data ./data
COPY tests ./tests
EXPOSE 8080
CMD ["uvicorn", "schild.api:app", "--host", "0.0.0.0", "--port", "8080"]
