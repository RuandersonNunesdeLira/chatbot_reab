FROM python:3.13.5-bookworm AS build

RUN useradd -m -s /usr/bin/bash ruan

FROM build AS development

USER ruan

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
