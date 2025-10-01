import cv2
import torch
import argparse


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
    model = torch.hub.load("ultralytics/yolov5", "yolov5s")
    return model

# Return dictionary of objects (offsets, boundbox area), will likely only need x-axis offset for steering
def find_objects(results):
    debug = True
    if debug:
        results_pd = results.pandas().xyxy[0]
        dbg_print(results_pd)

    items = []
    results = results.xyxy[0]
    for result in results:
        x_min, y_min, x_max, y_max, conf, cls = result
        if cls.int() == 0: # TODO: change to pole after training with custom dataset 
            len_x = x_max - x_min
            len_y = y_max - y_min
            area = len_x * len_y
            # Using results.xywh to get center also option, but I believe is more resource-intensive 
            # since we will need to reparse data.
            offset_x = (x_max + x_min) / 2
            offset_y = (y_max + y_min) / 2
            items.append({
                "offset_x": offset_x, 
                "offset_y": offset_y,
                "area": area
            })
            dbg_print(f"Offset: {offset_x}, {offset_y} of area {area} and type {type(offset_x)}")
    # TODO: integrate with motor control
    return items

# find closest object and sets it as target
# TODO: look into setting target in YOLO model
def select_target(objects):
    closest_obj_area = max([i["area"] for i in objects])
    dbg_print(f"closest_obj_area: {closest_obj_area}")
    for index, obj in enumerate(objects):
        dbg_print(obj)
        if obj["area"] == closest_obj_area:
            dbg_print(f"Index of closest object is {index}")
            break
    return obj


def steer_motor(closest_obj, cam_w, cam_h):
    return

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
        dbg_print(closest_obj)
        annotated_frame = results.render()[0]
        cv2.imshow("Labled Capture", annotated_frame)
        if cv2.waitKey(1) == ord('q'):
            print("Exiting...")
            break

    cleanup(cam)

if __name__ == "__main__":
    args = parse_arguments()
    main()