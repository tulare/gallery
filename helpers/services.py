# -*- encoding: utf-8 -*-

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import os
import re
import lxml.html
import urllib.parse
import requests


class ServiceError(BaseException) :
    pass


class Service :
    def __init__(self, session=None) :
        self.session = session or requests.Session()

    @property
    def session(self) :
        return self._session

    @session.setter
    def session(self, session) :
        self._session = session
        log.debug(
            '{} SESSION HEADERS {}'.format(
                self.__class__.__name__,
                self.session.headers
            )
        )


    @property
    def user_agent(self) :
        return self._session.headers['User-Agent']

    @user_agent.setter
    def user_agent(self, agent) :
        self._session.headers.update({ 'User-Agent' : agent })
        log.debug(
            '{} SESSION HEADERS {}'.format(
                self.__class__.__name__,
                self.session.headers
            )
        )
        
    def test(self) :
        return self.session.get('http://httpbin.org/get').json()
    

class WebRequest(Service) :
    def __call__(self, url) :
        log.debug(
            '{} CALL URL {} HEADERS {}'.format(
                self.__class__.__name__,
                url,
                self.session.headers
            )
        )
        try :
            page = self.session.get(url)
            page.raise_for_status()
            return page
        except requests.exceptions.RequestException as e :
            raise ServiceError(e)


class GrabService(Service) :
    def __init__(self, session=None) :
        super().__init__(session)

        self.tree = None
        self._url = None
        self._head = '.+'
        self._ext = 'jpg', 'jpeg', 'png', 'bmp', 'gif'

    def _grab(self, url) :
        log.debug(
            '{} GRAB URL "{}"'.format(
                self.__class__.__name__,
                url
            )
        )
        try :
            stream_saved = self.session.stream
            self.session.stream = True
            page = self.session.get(url)
            page.raise_for_status()
            self.tree = lxml.html.fromstring(page.content)
            self._url = url
        except requests.exceptions.RequestException as e :
            log.error(
                '{} GRAB URL "{}" {}'.format(
                    self.__class__.__name__,
                    url,
                    repr(e)
                )
            )   
            raise ServiceError(e)
        finally :
            self.session.stream = stream_saved

    def update(self) :
        self._grab(self.url)

    @property
    def url(self) :
        return self._url

    @url.setter
    def url(self, url) :
        self._grab(url)

    @property
    def head(self) :
        return self._head

    @head.setter
    def head(self, head) :
        self._head = head

    @property
    def ext(self) :
        return self._ext

    @ext.setter
    def ext(self, ext) :
        self._ext = tuple(ext)

    @property
    def images(self) :
        log.debug(
            '{} IMAGES HEAD {} EXT {}'.format(
                self.__class__.__name__,
                self.head, self.ext
            )
        )
        images = list()
        if self.tree is not None :
            images = [
                urllib.parse.urljoin(self.url, image)
                for image in filter(
                    lambda item : (
                        re.match(self.head, os.path.basename(item))
                        and re.search('\.('+'|'.join(self.ext)+')\?*', item)
                    ),
                    self.tree.xpath('//img/@src')
                )
            ]
        return images

    @property            
    def links(self) :
        log.debug(
            '{} LINKS HEAD {} EXT {}'.format(
                self.__class__.__name__,
                self.head, self.ext
            )
        )
        links = list()
        if self.tree is not None :
            links = [
                urllib.parse.urljoin(self.url, link)
                for link in filter(
                    lambda item :
                        re.match(self.head, os.path.basename(item))
                        and re.search('\.('+'|'.join(self.ext)+')\?*', item),
                    self.tree.xpath(
                        '//a/@href'
                    )
                )
            ]

        return links
            
if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)
    gs = GrabService()
    
