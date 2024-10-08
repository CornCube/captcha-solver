# captcha-solver

A project that breaks Google reCAPTCHA v2

### HOW TO USE

make sure that the latest chromedriver is installed, then run main() to test.

the implementation inside `/custom` uses a model that I fine-tuned off of the Resnet-18 architecture, done for my Deep Learning final project. The run details are the same. I've omitted the training data to conserve space, the dataset can be located here (https://www.kaggle.com/datasets/sanjeetsinghnaik/google-recaptcha/data).

### Details

there are 4 main types of recaptcha that may be encountered. I have labeled them as types 1-4 in my code.

- type 1 = 16 grouped squares, need to select each square that has a part of the bounding box in it
- type 2 = 16 grouped squares, same as type 1, but may also have to press 'skip' if nothing is detected.
- type 3 = 9 individual images, simply need to select the right ones and hit verify
- type 4 = 9 individual images, but need to keep solving as long as new images that meet the requirement are detected

to solve, the program follows the following steps:

1. initialize chrome and pretrained yolov5 model on the COCO dataset (or `best_model.pth` if using the custom model)
2. pull the instructions from the header and classifies the challenge by object and type
3. takes a screenshot of the entire image grid and runs yolov5 on it
4. presses on tiles that contain the corresponding object
5. takes another screenshot if the challenge calls for multiple runs, or hits verify if not.

### Limitations

- model is not always accurate, leading to incorrect tile presses
- captchas get progressively harder to solve as failed attempts accumulate on the ip
- the COCO dataset doesn't contain a couple of objects that captchas may ask about - mountains, hills, and crosswalks for example
