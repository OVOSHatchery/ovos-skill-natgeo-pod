import requests
from ovos_workshop.decorators import intent_handler
from ovos_workshop.decorators import resting_screen_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill


class NatGeoPictureOfThedaySkill(OVOSSkill):

    def update_picture(self):
        try:
            url = "https://www.natgeotv.com/ca/photo-of-the-day"
            data = requests.get(url).text
            for c in data.split('class="PODItem"')[1:]:
                title = "National Geographic Photo of the day"
                url = c.split('src="')[1].split('"')[0]
                summary = c.split('class="ItemDescription">')[1].split('</div>')[0]
                if not self.lang.lower().startswith("en"):
                    summary = self.translator.translate(summary, self.lang)
                    title = self.translator.translate(title, self.lang)
                self.settings['imgLink'] = url
                self.settings['title'] = title
                self.settings['summary'] = summary
        except Exception as e:
            self.log.exception(e)
        self.gui['imgLink'] = self.settings['imgLink']
        self.gui['title'] = self.settings['title']
        self.gui['summary'] = self.settings['summary']
        self.set_context("NatGeo")

    @resting_screen_handler("NatGeo")
    def idle(self, message):
        self.update_picture()
        self.gui.show_page('idle.qml')

    @intent_handler('natgeo.intent')
    def handle_pod(self, message):
        self.update_picture()
        self.gui.show_image(self.settings['imgLink'],
                            caption=self.settings['title'],
                            fill='PreserveAspectFit')
        self.speak("National Geographic Photo of the day")

    @intent_handler(
        IntentBuilder("ExplainIntent").require("ExplainKeyword").require(
            "NatGeo"))
    def handle_explain(self, message):
        self.speak(self.settings['summary'])
