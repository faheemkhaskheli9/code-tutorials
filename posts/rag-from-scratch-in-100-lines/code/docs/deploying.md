# Deploying a service

    quokka deploy --env staging
    quokka deploy --env prod

A deploy runs in five phases: build, push, canary, ramp, finish. Quokka prints
the phase it is in and the elapsed time, and the whole thing takes four to eight
minutes for a normal service.

## The canary phase

Quokka sends 5% of traffic to the new version for 90 seconds and watches the
error rate. If the new version's 5xx rate is more than 1.5x the old version's,
the canary fails and Quokka rolls back on its own - you do not have to do
anything. The threshold is deliberately loose; a tighter one produced too many
false alarms on low-traffic services.

Skip the canary with `--no-canary`. Only do this for a config-only change or
when you are shipping a fix for an outage that is already happening.

## The ramp phase

After a healthy canary, traffic moves in four steps: 25%, 50%, 75%, 100%, with a
60-second hold at each step. A deploy therefore cannot complete faster than
about five minutes even if the build is instant. `--fast-ramp` collapses the
ramp to a single 0-100% cut and is restricted to the `staging` environment.

## Deploy locks

Only one deploy per service per environment can run at a time. Quokka takes a
lock at the start of the build phase and releases it when the deploy finishes or
fails. A second deploy attempted while the lock is held exits immediately with
`E_LOCKED`.

## Who can deploy

Anyone on the service's owning team can deploy to staging. Production deploys
require the `deployer` role, and between 17:00 Friday and 09:00 Monday they also
require `--break-glass` plus an incident ID. Quokka posts every production
deploy to the team's Slack channel, including the break-glass ones.
