import numpy as np
import cv2
from math import sqrt

#helper Functions
def convertTuple(tup):
  str =  ''.join(tup)
  return str


def FromStringToListLayOut(string):

  string = string.replace('[', '')
  string = string.replace(']', '')
  string = string.replace('\n','')

  li = list(string.split(" "))
  for i in list(li):
      if i == "" :
          li.remove(i)

  for i in range(len(li)) :
      li[i] = float(li[i])
  return li

def FromStringToList(string):
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\n','')
    li = list(string.split(" "))
    print(li)
    for i in range(len(li)) :
            li[i] = np.float(li[i])
    return li

#error metric for mean
def CalcMeanError(inputFeature,databaseFeature): 
  # Mean Squared Error
  MSE = np.abs(np.subtract((inputFeature/ np.linalg.norm(inputFeature)),(databaseFeature/np.linalg.norm(databaseFeature)))).mean()
  return MSE

#error metric for layout
def CalcLayoutError(inputLayout,databaseLayout):
  shape = inputLayout.shape
  rows = shape[0]
  error = 0
  for i in range(rows):
    error += CalcMeanError(inputLayout[i],databaseLayout[i])
  error /= rows
  return error

#Evaluate the error
def Evaluation(error,Threshold):
  if (error<=Threshold):
    return True
  elif (error>Threshold):
    return False
  else: print("error from Evaluation")

#error metric for histo
def CalcHistoError(inputHisto,databaseHisto):
  inputHisto = np.float32(inputHisto)
  databaseHisto  = np.float32(databaseHisto)
  error = cv2.compareHist(inputHisto, databaseHisto, cv2.HISTCMP_BHATTACHARYYA)
  # error = error/np.sum(databaseHisto)
  return error

def CalcErrorVideo(inputHisto,databaseHisto):
  inputHisto = np.float32(inputHisto)
  databaseHisto = np.float32(databaseHisto)
  correlation = cv2.compareHist(inputHisto, databaseHisto, cv2.HISTCMP_CORREL)
  error = 1-correlation
  return error
def Get_Color_Features(path,bins):

  '''
  Computes the color feature vector of the image
  based on RGB histogram
  '''
  img = cv2.imread(path)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

 
  histSize = [bins, bins, bins]



  channels = [0, 1, 2]

  # extract a 3D RGB color histogram from the image,
  # using bins per channel, normalize, and update
  # the index
  hist = cv2.calcHist([img], channels , None, histSize, [0, 256, 0, 256, 0, 256])
  hist = cv2.normalize(hist, hist).flatten()
  # print("shape of Get_Color_Features1 must be 1,X : ", hist.shape) 
 
  return hist

#to save the full histogram
def CreateHistoInfo(path):
  editedPath = path.split(".")[0].split("/")[-1]
  features = Get_Color_Features(path,4)
  FileName = "histoinfo" + "/" + editedPath + ".txt"
  f = open(FileName, "w")
  f.write(str(features))
  f.close()
  return FileName

#to save the full blocks
def CreateLayoutInfo(path):
  editedPath = path.split(".")[0].split("/")[-1]
  features = Color_Layout(path,36)
  FileName = "layoutinfo" + "/" + editedPath + ".txt"
  f = open(FileName, "w")
  f.write(str(features))
  f.close()
  return FileName

#get all histo info
def GetHistoInfo(path):
  editedPath = path.split(".")[0].split("/")[-1]
  features = Get_Color_Features(path,4)
  # if (path == 'Images/sky-orange.jpg'):
  #     print("in cond")
  #     print(editedPath)
  #     print(features[0])
  #     print(features)

  FileName = "histoinfo" + "/" + editedPath + ".txt"
  f = open(FileName, "r")
  features_list = FromStringToListLayOut(f.read())
  # if (path == 'Images/sky-orange.jpg'):
  #   print(features_list)
  features = np.array(features_list)
  features = features.reshape(1,pow(4,3))
  # if (path == 'Images/sky-orange.jpg'):
  #   print("in cond")
  #   print(features[0])
  #   print(features)
  return features[0]

#get all layout info
def GetLayoutInfo(path):
  editedPath = path.split(".")[0].split("/")[-1]
  features = Color_Layout(path,36)
  FileName = "layoutinfo" + "/" + editedPath + ".txt"
  f = open(FileName, "r")
  features_list = FromStringToListLayOut(f.read())
  features = np.array(features_list)
  features = features.reshape(36,3)
  return features

def Feature_Normalization(feature):
    mean=np.mean(feature)
    dev=np.std(feature)
    feature = (feature - mean)/dev
    return feature

def Mean_Color(image_path):
    """
    parameter: path of RGB image 
    return:    list of length 3 contains mean_color where index 0 for red channel index 1 for green channel index 2 for blue channel
    """
    Mean_Color = []
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    channels = cv2.mean(image)
    Mean_Color.append(channels[2])
    Mean_Color.append(channels[1])
    Mean_Color.append(channels[0])
    return Mean_Color

def Color_Layout(image_path,n_blocks):
    """
    parameter: path of RGB image , number of blocks to divide the image  
    return:  mean color of each block(n_blocks) as a numpy 2D-array with shape (n_blocks,3)  
    """
    block_width = int(sqrt(n_blocks))
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    w,h,channels = image.shape
    x_intervals = []
    y_intervals = []
    x_step = int(w/block_width)  #width of each block
    y_step = int(h/block_width)  #hight of each block
    x_intervals.append(0)
    y_intervals.append(0)

    for i in range(1,block_width):
        x_intervals.append(x_intervals[i-1] + x_step)
        y_intervals.append(y_intervals[i-1] + y_step)
        
    x_intervals.append(w)
    y_intervals.append(h)
    blocks_mean_color = []
    b,g,r = cv2.split(image)
    
    #devide image into 36 blocks
    for i in range (0,block_width):
        for j in range(0,block_width):
            block_mean_color = []
            start_x = x_intervals[i]
            end_x =  x_intervals[i+1]  
            start_y = y_intervals[j]
            end_y = y_intervals[j+1]
            block_r = r[start_x:end_x,start_y:end_y]
            block_g = g[start_x:end_x,start_y:end_y]
            block_b = b[start_x:end_x,start_y:end_y]
            r_mean = cv2.mean(block_r)
            g_mean = cv2.mean(block_g)
            b_mean = cv2.mean(block_b)
            block_mean_color.append(r_mean[0])
            block_mean_color.append(g_mean[0])
            block_mean_color.append(b_mean[0])
            blocks_mean_color.append(block_mean_color)
    #features normalization
    blocks_mean_color = Feature_Normalization(blocks_mean_color)
    return blocks_mean_color