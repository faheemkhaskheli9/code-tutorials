# Getting started with Quokka

Quokka is our internal deployment CLI. It wraps the cluster API so nobody has to
remember kubectl incantations at 2am.

## Install

Quokka ships as a single binary. Grab it from the internal artifact store:

    curl -sSL https://artifacts.internal/quokka/latest -o /usr/local/bin/quokka
    chmod +x /usr/local/bin/quokka
    quokka version

The binary is statically linked, so there is nothing else to install. macOS and
Linux are supported. Windows users should run Quokka inside WSL2; the native
Windows build was dropped in 3.0 because the file-watcher was unreliable.

## First run

`quokka login` opens a browser and writes a token to `~/.quokka/credentials`.
The token lasts 30 days. There is no service-account flow for humans - CI uses a
separate `QUOKKA_CI_TOKEN` environment variable instead.

## The local dev server

`quokka dev` builds your service and serves it on **port 7717**. Pick a
different port with `quokka dev --port 8080`. The dev server watches the source
tree and rebuilds on change; the rebuild is incremental, so the first build is
slow (30-90 seconds for a typical service) and later ones take about two
seconds.

The dev server does *not* talk to production data. It points at the `sandbox`
database by default. Override with `--db staging`, but never `--db prod` - the
CLI refuses that combination and prints `E_NO_PROD_FROM_DEV`.

## Configuration

Each service has a `quokka.toml` at its repository root:

    [service]
    name = "billing-api"
    runtime = "python3.12"
    port = 8000

    [deploy]
    regions = ["eu-west", "us-east"]
    min_instances = 2

`min_instances` below 2 is allowed but disables the zero-downtime deploy path,
because there is no spare instance to shift traffic onto. Quokka warns about
this every time it deploys such a service.
