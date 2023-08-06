from typing import Union
import torch

def silverman_rule_of_thumb_sample(target_sample: torch.Tensor) -> torch.Tensor:
    """Function used to compute $\gamma$ parameter. from a sample
    See p. 5 in https://jmlr.org/papers/volume21/19-560/19-560.pdf for the details.
    This approximation is termed the normal distribution approximation, Gaussian approximation, or Silverman's rule of thumb.

    Args:
        target_sample (torch.Tensor): Sample which parameters will be used to compute gamma's value.

    Returns:
        torch.Tensor: Value of gamma parameter computed using the Silverman's rule of thumb.
    """

    sample_count = target_sample.size(0)
    sample_stddev = target_sample.std()
    return silverman_rule_of_thumb(sample_stddev, sample_count)

def silverman_rule_of_thumb(sample_stddev: Union[torch.Tensor, float], sample_count: Union[torch.Tensor, int]) -> torch.Tensor:
    """Function used to compute $\gamma$ parameter provided with sample's stddev and count.
    See p. 5 in https://jmlr.org/papers/volume21/19-560/19-560.pdf for the details.
    This approximation is termed the normal distribution approximation, Gaussian approximation, or Silverman's rule of thumb.

    Args:
        sample_stddev (torch.Tensor): Value of standard deviation of the sample
        sample_count (int): Number of elements in the sample

    Returns:
        torch.Tensor: Value of gamma parameter computed using the Silverman's rule of thumb.
    """
    assert sample_count > 0, f"{sample_count} must be positive"
    assert sample_stddev >= 0, f"{sample_stddev} cannot be negative"
    
    sample_stddev = torch.as_tensor(sample_stddev)
    sample_count = torch.as_tensor(sample_count)
    
    assert sample_stddev.ndim == 0, f"{sample_stddev} must be a zero dimensional tensor"
    assert sample_count.ndim == 0, f"{sample_count} must be a zero dimensional tensor"

    return torch.square(1.059*sample_stddev)*torch.pow(sample_count, -0.4)

