from vectorscope import Vectorscope

import gc
from vos_debug import debug_print as debug
import vectoros
import vos_state
import vos_debug
import keyboardcb
import keyleds
import keyboardio
import asyncio

_abort=False

async def do_rendering_loop(v):
    while not _abort:
        for i in range(50):
            # simply do nothing
            await asyncio.sleep(0)

def do_abort(key):
    global _abort
    _abort=True


async def vos_main():

    vectoros.get_screen().idle()
    gc.collect()
    vos_state.gc_suspend=True
    # await asyncio.sleep(1)

    v = Vectorscope()

    await do_rendering_loop(v)

    vectoros.reset()



