import os
import sys


#python /home/yuhan/neuraltalk/python_features/extract_features.py --caffe ~/caffe/ --model_def /home/yuhan/neuraltalk/python_features/VGG_ILSVRC_16_layers_deploy.prototxt --model ~/caffe/models/vgg_ilsvrc_16/VGG_ILSVRC_16_layers.caffemodel --files /home/yuhan/caffe/python/tasks.txt --out KIDS_PLAYING_BASKETBALL_recog.pickle --output_file test.json


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print 'Usage', sys.argv[0], 'frame_folder(-/frame)'
        exit(-1)
	
    video_folder = sys.argv[1]
    	
    output_file = 'vgg_keyframe_classify.sh'
    fh_out = open(output_file, 'w')

    
    for v in os.listdir(video_folder):
        video_path = os.path.join(video_folder, v)
        if not os.path.isdir(video_path):
            continue

        print video_path        
		
        task_filename = os.path.abspath(os.path.join('./tmp' , v + '_tasks.txt'))
        '''
        # generate tasks.txt
		task_filename = v + '_tasks.txt'
		fh_task_out = open(v + '_tasks.txt', 'w')
		fs = []
		for f in os.listdir(video_path):
			if f.find('.jpg') >= 0:
				fs += [f]
		for f in sorted(fs, key=lambda x: int(x.split('.')[0])):
			fh_task_out.write(os.path.join(video_path, f) + '\n')
		
		fh_task_out.close()	
        '''
        fh_out.write('python /home/t-yuche/neuraltalk/python_features/keyframe_vgg_classify.py --video_name ' + v + '\n\n') 
		# append to run script
        #fh_out.write('python /home/t-yuche/neuraltalk/python_features/vgg_classify.py --gpu --caffe ~/caffe/ --model_def /home/t-yuche/neuraltalk/python_features/VGG_ILSVRC_16_layers_deploy.prototxt --model /home/t-yuche/caffe/models/vgg_ilsvrc_16/VGG_ILSVRC_16_layers.caffemodel --files '+  task_filename + ' --output_file /mnt/tags/recognition/' + v + '_recog.json\n\n')
    fh_out.close()


	## prediction script
	##python predict_on_images.py lstm_model.p -r example_images
		
