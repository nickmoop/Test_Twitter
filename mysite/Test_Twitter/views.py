import tweepy

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from Test_Twitter.forms import Login, Search, Tweet
from Test_Twitter.models import TwitterUser


#HOST_NAME = ''
#ACCESS_KEY = ''
#ACCESS_SECRET = ''
#CONSUMER_KEY = ''
#CONSUMER_SECRET = ''


def look(request, user_name='none', post_name='none'):
    token = request.META.get('CSRF_COOKIE', None)
    user_token = getStatus(token)
    if not user_token:
        user_token = [ACCESS_KEY, ACCESS_SECRET]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(user_token[0], user_token[1])
    api = tweepy.API(auth)

    content = []
    content.append(user_token)
    if user_name != 'none':
        list_of_users = api.search_users(user_name)
        for i in range(0, 5):
            name = list_of_users[i].screen_name
            timeline = api.user_timeline(screen_name=name, count=5)
            content.append([list_of_users[i], timeline])
        content_type = 'users'
    elif post_name != 'none':
        list_of_result = api.search('#{}'.format(post_name))
        content = list_of_result[0:5]
        content_type = 'tweets'
    else:
        return redirect(HOST_NAME + '/Test_Twitter/search')

    template = loader.get_template('Test_Twitter/look.html')
    context = RequestContext(
        request,
        {'content': content, 'content_type': content_type}
    )

    return HttpResponse(template.render(context))


def tweet(request):
    token = request.META.get('CSRF_COOKIE', None)
    if not getStatus(token):
        return redirect(HOST_NAME + '/Test_Twitter/')

    if request.method == 'POST' and request.is_ajax():
        form = Tweet(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            message_status = sendMessage(token, message)

            return JsonResponse({'error_message': message_status})

    status = 'NOT logged in Twitter'
    if getStatus(token):
        status = 'logged in Twitter'

    template = loader.get_template('Test_Twitter/tweet.html')
    context = RequestContext(request, {'form': Tweet(), 'status': status})
    return HttpResponse(template.render(context))


def index(request):
    token = request.META.get('CSRF_COOKIE', None)
    status = 'NOT logged in Twitter'
    if getStatus(token):
        status = 'logged in Twitter'

    template = loader.get_template('Test_Twitter/index.html')
    context = RequestContext(request, {'status': status})
    return HttpResponse(template.render(context))


def admin(request):
    if request.method == 'POST' and request.is_ajax():
        form = Login(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if email == 'no' and password == 'no':
                return JsonResponse(
                    {'error_message': 'YOU LOGGED IN ADMIN PANEL'}
                )
            else:
                return JsonResponse({'error_message': 'SOMETHING WRONG'})

    template = loader.get_template('Test_Twitter/admin.html')
    context = RequestContext(request, {'form': Login()})
    return HttpResponse(template.render(context))


def logoutUser(token):
    TwitterUser.objects.filter(token=token).delete()


def callback(request):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    token = request.session['request_token']
    request.session.delete('request_token')
    auth.request_token = token

    verifier = request.GET.get('oauth_verifier')
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        return JsonResponse({'error_message': 'callback error'})

    key = auth.access_token
    secret = auth.access_token_secret
    token = request.META.get('CSRF_COOKIE', None)

    logoutUser(token)
    loginUser(token, key, secret)

    return redirect(HOST_NAME + '/Test_Twitter/')


def login(request):
    callback = 'https://nick1.pythonanywhere.com/Test_Twitter/callback'
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback)

    try:
        auth_url = auth.get_authorization_url()
    except tweepy.TweepError:
        return JsonResponse({'error_message': 'login error'})

    request.session['request_token'] = auth.request_token

    return redirect(auth_url)


def loginUser(token, oauth_token, oauth_secret):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(oauth_token, oauth_secret)
    api = tweepy.API(auth)

    username = api.me().screen_name
    new_user = TwitterUser(
        token=token,
        username=username,
        oauth_token=oauth_token,
        oauth_secret=oauth_secret)
    new_user.save()


def getStatus(token):
    current_users = TwitterUser.objects.all()
    for user in current_users:
        if user.token == token:
            return [user.oauth_token, user.oauth_secret]

    return False


def sendMessage(token, message):
    if len(message) > 140:
        error_message = 'YOUR MESSAGE TOO LONG : '
        error_message += '{} SYMBOLS INSTEAD OF 140'.format(len(message))
        return error_message

    user_token = getStatus(token)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(user_token[0], user_token[1])
    api = tweepy.API(auth)
    api.update_status(message)

    return 'TWEET SEND'


def search(request):
    if request.method == 'POST' and request.is_ajax():
        form = Search(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            message = form.cleaned_data['message']

            redirect_url = '{}/Test_Twitter/look/'.format(HOST_NAME)
            if (message != 'none') and (len(message) > len(user)):
                redirect_url += 'none/{}'.format(message)
                return JsonResponse({'redirect_url': redirect_url})
            elif (user != 'none') and (len(message) <= len(user)):
                redirect_url += '{}/none'.format(user)
                return JsonResponse({'redirect_url': redirect_url})
            else:
                error_message = 'ERROR {} {}'.format(message, user)
                return JsonResponse({'error_message': error_message})

    template = loader.get_template('Test_Twitter/search.html')
    context = RequestContext(request, {'form': Search()})
    return HttpResponse(template.render(context))
