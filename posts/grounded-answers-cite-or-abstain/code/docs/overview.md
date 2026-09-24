# Quill 2 weather station - overview

The Quill 2 is a battery-powered outdoor sensor unit. It records air
temperature, relative humidity, barometric pressure and rainfall. Each reading
is written to the microSD card as a row of CSV, and a summary packet is sent
over the 869.5 MHz radio uplink to the base station every 15 minutes.

The default sampling interval is 90 seconds. Every sample carries a timestamp
from the on-board clock, which is resynchronised from the base station on each
successful uplink.

The unit ships with firmware 2.4.1 and a 4 GB microSD card. The three status
LEDs on the underside mean: green for a normal cycle, amber while writing to
the card, red for any error condition listed in the error reference.

Readings are kept on the card indefinitely; the Quill 2 never deletes old
files. A 4 GB card holds roughly 11 years of CSV at the default interval, so
in practice you copy files off when you visit the site and leave the card
alone.
