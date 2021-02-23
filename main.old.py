import universities
import scholarly
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import unicodedata
import matplotlib.pyplot as plt
import pickle


def get_bs_object(url, session):
    r = session.get(url)
    r.html.render(timeout=10)
    return BeautifulSoup(
        str(r.content, 'utf8'), 'html.parser')


def load_names():
    try:
        return pickle.load(open('names.p', 'rb'))
    except FileNotFoundError:
        return None


def save_names(obj):
    print('saving names')
    pickle.dump(obj=obj, file=open('names.p', 'wb'))


def get_reviews(url, session):

    bs = get_bs_object(url, session)
    reviews = set()
    # To download the whole data set, let's do a for loop through all a tags
    for tag in bs.findAll('a'):
        link = tag['href']
        if 'issue' in link and 'http' in link:
            reviews.add(link)
    return reviews


def get_names_from_review_page(urls, session):
    names = set()
    for url in urls:
        try:
            bs = get_bs_object(url, session)
            for li in bs.findAll('li', attrs={'class': 'loa__item'}):
                names.add(
                    unicodedata.normalize('NFKD', li.contents[0].replace(',', ''))
                )
        except:
            pass
    return names


def get_universities(names):
    univ = []
    for name in names:
        try:
            search_query = list(scholarly.search_author(name))
            if search_query:
                author = search_query[0]
                if getattr(author, 'affiliation'):
                    univ.append(author.affiliation)
        except:
            pass

    return univ


def plot(x):
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.hist(x)
    plt.show()


def main():

    names = load_names()

    if names is None:
        print('Names not found')
        # Set the URL you want to webscrape from
        all_reviews_url = \
            'https://www.cell.com/neuron/libraries/special-issues'

        session = HTMLSession()
        urls = get_reviews(all_reviews_url, session)
        names = get_names_from_review_page(urls, session)
        save_names(names)

    univ = get_universities(names)
    plot(univ)


if __name__ == '__main__':
    main()

