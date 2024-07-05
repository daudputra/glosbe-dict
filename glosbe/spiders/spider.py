import os
import csv
import random
from datetime import datetime
from fake_useragent import UserAgent
from typing import Iterable
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings
from .utils.langcode import LanguageCode
from .utils.savev2 import save_json
from .utils.logger import setup_logger, log_warning, log_error, log_info
from .utils.token import upload_to_s3



class GlosbeSpider(Spider):
    name = 'glosbe'
    allowed_domains = ['id.glosbe.com']
    start_urls = ['https://id.glosbe.com/']
    handle_httpstatus_list = [404, 302]

    def __init__(self, *args, **kwargs):
        super(GlosbeSpider, self).__init__(*args, **kwargs)
        self.data_dict = {}
        setup_logger()

    def start_requests(self) -> Iterable[Request]:
        # settings = get_project_settings()
        # user_agents = settings.get('FAKEUSERAGENT_PROVIDERS', [])
        # header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
        ua = UserAgent()
        header = {'User-Agent': ua.random}

        csv_folder = 'list'
        csv_files = ['bbc.csv', 'mad.csv', 'ban.csv', 'bjn.csv', 'bug.csv', 'sda.csv', 'tvo.csv', 'bhw.csv', 'lbw.csv', 'kge.csv', 'bts.csv']
        for csv_file in csv_files:
            log_info(f'read data from {csv_file}')
            csv_path = os.path.join(csv_folder, csv_file)
            with open(csv_path, newline='') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in csvreader:
                    kata = row[0]
                    no = int(row[1])
                    bahasa = row[2]
                    prov = row[3]
                    lang = LanguageCode(bahasa)

                    # user_agent = random.choice(user_agents)
                    # header = {'User-Agent': user_agent}

                    url = f'{self.start_urls[0]}id/{lang}/{kata}'
                    yield Request(url, callback=self.parse, headers=header, meta={
                        'header' : header,
                        'no' : no,
                        'bahasa' : bahasa,
                        'prov' : prov,
                        'lang' : lang,
                        'kata' : kata
                    })  

    def parse(self, response):
        status_code = response.status
        kata = response.meta['kata']
        bahasa = response.meta['bahasa']
        prov = response.meta['prov']
        try:
            if status_code == 200:
                # header = response.meta['header']
                ua = UserAgent()
                header = {'User-Agent': ua.random}
                # log_info(f'user agent => {header}')
                no = response.meta['no']
                lang = response.meta['lang']
                desc_raw = response.css('#content-summary > span *::text').getall()
                desc = ' '.join(desc_raw).strip()
                tl_rows = response.xpath('/html/body/div[1]/div/div[2]/main/article/div/div[1]/section[1]/div[2]/div/ul/li')
                tl_list = []

                log_info(f'get data from kata => {kata} - {bahasa} - {prov} - {status_code}')

                for row in tl_rows:
                    tl_text = row.xpath('.//div[2]/div[1]/div/h3//text()').get()
                    if tl_text:
                        tl_text = tl_text.strip()
                    tl_list.append(tl_text)

                

                filename = f'{kata}.json'
                local_path = f'D:/Visual Studio Code/Work/magang/glosbe/glosbe/data/{bahasa.replace(' ','_').lower()}/{filename}'
                s3_path = f's3://ai-pipeline-raw-data/data/data_descriptive/data_kamus/{prov.replace(' ','_').lower()}/{bahasa.replace(' ','_').lower()}/glosbe/json/{filename}'
                full_data = {
                    'link' : response.url,
                    'domain' : response.url.split('/')[2],
                    'tag' : [
                        response.url.split('/')[2],
                        prov,
                        bahasa
                    ],
                    'crawling_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'crawling_time_epoch' : int(datetime.now().timestamp()),
                    'path_data_raw' : s3_path,
                    'path_data_clean' : None,
                    'provinsi' : prov,
                    'nama_bahasa' : bahasa,
                    'kata' : kata,
                    'data': {
                        'kata' : kata,
                        'terjemahan' : tl_list,
                        'deskripsi' : desc,
                        'contoh_teks_terjemahan' : []
                    },
                }
                save_json(full_data, bahasa.replace(' ', '_').lower(), filename)
                try:
                    upload_to_s3(local_path, s3_path.replace('s3://','')) 
                except Exception as e:
                    log_error(f'error upload s3 => {e}')


                max = 10
                for index in range(1, max + 1):
                    desc_raw = response.css('#content-summary > span *::text').getall()
                    desc = ' '.join(desc_raw).strip()
                    text_ex = f'{response.url}/fragment/tmem?page={index}&mode=MUST&stem=false'
                    yield Request(text_ex, callback=self.getExampleText, headers=header, meta={
                        'kata': kata,
                        'no' : no,
                        'bahasa' : bahasa,
                        'prov' : prov,
                        'lang' : lang,
                        'desc' : desc,
                        'tl_list' : tl_list
                    })
            elif status_code == 302:
                log_error(f'Kata => {kata} - {bahasa} - {prov} menghasilkan 302, click manual CAPTCHA')
                raise CloseSpider(f'Redirected with status 302 => Kata => {kata} - {bahasa} - {prov}')
            elif status_code == 404:
                log_warning(f'Kata => {kata} dari {bahasa} - {prov} tidak ditemukan {status_code}')
            else:
                log_error(f'Error pada kata => {kata} data tidak terambil')
        except Exception as e:
            log_error(f'error pada kata {kata} => {e}')


    def getExampleText(self, response): 
        kata = response.meta['kata']
        no = response.meta['no']
        bahasa = response.meta['bahasa']
        prov = response.meta['prov']
        if response.status == 200:
            lang = response.meta['lang']
            desc = response.meta['desc']
            tl_list = response.meta['tl_list']

            r = f'{self.start_urls[0]}id/{lang}/{kata}'

            rows = response.xpath('/html/body/div[2]/div/div[1]')
            for row in rows:
                kata_text1_raw = row.xpath('.//div[1]//text()').getall()
                kata_text2_raw = row.xpath('.//div[2]//text()').getall()

                kata_text1 = ' '.join(kata_text1_raw).strip()
                kata_text2 = ' '.join(kata_text2_raw).strip()

                dict_exs = {
                    'teks' : kata_text1,
                    'terjemahan' : kata_text2,
                }

                if kata not in self.data_dict:
                    self.data_dict[kata] = []

                self.data_dict[kata].append(dict_exs)


            # for kata, data_list in self.data_dict.items():
                filename = f'{kata}.json'
                local_path = f'D:/Visual Studio Code/Work/magang/glosbe/glosbe/data/{bahasa.replace(' ','_').lower()}/{filename}'
                s3_path = f's3://ai-pipeline-raw-data/data/data_descriptive/data_kamus/{prov.replace(' ','_').lower()}/{bahasa.replace(' ','_').lower()}/glosbe/json/{filename}'
                full_data = {
                    'link' : r,
                    'domain' : r.split('/')[2],
                    'tag' : [
                        r.split('/')[2],
                        prov,
                        bahasa
                    ],
                    'crawling_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'crawling_time_epoch' : int(datetime.now().timestamp()),
                    'path_data_raw' : s3_path,
                    'path_data_clean' : None,
                    'provinsi' : prov,
                    'nama_bahasa' : bahasa,
                    'kata' : kata,
                    'data': {
                        'kata' : kata,
                        'terjemahan' : tl_list,
                        'deskripsi' : desc,
                        'contoh_teks_terjemahan' : self.data_dict[kata]
                    },
                }
                save_json(full_data, bahasa.replace(' ', '_').lower(), filename)
                try:
                    upload_to_s3(local_path, s3_path.replace('s3://','')) 
                except Exception as e:
                    log_error(f'error upload s3 => {e}')
        elif response.status == 302:
                log_error(f'fragmen kata => {kata} - {bahasa} - {prov} menghasilkan 302, click manual CAPTCHA')
                raise CloseSpider(f'Redirected with status 302 => Fragmen Kata => {kata} - {bahasa} - {prov}')
        else:
                log_error(f'Error pada Fragmen kata => {kata} data fragmen tidak terambil')