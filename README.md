### Raspberry Pi Waste Detection Installation and Usage Guide

#### Installation Steps:

1. Clone the repository on your Raspberry Pi:

   ```

   git clone https://github.com/PPeerawat/waste-detection-RaspberryPi.git

   ```

2. Install the required packages:

   ```

   sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv41-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python3-pip python3-opencv cmake libcamera-dev libkms++-dev libfmt-dev libdrm-dev libcblas-dev libhdf5-dev libhdf5-serial-dev libqtgui4 libqt4-test

   ```

3. Install necessary Python libraries:

   ```

   pip install opencv-python picamera2 onnxruntime

   ```

#### Usage:

- To run the waste detection model:

  ```

  python main.py

  ```

- To control the wireless car:

  ```

  python control.py

  ```

---

### Website Installation and Usage Guide

#### Installation Steps:

1. Clone the repository on your computer:

   ```

   git clone https://github.com/palmKumpanat/waste-detection.git

   ```

2. Navigate into the cloned folder.

3. Run the following commands in the terminal:

   ```

   npm install

   npm run serve

   ```

#### Usage:

- Access the website to control the wireless car using the keyboard.

- Use the following keys for control:

  - W = Move forward

  - A = Turn left

  - S = Move backward

  - D = Turn right
