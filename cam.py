import cv2
# import torch
import argparse
from ultralytics import YOLO


# Integrate cmdl arguments later if needed. 
# For now, debug is assumed True
def parse_arguments():
    parser = argparse.ArgumentParser(description="Control file for PiCamera and Object Detection")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug messages")
    return parser.parse_args()

# Print debug messages
def dbg_print(msg):
    return print(f"[DEBUG]: {msg}")

# Release camera and destroy windows
def cleanup(cam):
    cam.release()
    cv2.destroyAllWindows()
    dbg_print("Released camera")
    return

# Import neural model
def load_model():
    # model = torch.hub.load("ultralytics/yolov5", "yolov5s")
    model = YOLO("./best2.pt")
    return model

# Return dictionary of objects (offsets, boundbox area), will likely only need x-axis offset for steering
def find_objects(results):
    debug = True
    res = results[0]  # get first Results object
    boxes = res.boxes
    items = []
    for box in boxes:
        x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
        # conf = box.conf.item()
        cls = int(box.cls.item())
        if cls == 0: 
            len_x = x_max - x_min
            len_y = y_max - y_min
            area = len_x * len_y
            offset_x = (x_max + x_min) / 2
            offset_y = (y_max + y_min) / 2
            items.append({
                "offset_x": offset_x,
                "offset_y": offset_y,
                "area": area
            })
            if debug:
                dbg_print(f"Offset: {offset_x}, {offset_y} of area {area}")
    return items


# find closest object and sets it as target
# TODO: look into setting target in YOLO model
def select_target(objects):
    if not objects:
        dbg_print("No objects detected. Skipping target selection...")
        return None
    closest_obj_area = max([i["area"] for i in objects])
    dbg_print(f"closest_obj_area: {closest_obj_area}")
    for index, obj in enumerate(objects):
        dbg_print(obj)
        if obj["area"] == closest_obj_area:
            dbg_print(f"Index of closest object is {index}")
            break
    return obj

def steer_motor(closest_obj, cam_w, cam_h):
    offset_x_norm = closest_obj["offset_x"] / cam_w
    # if offset_x < 0.4 or offset_x > 0.6:
    return offset_x_norm

def main():
    dbg_print("In main...")
    model = load_model()
    cam = cv2.VideoCapture(0) # 0: default camera
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
    dbg_print(f"Camera resolution: {width}, {height}")
    if not cam.isOpened():
        print("Failed to open camera")
        exit()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Couldn't receive video frame")
            break
        results = model(frame)
        objects_dict = find_objects(results)
        closest_obj = select_target(objects_dict)
        annotated_frame = results[0].plot()
        cv2.imshow("Labled Capture", annotated_frame)
        if cv2.waitKey(1) == ord('q'):
            print("Exiting...")
            break
        if closest_obj is None: continue
        dbg_print(closest_obj)

    cleanup(cam)

if __name__ == "__main__":
    args = parse_arguments()
    main()