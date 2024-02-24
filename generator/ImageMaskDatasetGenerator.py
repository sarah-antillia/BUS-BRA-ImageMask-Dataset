# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 2024/01/28 
# create_base_dataset.py
# 2024/02/22 Modified to call normalize in create_image_files function.
# 2024/02/22 Modified to use PIL.Image instead of cv2.
import os
import sys
import shutil
from PIL import Image
import glob
import numpy as np
import math
import traceback

class ImageMaskDatasetGenerator:

  def __init__(self, images_dir, masks_dir, output_images_dir, output_masks_dir):
    self.images_dir = images_dir
    self.masks_dir  = masks_dir
    self.output_images_dir = output_images_dir
    self.output_masks_dir  = output_masks_dir
    self.RESIZE    = (512, 512)
       
  def create_mask_files(self, mask_filepath, name,  output_masks_dir):
    #basename = os.path.basename(mask_filepath)

    img = Image.open(mask_filepath)
    img = img.convert("RGB")
    img = self.resize_to_square(img, mask=True)
    filename = name + ".jpg"
    filepath = os.path.join(output_masks_dir, filename)      
    img.save(filepath)
    
    print("Saved {}".format(filepath))
    return 1
  
  def normalize(self, image):
    min = np.min(image)/255.0
    max = np.max(image)/255.0
    scale = (max - min)
    image = (image - min) / scale
    image = image.astype('uint8') 
    return image   

  def resize_to_square(self, image, mask=False):
    w, h = image.size
    size = w
    if h >= w:
      size = h
    px = int( (size - w)/2 )
    py = int( (size - h)/2 )

    if mask == False:
      pixel = image.getpixel((8,8))
      pixel = (60, 60, 60)
      image_background = Image.new("RGB", (size, size), pixel)
      image_background.paste(image, (px, py))
      resized_image = image_background.resize(self.RESIZE)
      return resized_image
    else:
      mask_background = Image.new("L", (size, size))
      mask_background.paste(image, (px, py))
      resized_mask  = mask_background.resize((self.RESIZE))
      return resized_mask

  def create_image_files(self, image_file, name, output_images_dir):
    img = Image.open(image_file)    
    
    img = img.convert("RGB")
    img = self.resize_to_square(img)
    filename = name + ".jpg"
    filepath = os.path.join(output_images_dir, filename)      

    img.save(filepath)
    print("Saved {}".format(filepath))
    return 1
  

  def generate(self):
    image_files = glob.glob(self.images_dir + "/*.png")

    for image_file in image_files:
        basename = os.path.basename(image_file)
        nameonly = basename.split(".")[0]
        name     = nameonly.replace("bus_", "")
        mask_name = "mask_" + name + ".png"
        mask_file = os.path.join(self.masks_dir, mask_name)
        print("---image file {}".format(image_file))

        print("---mask file  {}".format(mask_file))
        
        # 1 create mask files at first. 
        num_masks  = self.create_mask_files(mask_file,  name, self.output_masks_dir)
        # 2 create image files if mask files exist.
        num_images = self.create_image_files(image_file, name, self.output_images_dir)
        print(" num_images: {}  num_masks: {}".format(num_images, num_masks))


if __name__ == "__main__":
  try:
    images_dir        = "./BUSBRA/Images"
    labels_dir        = "./BUSBRA/Masks"
    output_images_dir = "./BUSBRA-master/images/"
    output_masks_dir  = "./BUSBRA-master/masks/"

    if os.path.exists(output_images_dir):
      shutil.rmtree(output_images_dir)
    if not os.path.exists(output_images_dir):
      os.makedirs(output_images_dir)

    if os.path.exists(output_masks_dir):
      shutil.rmtree(output_masks_dir)
    if not os.path.exists(output_masks_dir):
      os.makedirs(output_masks_dir)

    # Create jpg image and mask files from nii.gz files under data_dir.                                           
    generator = ImageMaskDatasetGenerator(images_dir, labels_dir, 
                                          output_images_dir, output_masks_dir)
    generator.generate()

  except:
    traceback.print_exc()


