import torch
from . import vampnet as vnet
from ..kernels import BaseKernel, GaussianKernel


def gramian_gauss(Y, sigma=1.):
    differences = torch.unsqueeze(Y, -2) - torch.unsqueeze(Y, -3)
    D = torch.sum(torch.pow(differences, 2), dim=-1)
    return torch.exp(-D / (2. * sigma ** 2))


def whiten(data, epsilon=1e-6, mode='clamp'):
    data_meanfree = data - data.mean(dim=0, keepdim=True)
    cov = 1 / (data.shape[0] - 1) * (data_meanfree.t() @ data_meanfree)
    cov_sqrt_inv = vnet.sym_inverse(cov, epsilon=epsilon, mode=mode, return_sqrt=True)
    return data_meanfree @ cov_sqrt_inv


def kvad_score(chi_x, y, kernel: BaseKernel = GaussianKernel(1.), epsilon=1e-6, mode='regularize'):

    with torch.no_grad():
        gramian_np = kernel.gram(y.cpu().numpy())
        gramian = torch.as_tensor(gramian_np, dtype=y.dtype, device=chi_x.device)

    chi_x_whitened = whiten(chi_x, epsilon=epsilon, mode=mode)
    x_g_x = torch.chain_matmul(chi_x_whitened.t(), gramian, chi_x_whitened)

    evals_sum = torch.trace(x_g_x)

    N = y.shape[0]
    score = 1 / (N * N) * (evals_sum + torch.sum(gramian))
    return score
