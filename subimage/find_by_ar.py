#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: find_by_ar.py
Desc: find image connected components by their aspect ratio
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, Sept 21st 2014

  Given an image, find connected components (after basic filtering)
  that match a given aspect ratio.

  Typical usage:
  ./find_by_ar.py poker.jpg --aspect 0.7 --error 0.018 -d -v 
  
"""

import numpy as np
import scipy.ndimage as sp
import scipy.misc as misc
import scipy.signal as signal
import cv2
import math
import sys
import argparse
import os

class ConnectedComponent(object):
  def __init__(self, slices, mask):
    self.box = slices
    self.mask = mask
    (x, y, w, h) = cc_shape(slices)
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    

def find_by_ar(img, ar, error, min_height=50,min_width=50):
  #(t,binary) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
  (t,binary) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
  binary = cv2.erode(binary, kernel)
  ccs = get_connected_components(binary)
  masks = get_cc_masks(binary)

  aoi = []
  for i,cc in enumerate(ccs):
    (x, y, w, h)=cc_shape(cc)
    if h<=0:return None
    aspect = float(w)/float(h)
    if aspect > ar-error and aspect < ar+error and w>=min_width and h>=min_width:
      aoi.append(ConnectedComponent(cc, masks[i]))
  return aoi

def cc_shape(component):
  x = component[1].start
  y = component[0].start
  w = component[1].stop-x
  h = component[0].stop-y
  return (x, y, w, h)

def get_cc_masks(image):
  s = sp.morphology.generate_binary_structure(2,2)
  labels,n = sp.measurements.label(image)#,structure=s)
  objects = sp.measurements.find_objects(labels)
  masks = []
  for i,obj in enumerate(objects):
    mask = labels[obj]==(i+1)
    mask = sp.morphology.binary_fill_holes(mask)#, structure=None, output=None, origin=0)
    masks.append(mask)
  if len(masks)<1:
    return None
  return masks  

def get_connected_components(image):
  s = sp.morphology.generate_binary_structure(2,2)
  labels,n = sp.measurements.label(image)#,structure=s)
  objects = sp.measurements.find_objects(labels)
  return objects

def draw_bounding_boxes(img,connected_components,color=(0,0,255),line_size=2):
  for component in connected_components:
    x = component.x
    y = component.y
    w = component.w
    h = component.h
    cv2.rectangle(img,(x, y), (x+w, y+h), color, line_size)

def save_output(infile, outfile, connected_components):
  img = cv2.imread(infile)
  draw_bounding_boxes(img, connected_components)
  cv2.imwrite(outfile, img)

def  find_by_ar_from_files(infile, ar, error):
  img = cv2.imread(infile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  return find_by_ar(img, ar, error)


def main():
  parser = argparse.ArgumentParser(description='Segment raw Manga scan image.')
  parser.add_argument('infile', help='Input primary image in which we will examine.')
  parser.add_argument('-o','--output', help='Output image.', type=str, default=None)
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  parser.add_argument('-d','--debug', help='Overlay input image into output.', action="store_true")
  parser.add_argument('--aspect', help='Aspect ratio of components of interest. Width divided by height.',type=float, default=0.5)
  parser.add_argument('--error', help='Error threshold for passable aspect ratio.', type=float, default = 0.1)
  args = parser.parse_args()
  infile = args.infile
  outfile = infile + '.locations.png'
  if args.output:
    outfile = args.output

  if not os.path.isfile(infile):
    print 'Please provide a regular existing input files. Use -h option for help.'
    sys.exit(-1)

  if args.verbose:
    print 'Processing primary input file ' + infile + '.'
    print 'Generating output ' + outfile

  image_locations = find_by_ar_from_files(infile, args.aspect, args.error)
  if image_locations:
    if args.verbose:
      print str(len(image_locations)) + ' components of appropriate aspect ratio found.'
    save_output(infile, outfile, image_locations)
  elif args.verbose:
    print 'No components of appropriate aspect ratio found in image.'

if __name__ == '__main__':
  main()
