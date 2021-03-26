export const environment = {
  production: false,
  apiServerUrl: "http://127.0.0.1:5000", // the running FLASK api server url
  auth0: {
    url: "torquato", // the auth0 domain prefix
    audience: "coffee-shop", // the audience set for the auth0 app
    clientId: "Adxqb4rbqTIoqxsETkJi6crFLk8oTief", // the client id generated for the auth0 app
    callbackURL: "http://localhost:4200", // the base url of the running ionic application.
  },
};
