from sys import flags
import time
import cv2
import pyautogui as p


def AuthenticateFace():

    flag = ""
    # Local Binary Patterns Histograms
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.read('backend\\auth\\trainer\\trainer.yml')  # load trained model
    cascadePath = "backend\\auth\\haarcascade_frontalface_default.xml"
    # initializing haar cascade for object detection approach
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX  # denotes the font type


    id = 2  # number of persons you want to Recognize


    names = ['','', 'ThanhHuy']  # names, leave first empty bcz counter starts from 0


    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # cv2.CAP_DSHOW to remove warning
    cam.set(3, 640)  # set video FrameWidht
    cam.set(4, 480)  # set video FrameHeight

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    # flag = True
    
    # Thiết lập ngưỡng độ chính xác tối thiểu (50%)
    accuracy_threshold = 45

    while True:

        ret, img = cam.read()  # read the frames using the above created object

        # The function converts an input image from one color space to another
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for(x, y, w, h) in faces:

            # used to draw a rectangle on any image
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # to predict on every single image
            id, confidence = recognizer.predict(converted_image[y:y+h, x:x+w])
            
            # Chuyển đổi confidence thành độ chính xác (accuracy)
            accuracy = 100 - confidence

            # Kiểm tra nếu độ chính xác lớn hơn ngưỡng đã thiết lập
            if (accuracy > accuracy_threshold):
                id = names[id]
                accuracy_str = "  {0}%".format(round(accuracy))
                flag = 1
            else:
                id = "unknown"
                accuracy_str = "  {0}%".format(round(accuracy))
                flag = 0

            cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(accuracy_str), (x+5, y+h-5),
                        font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        if flag == 1:
            # Thêm một khoảng delay nhỏ để xác nhận khuôn mặt ổn định
            time.sleep(0.5)
            # Kiểm tra lại lần nữa để chắc chắn
            ret, img = cam.read()
            if ret:
                converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(
                    converted_image,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(int(minW), int(minH)),
                )
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    id, confidence = recognizer.predict(converted_image[y:y+h, x:x+w])
                    accuracy = 100 - confidence
                    if accuracy > accuracy_threshold:
                        break
                    else:
                        flag = 0  # Đặt lại flag nếu lần kiểm tra thứ hai thất bại
            

    # Do a bit of cleanup
    cam.release()
    cv2.destroyAllWindows()
    return flag
