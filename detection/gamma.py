import numpy as np
from scipy.stats import gamma
from scipy.optimize import curve_fit

# Generate a set of sample data
np.random.seed(0)
data = gamma.rvs(a=2, scale=1, size=1000)

# Define gamma distribution's probability density function
def gamma_pdf(x, alpha, beta):
    return gamma.pdf(x, a=alpha, scale=1/beta)

# Use maximum likelihood estimation to fit the gamma distribution parameters
params, _ = curve_fit(gamma_pdf, data, np.arange(len(data)), p0=[1, 1], method='trf', maxfev=1000)

# Output the fitted parameters of the gamma distribution
alpha_fit = params[0]
beta_fit = params[1]
print("Fitted shape parameter (alpha):", alpha_fit)
print("Fitted scale parameter (beta):", beta_fit)
