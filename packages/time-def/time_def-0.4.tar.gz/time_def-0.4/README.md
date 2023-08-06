<h3>The library is designed to display the execution time of functions in a convenient way.</h3> 

This is my first publication

GitHub: https://github.com/MaximF39/time_def

pip install time_def

Example:
```python
from time_def import time_def
import time
    
@time_def
def time_sleep(r, r2):
    time.sleep(1)
    return r, r2

time_sleep(1, r2=4)
# func: time_sleep, res=(1, 4), time: 1.0127627849578857 s
```