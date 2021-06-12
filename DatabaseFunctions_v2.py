import mysql.connector
import numpy as np
import Algorithm as alg
import videokf as vf
import cv2
import numpy as np
import os, os.path
# import Algorithm as al
#####################################################
#mean color is done :D
#accuracy of histo 
#layout
#Video
#####################################################
#Create the two folders
if not os.path.exists("histoinfo"):
        os.mkdir("histoinfo")
if not os.path.exists("layoutinfo"):
        os.mkdir("layoutinfo")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  autocommit=True,
)
mycursor = mydb.cursor()

#create database
mycursor.execute("CREATE DATABASE IF NOT EXISTS multimedia")
mycursor.execute("use multimedia;")
#create table mean
create_mean = """CREATE TABLE IF NOT EXISTS `mean` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `meanred` int,
                    `meangreen` int,
                    `meanblue` int,  
                    PRIMARY KEY (id) 
                    )
                    """
mycursor.execute(create_mean)

#create table histo
create_histo1 = """CREATE TABLE IF NOT EXISTS `histo` (
    `id` int NOT NULL AUTO_INCREMENT,
"""
create_histo2 = """"""
create_histo3 = "    "+"""PRIMARY KEY (id)) """
for i in range (1,9):
    create_histo2 = create_histo2 + "    " + "`feature" + str(i) +"`" + " float," + "\n"
create_histo = create_histo1+create_histo2+create_histo3

mycursor.execute(create_histo)

#create layout table
create_layout1 = """CREATE TABLE IF NOT EXISTS `layout` (
    `id` int NOT NULL AUTO_INCREMENT,
"""
create_layout2 = """"""
create_layout3 = "    "+"""PRIMARY KEY (id)) """
for i in range (1,13):
    create_layout2 = create_layout2 + "    " + "`feature" + str(i) +"`" + " float," + "\n"
create_layout = create_layout1+create_layout2+create_layout3
mycursor.execute(create_layout)



#create table images
create_images = """CREATE TABLE IF NOT EXISTS `images` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `path` VARCHAR(255),
                    `meancolor` int,
                    `hist` int,
                    `layout` int,
                    `pathhist` VARCHAR(255),
                    `pathlayout` VARCHAR(255),     
                    PRIMARY KEY (id),
                    FOREIGN KEY (meancolor) REFERENCES mean(id),
                    FOREIGN KEY (hist) REFERENCES histo(id),
                    FOREIGN KEY (layout) REFERENCES layout(id)
                    )
                    """
mycursor.execute(create_images)



#to insert in mean table
def insertInMean(meanlist):
  sql_statement = """INSERT INTO `mean`
                    (
                    `meanred`,
                    `meangreen`,
                    `meanblue`
                    )
                    VALUES
                    (%s,%s,%s);
                """
  mycursor.execute(sql_statement,[meanlist[0],meanlist[1],meanlist[2]])
  return mycursor.lastrowid

#to insert in histo table
def insertInHisto(histolist):
  insert_histo = """INSERT INTO `histo` ( 
                `feature1`,
                `feature2`,
                `feature3`,
                `feature4`,
                `feature5`,
                `feature6`,
                `feature7`,
                `feature8`
                )
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s);
                """
  mycursor.execute(insert_histo,histolist)
  return mycursor.lastrowid

#to insert in layout table
#R1,G1,B1,R2,G2,B2 and so on for each block
def insertInLayout(layoutlist):
    insert_histo = """INSERT INTO `layout` ( 
            `feature1`,
            `feature2`,
            `feature3`,
            `feature4`,
            `feature5`,
            `feature6`,
            `feature7`,
            `feature8`,
            `feature9`,
            `feature10`,
            `feature11`,
            `feature12`
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """
    mycursor.execute(insert_histo,layoutlist)
    return mycursor.lastrowid

