
import Image
import os
import sys
import time
import pytesseract


def transform_image(im, x1, y1, x2, y2, scale, inverted=False):

    im = im.crop((x1,y1,x2,y2))

    width, height = im.size
    im = im.resize((scale*width,scale*height), Image.BILINEAR)
    width, height = im.size

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


outname = 'monitor_lumi.txt'

curtime = time.time()

fname = 'lhclumi.png'
status = os.system("curl -s -S -o "+ fname +" https://vistar-capture.web.cern.ch/vistar-capture/lhclumi.png")

# if status!=0:
#     print "ERROR: could not download CMS status image (https://cmspage1.web.cern.ch/cmspage1/data/page1.png)"
#     sys.exit(0)

im = Image.open(fname)
im_cms = transform_image(im, 140, 435, 310, 465, 2, inverted=True)
im_atl = transform_image(im, 140, 340, 310, 372, 2, inverted=True)

str_cms = pytesseract.image_to_string(im_cms).strip()
str_atl = pytesseract.image_to_string(im_atl).strip()

fid = open(outname,"a")
fid.write('\t'.join([str(curtime),str_cms,str_atl])+'\n')
fid.close()

