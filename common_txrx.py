import numpy
import math
import operator

import binascii
# Methods common to both the transmitter and receiver.

def lpfilter(samples_in, omega_cut):
    '''
    A low-pass filter of frequency omega_cut.
    '''

    L = 50
    samples_out = []

	# set the filter unit sample response
    h = []
    for n in range(-L, L+1):
    	if(n == 0):
    		h.append(omega_cut / math.pi)
    	else:
    		h.append(math.sin(omega_cut * n) / (math.pi*n))
    # convolve unit sample response with input samples
    for n in range(0, len(samples_in)):
    	lower = 0 if n - L < 0 else n - L
    	upper = len(samples_in) - 1 if n + L > len(samples_in) - 1 else n + L + 1
    	h_lower = lower
    	h_upper = len(h) if n + L <= len(samples_in) - 1 else len(h) + ((len(samples_in) - 1) -  (n + L + 1)) 
    
    	s_range = samples_in[lower:upper]
    	h_range = h[h_lower:h_upper]
        sums = 0
    	for i in range(0, len(h_range)):
      		sums += s_range[i] * h_range[i]
    	samples_out.append(sums)
    
    return numpy.array(samples_out)

def bits_to_samples(bits, spb, one):
        '''
        Convert each bits into [spb] samples. 
        Sample values for bit '1', '0' should be [one], 0 respectively.
        Output should be an array of samples.
        '''
        samples = []
        for i in range(len(bits)):
            for j in range(spb):
                if bits[i] == 0: samples.append(0)
                if bits[i] == 1: samples.append(one)
        return samples
        