#insert in image database
def insertInDB(path):
    #mean features
    mean_features = alg.Mean_Color(path)
    id_mean = insertInMean(mean_features)
    #histo features
    histo_float_features = [0] * 8
    histo_features = alg.Get_Color_Features(path,2)
    for i in range(len(histo_features)):
        histo_float_features[i] = histo_features[i].item()
    id_histo = insertInHisto(histo_float_features)
    path_histo = alg.CreateHistoInfo(path) 
    #layout features
    layout_float_features = [0] * 12
    layout_features = alg.Color_Layout(path,4)
    layout_features_list = list(np.ndarray.flatten(layout_features))
    for j in range(len(layout_features_list)):
        layout_float_features[j] = layout_features_list[j].item()
    id_layout = insertInLayout(layout_float_features)
    path_layout = alg.CreateLayoutInfo(path)
    #insert all information in image database
    insert_image = """ insert into `images` (`path`,`meancolor`,`hist`,`layout`,`pathhist`,`pathlayout`) VALUES (%s,%s,%s,%s,%s,%s); """
    mycursor.execute(insert_image,[path,id_mean,id_histo,id_layout,path_histo,path_layout])
#helper function to retrieve 
def searchMean(feature,threshold):
    select_from_mean = """ select * from mean; """
    mycursor.execute(select_from_mean) 
    all_rows = mycursor.fetchall()
    retrieved_ids = []
    for i in range(len(all_rows)):
        row = all_rows[i]
        id = row[0] 
        L = [row[1],row[2],row[3]]
        L_num = np.array(L)
        error = alg.CalcMeanError(feature,L_num)
        isCorrect = alg.Evaluation(error,threshold)
        if (isCorrect):
            retrieved_ids.append(id)
    retrieved_paths = []
    for j in retrieved_ids:
        select_from_images = """ SELECT images.path FROM images WHERE images.meancolor = {} """.format(j)
        mycursor.execute(select_from_images)
        returned_paths = mycursor.fetchall()
        retrieved_paths.extend(returned_paths)
    retrieved_paths = list(set(retrieved_paths))
    return(retrieved_paths)

def searchHisto(feature,threshold):
    select_from_histo = """ select * from histo;"""
    mycursor.execute(select_from_histo) 
    all_rows = mycursor.fetchall()
    retrieved_images = []
    for i in range(len(all_rows)):
        row = all_rows[i]
        id = row[0] 
        L = [row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        L_num = np.float32(np.array(L))
        error = alg.CalcHistoError(L_num,feature)
        isCorrect = alg.Evaluation(error,threshold)
        if (isCorrect):
            retrieved_images.append(id)
    return retrieved_images

def secondPhaseHisto(retrieved_ids):
    Paths = []
    for i in range(len(retrieved_ids)):
        select_paths = """ select path from `images` where hist = {}  """.format(retrieved_ids[i])
        mycursor.execute(select_paths) 
        path = mycursor.fetchone()
        Paths.append(alg.convertTuple(path))
    return Paths

def searchLayout(feature,threshold):
    features_list = list(np.ndarray.flatten(feature))
    select_from_histo = """select * from layout;"""
    mycursor.execute(select_from_histo) 
    all_rows = mycursor.fetchall()
    retrieved_images = []
    for i in range(len(all_rows)):
        row = all_rows[i]
        id = row[0] 
        L = [row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]]
        L_num = np.array(L)
        features_list = np.array(features_list)
        error = alg.CalcLayoutError(features_list,L_num)
        isCorrect = alg.Evaluation(error,threshold)
        if (isCorrect):
            retrieved_images.append(id)
    return retrieved_images

def secondPhaseLayout(retrieved_ids):
    Paths = []
    for i in range(len(retrieved_ids)):
        select_paths = """ select path from `images` where layout = (%s)  """
        mycursor.execute(select_paths,[retrieved_ids[i]]) 
        path = mycursor.fetchone()
        Paths.append(alg.convertTuple(path))
    return Paths

#retrieve using mean color method
def retrieve_using_mean(path):
    #first get the features of the image using mean color
    features = alg.Mean_Color(path)
    #then we search in database using mean color and get the matched images
    retrieved_paths = searchMean(features,0.15)
    return retrieved_paths

