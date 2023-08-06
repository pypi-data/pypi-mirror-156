import numpy as np
import cv2
import os

input_dir = '../training_data/sketchy/'
output_dir = '../training_data/flickr_output/'
save_path = "../training_data/lineotsu/"

os.mkdir(save_path)

input_filename = [os.path.join(input_dir, f) for f in sorted(os.listdir(input_dir))
                      if os.path.isfile(os.path.join(input_dir, f))]
output_filename = [os.path.join(output_dir, f) for f in sorted(os.listdir(output_dir))
                      if os.path.isfile(os.path.join(output_dir, f))]

print("paired file input num: %d" % len(input_filename))
print("paired file ouput num: %d" % len(output_filename))


def drawline(sigma): 
    print("processing...")
    kernel_size = 3
    _img = 0
    for i in range(0,len(input_filename)):
        inp = cv.imread(input_filename[i])
        out = cv.imread(output_filename[i], 0)

        out_blur =  cv.GaussianBlur(out,(0,0),sigma)

        high_threshold, thresh_im = cv.threshold(out_blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        low_threshold = 0.5*high_threshold
        # v = np.median(out_blur)
	    # # apply automatic Canny edge detection using the computed median
        # s = 0.33
        # low_threshold = int(max(0, (1.0 - s) * v))
        # high_threshold = int(min(255, (1.0 + s) * v))

        edges = cv.Canny(out_blur, low_threshold, high_threshold, kernel_size)
        edgeBGR = cv.cvtColor(edges,cv.COLOR_GRAY2BGR)
    
        # white=np.where((edgeBGR[:,:,0]==255) & (edgeBGR[:,:,1]==255) & (edgeBGR[:,:,2]==255))
        # inp[white]=(0,0,255)

        cv.imwrite(os.path.join(save_path, os.path.split(input_filename[i])[1]), edges)
    print("done")

drawline(sigma=2)

