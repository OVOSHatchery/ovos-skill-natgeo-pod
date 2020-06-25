from mycroft import MycroftSkill, intent_file_handler, intent_handler
import requests
from mycroft.skills.core import resting_screen_handler
from adapt.intent import IntentBuilder
from mtranslate import translate
from datetime import datetime, timedelta


class NatGeoPictureOfThedaySkill(MycroftSkill):

    def update_picture(self):
        try:
            today = datetime.now().replace(hour=12, second=0, minute=0,
                                           microsecond=0)
            if not self.settings.get("ts"):
                self.settings["ts"] = (today - timedelta(days=1)).timestamp()
            if today.timestamp() != self.settings["ts"] or \
                    not self.settings.get('imgLink'):
                baseurl = "https://www.nationalgeographic.com/photography/photo-of-the-day" \
                          "/_jcr_content/.gallery."
                url = baseurl + str(today.year) + "-" + str(today.month) + ".json"

                data = requests.get(url).json()

                title = data['items'][0]['image']['title']
                summary = data['items'][0]['image']['caption']
                if not self.lang.lower().startswith("en"):
                    summary = translate(summary, self.lang)
                    title = translate(title, self.lang)

                self.settings['imgLink'] = data['items'][0]['image']['uri']
                self.settings['title'] = title
                self.settings['summary'] = summary
                self.settings["ts"] = today.timestamp()
        except Exception as e:
            self.log.exception(e)
        self.gui['imgLink'] = self.settings['imgLink']
        self.gui['title'] = self.settings['title']
        self.gui['summary'] = self.settings['summary']
        self.set_context("NatGeo")

    @resting_screen_handler("NatGeo")
    def idle(self, message):
        self.update_picture()
        self.gui.clear()
        self.gui.show_page('idle.qml')

    @intent_file_handler('natgeo.intent')
    def handle_pod(self, message):
        self.update_picture()
        self.gui.clear()
        self.gui.show_image(self.settings['imgLink'],
                            caption=self.settings['title'],
                            fill='PreserveAspectFit')

        self.speak(self.settings['title'])

    @intent_handler(IntentBuilder("ExplainIntent")
                    .require("ExplainKeyword").require("NatGeo"))
    def handle_explain(self, message):
        self.speak(self.settings['summary'])


def create_skill():
    return NatGeoPictureOfThedaySkill()
