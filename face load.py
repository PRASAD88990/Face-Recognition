# -*- coding: utf-8 -*-
"""Another copy of fnmain4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1abRAMyWZWMsbJ3-oTQVWIBvf4lhzll8I
"""

!pip install mtcnn

import cv2 as cv,os,tensorflow as tf,matplotlib.pyplot as plt,numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



img=cv.imread('/content/drive/MyDrive/newfn/dataset/robert_downey/1.jpg')

img=cv.cvtColor(img,cv.COLOR_BGR2RGB)
plt.imshow(img)

from mtcnn.mtcnn import MTCNN

detector=MTCNN()

results=detector.detect_faces(img)

results

x,y,w,h=results[0]['box']

img=cv.rectangle(img,(x,y),(x+w,y+h),(0,0,255),15)
plt.imshow(img)

my_face= img[y:y+h,x:x+w]
my_face=cv.resize(my_face,(160,160))
plt.imshow(my_face)

class FACELOADING:
  def __init__(self,directory):
    self.directory=directory
    self.target_size=(160,160)
    self.X=[]
    self.Y=[]
    self.detector=MTCNN()

  def extract_face(self,filename):
    img=cv.imread(filename)
    img=cv.cvtColor(img,cv.COLOR_BGR2RGB)
    x,y,w,h=self.detector.detect_faces(img)[0]['box']
    x,y=abs(x),abs(y)
    face=img[y:y+h,x:x+w]
    face_arr=cv.resize(face,self.target_size)
    return face_arr

  def load_faces(self,dir):
    FACES=[]
    for im_name in os.listdir(dir):
      try:
          path=dir+im_name
          single_face=self.extract_face(path)
          FACES.append(single_face)
      except Exception as e:
        pass
    return FACES

  def load_classes(self):
    for subdir in os.listdir(self.directory):
      path=self.directory+'/'+subdir+'/'
      FACES=self.load_faces(path)
      labels=[subdir for _ in range(len(FACES))]
      print(f"loaded successfully: {len(labels)}")
      self.X.extend(FACES)
      self.Y.extend(labels)

    return np.asarray(self.X), np.asarray(self.Y)

  def plot_images(self):
    plt.figure(figsize=(18,16))
    for num,image in enumerate(self.X):
      ncols=3
      nrows=len(self.Y)//ncols +1
      plt.subplot(nrows,ncols,num+1)
      plt.imshow(image)
      plt.axis('off')

faceloading=FACELOADING('/content/drive/MyDrive/newfn/dataset')
X,Y=faceloading.load_classes()

Y

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

# plt.figure(figsize=(16,12))
for num,image in enumerate(X):
  ncols=3
  nrows=len(Y)//ncols +1
  plt.subplot(nrows,ncols,num+1)
  plt.imshow(image)
  plt.axis('off')

faceloading.plot_images()

np.savez_compressed('faces-dataset4.npz',X,Y)

import numpy as np

# Load the data from the NPZ file
data = np.load('faces-dataset4.npz')

# Access the arrays by their names
X = data['arr_0']
Y = data['arr_1']

"""# FACE NET

"""

!pip install keras-facenet

from keras_facenet import FaceNet
embedder=FaceNet()
def get_embedding(face_pixels):
  face_pixels=face_pixels.astype('float32')
  face_pixels=np.expand_dims(face_pixels,axis=0)
  yhat=embedder.embeddings(face_pixels)
  return yhat[0]

EMBEDDED_X=[]
for img in X:
  EMBEDDED_X.append(get_embedding(img))

EMBEDDED_X=np.asarray(EMBEDDED_X)

np.savez_compressed('faces-4.npz',EMBEDDED_X,Y)

Y

"""# svm

"""

from sklearn.preprocessing import LabelEncoder

encoder=LabelEncoder()
encoder.fit(Y)
Yog=encoder.transform(Y)

from sklearn.model_selection import train_test_split

