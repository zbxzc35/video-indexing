import threading
import Queue
import pickle
import time
import os
import sys
import cv2
CLUSTER_PATH = '/home/t-yuche/clustering/clusterLib'
sys.path.append(CLUSTER_PATH)
from cluster import *

VIDEO_FOLDER = "/home/t-yuche/deep-video/data/videos"

event_queue = []

class RankedVideoPlayer(threading.Thread):

    def __init__(self, threadID, ranked_videos, stop_event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        # (video_name, best_node, score)
        self.ranked_videos = ranked_videos
        self.stop_event = stop_event

    def stop(self, caps):
        
        for cap in caps:
            cap.release()

        cv2.destroyAllWindows()
        return

    def init_videos(self, video_names, ranked_videos):
        caps = []
        video_chunks = []
        for idx, video in enumerate(video_names):

            if video.find('.mp4') < 0:
                video += '.mp4'

            video_path = os.path.join(VIDEO_FOLDER, video)
            cap = cv2.VideoCapture(video_path)
            caps.append(cap)

            video_chunks += [(max(0, min(ranked_videos[idx][1]['n_idx'])), min(int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)), max(ranked_videos[idx][1]['n_idx'])))]

        return caps, video_chunks

    def run(self):
        COLUMN_NUM = 5

        video_names = [x[0] for x in self.ranked_videos]
        caps, video_chunks = self.init_videos(video_names, self.ranked_videos) 
   
        #create windows
        for idx, video_name in enumerate(video_names):
            cv2.namedWindow(video_name)
            cv2.resizeWindow(video_name, 50, 60)
            col = idx % 5
            row = idx / 5 
            cv2.moveWindow(video_name, col * 400, row * 400)
         

        #check if videos are opened - should always work
        for idx, cap in enumerate(caps):
            if (not cap.isOpened()):
                print video_names[idx], 'not opened'
                cv2.destroyAllWindows() 
                return
            else:
                cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, video_chunks[idx][0])


        #play all videos
        frame_counters = [x[0] for x in video_chunks]
        while(not self.stop_event.is_set()):

            for idx, cap in enumerate(caps):
                video_name = video_names[idx] 
                
                if frame_counters[idx] == video_chunks[idx][1]: # need to replay
                    frame_counters[idx] = video_chunks[idx][0]
                    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, video_chunks[idx][0])
               
                  
                ret, frame = cap.read()
                frame = cv2.resize(frame, (350, 300))
                cv2.imshow(video_name, frame)                
                frame_counters[idx] += 1

            c = cv2.waitKey(33)
  
        self.stop(caps) 
 
    
class VideosPlayerThread(threading.Thread):

    def __init__(self, threadID, video_names, stop_event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.video_names = video_names
        self.stop_event = stop_event
        self.mailbox = Queue.Queue()
        event_queue.append(self.mailbox)    



    def stop(self, caps):
        
        for cap in caps:
            cap.release()

        cv2.destroyAllWindows() 
    

    def run(self):
        COLUMN_NUM = 5

        caps = []
        video_lengths = []
        for idx, video_name in enumerate(self.video_names):
            video_path = os.path.join(VIDEO_FOLDER, video_name)

            cap = cv2.VideoCapture(video_path)
            caps.append(cap)

            video_length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
            video_lengths.append(video_length)
   
        #create windows
        for idx, video_name in enumerate(self.video_names):
            cv2.namedWindow(video_name)
            cv2.resizeWindow(video_name, 50, 60)
            col = idx % 5
            row = idx / 5 
            cv2.moveWindow(video_name, col * 400, row * 400)
         
        #cv2.waitKey(-1)

        #check if videos are opened - should always work
        for idx, cap in enumerate(caps):
            if (not cap.isOpened()):
                print self.video_names[idx], 'not opened'
                cv2.destroyAllWindows() 
                return

        #play all videos
        frame_counters = [0 for x in xrange(len(self.video_names))]
        while(not self.stop_event.is_set()):
            try:
                ranked_list = self.mailbox.get(False)
                print ranked_list
                # move windows
                for mv in ranked_list:
                    col = idx % 5
                    row = idx / 5
                    print mv[0] 
                    cv2.moveWindow(mv[0], col * 400, row * 400)
                                         
            except Queue.Empty, qe:
                pass 
            for idx, cap in enumerate(caps):
                video_name = self.video_names[idx] 
                
                if frame_counters[idx] == video_lengths[idx]: # it is the last frame
                    frame_counters[idx] = 0
                    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
               
                  
                ret, frame = cap.read()
                frame = cv2.resize(frame, (350, 300))
                cv2.imshow(video_name, frame)                
                cv2.resizeWindow(video_name, 50, 60)
                '''
                col = idx % 5
                row = idx / 5 
                cv2.moveWindow(video_name, col * 400, row * 400)
                '''
                frame_counters[idx] += 1

            c = cv2.waitKey(33)
  
        self.stop(caps) 


def rank_video(matched_list, score_thresh = 0.1):
     
    ranked_list = sorted(matched_list, key = lambda x:x[2], reverse=True)
    ranked_list = filter(lambda x: x[2] > score_thresh, ranked_list) 

    return ranked_list


#def play_video():


if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print 'Usage:', sys.argv[0], 'video_names index_file'
        exit(-1)
    
    video_names = [line.strip() for line in open(sys.argv[1]).readlines()]
    index_file = sys.argv[2]
    
    # load index from index.pickle file
    indexes = {}
    with open(index_file, 'rb') as pickle_fh:
       indexes = pickle.load(pickle_fh)
    '''
    indexes = {}
    for idx, video_name in enumerate(video_names): 
        if idx == 1:
            break
        video_name = video_name.split('.')[0]
        gt_nodes = load_turker_labels(video_name)
        clusters, linkage_matrix = cluster(gt_nodes)
        indexes[video_name] = clusters
    '''
    thread_stop_event = None 
    while True:
        query_str = (raw_input('$ '))
        if query_str.find('quit') >= 0 or query_str.find('exit') >= 0:
            if thread_stop_event != None: 
                thread_stop_event.set()
                play_video_thread.join()
                play_video_thread = None
            break
    
        else:
            # match against all videos
            matched_list = []
            ranked_list = []
            matched_list = match_indexes(indexes, query_str)
            ranked_list = rank_video(matched_list)
                    
            if len(ranked_list) == 0:
                cv2.destroyAllWindows()
            #event_queue[0].put(ranked_list)
            else:
                if thread_stop_event != None: 
                    thread_stop_event.set()
                    play_video_thread.join()
                    play_video_thread = None
                    
                thread_stop_event = threading.Event()
                play_video_thread = RankedVideoPlayer(2, ranked_list, thread_stop_event) 
                play_video_thread.start()
    '''
    threads = []
    
    for idx, video_name in enumerate(video_names):
        threads.append(VideoPlayerThread(idx, video_name, os.path.join(VIDEO_FOLDER, video_name)))
    
    print threads 
    for idx, video_name in enumerate(video_names):
        threads[idx].start()
    '''
