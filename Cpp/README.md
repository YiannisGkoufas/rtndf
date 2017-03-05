# Cpp rtndf pipeline processing elements
    
### Pre-requisites

The Cpp PPEs require Qt5:

    cd ~/
    sudo apt-get install qt5-default git build-essential
    
To run speechdecode, pocketsphinx and sphinxbase are required. Follow the instructions here - http://cmusphinx.sourceforge.net/wiki/tutorialpocketsphinx.

### Get the repo
    
Clone the repo:

    cd ~/
    git clone git://github.com/richardstechnotes/rtndf.git
       
### Building the Cpp PPEs

All PPEs are built following the example here:

    cd ~/rtndf/Cpp/speechdecode
    qmake
    make -j8
    sudo make install
    speechdecode
    
The "-j8" part can be modified depending on how many cores are in the processor.

### Running the Cpp PPEs

PPEs can be run in window mode or console mode. Running in window mode allows runtime parameters to be configured via a GUI. If this isn't required, use the "-x" flag to change to console mode. E.g.:

    speechdecode -x
    
To run in daemon mode, there is a "-y" flag that can be used in conjunction with the -x flag. E.g.:

    speechdecode -x -y
    
### Configuring speechdecode

By default, speechdecode uses pocketsphinx's default HMM mode, language model and dictionary. It is possible to use custom version (usually just the language model and dictionary). Sentence files can be uploaded to this website - http://www.speech.cs.cmu.edu/tools/lmtool-new.html - and a customized language model is returned in a .tgz file. This should be decompressed and speechdecode configured with the location and file names via either the GUI or else by editing the ~/.config/rtn/speechdecode.conf file. By default, there will be some entries like this:

    ...
    [speechDecoder]
    dict=cmudict-en-us.dict
    hmmdir=/usr/local/share/pocketsphinx/model/en-us/en-us
    model=en-us.lm.bin
    phrasedir=/usr/local/share/pocketsphinx/model/en-us/
    ...
    
These can be changed to point to the custom files.

### imuview

This is a simple OpenGL viewer that can be used to display data being streamed from the imu PPE. By default it uses the topic imu/imudata but that can be changed by editing ~/.config/rtn/imuview.




