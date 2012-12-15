from django.contrib import messages
from apps.account.templatetags.message_utils import message_level_as_text
import simplejson as json


class AjaxMessaging(object):
    def process_response(self, request, response):
        if request.is_ajax():
            print response['Content-Type']
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = json.loads(response.content)
                except ValueError:
                    return response

                django_messages = []

                for message in messages.get_messages(request):
                    msg = {
                        'level': message_level_as_text(message.level),
                        'message': message.message,
                        'extra_tags': message.tags
                    }
                    if message.is_persistent():
                      msg['read_url'] = '/messages/mark_read/' + str(message.pk) + '/'
                    else: msg['read_url'] = '#'
                    django_messages.append(msg)

                content['messages'] = django_messages

                response.content = json.dumps(content)
        return response
