from uctypes import addressof
import array
import rp2
import time
import machine
import dma_defs
import pio_defs
import vos_debug

# read_debug = machine.Pin(26, machine.Pin.OUT)

num_frames            = const(16)
num_samples_per_frame = const(1024)
bytes_per_sample      = const(4)
data_length     = const(num_frames * num_samples_per_frame *  bytes_per_sample)
#colors = [0x01000000 * i for i in range(1, num_frames + 1)]
colors = [0xFFFF0000 for i in range(1, num_frames + 1)]

class Buffer():

    def __init__(self):

        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_WARNING,"Buffer init start")
        self.num_samples_per_frame = num_samples_per_frame
        ## Setup storage for frames of samples
        self.data = bytearray(data_length)

		# Define a list of 16 colors (in this example, simple gradient from 0x00000000 to 0x0F000000)
	    ## Fill each frame with its respective color
        #for frame_index in range(num_frames):
        #    start_pos = frame_index * self.num_samples_per_frame * bytes_per_sample
        #    end_pos = start_pos + self.num_samples_per_frame * bytes_per_sample
        #    color_bytes = colors[frame_index].to_bytes(bytes_per_sample, 'little')
        #    for i in range(start_pos, end_pos, bytes_per_sample):
        #        self.data[i:i+bytes_per_sample] = color_bytes
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_WARNING,"Buffer init 2")

        ## and the individual frames start here
        self.frame_starts = array.array("L", [addressof(self.data) + i*num_samples_per_frame*bytes_per_sample for i in range(num_frames)])
        self.current_frame = 0
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_WARNING,"init done")
