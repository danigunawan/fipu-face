from fipu_face.fipu_face import *


###############
#   TESTING   #
###############

def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path)
    try:
        frame = detect(frame)
        cv2.imwrite('imgs/new/' + stream_path.replace('.jpg', '.jpg'), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        # success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        # print(len(buffer.tobytes())/(1024*1024), " MB")
    except ImageException as e:
        print(e.message)


if __name__ == '__main__':
    # """
    for i in ['1.jpg', 'a.jpg', 'j.jpg', 'm.jpg', 'w.jpg', 's1.jpg', 's2.jpg', 'l1.jpg', 'l2.jpg', 'l3.jpg']:
        do_detect(i)
    # """
    # do_detect('n.jpg')

"""
img = cv2.imread('imgs/w.jpg')

# success, buffer = cv2.imencode('.png', img) # , [cv2.IMWRITE_JPEG_QUALITY, 75])
success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
s = base64.b64encode(buffer).decode('utf-8')
cv2.imwrite('imgs/new/test.png', img) #,  [cv2.IMWRITE_JPEG_QUALITY, 75])

img, m = detect(img)

with open('index.html', 'w') as f:
    f.write('<html><body><img src="data:image/jpg;base64,%s" style="width: 200px;"><body><html>' % s)

len(buffer.tobytes())/(1024*1024)
"""
