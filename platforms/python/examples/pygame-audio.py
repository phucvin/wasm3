#!/usr/bin/env python3

import os, struct, time
import multiprocessing as mp
import wasm3
import numpy

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "true"

def consumer(conn):
    import pygame
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)
    pygame.init()

    channel = pygame.mixer.Channel(0)
    while True:
        chunk = pygame.mixer.Sound(buffer=conn.recv())

        indicator = '|' if channel.get_queue() else '.'
        print(indicator, end='', flush=True)
        while channel.get_queue() != None:
            time.sleep(0.01)

        channel.queue(chunk)

    pygame.quit()


if __name__ == '__main__':
    print("Hondarribia - Intro song WebAssembly Summit 2020 by Peter Salomonsen")
    print("Source:      https://petersalomonsen.com/webassemblymusic/livecodev2/?gist=5b795090ead4f192e7f5ee5dcdd17392")
    print("Synthesized: https://soundcloud.com/psalomo/hondarribia")

    conn, child_conn = mp.Pipe()
    p = mp.Process(target=consumer, args=(child_conn,))
    p.start()

    scriptpath = os.path.dirname(os.path.realpath(__file__))
    wasm_fn = os.path.join(scriptpath, "./wasm/hondarribia.wasm")

    # Prepare Wasm3 engine

    env = wasm3.Environment()
    rt = env.new_runtime(1024)
    with open(wasm_fn, "rb") as f:
        mod = env.parse_module(f.read())
        rt.load(mod)

    buff = b''
    buff_sz = 256
    print("Pre-buffering...")

    def fd_write(fd, wasi_iovs, iows_len, nwritten):
        global buff, buff_sz
        mem = rt.get_memory(0)

        # decode
        (off, size) = struct.unpack("<II", mem[wasi_iovs:wasi_iovs+8])
        arr = numpy.frombuffer(mem[off:off+size], dtype=numpy.float32) * 32768
        buff += arr.astype(numpy.int16).tobytes()

        # buffer
        if len(buff) > buff_sz*1024:
            conn.send(buff)
            buff = b''
            buff_sz = 64

        return size

    mod.link_function("wasi_unstable", "fd_write", "i(i*i*)", fd_write)

    wasm_start = rt.find_function("_start")
    wasm_start()

    p.join()
