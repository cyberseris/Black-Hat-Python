import os
from cv2 import cv2

ROOT = './pictures'
FACES = './faces'
TRAIN = './training_files'

def detect(srcdir=ROOT, tgtdir=FACES, train_dir=TRAIN):
    for fname in os.listdir(srcdir):
        if not fname.upper().endswith('.JPG'):
            continue
        fullname = os.path.join(srcdir, fname)
        newname = os.path.join(tgtdir, fname)
        img = cv2.imread(fullname)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGRGRAY)
        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')
        cascade = cv2.CascadeClassifier(training)
        reacts = cascade.detectMultiScale(gray, 1.3, 5)

        try:
            # 有偵測到臉部的話
            if reacts.any():
                print("Got a face")
                reacts[:, 2:] += reacts[:,:2]
        except AttributeError:
            print(f"No faces found in {fname}")
            continue

        for x1, y1, x2, y2 in reacts:
            # RGB: (127, 255, 0), line thickness: 2
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
        cv2.imwrite(newname, img)

if __name__ == '__main__':
    detect()