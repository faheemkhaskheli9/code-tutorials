# Error reference

Errors are shown as a red LED pattern and written to `quill.log` on the card.

**E_BATT** - the pack has dropped below 3.4 V. The unit keeps sampling but
stops transmitting on the radio uplink to save power. Replace the pack; the
logged data on the card is not affected.

**E_SD** - no card is present, the card is larger than 128 GB, or it is not
formatted FAT32. Nothing is logged while E_SD is active, so fix it on site
rather than waiting for the next visit.

**E_RADIO** - three consecutive uplinks went unacknowledged. Check that the
base station is powered and within 400 m line of sight, then re-pair. Sampling
continues to the card during E_RADIO.

**E_CAL** - the calibration in the current firmware image is more than 12
months old. Readings are still logged and still transmitted, but they are
flagged `suspect=1` in the CSV until the unit is recalibrated.

**E_SELFTEST** - one of the four sensors failed the boot self-test. The LED
blinks once per failed sensor. A unit in E_SELFTEST does not log at all and
has to be returned.
