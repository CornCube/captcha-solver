import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import math


class Solve:
    def __init__(self):
        self.model = models.resnet18(pretrained=False)

        num_features = self.model.fc.in_features
        self.model.fc = torch.nn.Linear(num_features, 12)

        state_dict = torch.load('best_model.pth')
        self.model.load_state_dict(state_dict)
        self.model.eval()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.transform = transforms.Compose([
            transforms.Resize((120, 120)),  # Resize the image as the model expects
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # Normalization used during training
        ])

        self.categories = ['Bicycle', 'Bridge', 'Bus', 'Car', 'Chimney', 'Crosswalk', 'Hydrant', 'Motorcycle', 'Other', 'Palm', 
                           'Stair', 'Traffic Light']

    def inference(self, img, size, item):
        img = img.convert('RGB')  # Ensure img is in RGB format
        tile_size = img.width // size  # Calculate size of each tile
        results = []

        for row in range(size):
            for col in range(size):
                # Crop the tile from the CAPTCHA
                left = col * tile_size
                top = row * tile_size
                right = left + tile_size
                bottom = top + tile_size
                tile = img.crop((left, top, right, bottom))

                # Prepare tile for model input
                tile_tensor = self.transform(tile).unsqueeze(0).to(self.device)

                # Model prediction
                with torch.no_grad():
                    outputs = self.model(tile_tensor)
                    _, predicted = torch.max(outputs, 1)
                    predicted_class = self.categories[predicted.item()]

                # show the tile and the predicted class
                print(f"Predicted class: {predicted_class}")

                # Append the result if it matches the target item
                if predicted_class.lower() == item:
                    results.append({'tile_col': col + 1, 'tile_row': row + 1, 'class_name': predicted_class})

        print(results)
        return results
