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
        centroid1 = min(demod_samples)
        centroid2 = max(demod_samples) 
        prev1 = 0
        prev2 = 0

        # insert code to implement 2-means clustering     
        while ((centroid1 != prev1) and (centroid2 != prev2)):
            prev1 = centroid1
            prev2 = centroid2
            sum1 = 0
            sum2 = 0
            count1 = 0
            count2 = 0

            for n in range(len(demod_samples)):
              sample = demod_samples[n];
              if(abs(sample-centroid1) <= abs(sample-centroid2)):
                sum1 += sample
                count1 += 1
              else:
                sum2 += sample
                count2 += 1

            centroid1 = sum1/count1
            centroid2 = sum2/count2

        zero = centroid1
        one = centroid2
        thresh = (zero + one)/2
        
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
        pass

    def demodulate(self, samples):
        '''
        Perform quadrature modulation.
        Return the demodulated samples.
        '''
        demod_samples = []
        omega_cut = math.pi*(self.fc/self.samplerate)
        for i in range(len(samples)):
            demodded_sample = samples[i] * numpy.exp(1j*2*omega_cut*i);
            demod_samples.append(demodded_sample)
        # fill in your implementation
        for i in range(len(demod_samples)):
            LA.norm(demod_samples[i])
        demod_samples = lpfilter(demod_samples, omega_cut)
        return demod_samples

    def decode(self, recd_bits):
        return cc.get_databits(recd_bits)
