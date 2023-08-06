import datetime
from typing import List
from typing import Optional

from bs4 import BeautifulSoup

from dphonebook.lib.numberprovider import NumberProvider
from dphonebook.lib.numberprovider import SiteNotAvailable
from dphonebook.lib.phonenumber import PhoneNumber


class ReceiveSmss(NumberProvider):

    @staticmethod
    def domain() -> str:
        return 'receive-smss.com'

    def run(self) -> List[PhoneNumber]:

        response = self.session.get(f'https://{self.domain()}/')

        if not response.ok:
            raise SiteNotAvailable(response.content)

        page = BeautifulSoup(response.content, features='html.parser')
        number_links = page.find_all('h4', class_='number-boxes-itemm-number')

        self.progress_total = len(number_links) - 1

        for number_element in number_links:
            self.progress_current += 1
            if self.stopped():
                return

            number = number_element.contents.pop()
            last_message_time = self.last_message_time(number)
            if not self.verify_number_active(number, last_message_time):
                self.logger.info('ReceiveSmss number %s is not active, skipping', number)
                continue
            self.writer.append(PhoneNumber(
                number,
                provider=self.domain(),
                last_message=last_message_time,
                url=self.number_to_url(number)
            ))

    def number_to_url(self, number_uri_fragment: str) -> str:
        return f'https://{self.domain()}/sms/{number_uri_fragment.strip("+")}/'

    def last_message_time(self, number: str) -> Optional[datetime.datetime]:
        response = self.session.get(self.number_to_url(number))
        if not response.ok:
            return None

        page = BeautifulSoup(response.content, features='html.parser')

        # Get the first row on "received messages" table (the latest message)
        try:
            latest_message = page.find('table', class_='wrptable').find('tbody').find('tr')

            # Fuzzy time ("43 minutes ago") on the 2nd column
            latest_time = latest_message.find_all('td')[2].find('span').contents.pop()

            # Assuming less than a day from latest activity on this number
            # Provider increments fuzzy time units from hours -> days -> ...
            # Unclear how "true" reported message times are
            return self.fuzzy_time_to_datetime(latest_time)
        except Exception as e:
            self.logger.warn(e)

        return None
