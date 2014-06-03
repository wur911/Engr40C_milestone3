import sys
import math
import numpy
import matplotlib.pyplot as p
import scipy.cluster.vq
import common_txrx as common
from graphs import *
from numpy import linalg as LA

import hamming_db
import channel_coding as cc

class Receiver:
    def __init__(self, carrier_freq, samplerate, spb):
        '''
        The physical-layer receive function, which processes the
        received samples by detecting the preamble and then
        demodulating the samples from the start of the preamble 
        sequence. Returns the sequence of received bits (after
        demapping)
        '''
        self.fc = carrier_freq
        self.samplerate = samplerate
        self.spb = spb 
        self.preamble = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        print 'Receiver: '

    def detect_threshold(self, demod_samples):
        '''
        Returns representative sample values for bit 0, 1 and the threshold.
        Use kmeans clustering with the demodulated samples
        '''
        # fill in your implementation 
        one = 1.0
        zero = 0.0
        newone = 2.0
        newzero = -1.0
        while newone-one > 0.01 and zero-newzero > 0.01:
            onecluster = []
            zerocluster = []
            for val in demod_samples:
                if one-val < val-zero:
                    onecluster.append(val)
                else:
                    zerocluster.append(val)
            newone = sum(onecluster)/len(onecluster)
            newzero = sum(zerocluster)/len(zerocluster)
        one = newone
        zero = newzero
        thresh = (one+zero)/2

        return one, zero, thresh

    def energycheck(self, demod_samples, thresh, one):
        for i in range(0, len(demod_samples)+1 - self.spb):
            window = demod_samples[i: i + self.spb]
            quarter = len(window)/4
            avg = numpy.average(window[quarter:len(window)-quarter])
            if avg > (one + thresh)/2.0:
                return i
        return 0
 

    def findPreambleOffset(self, demod_samples, offset):
        preamble_samples = common.bits_to_samples(self.preamble, self.spb, self.one)
        preamble_length = len(preamble_samples)
        upperBound =  offset + 3 * preamble_length;
        index = 0
        max_correlation = 0
        for i in range(offset, upperBound):
            norm = LA.norm(demod_samples[i: i + preamble_length])
            correlation = numpy.correlate(preamble_samples, demod_samples[i: i + preamble_length])/norm
            if correlation > max_correlation:
                max_correlation = correlation
                index = i

        return index-offset

    def detect_preamble(self, demod_samples, thresh, one):
        '''
        Find the sample corresp. to the first reliable bit "1"; this step 
        is crucial to a proper and correct synchronization w/ the xmitter.
        '''
        
        '''
        First, find the first sample index where you detect energy based on the
        moving average method described in the milestone 2 description.
        '''
        # Fill in your implementation of the high-energy check procedure

        # Find the sample corresp. to the first reliable bit "1"; this step 
        # is crucial to a proper and correct synchronization w/ the xmitter.

        offset =  self.energycheck(demod_samples, thresh, one);
        if offset < 0:
            print '*** ERROR: Could not detect any ones (so no preamble). ***'
            print '\tIncrease volume / turn on mic?'
            print '\tOr is there some other synchronization bug? ***'
            sys.exit(1)

        '''
        Then, starting from the demod_samples[offset], find the sample index where
        the cross-correlation between the signal samples and the preamble 
        samples is the highest. 
        '''
        # Fill in your implementation of the cross-correlation check procedure
        pre_offset = self.findPreambleOffset(demod_samples, offset);
        '''
        [pre_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''

        return offset + pre_offset
        
    def demap_and_check(self, demod_samples, barker_start):
        '''
        Demap the demod_samples (starting from [preamble_start]) into bits.
        1. Calculate the average values of midpoints of each [spb] samples
           and match it with the known preamble bit values.
        2. Use the average values and bit values of the preamble samples from (1)
           to calculate the new [thresh], [one], [zero]
        3. Demap the average values from (1) with the new three values from (2)
        4. Check whether the first [preamble_length] bits of (3) are equal to
           the preamble. If it is proceed, if not print an error message and 
           terminate the program. 
        Output is the array of data_bits (bits without preamble)
        '''

        # Fill in your implementation
        zerovals = []
        onevals = []
        for i in range(0,len(self.preamble)):
            midpoint = demod_samples[barker_start + self.spb/4 + i*self.spb : barker_start + 3*self.spb/4 + i*self.spb]
            average = 2*sum(midpoint)/self.spb
            if self.preamble[i] == 0:
                zerovals.append(average)
            else:
                onevals.append(average)
        zero = sum(zerovals)/len(zerovals)
        one = sum(onevals)/len(onevals)
        thresh = (zero+one)/2
        
        data_bits = []
        for i in range(0,(len(demod_samples)-barker_start)/self.spb):
            midpoint = demod_samples[barker_start + self.spb/4 + i*self.spb : barker_start + 3*self.spb/4 + i*self.spb]
            average = 2*sum(midpoint)/self.spb
            if average > thresh:
                data_bits.append(1)
            else:
                data_bits.append(0)
        for i in range(0,len(self.preamble)):
            if self.preamble[i] != data_bits[i]:
                print "Cannot read preamble. Exiting..."
                sys.exit(1)
        output = data_bits[len(self.preamble)]
        
        return numpy.array(output)

    def demodulate(self, samples):
        '''
        Perform quadrature modulation.
        Return the demodulated samples.
        '''
        # fill in your implementation
        demod_samples = []
        demod_unfilter_samples = []
        for i in range(len(samples)):
            demod = samples[i] * math.e**(1j*2*math.pi*(float(self.fc)/self.samplerate)*i)
            demod_unfilter_samples.append(demod)
        print demod_unfilter_samples
        demod_filter = common.lpfilter(demod_unfilter_samples,math.pi*(float(self.fc)/self.samplerate))
        demod_samples = []
        for i in range(len(demod_filter)):
            demod_samples.append(abs(demod_filter[i]))
        return demod_samples

    def decode(self, recd_bits):
        return cc.get_databits(recd_bits)
