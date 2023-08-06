from typing import Union
import torch

cw_normality_scale_factor = 0.28209479177
cw_scale_factor = 0.56418958354

def cw_normality_no_scale(sample: torch.Tensor, gamma: Union[torch.Tensor, float]) -> torch.Tensor:
    """The function measures a Cramer-Wold distance of a sample from the standard multivariate normal distribution. 
    The implementation follows the formula from Theorem 3 in: https://jmlr.org/papers/volume21/19-560/19-560.pdf
    This function skips scaling of the computed distance by $ \frac{1}{2*sqrt()\pi) }$. 
    It is effectively the formula from page 14 which is the formula used by original CWAE implementation.

    Args:
        sample (torch.Tensor): sample to evaluate. Sample must be a 2D tensor N x D.
        gamma (Union[torch.Tensor, float]): value of gamma coefficient. 

    Returns:
        torch.Tensor: One dimensional nonnegative tensor storing a distance of the sample from standard multidimensional normal distribution.
    """
    assert sample.ndim == 2, f"{sample} must be a two dimensional tensor"
    assert gamma.ndim == 0, f"{gamma} must be a zero dimensional tensor"

    N, D = sample.size()
    gamma = torch.as_tensor(gamma)

    K = 1.0/(2.0*D-3.0)

    A1 = torch.pdist(sample)**2
    A = 2.0 * torch.rsqrt(gamma + K*A1).sum() / N**2 + torch.rsqrt(gamma) / N

    B1 = torch.linalg.norm(sample, 2, axis=1)**2 
    B = torch.rsqrt(gamma + 0.5 + K*B1).mean()

    result = A + torch.rsqrt(1+gamma) - 2.0 * B

    return result

def cw_normality(sample: torch.Tensor, gamma: torch.Tensor) -> torch.Tensor:
    """The function measures a Cramer-Wold distance of a sample from the standard multivariate normal distribution. 
    The implementation follows the formula from Theorem 3 in: https://jmlr.org/papers/volume21/19-560/19-560.pdf

    Args:
        sample (torch.Tensor): sample to evaluate. Sample must be a 2D tensor N x D.
        gamma (torch.Tensor): value of gamma coefficient. 

    Returns:
        torch.Tensor: One dimensional nonnegative tensor storing a distance of the sample from standard multidimensional normal distribution.
    """
    
    result = cw_normality_no_scale(sample, gamma)   

    return result * cw_normality_scale_factor

def cw(first_sample: torch.Tensor, second_sample: torch.Tensor, gamma: Union[torch.Tensor, float]) -> torch.Tensor:
    """The function measures a Cramer-Wold distance between two samples with the same count. 
    The implementation follows the formula from Theorem 1 in: https://jmlr.org/papers/volume21/19-560/19-560.pdf

    Args:
        first_sample (torch.Tensor): first sample to evaluate. Sample must be a 2D tensor N x D.
        second_sample (torch.Tensor): second sample to evaluate. Sample must be a 2D tensor N x D.
        gamma (Union[torch.Tensor, float]): value of gamma coefficient. 

    Returns:
        torch.Tensor:  One dimensional nonnegative tensor storing a distance between the samples.
    """
    assert first_sample.ndim == 2, 'first_sample must be 2D tenor'
    assert second_sample.ndim == 2, 'second_sample must be 2D tenor'
    assert first_sample.size() == second_sample.size(), 'size of the first_sample must equal to the size of the second_sample'

    N, D = first_sample.size()

    gamma = torch.as_tensor(gamma)
    T = torch.rsqrt(gamma)*cw_scale_factor/(2.0*N*N)

    A0 = torch.pdist(first_sample)**2
    A = 2*__phi_sampling_modified(A0/gamma, D).sum() + N

    B0 = torch.pdist(second_sample)**2
    B = 2*__phi_sampling_modified(B0/gamma, D).sum() + N

    C0 = torch.cdist(first_sample, second_sample)**2
    C = __phi_sampling_modified(C0/gamma, D).sum()

    return T*(A + B - 2*C)

def __phi_sampling_modified(s: torch.Tensor, D: int):
    """Modified asymptotic formula based on equation (4) from https://jmlr.org/papers/volume21/19-560/19-560.pdf.
    It differs from the formula in the paper because it dropped multiplication by 4 because 4 always comes in the denominator in this scenario.

    Args:
        s (torch.Tensor): argument of $\phi_D$
        D (int): dimension

    Returns:
        _type_: Value of $\phi_D$ function computed with asymptotic formula. 
    """

    return torch.rsqrt(1.0 + s/(2.0*D-3))

