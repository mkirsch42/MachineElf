FROM python:3.10.2

RUN useradd --create-home --shell /bin/bash elf
USER elf
ENV PATH=/home/elf/.local/bin:/home/elf/.cargo/bin:$PATH

RUN curl -sSL https://sh.rustup.rs | bash -s -- -y

RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml /srv/
RUN poetry install --only main

ADD . /srv

WORKDIR /srv
CMD poetry run python -m app.main
