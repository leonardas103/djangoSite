from sklearn.base import BaseEstimator, TransformerMixin
import cosfire as c
import math as m
import numpy as np
import time

class COSFIRE(BaseEstimator, TransformerMixin):

	def __init__(self, strategy):
		self.strategy = strategy

	def fit(self, *pargs, **kwargs):
		self.strategy.fit(*pargs, **kwargs)
		return self;

	def transform(self, subject):
		return self.strategy.transform(subject)

	def get_params(self, deep=True):
		return self.strategy.get_params(deep)

	def set_params(self, **params):
		return self.strategy.set_params(**params)


class CircleStrategy(BaseEstimator, TransformerMixin):

	def __init__(self, filt, filterArgs, rhoList, prototype, center, sigma0=0, alpha=0, rotationInvariance=[0], scaleInvariance=[1], T1=0, T2=0.2):
		self.filterArgs = self.convertFilterArgs(filterArgs) if type(filterArgs) is dict else filterArgs
		self.filt = filt
		self.T1 = T1
		self.T2 = T2
		self.rhoList = rhoList
		self.prototype = prototype
		self.center = center
		self.sigma0 = sigma0/6
		self.alpha = alpha/6
		self.rotationInvariance = rotationInvariance
		self.scaleInvariance = scaleInvariance
		self.timings = []

	def fit(self):
		self.protoStack = c.ImageStack().push(self.prototype).applyFilter(self.filt, self.filterArgs)
		self.protoStack.treshold = self.T2
		self.tuples = self.findTuples()

	def transform(self, subject):
		t0 = time.time()                                         # Time point

		# Precompute all blurred filter responses
		self.responses = self.computeResponses(subject)

		# Store timing
		self.timings.append( ("Precomputing {} filtered+blurred responses".format(len(self.responses)), time.time()-t0) )

		t1 = time.time()                                         # Time point

		variations = []
		for psi in self.rotationInvariance:
			for upsilon in self.scaleInvariance:
				variations.append( (psi, upsilon) )

		# Store the maximum of all the orientations
		result = np.amax([self.shiftCombine(tupl) for tupl in variations], axis=0)

		# Store timing
		self.timings.append( ("Shifting and combining all responses", time.time()-t1) )

		return result

	def shiftCombine( self, variation ):
		psi = variation[0]
		upsilon = variation[1]
		t0 = time.time()                                 # Time point

		# Adjust base tuples
		curTuples = [(rho*upsilon, phi+psi, *params) for (rho, phi, *params) in self.tuples]

		# Collect shifted filter responses
		curResponses = []
		for tupl in curTuples:
			rho = tupl[0]
			phi = tupl[1]
			args = tupl[2:]
			dx = int(round(rho*np.cos(phi)))
			dy = int(round(-rho*np.sin(phi)))

			# Apply shift
			response = c.shiftImage(self.responses[(rho,)+args], -dx, -dy).clip(min=0)

			# Add to set of responses
			#curResponses.append( (response, rho) )    # For weighted geometric mean
			curResponses.append( response )

		# Combine shifted filter responses
		# curResult = self.weightedGeometricMean(curResponses)
		result = np.multiply.reduce(curResponses)
		result = result**(1/len(curResponses))

		# Store timing
		self.timings.append( ("\tShifting and combining the responses for psi={:4.2f} and upsilon={}".format(psi, upsilon), time.time()-t0) )

		return result

	def findTuples(self):
		# Init some variables
		(cx, cy) = self.center
		tuples = []

		t0 = time.time()                                     # Time point
		# Go over every rho (radius of circles)
		for rho in self.rhoList:
			t1 = time.time()                                 # Time point
			if rho == 0:
				# Circle with no radius, so just the center point
				val = self.protoStack.valueAtPoint(cx, cy)
				if (val[0] > self.T1):
					tuples.append((rho, 0)+val[1])
			elif rho > 0:
				# Compute points on the circle of radius rho with center point (cx,cy)
				coords = [ ( cx+int(round(rho*np.cos(phi))) , cy+int(round(rho*np.sin(phi))) )
							for phi in
								[i/360*2*np.pi for i in range(360)]
						 ]
				# Make list unique
				coords = [coords[i] for i in sorted(set([coords.index(c) for c in coords]))]

				# Retrieve values on the circle points in the given filtered prototype
				vals = [self.protoStack.valueAtPoint(*coord)+coord for coord in coords]

				# Find peaks in circle
				maxima = c.circularPeaks([x[0] for x in vals])
				for i in maxima:
					dx = vals[i][2] - cx
					dy = vals[i][3] - cy
					phi = (np.arctan2(dy, dx))%(2*np.pi)
					tuples.append( (rho,phi)+vals[i][1] )

			# Store timing
			self.timings.append( ("\tFinding tuples for rho={}".format(rho), time.time()-t1) )

		# Store timing
		self.timings.append( ("Finding all {} tuples for {} different values of rho".format(len(tuples), len(self.rhoList)), time.time()-t0) )

		return tuples

	def computeResponses(self, subject):
		# Response steps:
		#  - apply the filter
		#  - trim off values < T1
		#  - apply blurring

		t0 = time.time()                                 # Time point

		uniqueArgs = c.unique([ tuple(args) for (rho,phi,*args) in self.tuples])
		filteredResponses = {}
		for args in uniqueArgs:
			# First apply the chosen filter
			filteredResponse = self.filt(*args).transform(subject)
			# ReLU
			filteredResponse = np.where(filteredResponse < self.T1, 0, filteredResponse)
			# Save response
			filteredResponses[args] = filteredResponse

		# Store timing
		self.timings.append( ("\tApplying {} filter(s)".format(len(filteredResponses)), time.time()-t0) )
		t1 = time.time()                                 # Time point

		responses = {}
		for tupl in self.tuples:
			rho = tupl[0]
			args = tupl[2:]

			if self.alpha != 0:
				for upsilon in self.scaleInvariance:
					localRho = rho * upsilon
					if (localRho,)+args not in responses:
						localSigma = self.sigma0 + localRho*self.alpha
						blurredResponse = c.GaussianFilter(localSigma, sz=int(round(localSigma*6))+(1-int(round(localSigma*6))%2)).transform(filteredResponses[args])
						responses[(localRho,)+args] = blurredResponse
			else:
				blurredResponse = c.GaussianFilter(self.sigma0).transform(filteredResponses[args])
				for upsilon in self.scaleInvariance:
					localRho = rho * upsilon
					responses[(localRho,)+args] = blurredResponse

		# Store timing
		self.timings.append( ("\tComputing {} blurred filter response(s)".format(len(responses)), time.time()-t1) )

		return responses

	# Function to compute the weighted geometric mean
	# of a list of responses
	def weightedGeometricMean(self, images):
	    maxWeight = 2*(np.amax([img[1] for img in images])/3)**2
	    totalWeight = 0
	    result = np.ones(images[0][0].shape)
	    for img in images:
	        weight = np.exp(-(img[1]**2)/maxWeight)
	        totalWeight += weight
	        result = np.multiply(result, img[0]**weight)
	    return result**(1/totalWeight)

	def convertFilterArgs(self, dict):
		if len(dict) == 2:
			return (dict['sigma'], dict['onoff'])
		if len(dict) == 5:
			return (dict['sigma'], dict['theta'], dict['lambd'], dict['gamma'], dict['psi'])
		return dict.items()
