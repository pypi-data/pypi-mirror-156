from pathlib import Path
from torch.utils.data import RandomSampler, SequentialSampler, DataLoader
from torchvision.datasets.folder import ImageFolder
from torchvision import transforms


class Transforms:
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    # normalize = transforms.Normalize(mean=[123.68, 116.779, 103.939],
    #                                  std=[58.393, 57.12, 57.375])

    train = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        normalize,
    ])

    test = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize,
    ])


class ImageNet:
    def __init__(self, root="/media/pc/data/4tb/lxw/datasets/ILSVRC"):
        self.root = Path(root)

    @property
    def trainset(self):
        return ImageFolder(self.root/"train", Transforms.train)

    @property
    def testset(self):
        return ImageFolder(self.root/"val", Transforms.test)

    def loader(self, batch_size, split="train"):
        if split == "train":
            dataset = self.trainset
            sampler = RandomSampler(dataset)
        else:
            dataset = self.testset
            sampler = SequentialSampler(dataset)
        return DataLoader(dataset,
                          batch_size=batch_size,
                          sampler=sampler)


if __name__ == "__main__":
    root = "/media/pc/data/4tb/lxw/datasets/ILSVRC"
    dataset = ImageNet(root)
    trainset = dataset.loader(batch_size=30, split="train")
    valset = dataset.loader(batch_size=50, split="val")
