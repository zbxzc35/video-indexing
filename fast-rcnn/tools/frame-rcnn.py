#!/usr/bin/env python
import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from utils.cython_nms import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
import json
import os

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')


NETS = {'vgg16': ('VGG16',
                  'vgg16_fast_rcnn_iter_40000.caffemodel'),
        'vgg_cnn_m_1024': ('VGG_CNN_M_1024',
                           'vgg_cnn_m_1024_fast_rcnn_iter_40000.caffemodel'),
        'caffenet': ('CaffeNet',
                     'caffenet_fast_rcnn_iter_40000.caffemodel')}


def Detect(net, image_path):
    
    """Detect object classes in an image assuming the whole image is an object."""
    # Load the image
    im = cv2.imread(image_path)
    h, w, c = im.shape

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im, np.array([[0, 0, w, h]]))
    scores = scores[0]
    timer.toc()
 
    # get top 6 prediction
    pred_classes = [CLASSES[idx] for idx in ((-scores).argsort()[:6]).tolist()]
    conf = [ (-1) * prob for prob in np.sort(-scores)[:6].tolist()]
    
    img_blob = {}
    img_blob['image_path'] = image_path
    img_blob['pred'] = {'text': pred_classes, 'conf': conf}
    img_blob['rcnn_time'] = timer.total_time

    return img_blob


def parse_args():

    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Train a Fast R-CNN network')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        choices=NETS.keys(), default='vgg16')

    parser.add_argument('--video_folder', dest = 'video_folder', type=str, 
                        default='/home/t-yuche/car2cloud/frames')
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()

    prototxt = os.path.join(cfg.ROOT_DIR, 'models', NETS[args.demo_net][0],
                            'test.prototxt')
    caffemodel = os.path.join(cfg.ROOT_DIR, 'data', 'fast_rcnn_models',
                              NETS[args.demo_net][1])

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
                       'fetch_fast_rcnn_models.sh?').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()

    video_folder = args.video_folder    
    
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)
    
    for v in os.listdir(video_folder):
        print v 
        blob = {}
        blob['imgblobs'] = []
       
        frame_folder = os.path.join(video_folder, v)
        
        for f in os.listdir(frame_folder):
            frame_path = os.path.join(frame_folder, f) 
        
            img_blob = Detect(net, frame_path) 

            blob['imgblobs'] += [img_blob]

        json_filename = v + '_rcnnrecog.json'
        json.dump(blob, open(os.path.join('/home/t-yuche/car2cloud/rcnn-bbox', json_filename), 'w'))

