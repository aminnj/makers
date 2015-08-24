# -*- coding: utf-8 -*-

from PIL import Image
import os
import sys
import time
import pytesseract


def transform_image(im, x1, y1, x2, y2, scale, inverted=False, filter=True):

    im = im.crop((x1,y1,x2,y2))

    width, height = im.size
    im = im.resize((scale*width,scale*height), Image.BILINEAR)
    width, height = im.size

    if not filter:
        return im

    pix = im.load()
    for x in range(width):
        for y in range(height):
            r,g,b = pix[x,y]
            if inverted:
                if (r+g+b)/3.0/255 > 0.45:
                    im.putpixel((x,y),(0,0,0))
                else:
                    im.putpixel((x,y),(255,255,255))
            else:
                if (r+g+b)/3.0/255 < 0.55:
                    im.putpixel((x,y),(0,0,0))
                else:
                    im.putpixel((x,y),(255,255,255))

    return im


starttime = time.time()

# time in seconds between fetching data
waittime = 60.0 * 3

outfile = '/home/users/bemarsh/public_html/monitoring/cms_status.txt'

while True:

    curtime = time.time()

    fname = '/home/users/bemarsh/tmp/cmspage1.png'
    status = os.system("wget -q -O "+ fname +" https://cmspage1.web.cern.ch/cmspage1/data/page1.png")
    fname2 = '/home/users/bemarsh/tmp/lhcop.png'
    status2 = os.system("wget -q -O "+ fname2 +" https://vistar-capture.web.cern.ch/vistar-capture/lhc3.png")                                                                                                                                 

    # if status!=0:
    #     print "ERROR: could not download CMS status image (https://cmspage1.web.cern.ch/cmspage1/data/page1.png)"
    #     sys.exit(0)

    # if status2!=0:                                                                                            
    #     print "ERROR: could not download LHC Op image (https://vistar-capture.web.cern.ch/vistar-capture/lhc3.png)"                                                                                                          
    #     sys.exit(0)

    try:
        im = Image.open(fname)
    except:
        print "get_cms_data.py: Image open error"

    im_Bfield = transform_image(im, 710, 433, 782, 446, 4, inverted=True)
    try:
        Bstr = pytesseract.image_to_string(im_Bfield)
        Bstr = Bstr.replace('—','-')    
        Bfield = float(Bstr)
    except:
        Bfield = -1

    im_stat_c1 = []
    stat_c1 = []
    for i in range(14):
        im_stat_c1.append( transform_image(im, 464, 369+16*i, 498, 381+16*i, 4, inverted=False) )
        stat_c1.append(pytesseract.image_to_string(im_stat_c1[i]).replace('0','O'))
        
    im_stat_c2 = []
    stat_c2 = []
    for i in range(9):
        im_stat_c2.append( transform_image(im, 503, 369+16*i, 556, 381+16*i, 4, inverted=False) )
        stat_c2.append(pytesseract.image_to_string(im_stat_c2[i]).replace('0','O'))
    
    for i in range(len(stat_c1)):
        if stat_c1[i]=='IN':
            stat_c1[i] = '1'
        elif stat_c1[i]=='OUT':
            stat_c1[i] = '0'
        else:
            stat_c1[i] = '-1'

    for i in range(len(stat_c2)):
        if stat_c2[i]=='ON':
            stat_c2[i] = '1'
        elif stat_c2[i]=='NOT ON':
            stat_c2[i] = '0'
        elif stat_c2[i]=='PAR ON':
            stat_c2[i] = '0'
        else:
            stat_c2[i] = '-1'

    im_energy = transform_image(im, 373, 58, 491, 81, 4, inverted=False)
    try:
        energy = float(pytesseract.image_to_string(im_energy).split()[0])
    except:
        energy = 0
    
    im_beam = transform_image(im, 243, 58, 361, 79, 4, inverted=False)
    beam_stat = pytesseract.image_to_string(im_beam, config="-psm 8")

    if beam_stat.find('TABLE')!=-1:
        beam_stat = 'STABLE'

    fid = open(outfile,"a")
    fid.write('\t'.join([str(curtime),str(Bfield),str(energy),beam_stat]+stat_c1+stat_c2)+'\n')
    fid.close()

    time.sleep(waittime - (time.time()-starttime)%waittime)
