import simplejson

import oauth.oauth as oauth
from restclient import GET


class OpenSocial(object):
	"""
		A client to OpenSocial Restful API's.    	
    """

	def __init__(self, oauth_consumer_key, oauth_consumer_secret, oauth_signature, server_url, token, token_secret, token_expire):
		"""
			Create an OpenSocial Client to perform OAuth-Authenticated requests.
						
			Params:
				oauth_consumer_key: platform api key
				oauth_consumer_secret: platform api secret
				oauth_signature: platform signature method
				server_url: api url
				token: communication token
				token_secret: communication secret
				token_expire: timestamp of token expiration
			
		"""
		
		# create a consumer object
		self.consumer = oauth.OAuthConsumer(oauth_consumer_key, oauth_consumer_secret)	

		self.server_url = server_url
		
		# create a token object
		self.token = oauth.OAuthToken(token, token_secret)
		self.token_expire = token_expire
			
		# get an instance of the signature object
		self.signature_method = eval('oauth.'+oauth_signature)()
		

	@staticmethod
	def get_request_token(oauth_consumer_key, oauth_consumer_secret, oauth_signature_method, oauth_request_token_url):
		
		# initialize necessary parameters for oauth 
		consumer = oauth.OAuthConsumer(oauth_consumer_key, oauth_consumer_secret)

		# get request token
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url=oauth_request_token_url)
		oauth_request.sign_request(oauth_signature_method, consumer, None)

		try:
			#response = GET(current_platform.oauth_request_token_url, headers=oauth_request.to_header())
			response = GET(oauth_request.to_url())  # using the header doesn't seems to work on partuza get an invalid consumer key error
			
			# request token
			return oauth.OAuthToken.from_string(response)
			
		except Exception, ex:
			raise OpenSocialError(200, response)
		
		
	def get_request(self, path, params=None):
		'''
			A method to execute a call to the API

			Params:
				path: the request path
				params: params to pass to the request

		'''
	
		# build the request
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.token, http_url=self.server_url+path, parameters=params)
		
		# sign the request
		oauth_request.sign_request(self.signature_method, self.consumer, self.token)

		try:
			# execute the request
			response = GET(oauth_request.to_url())
			#print oauth_request.to_url()
			
			# parse the response with simplejson
			response_json = simplejson.loads(response)
			
		except Exception:
			raise OpenSocialError(300, response)
		
		return response_json
	
		
	def get_uid(self):
		'''
			Get the user id from the remote platform
		'''
		
		# the request
		request_string = 'people/@me/@self'
		
		# send the request
		response = self.get_request(request_string)
		
		# extract uid
		try:
			return response['entry']['id']
		except KeyError:
			raise OpenSocialError(300, response)
		
	
	def get_friends(self, fields=None):
		'''
			Get a user's friends.
			
			Params:
				uid: the user's id
				fields: the fields to retrieve
				
		'''
		
		# the request
		request_string = 'people/@me/@friends'
		
		if fields is not None:
			#params = {'fields': ', '.join(fields)}
			params = {'fields': '@all'}
			
		else:
			params = None
		
		try:
			# send the request
			response = self.get_request(request_string, params)		
			return response['entry']
			
		except Exception:
			raise OpenSocialError(300, response)
			
			
	def get_users_profile(self, ids, fields=None):
		'''
			Get the profile of a list of users.
			
			Params: 
				ids: a list of user ids
				fields: the fields to retrieve
		'''
		
		profiles = []
		
		for id in ids:
			request_string = 'people/%s/@self' % id
			if fields is not None:
				#params = {'fields': ', '.join(fields)}
				params = {'fields': '@all'}

			else:
				params = None
			try:
				response = self.get_request(request_string, params)		
				profiles.append(response['entry'])
				
			except Exception, ex:
				raise OpenSocialError(300, ex.message)
			
		return profiles
				

		
		
	def get_groups(self, id):
		'''
			Get the groups of a user.
			
			WARNING THIS CODE HAS NOT BEEN TESTED!!
		'''
		
		# the request
		request_string = 'groups/%s/@self' % id
		
		# send the request			
		response = self.get_request(request_string)		
		
		return	response['entry']
				
				
	# def get_activities(self, uid, target):
	# 	
	# 	request_string = 'activities/%s/%s' % (uid, target)
	# 	#print request_string
	# 	params = None
	# 
	# 	try:
	# 		response = self.get_request(request_string, params)				
	# 		return response['entry']
	# 		
	# 	except Exception:
	# 		raise OpenSocialError
		
	

		
		
class OpenSocialError(Exception):
	'''Exception class for errors for OpenSocial.'''

	def __init__(self, code, message):
		self.code = code
		self.message = message

	def __unicode__(self):
		return repr('Error '+str(self.code) +': '+self.message)

# Error codes:
# 100: authentification
# 200: OAuth
# 300: other
#
