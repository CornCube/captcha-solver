import torch
import math


class Solve:
    def __init__(self):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5l", pretrained=True)
        self.names = self.model.names

    def inference(self, img, size, item):
        results = []
        inference_result = self.model(img)
        inference_result.show()  # comment out for prod

        for i in inference_result.xyxy[0]:
            class_name = self.names[int(i[5])]

            # images are 288 x 288
            tile_row, tile_col = 0, 0
            if item == class_name:
                if size == 3:
                    # squares are 95 x 95
                    tile_col = math.ceil(float(i[0]) / 95.0)
                    tile_row = math.ceil(float(i[1]) / 95.0)

                if size == 4:
                    # squares are 70x70
                    tile_col = math.ceil(float(i[0]) / 70.0)
                    tile_row = math.ceil(float(i[1]) / 70.0)

                results.append({"tile_col": tile_col, "tile_row": tile_row, "class_name": class_name})

        print(inference_result.xyxy[0])
        print(results)  # comment out for prod
        return results
