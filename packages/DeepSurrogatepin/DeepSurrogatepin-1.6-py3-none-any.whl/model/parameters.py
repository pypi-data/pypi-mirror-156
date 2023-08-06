import itertools
from enum import Enum
import numpy as np
import pandas as pd

import sys


##################
# params Enum
##################

class Optimizer(Enum):
    SGD = 1
    SGS_DECAY = 2
    ADAM = 3
    RMS_PROP = 4
    ADAMAX = 5
    NADAM = 5
    ADAGRAD = 5

class Process(Enum):
    PIN = 1
    APIN = 2

class Sampling(Enum):
    RANDOM = 1
    LATIN_HYPERCUBE = 2
    SPARSE_GRID = 3
    GRID_10 = 4
    GIRD_20 = 5
    GRID_LOCALP = 6
    GRID_ZERO = 7
    GRID_15 = 8
    GRID_20_LOCALP = 9
    GRID_20_ZERO = 10
    GRID_30 = 30
    GRID_50 = 12
    GRID_50_bis = 13

class Loss(Enum):
    MSE = 1
    MAE = 2

## add our models
class ParamsProcess:
    def draw_values(self, nb=1, smaller_range=False, mean_value=False):
        d = self.__dict__.copy()
        for k in d.keys():
            if smaller_range:
                min_ = d[k][0]
                max_ = d[k][1]
                delt = max_ - min_
                min_ = min_ + delt * 0.1
                max_ = max_ - delt * 0.1
            else:
                min_ = d[k][0]
                max_ = d[k][1]

            if (type(d[k][0]) == int) & (type(d[k][1]) == int):
                d[k] = np.random.randint(int(np.ceil(min_)), int(np.ceil(max_)) + 1, nb)
            else:
                if mean_value:
                    d[k] = np.array([(min_ + max_) / 2])
                else:
                    d[k] = np.random.uniform(min_, max_, nb)

        return d


class ParamsPin(ParamsProcess):
    def __init__(self):
        self.alpha = [0.0, 1.0]
        self.delta = [0.0, 1.0]
        self.epsilon_b = [200, 300]
        self.epsilon_s = [200, 300]
        self.mu = [200, 300]
        self.buy = [200, 600]
        self.sell = [200, 600]

class ParamsApin(ParamsProcess):
    def __init__(self) -> None:
        pass
    #In construction

class ParamsOption:
    def __init__(self):
        self.process = Process.PIN    

class ParamsModels:
    def __init__(self):
        self.save_dir = './model_save/'
        self.res_dir = './res/'

        self.name = Process.PIN
        self.normalize = True
        self.normalize_range = False
        # performance #
        # 8 layer: 0.8035
        # 7 layer: 0.78
        # 6 layer: 0.81 (VM)
        #self.layers = [400] # 6 hidden layer
        self.layers = [400,400,200,100] # 0.98
        self.batch_size = 256
        self.activation = "swish"
        self.opti = Optimizer.ADAM # use this
        self.loss = Loss.MSE

        self.learning_rate = 0.5e-3

        self.E = 15

class ParamsData:
    def __init__(self):
        self.path_sim_save = './data/'
        self.train_size = 3
        self.test_size = 10000
        # self.cross_vary_list = ["alpha","delta","epsilon_b","epsilon_s","mu","buy","sell"] # put only obsvervable state for backward compatibility
        self.cross_vary_list = ["buy","sell"]
        self.parallel = False

