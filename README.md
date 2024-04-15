# MicroPython VFD news ticker

>News ticker for the 16 segment VFD display

Scroll the news items from your favourite news organization on a VFD display.

## Hardware

You need an ESP32 dev board and a 16 segment VFD display:

- DOIT ESP32 devkit v1
- Futaba 8-MD-06INKM 16 segment VFD display

## Micropython

Make sure Micropython is installed on the ESP32.

[Getting started with MicroPython on the ESP32](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

## Configuration

Edit the file `config.py` and set the url of the RSS feed of your favourite news organization.
The default is the feed of CBS world news.
You can optionally set words so that items containing those words will be skipped.

Also set the name of your WiFi access point and the WiFi password.

> [!NOTE]  
> Some RSS feeds don't work well. They can be too big causing memory problems
> or they contain the XML `<![CDATA[` section that the current XML parser can't handle.

## License

Copyright 2022 [Edwin Martin](https://bitstorm.org/) and released under the [MIT license](LICENSE).
