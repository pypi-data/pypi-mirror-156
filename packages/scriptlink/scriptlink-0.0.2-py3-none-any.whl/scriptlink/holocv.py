#from scriptlink import *
import tensorflow as tf
import csv
import cv2
import pytesseract
import numpy as np
import mss
import os
import base64,urllib.request
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Activation, BatchNormalization
from scriptlink import FileExists
GetLocalFolder=os.getcwd()+"\\"
class ImageSortBuilderClass:
    def __init__(self, wtsname='wts.h5',numpywtsname="data.npy",modeltype="dense",keycount=16,h=28,w=28,sz=4096):
        self.h=h;self.w=w;self.sz=sz
        self.arraysz=self.sz*self.h*self.w
        self.imgs=np.empty(self.arraysz, dtype=np.uint8)
        self.res=np.arange(0, self.sz, 1, dtype=int)
        self.imgsz=self.w*self.h
        self.img_arrayindex=0;self.imgno=0
        if (modeltype=="dense"):
            self.createmodeldense(keycount)
        if (modeltype=="conv"):
            self.createmodelconv(keycount)
        self.wtsname=wtsname
        self.numpysavename=numpywtsname
        self.img_mainct=0
        self.W=None
        self.numpy=False
        '''if (len(loadname)>0):
            if (os.path.exists(loadname)==0):
                print("failed to load",loadname)
            else:
                #model.train_on_batch(X[:1], Y[:1])
                model.load_weights(wtsname)'''
    def loadmodelfromweights(self,wtsname):
        self.model.load_weights(wtsname)
    def load(self,modelname=""):
        if (os.path.exists(modelname)==0):
            print("failed to load",modelname)
            return
        self.model = tf.keras.models.load_model(modelname)
    def createmodeldense(self,keycount=16):
        print("creating dense model with"+str(keycount)+" keys")
        self.model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(1000,'relu'),
        tf.keras.layers.Dense(100,'relu'),
        tf.keras.layers.Dense(keycount,'softmax'),])
        self.model.compile('adam','sparse_categorical_crossentropy')
        self.model._name = 'Dense'
        self.numpy=True
    def createmodelconv(self,keycount=20):
        print("\r\ncreating convolutional model with"+str(keycount)+" keys")
    
        """
        Implementation of a modified LeNet-5.
        Modified Architecture -- ConvNet --> Pool --> ConvNet --> Pool --> (Flatten) --> FullyConnected --> FullyConnected --> Softmax 

        Arguments:
        input_shape -- shape of the images of the dataset
        classes -- integer, number of classes

        Returns:
        model -- a Model() instance in Keras
        """
        
        self.model = Sequential([
            
        # Layer 1
        Conv2D(filters = 6, kernel_size = 5, strides = 1, activation = 'relu', input_shape = (28,28,1), name = 'convolution_1'),
        MaxPooling2D(pool_size = 2, strides = 2, name = 'max_pool_1'),
            
        # Layer 2
        Conv2D(filters = 16, kernel_size = 5, strides = 1, activation = 'relu', name = 'convolution_2'),
        MaxPooling2D(pool_size = 2, strides = 2, name = 'max_pool_2'),
            
        # Layer 3
        Flatten(name = 'flatten'),
        Dense(units = 120, activation = 'relu', name = 'fully_connected_1'),
            
        # Layer 4
        Dense(units = 84, activation = 'relu', name = 'fully_connected_2'),
        
        # Output
        Dense(units = keycount, activation = 'softmax', name = 'output')
            
        ])
        
        self.model._name = 'LeNet5'
        self.model.compile('adam','sparse_categorical_crossentropy')
        self.numpy=False
    def recolorimage(self,name,key,bgcolor):
        tempfile=GetLocalFolder+name
        print("loading"+tempfile)
        src = cv2.imread(tempfile,cv2.IMREAD_UNCHANGED)
        src[np.all(src == 255, axis=2)] = 0
    def addimagescaled(self,name,key,scalecount=1,startsize=30,increment=2):
        sz=scalecount;start=startsize;inc=increment
        if(self.imgno>self.sz-sz-1):print("too many images");return
        tempfile=GetLocalFolder+name
        print("loading key:"+str(key)+" file:"+tempfile)
        img = cv2.imread(tempfile,cv2.IMREAD_UNCHANGED)
        if img is None:
            print("failed to read img",tempfile)
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        dimz = (start, start)
        tmpimg=img.copy()
        print(tmpimg.shape)
        newsz=sz
        #------translations
        '''for tx in range(-8,8,4):
            for ty in range(-8,8,4):
            
                translation_matrix = np.array([
                    [1, 0, tx],
                    [0, 1, ty]
                ], dtype=np.float32);
                
                translated = cv2.warpAffine(src=tmpimg, M=translation_matrix, dsize=(self.w, self.h))
                print(self.imgno,":t:",translated.shape,self.imgs.shape)
                self.imgs[self.img_arrayindex:self.img_arrayindex+self.imgsz]=translated.reshape(-1)
                self.res[self.imgno]=key
                self.img_arrayindex+=self.imgsz
                self.imgno+=1'''
        
        #----------sizes        
        while(sz>0):
        
            resized = cv2.resize(tmpimg, dim, interpolation = cv2.INTER_AREA)
            print(self.imgno,":S:",resized.shape,self.imgs.shape)
            self.imgs[self.img_arrayindex:self.img_arrayindex+self.imgsz]=resized.reshape(-1)
            self.res[self.imgno]=key
            self.img_arrayindex+=self.imgsz
            self.imgno+=1
            dimz = (start+inc*sz, start+inc*sz)
            tmpimg=img.copy()
            tmpimg=cv2.resize(tmpimg, dimz, interpolation = cv2.INTER_AREA)
            sz-=1
        self.img_mainct+=1
    def printweights(self):
        W = self.W
        print("len:",len(W))
        for a in W:
            print(a.shape)
        for a in W:
            print(a)
    def save(self,modelname=""):
        #W = self.W
        W = self.model.get_weights()
        print(self.numpysavename,"numpy savelen:",len(W),"type:",type(W))
        np.save(self.numpysavename,W)
        if (len(modelname)==0):
            self.model.save(str(self.model._name)+"_model")
        else:
            self.model.save(str(modelname))
        for a in W:
            print(a.shape)
        #A = [arr1, arr2, arr3]  # each arrX is a numpy array
        '''with h5py.File('file.h5', 'w', libver='latest') as f:  # use 'latest' for performance
            for idx, arr in enumerate(A):
                dset = f.create_dataset(str(idx), shape=(240, 240), data=arr, chunks=(240, 240)
                                        compression='gzip', compression_opts=9)'''
    def train(self,ct):
        self.imgs=self.imgs.reshape(self.sz,28,28)
        '''for i in range(self.imgno):
            plt.imshow(self.imgs[i], cmap='gray')
            plt.show()'''
        #print(self.imgs.flags,self.imgs.shape)
        while(ct>0):
            ct-=1;
            self.model.train_on_batch(self.imgs[:self.imgno], self.res[:self.imgno])
        self.model.save_weights(self.wtsname)    
        self.W = self.model.get_weights()
        self.imgs=self.imgs.reshape(-1)
    def fit(self,epoch):
        bsz=int(self.imgno/4)
        print("fitting batch size:",bsz)
        Xb=self.imgs[:self.img_arrayindex].reshape(self.imgno,28,28);
        Yb= self.res[:self.imgno]
        
        #X=self.imgs[:self.imgno];Y= self.res[:self.imgno]
        p = np.random.permutation(len(Xb))
        X=Xb[p];Y=Yb[p]
        '''for i in range(10,self.imgno,1):
            plt.imshow(X[i], cmap='gray')
            plt.suptitle(str(self.imgno)+'FITTEST :'+str(i)+","+str(Y[i]))
            plt.show()'''
        print("X:",X.shape,"Y:",Y.shape,Y)
        self.model.fit(X,Y,epochs=epoch,batch_size=bsz)
        self.model.save_weights(self.wtsname)
        self.save()
        self.imgs=self.imgs.reshape(-1)
    def fitconv(self,epoch):
        bsz=int(self.imgno/4)
        print("fitting batch size:",bsz)
        Xb=self.imgs[:self.img_arrayindex].reshape(self.imgno,28,28,1);
        Yb= self.res[:self.imgno]
        
        #X=self.imgs[:self.imgno];Y= self.res[:self.imgno]
        p = np.random.permutation(len(Xb))
        X=Xb[p];Y=Yb[p]
        '''for i in range(10,self.imgno,1):
            plt.imshow(X[i], cmap='gray')
            plt.suptitle(str(self.imgno)+'FITTEST :'+str(i)+","+str(Y[i]))
            plt.show()'''
        print("X:",X.shape,"Y:",Y.shape,Y)
        self.model.fit(X,Y,epochs=epoch,batch_size=bsz)
        self.model.save_weights(self.wtsname)
        self.save()
        self.imgs=self.imgs.reshape(-1)
    def predict(self,X):
        W = self.model.get_weights()#W = self.W
        #print(X.shape)
        X      = X.reshape(-1)           #Flatten   X      = X.reshape((X.shape[0],-1))
        #print(X.shape,W[0].shape,W[1].shape)
        X      = X @ W[0] + W[1]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[2] + W[3]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[4] + W[5]                      #Dense
        print(X)
        #X      = np.exp(X)/np.exp(X).sum(1)[...,None] #SoftmaxX      = np.exp(X) / np.sum(np.exp(X));#np.exp(X)/np.exp(X).sum(1)[...,None] #Softmax
        #print(X,np.argmax(X))
        return X    
    def singlepredict(self,X):
        W = self.model.get_weights()#W = self.W
        #print(X.shape)
        X      = X.reshape(-1)           #Flatten   X      = X.reshape((X.shape[0],-1))
        #print(X.shape,W[0].shape,W[1].shape)
        X      = X @ W[0] + W[1]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[2] + W[3]                      #Dense
        X[X<0] = 0                                    #Relu
        X      = X @ W[4] + W[5]                      #Dense
        print(X)
        #X      = np.exp(X)/np.exp(X).sum(1)[...,None] #SoftmaxX      = np.exp(X) / np.sum(np.exp(X));#np.exp(X)/np.exp(X).sum(1)[...,None] #Softmax
        #print(X,np.argmax(X))
        return X
    def showimage(self,n):
        two_d = np.reshape(self.imgs[n*self.imgsz:n*self.imgsz+self.imgsz], (28, 28))
        plt.imshow(two_d, cmap='gray')
        plt.suptitle('imgno:'+str(n)+str(self.res[n]))
        plt.show()
    def findfromfile(self,name):
        tempfile=GetLocalFolder+name
        if (FileExists(tempfile)==0):
            print("no file"+tempfile);return;
        print("loading"+tempfile)
        img = cv2.imread(tempfile,cv2.IMREAD_UNCHANGED)
        return self.find(img)
        '''img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        if (self.numpy==True):
            r=resized.reshape(1,28,28)
            p=self.singlepredict(resized).argmax(0)
            g=self.model.predict(r).argmax(1)
        else:
            r=resized.reshape(1,28,28,1)
            p=self.model.predict(r).argmax(1)
            g=""'''
    def find(self,img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        if (self.numpy==True):
            r=resized.reshape(1,28,28)
            p=self.singlepredict(resized).argmax(0)
            g=self.model.predict(r).argmax(1)
        else:
            r=resized.reshape(1,28,28,1)
            p=self.model.predict(r).argmax(1)
            g=""
        return p[0];
    def findtest(self,name,key):
        tempfile=GetLocalFolder+name
        print("loading"+tempfile)
        img = cv2.imread(tempfile,cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (self.w, self.h)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        print(resized.shape)
        if (self.numpy==True):
            r=resized.reshape(1,28,28)
            p=self.singlepredict(resized).argmax(0)
            g=self.model.predict(r).argmax(1)
        else:
            r=resized.reshape(1,28,28,1)
            p=self.model.predict(r).argmax(1)
            g=""
        plt.imshow(resized, cmap='gray')
        plt.suptitle('test title'+str(p)+","+str(g)+" ans:"+str(key))
        plt.show()
        return p;
    def runtests(self,folder,count=20):
        return
def downloadandcache(url,redl=0):
    b64n=base64.urlsafe_b64encode(url.encode('ascii')).decode()
    fname=GetLocalFolder+b64n+".txt"
    e=os.path.isfile(fname)
    print(e,fname)
    if (e and redl==0):
        print("reading file")
        f = open(fname, "r",encoding='utf-8')
        r=f.read()
        if (len(r)==0):e=0
    if ((not e) or redl==1):
        print("downloading",e,redl)
        r=urllib.request.urlopen(url).read().decode()
        f = open(fname, "w",encoding='utf-8')
        f.write(r)
        f.close()
    return r
def FixDir(file):
    return GetLocalFolder+file
def LoadCanny(imagename):
    tempfile=GetLocalFolder+imagename
    print("loading"+tempfile)
    template = cv2.imread(tempfile)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 50, 200)
    return template
def findsubimage(needle,hay):
    image = cv2.imread("hay")  
    template = cv2.imread("needle")  
    result = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
    print(result)  
    print(np.unravel_index(result.argmax(),result.shape))

def findtext(gray_image):
    #print(imagename)
    #image = cv2.imread(imagename)
    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # converting it to binary image
    #image=gray_image
    #gray_image= cv2.Laplacian(gray_image, cv2.CV_8U)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # saving image to view threshold image
    #cv2.imwrite('thresholded.png', threshold_img)

    #cv2.imshow('threshold image', threshold_img)
    tesseract_config = r'--oem 3 --psm 6'
    # now feeding image to tesseract

    details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,config=tesseract_config, lang='eng')
    
    total_boxes = len(details['text'])
    threshold_point=30
    for sequence_number in range(total_boxes):
        if int(float(details['conf'][sequence_number])) > threshold_point:
            (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number],
                            details['width'][sequence_number], details['height'][sequence_number])
            image = cv2.rectangle(gray_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # saving image to local
    #cv2.imwrite('captured_text_area.png', image)
    # display image
    #cv2.imshow('captured text', image)
    
    parse_text = []
    word_list = []
    last_word = ''
    for word in details['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == details['text'][-1]):
            parse_text.append(word_list)
            word_list = []
    with open('resulted_text.txt', 'w', newline="") as file:
        csv.writer(file, delimiter=" ").writerows(parse_text)
    
    return parse_text
    
             
def pre_processing(image):
    """
    This function take one argument as
    input. this function will convert
    input image to binary image
    :param image: image
    :return: thresholded image
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # converting it to binary image
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # saving image to view threshold image
    cv2.imwrite('thresholded.png', threshold_img)

    cv2.imshow('threshold image', threshold_img)
    # Maintain output window until
    # user presses a key
    cv2.waitKey(0)
    # Destroying present windows on screen
    cv2.destroyAllWindows()

    return threshold_img


def parse_text(threshold_img):
    """
    This function take one argument as
    input. this function will feed input
    image to tesseract to predict text.
    :param threshold_img: image
    return: meta-data dictionary
    """
    # configuring parameters for tesseract
    tesseract_config = r'--oem 3 --psm 6'
    # now feeding image to tesseract
    details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,
                                        config=tesseract_config, lang='eng')
    return details


def draw_boxes(image, details, threshold_point):
    """
    This function takes three argument as
    input. it draw boxes on text area detected
    by Tesseract. it also writes resulted image to
    your local disk so that you can view it.
    :param image: image
    :param details: dictionary
    :param threshold_point: integer
    :return: None
    """
    total_boxes = len(details['text'])
    for sequence_number in range(total_boxes):
        if int(details['conf'][sequence_number]) > threshold_point:
            (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number],
                            details['width'][sequence_number], details['height'][sequence_number])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # saving image to local
    cv2.imwrite('captured_text_area.png', image)
    # display image
    cv2.imshow('captured text', image)
    # Maintain output window until user presses a key
    cv2.waitKey(0)
    # Destroying present windows on screen
    cv2.destroyAllWindows()


def format_text(details):
    """
    This function take one argument as
    input.This function will arrange
    resulted text into proper format.
    :param details: dictionary
    :return: list
    """
    parse_text = []
    word_list = []
    last_word = ''
    for word in details['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == details['text'][-1]):
            parse_text.append(word_list)
            word_list = []

    return parse_text


def write_text(formatted_text):
    """
    This function take one argument.
    it will write arranged text into
    a file.
    :param formatted_text: list
    :return: None
    """
    with open('resulted_text.txt', 'w', newline="") as file:
        csv.writer(file, delimiter=" ").writerows(formatted_text)


if __name__ == "__main__":
    # reading image from local
    image = cv2.imread('sample_image.png')
    # calling pre_processing function to perform pre-processing on input image.
    thresholds_image = pre_processing(image)
    # calling parse_text function to get text from image by Tesseract.
    parsed_data = parse_text(thresholds_image)
    # defining threshold for draw box
    accuracy_threshold = 30
    # calling draw_boxes function which will draw dox around text area.
    draw_boxes(thresholds_image, parsed_data, accuracy_threshold)
    # calling format_text function which will format text according to input image
    arranged_text = format_text(parsed_data)
    # calling write_text function which will write arranged text into file
    write_text(arranged_text)