from utils import *
from mapk import *
from ndcg import *
import numpy as np
import scipy.stats as stats
import operator
import pickle
import matplotlib
import matplotlib.pyplot as plt
try:
    plt.style.use('ggplot')
except:
    pass

COSSIM_THRESH = 0.05

def combine_all_models(video_name, _vgg_data, _msr_data, _rcnn_data, _fei_data):

    stop_words = get_stopwords()
    wptospd = word_pref_to_stopword_pref_dict()
    convert_dict = convert_to_equal_word()

    tf_list = []
    assert(len(_vgg_data) == len(_msr_data))
    assert(len(_rcnn_data) == len(_fei_data))
    assert(len(_vgg_data) == len(_fei_data))

    for fid in xrange(len(_vgg_data)):

        rcnn_data = _rcnn_data[fid]
        vgg_data = _vgg_data[fid]
        msr_data = _msr_data[fid]
        fei_data = _fei_data[fid]
   
        frame_name = rcnn_data['image_path'].split('/')[-1]
        assert(rcnn_data['image_path'] == vgg_data['img_path'])
        assert(rcnn_data['image_path'] == msr_data['img_path'])
        assert(rcnn_data['image_path'] == fei_data['img_path'])

        # combine words
        rcnn_ws = []
        if len(rcnn_data) > 0:
            for rcnn_idx, word in enumerate(rcnn_data['pred']['text']):
                ## the confidence is higher than 10^(-3) and is not background
                if rcnn_data['pred']['conf'][rcnn_idx] > 0.0005 and word not in stop_words:
                    rcnn_ws += [word]
        vgg_ws = []
        if len(vgg_data) > 0:
            for vgg_idx, w in enumerate(vgg_data['pred']['text']):
                w = wptospd[w]
                if w in convert_dict:
                    w = convert_dict[w]
                prob = vgg_data['pred']['conf'][vgg_idx]
            
                if w not in stop_words:
                    vgg_ws += [w]
    
        fei_ws = [] 
        if len(fei_data) > 0:
            str_list = fei_data['candidate']['text']
            for s in str_list:
                for w in s.split(' '):
                    w = inflection.singularize(w)
                    if w not in stop_words and w not in fei_ws:
                        fei_ws += [w]         

        msr_ws = [] 
        if len(msr_data) > 0:
            for msr_idx, w in enumerate(msr_data['words']['text']):
                w = inflection.singularize(w)
                prob = msr_data['words']['prob'][msr_idx]
                if w not in stop_words:
                    msr_ws += [w]

        words = {}
        for w in rcnn_ws:
            if w not in words:
                words[w] = 1
            else:
                words[w] += 1
        for w in vgg_ws:
            if w not in words:
                words[w] = 1
            else:
                words[w] += 1
        
        for w in fei_ws:
            if w not in words:
                words[w] = 1
            else:
                words[w] += 1
    
        for w_idx, w in enumerate(msr_ws):
            if w not in words:
                words[w] = 1
            else:
                words[w] += 1

        if '' in words:
            words.pop('', None)

        tf_list += [{'frame_name': frame_name, 'tf': words}]

    return tf_list

def load():
    
    VIDEO_LIST = '/mnt/video_list.txt'
    videos = open(VIDEO_LIST).read().split()
    
    vgg = {}
    fei_cap = {}
    msr_cap = {}
    rcnn = {}
    turker_labels = {}
    for vid, video_name in enumerate(videos):
        _vgg_data = load_video_recog('/mnt/tags/vgg-classify-all', video_name)
        _fei_caption_data = load_video_caption('/mnt/tags/fei-caption-all', video_name)
        _msr_cap_data = load_video_msr_caption('/mnt/tags/msr-caption-all', video_name)
        _rcnn_data = load_video_rcnn('/mnt/tags/rcnn-info-all', video_name)
        _turker_data = load_video_processed_turker(video_name)       
 
        vgg[video_name] = _vgg_data[0]
        fei_cap[video_name] = _fei_caption_data[0]
        msr_cap[video_name] = _msr_cap_data[0]
        rcnn[video_name] = _rcnn_data[0]
        turker_labels[video_name] = _turker_data[0]

        if vid == 30:
            break
    return vgg, fei_cap, msr_cap, rcnn, turker_labels


