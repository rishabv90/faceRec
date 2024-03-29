
'''

Reference links:
#uickstart:
https://docs.microsoft.com/en-us/azure/cognitive-services/face/quickstarts/python-sdk
Face operations:
https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-face/azure.cognitiveservices.vision.face.operations?view=azure-python

'''


import asyncio, io, glob, os, sys, time, uuid, requests, cv2
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

#cascPath = "weird_xml_file.xml"
#faceCascade = cv2.CascadeClassifier(cascPath)

global KEY
# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
#KEY = os.environ['FACE_SUBSCRIPTION_KEY']
KEY = '12f952f3b226421aa2019ab14740b123'

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
global ENDPOINT
ENDPOINT = "https://testface19025.cognitiveservices.azure.com/face/v1.0/detect?returnFaceId=true&returnFaceLandmarks=true&returnFaceAttributes=[age,gender,glasses]&recognitionModel=recognition_02&returnRecognitionModel=false&detectionModel=detection_01"

global face_client
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

global PERSON_GROUP_ID
PERSON_GROUP_ID = 'test'


def getRectangle(faceDictionary):
    #function used to get rectangle dimensions from detected face object
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    bottom = left + rect.height
    right = top + rect.width
    return ((left, top), (bottom, right))

def getText(faceDictionary):
    #function used to get text location from detected face object
    rect = faceDictionary.face_rectangle
    left = rect.left - (int(rect.width/2))
    top = rect.top - 20
    return (left,top)


def connect():

    
    faces = [] #stores face objects
    i = 0
    video_capture = cv2.VideoCapture(0)
    while True:
        
        # Capture frame-by-frame
        ret, frame = video_capture.read() #takes a picture of current frame

        frame = cv2.resize(frame,(960,720),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = [] #stores IdentifyResult objects
        

        
        #take picture ever time i = 25 (only used this cuz my computer cant process it fast enough)
        if i == 50:
            i = 0
            #change the code below to match the file directory of current visual student project
            name = '/Users/Brian/source/repos/Face group/Face group/frame.jpg'

            cv2.imwrite(name, frame)
            group_photo = 'frame.jpg'
            
            #gets folder of current project directioary
            IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)))

            # Get test image
            test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, group_photo))
            image = open(test_image_array[0], 'r+b')

            # Detect faces
            face_ids = []
            faces = face_client.face.detect_with_stream(image, return_face_id=True, return_face_landmarks=True, return_face_attributes=['age', 'gender', 'headPose', 'smile', 'facialHair', 'glasses', 'emotion'], recognition_model='recognition_02', return_recognition_model=False, detection_model='detection_01', custom_headers=None, raw=False, callback=None)
            
            for face in faces:
                #add face ids to face_ids list for .indentify() method
                face_ids.append(face.face_id)

            # Identify faces
            # Check to make sure face was detected
            if face_ids != []:
                results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
                
            names = [] #stores names of person from .indentify ()
            confidence =[] #stores confidence of person from .indentify()
            if not results:
                print('No person identified in the person group'.format(os.path.basename(image.name)))
            for person in results:
                if person.candidates != []:
                   
                    
                    #.get() used to return person object in persongroup
                    temp = face_client.person_group_person.get(PERSON_GROUP_ID, person.candidates[0].person_id, custom_headers=None, raw=False)

                    names.append(temp.name)
                    confidence.append(person.candidates[0].confidence)
                    print('Person: {}    Confidence: {}.'.format(temp.name, person.candidates[0].confidence)) # Get topmost confidence score
                else:
                    
                    results.remove(person)
                   
        
            faces = faces[:len(results)] #trim faces to match length of results

        count = 0 #used as incrementor for name, confidence lists
        for face in faces:
            
            #draws rectangle on image
            rectangle = getRectangle(face)
            v1 = rectangle[0]
            v2 = rectangle[1]
            
            #cv2.rectangle(frame, (x, y), (x+w, y+h), (150, 140, 150), 2)

            #draws string on image
            font = cv2.FONT_HERSHEY_PLAIN
            #cv2.putText(frame,'OpenCV Tuts!',(x,y), font, 1,(200,255,155), 1, cv2.LINE_AA)
            face_attributes = face.face_attributes
            if confidence != []:
                conf = int(confidence[count] * 100)
                if conf >= 95:
                    color = (0,150,0)
                else:
                    color = (0,0,150)
                text =  names[count] + ' Confidence: '+ str(conf) + '% ' + str(face_attributes.age) + ' '  + face_attributes.glasses
                cv2.rectangle(frame,v1,v2,color, 1)
                cv2.putText(frame,text,getText(face),font, 1.5,color, 1, cv2.LINE_AA)
                count += 1 
        
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        i+=1
    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()
    return



connect()


