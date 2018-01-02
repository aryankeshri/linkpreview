"""
    Created on 03/jan/2018
    
    @author: Aryan Keshri
    
    link_preview is now a fashionable way of sharing links
    in social media. The contents of what the preview is 
    made up are:-
        1. og.title:-
            Title of the preview. 
            In HTML: <meta property="og.title" content="XYZ">
            Value: XYZ
            
        2. og.description:-
            Description of the preview.
            In HTML: <meta property="og.description" content="XYZ">
            Value: XYZ
            
        3. og.image:-
            Image of the preview.
            In HTML: <meta property="og.image" content="XYZ">
            Value: XYZ
            
        4. title:-
            if 'og:title' is not found, this becomes the Title.
            In HTML: <title>XYZ</title>
            Value: XYZ
            
        5. meta description:-
            if 'og:description' is not found, this becomes the Description.
            In HTML: <meta name="description" content="XYZ">
            Value: XYZ
            
        6. favicon:-
            if 'og:image' is not found, this becomes the Image.
            In HTML: <link rel="shortcut icon" href="XYZ" type="image/x-icon">
            Value: XYZ
            
        7. website:-
            Host website for the link.
            
    Reference:- https://richpreview.com/ (from where I learned)
    
    This module fetches all these data and combines those into 
    a dictionary.
    
    A sample WhatsApp link_preview:
    
        #######################################
        #   I    #    Title                   #
        #   M    #    Description             #
        #   A    #                            #
        #   G    #    website                 #
        #   E    #                            #
        #######################################
    
    Usage:-
    x = LinkPreview('https://timesofindia.indiatimes.com/videos/one-min-news/January/Jan-2-2018/video-news-all-in-one-minute-6pm/videoshow/62339165.cms?utm_source=browser_notification&utm_medium=chrome&utm_campaign=TOI_browsernotification').generate_dict()
    returns
            {
                    'description': 'Video news: All in one minute @ 6pm.Times Now is the first channel to reach the encounter site inside CRPF&rsquo;s Lethpora training center. Five jawans were martyred and three terrorists were neutralised during the encounter.',
                    'image': 'https://timesofindia.indiatimes.com/photo/62339165.cms',
                    'title': 'Video news: All in one minute @ 6pm | - Times of India Videos'
                    'website': 'timesofindia.indiatimes.com'
                     }
"""

import urllib.request as req
import re


class LinkPreview(object):

    def __init__(self, url):
        self.url = url
        self.return_dict = {}

    @classmethod
    def return_og(self, elem):
        """
        returns content of og_elements
        :param elem:
        :return:
        """
        content = re.findall('content[\s]*=[\s]*"[^<>"]+"', elem)[0]
        p = re.findall('"[^<>]+"', content)[0][1:-1]
        if 'og:title' in elem:
            return "og.title", p
        elif 'og:image' in elem and 'og:image:' not in elem:
            return "og.image", p
        elif 'og:description' in elem:
            return "og.description", p

    def find_title(self, html):
        '''
            returns the <title> of html
        '''
        try:
            title_elem = re.findall('<[\s]*title[\s]*>[^<>]+<[\s]*/[\s]*title[\s]*>', html)[0]
            title = re.findall('>[^<>]+<', title_elem)[0][1:-1]
        except:
            title = ''
        return title

    def find_meta_desc(self, html):
        '''
            returns the description (<meta name="description") of html
        '''
        try:
            meta_elem = re.findall('<[\s]*meta[^<>]+name[\s]*=[\s]*"[\s]*description[\s]*"[^<>]*>', html)[0]
            content = re.findall('content[\s]*=[\s]*"[^<>"]+"', meta_elem)[0]
            description = re.findall('"[^<>]+"', content)[0][1:-1]
        except:
            description = ''
        return description

    def find_image(self, html):
        '''
            returns the favicon of html
        '''
        try:
            favicon_elem = re.findall('<[\s]*link[^<>]+rel[\s]*=[\s]*"[\s]*shortcut icon[\s]*"[^<>]*>', html)[0]
            href = re.findall('href[\s]*=[\s]*"[^<>"]+"', favicon_elem)[0]
            image = re.findall('"[^<>]+"', href)[0][1:-1]
        except:
            image = ''
        return image

    def find_host_website(self, url):
        '''
            returns host website from the url
        '''
        return list(filter(lambda x: '.' in x, url.split('/')))[0]

    def generate_dict(self):
        '''
            returns dictionary containing elements of link_preview:
                dict_keys :
                    'title' : '',
                    'description': '',
                    'image': '',
                    'website': ''
            if Exception occurs, it raises Exception of urllib.request module.
        '''
        try:
            html = req.urlopen(self.url).read().decode('utf-8')
            meta_elems = re.findall('<[\s]*meta[^<>]+og:(?:title|image|description)(?!:)[^<>]+>', html)
            og_map = map(self.return_og, meta_elems)
            og_dict = dict(list(og_map))

        #     title
            try:
                self.return_dict['title'] = og_dict['og.title']
            except KeyError:
                self.return_dict['title'] = self.find_title(html)

        #     description
            try:
                self.return_dict['description'] = og_dict['og.description']
            except KeyError:
                self.return_dict['description'] = self.find_meta_desc(html)

        #     website
            self.return_dict['website'] = self.find_host_website(self.url)

        #     Image
            try:
                self.return_dict['image'] = og_dict['og.image']
            except KeyError:
                image_path = self.find_image(html)
                if 'http' not in image_path:
                    image_path = 'http://' + self.return_dict['website'] + image_path
                    self.return_dict['image'] = image_path

            return self.return_dict

        except Exception as e:
            'Raises Occurred Exception'
            raise e
