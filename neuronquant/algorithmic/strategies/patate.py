from zipline.algorithm import TradingAlgorithm
import numpy as np


class MarkovGenerator(TradingAlgorithm):
    '''
    Build a probabilist state graph from input data
    from to permit Markov regression
    '''

    def initialize(self, properties):

        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)
        self.loops = 0

        self.data_size = 5
        tmin = np.ones([self.data_size])
        tmax = np.zeros([self.data_size])
        self.tab_minmax = np.column_stack([tmin, tmax])

        self.input_data = np.zeros([self.data_size])

        # phase 1
        self.states = []
        self.states_id = 1

        # phase 2
        self.matrix = WhoNext()

    def handle_data(self, data):
        self.loops += 1
        ''' --------------------------------------------------    Init   --'''
        if self.initialized:
            user_instruction = self.manager.update(
                self.portfolio,
                self.datetime.to_pydatetime(),
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save,
                widgets=False
            )
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        for sid in data:
            #data frame type
            self.input_data[0] = data[sid].Open
            self.input_data[1] = data[sid].High
            self.input_data[2] = data[sid].Low
            self.input_data[3] = data[sid].Close
            self.input_data[4] = data[sid].volume

            alpha = np.zeros([self.data_size])

            # mobile normalize
            for i in xrange(self.data_size):
                if self.tab_minmax[i][0] > self.tab_minmax[i][1]:
                    self.tab_minmax[i][0] = self.input_data[i]
                    self.tab_minmax[i][1] = self.input_data[i]
                    alpha[i] = -1.0
                elif self.input_data[i] < self.tab_minmax[i][0]:
                    self.tab_minmax[i][0] = self.input_data[i]
                    alpha[i] = 0.0
                elif self.input_data[i] > self.tab_minmax[i][1]:
                    self.tab_minmax[i][1] = self.input_data[i]
                    alpha[i] = 1.0
                elif self.tab_minmax[i][0] != self.tab_minmax[i][1]:
                    #normalize
                    tmp0 = self.input_data[i] - self.tab_minmax[i][0]
                    tmp1 = self.tab_minmax[i][1] - self.tab_minmax[i][0]
                    alpha[i] = tmp0 / tmp1
                else:
                    #alpha = -1 #error or data unupdated yet
                    alpha[i] = -1.0

            #distance evaluation # ps : factorisable
            #and add input to states
            if len(self.states):
                state = None
                beta = 1.0  # range max
                #match with states already poped?
                for i in xrange(len(self.states)):
                    beta0 = self.states[i].eval_range(alpha)
                    if beta0 < beta:
                        beta = beta0
                        state = self.states[i]
                if state:
                    #yes, amomomomo => check the expected value
                    state.add_input(alpha)

                    # Compare with planned result
                    self.matrix.compare(state)
                else:
                    #nop, build a new one => awe, update the transfert matrix, it sucks
                    state = State(self.data_size, self.states_id)
                    state.add_input(alpha)
                    self.states.append(state)
                    self.states_id += 1
                    #add the new state to the matrix index
                    self.matrix.add_state(state)

            else:
                #no state on the queue, build the first one!
                state = State(self.data_size, self.states_id)
                state.add_input(alpha)
                self.states.append(state)
                self.states_id += 1

                self.matrix.add_state(state)

                #self.states is the output of the state graph builder

        #phase 2 : WhoNext?
        self.matrix.expect()

        #phase 3 : Markov Regression


