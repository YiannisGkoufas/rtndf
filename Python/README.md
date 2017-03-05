# Python rtndf pipeline processing elements

### Docker install

In order to avoid installing the dependencies and building manually, there are some containers available on Docker hub:

    * rtndocker/rtndf. This is the core library for Python nodes.
    * rtndocker/uvccam. This is a  dockerized version of the uvccam node.
    
These containers can also be built using the dockerbuild files in the relevant directories. The directories also include a start script (e.g. uvccamstart) that starts Docker container with the correct setup. In particular, they must be started with the "--net=host" parameter to docker run.


### Manual build and install

#### Pre-requisites

Prepare the system by installing the pre-requisites:

	sudo apt-get install git python-dev python-pip python-pygame python-pyaudio
	
Manifold (https://github.com/richardstechnotes/Manifold) is required. Build ManifoldPythonLib using the instructions here - https://github.com/richardstechnotes/Manifold/blob/master/README.md.

TensorFlow with Python support should be installed from https://www.tensorflow.org/versions/r0.10/get_started/os_setup.html

The modet PPE requires an OpenCV that supports background subtraction so a version should be used that includes the opencv_contrib code. The instructions here are quite useful - http://www.pyimagesearch.com/2015/06/22/install-opencv-3-0-and-python-2-7-on-ubuntu/. V3.0.0 seemed to work fine, V3.1.0 did not.
    
#### Get the repo
    
Clone the repo:

    cd ~/
    git clone git://github.com/richardstechnotes/rtndf.git
    
#### Build and install rtndf

    cd ~/rtndf/Python
    python setup.py build
    sudo python setup.py install
    
#### Build and install sensorlib

This library is needed is any of the sensor PPEs (sensehat, sensors and sensorview) are required.

    cd ~/rtndf/Python
    python sensorlib.py build
    sudo python sensorlib.py install
    
### OpenFace

To run facerec, it is necessary to install docker:

    sudo apt-get install docker.io
    
In order to run docker without using sudo, it's necessary to be part of the docker group. This can be done using:

    sudo usermod -aG docker <username>
    
It is necessary to log off and in again or restart the machine for this to take effect.

Then the custom containers for facerec and and the training software needs to built:

    cd ~/rtndf/Python/facerec
    ./facerecbuild
    ./facerectrainbuild

### sensehat

There are some extra pre-requisite needed to run the sensehat PPE:

    sudo pip install evdev

### Running the scripts
    
Each of the scripts has its own set of command line parameters and details can be obtained by entering:

    cd ~/rtndf/Python/xxxxx
    python xxxxx.py -h
    
This will display the command line parameters and their default settings.
        
To run uvccam for example:

    cd ~/rtndf/uvccam
    python uvccam.py -b broker_address
    
The default broker address is localhost so if the broker is running on the same machine then the -b option can be omitted. The broker_address can be either an IP address or hostname if the network can resolve the hostname to an IP address.

Note that uvccam defaults to a windowed mode and displays a preview of the video stream. If running in console mode or on a Raspberry Pi, the script should be run in non-GUI mode:

    cd ~/rtndf/Python/uvccam
    python uvccam.py -b broker_address -x

### Displaying the video and audio streams

The avview script can be used to display video and audio streams. By default, the topics it subscribes to are the default topics for uvccam and audio but these can be changed using command line options. Run:

    cd ~/rtndf/Python/avview
    python avview.py -b broker_address

### The imageproc pipeline processing element

By default, the imageproc pipeline element subscribes to topic uvccam/video and outputs processed images on topic uvccam/imageproc. The processed image is the input image after being scaled down by a factor of two and then processed by a Laplacian to perform edge detection. The typical data flow is:

    uvccam -> imageproc -> avview
    
avview should be run like this:

    cd ~/rtndf/Python/avview
    python avview.py -b broker_address -v uvccam/imageproc
    
### The modet pipeline processing element

By default, the modet pipeline script subscribes to topic uvccam/video and outputs processed images on topic uvccam/modet. The output stream contains the input images annotated with a box around any objects in motion in the stream. The typical data flow is:

    uvccam -> modet -> avview
    
avview should be run like this:

    cd ~/rtndf/Python/avview
    python avview.py -b broker_address -v uvccam/modet
    
### The recognize pipeline processing element

This is based on the Inception-v3 example here:

    https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/image/imagenet/classify_image.py
    
In receives an incoming video stream and searches each frame for a recognized object. The output stream consists of the input stream with a label indicating if anything was detected.

recognize also works with modet. An example pipeline is:

    uvccam -> modet -> recognize -> avview
    
modet will insert metadata into the stream that allows recognize to focus on objects in motion. To use this mode, add a -m flag:

    cd ~/rtndf/recognize
    python recognize.py -m -i uvccam/modet
    
This assumes the default output stream topic for modet. recognize generates a new stream on uvccam/recognize by default. This can be viewed with avview in the normal way. recognize will add labels to the modet detection boxes in this mode.

### The facerec pipeline processing element

Running this PPE is a little more complicated as it uses a docker container to isolate all of the OpenFace dependencies. The easiest way to run it is like this:

    cd ~/rtndf/Python/facerec
    ./facerecrun
    
This should start the container and the facerec.py script. However, at this point OpenFace doesn't know any faces. It has to be trained to do this. Training is done using one of the OpenFace demos described here - https://cmusatyalab.github.io/openface/demo-1-web/. This repo includes a customized version that saves the data in the correct way for facerec. To start the webserver system for training, enter:

    cd ~/rtndf/Python/facerec
    ./facerectrainrun
    
This should start up the training webserver on localhost:8000. Using a browswer, go to this URL. The web page should automatically pick up an attached webcam. Training is basically a case of typing a name in the Add Person box and pressing that button and then selecting Training On. After a reasonable number of frames have been collected, turn training off. This will save the data to the ~/.config/Manifold/facerec directory (ofpeople.ini and ofimages.ini). The same process can be done for different faces by typing a name and turning training on and the off after frames have been collected.

As with recognize, facerec can either work on the whole frame or regions. By default, with no runtime arguments, it expects the input stream to be uvccam/video and generates an annotated stream uvccam/facerec. A suitable pipeline for this is:

    uvccam -> facerec -> avview
    
In this case, facerec will try to process the largest face detected.
    
Note that the face recognition process may be quite slow. facerec continues to forward frames with the latest facerec data while waiting for an update. Therefore, the annotation may fall behind any motion of the face.

Alternatively, the metadata from modet can be used to focus on moving segments. To use modet regions, start facerec like this:

    cd ~/rtndf/Python/facerec
    ./facerecstart -m -i uvccam/modet

In this mode, one face per region in motion can be detected, allowing for the recognition of multiple faces.

