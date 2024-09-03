# MicroPython VFD news ticker

>News ticker for the 16 segment VFD display

Scroll the news items from your favourite news organization on a VFD display.

## Hardware

You need an ESP32 dev board and a 16 segment VFD display:

- Esp32 C3 Supermini board
- Futaba 16 segment VFD display

## Micropython

Make sure Micropython is installed on the ESP32.

[Getting started with MicroPython on the ESP32](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

## Configuration

Edit the file `config.py` and set the url of the RSS feed of your favourite news organization.
The default is the feed of CBS world news.
You can optionally set words so that items containing those words will be skipped.

Also set the name of your WiFi access point and the WiFi password.

When all changes are made, upload all Python files to the ESP32.
A beginners friendly way to do this is by using [Thonny](https://thonny.org/).

> [!NOTE]  
> Some RSS feeds don't work well. They can be too big causing memory problems
> or they contain the XML `<![CDATA[` section that the current XML parser can't handle.

## Source

The source of this project is writting in Python.

[micropython-vfd-newsticker](https://github.com/edwinm/micropython-vfd-newsticker) (news ticker)
[micropython-vfd-driver](https://github.com/edwinm/micropython-vfd-driver) (VFD 16 segment driver)

Both are MIT licensed.

## License

Copyright 2024 [Edwin Martin](https://bitstorm.org/) and released under the [MIT license](LICENSE).
