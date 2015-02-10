#! /usr/bin/env python3

import asyncio
import monome

class GridStudies(monome.Monome):
    def __init__(self):
        super().__init__('/monome')

    def ready(self):
        self.step = [[0 for col in range(self.width)] for row in range(6)]
        self.loop_start = 0
        self.loop_end = self.width - 1
        self.play_position = 0
        self.next_position = 0
        self.cutting = False
        self.keys_held = 0
        self.key_last = 0

        asyncio.async(self.play())

    @asyncio.coroutine
    def play(self):
        while True:
            if self.cutting:
                self.play_position = self.next_position
            elif self.play_position == self.width - 1:
                self.play_position = 0
            elif self.play_position == self.loop_end:
                self.play_position = self.loop_start
            else:
                self.play_position += 1

            # TRIGGER SOMETHING
            for y in range(6):
                if self.step[y][self.play_position] == 1:
                    self.trigger(y)

            self.cutting = False
            self.draw()

            yield from asyncio.sleep(0.1)

    def trigger(self, i):
        print("triggered", i)

    def draw(self):
        buffer = monome.LedBuffer(self.width, self.height)

        # display steps
        for x in range(self.width):
            # highlight the play position
            if x == self.play_position:
                highlight = 4
            else:
                highlight = 0

            for y in range(6):
                buffer.led_level_set(x, y, self.step[y][x] * 11 + highlight)

        # draw trigger bar and on-states
        for x in range(self.width):
            buffer.led_level_set(x, 6, 4)

        for y in range(6):
            if self.step[y][self.play_position] == 1:
                buffer.led_level_set(self.play_position, 6, 15)

        # draw play position
        buffer.led_level_set(self.play_position, 7, 15)

        # update grid
        buffer.render(self)

    def grid_key(self, x, y, s):
        # toggle steps
        if s == 1 and y < 6:
            self.step[y][x] ^= 1
            self.draw()
        # cut and loop
        elif y == 7:
            self.keys_held = self.keys_held + (s * 2) - 1
            # cut
            if s == 1 and self.keys_held == 1:
                self.cutting = True
                self.next_position = x
                self.key_last = x
            # set loop points
            elif s == 1 and self.keys_held == 2:
                self.loop_start = self.key_last
                self.loop_end = x

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(monome.create_serialosc_connection(GridStudies))
    loop.run_forever()