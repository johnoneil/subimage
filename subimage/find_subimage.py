#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: find_subimage.py
Desc: find instances of an image in another image
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, Sept 21st 2014

  Given two image inputs, find instances of one image in the other.
  This ought not account for scaling or rotation. 
  
"""

import numpy as np
import scipy.ndimage as sp
import scipy.misc as misc
import scipy.signal as signal
import math
import sys
import argparse
import os

#cv2 is not well package managed, so we bail if it's not present
try:
  import cv2
except ImportError as e:
  print 'Could not import cv2. Please install current version of opencv and python binding.'
  print 'This message is provided because opencv is not managed via pypi (pip install) package mgr.'
  raise e


def find_subimages(primary, subimage, confidence=0.80):
  primary_edges = cv2.Canny(primary, 32, 128, apertureSize=3)
  subimage_edges = cv2.Canny(subimage, 32,128, apertureSize=3)

  result = cv2.matchTemplate(primary_edges, subimage_edges, cv2.TM_CCOEFF_NORMED)
  (y, x) = np.unravel_index(result.argmax(),result.shape)

  result[result>=confidence]=1.0
  result[result<confidence]=0.0
  
  ccs = get_connected_components(result)
  return correct_bounding_boxes(subimage, ccs)  


def cc_shape(component):
  x = component[1].start
  y = component[0].start
  w = component[1].stop-x
  h = component[0].stop-y
  return (x, y, w, h)

def correct_bounding_boxes(subimage, connected_components):
  (image_h, image_w)=subimage.shape[:2]
  corrected = []
  for cc in connected_components:
    (x, y, w, h) = cc_shape(cc)
    presumed_x = x+w/2
    presumed_y = y+h/2
    corrected.append((slice(presumed_y, presumed_y+image_h), slice(presumed_x, presumed_x+image_w)))
  return corrected

def get_connected_components(image):
  s = sp.morphology.generate_binary_structure(2,2)
  labels,n = sp.measurements.label(image)#,structure=s)
  objects = sp.measurements.find_objects(labels)
  return objects

def draw_bounding_boxes(img,connected_components,max_size=0,min_size=0,color=(0,0,255),line_size=2):
  for component in connected_components:
    if min_size > 0 and area_bb(component)**0.5<min_size: continue
    if max_size > 0 and area_bb(component)**0.5>max_size: continue
    (ys,xs)=component[:2]
    cv2.rectangle(img,(xs.start,ys.start),(xs.stop,ys.stop),color,line_size)

def save_output(infile, outfile, connected_components):
  img = cv2.imread(infile)
  draw_bounding_boxes(img, connected_components)
  cv2.imwrite(outfile, img)

def  find_subimages_from_files(primary_image_filename, subimage_filename, confidence):
  '''
  2d cross correlation we'll run requires only 2D images (that is color images
  have an additional dimension holding parallel color channel info). So we 'flatten'
  all images loaded at this time, in effect making them grayscale.
  There is certainly a lot of info that will be lost in this process, so a better approach
  (running separately on each channel and combining the cross correlations?) is probably
  necessary.  
  '''
  primary = cv2.imread(primary_image_filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  subimage = cv2.imread(subimage_filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  return find_subimages(primary, subimage, confidence)


def main(): 
  parser = argparse.ArgumentParser(description='Segment raw Manga scan image.')
  parser.add_argument('image', help='Input primary image in which we look for subimages.')
  parser.add_argument('subimage', help='Subimage instances of which will be found in primary image.')
  parser.add_argument('-o','--output', help='Filename for output image to generate', type=str, default='correlations.png')
  parser.add_argument('-v','--verbose', help='Verbose operation. Spin detected image coordinates to command line', action="store_true")
  parser.add_argument('-d','--debug', help='Overlay input image into output.', action="store_true")
  parser.add_argument('--confidence', help='Confidence level for matching subimages.',type=float, default=0.80)
  
  args = parser.parse_args()
  
  primary_image_filename = args.image
  subimage_filename = args.subimage
  outfile = args.output

  if not os.path.isfile(primary_image_filename) or not os.path.isfile(subimage_filename):
    print 'Please provide a regular existing input files. Use -h option for help.'
    sys.exit(-1)

  if args.verbose:
    print '\tProcessing primary input file ' + primary_image_filename + ' and subimage file ' + primary_image_filename + '.'
    print '\tGenerating output ' + outfile

  image_locations = find_subimages_from_files(primary_image_filename, subimage_filename,confidence=args.confidence,)

  save_output(primary_image_filename, outfile, image_locations)

  if args.verbose:
    print 'Instances of subimage {subimage} in primary image {primary} were found at:'.format(subimage=subimage_filename, primary=primary_image_filename)
    print str(image_locations)

if __name__ == '__main__':
  main()
