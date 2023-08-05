import os
import json
import time
from collections import defaultdict

import requests
import lxml.etree as ET

from freud_api_crawler.string_utils import clean_markup, extract_page_nr, always_https, normalize_white_space

from freud_api_crawler.tei_utils import make_pb

FRD_BASE = "https://www.freud-edition.net"
FRD_API = os.environ.get('FRD_API', f'{FRD_BASE}/jsonapi/')
FRD_WORK_LIST = f"{FRD_API}node/werk?filter[field_status_umschrift]=2"
FRD_WORK_SIGNATUR_EP = f"{FRD_API}taxonomy_term/signatur_fe/"
FRD_USER = os.environ.get('FRD_USER', False)
FRD_PW = os.environ.get('FRD_PW', False)
FULL_MANIFEST = "228361d0-4cda-4805-a2f8-a05ee58119b6"
HISTORISCHE_AUSGABE = "5b8d9c77-99d0-4a80-92d8-4a9de06ac7ca"

MANIFEST_DEFAULT_FILTER = {
    "field_doc_component.id": FULL_MANIFEST,
    "field_manifestation_typ.id": HISTORISCHE_AUSGABE,
    "field_status_umschrift": 2
}


def get_auth_items(username, password):
    """ helper function to fetch auth-cookie

    :param username: Drupal-User Username
    :type username: str
    :param password: Drupal-User Password
    :type password: str

    :return: A dict with auth-items `'cookie', 'current_user', 'csrf_token', 'logout_token'`
    :rtype: dict
    """

    url = "https://www.freud-edition.net/user/login?_format=json"
    payload = {
        "name": username,
        "pass": password
    }
    headers = {
        'Content-Type': 'application/json',
    }
    r = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload)
    )
    auth_items = {
        'cookie': r.cookies,
    }
    for key, value in r.json().items():
        auth_items[key] = value
    return auth_items


AUTH_ITEMS = get_auth_items(FRD_USER, FRD_PW)

XSLT_FILE = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "make_tei.xslt"
)

XSL_DOC = ET.parse(XSLT_FILE)

TEI_DUMMY = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "tei_dummy.xml"
)

CUR_LOC = os.path.dirname(os.path.abspath(__file__))


