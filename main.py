# -*- coding: utf-8 -*-
"""
ELEVATTESTER

Dette programmet genererer automatisk attester for elever.

MERKNAD: Antar at elever ikke møter opp på flere grupper i uken.

Created February 2017, Tommy O.
"""

# Imports
import subprocess, string, time, collections, os, datetime, shutil
import mechanicalsoup

# Constants -- the user may change these
USERNAME = r'email'
PASSWORD = r'password'
MIN_OPPMOTER = 8
MIN_PROSENT = 80
WEEKS = collections.defaultdict(lambda : None)
WEEKS[2016] = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
WEEKS[2017] = [4, 5, 6, 7]

def attest(oppmoter, prosent):
    """
    Endre denne funksjonen.
    Antall oppmøter er totalt antall ganger elever har møtt opp.
    Prosent er prosent av ukene etter første uke som eleven møtte.
    """
    if (oppmoter > MIN_OPPMOTER) and (prosent >= MIN_PROSENT):
        return True
    return False

# Constants -- do not change unless you know what you're doing
this_dir, _ = os.path.split(__file__)
TEMPLATE_FILE = os.path.join(this_dir, r'template\attest_template.tex')
TEMP_PATH = os.path.join(this_dir, r'temp') 
GENERATED_PATH = os.path.join(this_dir, r'generated')

def login(browser):
    """
    Logs in, returns the index page.
    """

    login_page = browser.get('http://reg.ent3r.no/elever')
    login_form = login_page.soup.find('form')

    login_form.select("#name")[0]['value'] = USERNAME
    login_form.select("#password")[0]['value'] = PASSWORD
    page = browser.submit(login_form, login_page.url)
    time.sleep(1)
    return page


def yield_elev_urls(browser):
    """
    Yield all elev urls.
    """
    page = browser.get('http://reg.ent3r.no/eleverraw')
    for tr in page.soup.find_all('tr'):
        yield 'http://reg.ent3r.no/elev/{}'.format(tr.td.text)


def get_name_oppmoter(elev_page_url):
    """
    Get oppmøter in format: name, [(2016, 37), ...]
    """
    elev_page = browser.get(elev_page_url)
    title = elev_page.soup.title.text
    tds = list(elev_page.soup.find_all('td'))
    
    for i, td in enumerate(tds):
        if 'Oppmøtehistorikk' in td.text:
            start = i + 1
            break
        
    oppmoter = []
    for i, tr in enumerate(tds[start].find_all('tr')):
        # Skip the header
        if i == 0:
            continue
        
        tds = list(tr.find_all('td'))
        week, year = tds[1].text, tds[2].text
        oppmoter.append((int(week), int(year)))
    return title[16:], oppmoter


def total_oppmoter(global_dict, elev_oppmoter):
    """
    Count total number of oppmøter.
    """
    counter = 0
    for (week, year) in elev_oppmoter:
        if global_dict[year] is None:
            continue
        if week in global_dict[year]:
            counter += 1
    return counter


def oppmoter_mulige(global_dict, elev_oppmoter):
    """
    Returns the percentage of possible since first oppmøte.
    """
    possible = 0
    started = False

    first_week, first_year = elev_oppmoter[0]

    for year, weeks in global_dict.items():
        for week in weeks:

            if (week >= first_week) and (year >=first_year):
                started = True
            if started:
                possible += 1
    return len(set(elev_oppmoter)), possible


def prettify_name(name):
    for delim in [' ']:
        name = delim.join(w.capitalize() for w in name.split(delim))
    return name


def filename(name):
    today = datetime.datetime.today()
    date_str = '_'.join([str(i) for i in [today.year, today.month, today.day]]) + '_'
    name = name.strip().lower()
    new = ''
    for char in name:
        if char in string.ascii_lowercase:
            new += char
        if char == ' ':
            new += '_'
        
    return 'attest_' + new + '_' + str(date_str)


def files_in_dir(path):
    """
    Returns a list of FILES in a directory.
    
    Does not include sub-directories.
    """
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def get_file_exension(string):
    """
    Returns the file extension.
    
    get_file_exension('new.document.txt')
    
    will return 'txt'
    """

    for index, char in enumerate(reversed(string)):
        if char == '.':
            break

    return string[-index:]


def delete_files_by_extension(path, extensions, recursive=False):
    """
    Recursively deletes all files if their extensions are given.
    """

    extensions = list(extensions)
    deleted_count = 0

    # Delete recursively
    if recursive:
        # Walk the path
        for root, dirs, files in os.walk(path):
            for file in files:
                if get_file_exension(file) in extensions:

                    file_path = os.path.join(root,file)
                    try:
                        os.remove(file_path)
                    except PermissionError as e:
                        print('ERROR:', e)
                    deleted_count += 1

    # Not do go recursively into folder structure
    # when looking for files
    else:
        for file in files_in_dir(path):
            if get_file_exension(file) in extensions:

                file_path = os.path.join(path,file)
                try:
                    os.remove(file_path)
                except PermissionError as e:
                    print('ERROR:', e)
                deleted_count += 1

    return deleted_count
    

def generate_attest(name):
    
    # Prettyify the name
    name = prettify_name(name)
    pdf_name = filename(name)
    
    # Open and read the template file
    tex_markup_file = open(TEMPLATE_FILE, 'r', encoding = 'utf-8')
    tex_markup = ''.join(l for l in tex_markup_file)
    tex_markup_file.close()
    
    # Change the template file copy
    tex_markup = tex_markup.replace('INSERTNAMEHERE', name)
    tex_markup = tex_markup.replace('INSERTDOTSHERE', '- '*int(len(name)*0.7 + 2))
    
    # Write a new .tex file
    tex_out_path = os.path.join(TEMP_PATH, '{}.tex'.format(pdf_name))
    tex_out_file = open(tex_out_path, 'w', encoding = 'utf-8')
    tex_out_file.write(tex_markup)
    tex_out_file.close()
    
    # Change directory, run latex, delete files
    os.chdir(TEMP_PATH)    
    args = ['pdflatex.exe','-synctex=1','-interaction=nonstopmode','"{}".tex'.format(pdf_name)]
    subprocess.check_call(args, cwd=TEMP_PATH, stdout=subprocess.DEVNULL)

    # Move the generated .pdf file
    before = os.path.join(TEMP_PATH, '{}.pdf'.format(pdf_name))
    after = os.path.join(GENERATED_PATH, '{}.pdf'.format(pdf_name))
    shutil.move(before, after)
    

if __name__ == '__main__':
    # Create a browser and log in
    browser = mechanicalsoup.Browser()
    login(browser)
    
    # Go through students
    for url in yield_elev_urls(browser):
        name, oppmoter = get_name_oppmoter(url)

        # Skip if no oppmøter
        if len(oppmoter) < 1:
            continue

        oppmoter_tot, mulige = oppmoter_mulige(WEEKS, oppmoter)
        prosent = round((oppmoter_tot/mulige)*100)
    
        if attest(oppmoter_tot, prosent):
            print(name , 'får attest!')
            generate_attest(name)
            

            
    





