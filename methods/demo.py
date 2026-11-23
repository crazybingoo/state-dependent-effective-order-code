"""Run small deterministic demonstrations: python -m methods.demo."""
from .projection import sine_coefficients, project_fourier, effective_order
from .hypergraph import centered_coefficients, product_law_risk, beta_variance
from .dynamics import linear_error, regional_error_bound


def main():
    coupling=sine_coefficients([(1.2,(1,0,0),0),(.7,(1,1,1),-.2)])
    for rho in (0,.85,.95):
        risks={q:project_fourier(coupling,(1,1,-1),rho,q)[1] for q in range(1,5)}
        print(f'rho={rho}: risks={risks}; effective order={effective_order(risks,.05)}')
    coeff=centered_coefficients([(0,1),(0,1,2)],0)
    for a in (1,8):
        print(f'Beta({a},{a}) toy hypergraph risks:',[product_law_risk(coeff,q,variance=beta_variance(a)) for q in (1,2,3)])
    print('Stable feedback error at t=2:',linear_error([[-1]],[.02],2))
    print('Regional metric bound at t=2:',float(regional_error_bound(2,1,.02)))


if __name__=='__main__': main()
