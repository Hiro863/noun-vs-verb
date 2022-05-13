from datetime import datetime
from time import sleep

if __name__ == "__main__":
    now = datetime.now()

    first_time = datetime.now()
    sleep(10)
    later_time = datetime.now()
    print((later_time - first_time).strftime("%Hh%Mm%Ss"))
    print(now.strftime("%m/%d/%Y, %H:%M:%S"))