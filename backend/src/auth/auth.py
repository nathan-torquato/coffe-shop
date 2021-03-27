import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

AUTH0_DOMAIN = 'torquato.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
	def __init__(self, error, status_code):
		self.error = error
		self.status_code = status_code


## Auth Header

def get_token_auth_header():
	auth_header = request.headers.get('Authorization', None)
	
	if not auth_header:
		raise AuthError({
			'code': 'authorization_header_missing',
			'description': 'Authorisation header is required'
		}, 401)
	
	auth_header_info = auth_header.split()
	if len(auth_header_info) != 2:
		raise AuthError({
			'code': 'authorization_header_invalid',
			'description': 'Authorisation header must be bearer token'
		}, 401)
	
	[bearer, token] = auth_header_info
	if bearer.lower() != 'bearer':
		raise AuthError({
			'code': 'authorization_header_invalid',
			'description': 'Authorisation header must start with `Bearer`'
		}, 401)
	
	return token

def check_permissions(permission, payload):
	if 'permissions' not in payload:
		raise AuthError({
			'code': 'invalid_claims',
			'description': 'JWT does not include `permissions`.'
		}, 400)
	
	if permission not in payload['permissions']:
		raise AuthError({
			'code': 'unauthorised',
			'description': 'User is not allowed to perform this action.'
		}, 403)
	
	return True

def verify_decode_jwt(token):
	jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
	jwks = json.loads(jsonurl.read())
	unverified_header = jwt.get_unverified_header(token)
	
	if 'kid' not in unverified_header:
		raise AuthError({
			'code': 'invalid_header',
			'description': 'Malformed authorisation'
		}, 401)
	
	rsa_key = {}
	for key in jwks['keys']:
		if key['kid'] == unverified_header['kid']:
			rsa_key = {
				'kty': key['kty'],
				'kid': key['kid'],
				'use': key['use'],
				'n': key['n'],
				'e': key['e'],
			}
	
	if not rsa_key['kid']:
		raise AuthError({
			'code': 'invalid_header',
			'description': 'Appropriate key was not found'
		}, 400)
	
	try:
		payload = jwt.decode(
			token,
			rsa_key,
			algorithms=ALGORITHMS,
			audience=API_AUDIENCE,
			issuer=f'https://{AUTH0_DOMAIN}/'
		)
		return payload

	except jwt.ExpiredSignatureError:
		raise AuthError({
			'code': 'expired_token',
			'description': 'Expired token.'
		}, 400)

	except jwt.JWTClaimsError:
		raise AuthError({
			'code': 'invalid_claims',
			'description': 'Invalid claims.'
		}, 400)

	except Exception:
		raise AuthError({
			'code': 'invalid_header',
			'description': 'Authentication token could not be parsed'
		}, 400)

def requires_auth(permission=''):
	def requires_auth_decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			token = get_token_auth_header()
			payload = verify_decode_jwt(token)
			check_permissions(permission, payload)
			return f(payload, *args, **kwargs)

		return wrapper
	return requires_auth_decorator