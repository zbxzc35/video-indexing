from tools.utils import *


import numpy as np
import copy
import sys
import json
import cv2
import os

'''
subsample.py subsamples the frames for labeling
'''

def getSobel(img, k_size = 3):
    ddepth = cv2.CV_16S
    scale = 1
    delta = 0


    cv2.GaussianBlur(img, (3,3), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #Gradient-x
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize = k_size, scale = scale, delta = delta, borderType = cv2.BORDER_DEFAULT)

   
    #Gradient-y
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize = k_size, scale = scale, delta = delta, borderType = cv2.BORDER_DEFAULT)

    # converting back to uint8
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
   
    dst = cv2.addWeighted(abs_grad_x,0.5,abs_grad_y,0.5,0)
    #dst = cv2.add(abs_grad_x,abs_grad_y)
    return dst

def uniformSampling(blob, total_frame, sampling_freq = 30): # sampling_freq in fps

    upsample_blob = {}
    upsample_blob['img_blobs'] = []

    for idx, kf in enumerate(blob['img_blobs']): # for each pair
        if idx == (len(blob['img_blobs']) - 1): # the last one
            # last 
            cur = int(kf['key_frame'].split('.')[0])
            nxt = total_frame-1 

        else:
            cur = int(kf['key_frame'].split('.')[0])
            nxt = int(blob['img_blobs'][idx + 1]['key_frame'].split('.')[0])
    
        # upsample
        counter = 0
        add_frame = cur + sampling_freq * counter
        while ( add_frame < nxt ):
            # add frame
            img_blob = {}
            img_blob['key_frame'] = str(add_frame) + '.jpg'
            upsample_blob['img_blobs'] += [img_blob]
            counter += 1 
            add_frame = cur + sampling_freq * counter
        
         
    return upsample_blob

def getFrameDiff(prev_frame, cur_frame):
    
    frameDelta = cv2.absdiff(prev_frame, cur_frame)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    movement = cv2.countNonZero(thresh)
    
    return movement

def loadVideos(frame_folder):

    video_paths = []
    for f in os.listdir(frame_folder):
        video_path = os.path.join(frame_folder, f)
        video_paths += [video_path]

    return video_paths

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], ' video_index(int)'
        exit(-1)

    video_index = int(sys.argv[1])
    video_paths = loadVideos('/mnt/frames')
    if video_index >= len(video_paths):
        exit(-1) 

    video_path = video_paths[video_index]
    MOVETHRESH = 0.5  # ratio of the w * h
    state = 0 # state 0: waiting for frames/ state 1: waiting for clear frames 

    total_frame = len(os.listdir(video_path)) 
    blob = {}
    blob['img_blobs'] = []
       
 
    if len(video_path.split('/')[-1]) > 1:
        video_name = video_path.split('/')[-1]
    else:
        video_name = video_path.split('/')[-2]

    prevFrame = None
    for f in sorted(os.listdir(video_path), key=lambda x: int(x.split('.')[0])):
        
        frame_path = os.path.join(video_path, f) 
        img = cv2.imread(frame_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prevFrame is None:
            #print 'frame:', f
            prevFrame = gray
            img_blob = {}
            img_blob['key_frame'] = f
            blob['img_blobs'] += [img_blob]
            continue
        
        movement = getFrameDiff(prevFrame, gray) 
        #cv2.putText(thresh,str(movement) , (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
        #cv2.imshow('frameDelta', thresh)
        
        # test if it's key frame
        if state == 0 and movement > (MOVETHRESH * gray.shape[0] * gray.shape[1]):
            prevFrame = gray
            state = 0 
            img_blob = {}
            img_blob['key_frame'] = f
            blob['img_blobs'] += [img_blob]
            '''
            cv2.imshow('frame', img)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            '''
    # uniform sampling
    blob = uniformSampling(blob, total_frame)   
    
    print 'subsample rate:', len(blob['img_blobs'])/(len(os.listdir(video_path)) * 1.0), '(', len(blob['img_blobs'])  , '/' , len(os.listdir(video_path)) , ')'
    json.dump(blob, open(os.path.join('/home/t-yuche/gt-labeling/frame-subsample/keyframe-info', video_name + '_uniform.json'),  'w'))


