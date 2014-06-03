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
    
    #pad samples with zeros on either side to pretend like we have an everlasting signal 
    padding = numpy.zeros(50)
    padded_samples = numpy.append(padding, samples_in)
    padded_samples = numpy.append(padded_samples, padding)

    # convolve unit sample response with input samples
    for n in range(0, len(samples_in)):
        c = 0;
        for i in range(len(h)):
            c += h[i] * padded_samples[i]
    	samples_out.append(c)
    
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
        