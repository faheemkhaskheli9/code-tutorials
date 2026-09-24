# Rolling back

To roll back a bad deploy, run:

    quokka rollback --env prod

With no other arguments this moves all traffic to the previous successful
release and takes about 40 seconds. It does not rebuild anything - the previous
image is still in the registry, so a rollback is just a traffic change.

Roll back to a specific release instead of the previous one:

    quokka releases --env prod          # lists the last 20 releases with IDs
    quokka rollback --env prod --to r-4812

Quokka keeps the last 20 images per service per environment. Anything older has
been garbage-collected and cannot be rolled back to; you have to redeploy that
commit from source.

## What a rollback does not undo

A rollback moves code, not data. Database migrations are *not* reverted, which
is why every migration has to be backward compatible with the previous release -
add a nullable column, deploy, backfill, then drop the old column in a later
release. If you skip that discipline, the rollback will succeed and the old code
will then fail against the new schema, which is a worse outage than the one you
were fixing.

Feature flags are also unaffected. If the bad behaviour came from a flag, turn
the flag off; that takes effect in about five seconds and is much cheaper than a
rollback.

## After a rollback

Quokka marks the rolled-back release as `quarantined`. A quarantined release
cannot be deployed again until someone runs `quokka release unquarantine r-4812`
with a reason. This exists because people kept re-deploying the same broken
build while debugging.
