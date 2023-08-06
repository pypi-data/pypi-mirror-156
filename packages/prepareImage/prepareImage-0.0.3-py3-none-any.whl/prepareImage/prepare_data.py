import argparse

from prepareImage.line_hed import CropLayer
import os
import pathlib
import random

import cv2
import numpy as np
import pandas as pd
import glob
from PIL import Image, ImageOps 
import imagehash
from skimage.feature import canny

from wand.image import Image as WImage
################################################################################################################################################
################################################################# Tools ########################################################################
################################################################################################################################################
# functions which can be considered as tools
def is_image(filename):
    f = filename.lower()
    return f.endswith(".png") or f.endswith(".jpg") or \
        f.endswith(".jpeg") or f.endswith(".bmp") or \
        f.endswith(".gif") or '.jpg' in f or  f.endswith(".svg")

def makeDir(pos2_dir, pos7_dir, grayscale_dir, output_dir, train_dir, val_dir, test_dir, line_dir, combine_dir):
    for path in list([pos2_dir, pos7_dir, grayscale_dir, output_dir, train_dir, val_dir, test_dir, line_dir, combine_dir]):
        if not os.path.exists(path):
            os.makedirs(path)

def deload(pos2_path, line_path, real_path, combine_path):
    input_image = cv2.imread(pos2_path)
    line_image = cv2.imread(line_path)
    real_image = cv2.imread(real_path)

    vis = np.concatenate((real_image, input_image, line_image), axis=1)
    cv2.imwrite(combine_path, vis)

def convertToPosN(df_grayscale,pos_path, pos):
    # with Image.open(f"{df_grayscale[0]}") as img:
    #     img = ImageOps.posterize(img, 2) 
    #     img.save(fp=f"{pos_path}/{df_grayscale[0].split('/')[-1]}")
    with WImage(filename=f"{df_grayscale[0]}") as image:
        image.posterize(2, 'no')
        image.save(filename=f"{pos_path}/{df_grayscale[0].split('/')[-1]}")
    pass

def generateLine(df_grayscale, hed_path, net):
    image=cv2.imread(f"{df_grayscale[0]}")
    height = image.shape[0]
    width = image.shape[1]

    inp = cv2.dnn.blobFromImage(image, scalefactor=1.0, size=(width, height),
                            mean=(104.00698793, 116.66876762, 122.67891434),
                            swapRB=False, crop=False)
    net.setInput(inp)
    # edges = cv.Canny(image,image.shape[1],image.shape[0])
    out = net.forward()

    out = out[0, 0]
    out = cv2.resize(out, (image.shape[1], image.shape[0]))

    # print(out.shape)
    out=cv2.cvtColor(out,cv2.COLOR_GRAY2BGR)
    out = 255 * out
    out = out.astype(np.uint8)
    img_gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    thinned = cv2.ximgproc.thinning(img_gray)
    #cv.imwrite('out.jpg',con)
    cv2.imwrite(f"{hed_path}/{df_grayscale[0].split('/')[-1]}", thinned)

def make_grayscale(df_image, grayscale_path):
    image=cv2.imread(f"{df_image[0]}")
    out=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"{grayscale_path}/{df_image[0].split('/')[-1]}", out)

################################################################################################################################################
####################################################### Processing functions ###################################################################
################################################################################################################################################

def split(combine_dir,train_dir,val_dir,test_dir):

    combine_list_shufflled = [os.path.join(combine_dir, f) for f in sorted(os.listdir(combine_dir))
                      if is_image(os.path.join(combine_dir, f))]
    random.Random('VALUEGAN').shuffle(combine_list_shufflled)

    train_size = int(len(combine_list_shufflled)*0.7)
    val_size = int(len(combine_list_shufflled)*0.2)
    test_size = len(combine_list_shufflled) - train_size - val_size

    #split train
    for i in range(train_size):
        # move from combine_dir to train_dir
        os.replace(combine_list_shufflled[i],str(train_dir+f"/{combine_list_shufflled[i].split('/')[-1]}")) 
        if (i+1) % 10 ==0:
            print(".", end='', flush=True)
    print(f"finish split {train_size} pictures to {train_dir}")
    #split val
    for i in range(train_size, train_size+val_size):
        os.replace(combine_list_shufflled[i],str(val_dir+f"/{combine_list_shufflled[i].split('/')[-1]}")) 
        if (i+1-train_size) % 10 ==0:
            print(".", end='', flush=True)
    print(f"finish split {val_size} pictures to {val_dir}")
    #split test
    for i in range(train_size+val_size,len(combine_list_shufflled)):
        os.replace(combine_list_shufflled[i],str(test_dir+f"/{combine_list_shufflled[i].split('/')[-1]}")) 
        if (i+1 - train_size - val_size) % 10 ==0:
            print(".", end='', flush=True)
    print(f"finish split {test_size} pictures to {test_dir}")

