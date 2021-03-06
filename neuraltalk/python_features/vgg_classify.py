import os
import json
import sys
import argparse
import time
import Image
import numpy as np
import pandas as pd
from scipy.misc import imread, imresize

import cPickle as pickle

parser = argparse.ArgumentParser()
parser.add_argument('--caffe',
                    help='path to caffe installation')
parser.add_argument('--model_def',
                    help='path to model definition prototxt')
parser.add_argument('--model',
                    help='path to model parameters')
parser.add_argument('--files',
                    help='path to a file contsining a list of images')
parser.add_argument('--gpu',
                    action='store_true',
                    help='whether to use gpu training')
parser.add_argument("--label_file",
                    default="/home/t-yuche/caffe/data/ilsvrc12/synset_words.txt",
                    help="Index to label file."
                    )
parser.add_argument("--output_file", help='name of the json file where to store the prediction results')

args = parser.parse_args()

caffepath = args.caffe + '/python'
sys.path.append(caffepath)

import caffe

def predict(in_data, net):
    """
    Get the features for a batch of data using network

    Inputs:
    in_data: data batch
    """

    out = net.forward(**{net.inputs[0]: in_data})
    features = out[net.outputs[0]].squeeze(axis=(2,3))
    return features

def classify(in_data, net):

    out = net.forward_all(**{net.inputs[0]: in_data})
    predictions = out[net.outputs[0]] 
    all_labels = []
    all_confs = []
    
    for p in predictions:
        indices = (-p).argsort()[:5]
        label_predictions = labels[indices].tolist()
        all_labels += [label_predictions]
        all_confs += [np.sort(-p)[:5].tolist()]
    return (all_labels, all_confs)

def batch_predict(filenames, net, labels):
    """
    Get the features for all images from filenames using a network

    Inputs:
    filenames: a list of names of image files

    Returns:
    an array of feature vectors for the images in that file
    """
    blob = {}
    blob['imgblobs'] = []
    N, C, H, W = net.blobs[net.inputs[0]].data.shape
    F = net.blobs[net.outputs[0]].data.shape[1]
    Nf = len(filenames)
    #allftrs = np.zeros((Nf, F))
    allpreds = []
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

        (ps,cs) = classify(in_data, net)
        toc = time.time()
        print 'time: ', str(toc-tic), 'per image: ', (toc-tic)/len(batch_range)
        #allpreds += [ps]
        for j, fname in enumerate(batch_filenames):
            img_blob = {}
            img_blob['img_path'] = fname
            img_blob['pred'] = {'text': ps[j], 'conf': cs[j]} 
            blob['imgblobs'].append(img_blob) 
        
        # predict features
        #ftrs = predict(in_data, net)
        #for j in range(len(batch_range)):
        #    allftrs[i+j,:] = ftrs[j,:]
        print 'Done %d/%d files' % (i+len(batch_range), len(filenames))

    return blob


if args.gpu:
    caffe.set_mode_gpu()
else:
    caffe.set_mode_cpu()

net = caffe.Net(args.model_def, args.model, 0)

# Load all images
filenames = []
with open(args.files) as fp:
    for line in fp:
        filename = line.strip().split()[0]
        filenames.append(filename)


# Load label file
with open(args.label_file) as f:
    labels_df = pd.DataFrame([
        {
            'synset_id':l.strip().split(' ')[0],
            'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
        }
        for l in f.readlines()
    ])
labels = labels_df.sort('synset_id')['name'].values

allpreds = batch_predict(filenames, net, labels)

# dump result struct to file
save_file = os.path.join(args.output_file)
print 'writing predictions to %s...' % (save_file, )
json.dump(allpreds, open(save_file, 'w'))
