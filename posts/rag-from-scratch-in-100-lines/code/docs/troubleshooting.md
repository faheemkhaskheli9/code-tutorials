# Troubleshooting

## E_LOCKED

Another deploy holds the lock for this service and environment. Check who with
`quokka locks --env prod`; the output shows the holder and when the lock was
taken. Wait for it to finish - that is almost always the right answer.

A lock older than 30 minutes is stale, usually because a CI runner was killed
mid-deploy. Break it with `quokka locks --break --env prod` and say why in the
prompt. Breaking a lock while a deploy really is running will interleave two
ramps and send traffic to both versions in an order nobody can predict, so check
the age first.

## E_NO_PROD_FROM_DEV

You passed `--db prod` to `quokka dev`. The CLI blocks this on purpose. If you
genuinely need to read production data, use `quokka shell --env prod --readonly`,
which is audited.

## Build hangs at "resolving dependencies"

Almost always the internal package mirror. `quokka doctor` checks reachability of
the mirror, the registry and the cluster API, and prints which one is failing.
If the mirror is down, `--offline-deps` will build from the last successful
dependency set, but it will not pick up any dependency change you just made.

## The deploy finished but the old version is still serving

Your service is probably running with `min_instances = 1`. With one instance
there is no spare capacity to shift traffic onto, so Quokka replaces the
instance in place and the load balancer can keep an existing connection open to
the old process for up to 120 seconds. Raise `min_instances` to 2 or wait.

## Credentials keep expiring

`~/.quokka/credentials` holds a 30-day token. If it expires daily instead, you
are probably on a machine where the keyring is not unlocked at login, so Quokka
falls back to an in-memory token that dies with the shell. Run
`quokka login --no-keyring` to write a plain file instead, and accept that the
token is then readable by anything running as you.
