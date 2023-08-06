import os
import json
import time
from collections import defaultdict

import requests
import lxml.etree as ET
import jinja2

from freud_api_crawler.string_utils import clean_markup, extract_page_nr, always_https, normalize_white_space

# from freud_api_crawler.tei_utils import make_pb

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
        # wrapped_body = f'<div xmlns="http://www.tei-c.org/ns/1.0" xml:id="page__{page_id}">{body}</div>'
        cleaned_body = clean_markup(body)
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

    def make_xml(self, save=False, limit=True, dump=False):

        """serializes a manifestation as XML/TEI document

        :param save: if set, a XML/TEI file `{self.save_path}` is saved
        :param type: bool

        :return: A lxml.etree
        """
        json_dump = self.get_man_json_dump(lmt=limit, dmp=dump)
        templateLoader = jinja2.PackageLoader(
            "freud_api_crawler", "templates"
        )
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template('./tei.xml')
        tei = template.render({"objects": [json_dump]})
        tei = ET.fromstring(tei)
        transform = ET.XSLT(self.xsl_doc)
        tei = transform(tei)
        if save:
            with open(self.save_path, 'wb') as f:
                f.write(ET.tostring(tei, pretty_print=True, encoding="utf-8"))
        return tei

    def get_man_json_dump(self, lmt=True, dmp=False):
        if dmp:
            json_dump = {}
            json_dump["id"] = f"manifestation__{self.manifestation_id}"
            json_dump['man_title'] = f"{self.md__title} ({self.manifestation_signatur})"
            try:
                s_title_t = self.manifestation['data']['attributes']['field_shorttitle']
                json_dump['man_shorttitle'] = s_title_t['value']
            except (KeyError, TypeError):
                print("No short title found!")
            json_dump["publication"] = {}
            try:
                json_dump["publication"]["id"] = f"bibl__{self.publication['data']['id']}"
            except (KeyError, TypeError):
                json_dump["publication"]["id"] = f"bibl__{self.manifestation_id}"
            try:
                json_dump["publication"]["title"] = self.publication['data']['attributes']['title']
            except (KeyError, TypeError):
                json_dump["publication"]["title"] = self.manifestation_id
            json_dump["work"] = {}
            json_dump["work"]["id"] = f"bibl__{self.werk['id']}"
            json_dump["work"]["title"] = self.werk['attributes']['title']
            try:
                json_dump["author"] = self.author['data']['attributes']['name']
            except (KeyError, TypeError):
                json_dump["author"] = "Freud, Sigmund"
            try:
                bibl_type = self.publication['data']['type'].replace('--', '/')
                json_dump["publication"]["id"] = f"{bibl_type}/{self.publication['data']['id']}"
            except (KeyError, TypeError):
                print("No publication ID found!")
            try:
                bibl_title_obj = self.publication['data']['attributes']['field_titel']
                json_dump["publication"]["title_main"] = bibl_title_obj['value']
            except (KeyError, TypeError):
                print("No publication main title found!")
            try:
                bibl_title_obj = self.publication['data']['attributes']['field_secondary_title']
                json_dump["publication"]["title_sub"] = bibl_title_obj['value']
            except (KeyError, TypeError):
                print("No publication secodnary title found!")
            try:
                bibl_title_obj = self.publication['data']['attributes']['field_shorttitle']
                json_dump["publication"]["title_short"] = bibl_title_obj['value']
            except (KeyError, TypeError):
                print("No publication short title found!")
            try:
                places = self.publication['data']['attributes']['field_publication_place']
                for x in places:
                    place = x["value"]
                    json_dump["publication"]["places"] = []
                    json_dump["publication"]["places"].append({"name": place})
            except (KeyError, TypeError):
                print("No publication place(s) found!")
            try:
                bibl_date_obj = self.publication['data']['attributes']['field_publication_year']
                json_dump["publication"]["date"] = bibl_date_obj
            except (KeyError, TypeError):
                print("No publication year found!")
            try:
                bibl_scope_obj = self.publication['data']['attributes']['field_band']
                json_dump["publication"]["biblScope"] = bibl_scope_obj['value']
            except (KeyError, TypeError):
                print("No publication field band found!")
            try:
                if type(self.publisher) is list:
                    for x in self.publisher:
                        pub_type = x['data']['type'].replace('--', '/')
                        json_dump["publication"]["publisher"] = []
                        json_dump["publication"]["publisher"].append(
                            {
                                "id": f"{pub_type}/{x['data']['id']}",
                                "name": f"{x['data']['attributes']['name']} (field_publisher)"
                            }
                        )
                else:
                    pub_type = self.publisher['data']['type'].replace('--', '/')
                    json_dump["publication"]["publisher"] = []
                    json_dump["publication"]["publisher"] = [
                        {
                            "id": f"{pub_type}/{self.publisher['data']['id']}",
                            "name": f"{self.publisher['data']['attributes']['name']} (field_publisher)"
                        }
                    ]
            except (KeyError, TypeError):
                print("No publication publisher found!")
            try:
                if type(self.herausgeber) is list:
                    for x in self.herausgeber:
                        pub_type = x['data']['type'].replace('--', '/')
                        json_dump["publication"]["herausgeber"] = []
                        json_dump["publication"]["herausgeber"].append(
                            {
                                "id": f"{pub_type}/{x['data']['id']}",
                                "name": f"{x['data']['attributes']['name']} (field_herausgeber)"
                            }
                        )
                else:
                    pub_type = self.herausgeber['data']['type'].replace('--', '/')
                    json_dump["publication"]["herausgeber"] = []
                    json_dump["publication"]["herausgeber"].append(
                        {
                            "id": f"{pub_type}/{self.herausgeber['data']['id']}",
                            "name": f"{self.herausgeber['data']['attributes']['name']} (field_herausgeber)"
                        }
                    )
            except (KeyError, TypeError):
                print("No publication herausgeber found!")
            try:
                if type(self.pub_author) is list:
                    for x in self.pub_author:
                        pub_type = x['data']['type'].replace('--', '/')
                        json_dump["publication"]["author"] = []
                        json_dump["publication"]["author"].append(
                            {
                                "id": f"{pub_type}/{x['data']['id']}",
                                "name": f"{x['data']['attributes']['name']} (field_authors)"
                            }
                        )
                else:
                    pub_type = self.pub_author['data']['type'].replace('--', '/')
                    json_dump["publication"]["author"] = []
                    json_dump["publication"]["author"].append(
                        {
                            "id": f"{pub_type}/{self.pub_author['data']['id']}",
                            "name": f"{self.pub_author['data']['attributes']['name']} (field_authors)"
                        }
                    )
            except (KeyError, TypeError):
                print("No publication author(s) found!")
            try:
                if type(self.pub_editors) is list:
                    for x in self.pub_editors:
                        pub_type = x['data']['type'].replace('--', '/')
                        json_dump["publication"]["editor"] = []
                        json_dump["publication"]["editor"].append(
                            {
                                "id": f"{pub_type}/{x['data']['id']}",
                                "name": f"{x['data']['attributes']['name']} (field_editors)"
                            }
                        )
                else:
                    pub_type = self.pub_editors['data']['type'].replace('--', '/')
                    json_dump["publication"]["editor"] = []
                    json_dump["publication"]["editor"].append(
                        {
                            "id": f"{pub_type}/{self.pub_editors['data']['id']}",
                            "name": f"{self.pub_editors['data']['attributes']['name']} (field_editors)"
                        }
                    )
            except (KeyError, TypeError):
                print("No publication editor(s) found!")
            try:
                msType = self.repository['data']['type']
                json_dump["repository"] = {
                    "id": f"{msType}__{self.repository['data']['id']}",
                    "name": self.repository['data']['attributes']['name']
                }
            except (KeyError, TypeError):
                print("It seems there is not 'filed_aufbewahrungsort'")
            json_dump["pages"] = []
            pages = self.pages
            if lmt:
                actual_pages = pages[:2]
            else:
                actual_pages = pages
            for x in actual_pages:
                page_json = self.get_page(x['id'])
                pp = self.process_page(page_json)
                json_dump["pages"].append(pp)
            os.makedirs(os.path.join(self.save_dir, self.werk_signatur), exist_ok=True)
            with open(self.save_path_json, 'w', encoding='utf8') as f:
                json.dump(json_dump, f)
        else:
            try:
                with open(self.save_path_json, 'r', encoding='utf8') as f:
                    json_dump = json.load(f)
            except FileNotFoundError:
                print(f"file {self.save_path_json} not found, switching dump=True and restarting")
                json_dump = self.get_man_json_dump(lmt=lmt, dmp=True)
        return json_dump

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
        try:
            item = self.manifestation['data']['relationships'][field_type]['data']
        except (KeyError, TypeError):
            print(f"looks like there is no {field_type}")
            return {}
        try:
            item_id = item['id']
        except (KeyError, TypeError):
            print(f"looks like there is not ID for {field_type}")
            return {}
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

    def get_fields_any_any(self, field_type, get_fields):
        """requests manifestation 'relationships' fields

        :param field_type: takes a string refering to the correct field e.g. 'field_published_in'

        :return: json
        """
        try:
            get_fields['data']['id']
        except (KeyError, TypeError):
            print("looks like there is no ID for get_fields")
            return {}
        try:
            item = get_fields['data']['relationships'][field_type]['data']
        except (KeyError, TypeError):
            print(f"looks like there is no {field_type}")
            return {}
        if type(item) is list:
            result = []
            for x in item:
                try:
                    item_id = x['id']
                except (KeyError, TypeError):
                    print(f"looks like there is not ID for {field_type}")
                    return {}
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
            return result
        else:
            try:
                item_id = item['id']
            except (KeyError, TypeError):
                print(f"looks like there is not ID for {field_type}")
                return {}
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
        self.publication = self.get_fields_any('field_published_in')
        self.author = self.get_fields_any('field_authors')
        self.repository = self.get_fields_any('field_aufbewahrungsort')
        self.publisher = self.get_fields_any_any('field_publisher', self.publication)
        self.herausgeber = self.get_fields_any_any('field_herausgeber', self.publication)
        self.pub_author = self.get_fields_any_any('field_authors', self.publication)
        self.pub_editors = self.get_fields_any_any('field_editors', self.publication)
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
        self.file_name_json = f"sfe-{self.manifestation_signatur.replace('/', '__').replace('.', '_')}.json"
        self.save_path = os.path.join(
            self.save_dir, self.werk_signatur, self.file_name
        )
        self.save_path_json = os.path.join(
            self.save_dir, self.werk_signatur, self.file_name_json
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