#retrieve using histogram method
def retrieve_using_histo(path):
    alg.CreateHistoInfo(path)
    # print("hello")
    #first get the features of the image using histo
    features = alg.Get_Color_Features(path,2)
    #then we search in database using histogram and get the matched images
    retrieved_ids = searchHisto(features,0.6)
    # print(retrieved_ids)
    # print("hello2")
    #second phase search
    paths = secondPhaseHisto(retrieved_ids)

    input_info = alg.GetHistoInfo(path)

    retrieved_hist_paths = []
    for i in range(len(paths)):

        image_info = alg.GetHistoInfo(paths[i])
        # if (paths[i] == 'Images/sky-orange.jpg'):
        #     print("in cond")
        #     print(image_info)
        error = alg.CalcHistoError(image_info,input_info)


        isCorrect = alg.Evaluation(error,0.65)

        if (isCorrect):
            retrieved_hist_paths.append(paths[i])

    # print(retrieved_hist_paths)
    return retrieved_hist_paths

#retrieve using layout method
def retrieve_using_layout(path):
    alg.CreateLayoutInfo(path)
    #first get the features of the image using layout
    features = alg.Color_Layout(path,4)
    #then we search in database using histogram and get the matched images
    retrieved_ids = searchLayout(features,0.6)
    #second phase search
    paths = secondPhaseLayout(retrieved_ids)
    input_info = alg.GetLayoutInfo(path)
    retrieved_layout_paths = []
    for i in range(len(paths)):
        image_info = alg.GetLayoutInfo(paths[i])
        error = alg.CalcLayoutError(image_info,input_info)
        isCorrect = alg.Evaluation(error,0.4)
        if (isCorrect):
            retrieved_layout_paths.append(paths[i])
    return retrieved_layout_paths


#############################################################################################################################
"""
first create 2 empty directories 
                            1- videos : to place video dataset 
                            2- videoKeyFrames : to place extracted keyframes of video in a folder of same video name
NOTICE: you can't have similar video names, if so a this warning statement will be displayed 
"!!! The output directory 'short3' is not empty. No iframes were extracted. !!!"
function  
--------
        input  : path of video 
        output : path of folder where extracted key frames and number of key frames in this folder
"""
#############################################################################################################################

def getVideoKeyFrame(videoPath):
    videoName = ((videoPath.split(".")[0]).split("/"))[-1]
    cwd = os.getcwd()
    cwd = cwd.replace("\\","/")
    parent_dir = cwd +"/videoKeyFrames/"
    path = parent_dir + videoName + '/'
    command = 'video-kf "{}" -m iframes -o "{}"'.format(videoPath,path)
    os.system(command)
    keyFramesCount = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
    print ("Number of key frames extracted from video '{}' : {}".format(videoName,keyFramesCount))
    return keyFramesCount,path

#############################################################################################################################

# cursor = mydb.cursor()

sql_statement = """INSERT INTO `video_table`
                    (`path`)
                    VALUES
                    (%s);
                """

sql_statement_1 = """INSERT INTO `kf_table`
                    (`path`,`mean_red`,`mean_green`,`mean_blue`,`key_frame`)
                    VALUES
                    (%s,%s,%s,%s,%s);
                """

id_statement =  """ SELECT `id` FROM `video_table` ORDER BY `id` DESC LIMIT 1
                """

def create_video_db():
    create_video_table = """CREATE TABLE  IF NOT EXISTS `video_table` (
                        `path` varchar(100),
                        `id` int NOT NULL AUTO_INCREMENT,
                        PRIMARY KEY (id) 
                        )
                        """

    mycursor.execute(create_video_table)

    create_kf_table = """CREATE TABLE  IF NOT EXISTS `kf_table` (
                            `path` varchar(100),
                            `id` int NOT NULL AUTO_INCREMENT,
                            `mean_red` float,
                            `mean_green` float,
                            `mean_blue` float,
                            `key_frame` int,
                            PRIMARY KEY (id),
                            FOREIGN KEY (key_frame) REFERENCES video_table(id)
                            )
                            """

    mycursor.execute(create_kf_table)


def insert_video_DB(path):
    mycursor.execute(sql_statement,[path])
    mycursor.execute(id_statement)
    id = mycursor.fetchone()[0]
    keyFramesCount,videoDir = getVideoKeyFrame(path)
    images = os.listdir(videoDir)
    for image in images:
        mean_rgb = alg.Mean_Color(videoDir+image)
        #db insertion key frames
        mycursor.execute(sql_statement_1,[videoDir+image,mean_rgb[0],mean_rgb[1],mean_rgb[2],id]) 
    


