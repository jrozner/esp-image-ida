# esp-image-ida

This is a loader for the esp-idf application images for IDA Pro You'll want to install the xtensa processor module as well available https://github.com/themadinventor/ida-xtensa or https://github.com/jrozner/ida-xtensa (my fork with some fixes) in order to actually get it to disassemble. This is just to load the images.

This is some pretty crappy code and I don't know Python but it seems to work. Will eventually get around to adding ESP8266 support and building a real module.

## Installation

Drop this into your `$IDAUSER/loaders/` or `$IDADIR/loaders/` directory and IDA should automatically load it.
