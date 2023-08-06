from cellpose import models
from PyQt5.QtCore import QObject, pyqtSignal
import imageio
import pandas as pd
import numpy as np

from typing import Tuple

from .utility import select_file

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .segmentation import Segmentation


class Communicate(QObject):
    """signals from datastructures"""

    segmentation_list_changed = pyqtSignal()
    active_segmentation_changed = pyqtSignal()
    gene_expression_changed = pyqtSignal()
    genes_mapped = pyqtSignal()
    cell_types_changed = pyqtSignal()


class Dataset:

    all = {}

    def __init__(self, name):
        """Creates an experimental dataset.

        name: Name of the dataset
        """
        # Assign information about dataset
        self.name: str = name

        # Create datastructures
        self.images: dict[str, np.ndarray] = dict()
        self.gene_expression: pd.DataFrame = None

        # Note, these are now added from the segmentation class
        self.segmentation: dict[int, "Segmentation"] = dict()
        self.active_segmentation: Segmentation = None

        # Translate is changed by the crop method
        self.translate = (0, 0)

        # Add dataset to class dictionary
        self.all[name] = self

        # instantiate communicator object
        self.com: Communicate = Communicate()

    def load_nuclei(self, path=False):
        """load nuclei image and store under images["Nuclei"]"""
        if not path:
            path = select_file(title="Please select a nuclei image")

        image = imageio.imread(path)
        self.images["Nuclei"] = image

    def load_cytoplasm(self, path=False):
        """load cytoplasm image and store under images["Cytoplasm"]"""
        if not path:
            path = select_file(title="Please select a cytoplasm image")

        image = imageio.imread(path)
        self.images["Cytoplasm"] = image

    def load_other_channel(self, channel="other", path=False):
        """load channel image and store under images[channel]"""
        if not path:
            path = select_file(title=f"Please select a {channel} image")

        image = imageio.imread(path)
        self.images[channel] = image

    def add_gene_expression(self, df):
        """Loads gene expression"""
        self.gene_expression = df
        self.com.gene_expression_changed.emit()
        #TODO: Connect this signal to downstream functions
        

    def add_segmentation(self, seg: "Segmentation"):
        """add segmentation to the end of list"""
        self.segmentation[seg.id] = seg
        self.com.segmentation_list_changed.emit()

    def remove_segmentation(self, seg: "Segmentation"):
        """remove segmentation at specificed index in list"""
        self.segmentation.pop(seg.id)
        self.com.segmentation_list_changed.emit()

    def crop(
        self, center: Tuple[float, float], width: int = 1000, height: int = 1000
    ) -> "Dataset":
        """returns a cropped version of the dataset
        with added information about the cropping"""

        # Create the new dataset to cold the cropped data
        dataset = Dataset(name=f"cropped {self.name}")

        # Calculate the bounding box coordinates of the crop
        x0, x1 = (int(center[0] - (width / 2)), int(center[0] + (width / 2)))
        y0, y1 = (int(center[1] - (height / 2)), int(center[1] + (height / 2)))

        # Store cropping information
        dataset.center = center
        dataset.width = width
        dataset.height = height
        dataset.boundingbox = (x0, x1, y0, y1)
        dataset.translate = (x0, y0)

        # Cropping images
        # TODO: investigate effect of modifying the iterable (image)
        # Should these be moved to another variable fist?
        for name, image in self.images.items():
            dataset.images[name] = image[x0:x1, y0:y1].copy()

        # Cropping genes
        if isinstance(self.gene_expression, pd.DataFrame):
            idx = list()
            for i, gene in self.gene_expression.iterrows():
                if gene.x > x0 and gene.x < x1:
                    if gene.y > y0 and gene.y < y1:
                        idx.append(i)

            df = self.gene_expression.iloc[idx].copy()
            df.x = df.x - x0
            df.y = df.y - y0
            
            dataset.add_gene_expression(df)

        return dataset

    def set_active_segmentation(self, segmentation: "Segmentation"):
        self.active_segmentation = segmentation
        self.com.active_segmentation_changed.emit()

