#PyInstl.py
import time
import sys
import os
import argparse
import subprocess
from pyfiglet import Figlet
from clint.textui import puts, colored, indent

#Load Animation for PyInstl
import time
import sys
import os

def load_animation():
  
    # String to be displayed when the application is loading
    load_str = "Loading Components..."
    ls_len = len(load_str)
  
  
    # String for creating the rotating line
    animation = "|/-\\"
    anicount = 0
      
    # used to keep the track of
    # the duration of animation
    counttime = 0        
      
    # pointer for travelling the loading string
    i = 0                     
  
    while (counttime != 50):
          
        # used to change the animation speed
        # smaller the value, faster will be the animation
        time.sleep(0.075) 
                              
        # converting the string to list
        # as string is immutable
        load_str_list = list(load_str) 
          
        # x->obtaining the ASCII code
        x = ord(load_str_list[i])
          
        # y->for storing altered ASCII code
        y = 0                             
  
        # if the character is "." or " ", keep it unaltered
        # switch uppercase to lowercase and vice-versa 
        if x != 32 and x != 46:             
            if x>90:
                y = x-32
            else:
                y = x + 32
            load_str_list[i]= chr(y)
          
        # for storing the resultant string
        res =''             
        for j in range(ls_len):
            res = res + load_str_list[j]
              
        # displaying the resultant string
        sys.stdout.write("\r"+res + animation[anicount])
        sys.stdout.flush()
  
        # Assigning loading string
        # to the resultant string
        load_str = res
  
          
        anicount = (anicount + 1)% 4
        i =(i + 1)% ls_len
        counttime = counttime + 1
      
# Driver program
if __name__ == '__main__': 
    load_animation()


def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as err:
        puts(colored.red('ERROR: ') + colored.yellow(err))


def make_args():
    my_parser = argparse.ArgumentParser(description='Package Installer')
    my_parser.add_argument('Package',
                       metavar='pkg_name',
                       type=str,
                       help='The Package Name')
    
    args = my_parser.parse_args()

def get_user_input():
    if len(sys.argv) > 2:
        print('You have specified too many arguments')
        sys.exit()

    if len(sys.argv) < 2:
        return ""

    return sys.argv[1]

def main(pkg_name):
    f = Figlet(font='slant')
    print(f.renderText('PyInstl'))
    make_args()
    with indent(4, quote='>>>'):
        puts(colored.blue('Installing package: ') + str(pkg_name))
    load_animation()
    install(pkg_name)
    

if __name__ == "__main__":
    main(get_user_input())