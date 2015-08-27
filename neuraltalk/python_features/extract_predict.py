import os
import json
import sys
import argparse
import Image
import time
import numpy as np
import pandas as pd
from scipy.misc import imread, imresize
import cPickle as pickle
caffepath =  '/home/t-yuche/caffe/python'
sys.path.append(caffepath)
import caffe
TOOL_PATH = '/home/t-yuche/clustering/tools'
sys.path.append(TOOL_PATH)
from utils import *

def predict(in_data, net):
    """
    Get the features for a batch of data using network

    Inputs:
    in_data: data batch
    """
    out = net.forward(**{net.inputs[0]: in_data})
    features =  out[net.outputs[0]]
    return features


def batch_predict(filenames, net):
    """
    Get the features for all images from filenames using a network

    Inputs:
    filenames: a list of names of image files

    Returns:
    an array of feature vectors for the images in that file
    """
    N, C, H, W = net.blobs[net.inputs[0]].data.shape
    F = net.blobs[net.outputs[0]].data.shape[1]
    Nf = len(filenames)
    allftrs = np.zeros((Nf, F))
    #allpreds = []
    for i in range(0, Nf, N):
        tic = time.time()
        in_data = np.zeros((N, C, H, W), dtype=np.float32)

        batch_range = range(i, min(i+N, Nf))
        batch_filenames = [filenames[j] for j in batch_range]
        Nb = len(batch_range)

        batch_images = np.zeros((Nb, 3, H, W))
        for j,fname in enumerate(batch_filenames):
            im = np.array(Image.open(fname))
            
            if len(im.shape) == 2:
                im = np.tile(im[:,:,np.newaxis], (1,1,3))
            # RGB -> BGR
            im = im[:,:,(2,1,0)]
            # mean subtraction
            im = im - np.array([103.939, 116.779, 123.68])
            # resize
            im = imresize(im, (H, W))
            # get channel in correct dimension
            im = np.transpose(im, (2, 0, 1))
            batch_images[j,:,:,:] = im

        # insert into correct place
        in_data[0:len(batch_range), :, :, :] = batch_images
        
        # predict features
        ftrs = predict(in_data, net)
        toc = time.time()
        
        for j in range(len(batch_range)):
            allftrs[i+j,:] = ftrs[j,:]

    return allftrs

input_idx = int(sys.argv[1])
model_def = '/home/t-yuche/neuraltalk/python_features/VGG_ILSVRC_16_layers_deploy.prototxt'
model = '/home/t-yuche/caffe/models/vgg_ilsvrc_16/VGG_ILSVRC_16_layers.caffemodel'
caffe.set_mode_cpu()
net = caffe.Net(model_def, model, 0)
OUTPUT_FOLDER = '/mnt/tags/fei-caption-all'

# Load all images
FRAME_FOLDER = '/mnt/frames'
all_video_names = os.listdir(FRAME_FOLDER)

if input_idx >= len(all_video_names):
    exit(-1)

video_name = all_video_names[input_idx]
all_frames = [os.path.join(FRAME_FOLDER, video_name, x) for x in os.listdir(os.path.join(FRAME_FOLDER, video_name))]


# Load unprocessed frames to filenames
fei_cap_data = load_video_caption('/mnt/tags/fei-caption-keyframe', video_name)
processed_frames = [x['img_path'] for x in fei_cap_data]

filenames = []
for frame in all_frames:
    if frame not in processed_frames:
        filenames += [frame] 


# start batch prediction
allftrs = batch_predict(filenames, net)

# store the features in a pickle fileF
FEATURES_PATH = os.path.join('/mnt/tags/fei-caption-all-pickle', video_name + '.pickle')
with open(FEATURES_PATH, 'w') as fp:
    pickle.dump(allftrs, fp)

# start generate caption

# load the checkpoint
checkpoint = pickle.load(open('/home/t-yuche/neuraltalk/models/flickr8k_cnn_lstm_v1.p', 'rb'))
checkpoint_params = checkpoint['params']
dataset = checkpoint_params['dataset']
model = checkpoint['model']
misc = {}
misc['wordtoix'] = checkpoint['wordtoix']
ixtoword = checkpoint['ixtoword']

#output blob
blob = {} 
blob['checkpoint_params'] = checkpoint_params
blob['imgblobs'] = []
features = pickle.load(open(FEATURES_PATH))
features = features.T
D,N = features.shape
beam_size = 5

# iterate over all images and predict sentences
BatchGenerator = decodeGenerator(checkpoint_params)
for n in xrange(N):

    # encode the image
    img = {}
    img['feat'] = features[:, n]
    img['local_file_path'] = filenames[n]

    # perform the work. heavy lifting happens inside
    kwparams = { 'beam_size' : 5 }
    tic = time.time()
    Ys = BatchGenerator.predict([{'image':img}], model, checkpoint_params, **kwparams)
    toc = time.time()

    # build up the output
    img_blob = {}
    img_blob['img_path'] = img['local_file_path']
    img_blob['rnn_time'] = (toc-tic)
    img_blob['candidate'] = {'text': [], 'logprob': []}
    # encode the top prediction
    top_predictions = Ys[0] # take predictions for the first (and only) image we passed in
    for i in xrange(min(5, len(top_predictions))):
        top_prediction = top_predictions[i]  
        candidate = ' '.join([ixtoword[ix] for ix in top_prediction[1] if ix > 0]) # ix 0 is the END token, skip that
        #print '%f PRED: (%f) %s' % (img_blob['rnn_time'], top_prediction[0], candidate)
        img_blob['candidate']['text'] += [candidate]
        img_blob['candidate']['logprob'] += [top_prediction[0]]
    
    #img_blob['candidate'] = {'text': candidate, 'logprob': top_prediction[0]}    
    blob['imgblobs'].append(img_blob)

# dump result struct to file
save_file = os.path.join(OUTPUT_FOLDER, video_name + '_5_caption.json') 
print 'writing predictions to %s...' % (save_file, )
json.dump(blob, open(save_file, 'w'))


