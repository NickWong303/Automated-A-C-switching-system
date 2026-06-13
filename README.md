# Automated A/C switching system
This is an automated A/C switching system applicable for HKUST stndents, you can set a time to turn on/off A/C periodically

## How can I use it?
This is very easy. First of all, make sure your computer can run Python locally and has Chrome installed. Then you can run the program in a terminal, PyCharm, or whatever you want. (You will probably be missing some packages, like ```selenium```. You can open the terminal and type ```pip install selenium``` – do this for all missing packages, and then you can finally run it.) 

After running the program, it will call and open a new Chrome webpage and redirect to the [A/C control system](https://w5.ab.ust.hk/njggt/app/home). The only thing you have to do is fill in your account email and password to get into the A/C controller. After that, press 'Enter' in your shell terminal, and you're done.

The default times for turning on and turning off are 30 minutes each. You can adjust them through the two variables ```ON_TIME``` and ```OFF_TIME```.

# Change Log
2026-06-13: 
 - `AntoAC.py` can now show the time of execution (based on system time) and number of loops
 - Fixed some known bugs
