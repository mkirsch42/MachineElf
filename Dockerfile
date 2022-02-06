FROM python:3.10.2

RUN useradd --create-home --shell /bin/bash elf
USER elf

WORKDIR /tmp
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/home/elf/.local/bin:$PATH
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /tmp/
RUN poetry install --no-dev

ADD . /srv

WORKDIR /srv
CMD python -m app.main