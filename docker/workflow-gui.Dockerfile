FROM python:3.12-alpine

# Non-root user for container security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY scripts/workflow_gui.py /app/scripts/workflow_gui.py

USER appuser

EXPOSE 8088

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8088/health')" || exit 1

ENTRYPOINT ["python3", "scripts/workflow_gui.py", "--serve", "--port", "8088"]
