import torch

from .config import Config


def get_person_coordinates(image):
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.eval() 
    model.to(Config.USE_DEVICE)

    results = model(image)
    bbox = results.xyxy[0].detach().cpu().numpy()
    coords = []
    for preds in bbox:
        pos1 = (int(preds[0]), int(preds[1]))
        pos2 = (int(preds[2]), int(preds[3]))
        type = int(preds[5])
        if type == Config.PERSON:
            coords.append((pos1, pos2))
    return coords