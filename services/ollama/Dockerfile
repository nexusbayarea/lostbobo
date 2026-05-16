FROM ollama/ollama:latest

COPY services/ollama/pull_models.sh /usr/local/bin/pull_models.sh
RUN chmod +x /usr/local/bin/pull_models.sh

ENTRYPOINT ["ollama", "serve"]
CMD ["--host", "0.0.0.0"]
