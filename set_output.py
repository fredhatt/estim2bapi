import estim2b
import time


# for Linux, device addr on Windows and Mac will be different.
e2b = estim2b.Estim('/dev/ttyUSB0')
e2b.unlinkChannels()
e2b.kill() # start from zero

'''
Set channel A to 2% for 5 seconds
'''
e2b.setOutput(channel='A', level=2)
time.sleep(5)
e2b.kill() 

'''
Set channel B to 10% for 5 seconds
'''
e2b.setOutputs(levelB=10)
time.sleep(5)

'''
Set both channel A and B to 20% for 5 seconds
'''
e2b.setOutputs(20, 20)
time.sleep(5)

e2b.status()
e2b.kill()


