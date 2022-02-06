from scc import base_dir
from pathlib import Path
from os import listdir
from os.path import isfile, join
from datetime import datetime
import sys
from . import styles
from . import bibtext

class metadata(object):

    def __init__(self, repo_metadata, embedded = False):
        self.md = repo_metadata
        self.s = styles.styles(embedded)
        self.base = 'https://github.com/dakixr/scc/raw/main/src/scc/assets/' if embedded else ''

    # Assets ####################################################
    def logo(self):
        return f"{self.base}img/github-default.svg"

    def icon_star(self):
        return f"{self.base}repo_icons/star.png"

    def icon_releases(self):
        return f"{self.base}repo_icons/releases.png"
    
    def html_languages(self):

        languages = safe_dic(safe_dic(self.md,'languages'),'excerpt')

        if not languages:
            return ''

        language_icons_dir = Path(base_dir, 'assets', 'language_icons')
        supported_languages = [str(f).removesuffix('.svg').lower() for f in listdir(language_icons_dir) if isfile(join(language_icons_dir, f))]

        html = ''

        for lang in languages:
            lang = str(lang).lower()
            if lang in supported_languages:
                html += f"""<img src="{self.base}language_icons/{lang}.svg" alt="{lang}" {self.s.get('repo-icon')} title={lang.capitalize()}>\n"""
        
        return html

    def html_repo_icons(self):

        html = ''
    
        license = self.license()
        if license:
            html += f"""<a href="{safe_dic(license,'url')}" target="_blank" {self.s.get('repo-icon')}><img src="{self.base}repo_icons/license.png" alt="license" {self.s.get('repo-icon')} title="License: {license['name']}"></a>"""
        
        readme_url = safe_dic(safe_dic(self.md,'readme_url'),'excerpt')
        if readme_url:
            html += f"""<a href="{readme_url}" target="_blank" {self.s.get('repo-icon')}><img src="{self.base}repo_icons/readme.png" alt="readme" {self.s.get('repo-icon')} title="Readme"></a>"""
        
        notebook = safe_dic(safe_dic(self.md,'hasExecutableNotebook'),'excerpt')
        if notebook:
            html += f"""<img src="{self.base}repo_icons/notebook.png" alt="notebook" {self.s.get('repo-icon')} title="Notebook">"""

        download_url = safe_dic(safe_dic(self.md,'downloadUrl'),'excerpt')
        if download_url:
            html += f"""<a href="{download_url}" target="_blank" {self.s.get('repo-icon')}><img src="{self.base}repo_icons/download.png" alt="download" {self.s.get('repo-icon')} title="Download"></a>"""

        all_citations = safe_dic(self.md,'citation')
        if all_citations:
            citations = []
            for c in all_citations:
                if c['technique'] == 'Regular expression':
                    citations.append(c['excerpt'])
            if len(citations) > 0:
                for citation in citations:
                    html += f"""<img src="{self.base}repo_icons/citation.png" alt="citation" {self.s.get('repo-icon')} title="{citation}">"""

                    # Paper repo-icon 
                    # TODO: Consider if separating paper and citation logic makes sense
                    p_citation = bibtext.bibtext.parse(citation)[0]
                    p_citation_fields_keys = p_citation.fields.keys()

                    if 'doi' in p_citation_fields_keys and not 'url' in p_citation_fields_keys:
                        link_paper = p_citation.fields['doi'][1:-1]

                    if 'url' in p_citation_fields_keys:
                        link_paper = p_citation.fields['url'][1:-1]
                    
                    title_paper = p_citation.fields['title'][1:-1] # remove '{' and '}'
                    html += f"""<a href="{link_paper}" target="_blank" {self.s.get('repo-icon')}>
                                    <img src="{self.base}repo_icons/paper.png" 
                                         alt="{title_paper}" {self.s.get('repo-icon')} 
                                         title="Paper: {title_paper}">
                                </a>"""

        docker = safe_dic(safe_dic(self.md,'hasBuildFile'),'excerpt')
        if docker:
            html += f"""<img src="{self.base}repo_icons/docker.png" alt="docker" {self.s.get('repo-icon')} title="{[str(d) for d in docker]}">"""
        
        installation = safe_dic(self.md,'installation')
        if installation:
            installation = safe_dic(installation[0],'excerpt')
            html += f"""<img src="{self.base}repo_icons/installation.png" alt="installation" {self.s.get('repo-icon')} title="Installation:\n{installation}">"""
        
        requirements = safe_dic(self.md,'requirement')
        if requirements:
            requirements = safe_dic(requirements[0],'excerpt')
            html += f"""<img src="{self.base}repo_icons/requirements.png" alt="requirements" {self.s.get('repo-icon')} title="Requirements:\n{requirements}">"""

        return html
    
    def recently_updated(self):

        hex_states = [
            {'hex': '#6da862', 'days_threshold': 30},
            {'hex': '#a88d62', 'days_threshold': 90},
            {'hex': '#a86262', 'days_threshold': sys.maxsize}
        ]
        
        date_of_extraction_str = safe_dic(safe_dic(safe_dic(self.md,'stargazers_count'),'excerpt'),'date')[:-4]
        date_of_extraction = datetime.strptime(date_of_extraction_str, '%a, %d %b %Y %H:%M:%S') 
        delta = (date_of_extraction - self.last_update()).days

        state_updated = ''
        for state in hex_states:
            if delta < state['days_threshold']:
                state_updated = state['hex']
                break

        return f"""<div {self.s.get('recently-updated',custom_css=f'background-color: {state_updated};')} title="Last updated on: {self.last_update()}"></div>"""

    # Metadata ##################################################
    def repo_url(self):
        return safe_dic(safe_dic(self.md,'codeRepository'),'excerpt')
            
    def title(self):
        return safe_dic(safe_dic(self.md,'name'),'excerpt')
        
    def description(self):

        all_descriptions = safe_dic(self.md,'description')

        description = None
        if all_descriptions:
            for d in all_descriptions:
                if safe_dic(d,'technique') == 'GitHub API':
                    description = safe_dic(d,'excerpt')
                    break

        if not description:
            description = safe_dic(safe_list(all_descriptions,0),'excerpt')
            if not description:
                description = 'No description available yet.'
            
        return description

    def license(self):
        return safe_dic(safe_dic(self.md,'license'),'excerpt')

    def last_update(self):
        date_modified_str = safe_dic(safe_dic(self.md,'dateModified'),'excerpt')[:-1]
        date_modified = datetime.strptime(date_modified_str, '%Y-%m-%dT%H:%M:%S')

        return date_modified

    def stars(self):
        return safe_dic(safe_dic(safe_dic(self.md,'stargazers_count'),'excerpt'),'count')
    
    def n_releases(self):
        rel = safe_dic(safe_dic(self.md,'releases'),'excerpt')
        return len(rel) if rel is not None else 0
    
    def url_releases(self):
        return safe_dic(safe_dic(self.md,'downloadUrl'),'excerpt')
        
    
# Aux ##########################################################
def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None

def safe_list(list, i):
    try:
        return list[i]
    except:
        return None