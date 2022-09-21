import torch
import torchvision.models as torch_models
import torchvision.transforms as transforms
import PIL.Image as Image
import torch.nn as nn
from pathlib import Path
import os


def ResNet_classify(img_url):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    dataset_dir = os.path.join(BASE_DIR, 'car_data','car_data')
    PATH = os.path.join(BASE_DIR, 'car_classification','result_app','ResNet_model.pt')

    model = torch_models.resnet34(pretrained=True)
    num_ftrs = model.fc.in_features

    model.fc = nn.Linear(num_ftrs, 196)
    model = model.to(device)

    model.load_state_dict(torch.load(PATH))
    model.eval()

    # transforms for the input image
    loader = transforms.Compose([transforms.Resize((400, 400)),
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    image = Image.open(img_url)
    image = loader(image).float()
    image = torch.autograd.Variable(image, requires_grad=True)
    image = image.unsqueeze(0)
    image = image.cuda()
    output = model(image)

    # conf, predicted = torch.max(output.data, 1)
    # print(torch.topk(output.data, 5, 1))
    conf, predicted = torch.topk(output.data, 5, 1)

    classes, c_to_idx = find_classes(dataset_dir+"/train")
    class_rank, conf_rank = [], []
    for i in range(5):
        class_rank.append(classes[predicted[0][i].item()])
        conf_rank.append(round(conf[0][i].item(),2))
        
    return class_rank, conf_rank

def find_classes(dir):
    classes = os.listdir(dir)
    classes.sort()
    class_to_idx = {classes[i]: i for i in range(len(classes))}
    return classes, class_to_idx