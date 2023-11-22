
# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
FROM python:3.11-slim

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Встановимо залежності всередині контейнера
COPY pyproject.toml $APP_HOME/pyproject.toml
COPY poetry.lock $APP_HOME/poetry.lock
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

# Скопіюємо інші файли в робочу директорію контейнера
COPY . .


# Позначимо порт, де працює застосунок всередині контейнера
# EXPOSE 5000

# Запустимо наш застосунок всередині контейнера
# CMD Xvfb :99 -ac -screen 0 1024x768x16 & python main.py
CMD ["tail", "-f", "/dev/null"]