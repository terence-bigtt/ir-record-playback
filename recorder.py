import numpy as np
import pigpio

class IrRecorder(object):
    def __init__(self, gpio, pi, tol= .1,verbose = False):
    """"
    gpio: pin attached to IR sensor
    pi: pigpio instance
    tol : tolerance for same signal length (0<= tol <=1)
    verbose: outputs edge callback values
    """"
        self._gpio = gpio
        self._pi = pi
        self.verbose = verbose
        self.tol=tol
        pi.set_mode(gpio, pigpio.INPUT)
        self._rising = []
        self._falling= []
        self._signal = []
        self.key=""
        self.cleaned_signal=[]
        self.signals={}
        self.rcb = None
        self.fcb = None
    
    def _rising_cb(self, gpio, level, tick):
        if self.verbose:
            print gpio, level, tick
        self._rising.append((gpio, level, tick))
        self._signal.append((level, tick))

    def _falling_cb(self, gpio, level, tick):
        if self.verbose:
            print gpio, level, tick
        self._falling.append((gpio, level, tick))        
        self._signal.append((level, tick))        
        
        
    def _clean_record(self):
        self._ticks=[]
        self._signal=[]
        self._rising=[]
        self._falling=[]
        
    def record(self, key):
        if self.key is not None and self.rcb is not None and self.fcb is not None:
            self.stop()
        self._clean_record()
        self.key = key
        self.rcb= pi.callback(self._gpio, pigpio.RISING_EDGE, self._rising_cb)
        self.fcb = pi.callback(self._gpio, pigpio.FALLING_EDGE, self._falling_cb)
        print("recording key {} on pin {}".format(self.key, self._gpio))
        
    def stop(self):
        self.rcb.cancel()
        self.fcb.cancel()
        self._process()
        self.signals.update({self.key:self.clean(self.tol)})
        print("stopped recording key {} on pin {}".format(self.key, self._gpio))
        self.key = None
        
    def _process(self):
        self._ticks= [s[1] for s in self._signal]
        self._levels = [s[0] for s in self._signal[:-1]]
        self._durations = np.array(self._ticks[1:])-np.array(self._ticks[:-1])

    @property
    def ticks(self):
        return self._ticks
    
    @property
    def levels(self):
        return self._levels
    
    @property
    def durations(self):
        return self._durations
    
    @staticmethod
    def _same_within_tol(x, y, tol=0.1):
        return np.abs(x - y) <= tol*(x + y)/2.

    @staticmethod
    def _different_values(values, tol=.1):
        splitted=[]
        svalues = sorted(values)
        pairs= zip(svalues[:-1], svalues[1:])
        cuts= []
        for i, p in enumerate(pairs):
            if not IrRecord._same_within_tol(p[0], p[1], tol):
                cuts.append(i)
        v_occurences= [svalues[slice(*s)] for s in  zip([None]+cuts, cuts + [None])]
        return [np.round(np.mean(v)) for v in v_occurences]

    @staticmethod
    def round_to_closer(x, candidates):
        diffs= [np.abs(x-c) for c in candidates]
        mindif = min(diffs)
        return candidates[diffs.index(mindif)]

    def clean(self, tol):
        values = IrRecord._different_values(self.durations)
        self.cleaned_signal = [IrRecord.round_to_closer(x, values) for x in self.durations]
        return self.cleaned_signal
