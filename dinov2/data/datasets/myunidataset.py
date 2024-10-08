import logging
from enum import Enum
from typing import Any, Dict, List, Tuple, Callable, Optional
from PIL import Image
from fastai.vision.all import Path, get_image_files, verify_images
import numpy as np

from dinov2.data.datasets.extended import ExtendedVisionDataset

logger = logging.getLogger("dinov2")


class MyUniDataset(ExtendedVisionDataset):
    def __init__(self, root: str, verify: bool = False, transforms: Optional[Callable] = None,
                 transform: Optional[Callable] = None, target_transform: Optional[Callable] = None) -> None:
        super().__init__(root, transforms, transform, target_transform)

        self.root = Path(root).expanduser()
        image_paths = get_image_files(self.root)
        invalid_images = set()
        if verify:
            invalid_images = set(verify_images(image_paths))
        self.image_paths = [p for p in image_paths if p not in invalid_images]

    def get_image_data(self, index: int) -> bytes:
        image_path = self.image_paths[index]
        img = Image.open(image_path)
        #img = Image.open(image_path).convert("RGB")
        #img = self.remove_transparency(img).convert('L')
        #num_channels = len(img.getbands())
        #width, height = img.size
        # logger.info("0 img type: " + str(type(img)))
        # logger.info("0 Width: " + str(width))
        # logger.info("0 Height: " + str(height))
        # logger.info("0 image mode: " + str(img.mode))
        # logger.info("0 Number of channels: " + str(num_channels))

        return img

    def get_target(self, index: int) -> Any:
        return 0

    def remove_transparency(self, im, bg_colour=(255, 255, 255)):

        # Only process if image has transparency
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

            # Need to convert to RGBA if LA format due to a bug in PIL
            alpha = im.convert('RGBA').split()[-1]

            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format

            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            return bg

        else:
            return im

    def normalize_image(self, image):
        # Convert PIL Image to numpy array
        #img_array = np.array(image).astype(np.float32)
        img_array = np.array(image)
        # Normalize the pixel values to the range [0, 1]
        #divisor = np.uint16(65535.0)
        img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min())) / 65535
        #img_array /= divisor.astype(np.uint16)

        image = Image.fromarray(img_array)

        return image

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        try:
            image = self.get_image_data(index)
        except Exception as e:
            raise RuntimeError(f"can not read image for sample {index}") from e
        target = self.get_target(index)

        #image = self.remove_transparency(image).convert('L')
        #image = image.convert('I;16')
        '''
        width, height = image.size
        logger.info("2 img type: " + str(type(image)))
        logger.info("2 Width: " + str(width))
        logger.info("2 Height: " + str(height))
        logger.info("2 image mode: " + str(image.mode))
        '''

        image = self.normalize_image(image)

        if self.transforms is not None:
            #logger.info("TRANSFORMS ENABLED")
            image, target = self.transforms(image, target)

        #logger.info("3 img type: " + str(type(image)))
        #logger.info("3 img : " + str(image))

        return image, target
