#!/usr/bin/env python

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.api import users

import logging
import os.path
import webapp2

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from models import User
import webapp2

import os
from google.appengine.api import mail

def user_required(handler):
    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            self.redirect(self.uri_for('login'), abort=True)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def user_info(self):
        return self.auth.get_user_by_session()

    @webapp2.cached_property
    def user(self):
        u = self.user_info
        return self.user_model.get_by_id(u['user_id']) if u else None

    @webapp2.cached_property
    def user_model(self):
        return self.auth.store.user_model

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="datastore")

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        user = self.user_info
        params['user'] = user
        path = os.path.join(os.path.dirname(__file__), 'views', view_filename)
        self.response.out.write(template.render(path, params))

    def display_message(self, message):
        params = {
            'message': message
        }
        self.render_template('message.html', params)

   
    def dispatch(self):        
        self.session_store = sessions.get_store(request=self.request)

        try:            
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)


class MainHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


class SignupHandler(BaseHandler):
    def get(self):
        self.render_template('signup.html')

    def post(self):
        user_name = self.request.get('fullname')
        email = self.request.get('email')       
        password = self.request.get('password')       

        unique_properties = ['email_address', 'name']
        user_data = self.user_model.create_user(user_name,
                                                unique_properties,
                                                email_address=email, name=user_name, password_raw=password,
                                                verified=False)
        if not user_data[0]:  
            self.display_message('Unable to create user for email %s because of \
            duplicate keys %s' % (user_name, user_data[1]))
            return

        users = User.query().fetch()

        user_list = []

        for user in users:
            user_list.append(user)          
        

        user = user_data[1]
        user_id = user.get_id()

        token = self.user_model.create_signup_token(user_id)

        verification_url = self.uri_for('verification', type='v', user_id=user_id,
                                        signup_token=token, _full=True)

        msg = 'Send an email to user in order to verify their address. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

        
        self.display_message("successfully registered")    


class ForgotPasswordHandler(BaseHandler):

    def get(self):
        self._serve_page()

    def post(self):
        username = self.request.get('fullname')

        user = self.user_model.get_by_auth_id(username)
        if not user:
            logging.info(
                'Could not find any user entry for username %s', username)
            self._serve_page(not_found=True)
            return

        user_id = user.get_id()
        token = self.user_model.create_signup_token(user_id)

        verification_url = self.uri_for('verification', type='p', user_id=user_id,
                                        signup_token=token, _full=True)

        msg = 'Send an email to user in order to reset their password. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

        self.display_message(msg.format(url=verification_url))

    def _serve_page(self, not_found=False):
        username = self.request.get('fullname')
        params = {
            'username': username,
            'not_found': not_found
        }
        self.render_template('forgot.html', params)


class VerificationHandler(BaseHandler):

    def get(self, *args, **kwargs):
        user = None
        user_id = kwargs['user_id']
        signup_token = kwargs['signup_token']
        verification_type = kwargs['type']
       
        user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
                                                     'signup')

        if not user:
            logging.info('Could not find any user with id "%s" signup token "%s"',
                         user_id, signup_token)
            self.abort(404)
        
        self.auth.set_session(
            self.auth.store.user_to_dict(user), remember=True)

        if verification_type == 'v':
            
            self.user_model.delete_signup_token(user.get_id(), signup_token)

            if not user.verified:
                user.verified = True
                user.put()

            self.display_message('User email address has been verified.')
            return
        elif verification_type == 'p':
           
            params = {
                'user': user,
                'token': signup_token
            }
            self.render_template('resetpassword.html', params)
        else:
            logging.info('verification type not supported')
            self.abort(404)


class SetPasswordHandler(BaseHandler):

    @user_required
    def post(self):
        password = self.request.get('password')
        old_token = self.request.get('t')

        if not password or password != self.request.get('confirm_password'):
            self.display_message('passwords do not match')
            return

        user = self.user
        user.set_password(password)
        user.put()

       
        self.user_model.delete_signup_token(user.get_id(), old_token)

        self.display_message('Password updated')


class LoginHandler(BaseHandler):

    def get(self):
        self._serve_page()

    def post(self):
        name = self.request.get('fullname')
        password = self.request.get('password')
        

        try:            
            from google.appengine.api import users
           
            user = self.auth.get_user_by_password(name, password, remember=True,
                                               save_session=True)
          

            users = User.query().fetch()

            user_list = []

            for user in users:
                user_list.append(user)                
                

            self.render_template('user_list.html', {'user_list': user_list})
            
           
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            logging.info(
                'Login failed for user %s because of %s', name, type(e))
            self._serve_page(True)

    def _serve_page(self, failed=False):
        name = self.request.get('fullname')
        mail = self.request.get('email_address')
       
        params = {
            'name': name,
            'failed': failed
        }
        self.render_template('login.html', params)



class MessageHandler(BaseHandler):

    def get(self):
        

        users = User.query().fetch()

        user_list = []

        for user in users:
            user_list.append(user)                
    
        self.render_template('user_list.html', {'user_list': user_list})



class UserHandler(BaseHandler):

    def get(self):
        self._serve_page()

    def _serve_page(self, failed=False):
        username = self.request.get('fullname')
        users = self.request.filter('auth_ids')

  
        self.render_template('userslist.html', params)


class LogoutHandler(BaseHandler):

    def get(self):
        self.auth.unset_session()
        self.redirect(self.uri_for('home'))


class AuthenticatedHandler(BaseHandler):

    @user_required
    def get(self):
        self.render_template('authenticated.html')



class mailHandler(BaseHandler):
     
    def get(self):
        self.render_template('contact_mail.html')
    def post(self):
        userMail=self.request.get("mail")
        subject=self.request.get("subject")
        
        userMessage=self.request.get("message")
        mail_store = User(email1 = userMail,subject =subject,message= userMessage)
        mail_store.put()
        
        message=mail.EmailMessage(sender="vinodsesetti@yopmail.com",subject="Test")



        if not mail.is_email_valid(userMail):
            self.response.out.write("Wrong email! Check again!")

        else:
            message.to=userMail
            message.body="""Thank you!
            You have entered following information:
            Your mail: %s
            Subject: %s
            
            Message: %s""" %(userMail,subject,userMessage)
            message.send()
            self.display_message("Message sent")



config = {
    'webapp2_extras.auth': {
        'user_model': 'models.User',
        'user_attributes': ['name', 'email_address', 'password']
    },
    'webapp2_extras.sessions': {
        'secret_key': 'YOUR_SECRET_KEY'
    }


}

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name='home'),    
    webapp2.Route('/signup', SignupHandler),
    webapp2.Route('/mail',mailHandler),
    webapp2.Route('/message',MessageHandler),    
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
                  handler=VerificationHandler, name='verification'),
    webapp2.Route('/password', SetPasswordHandler),
    webapp2.Route('/login', LoginHandler, name='login'),
    webapp2.Route('/logout', LogoutHandler, name='logout'),
    webapp2.Route('/forgot', ForgotPasswordHandler, name='forgot'),
    webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated'),
    

], debug=True, config=config)

logging.getLogger().setLevel(logging.DEBUG)
