import time
import network
import urequests as requests
from machine import Pin, Timer, reset
import vfd_16
import xmltok2
import config

display = vfd_16.Display(cs=4, clk=3, sdi=6, spi_id=1, dimming=100)

def main():
    global display
    maxItems = 10
    SEPARATOR = " \x01\x01\x01 "
    refreshTime = 60 * 30 # 30 minutes

    timer = Timer(0)
    timer.init(mode=Timer.ONE_SHOT, period=refreshTime * 1000, callback=resetTicker)

    customCharacters(display)

    display.clear()
    display.write('\x00 Connecting...')

    while True:
        do_connect()

        display.clear()
        display.write('\x00 Getting feed...')
        print("Fetching " + config.RSS_FEED_URL)

        res = requests.get(url=config.RSS_FEED_URL)

        display.clear()
        display.write('\x00 Parsing...')

        # res.text = res.text.replace('<![CDATA[', '').replace(']]>', '')

        items = parseFeed(res.text, maxItems)

        text = SEPARATOR + SEPARATOR.join(items)

        ticker(text)


def parseFeed(feed, maxItems):
    global display
    inItem = False
    inTitle = False
    items = []

    stream = TextStream(feed)

    for i in xmltok2.tokenize(stream):
        token, title, tag, ns = i
        if token == xmltok2.START_TAG:
            if tag == "item":
                inItem = True
            elif tag == "title":
                inTitle = True
        elif token == xmltok2.END_TAG:
            if tag == "item":
                inItem = False
            elif tag == "title":
                inTitle = False
        elif token == xmltok2.TEXT and inItem and inTitle:
            display.write(chr(ord('0') + (len(items) + 1) % 10), 15)
            skipTitle = False
            for skipWord in config.SKIP_WORDS:
                if title.find(skipWord) != -1:
                    skipTitle = True
            if skipTitle:
                print("X " + title)
            else:
                title = title.replace('&#039;', '\x02')
                title = title.replace('&quot;', '\x03')

                print("> " + title)
                items.append(title)
            if len(items) == maxItems:
                break
    return items
    

# To prevent crashes due to memory leaks, reset before updating feed
def resetTicker(pin):
    reset()


class TextStream:
    def __init__(self, text):
        self.text = text
        self.position = 0
        
    def read(self, n):
        if self.position == len(self.text):
            return ""
        
        char = self.text[self.position]
        self.position = self.position + 1
        return char
     
     
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


def customCharacters(display):
    display.define_character(0,
"""

  *
   *
*****
   *
  *
""")
    
    display.define_character(1,
"""


 *** 
*****
 ***


""")
    
    display.define_character(2,
"""
  *
  *
 *



""")

    display.define_character(3,
"""
 * *
 * *
* *



""")
    
def ticker(text):
    fps=6
    position = 0
    display.clear()
    
    while True:
        if position == len(text):
            position = 0
        elif len(text) > 16 and position > len(text) - 16:
            display.write(text[position:len(text)])
            display.write(text[0:16 - position], position=len(text) - position)

        if position < len(text):
            display.write(text[position:position + 16])

        position = position + 1
        time.sleep_ms(int(1000 / fps))


if __name__ == '__main__':
    try:
        main()
    except OSError as exc:
        print('X Exception occured, errno', exc.errno)
        print('Reboot in 10 seconds')
        display.write('Error occured...')
        timer = Timer(0)
        timer.init(mode=Timer.ONE_SHOT, period=10 * 1000, callback=resetTicker)




