FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
ENV FLASK_APP=app.py
ENV FLASK_ENV=development  
ENTRYPOINT ["/entrypoint.sh"]