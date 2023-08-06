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

from pathlib import Path
from prepareImage.prepare_data import *

################################################################################################################################################
################################################################# Class Dataset ########################################################################
################################################################################################################################################

class dataset():
    # parameters 
    # image_dir: path of the folder that contains all of your raw images.
    def __init__(self,image_path):
        self.image_path = str(Path(image_path).absolute())
        self.list_raw_images = np.array([os.path.join(self.image_path, f) for f in sorted(os.listdir(self.image_path))
                      if prepare_data.is_image(os.path.join(self.image_path, f))])
        self.length = len(self.list_raw_images) 
        self.df_raw_images = pd.DataFrame(self.list_raw_images)
        self.parent_path = str(Path(image_path).parent.absolute())
        self.train_path = f"{self.parent_path}/train"
        self.val_path = f"{self.parent_path}/val"
        self.test_path = f"{self.parent_path}/test"
        self.array = [self.image_path,self.train_path,self.val_path,self.test_path]
        self.is_split = False
        pass
    
    def len(self):
        return self.length
    
    def __repr__(self):
        if not self.is_split:
            return f"Raw image directory: {self.image_path}\n \
                     This dataset contains {self.length} images"
        else:
            return f"Raw image directory: {self.image_path}\n \
                    This dataset contains {self.length} images\n \
                    Split into _ train images, _ validation images, _ test images \
                    Train image directory: {self.train_path}\n \
                    Validation image directory: {self.val_path}\n \
                    Test image directory: {self.test_path}\n \
                    "
    
    def __str__(self):
        if not self.is_split:
            return f"Raw image directory: {self.image_path}\n \
                     This dataset contains {self.length} images"
        else:
            return f"Raw image directory: {self.image_path}\n \
                    This dataset contains {self.length} images\n \
                    Split into _ train images, _ validation images, _ test images \
                    Train image directory: {self.train_path}\n \
                    Validation image directory: {self.val_path}\n \
                    Test image directory: {self.test_path}\n \
                    "
    
    def copy(self):
        return eval(repr(self))
    
    def __getitem__(self, item):
        return self.array[item]
    
    def __setitem__(self, key, value):
        self.array[key] = value