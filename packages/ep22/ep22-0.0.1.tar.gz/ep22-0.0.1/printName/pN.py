#This programe is written for understand package distribution on pip for open source
'''Code written by EP on 23/6/22
on the importing of the package it will ask for enter name and once valid input given then return a short msg
package name = printName
main code file name = pN.py

'''


def NamePrint():
    def PassName(x):
        Result = "Hello {}! happy to see you here. V-2(ep22)"
        print(Result.format(x))

    x = input ("Enter your Name\t")
    PassName(x)
