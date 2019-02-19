
import os, sys
import numpy as np
from netCDF4 import Dataset
from shutil import copy2, move

def fill_values(to,frm,var):
    i = -1
    var1 = var
    for z, y, x in to:
        i = i + 1
        (z1, y1, x1) = frm[i]
        var1[:,z,y,x] = var[:,z1,y1,x1]
    return var1

oldgrdfile=sys.argv[1]
newgrdfile=sys.argv[2]

inifiles=sys.argv[3:]

oldgrd = Dataset(oldgrdfile,'r',format="NETCDF4")
newgrd = Dataset(newgrdfile,'r',format="NETCDF4")

oldkmt = (oldgrd.variables['kmt'][:]).astype(int)
zt = oldgrd.variables['zt'][:]

newkmt = (newgrd.variables['kmt'][:]).astype(int)

ny, nx = oldkmt.shape

nz, = zt.shape

oldmask = np.zeros((nz,ny,nx))
newmask = np.zeros((nz,ny,nx))

for y in np.arange(ny):
    for x in np.arange(nx):
        oldmask[:oldkmt[y,x],y,x] = 1
        newmask[:newkmt[y,x],y,x] = 1

mask = newmask-oldmask

tmp = np.where(mask>0)

to = zip(*tmp)
frm = [(-1,-1,-1) for z, y, x in to]

maxl = np.maximum(nx/4,ny/4)

i = -1
for z, y, x in to:
    found = False
    i = i + 1
    for l in np.arange(1,maxl):
        if found: break
        xm = x - l
        if (xm<0): xm = nx + xm
        
        xp = x + l
        if (xp>nx): xp = xp - nx

        ym = y - l
        if (ym<0): ym = 0

        yp = y + l
        if (yp>=ny): yp = ny-1

        yl = np.arange(ym,yp+1)

        if (xp>xm):
            xl = np.arange(xm,xp)
        else:
            xl = np.arange(0,xp+1)+np.arange(xm,nx)

        for y1 in yl:
            if found: break
            for x1 in xl:
                if found: break
                if oldmask[z,y1,x1]>0:
                    found=True
                    frm[i] = (z,y1,x1)
                    break
try:
    os.makedirs("outfiles")
except OSError:
    if not os.path.isdir("outfiles"):
        raise

for fil in inifiles:
    basenm=os.path.basename(fil)
    ofile = "outfiles/"+basenm
    copy2(fil,ofile)
    f = Dataset(ofile,'r+',format="NETCDF4")
    for var in f.variables:
        if len(f.variables[var].shape)==4:
            print(f.variables[var].shape)
            dat = f.variables[var][:]
            dat = fill_values(to,frm,dat)
            f.variables[var][:]=dat
        elif len(f.variables[var].shape)!=1:
            print("Dimension Error")
            exit()
    f.close()



