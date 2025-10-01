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

# Return object postition, will likely only need x for steering
def read_offset(results):
    item_areas = []
    results_pd = results.pandas().xyxy[0]
    dbg_print(results_pd)
    for i in range(len(results_pd)):
        if results_pd["name"][i] == "person": # TODO: change to pole after training with custom dataset
            len_x = results_pd["xmax"][i] - results_pd["xmin"][i]
            len_y = results_pd["ymax"][i] - results_pd["ymin"][i]
            area = (len_x * len_y)#.item()
            offset_x = (results_pd["xmax"][i] + results_pd["xmin"][i]) / 2
            offset_y = (results_pd["ymax"][i] + results_pd["ymin"][i]) / 2
            item_areas.append({"offset": offset_x, "area": area})
            dbg_print(f"Offset: {offset_x}, {offset_y} of area {area} and type {type(offset_x)}")
    # TODO: integrate with motor control
    closest_item = max([i["area"] for i in item_areas])
    for index, item in enumerate(item_areas):
        dbg_print(item)
        if item["area"] == closest_item:
            dbg_print(f"Index of closest object is {index}")
    return

def main(debug):
    print(debug)
    print_frame_results = True
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
        # cv2.imshow("Video Capture", frame)
        results = model(frame)
        if print_frame_results:
            print("PRINTING FRAME RESULTS ********")
            print(type(results))
            print(results)
            print(results.xyxyn[0]) # bounding box 0-1000?
            print(results.xywhn[0])
            read_offset(results)
            print("PRINTING FRAME RESULTS ********")
            # print_frame_results = False
            break
        annotated_frame = results.render()[0]
        cv2.imshow("Labled Capture", annotated_frame)
        if cv2.waitKey(1) == ord('q'):
            print("Exiting...")
            break

    cleanup(cam)

if __name__ == "__main__":
    args = parse_arguments()
    main(args.debug)