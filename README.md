# Extended Example for OAuth 2 Server

This is an extended example of OAuth 2 Server.

The original version can be found here
<http://lepture.com/en/2013/create-oauth-server>.

This extends that example to include niceties that would be found in a full
oauth2 implementation.

*This should not be used as is in production*.

## Why was this created?

I was working on an implementation and while the original example is helpful,
there are a ton of things all going on in a single file. It was easier to see
how things fit together once I split everything out in a way that better
matched how an actual site would be designed.

Also some of the original actions return json, probably for ease of setting
up the example, this attempts to use HTML displays in those cases.

I also wanted to make sure it worked with python3. This is tested on 3.4.3

## What has been changed?

- Both of the apps are in separate folders
- The provider uses a flask blueprint structure where each logical section is
  split off into a separate controller.
- The provider also has a number helper displays for clients, users, etc.
- A login\_required decorator is used to check if the user is authenticated.
- The client has been updated to specifically require clicking on "login"
- Assuming no errors the client will also redirect once authentication is
  completed. If there are errors an HTML template now displays them rather
  than a python string template.

## What still needs to be done?

- Csrf protection on all of the forms.
- Haven't actually tested not being authenticated when attempting
  authorization. The redirect may not be escaping things correctly for the
  redirect.
- More error checking on all of the forms.
- Ideally the provider user would have a password, and there would be a way
  to bootstrap an initial admin user who could then create new users.
- If an admin distinction is used, then roles need to be created.
- The client secret info should not be that easy to view. Although again as
  an example this is fine.
- Creating a new client could use frontend work, as in it should be possible
  to insert multiple redirect uris/scopes without reloading the page. Right
  now you can remove them by submitting blank text, but a more obvious
  "delete" would be nice.
- If there is only one provider then having a single client id/secret in the
  settings makes sense, but that too could be put in a database at which point
  there could be multiple login buttons for various providers.

# Installation

    $ pip install -r requirements.txt

# Usage

*Note* there may be issues running both of these servers on the same host, so
one should use 127.0.0.1 and the other should use localhost.

1. Start your provider server with:

        $ cd provider
        $ python app.py

2. Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) and fill a username.

3. And then visit [http://127.0.0.1:5000/client](http://127.0.0.1:5000/client).
   Then click "add client" to get a new client.

4. Take the client key and client secret, and modify the client.py script
   with the key and secret. Specifically update `CLIENT_ID` and `CLIENT_SECRET`
   variables on lines 5-6.

5. Start the client server with:

        $ cd client
        $ python client.py


6. Visit [http://localhost:8000](http://localhost:8000), click on the "login"
   button to begin the process. Once redirected to the confirm page, choose yes,
   the client will obtain a pair of access token and secret. Assuming no errors
   the home page will indicate "loggied in as" with the provider username and
   display the token info.