class Params:
    def __init__(self):
        self.name_detail = ''
        self.name = ''
        self.seed = 12345
        self.model = ParamsModels()
        self.data =  ParamsData()
        self.opt = ParamsOption()
  
        self.process = None
        self.update_process()
        # à remettre au prochain entrainement de model
        self.update_model_name()

    def update_process(self, process=None):
        if process is not None:
            self.opt.process = process

        if self.opt.process.name == Process.PIN.name:
            self.process = ParamsPin()

        if self.opt.process.name == Process.APIN.name:
            self.process = ParamsApin()


    def update_model_name(self):
        """
        change model name
        """
        n = self.name_detail
        n += 'Layer_'
        # for l in self.model.layers:
        #     n = n + str(l)+'_'
        if np.all(self.model.layers[0] == np.array(self.model.layers)):
            n = n + str(len(self.model.layers)) + 'L' + str(self.model.layers[0]) + '_'
        else:
            for l in self.model.layers:
                n = n + str(l) + '_'

        n += self.model.activation + '_Lr'
        n += str(self.model.learning_rate) + '_'
        # n += str(self.model.opti)+'_'

        n += self.model.opti.name + 'o' + self.model.loss.name + '_'
        n += 'BATCH_' + str(self.model.batch_size)

        n = n + 'tr_size_' + str(self.data.train_size) + 'CM'
        # for k in self.process.__dict__.keys():
        #     n = n + str(k) + str(self.process.__dict__[k][0]) + str(self.process.__dict__[k][1]) + '_'
        # n = n + 'tr_size_' + str(self.data.train_size) + '_te_size_' + str(self.data.test_size)

        n = n.replace('.', '_')
        n = n.replace('-', '_')
        self.name = n
        # In constrcution
        pass

    def print_values(self):
        """
        Print all parameters used in the model
        """

        for key, v in self.__dict__.items():
            try:
                print("#######",key,'#######')
                for key2, vv in v.__dict__.items():
                    print(key2, ":", vv)
            except:
                print(v)


    def save(self, save_dir, file_name="./parameters.p"):
       # simple save function that allows loading of deprecated parameters object
        df = pd.DataFrame(columns=['key', 'value'])

        for key, v in self.__dict__.items():
            try:
                for key2, vv in v.__dict__.items():
                    temp = pd.DataFrame(data=[str(key) + '_' + str(key2), vv], index=['key', 'value']).T
                    df = df.append(temp)

            except:
                temp = pd.DataFrame(data=[key, v], index=['key', 'value']).T
                df = df.append(temp)
        df.to_pickle("./"+save_dir + file_name,protocol=4)

    def load(self, load_dir, file_name="./parameters.p"):
        # simple load function that allows loading of deprecated parameters object
        df = pd.read_pickle(load_dir + file_name)
        # First check if this is an old pickle version, if so transform it into a df
        if type(df) != pd.DataFrame:
            loaded_par = df
            df = pd.DataFrame(columns=['key', 'value'])
            for key, v in loaded_par.__dict__.items():
                try:
                    for key2, vv in v.__dict__.items():
                        temp = pd.DataFrame(data=[str(key) + '_' + str(key2), vv], index=['key', 'value']).T
                        df = df.append(temp)

                except:
                    temp = pd.DataFrame(data=[key, v], index=['key', 'value']).T
                    df = df.append(temp)

        no_old_version_bug = True

        for key, v in self.__dict__.items():
            try:
                for key2, vv in v.__dict__.items():
                    t = df.loc[df['key'] == str(key) + '_' + str(key2), 'value']
                    if t.shape[0] == 1:
                        tt = t.values[0]
                        self.__dict__[key].__dict__[key2] = tt
                    else:
                        if no_old_version_bug:
                            no_old_version_bug = False
                            # print('#### Loaded parameters object is depreceated, default version will be used')
                        # print('Parameter', str(key) + '.' + str(key2), 'not found, using default: ',
                        #       self.__dict__[key].__dict__[key2])

            except:
                t = df.loc[df['key'] == str(key), 'value']
                if t.shape[0] == 1:
                    tt = t.values[0]
                    self.__dict__[key] = tt
                else:
                    if no_old_version_bug:
                        no_old_version_bug = False
                    #     print('#### Loaded parameters object is depreceated, default version will be used')
                    # print('Parameter', str(key), 'not found, using default: ', self.__dict__[key])

        self.update_process()

        # to ensure backward compatibility, we update her the cross_vary_list
        self.data.cross_vary_list = ["buy","sell"]

if __name__ == "__main__":
    params = Params()
    process = Process
    