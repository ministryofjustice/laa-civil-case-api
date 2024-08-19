# Access Tokens
All access tokens are valid for 30 minutes on the API. This can be adjusted by amending ACCESS_TOKEN_EXPIRE_MINUTES on the auth/security.py file. This can be authenticated via a username and password which is compared to the database. As long as the user is logged in, a JWT token can be generated for their user.

## Updating the Secret Key
The OAuth2 JWT encoding requires a SECRET_KEY. This can be defined in your .env file to generate unique tokens. All environments have a different secret key that defines what to be encoded against.

## Adding Auth to Routes
To add authorisation to any route, simple add the below to the route definition:
```shell
current_user: Users = Depends(get_current_active_user)
```

## Hashing and Encoding
All password information is hashed and salted per bcrypt and passlib. The token is then generated and encoded via JWT which uses the secret key to sign the identity of the token. This means that the token contains a header, payload and a signature following the HS256 algorithm ensuring security.