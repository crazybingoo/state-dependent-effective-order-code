import unittest
import numpy as np
from methods.projection import *
from methods.hypergraph import *
from methods.dynamics import *
from methods.estimation import *


class Principles(unittest.TestCase):
    def test_exact_risks(self):
        c=sine_coefficients([(1.2,(1,0,0),0),(.7,(1,1,1),-.2)])
        for rho in (0,.2,.85,.95,.995):
            self.assertAlmostEqual(project_fourier(c,(1,1,-1),rho,2)[1],.245*(1-rho*rho),places=11)
            self.assertAlmostEqual(project_fourier(c,(1,1,-1),rho,3)[1],.245*(1-rho*rho)/(1+rho*rho),places=11)
        c=sine_coefficients([(1.2,(1,0,0),0),(.7,(2,1,-3),-.2)])
        self.assertAlmostEqual(project_fourier(c,(3,2,-6),.95,3)[1],.245)

    def test_phase_cross_terms_and_quadrature(self):
        # Independent uniform-grid integration checks complex phase and interference.
        u=np.arange(128)*2*np.pi/128
        X=np.stack(np.meshgrid(u,u,indexing='ij'),axis=-1).reshape(-1,2)
        c=sine_coefficients([(.8,(1,1),.3),(.4,(2,2),-.7),(.3,(1,0),.1)])
        a,risk=project_fourier(c,(1,1),.6,2,phi=.4)
        residual=evaluate(c,X)-evaluate(a,X)
        numerical=np.mean(np.abs(residual)**2*poisson_density(X,(1,1),.6,.4))
        self.assertAlmostEqual(numerical,risk,places=10)
        for k in a:
            self.assertLess(abs(np.mean(np.exp(-1j*(X@k))*residual*poisson_density(X,(1,1),.6,.4))),1e-10)

    def test_anchor_edge_cases(self):
        self.assertEqual(anchors((0,2,3),(0,1,1),2),{(0,0,1),(0,-1,0)})
        self.assertEqual(anchors((1,2,3),(0,1,1),1),set())
        self.assertEqual(anchors((0,0,0),(1,0,0),2),{(0,0,0)})
        self.assertAlmostEqual(bridge_residual(1,3,[2],.7),0)

    def test_product_projection(self):
        edges=[(0,1),(0,1,2),(0,1,3)]
        c=centered_coefficients(edges,0)
        self.assertEqual(c[(1,)],3)
        # Tensor Gauss-Legendre quadrature integrates this polynomial exactly.
        from itertools import product
        z,w=np.polynomial.legendre.leggauss(4);z=(z+1)/2;w=w/2
        indexes=list(product(range(4),repeat=4));X=np.array([[z[j] for j in row] for row in indexes]);W=np.array([np.prod([w[j] for j in row]) for row in indexes])
        for q in (1,2,3):
            residual=evaluate_projection(c,X,0,4)-evaluate_projection(c,X,0,q)
            self.assertAlmostEqual(W@(residual**2),product_law_risk(c,q),places=12)

    def test_feedback_sign_and_bound(self):
        times=np.linspace(0,3,31)
        expected=-.1*(1-np.exp(-times))
        response=variational_error(lambda t:np.array([[-1.]]),lambda t:np.array([.1]),times,1)[:,0]
        np.testing.assert_allclose(response,expected,atol=2e-10)
        self.assertAlmostEqual(linear_error([[-1]],[.1],3)[0],expected[-1])
        np.testing.assert_allclose(regional_error_bound(times,1,.1),-expected,atol=1e-14)
        self.assertAlmostEqual(metric_contraction_rate([[-1]],[[2]]),1)
        self.assertEqual(phase_chord_error(np.array([0,1,2]),np.array([3,4,5])),0)

    def test_weighted_projection(self):
        X=np.arange(20).reshape(10,2)/10; y=1+X@np.array([2.,-1.])
        intercept,coef,loss=weighted_projection(X,y,np.arange(1,11))
        np.testing.assert_allclose(intercept+X@coef,y,atol=1e-12)
        self.assertLess(loss,1e-24)
        lo,hi=empirical_bernstein(np.repeat(.2,100),1,.05)
        self.assertLessEqual(lo,.2);self.assertGreaterEqual(hi,.2)

    def test_cubic_bounds(self):
        from scipy.integrate import quad
        for t in (.01,1,5):
            p,r=cubic_decay_bounds(t,.7,.2)
            self.assertAlmostEqual(p,quad(lambda s:.2*np.exp(-.7*(t-s))*np.exp(-2.1*s),0,t)[0])
            self.assertAlmostEqual(r,quad(lambda s:.04*np.exp(-4.2*s),0,t)[0]/t)
        p,r=cubic_decay_bounds(0,.7,.2)
        self.assertEqual(p,0);self.assertAlmostEqual(r,.04)


if __name__=='__main__':unittest.main()
