import os, csv, cv2, random
import numpy as np

class CelebA(object):

    def __init__(self, op_size, channel, sample_size, batch_size, data_dir='D:/Data/celeba/'):

        self.dataname = 'CelebA'
        self.sample_size = sample_size
        self.batch_size = batch_size
        self.dims = op_size*op_size
        self.shape = [op_size,op_size,channel]
        self.image_size = op_size
        self.data_dir = data_dir
        self.y_dim = 11
        self.data, self.data_y = self.load_data()

    def load_data(self):
        cur_dir = os.getcwd()

        X = []
        y = []

        with open(os.path.join(self.data_dir,'list_attr_celeba.csv')) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            data = []
            for row in readCSV:
                data.append(row)
            del data[0]
            random.shuffle(data[:20000])
            images_dir = os.path.join(self.data_dir,'img_align_celeba')
            for i in range(1,self.sample_size):
                img = data[i][0]
                print('\rLoading: {}'.format(img), end='')
                image = cv2.imread(os.path.join(images_dir,img))
                image = cv2.resize(image, (self.image_size, self.image_size))
                X.append(image)
                features = np.zeros(self.y_dim)
                features[0] = int(data[i][5])        #Bald
                features[1] = int(data[i][9])        #Black hair
                features[2] = int(data[i][10])       #Blond hair
                features[3] = int(data[i][12])       #Brown hair
                features[4] = int(data[i][16])       #Glasses
                features[5] = int(data[i][17])       #Goatee
                features[6] = int(data[i][18])       #Gray hair
                features[7] = int(data[i][21])       #Male
                features[8] = int(data[i][23])       #Mustache
                features[9] = int(data[i][25]) * -1  #Beard (invert because in dataset, positive 1 represents no beard)
                features[10] = int(data[i][27])     #Pale skin
                y.append(features)

        print('')
        X = np.array(X)
        y = np.array(y)

        seed = 547

        np.random.seed(seed)
        np.random.shuffle(X)
        np.random.seed(seed)
        np.random.shuffle(y)

        return X / 255. , y

    def get_next_batch(self, iter_num):
        ro_num = len(self.data) / self.batch_size - 1

        if iter_num % ro_num == 0:
            length = len(self.data)
            perm = np.arange(length)
            np.random.shuffle(perm)
            self.data = np.array(self.data)
            self.data = self.data[perm]
            self.data_y = np.array(self.data_y)
            self.data_y = self.data_y[perm]

        return self.data[int(iter_num % ro_num) * self.batch_size: int(iter_num % ro_num + 1) * self.batch_size], self.data_y[int(iter_num % ro_num) * self.batch_size: int(iter_num % ro_num + 1) * self.batch_size]

    def text_to_vector(self, text):
        key_words = {'bald':1.,
                    'black hair':1.,
                    'blond hair':1.,
                    'brown hair':1.,
                    'glasses':1.,
                    'gray hair':1.,
                    'male':1.,
                    'mustache':1.,
                    'beard':1.,
                    'white':1.
                    }
        vec = np.ones(self.y_dim)*-1
        for key, i in enumerate(key_words, 0):
            if key in text:
                vec[i] = key_words[key]
        batch_vector = np.tile(vec,(self.batch_size,1))
        return batch_vector

def merge(images, size):
    h, w = images.shape[1], images.shape[2]
    if (images.shape[3] in (3,4)):
        c = images.shape[3]
        img = np.zeros((h * size[0], w * size[1], c))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w, :] = image
        return img
    elif images.shape[3]==1:
        img = np.zeros((h * size[0], w * size[1]))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w] = image[:,:,0]
        return img
    else:
        raise ValueError('in merge(images,size) images parameter must have dimensions: HxW or HxWx3 or HxWx4')

def inverse_transform(images):
    return (images+1.)/2.

def save_images(images, size, image_path):
    return imsave(inverse_transform(images), size, image_path)

def imsave(images, size, path):
    image = np.squeeze(merge(images, size))
    return cv2.imwrite(path, image)