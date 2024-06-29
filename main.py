import io
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
#import library to send data
import json
from flask import Flask, Response, request, send_file
from flask_cors import CORS, cross_origin
from read_mq import MQ
from publish import MQTT
from io import BytesIO

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

frame_feed_orig = None
frame_feed_pred = ''

#predict in model send to http url, send other data to mqtt broker
def generate_frames(route):
    global frame_feed_orig
    
    if route == 101:
        return frame_feed_orig
    
    while True:
        original_frame = picam2.capture_array()
        
        original_frame_rgb = cv2.cvtColor(original_frame, cv2.COLOR_RGBA2RGB)
        predicted_frame_rgb = original_frame_rgb
        class_predicted = []
        
        #send original frame
        if route == 0:
            original_frame_encoded = cv2.imencode('.jpg', original_frame_rgb)[1].tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + original_frame_encoded + b'\r\n')
            continue
        
        # Predictions
        results = list(onnx_model(original_frame_rgb, conf=0.4, stream=True, imgsz=[320, 320]))
        
        for result in results:
            #draw boxes
            for box in result.boxes:
                #add class in class_predicted array
                #if result.names[int(box.cls[0])] not in class_predicted:
                class_predicted.append(result.names[int(box.cls[0])])
                
                #draw boxes
                cv2.rectangle(predicted_frame_rgb, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                              (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (0, 255, 0), 2)
                #put texts
                cv2.putText(predicted_frame_rgb, f"{result.names[int(box.cls[0])]}",
                            (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
        
        # Encode frames to JPEG
        original_frame_encoded = cv2.imencode('.jpg', results[0].orig_img)[1].tobytes()
        predicted_frame_encoded = cv2.imencode('.jpg', predicted_frame_rgb)[1].tobytes()
        
        #save frame
        frame_feed_pred = io.BytesIO(predicted_frame_encoded)
                                            #json data
        #--------------------------------------------------------------------------------------------
        #array = [b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + original_frame_encoded  + b'\r\n',
                 #b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + predicted_frame_encoded + b'\r\n']
        #data = {
            #"orig_img": array[0],
            #"pred_img": array[1]
        #}
        #json_data = json.dumps(str(data)).encode('utf-8')
        #--------------------------------------------------------------------------------------------
        
                                            #mq_sensor
        #--------------------------------------------------------------------------------------------
        mq_data = mq.read_mq()
        #--------------------------------------------------------------------------------------------
        
                                            #send to mqtt
        #--------------------------------------------------------------------------------------------
        result_send_mqtt = mqtt.publish(class_predicted, mq_data)
        #--------------------------------------------------------------------------------------------
        
    
        # Yield frames
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + predicted_frame_encoded + b'\r\n'

@app.route('/video_feed_original')
# @cross_origin(origin='*', headers=['Content-Type'])
def video_feed_original():
    response = Response(generate_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')
    return response

@app.route('/video_feed_predicted')
# @cross_origin(origin='*', headers=['Content-Type'])
# @cross_origin()
def video_feed_predicted():
    # return Response(generate_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')
    resp = Response(generate_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/frame_feed_original')
# @cross_origin(origin='*', headers=['Content-Type'])
def frame_feed_original():
    global frame_feed_orig
    #result = generate_frames(101)
    
    if frame_feed_orig is None:
        return "No frame data available."
    
    return send_file(frame_feed_orig, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')

@app.route('/frame_feed_predicted')
# @cross_origin(origin='*', headers=['Content-Type'])
def frame_feed_predicted():
    global frame_feed_pred
    #result = generate_frames(101)
    
    if frame_feed_pred is None:
        return "No frame data available."
    
    return send_file(frame_feed_pred, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')


if __name__ == '__main__':

    #setup picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (320, 240)}, controls={"FrameRate": 30}))
    picam2.start()
    
    #download model and convert to onnx format
    #model = YOLO('best.pt')
    #result = model.export(format='onnx')
    onnx_model = YOLO('best.onnx', task='detect')
    
    #setup mqtt
    mqtt = MQTT()
    
    #setup mq
    mq = MQ()
    
    app.run(host='0.0.0.0', port=5000, threaded=True)