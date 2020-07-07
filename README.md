

# FIPU face

Face detection using [RetinaFace](https://github.com/deepinsight/insightface/tree/master/RetinaFace) and image cropping to the **25x30@300dpi**.

FIPU face detects possible errors in the image:

- picture taken to close to the camera
- head tilted to the side
- not looking towards the camera
- covered eyes, nose or mouth
- multiple or no faces in the image



If none of the errors are detected on the image, the face is cropped and resized to match the `25x30@300dpi` format.



##### The repo also provides Flask API which crops the image and returns the processed image as the response in either `base64` or `bytes` format.

###### Service supports uploading a file on the route `crop-face` with following options:

1. Uploading a file through a form (param name ***img***)
2. Uploading a file in base64 encoding using form/json (param name ***img64***)
3. Uploading a file encoded as bytes using form/json (param name ***img_bytes***)
4. Specifiying output encoding using form/json (param name ***resp_enc\***)

Response returns two types of json objects:

- When error occurs

```python
{"message": "Error description here"}
```

- When image processing completed successfully

```python
{"img": "/9/dsjdias...."} # Processed image in base64/bytes format
```





## Examples

##### Original image

![Original image](imgs/w.jpg)



##### Croped and resized image

![Croped image](imgs/new/w.jpg)



##### Original image

![Original image](imgs/l2.jpg)



##### Croped and resized image

![Croped image](imgs/new/l2.jpg)




## Testing your own image

Place your image in `imgs` folder and run `test.py` with the name of your image. New image would be placed under the same name in `imgs/new` folder.

```python
from fipu_face.fipu_face import *

def do_detect(stream_path):
    frame = cv2.imread('imgs/' + stream_path)
    try:
        frame = detect(frame)
        cv2.imwrite('imgs/new/' + stream_path, frame)
    except ImageException as e:
        print(e.message) # Error: standing to close, not looking straight etc.


if __name__ == '__main__':
    do_detect('test.jpg')

```


## Future features

[ ] - Image cropping for [official documents]([https://mup.gov.hr/UserDocsImages/BannerZona/Upute%20za%20fotografije%202013%20(2).pdf](https://mup.gov.hr/UserDocsImages/BannerZona/Upute za fotografije 2013 (2).pdf)) (in Croatia) - `mup-test` branch










