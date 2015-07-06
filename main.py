#!/usr/bin/env python
from google.appengine.ext.webapp import template

from google.appengine.ext import ndb
# from google.appengine.ext import db
from google.appengine.api import users
import logging
import os.path
import webapp2

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from models import User, Message
import json

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
        self.render_template('main.html')
class SignupHandler(BaseHandler):    

    def get(self):
        print "this is get"
        self.render_template('signup.html')
  
    def post(self):
        
        print "this is post in SignupHandler"
        data = json.loads(self.request.body)
        print data
        fullname = data.get('fullname')
        email = data.get('email')
        password = data.get('password')
        print fullname
        print email
        print password
        unique_properties = ['email_address', 'name']
        user_data = self.user_model.create_user(fullname,
                                                unique_properties,
                                                email_address=email, name=fullname,
                                                password_raw=password,
                                                verified=False)
        print email
        print password
        print fullname
        print user_data
        if not user_data[0]:  # user_data is a tuple
            print "Unable to create user for emailb because of duplicate keys"
            status_message = "Error"
            message = 'Unable to create user for email %s because of \
            duplicate keys %s' % (fullname, user_data[1])
            result = {'status_message': status_message, 'message': message}
            self.response.headers['content-type'] = 'application/json'
            self.response.write(json.dumps(result))
        else:
            users = User.query().fetch()
            user_list = []
            for user in users:
                user_list.append(user)
                print user.name
            user = user_data[1]
            status_message = "Success"
            message = "Successfully registerd please signin"
            result = {'status_message': status_message, 'message': message}
            self.response.headers['content-type'] = 'application/json'
            self.response.write(json.dumps(result))


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

        # it should be something more concise like
        # self.auth.get_user_by_token(user_id, signup_token)
        # unfortunately the auth interface does not (yet) allow to manipulate
        # signup tokens concisely
        user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
                                                     'signup')

        if not user:
            logging.info('Could not find any user with id "%s" signup token "%s"',
                         user_id, signup_token)
            self.abort(404)

        # store user data in the session
        self.auth.set_session(
            self.auth.store.user_to_dict(user), remember=True)

        if verification_type == 'v':
            # remove signup token, we don't want users to come back with an old
            # link
            self.user_model.delete_signup_token(user.get_id(), signup_token)

            if not user.verified:
                user.verified = True
                user.put()

            self.display_message('User email address has been verified.')
            return
        elif verification_type == 'p':
            # supply user to the page
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

        # remove signup token, we don't want users to come back with an old
        # link
        self.user_model.delete_signup_token(user.get_id(), old_token)

        self.display_message('Password updated')


class LoginHandler(BaseHandler):

    # def get(self):
    # guests = model.AllGuests()
    # r = [ AsDict(guest) for guest in guests ]
    # self.SendJson(r)

    def get(self):
        self._serve_page()

    
    # def SendJson(self, r):
    #     self.response.headers['content-type'] = 'text/plain'
    #     self.response.write(json.dumps(r))


    def post(self):
        print "this is post in LoginHandler"
        data = json.loads(self.request.body)
        print data

        print type(data)
        
        print"***************"*20
        fullname = data.get('fullname')       
        password = data.get('password')
        print fullname  
        print password
        print"***************"*20

    # def post(self):
    #     name = self.request.get('fullname')
    #     password = self.request.get('password')
        # email = self.request.get('email_address')
        # auser = self.auth.get_user_by_session()
        # userid = auser['user_id']
        # user = auth_models.User.get_by_id(auser['user_id'])
        # existing_user = auth_models.User.get_by_auth_id(email)

        # user = self.auth.get_user_by_session()

        # print user
        # print existing_user
        try:
            u = self.auth.get_user_by_password(fullname, password, remember=True,
                                           save_session=True)

            
            all_users = User.query().fetch()

            user_list = []
            print "Name Name "
            print "Name Name "
            print u.get('name')
            curren_user = u.get('name')
            

            for user in all_users:
                user_list.append(user.name)
                print user.name
            print user_list
            print type(user_list)
           
            message_list = []
            message = Message.all()
            current_message = message.filter("receiver =", "%s"%curren_user )
            print current_message
            
            print '>>>>>>>>>>>>>>>>>>>>>>'

            #message.filter("last_name =", "Smith")

            for msg in message:
                message_list.append(msg.message) 
            print '************************'    
            print message_list    
            print '************************'

            # status_message = "Success"
            # message = "Successfully registerd please signin"
            # result = {'status_message': status_message, 'message': message}
            

            #self.response.headers['content-type'] = 'text/plain'
            #self.response.write(json.dumps(user_list,message_list))



            userlist = user_list
            messagelist = message_list
            result = {'userlist': userlist, 'messagelist': messagelist}
            self.response.headers['content-type'] = 'application/json'
            self.response.write(json.dumps(result))




            #self.send(user_list)
            # self.render_template('user_list.html', {'user_list': user_list})
            # user = users.get_current_user()
            # print user.name

            # self.redirect(self.uri_for('home'))
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            logging.info(
                'Login failed for user %s because of %s', fullname, type(e))
            self._serve_page(True)

    def _serve_page(self, failed=False):
        name = self.request.get('fullname')
        mail = self.request.get('email_address')
        # user = users.get_current_user()
        params = {
            'name': name,
            'failed': failed
        }
        self.render_template('login.html', params)


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
        self.redirect(self.uri_for('/home'))