class FrdClient():

    """Main Class to interact with freud.net-API """

    def tei_dummy(self):
        doc = ET.parse(TEI_DUMMY)
        return doc

    def list_endpoints(self):
        """ returns a list of existing API-Endpoints
        :return: A PyLobidPerson instance
        """

        time.sleep(1)
        r = requests.get(
            self.endpoint,
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        d = defaultdict(list)
        for key, value in result['links'].items():
            url = value['href']
            node_type = url.split('/')[-2]
            d[node_type].append(url)
        return d

    def __init__(
        self,
        out_dir=CUR_LOC,
        endpoint=FRD_API,
        xsl_doc=XSL_DOC,
        auth_items={},
        limit=10,
    ):

        """ initializes the class

        :param out_dir: The directory to save processed Manifestations
        :type out_dir: str
        :param endpoint: The API Endpoint
        :type endpoint: str
        :param xsl_doc: A `lxml.etree._ElementTree` object (i.e. a parsed XSL-Stylesheet)
        :type xsl_doc: lxml.etree._ElementTree
        :param auth_items: The result dict of a successfull drupal api login action
        :type auth_items: dict
        :param limit: After how many next-loads the loop should stop
        :type pw: int

        :return: A FrdClient instance
        """
        super().__init__()
        self.endpoint = endpoint
        self.auth_items = auth_items
        self.cookie = self.auth_items['cookie']
        self.limit = limit
        self.werk_ep = f"{self.endpoint}node/werk"
        self.manifestation_ep = f"{self.endpoint}node/manifestation"
        self.nsmap = {
            "tei": "http://www.tei-c.org/ns/1.0",
            "xml": "http://www.w3.org/XML/1998/namespace",
        }
        self.tei_dummy = self.tei_dummy()
        self.out_dir = out_dir
        self.xsl_doc = xsl_doc


class FrdWerk(FrdClient):
    """class to deal with Werke
    :param werk_id: The hash ID of a Werk Node
    :type werk_id: str

    :return: A FrdWork instance
    :rtype: class:`freud_api_crawler.freud_api_crawler.FrdWerk`
    """

    def get_werk(self):
        """ returns the werk json as python dict

        :return: a Werk representation
        :rtype: dict
        """
        time.sleep(1)
        r = requests.get(
            self.ep,
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result

    def get_manifestations(
        self,
        filters={}
    ):
        """ retuns a list of dicts of related manifestation
        :param filters: a dictionary holding query filter params, see e.g. `MANIFEST_DEFAULT_FILTER`
        :type werk_id: dict

        :return: A list of dicts with ids and titles of the related manifestations
        :rtype: list
        """
        man_col = []
        fields_param = "fields[node--manifestation]=id,title"
        url = f"{self.manifestation_ep}{self.filtered_url}&{fields_param}"
        for key, value in filters.items():
            if value is not None:
                url += f"&filter[{key}]={value}"
        next_page = True
        while next_page:
            print(url)
            response = None
            result = None
            x = None
            time.sleep(1)
            response = requests.get(
                url,
                cookies=self.cookie,
                allow_redirects=True
            )
            result = response.json()
            links = result['links']
            if links.get('next', False):
                orig_url = links['next']['href']
                url = always_https(orig_url)
            else:
                next_page = False
            for x in result['data']:
                item = {
                    "man_id": x['id'],
                    "man_title": x['attributes']['title']
                }
                man_col.append(item)
        return man_col

    def get_fe_signatur(self):
        r = requests.get(
            f"{FRD_WORK_SIGNATUR_EP}{self.signatur_hash}",
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result['data']['attributes']['name']

    def __init__(
        self,
        werk_id=None,
        filter_finished=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.werk_id = werk_id
        self.ep = f"{self.werk_ep}/{self.werk_id}"
        self.werk = self.get_werk()
        self.signatur_hash = self.werk['data']['relationships']['field_signatur_sfe']['data']['id']
        self.signatur = self.get_fe_signatur()
        self.werk_attrib = self.werk['data']['attributes']
        self.filter_finished = filter_finished
        if filter_finished:
            self.filtered_url = f"?filter[field_werk.id]={self.werk_id}"
        else:
            self.filtered_url = f"?filter[field_werk.id]={self.werk_id}"
        for x in self.werk_attrib.keys():
            value = self.werk_attrib[x]
            if isinstance(value, dict):
                for y in value.keys():
                    dict_key = f"{x}__{y}"
                    setattr(self, f"md__{dict_key}", value[y])
            else:
                setattr(self, f"md__{x}", value)
        self.meta_attributes = [x for x in dir(self) if x.startswith('md__')]
        print("fetching related manifestations")
        self.manifestations = self.get_manifestations()
        self.manifestations_count = len(self.manifestations)


class FrdManifestation(FrdClient):

    """class to deal with Manifestations
    :param manifestation_id: The hash ID of a Manifestation Node
    :type manifestation_id: str

    :return: A FrdManifestation instance
    :rtype: class:`freud_api_crawler.freud_api_crawler.FrdManifestation`
    """

    def get_manifest(self):
        """ returns the manifest json as python dict

        :return: a Manifestation representation
        :rtype: dict
        """
        fields_to_include = [
            'field_werk',
            'field_werk.field_signature_sfg',
            'field_chapters'
        ]
        url = f"{self.manifestation_endpoint}?include={','.join(fields_to_include)}"
        time.sleep(1)
        r = requests.get(
            url,
            cookies=self.cookie,
            allow_redirects=True
        )
        print(url)
        result = r.json()
        return result

    def get_pages(self):
        """ method returning related page-ids/urls

        :return: a list of dicts `[{'id': 'hash-id', 'url': 'page_url'}]`
        :rtype: list
        """
        page_list = []
        if self.manifestation['data']['relationships']['field_chapters']['data']:
            print("looks like there are chapters")
            for y in self.manifestation['included']:
                try:
                    pages = y['relationships']['field_seiten']['data']
                except KeyError:
                    continue
                for x in pages:
                    node_type = x['type'].split('--')[1]
                    page = {
                        'id': x['id'],
                        'url': f"{self.endpoint}node/{node_type}/{x['id']}"
                    }
                    page_list.append(page)
        else:
            for x in self.manifestation['data']['relationships']['field_seiten']['data']:
                node_type = x['type'].split('--')[1]
                page = {
                    'id': x['id'],
                    'url': f"{self.endpoint}node/{node_type}/{x['id']}"
                }
                page_list.append(page)
        return page_list

    def get_page(self, page_id):
        """ fetches a page matching the given id or url and returns the manifestation_seite json

        :param page_id: A hash-id or url to a manifestation_seite endpoint
        :type page_id: string

        :return: A manifestation_seite dict
        :rtype: dict
        """

        if not page_id.startswith('http'):
            url = f"{self.endpoint}node/manifestation_seite/{page_id}"
        else:
            url = page_id

        print(url)

        time.sleep(1)
        r = requests.get(
            f"{url}?include=field_faksimile",
            cookies=self.cookie,
            allow_redirects=True
        )

        result = r.json()
        return result

    def process_page(self, page_json):
        """ processes a page_json to something more useful

        :param page_json: The API response of a manifestation_seite endpoint
        :type page_json: dict

        :return: A dict containing a cleaned body with needed metatdata\

        {
            'id': page_id,
            'body': <div xml:id=page_id><p>lorem ipsum</p></div>
        }

        :rtype: dict
        """
        page_attributes = page_json['data']['attributes']
        page_id = page_json['data']['id']
        try:
            body = page_attributes['body']['processed']
        except:  # noqa: E722
            print("\n#####################")
            print(f"no content for manifestation_seite/{page_id}")
            print("#####################\n")
            body = "<p>BLANK</p>"
        wrapped_body = f'<div xmlns="http://www.tei-c.org/ns/1.0" xml:id="page__{page_id}">{body}</div>'
        cleaned_body = clean_markup(wrapped_body)
        cleaned_body = normalize_white_space(cleaned_body)
        faks = page_json['included'][0]
        page_nr = extract_page_nr(page_attributes['title'])
        result = {
            'id': page_id,
            'title': page_attributes['title'],
            'page_nr': page_nr,
            'attr': page_attributes,
            'body': cleaned_body,
            'faks': faks,
            'faks__id': faks['id'],
            'faks__url': faks['links']['self']['href'],
            'faks__payload': faks['attributes']['uri']['url']
        }
        return result

    def make_xml(self, save=False, limit=True):

        """serializes a manifestation as XML/TEI document

        :param save: if set, a XML/TEI file `{self.save_path}` is saved
        :param type: bool

        :return: A lxml.etree
        """
        doc = self.tei_dummy
        root_el = doc.xpath('//tei:TEI', namespaces=self.nsmap)[0]
        root_el.attrib["{http://www.w3.org/XML/1998/namespace}base"] = "https://whatever.com"
        root_el.attrib[
            "{http://www.w3.org/XML/1998/namespace}id"
        ] = f"manifestation__{self.manifestation_id}"
        title = doc.xpath('//tei:title[@type="manifestation"]', namespaces=self.nsmap)[0]
        title.text = f"{self.md__title} ({self.manifestation_signatur})"
        if self.manifestation['data']['attributes']['field_shorttitle']:
            s_title = doc.xpath('//tei:title[@type="manifestation_short"]', namespaces=self.nsmap)[0]
            s_title.text = f"{self.manifestation['data']['attributes']['field_shorttitle']['value']}"
        p_title = doc.xpath('//tei:title[@type="publication"]', namespaces=self.nsmap)[0]
        p_rs = ET.Element("{http://www.tei-c.org/ns/1.0}rs")
        p_rs.attrib["type"] = "bibl"
        try:
            p_rs.attrib["ref"] = f"#bibl__{self.publication['data']['id']}"
        except TypeError or KeyError:
            p_rs.attrib["ref"] = f"#bibl__{self.publication}"
        try:
            p_rs.text = f"{self.publication['data']['attributes']['title']}"
        except TypeError or KeyError:
            p_rs.text = f"{self.publication}"
        p_title.append(p_rs)
        w_title = doc.xpath('//tei:title[@type="work"]', namespaces=self.nsmap)[0]
        w_rs = ET.Element("{http://www.tei-c.org/ns/1.0}rs")
        w_rs.attrib["type"] = "bibl"
        w_rs.attrib["ref"] = f"#bibl__{self.werk['id']}"
        w_title.append(w_rs)
        w_rs.text = f"{self.werk['attributes']['title']}"
        titleStmt = doc.xpath('//tei:titleStmt', namespaces=self.nsmap)[0]
        author = ET.Element("{http://www.tei-c.org/ns/1.0}author")
        try:
            author.text = f"{self.author['data']['attributes']['name']}"
        except TypeError or KeyError:
            author.text = f"{self.author}"
        titleStmt.insert(3, author)
        fileDesc = doc.xpath('//tei:fileDesc', namespaces=self.nsmap)[0]
        sourceDesc = ET.Element("{http://www.tei-c.org/ns/1.0}sourceDesc")
        bibl = ET.Element("{http://www.tei-c.org/ns/1.0}bibl")
        if self.publication is not None:
            try:
                bibl.attrib["{http://www.w3.org/XML/1998/namespace}id"] = f"bibl__{self.publication['data']['id']}"
            except KeyError or TypeError:
                return
            try:
                if self.publication['data']['attributes']['field_secondary_title']:
                    bibl_title = ET.Element("{http://www.tei-c.org/ns/1.0}title")
                    bibl_title.attrib['type'] = "sub"
                    bibl_title.text = f"{self.publication['data']['attributes']['field_secondary_title']['value']}"
                    bibl.append(bibl_title)
            except KeyError or TypeError:
                return
            try:
                if self.publication['data']['attributes']['field_shorttitle'] is not None:
                    bibl_title = ET.Element("{http://www.tei-c.org/ns/1.0}title")
                    bibl_title.attrib['type'] = "short"
                    bibl_title.text = f"{self.publication['data']['attributes']['field_shorttitle']['value']}"
                    bibl.append(bibl_title)
            except KeyError or TypeError:
                return
            try:
                if self.publication['data']['attributes']['field_titel'] is not None:
                    bibl_title = ET.Element("{http://www.tei-c.org/ns/1.0}title")
                    bibl_title.attrib['type'] = "main"
                    bibl_title.text = f"{self.publication['data']['attributes']['field_titel']['value']}"
                    bibl.append(bibl_title)
            except KeyError or TypeError:
                return
            try:
                places = self.publication['data']['attributes']['field_publication_place']
                for x in places:
                    place = x["value"]
                    bibl_place = ET.Element("{http://www.tei-c.org/ns/1.0}pubPlace")
                    bibl_place.text = place
                    bibl.append(bibl_place)
            except KeyError or TypeError:
                return
            try:
                if self.publication['data']['attributes']['field_publication_year'] is not None:
                    bibl_date = ET.Element("{http://www.tei-c.org/ns/1.0}date")
                    bibl_date.attrib['when'] = f"{self.publication['data']['attributes']['field_publication_year']}"
                    bibl_date.text = f"{self.publication['data']['attributes']['field_publication_year']}"
                    bibl.append(bibl_date)
            except KeyError or TypeError:
                return
            try:
                if self.publication['data']['attributes']['field_band'] is not None:
                    bibl_scope = ET.Element("{http://www.tei-c.org/ns/1.0}biblScope")
                    bibl_scope.text = f"{self.publication['data']['attributes']['field_band']['value']}"
                    bibl.append(bibl_scope)
            except KeyError or TypeError:
                return
            if self.publisher is not None:
                try:
                    bibl_publisher = ET.Element("{http://www.tei-c.org/ns/1.0}publisher")
                    bibl_publisher.text = self.publisher['data']['attributes']['name']
                    bibl.append(bibl_publisher)
                except KeyError or TypeError:
                    return
            if self.herausgeber is not None:
                try:
                    if type(self.herausgeber) is list:
                        for x in self.herausgeber:
                            bibl_publisher = ET.Element("{http://www.tei-c.org/ns/1.0}publisher")
                            bibl_publisher.text = x['data']['attributes']['name']
                            bibl.append(bibl_publisher)
                    else:
                        bibl_publisher = ET.Element("{http://www.tei-c.org/ns/1.0}author")
                        bibl_publisher.text = self.herausgeber['data']['attributes']['name']
                        bibl.append(bibl_publisher)
                except KeyError or TypeError:
                    return
            if self.pub_author is not None:
                try:
                    if type(self.pub_author) is list:
                        for x in self.pub_author:
                            bibl_author = ET.Element("{http://www.tei-c.org/ns/1.0}author")
                            bibl_author.text = x['data']['attributes']['name']
                            bibl.append(bibl_author)
                    else:
                        bibl_author = ET.Element("{http://www.tei-c.org/ns/1.0}author")
                        bibl_author.text = self.pub_author['data']['attributes']['name']
                        bibl.append(bibl_author)
                except KeyError or TypeError:
                    return
        sourceDesc.append(bibl)
        fileDesc.insert(4, sourceDesc)
        body = doc.xpath('//tei:body', namespaces=self.nsmap)[0]
        pages = self.pages
        if limit:
            actual_pages = pages[:2]
        else:
            actual_pages = pages
        for x in actual_pages:
            page_json = self.get_page(x['id'])
            pp = self.process_page(page_json)
            div = ET.fromstring(pp['body'])
            pb_el = make_pb(pp)
            cur_div = div.xpath('//tei:div', namespaces=self.nsmap)[0]
            cur_div.insert(0, pb_el)
            body.append(div)
        transform = ET.XSLT(self.xsl_doc)
        tei = transform(doc)
        if save:
            os.makedirs(os.path.join(self.save_dir, self.werk_signatur), exist_ok=True)
            with open(self.save_path, 'wb') as f:
                f.write(ET.tostring(tei, pretty_print=True, encoding="utf-8"))
        return tei

    def get_fe_werk_signatur(self):
        r = requests.get(
            f"{FRD_WORK_SIGNATUR_EP}{self.werk_signatur_hash}",
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result['data']['attributes']['name']

    def get_fields_any(self, field_type):
        """requests manifestation 'relationships' fields

        :param field_type: takes a string refering to the correct field e.g. 'field_published_in'

        :return: json
        """
        if self.manifestation['data']['relationships'][field_type]['data'] is not None:
            try:
                item = self.manifestation['data']['relationships'][field_type]['data']
                item_id = item['id']
                node_type = item['type'].split('--')[1]
                taxonomy = item['type'].split('--')[0]
                url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
                r = requests.get(
                    url,
                    cookies=self.cookie,
                    allow_redirects=True
                )
                result = r.json()
                return result
            except KeyError or TypeError:
                print(f"{field_type} is null")
        else:
            return

    def get_fields_any_any(self, field_type, get_fields):
        """requests manifestation 'relationships' fields

        :param field_type: takes a string refering to the correct field e.g. 'field_published_in'

        :return: json
        """
        if get_fields is not None:
            try:
                field_any = get_fields
                item = field_any['data']['relationships'][field_type]['data']
                if type(item) is list:
                    result = []
                    for x in item:
                        item_id = x['id']
                        node_type = x['type'].split('--')[1]
                        taxonomy = x['type'].split('--')[0]
                        url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
                        r = requests.get(
                            url,
                            cookies=self.cookie,
                            allow_redirects=True
                        )
                        res = r.json()
                        result.append(res)
                else:
                    item_id = item['id']
                    node_type = item['type'].split('--')[1]
                    taxonomy = item['type'].split('--')[0]
                    url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
                    r = requests.get(
                        url,
                        cookies=self.cookie,
                        allow_redirects=True
                    )
                    result = r.json()
                return result
            except KeyError or TypeError:
                print(f"{field_type} is null")
        else:
            return

    def __init__(
        self,
        manifestation_id=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.manifestation_id = manifestation_id
        self.manifestation_endpoint = f"{self.endpoint}node/manifestation/{manifestation_id}"
        self.manifestation = self.get_manifest()
        self.werk = self.manifestation['included'][0]
        try:
            self.publication = self.get_fields_any('field_published_in')
        except TypeError or KeyError:
            self.publication = self.manifestation_id
        try:
            self.author = self.get_fields_any('field_authors')
        except TypeError or KeyError:
            self.author = "Freud, Sigmund"
        try:
            self.publisher = self.get_fields_any_any('field_publisher', self.publication)
        except TypeError or KeyError:
            self.publisher = None
        try:
            self.herausgeber = self.get_fields_any_any('field_herausgeber', self.publication)
        except TypeError or KeyError:
            self.herausgeber = None
        try:
            self.pub_author = self.get_fields_any_any('field_authors', self.publication)
        except TypeError or KeyError:
            self.pub_author = None
        self.werk_folder = self.werk['attributes']['path']['alias']
        # self.manifestation_folder = self.manifestation['attributes']['path']['alias']
        self.man_attrib = self.manifestation['data']['attributes']
        for x in self.man_attrib.keys():
            value = self.man_attrib[x]
            if isinstance(value, dict):
                for y in value.keys():
                    dict_key = f"{x}__{y}"
                    setattr(self, f"md__{dict_key}", value[y])
            else:
                setattr(self, f"md__{x}", value)
        self.meta_attributes = [x for x in dir(self) if x.startswith('md__')]
        self.pages = self.get_pages()
        self.page_count = len(self.pages)
        self.save_dir = os.path.join(self.out_dir)
        self.werk_signatur_hash = self.werk['relationships']['field_signatur_sfe']['data']['id']
        self.werk_signatur = self.get_fe_werk_signatur()
        self.manifestation_signatur = f"{self.werk_signatur}{self.man_attrib['field_signatur_sfe_type']}"
        self.file_name = f"sfe-{self.manifestation_signatur.replace('/', '__').replace('.', '_')}.xml"
        self.save_path = os.path.join(
            self.save_dir, self.werk_signatur, self.file_name
        )


def yield_works(url, simple=True):
    """ yields basic metadata from works

        :param url: The API-endpoint
        :param type: string

        :param simple: If True a processed dict is returned, otherwise the full data object
        :param type: bool

        :return: Yields a dict
        """
    next_page = True
    while next_page:
        print(url)
        response = None
        result = None
        x = None
        time.sleep(1)
        response = requests.get(
            url,
            cookies=AUTH_ITEMS['cookie'],
            allow_redirects=True
        )
        result = response.json()
        links = result['links']
        if links.get('next', False):
            orig_url = links['next']['href']
            url = always_https(orig_url)
        else:
            next_page = False
        for x in result['data']:
            if simple:
                yield x
            else:
                item = {}
                item['id'] = x['id']
                item['title'] = x['attributes']['title']
                item['nid'] = x['attributes']['drupal_internal__nid']
                item['vid'] = x['attributes']['drupal_internal__vid']
                item['path'] = x['attributes']['path']['alias']
                item['umschrift'] = x['attributes']['field_status_umschrift']
                yield item