def combine(pos2_dir,line_dir,output_dir,combine_dir):

    paired_filenames_1 = [os.path.join(pos2_dir, f) for f in sorted(os.listdir(pos2_dir))
                      if is_image(os.path.join(pos2_dir, f))]
    paired_filenames_3 = [os.path.join(output_dir, f) for f in sorted(os.listdir(output_dir))
                      if is_image(os.path.join(output_dir, f))]
    paired_filenames_2 = [os.path.join(line_dir, f) for f in sorted(os.listdir(line_dir))
                      if is_image(os.path.join(line_dir, f))]
    
    for i in range(0, len(paired_filenames_1)):
        try:
            deload(paired_filenames_1[i],paired_filenames_2[i],paired_filenames_3[i],str(combine_dir+f"/{i}.png"))
        except Exception as e:
            print('Problem:', e, 'with i = ', i, len(paired_filenames_1),len(paired_filenames_2),len(paired_filenames_3))
            quit()
        if (i+1) % 10 ==0:
            print(".", end='', flush=True)
    print(f"finish combine {paired_filenames_1*3} to {paired_filenames_1} pictures in {combine_dir}")


def grayscale(image_path, grayscale_path):
    list_grayscale = np.array(sorted(glob.glob(f'{image_path}/*.png')))
    df_grayscale = pd.DataFrame(list_grayscale)
    df_grayscale.apply(lambda x: make_grayscale(x,grayscale_path),axis = 1)

def posterize(grayscale_path,pos_path, pos):
    list_grayscale = np.array(sorted(glob.glob(f'{grayscale_path}/*.png')))
    df_grayscale = pd.DataFrame(list_grayscale)
    df_grayscale.apply(lambda x: convertToPosN(x,pos_path, pos),axis = 1)

def hed(grayscale_path, hed_path, prototxt, caffemodel):
    list_grayscale = np.array(sorted(glob.glob(f'{grayscale_path}/*.png')))
    df_grayscale = pd.DataFrame(list_grayscale)
    net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
    cv2.dnn_registerLayer('Crop', CropLayer)
    df_grayscale.apply(lambda x: generateLine(x, hed_path, net),axis = 1)
def removeLookAlike(grayscale_path):
    paired_filenames = [os.path.join(grayscale_path, f) for f in sorted(os.listdir(grayscale_path))
                      if is_image(os.path.join(grayscale_path, f))]
    images = {}
    count = 0
    # inspired by https://github.com/JohannesBuchner/imagehash
    for img in paired_filenames:
        try:
            hash = imagehash.dhash(Image.open(img))
        except Exception as e:
            print('Problem:', e, 'with', img)
            continue
        if hash in images:
            count += 1
            print(img, '  already exists as', ' '.join(images[hash]))
            os.remove(img)
        else:
            images[hash] = images.get(hash, []) + [img]
    print(f"deleted {count} images")

def removeWithoutEdge(grayscale_path):
    paired_filenames = [os.path.join(grayscale_path, f) for f in sorted(os.listdir(grayscale_path))
                      if is_image(os.path.join(grayscale_path, f))]
    count = 0
    for img in paired_filenames:
        image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        edge = np.uint8(canny(image, sigma=2.5, mask=None) * 255)
        if np.count_nonzero(edge) == 0:
            count += 1
            os.remove(img)
            print('removed', img)
            
    print(f"deleted {count} images")