def rank(query, video_tfs):
   
    # 
    query_dict = {}
    query_dict[query] = 1

    video_scores = {}
    for video_d in video_tfs:
        video_name = video_d['video_name']
        video_tf = video_d['tf']
        cos_sim = cos_similarty(query_dict, video_tf)  
        video_scores[video_name] = cos_sim

    ranked_video = sorted(video_scores.items(), key = operator.itemgetter(1), reverse=True)

    return ranked_video


def get_inrange_fids(start_fid, end_fid, subsampled_frames):

    in_range_fids = []
 
    for f_count, f_name in enumerate(subsampled_frames):
        fid = int(f_name.split('.')[0])
               
        if fid >= start_fid and fid <= end_fid:
            in_range_fids += [fid]
 
    if len(in_range_fids) == 0:
        for f_count, f_name in enumerate(subsampled_frames):
            fid = int(f_name.split('.')[0])
            
            if f_count == len(subsampled_frames)-1:
                if fid < start_fid:
                    in_range_fids += [fid]
                    break
            elif fid < start_fid and int(subsampled_frames[f_count + 1].split('.')[0]) > end_fid:
                    in_range_fids += [fid]
                    break

    return in_range_fids 


def get_turker_subsampled_tf(video_name, turker_data, in_range_fids):

    turker_tf = {} 
    for fid in in_range_fids:
        for label in filter(lambda x: int(x['frame_name'].split('.')[0]) == fid, turker_data)[0]['gt_labels']:
            if label not in turker_tf:
                turker_tf[label] = 1
            else:
                turker_tf[label] += 1
       
    return turker_tf 

def get_subsampled_tf(video_name, vgg_data, msr_data, rcnn_data, fei_data, in_range_fids):

    s_vgg_data = []
    s_fei_data = []
    s_msr_data = []
    s_rcnn_data = []
    
    for fid in in_range_fids:

        s_vgg_data += filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) == fid , vgg_data)
        s_fei_data += filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) == fid , fei_data)
        s_msr_data += filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) == fid , msr_data)
        s_rcnn_data += filter(lambda x: int(x['image_path'].split('/')[-1].split('.')[0]) == fid, rcnn_data)

    s_tf_list = combine_all_models(video_name, s_vgg_data, s_msr_data, s_rcnn_data, s_fei_data)
    s_tf = get_combined_tfs(s_tf_list)

    return s_tf


def reindexing(gt_video_rank, test_video_rank, score_thresh):
    """
    Indexing ranked video list using ground-truth video ranking
    """ 

    gt_rank = []
    k = 0
    for tid, tup in enumerate(gt_video_rank):
        video_name = tup[0]
        score = tup[1]
        if score > score_thresh:
            k += 1
        gt_rank += [video_name] 
     
    test_rank = [] 
    for tvid, tup in enumerate(test_video_rank):
        t_video_name = tup[0]
        t_score = tup[1]
        test_rank += [gt_rank.index(t_video_name)]

    return test_rank, k


# TODO: only consider score > 0
def kendall_correlation(gt_video_rank, test_video_rank):
  
    assert(len(gt_video_rank) == len(test_video_rank))
    tau, p_value = stats.kendalltau(range(len(gt_video_rank)), test_video_rank)
    
    return tau, p_value 
      

