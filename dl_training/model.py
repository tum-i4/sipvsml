from torch import nn


class DeepNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(300, 300),
            nn.ReLU(),
            nn.Linear(300, 3)
        )

    def forward(self, features):
        out = self.model(features)  # batch_size, 3
        return out
