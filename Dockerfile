# see https://www.python.org/doc/versions/
ARG PYTHON_VERSION=3.13.3

# -------------------------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS development

# see https://github.com/tj/n/tags
ARG N_VERSION=10.1.0

# see https://nodejs.org/en/about/previous-releases
ARG NODE_VERSION=22.15.0

RUN export URL=https://raw.githubusercontent.com/tj/n/v${N_VERSION}/bin/n && \
    curl -L $URL | bash -s ${NODE_VERSION}

COPY /pdm-deps.txt /pdm-install.sh /

RUN sh /pdm-install.sh && \
    pdm config build_isolation false && \
    pdm config check_update false && \
    rm /pdm-*

# -------------------------------------------------------------------------------------------------
FROM development AS build

COPY / /src

RUN cd /src && \
    pdm sync --no-isolation && \
    pdm build --no-sdist

# -------------------------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS production

COPY /jupyter /jupyter

COPY /kernel-deps.txt /kernel-install.sh /

COPY --from=build /src/dist/*.whl /

ENV JUPYTER_CONFIG_PATH=/jupyter

RUN export PYTHONDONTWRITEBYTECODE=1 && \
    pip install --no-cache-dir /*.whl && \
    sh /kernel-install.sh && \
    rm -rf /*.whl /kernel-* /var/lib/apt/lists/*

WORKDIR "/workdir"

ENTRYPOINT [ "minispot" ]
