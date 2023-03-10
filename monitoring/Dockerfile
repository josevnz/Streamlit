# Container to run our race results dashboards
# Author: @josevnz@fosstodon.org
FROM python:3.9-slim
WORKDIR /app
COPY .. /app/
RUN /usr/local/bin/python -m pip install --upgrade pip && \
    /usr/local/bin/pip3 install -r requirements.txt
EXPOSE 8501
HEALTHCHECK CMD python3 -c 'from urllib import request; request.urlopen("http://localhost:8501/_stcore/health")'
ENTRYPOINT ["streamlit", "run", "Main.py", "--server.port=8501", "--server.address=0.0.0.0"]