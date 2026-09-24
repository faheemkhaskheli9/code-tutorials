# Firmware and configuration

Firmware is updated over the USB-C port with the `quillflash` tool:

    quillflash --port COM3 --image quill-2.4.1.bin

The flash takes about 3 minutes. Do not disconnect power or unplug the cable
while the amber LED is lit; an interrupted flash leaves the unit in recovery
mode, and recovery mode can only be cleared by a second flash over USB-C.

Configuration lives in `quill.cfg` in the root of the microSD card. The file
is plain key=value text and is re-read at every boot. The keys that matter:

    sample_interval = 90      # seconds, 30 to 600
    uplink_minutes  = 15      # 5, 15, 30 or 60
    units           = metric  # metric or imperial
    site_id         = QL-0001

A `sample_interval` outside the 30 to 600 second range is ignored and the unit
falls back to 90 seconds, logging a warning line to `quill.log`.

Calibration coefficients are stored in the firmware image, not in
`quill.cfg`. Recalibrate with `quillflash --calibrate` and the factory
reference kit; the procedure takes about 20 minutes and must be run indoors at
a stable temperature.
