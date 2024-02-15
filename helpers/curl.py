# -*- coding: utf-8 -*-

__all__ = ['CurlEngine', 'PageHTML', 'site_url', 'force_https']

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import subprocess
import pathlib
import urllib.parse
import lxml.etree

# ------------------------------------------------------------------------------

class PageHTML :
    def __init__(self, page) :
        self._page = page

    @property
    def url(self) :
        return self._page.get('url')

    @property
    def source(self) :
        return self._page.get('source')

    @property
    def tree(self) :
        return self._page.get('tree')

# ------------------------------------------------------------------------------

class CurlEngine :

    def __init__(self, *, encoding='utf-8', use_tor=False, circuit='', cookie=None) :
        self.encoding = encoding
        self.use_tor = use_tor
        self.tor_circuit = circuit
        self.cookie = cookie

    @property
    def encoding(self) :
        return self._encoding
    @encoding.setter
    def encoding(self, value) :
        self._encoding = value

    @property
    def use_tor(self) :
        return self._use_tor
    @use_tor.setter
    def use_tor(self, value) :
        self._use_tor = bool(value)

    @property
    def tor_circuit(self) :
        return self._tor_circuit
    @tor_circuit.setter
    def tor_circuit(self, value) :
        self._tor_circuit = f'{value}@' if value else ''

    @property
    def cookie(self) :
        return self._cookie
    @cookie.setter
    def cookie(self, value) :
        self._cookie = value

    def _command(self) :
        # construire la command curl
        curl_command = ['curl', '--ssl-no-revoke']

        if self.cookie is not None :
            curl_command.extend(['--cookie', self.cookie])
        if self.use_tor :
            curl_command.extend(['--socks5-hostname', f'{self.tor_circuit}localhost:9150'])
        #log.debug(curl_command)

        return curl_command

    def load(self, url) :
        curl_command = self._command()
        curl_command.extend([f'{url}'])
        log.debug(curl_command)

        try :
            data = subprocess.check_output(curl_command, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e :
            log.error(e)
            raise OSError(e)

        return PageHTML({
            'url' : url,
            'source' : data.decode(self.encoding),
            'tree' : lxml.etree.HTML(data)
        })

    def post(self, url, data='', header=None) :
        curl_command = self._command()
        curl_command.extend(['--data', f'{data}', '-X', 'POST', f'{url}'])
        if header is not None :
            curl_command.extend(['-H', header])
        log.debug(curl_command)

        try :
            data = subprocess.check_output(curl_command, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e :
            log.error(e)
            raise OSError(e)

        return PageHTML({
            'url' : url,
            'source' : data.decode(self.encoding),
            'tree' : lxml.etree.HTML(data)
        })

    def download(self, url, outdir='.', filename=None) :
        # chemin relatif url
        url_path = pathlib.Path(urllib.parse.urlparse(url).path)

        # répertoire de sortie
        output_dir = pathlib.Path(outdir)
        if not output_dir.exists() :
            output_dir.mkdir()
        elif not output_dir.is_dir() :
            raise OSError(f"{output_dir} existe mais ce n'est pas un répertoire")

        # fichier de sortie
        output_file = output_dir / url_path.name
        if filename is not None :
            filename = pathlib.Path(filename)
            output_file = output_file.with_name(f'{filename.stem}_{url_path.name}')
        
        # construire la commande curl
        curl_command = self._command()        
        curl_command.extend([f'{url}', '--output', f'{output_file}'])
        log.debug(curl_command)

        # exécuter la commande
        try :
            subprocess.check_call(curl_command)
        except subprocess.CalledProcessError as e :
            raise OSError(e)

    def show_ip(self) :
        page = self.load('https://httpbin.org/ip')
        return page.source

    def show_cookies(self) :
        page = self.load('https://httpbin.org/cookies')
        return page.source

# ------------------------------------------------------------------------------

def site_url(url) :
    return urllib.parse.urlparse(url).netloc

# ------------------------------------------------------------------------------

def force_https(url) :
    url_parsed = urllib.parse.urlparse(url)
    url_https = url_parsed._replace(scheme='https')
    return urllib.parse.urlunparse(url_https)

