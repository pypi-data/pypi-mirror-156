import torch
from torch.distributions import AffineTransform, ExpTransform
from torch.distributions.utils import broadcast_all

from .exponential import Exponential
from .transformed_distribution import TransformedDistribution


class Pareto(torch.distributions.Pareto, TransformedDistribution):
    def __init__(self, scale, alpha, validate_args=None):
        self.scale, self.alpha = broadcast_all(scale, alpha)
        base_dist = Exponential(self.alpha, validate_args=validate_args)
        transforms = [ExpTransform(), AffineTransform(loc=0, scale=self.scale)]
        TransformedDistribution.__init__(
            self, base_dist, transforms, validate_args=validate_args
        )
