import math
import common_txrx as common
import numpy

import hamming_db
import channel_coding as cc
 
class Transmitter:
    def __init__(self, carrier_freq, samplerate, one, spb, silence, cc_len):
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.one = one
        self.spb = spb
        self.silence = silence
        self.cc_len = cc_len
        self.preamble = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        print 'Transmitter: '
        
    def add_preamble(self, databits):
        '''
        Prepend the array of source bits with silence bits and preamble bits
        The recommended preamble bits is 
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        The output should be the concatenation of arrays of
            [silence bits], [preamble bits], and [databits]
        '''
        
        # fill in your implementation
        databits_with_preamble = []
        for i in range(self.silence):
            databits_with_preamble.append(0)
        databits_with_preamble += self.preamble
        databits_with_preamble += databits
        print '\tSent Preamble: ', self.preamble
        return databits_with_preamble

    def bits_to_samples(self, bits):
        '''
        Convert each bits into [spb] samples. 
        Sample values for bit '1', '0' should be [one], 0 respectively.
        Output should be an array of samples.
        '''
        return common.bits_to_samples(bits, self.spb, self.one);
        
    def modulate(self, samples):
        '''
        Multiply samples by a local sinusoid carrier of the same length.
        Return the multiplied result.
        '''
        mod_samples = []

        omega_cut = 2*math.pi*(self.fc/self.samplerate);
        for i in range(len(samples)):

            modded_sample = samples[i] * math.cos(2*math.pi*(float(self.fc)/self.samplerate)*i)
            mod_samples.append(modded_sample)
        # fill in your implementation
        print '\tNumber of samples being sent:', # fill in here
        mod_samples = common.lpfilter(mod_samples, omega_cut)

        return mod_samples
        
    def encode(self, databits, cc_len):
        '''
        Wrapper function for milestone 2. No need to touch it        
        '''
        return cc.get_frame(databits, cc_len)