class WhoNext(object):
    '''build the n by n transfert matrice for the state graph'''
    def __init__(self):
        #NB : self.index and the self.state from the main class are the same array
        self.index = [0]
        #this array ll help us to determine the efficiency of the basic probabilist approach
        self.result = [[0, 0]]
        #size of the index, this variable is used to a more explicit programming
        self.size = 1
        #count the number of input in a edge
        self.matrix_occurence = np.array([0])
        #eval the probability from the matrix occurence, could use other source
        self.matrix_probability = np.array([0.0])

        self.current_state = 0
        self.state_id_expected = 0

    def add_state(self, state):
        #add a new state to the system
        self.index.append(state.name)
        self.result.append([0, 0])

        right_builder = []
        sub_builder = []
        for i in xrange(self.size):
            right_builder.append(0)
            sub_builder.append(0)

        #cos size(sub) = size(right)+1
        sub_builder.append(0)

        right = np.array(right_builder)
        sub = np.array(sub_builder)

        self.matrix_occurence = np.column_stack([self.matrix_occurence, right])
        self.matrix_occurence = np.transpose(self.matrix_occurence)
        self.matrix_occurence = np.column_stack([self.matrix_occurence, sub])
        self.matrix_occurence = np.transpose(self.matrix_occurence)

        self.matrix_probability = np.column_stack([self.matrix_probability, right])
        self.matrix_probability = np.transpose(self.matrix_probability)
        self.matrix_probability = np.column_stack([self.matrix_probability, sub])
        self.matrix_probability = np.transpose(self.matrix_probability)

        #update value after building system, 0 by default
        self.matrix_occurence[0][self.size] += 1

        #update the univers row. As every state born one time from it, the probability
        ##to build it is 1/number_of_state
        for i in xrange(self.size):
            self.matrix_probability[0][i] = 1.0 / (self.size+1)

        if self.current_state :
            self.matrix_occurence[self.current_state][self.size] = 1

            if self.state_id_expected:
                #cos of a bad prediction => bad mark
                self.result[self.current_state][1] += 1
            #else, if 0 was planned, that's not a bad prediction cos indeed, this new state born from state0
            else:
                self.result[self.current_state][0] += 1

            _sum = np.sum(self.matrix_occurence[self.current_state])
            for i in xrange(self.size):
                #TODO use external data source and merge with the occurence one
                self.matrix_probability[self.current_state][i] = self.matrix_occurence[self.current_state][i] / _sum

        self.size += 1

    def expect(self):
        #read the n by n transition matrix to expect the next one
        ## is it important to search hidden node from this dataframe
        ### from current_state get highest probability value

        if self.current_state:
            self.state_id_expected = 0
            _max = 0
            for i in xrange(self.size):
                if _max < self.matrix_probability[self.current_state][i]:
                    _max = self.matrix_probability[self.current_state][i]
                    self.state_id_expected = i;
                    #TODO : choose also from the density value of the targeted state, need an access to it
        else:
            self.state_id_expected = self.size #predict a new one! this is a default approch from the universe state

    def compare(self, state):
        #if self.index(state.name):
        if state.name in self.index:
            if state.name == self.state_id_expected:
                #WELL DONE BRO
                self.matrix_occurence[self.current_state][self.state_id_expected] +=1
                self.result[self.current_state][0] +=1
            else:
                #bad luck :/
                self.matrix_occurence[self.current_state][state.name] +=1
                self.result[self.current_state][1] +=1

            #update probability matrix

            _sum = np.sum(self.matrix_occurence[self.current_state])
            for i in xrange(self.size):
                #TODO use external data source and merge with the occurence one
                self.matrix_probability[self.current_state][i] = self.matrix_occurence[self.current_state][i] / _sum

            #update current_state
            self.current_state = state.name

        else:
            #error, state havn't been indexed
            return


class State(object):
    def __init__(self, dimension, name):
        self.name = name
        self.dim = dimension
        self.core = np.zeros([dimension])
        self.size = 0
        self.range = 0.1  # 10%

    #get normalize data
    def add_input(self, data):
        if len(data) == self.dim:
            #barycentric build
            for i in xrange(self.dim):
                weight0 = self.size * self.core[i] + data[i]
                weight1 = self.size + 1.0
                self.core[i] = weight0/weight1
            #update
            self.size += 1
            #this define how the state growth according to his size
            self.range = self.range / np.math.sqrt(self.size)

    def eval_range(self, data):
        if len(data) == self.dim:
            _sum = 0.0
        for i in xrange(self.dim):
            _sum += pow(self.core[i] - data[i], 2)
        #normalize
        beta = np.math.sqrt(_sum) / np.math.sqrt(self.dim)
        if beta <= self.range:
            return beta
        else:
            return 1.0
