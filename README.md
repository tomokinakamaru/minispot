# Minispot

## Usage

1. Install [Docker](https://www.docker.com/)

1. Launch Minispot

   ```sh
   docker run --rm -it -p8888:8888 -v$(pwd):/workdir ghcr.io/tomokinakamaru/minispot:latest
   ```

1. Open the localhost URL displayed in the terminal

   ```sh
   ...
   [C 2024-01-01 00:00:00.000 ServerApp]
   ...
           http://localhost:8888/tree?token=... # ← This URL
           http://127.0.0.1:8888/tree?token=...
   ...
   ```

1. Create a notebook and do anything you want

## Development

1. Install Docker
1. Open this repository using a [dev container](https://containers.dev)
1. Run `pdm sync` to setup the environment
1. Run `sh kernel-install.sh` to install the default kernel
1. Run `source .venv/bin/activate` to activate the virtual environment
1. Run `jlpm install` to setup the test environment

### Run linters

```sh
pdm run lint
pdm run fix # Fix lint issues
```

### Run tests

```sh
jlpm playwright install --with-deps chromium # Install dependencies
jlpm playwright test
```

### Run GitHub actions

```sh
# Run this command outside the dev container
act --job check --matrix python-version:3.13
```

### Build wheel

```sh
pdm build --no-sdist
```

### Upgrade dependencies

#### Upgrade Python and Node

Check the URLs listed in Dockerfile

#### Upgrade pdm dependencies

```sh
sh pdm-upgrade.sh
```

#### Upgrade default kernel dependencies

```sh
sh kernel-upgrade.sh
```

#### Upgrade pdm-managed dependencies

```sh
pdm update --unconstrained
```

#### Upgrade jlpm-managed dependencies

```sh
jlpm plugin import @yarnpkg/plugin-interactive-tools
jlpm upgrade-interactive
jlpm plugin remove @yarnpkg/plugin-interactive-tools
```