def populate_video_DB(videos_folder_path):
    files = os.listdir(videos_folder_path)
    for f in files:
        insert_video_DB(videos_folder_path+"/"+f)

#videos
#query image key frames
#current video key frame
def retrive_similiar_videos(path,mean_thershold,video_percentage_thershold):
    keyFramesCount,videoDir = getVideoKeyFrame(path)
    query_key_frames = os.listdir(videoDir)
    similiar_videos_pathes = []
    select_all_vidoes = """ select * from video_table; """
    mycursor.execute(select_all_vidoes) 
    all_rows = mycursor.fetchall()
    #loop on videos
    for row in all_rows:
        similiar_frames = 0
        video_path = row[0]
        # print(video_path)
        id = row[1]
        select_all_vidoe_kf = """ SELECT kf_table.mean_red,kf_table.mean_green,kf_table.mean_blue 
                                  FROM kf_table 
                                  WHERE kf_table.key_frame = {} """.format(id)
        mycursor.execute(select_all_vidoe_kf) 
        key_frames_rgb = mycursor.fetchall()
        #loop in query key frames compare with video key frame
        for image in query_key_frames:
            match = 0
            query_rgb = alg.Mean_Color(videoDir+image)
            for rgb_list in key_frames_rgb:
                error = alg.CalcErrorVideo(np.array(query_rgb),np.array(rgb_list))
                # print("              error =  "+str(error))
                isCorrect = alg.Evaluation(error,mean_thershold)
                if isCorrect:
                    # similiar_frames += 1
                    match += 1
                    # break
            if match/len(key_frames_rgb) >= 0.5 :
                similiar_frames +=1

        percentage = similiar_frames/keyFramesCount
        # print("         percentage = "+str(percentage))
        if(percentage >= video_percentage_thershold):
            similiar_videos_pathes.append(video_path)

    # print(similiar_videos_pathes)

    return similiar_videos_pathes

# print(retrive_similiar_videos("C:/Users/HRMS1/OneDrive/media/test_videos/sea1.mp4",0.09,0.8))

        
# populate_video_DB("C:/Users/HRMS1/OneDrive/media/test_videos")
#insert_video_DB("C:/Users/HRMS1/OneDrive/media/test_videos/sea1.mp4")

if __name__ == "__main__":
    # print(retrive_similiar_videos("C:/Users/HRMS1/OneDrive/med/test_videos/sunset3.mp4",0.215,0.7))
    # initilize database
    create_video_db()
    populate_video_DB("videos")
    # populate_video_DB("test_videos")
    List_of_images = ["Images/ballon-orange.jpg","Images/butterfly-red.jpg","Images/cat-purple.jpg","Images/cat.webp","Images/cat3.png","Images/gettyred.jpg","Images/hair-orange.jpg",
    "Images/leaf-orange.jpg","Images/leaf-purple.jpg","Images/Oranges.jpg","Images/purple-p.jpg"
    ,"Images/purple.jpg","Images/red-r.jpg","Images/red-rose.jpg","Images/rose-orange.jpg","Images/rose-purple.jpg","Images/sky-red.jpeg",
    "Images/tree-orange.jpg","Images/um-red.jpg","Images/1.jpg","Images/2.jpg","Images/3.jpg","Images/4.jpg","Images/5.jpg","Images/6.jpg","Images/7.jpg",
    "Images/8.jpg","Images/blue.jpg","Images/bluesky.jpeg","Images/Green-Wallpaper-35.jpg"
    ,"Images/greenplanet.jpg","Images/greenTrees.jpg","Images/red_leaves.jpg","Images/Strawberries.jpg","Images/red_apples.jpg","Images/purple_roses.jpg","Images/purpleButterflies.jpg","Images/purpleSky.jpg",
    "Images/red_tom.jpg","Images/sky-orange.jpg"]
    for i in range(len(List_of_images)):
        insertInDB(List_of_images[i])
    