import cv2 as op

img = op.VideoCapture()

while img.isOpened():
    ret, frame = img.read()
    
    if not ret:
        break
    
    op.imshow("Captura en Vivo", frame)

    if op.waitKey(1) & 0xFF == ord('q'):
        break

img.release()
op.destroyAllWindows()