def process(**kwargs):
    mode = kwargs["mode"]
    pos2_dir = kwargs["pos2_dir"]
    pos7_dir = kwargs["pos7_dir"]
    pos = kwargs["pos"]
    grayscale_dir = kwargs["grayscale_dir"]
    output_dir = kwargs["output_dir"]
    combine_dir = kwargs["combine_dir"]
    train_dir = kwargs["train_dir"]
    val_dir = kwargs["val_dir"]
    test_dir = kwargs["test_dir"]
    line_dir = kwargs["line_dir"]
    prototxt = kwargs["prototxt"]
    caffemodel = kwargs["caffemodel"]
    image_dir = kwargs["image_dir"]

    makeDir(pos2_dir, pos7_dir, grayscale_dir, output_dir, train_dir, val_dir, test_dir, line_dir, combine_dir)

    if mode == "combine":
        combine(pos2_dir,line_dir,output_dir,combine_dir)
    elif mode == "split":
        split(combine_dir, train_dir, val_dir, test_dir)
    elif mode == "pos":
        posterize(grayscale_dir,pos7_dir, pos)
    elif mode == "line":
        hed(grayscale_dir, line_dir, prototxt, caffemodel)
    elif mode == "gray":
        grayscale(image_dir, grayscale_dir)
    elif mode == "look_alike":
        removeLookAlike(grayscale_dir)
    elif mode == "without_edge":
        removeWithoutEdge(grayscale_dir)
    elif mode == "all":
        print("Mode: all")
        print("Create Grayscale Images")
        grayscale(image_dir, grayscale_dir)
        print("Remove Look Alike Grayscale Images")
        removeLookAlike(grayscale_dir)
        print("Remove Images Without Edge")
        removeWithoutEdge(grayscale_dir)
        print("Create HED Images")
        hed(grayscale_dir, line_dir, prototxt, caffemodel)
        print("Create Posterize Images")
        posterize(grayscale_dir,pos2_dir,pos)
        print("Combine")
        combine(pos2_dir,line_dir,output_dir,combine_dir)
        print("Split Dataset")
        split(combine_dir, train_dir, val_dir, test_dir)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Combine or line or pos or all')
    parser.add_argument('--mode', type=str, default="pos", help="combine or line or all")
    parser.add_argument('--pos2_dir', type=str, default='../training_data/sketchy', help="just input dir")
    parser.add_argument('--pos7_dir', type=str, default='../training_data/pos7', help="pos7 dir")
    parser.add_argument('--pos', type=int, default=2, help="posterize value")
    parser.add_argument('--grayscale_dir', type=str, default='../training_data/flickr_output', help="just output dir")
    parser.add_argument('--line_dir', type=str, default='../training_data/line', help="edge dir")
    parser.add_argument('--prototxt', type=str, default='deploy.prototxt', help="prototxt file")
    parser.add_argument('--caffemodel', type=str, default='../checkpoint/hed/hed_pretrained_bsds.caffemodel', help="model file")
    parser.add_argument('--output_dir', type=str, default='../training_data/flickr_output', help="just output dir")
    parser.add_argument('--combine_dir', type=str, default='../training_data/combine', help="folder that store paired images")
    parser.add_argument('--train_dir', type=str, default='../training_data/train', help="train dir")
    parser.add_argument('--test_dir', type=str, default='../training_data/test', help="test dir")
    parser.add_argument('--val_dir', type=str, default='../training_data/val', help="validation dir")
    parser.add_argument('--image_dir', type=str, default='../training_data/image', help="image dir")

    # ../training_data/new_data/
    args = parser.parse_args()

    assert args.mode in ["split", "combine", "line", "pos", "all", "gray", "look_alike", "without_edge"], "Unsupported mode"
    
    # Set default params
    d_params = {"mode": args.mode,
                "pos2_dir": args.pos2_dir,
                "pos7_dir": args.pos7_dir,
                "pos": args.pos,
                "grayscale_dir": args.grayscale_dir,
                "output_dir": args.output_dir,
                "combine_dir": args.combine_dir,
                "train_dir": args.train_dir,
                "test_dir": args.test_dir,
                "val_dir": args.val_dir,
                "line_dir": args.line_dir,
                "prototxt": args.prototxt,
                "caffemodel": args.caffemodel,
                "image_dir": args.image_dir,
                }
    
    process(**d_params)