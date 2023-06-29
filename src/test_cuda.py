import torch
import math

print(torch.backends.mps.is_available())  # the MacOS is higher than 12.3+
print(torch.backends.mps.is_built())  # MPS is activated