def plot_rank_debug(gt_rank, gt_tfs, test_tfs, video_rank, query_str, test_scheme_name = "groundtruth"):
    
    fig = plt.figure()
    fig.suptitle(test_scheme_name + ' query:' + query_str)
    for rank, tup in enumerate(gt_rank):
        video_name = tup[0]
        score = tup[1] 
       
        # get test tf
        tf = filter(lambda x: x['video_name'] == video_name, test_tfs)[0]['tf']
        deno = sum([tf[x] for x in tf]) * 1.0
        # get gt tf
        gt_tf = filter(lambda x:x['video_name'] == video_name, gt_tfs)[0]['tf']
        gt_deno = sum([gt_tf[x] for x in gt_tf]) * 1.0

        gt_x = gt_tf.keys()         
        # align test tf based on gt tf
        x = []
        y = []
        gt_y = []
        
        query_point = (-1,-1) 
        gt_query_point = (-1,-1) 
        for xidx, key in enumerate(gt_x):
            x += [key]
            gt_y += [gt_tf[key]/gt_deno]

            if key in tf:
                y += [tf[key]/deno] 
                if key == query_str.split('-')[0]:
                    query_point = (xidx, tf[key]/deno) 
                    gt_query_point = (xidx, gt_tf[key]/gt_deno) 
            else:
                y += [0]

        for key in tf:
            if key not in x:
                x += [key]
                y += [tf[key]/deno]

        # get test video rank
        t_rank = -1
        t_score = -1
        for trank, ttup in enumerate(video_rank):
            if ttup[0] == video_name:
                t_rank = trank
                t_score = ttup[1]
                break 

        ax = plt.subplot(len(gt_rank)/5,  5, rank+1)
        ax.plot( range(len(x)), y, color = 'blue', alpha = 0.7, label = test_scheme_name ) 
        ax.plot( range(len(gt_x)), gt_y, color = 'red', alpha = 0.7, label = "groundtruth")
        if query_point[0] != -1:
            ax.scatter(query_point[0], query_point[1], color = 'blue', marker = (5,1)) 
        if gt_query_point[0] != -1:
            ax.scatter(gt_query_point[0], gt_query_point[1], color = 'red', marker = (5,1)) 
        ax.set_title(video_name[3:13] + ' r:' + str(t_rank) + ' s:' + str(t_score) )
        ax.legend()
    plt.show()


