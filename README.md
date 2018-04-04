# ir-record-playback
Python classes for recording / playing infrared signals

This library depends on the pigpio [http://abyz.me.uk/rpi/pigpio] python api.
It is inspired by the irrp_py example therein.

- Api usage:
To record a IR signal, instanciate a IrRecorder object with a pigpio instance pi and a gpio number:

```python
recorder = IrRecorder(gpio, pi, [tol], [verbose])
```

and call the method 

```python
recorder.record("key")
```

record(key) to store a cleaned version of the signal read.

The signal is cleaned by collapsing all the IR pulse (both on and off) length to values that are differents within tol. 
This will lead to 3-4 different values, the initial signal is then reexpressed in terms of these values.

The recorded datae are stored in the dictionary recorder.records:

```python
recorder.records.get("key")
```

- Playback
Not yet implemented...
