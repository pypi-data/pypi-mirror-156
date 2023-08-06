#To take input from User and convert RA and Dec to degrees
from decimal import Decimal
from astropy.coordinates import Angle
from astropy import units as u
import numpy as np

def In(): #Method to take input
        RA, Dec="",""
        print("CORRECT FORMAT TO INPUT RIGHT ASCENSION AND DECLINATION\n")
        print("1. Please separate the values by colons")
        print("2. For RA values, input in HMS, i.e. H should not exceed 24, M should not exceed 60 and S should not exceed 60.")
        print("3. For Declination values, input in DMS, i.e. M should not exceed 60 and S should not exceed 60.\n")
        print("Enter Right Ascension in HMS format:", end='')
        RA=input()
        print("Enter Declination in DMS format:",end='')
        Dec=input()
        return RA, Dec

def Convert(RA,Dec):#Method to convert RA and Dec to degrees
    try:
        h,m,s = RA.split(':')
        d,m2,s2= Dec.split(':')
        #Converting to RA to degrees
        angle = Angle('{0}h{1}m{2}s'.format(h,m,s))
        RA_deg=angle.to(u.degree).value

        #Converting Dec to degrees
        angle = Angle('{0}d{1}m{2}s'.format(d,m2,s2))
        Dec_deg=angle.to(u.degree).value
        print("RA in degrees:",RA_deg)
        print("Dec in degrees:",Dec_deg)
        return RA_deg, Dec_deg
    except ValueError:
        print("InNCon.py says: Please enter the correct values in the correct format")
        return np.NaN, np.NaN

if __name__ == '__main__':
    RA,Dec=In()
    Convert(RA,Dec)