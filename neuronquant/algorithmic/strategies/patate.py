#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zipline.algorithm import TradingAlgorithm
import numpy as np
import copy

#format de la donnée
def get_input_fields(data, ignored):
    assert len(data.items())
    one_sid_event = data.items()[0][1]
    unused_fields = ['datetime', 'sid', 'source_id', 'dt', 'type'] + ignored
    #unused_fields.update(ignored)
    data_fields = one_sid_event.__dict__.keys()
    return [field for field in data_fields if field not in unused_fields]


class MarkovGenerator(TradingAlgorithm):
    '''
    Build a probabilist state graph from input data
    from to permit Markov regression
    '''

    def initialize(self, properties):
        self.vect_value = []
        self.vect_fft = []


        self.count = 0

        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)
        self.ignored = properties.get('ignored', [])
        if not isinstance(self.ignored, list):
            self.ignored = [self.ignored]

        self.input_data = []
        self.scope = 5

        self.state1 = 0

        self.next1 = 0

        self.transfert1 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        #self.transfert1 = [[0.5, 0.358695652173913, 0.08695652173913043, 0.05434782608695652], [0.4411764705882353, 0.3088235294117647, 0.14705882352941177, 0.10294117647058823], [0.19642857142857142, 0.17857142857142858, 0.2857142857142857, 0.3392857142857143], [0.08163265306122448, 0.10204081632653061, 0.4489795918367347, 0.3673469387755102]]
        self.transfert1 = [[0.511166253101737, 0.3829611248966088, 0.07030603804797353, 0.03556658395368073], [0.4066037735849057, 0.2981132075471698, 0.17452830188679244, 0.12075471698113208], [0.13178294573643412, 0.21705426356589147, 0.3067552602436323, 0.3444075304540421], [0.04026115342763874, 0.0957562568008705, 0.38737758433079433, 0.4766050054406964]]


        self.frequence1 = [0,0,0,0]

        self.occurence1 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        #self.occurence1 = [[46, 33, 8, 5], [30, 21, 10, 7], [11, 10, 16, 19], [4, 5, 22, 18]]
        #self.occurence1 = [[92, 66, 16, 10], [60, 42, 20, 14], [22, 20, 32, 38], [8, 10, 44, 36]]
        #self.occurence1 = [[138, 99, 24, 15], [90, 63, 30, 21], [33, 30, 48, 57], [12, 15, 66, 54]]
        #self.occurence1 = [[618, 463, 85, 43], [431, 316, 185, 128], [119, 196, 277, 311], [37, 88, 356, 438]]
        #self.occurence1 = [[1098, 827, 146, 71], [772, 569, 340, 235], [205, 362, 506, 565], [62, 161, 646, 822]]



        self.result1 = [0,0]

        self.memory = []

        #trigger variable
        self.scope_average = [0,0,0,0,0]
        self.min = [0,0,0,0,0]
        self.max = [0,0,0,0,0]

        #input counter for init
        self.init = 0

	#compute the scope
    def _average(self):
	_sum = [0,0,0,0,0]

	for ohlc in self.memory:
		for i in xrange(len(ohlc)):
			_sum[i] += ohlc[i]

	for i in xrange(self.data_size):
		self.scope_average[i] = _sum[i]/self.scope

    def _min(self):
	self.min = [0,0,0,0,0]

	for i,value in enumerate(self.memory[0]):
		self.min[i] = value
	for ohlc in self.memory:
		for i,value in enumerate(ohlc):
			if self.min[i] > value:
				self.min[i] = value

    def _max(self):
	self.max = [0,0,0,0,0]
	for i,value in enumerate(self.memory[0]):
		self.max[i] = value
	for ohlc in self.memory:
		for i,value in enumerate(ohlc):
			if self.max[i] < value:
				self.max[i] = value

    def trigger(self,data):
	#self.vect_fft.append(data[0])
	self.vect_value.append(data[0])
	#format de la donnée
	self._average()
	self._min()
	self._max()

	#donne l'état correspondant dans la dimension
	#ont les mêmes critères quelque soit la dimension
	selector = [0,0,0,0,0]

	for i,value in enumerate(data):
	    if value <= self.min[i]:
		selector[i] = 3
	    elif value >= self.max[i]:
		selector[i] = 0
	    else :
		if value < self.scope_average[i]:
		    selector[i] = 2
		elif value > self.scope_average[i]:# >= ???
		    selector[i] = 1
		else:
		    print 'error'

	return selector

    def get_next1(self):
        _max = self.transfert1[self.state1][0]
        next = 0
        for i,value in enumerate(self.transfert1[self.state1]):
            if _max < value:
                _max = value
                next = i
        self.next1 = next

    def push(self, data):
        self.memory.pop(0)
        self.memory.append(copy.deepcopy(data))

    def handle_data(self, data):

        self.count += 1
        signals = {}

        ''' --------------------------------------------------    Init   --'''
        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime.to_pydatetime(),
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False
            )
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True
            self.input_fields = get_input_fields(data, self.ignored)
            self.data_size = len(self.input_fields)

        for sid in data:
            break
            #data frame type

	    input_data = []
	    for _ in xrange(self.data_size):
		    input_data.append(0.0)

            for i, field in enumerate(self.input_fields):
                input_data[i] = data[sid][field]

	    if self.init < self.scope:
	    	self.init += 1
		self.memory.append(input_data)
	    	return
	    else :

	    	selector = self.trigger(input_data)

		self.frequence1[selector[0]] +=1

	    	#repeat for each dimension...
	    	if self.next1 == selector[0]:
			self.result1[0] += 1
	   	else :
			self.result1[1] += 1

	    	self.occurence1[self.state1][selector[0]] +=1
	    	_sum = 0.0
	    	for emission in self.occurence1[self.state1]:
			_sum += emission

	    	for i, value in enumerate(self.occurence1[self.state1]):
			self.transfert1[self.state1][i] = value / _sum

	    	#the input state become the current one
	    	self.state1 = selector[0]

	    	self.get_next1()

	    	self.push(input_data)

		if self.count == 172:
			print 'transferts'
			print self.transfert1
			print 'occurence'
			print self.occurence1
			print 'results'
			print 'bon : {0} , mauvais : {1}'.format(self.result1[0],self.result1[1])

			for i, line in enumerate(self.frequence1):
				print 'state{0} : {1}'.format(i,line)

			_sum = 0.0
			_sum += sum(self.frequence1)

			for i, line in enumerate(self.frequence1):
				print 'state{0} freq : {1}'.format(i,line/_sum)

			'''import matplotlib.pyplot as plt
			value = np.array(self.vect_value)
			plt.plot(value)
			plt.title("Data_Source")
			plt.xlabel("Date")
			plt.ylabel("Value")
			plt.show()'''

			#import numpy as np
			import pylab as py
			import scipy as sc

			#Fs = size_input
			#Fs = 150.0;  # sampling rate
			Fs = 365

			Ts = 1.0/Fs; # sampling interval

			Duration = len(self.vect_value) / 365
			diff = len(self.vect_value)%365
			value = self.vect_value[:-diff]

			t = sc.arange(0,Duration,Ts) # time vector

			print len(t)
			print len(value)

			signal = np.array(value)

			py.subplot(2,1,1)
			py.plot(t,signal)
			py.xlabel('Time')
			py.ylabel('Amplitude')
			py.subplot(2,1,2)

			#plotSpectrum(y,Fs)
			#def plotSpectrum(y,Fs):
			n = len(signal) # length of the signal
			k = sc.arange(n)
			T = n/Fs
			frq = k/T # two sides frequency range
			frq = frq[range(n/2)] # one side frequency range

			Y = sc.fft(signal)/n # fft computing and normalization
			Y = Y[range(n/2)]

			frq = frq[1:150]
			Y = Y[1:150]


			py.plot(frq,abs(Y),'r') # plotting the spectrum
			py.xlabel('Freq (Hz)')
			py.ylabel('|Y(freq)|')

			py.show()