X_train,X_test,Y_train,Y_test=train_test_split(EMBEDDED_X,Yog,shuffle=True,random_state=16)

from sklearn.svm import SVC
model=SVC(kernel='linear',probability=True)
model.fit(X_train,Y_train)

ypreds_train=model.predict(X_train)
ypreds_test=model.predict(X_test)

from sklearn.metrics import accuracy_score
print(accuracy_score(Y_train,ypreds_train))

print(accuracy_score(Y_test,ypreds_test))

t_im=cv.imread('/content/drive/MyDrive/test_img/rd test3.jpg')
t_im=cv.cvtColor(t_im,cv.COLOR_BGR2RGB)
x,y,w,h=detector.detect_faces(t_im)[0]['box']

t_im=t_im[y:y+h,x:x+w]
t_im=cv.resize(t_im,(160,160))
test_im = get_embedding(t_im)

plt.imshow(t_im)
plt.show()

test_im=[test_im]
ypreds=model.predict(test_im)

ypreds



encoder.inverse_transform(ypreds)

print(encoder.classes_)

original_labels = encoder.inverse_transform(np.arange(len(encoder.classes_)))
print(original_labels)

######

def predict_face_label(image_path):
    """Predicts the face label for an image.

    Args:
        image_path: The path to the image.

    Returns:
        The predicted face label.
    """
    # Load the image
    img = cv.imread(image_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # Detect the face
    x, y, w, h = detector.detect_faces(img)[0]['box']

    # Crop and resize the face
    face_img = img[y:y + h, x:x + w]
    face_img = cv.resize(face_img, (160, 160))

    # Get the embedding
    embedding = get_embedding(face_img)

    # Make the prediction
    prediction = model.predict([embedding])

    # Get the label
    label = encoder.inverse_transform(prediction)[0]

    # Display the result
    plt.imshow(face_img)
    #plt.title(f"Predicted Label: {label}")
    plt.show()



# ... (Your existing code for FaceNet embedding and SVM training) ...

    # Set a distance threshold
    distance_threshold = 0.6  # Adjust this value as needed

    # ... (Code to extract embedding from a new face) ...

    # Calculate distances to known embeddings
    distances = [cosine_similarity(embedding.reshape(1, -1), known_embedding.reshape(1, -1))[0][0] for known_embedding in EMBEDDED_X]

    # Check if distances are above the threshold for all known faces
    if max(distances) < distance_threshold:
        predicted_class = "unknown"
    else:
        # Find the closest known embedding and its corresponding class
        # closest_index = distances.index(max(distances))
        # predicted_class = Y[closest_index]  # Assuming Y contains class labels for EMBEDDED_X
        predicted_class = label

    print("Predicted Class:", predicted_class)

    return label

image_folder = '/content/drive/MyDrive/test_img/'  # Replace with the path to your image folder

for filename in os.listdir(image_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Adjust file extensions if needed
        image_path = os.path.join(image_folder, filename)
        predict_face_label(image_path)

import pickle
#save the model
with open('svm_model4.pkl','wb') as f:
    pickle.dump(model,f)

# ... (Your existing code for FaceNet embedding and SVM training) ...

# Set a distance threshold
distance_threshold = 0.6  # Adjust this value as needed

# ... (Code to extract embedding from a new face) ...

# Calculate distances to known embeddings
distances = [cosine_similarity(test_im, known_embedding.reshape(1, -1))[0][0] for known_embedding in EMBEDDED_X]

# Check if distances are above the threshold for all known faces
if max(distances) < distance_threshold:
    predicted_class = "unknown"
else:
    # Find the closest known embedding and its corresponding class
    closest_index = distances.index(max(distances))
    predicted_class = Y[closest_index]  # Assuming Y contains class labels for EMBEDDED_X

print("Predicted Class:", predicted_class)

from sklearn.metrics.pairwise import cosine_similarity