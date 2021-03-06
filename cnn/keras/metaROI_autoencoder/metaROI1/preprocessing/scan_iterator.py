from keras.preprocessing.image import Iterator
import keras.backend as K
import numpy as np

from utils.sort_scans import sort_groups


class ScanIterator(Iterator):
    def __init__(self, scans, image_data_generator,
                 target_size=(8, 8, 8), load_all_scans=False,
                 dim_ordering=K.image_dim_ordering,
                 classes=None,
                 batch_size=32, shuffle=True, seed=None):
        self.image_data_generator = image_data_generator
        self.target_size = tuple(target_size)
        self.load_all_scans = load_all_scans
        self.dim_ordering = dim_ordering
        self.shuffle = shuffle
        if self.dim_ordering == 'tf':
            self.image_shape = self.target_size + (1,)
        else:
            self.image_shape = (1,) + self.target_size

        np.random.seed(seed)

        # first, count the number of samples and classes
        self.nb_sample = 0
        groups, names = sort_groups(scans)
        if not classes:
            classes = names
        self.nb_class = len(classes)
        self.class_indices = dict(zip(classes, range(len(classes))))

        for c in classes:
            assert groups[c] is not None, \
                'Could not find class %s' % c
            assert len(groups[c]) > 0, \
                'Could not find any scans for class %s' % c
            self.nb_sample += len(groups[c])
        print('Found %d scans belonging to %d classes.' % (self.nb_sample, self.nb_class))

        # second, build an index of the images in the different class subfolders
        if self.load_all_scans:
            self.scans = np.zeros((self.nb_sample,) + self.target_size, dtype='float32')
        else:
            self.scans = []
        i = 0
        for c in classes:
            for scan in groups[c]:
                if self.load_all_scans:
                    self.scans[i] = self.load_scan(scan.path)
                else:
                    self.scans.append(scan.path)
                i += 1
        super(ScanIterator, self).__init__(self.nb_sample, batch_size, shuffle, seed)

    def load_scan(self, path):
            return np.load(path)

    def get_scan(self, scan):
        if not isinstance(scan, np.ndarray):
            return self.load_scan(scan)
        return scan

    def expand_dims(self, x, dim_ordering):
        if dim_ordering == 'tf':
            return np.expand_dims(x, axis=3)
        else:
            return np.expand_dims(x, axis=0)

    def next(self):
        with self.lock:
            index_array, current_index, current_batch_size = next(self.index_generator)
        # The transformation of images is not under thread lock so it can be done in parallel
        batch_x1 = np.zeros((current_batch_size,) + self.image_shape)
        # build batch of image data
        for i, j in enumerate(index_array):
            x1 = self.get_scan(self.scans[j])
            x1 = self.expand_dims(x1, self.dim_ordering)
            batch_x1[i] = x1
        return batch_x1, batch_x1

