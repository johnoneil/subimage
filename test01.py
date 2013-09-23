#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: test01.py
Desc: Test to draw info out of poker image.
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, Sept 21st 2014

  Simple test to draw info from poker image.
  Image and required info is in /test subfolder.

"""

import find_by_ar as ar
import find_subimage as si
import cv2

def contains_subimage(img, subimage_filename):
  subimage = cv2.imread(subimage_filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  hits = si.find_subimages(img, subimage, confidence=0.70)
  if hits:
    return True
  return False

def get_suit(img):
  if contains_subimage(img, './test/heart.png'):
    return 'heart'
  if contains_subimage(img, './test/diamond.png'):
    return 'diamond'
  if contains_subimage(img, './test/club.png'):
    return 'club'
  if contains_subimage(img, './test/spade.png'):
    return 'spade'
  return 'unknown'

def get_value(img):
  if contains_subimage(img, './test/2.png'):
    return '2'
  if contains_subimage(img, './test/6.png'):
    return '6'
  if contains_subimage(img, './test/7.png'):
    return '7'
  if contains_subimage(img, './test/8.png'):
    return '8'
  if contains_subimage(img, './test/a.png'):
    return 'ace'
  #hmm. Jack requires confidence level 0.7 to detect. Don't quite know why.
  if contains_subimage(img, './test/j.png'):
    return 'jack'
  if contains_subimage(img, './test/k.png'):
    return 'king'
  return 'unknown'


def main():
  img = cv2.imread('./test/poker.jpg', cv2.CV_LOAD_IMAGE_GRAYSCALE)
  cards = ar.find_by_ar(img, 0.7, 0.02,min_height=100,min_width=50)
  if not cards:
    print 'Sorry, couldn\'t find any cards in the provided image.'
    sys.error(-1)
  #tester = False
  for card in cards:
    (x, y, w, h)=ar.cc_shape(card)
    #try to find what suit this card is
    #print str(img[card]>0)
    subsection = img[card]
    #There's a bug here (well, design flaw) whereby image subsections are being carried
    #around as connected components, but they need to be carried around as images, where
    #non-cc pixels are zeroed out or something. Needs work.
    #if not tester:
    #  cv2.imwrite('debug.png',subsection)
    #  tester = True
    #  for s in card:
    #    print s
    #print str(subsection)
    suit = get_suit(subsection)
    value = get_value(subsection)
    print 'Card found at ' + str(x) +','+ str(y)+': ' + suit + ' ' + value 


if __name__ == '__main__':
  main()