class AuthenticatedHandler(BaseHandler):

    @user_required
    def get(self):
        self.render_template('authenticated.html')


class MessageHandler(BaseHandler):

    def get(self):    

        users = User.query().fetch()
        user_list = []
        for user in users:
            user_list.append(user) 

        message = Message.all() 
        message_list = []
        for msg in message:
            message_list.append(msg)               
    
        self.render_template('user_list.html', {'user_list': user_list, 'message_list': message_list})


class User_messageHandler(BaseHandler):
    def get(self):
        print '**********This is upto template*****************'
        self.render_template('user_message.html')


    def post(self):
        print "this is post in usermessageHandler"
        data = json.loads(self.request.body)
        print data
        print type(data)
        print"***************"*20
        reciver = data.get('reciver')
        message= data.get('message')
        
        print reciver
        print Message
        print"***************"*20
        user_message = Message(receiver = reciver,message= message)
        user_message.put()
        message_list = []
        message = Message.all() 
        for msg in message:
            message_list.append(msg.message)
            
            print msg.message
              

        print '_______________________________'
        print message_list 
        print '_______________________________'   
        self.response.headers['content-type'] = 'text/plain'
        self.response.write(json.dumps(message_list))
    

        # print data.fullname
        # print data.email
        # print data.password
        
        # for json_data in data:
        #     print json_data.fullname
        #     print json_data.email
        #     print json_data.password
        # email = self.request.get('email')
        # name = self.request.get('name')
        # password = self.request.get('password')
        # last_name = self.request.get('lastname')

        #unique_properties = ['email_address', 'name']
        # user_message = self.user_model.create_user(
                                                
        #                                         reciver=reciver, 
        #                                         Messgage=Messgage,
        #                                         verified=False)
        # user_data = self.user_model.create_user(fullname,
        #                                         unique_properties,
        #                                         email_address=email, name=fullname,
        #                                         password_raw=password,
        #                                         verified=False)
        print reciver
        
        print Message
        #print user_data
        # if not user_message[0]:  # user_data is a tuple
        #     print "Unable to create user for emailb because of duplicate keys"
        #     status_message = "Error"
        #     message = 'Unable to create user for email %s because of \
        #     duplicate keys %s' % (fullname, user_data[1])
        #     result = {'status_message': status_message, 'message': message}
        #     self.response.headers['content-type'] = 'application/json'
        #     self.response.write(json.dumps(result))
        #     # self.display_message('Unable to create user for email %s because of \
        #     # duplicate keys %s' % (fullname, user_data[1]))
        #     # return
        # else:
        #     users = User.query().fetch()

        #     user_list = []

        #     for user in users:
        #         user_list.append(user)
        #         print user.name


        #     user = user_data[1]
        # # user_id = user.get_id()

        # # token = self.user_model.create_signup_token(user_id)

        # # verification_url = self.uri_for('verification', type='v', user_id=user_id,
        #                                 # signup_token=token, _full=True)

        # # msg = 'Send an email to user in order to verify \
        # #      their address. \
        # #   They will be able to do so by visiting <a href="{url}">{url}</a>'

        # # self.display_message(msg.format(url=verification_url))
        #     status_message = "Success"
        #     message = "Successfully registerd please signin"
        #     result = {'status_message': status_message, 'message': message}
        #     self.response.headers['content-type'] = 'application/json'
        #     self.response.write(json.dumps(result))






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
    webapp2.Route('/', MainHandler, name='main'),    
    webapp2.Route('/signup', SignupHandler),
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
                  handler=VerificationHandler, name='verification'),
    webapp2.Route('/message',MessageHandler, name='message'),
    webapp2.Route('/usermessage',User_messageHandler, name='usermessage'),
    webapp2.Route('/password', SetPasswordHandler),
    webapp2.Route('/login', LoginHandler, name='login'),
    webapp2.Route('/logout', LogoutHandler, name='logout'),
    webapp2.Route('/forgot', ForgotPasswordHandler, name='forgot'),
    webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated')
], debug=True, config=config)

logging.getLogger().setLevel(logging.DEBUG)