def run(vgg, fei, msr, rcnn, turker_labels):
    SERVER_STORAGE_FRAMES = 5 * 30 # 5 sec * 30 fps
    BASELINE_SAMPLERATE = 0.02

    QUERY_LIST = './query.txt'
    queries = open(QUERY_LIST).read().split()
    
    VIDEO_LIST = '/mnt/video_list.txt'
    videos = open(VIDEO_LIST).read().split()


    ## Modify ##
    greedy_folder = '/home/t-yuche/luckyframe-eval/greedy-log'
    ##    
    query_dcgs = {'uniform': [], 'greedy': []}
    server_storage = []
    for query_str in queries:
        query = query_str.split('-')[0]

        n_video_tfs = []
        uni_video_tfs = []
        greedy_video_tfs = []
        turker_video_tfs = []
        sample_rates = []

        for vid, video_name in enumerate(videos):
        
            if video_name not in vgg or video_name not in turker_labels or video_name == "100_mile_wilderness_sled_dog_race_Qv4I_MDX7ws" or video_name == "70000_subscriber_thank_you_2bg_real_life_basketball_ep_5__game_of_horse_Qft3fOZjBgU":
                continue
            
            # load data
            vgg_data = vgg[video_name]
            fei_data = fei[video_name]
            msr_data = msr[video_name]
            rcnn_data = rcnn[video_name]
            turker_data = turker_labels[video_name]

            # load greedy subsampled frames
            greedy_gt_path = os.path.join(greedy_folder, video_name +  '_0.4_gtframe.pickle')
            with open(greedy_gt_path) as gt_fh:
                selected_frame_obj = pickle.load(gt_fh)
                greedy_frames = [ str(x) + '.jpg' for x in selected_frame_obj['picked_f']]
                video_len_f = selected_frame_obj['total_frame']
                subsampled_rate = selected_frame_obj['picked_rate']
                sample_rates += [subsampled_rate]
                #print subsampled_rate
                    
            # baseline
            uniform_frames = naive_subsample_frames(os.listdir(os.path.join('/mnt/frames', video_name)), BASELINE_SAMPLERATE) 
             
            # turker frames
            turker_frames = sorted([x['frame_name'] for x in turker_data], key=lambda x:int(x.split('.')[0]))
            
 
            # add random delays to each video stream -- starting at random position
            hash_str = video_name + query_str
            hash_val = int(abs(hash(hash_str)))%10
            video_start_fid = int((video_len_f/10.0) * hash_val)
            video_end_fid = min(video_start_fid + SERVER_STORAGE_FRAMES, video_len_f - 1)

            #print video_name, video_start_fid, video_end_fid
        
            '''       
            ## Turker labeled frames ## 
            '''
            '''
            turker_range_fids = get_inrange_fids(video_start_fid, video_end_fid, turker_frames)
            turker_tf = get_turker_subsampled_tf(video_name, turker_data, turker_range_fids)
            turker_video_tfs += [{'video_name': video_name, 'tf': turker_tf}]
            '''
            #print turker_frames
            #print turker_range_fids
            
            '''
            ## Non-subsampled video ## 
            '''
            # process in-server info for non-subsampled video
            _vgg_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, vgg_data)
            _fei_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, fei_data)
            _msr_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, msr_data)
            _rcnn_data = filter(lambda x: int(x['image_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['image_path'].split('/')[-1].split('.')[0]) <= video_end_fid, rcnn_data)
            
            tf_list = combine_all_models(video_name, _vgg_data, _msr_data, _rcnn_data, _fei_data)
            tf = get_combined_tfs(tf_list)
            n_video_tfs += [{'video_name': video_name, 'tf': tf}]
            #print n_video_tfs
              
            '''
            ## Baseline -- uniformly subsampled video ## 
            '''
            # process in-server info for subsampled video
            uni_range_fids = get_inrange_fids(video_start_fid, video_end_fid, uniform_frames)
            uni_tf = get_subsampled_tf(video_name, vgg_data, msr_data, rcnn_data, fei_data, uni_range_fids)
            uni_video_tfs += [{'video_name': video_name, 'tf': uni_tf}]

            '''
            ## Greedy -- subsampled video ##
            '''
            greedy_range_fids = get_inrange_fids(video_start_fid, video_end_fid, greedy_frames)
            #print 'greedy frames', greedy_frames
            #print 'greedy range fids', greedy_range_fids
            greedy_tf = get_subsampled_tf(video_name, vgg_data, msr_data, rcnn_data, fei_data, greedy_range_fids)
            greedy_video_tfs += [{'video_name': video_name, 'tf': greedy_tf}]
            #print greedy_video_tfs

        # ranking for a given query
        n_video_rank = rank(query, n_video_tfs)
        uni_video_rank = rank(query, uni_video_tfs) 
        greedy_video_rank = rank(query, greedy_video_tfs)
        #print turker_video_tfs
        #turker_video_rank = rank(query, turker_video_tfs) 

        rn_video_rank, k = reindexing(n_video_rank, n_video_rank, COSSIM_THRESH)
        runi_video_rank, k  = reindexing(n_video_rank, uni_video_rank, COSSIM_THRESH)
        rgreedy_video_rank, k = reindexing(n_video_rank, greedy_video_rank, COSSIM_THRESH)
        #rturker_video_rank = reindexing(n_video_rank, turker_video_rank, COSSIM_THRESH)
        
        video_rel = get_video_rel(n_video_rank, COSSIM_THRESH)    
        gt_dcg = dcg(video_rel, n_video_rank, COSSIM_THRESH)

        #turker_video_rel = get_video_rel(turker_video_rank, COSSIM_THRESH)
        #turker_dcg = dcg(turker_video_rel, turker_video_rank, COSSIM_THRESH)
        #print 'gt_dcg', gt_dcg
 
        #print n_video_rank
        #print rn_video_rank
        #print rn_video_rank
        #print '\n--------- Query', query_str, '-------'
        #print 'Ground-truth'
        #print n_video_rank 
        #print 'kendall tau:', kendall_correlation(rn_video_rank, rn_video_rank)
        #print 'APK:', apk(rn_video_rank, rn_video_rank, k)
        #print 'dcg:', dcg(video_rel, n_video_rank, COSSIM_THRESH)/gt_dcg

        
        #print uni_video_rank
        #print rn_video_rank
        print '\nUniform'
        print runi_video_rank
        #print 'kendall tau:', kendall_correlation(rn_video_rank, runi_video_rank)
        #print 'APK:', apk(rn_video_rank, runi_video_rank, k)
        uni_dcg =  dcg(video_rel, uni_video_rank, COSSIM_THRESH)/gt_dcg
        print 'dcg:', uni_dcg
        query_dcgs['uniform'] += [uni_dcg]

        #print greedy_video_rank
        print '\nGreedy'
        print rgreedy_video_rank
        print greedy_video_rank
        #print 'kendall tau:', kendall_correlation(rn_video_rank, rgreedy_video_rank)
        #print 'APK:', apk(rn_video_rank, rgreedy_video_rank, k)
        greedy_dcg = dcg(video_rel, greedy_video_rank, COSSIM_THRESH)/gt_dcg
        print 'dcg:', greedy_dcg
        query_dcgs['greedy'] += [greedy_dcg]
        #print 'ave sample rate:', np.mean(sample_rates), np.std(sample_rates, ddof = 1)
        
        #plot_rank_debug(n_video_rank, n_video_tfs, uni_video_tfs, uni_video_rank, query_str, test_scheme_name = "uniform")
        #plot_rank_debug(n_video_rank, n_video_tfs, greedy_video_tfs, greedy_video_rank, query_str, test_scheme_name = "greedy")
    print '' 
    print 'Unifrom:', np.mean(query_dcgs['uniform']), np.std(query_dcgs['uniform'])
    print 'Greedy:', np.mean(query_dcgs['greedy']), np.std(query_dcgs['greedy'])

def run_parallel(vgg, fei, msr, rcnn, turker_labels):

    SERVER_STORAGE_FRAMES = 5 * 30 # 5 sec * 30 fps

    QUERY_LIST = './query.txt'
    queries = open(QUERY_LIST).read().split()
    
    VIDEO_LIST = '/mnt/video_list.txt'
    videos = open(VIDEO_LIST).read().split()

    
    
    ## Modify ##
    greedy_folder = '/home/t-yuche/luckyframe-eval/greedy-log'
    ##    
    query_dcgs = {'uniform': [], 'greedy': []}
    server_storage = []
    for query_str in queries:
        query = query_str.split('-')[0]

        n_video_tfs = []
        uni_video_tfs = []
        greedy_video_tfs = []
        turker_video_tfs = []

        for vid, video_name in enumerate(videos):
        
            if video_name not in vgg or video_name not in turker_labels or video_name == "100_mile_wilderness_sled_dog_race_Qv4I_MDX7ws":
                continue
            
            # load data
            vgg_data = vgg[video_name]
            fei_data = fei[video_name]
            msr_data = msr[video_name]
            rcnn_data = rcnn[video_name]
            turker_data = turker_labels[video_name]

            # load greedy subsampled frames
            greedy_gt_path = os.path.join(greedy_folder, video_name +  '_0.4_gtframe.pickle')
            with open(greedy_gt_path) as gt_fh:
                selected_frame_obj = pickle.load(gt_fh)
                greedy_frames = [ str(x) + '.jpg' for x in selected_frame_obj['picked_f']]
                video_len_f = selected_frame_obj['total_frame']
                subsampled_rate = selected_frame_obj['picked_rate']
            
             
            # baseline
            uniform_frames = naive_subsample_frames(os.listdir(os.path.join('/mnt/frames', video_name)), subsampled_rate) 
           
            # turker frames
            turker_frames = sorted([x['frame_name'] for x in turker_data], key=lambda x:int(x.split('.')[0]))
            
 
            # add random delays to each video stream -- starting at random position
            hash_str = video_name + query_str
            hash_val = int(abs(hash(hash_str)))%10
            video_start_fid = int((video_len_f/10.0) * hash_val)
            video_end_fid = min(video_start_fid + SERVER_STORAGE_FRAMES, video_len_f - 1)

            print video_name, video_start_fid, video_end_fid
        
            '''       
            ## Turker labeled frames ## 
            '''
            turker_range_fids = get_inrange_fids(video_start_fid, video_end_fid, turker_frames)
            turker_tf = get_turker_subsampled_tf(video_name, turker_data, turker_range_fids)
            turker_video_tfs += [{'video_name': video_name, 'tf': turker_tf}]
            #print turker_frames
            #print turker_range_fids
            
            '''
            ## Non-subsampled video ## 
            '''
            # process in-server info for non-subsampled video
            _vgg_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, vgg_data)
            _fei_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, fei_data)
            _msr_data = filter(lambda x: int(x['img_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['img_path'].split('/')[-1].split('.')[0]) <= video_end_fid, msr_data)
            _rcnn_data = filter(lambda x: int(x['image_path'].split('/')[-1].split('.')[0]) >= video_start_fid and int(x['image_path'].split('/')[-1].split('.')[0]) <= video_end_fid, rcnn_data)
            
            tf_list = combine_all_models(video_name, _vgg_data, _msr_data, _rcnn_data, _fei_data)
            tf = get_combined_tfs(tf_list)
            n_video_tfs += [{'video_name': video_name, 'tf': tf}]
            #print n_video_tfs
              
            '''
            ## Baseline -- uniformly subsampled video ## 
            '''
            # process in-server info for subsampled video
            uni_range_fids = get_inrange_fids(video_start_fid, video_end_fid, uniform_frames)
            uni_tf = get_subsampled_tf(video_name, vgg_data, msr_data, rcnn_data, fei_data, uni_range_fids)
            uni_video_tfs += [{'video_name': video_name, 'tf': uni_tf}]

            '''
            ## Greedy -- subsampled video ##
            '''
            greedy_range_fids = get_inrange_fids(video_start_fid, video_end_fid, greedy_frames)
            #print 'greedy frames', greedy_frames
            print 'greedy range fids', greedy_range_fids
            greedy_tf = get_subsampled_tf(video_name, vgg_data, msr_data, rcnn_data, fei_data, greedy_range_fids)
            greedy_video_tfs += [{'video_name': video_name, 'tf': greedy_tf}]
            #print greedy_video_tfs

        # ranking for a given query
        n_video_rank = rank(query, n_video_tfs)
        uni_video_rank = rank(query, uni_video_tfs) 
        greedy_video_rank = rank(query, greedy_video_tfs)
        #print turker_video_tfs
        turker_video_rank = rank(query, turker_video_tfs) 

        rn_video_rank, k = reindexing(n_video_rank, n_video_rank, COSSIM_THRESH)
        runi_video_rank, k  = reindexing(n_video_rank, uni_video_rank, COSSIM_THRESH)
        rgreedy_video_rank, k = reindexing(n_video_rank, greedy_video_rank, COSSIM_THRESH)
        rturker_video_rank = reindexing(n_video_rank, turker_video_rank, COSSIM_THRESH)
        
        video_rel = get_video_rel(n_video_rank, COSSIM_THRESH)    
        gt_dcg = dcg(video_rel, n_video_rank, COSSIM_THRESH)

        turker_video_rel = get_video_rel(turker_video_rank, COSSIM_THRESH)
        turker_dcg = dcg(turker_video_rel, turker_video_rank, COSSIM_THRESH)
        #print 'gt_dcg', gt_dcg
 
        #print n_video_rank
        #print rn_video_rank
        #print rn_video_rank
        print '\n--------- Query', query_str, '-------'
        print 'Ground-truth'
        print n_video_rank 
        #print 'kendall tau:', kendall_correlation(rn_video_rank, rn_video_rank)
        #print 'APK:', apk(rn_video_rank, rn_video_rank, k)
        print 'dcg:', dcg(video_rel, n_video_rank, COSSIM_THRESH)/gt_dcg

        
        #print uni_video_rank
        #print rn_video_rank
        print runi_video_rank
        print '\nUniform'
        #print 'kendall tau:', kendall_correlation(rn_video_rank, runi_video_rank)
        #print 'APK:', apk(rn_video_rank, runi_video_rank, k)
        uni_dcg =  dcg(video_rel, uni_video_rank, COSSIM_THRESH)/gt_dcg
        print 'dcg:', uni_dcg
        query_dcgs['uniform'] += [uni_dcg]

        #print greedy_video_rank
        #print rn_video_rank
        print rgreedy_video_rank
        print '\nGreedy'
        #print 'kendall tau:', kendall_correlation(rn_video_rank, rgreedy_video_rank)
        #print 'APK:', apk(rn_video_rank, rgreedy_video_rank, k)
        greedy_dcg = dcg(video_rel, greedy_video_rank, COSSIM_THRESH)/gt_dcg
        print 'dcg:', greedy_dcg
        query_dcgs['greedy'] += [greedy_dcg]

        
        #plot_rank_debug(n_video_rank, n_video_tfs, uni_video_tfs, uni_video_rank, query_str, test_scheme_name = "uniform")
        #plot_rank_debug(n_video_rank, n_video_tfs, greedy_video_tfs, greedy_video_rank, query_str, test_scheme_name = "greedy")
    print '' 
    print 'Unifrom:', np.mean(query_dcgs['uniform']), np.std(query_dcgs['uniform'])
    print 'Greedy:', np.mean(query_dcgs['greedy']), np.std(query_dcgs['greedy'])
