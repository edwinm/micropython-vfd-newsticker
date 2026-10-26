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

        # Parse straight off the socket so the whole feed never has to live in
        # RAM at once (res.text would buffer the body and a decoded copy). A
        # read timeout keeps a stalled transfer from freezing the ticker; the
        # OSError handler below then reboots.
        try:
            res.raw.settimeout(15)
        except Exception:
            pass
        items = parseFeed(res.raw, maxItems)
        res.close()

        text = SEPARATOR + SEPARATOR.join(items)

        ticker(text)


def parseFeed(sock, maxItems):
    global display
    inItem = False
    inTitle = False
    items = []

    stream = ResponseStream(sock)

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
                title = title.replace('&#039;', '\x03')
                title = title.replace('\u2018', '\x02')
                title = title.replace('\u2019', '\x03')
                title = title.replace('&quot;', '\x04')

                print("> " + title)
                items.append(title)
            if len(items) == maxItems:
                break
    return items
    

# To prevent crashes due to memory leaks, reset before updating feed
def resetTicker(pin):
    reset()


class ResponseStream:
    # Reads an HTTP response body straight off the socket one character at a
    # time, decoding UTF-8 on the fly, so the whole feed is never buffered in
    # RAM. parseFeed stops after maxItems, so only the first items get read.
    def __init__(self, sock, bufsize=64):
        self.sock = sock
        self.bufsize = bufsize
        self.pending = b""
        self.chars = ""
        self.pos = 0
        self.eof = False

    def read(self, n):
        if self.pos >= len(self.chars):
            self._decode_more()
            if self.pos >= len(self.chars):
                return ""
        char = self.chars[self.pos]
        self.pos = self.pos + 1
        return char

    def _decode_more(self):
        self.chars = ""
        self.pos = 0
        while True:
            cut = self._complete_prefix(self.pending)
            if cut:
                self.chars = self.pending[:cut].decode()
                self.pending = self.pending[cut:]
                return
            if self.eof:
                return
            chunk = self.sock.read(self.bufsize)
            if not chunk:
                self.eof = True
                if self.pending:
                    try:
                        self.chars = self.pending.decode()
                    except Exception:
                        self.chars = ""
                    self.pending = b""
                return
            self.pending = self.pending + chunk

    @staticmethod
    def _complete_prefix(b):
        # Number of leading bytes that form whole UTF-8 characters; a trailing
        # partial multi-byte sequence is held back for the next read.
        n = len(b)
        if n == 0:
            return 0
        i = n - 1
        while i > 0 and 0x80 <= b[i] <= 0xBF:
            i = i - 1
        lead = b[i]
        if lead < 0x80:
            expected = 1
        elif lead < 0xE0:
            expected = 2
        elif lead < 0xF0:
            expected = 3
        else:
            expected = 4
        if n - i < expected:
            return i
        return n



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
  *
  *
 *



""")
    
    display.define_character(4,
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




