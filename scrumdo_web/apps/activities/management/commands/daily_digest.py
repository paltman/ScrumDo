import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template import loader, Context
from django.conf import settings
from activities.models import Activity, StoryActivity

from mailer import send_mail
from django.core.mail import EmailMultiAlternatives

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        for user in User.objects.all():
            if user.email_subscriptions.count() > 0:
                try:
                    self.dailyDigest( user )
                except:
                    logger.error("Could not send daily digest to %s" % user)
    
    def dailyDigest( self, user ):
        logger.debug( "Sending daily digest to %s" % user )
        
        template = loader.get_template('activities/digest_header.html')
        context = Context( {"user":user, "site_name":settings.SITE_NAME } )        
        body = template.render(context)
        domain = settings.BASE_URL
        
        email_address = user.email
        
        for sub in user.email_subscriptions.all():
            if not sub.project.active:
                continue
            logger.debug(sub)
            today = datetime.date.today()
            mdiff = datetime.timedelta(days=-1) # TODO - change this to 1
            daterange = today + mdiff            
            stories = {}
            activities = Activity.objects.filter( project=sub.project, created__gte=daterange).order_by("-created")
            for act in activities:
                act = act.mergeChildren()
                if hasattr(act,"story"):
                    if act.story.id in stories:
                        stories[act.story.id]["activities"].append(act)
                    else:
                        stories[act.story.id] = {"story":act.story, "activities":[act] }
                    
            template = loader.get_template('activities/digest_project.html')
            context = Context( {"project":sub.project , "stories":stories, "domain":domain, 'email_address':email_address,"support_email":settings.CONTACT_EMAIL} )        
            body = "%s %s" % (body, template.render(context))
        
        template = loader.get_template('activities/digest_footer.html')
        context = Context( {"user":user , "domain":domain, 'email_address':email_address,"support_email":settings.CONTACT_EMAIL} )        
        body = "%s %s" % (body, template.render(context))
        
        subject, from_email, to = 'ScrumDo Daily Digest', 'noreply@scrumdo.com', email_address
        text_content = 'See html email...'
        html_content = body
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        
        # logger.debug(body)

        
        
        

