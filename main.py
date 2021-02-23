from pymed import pymed as pm
import matplotlib.pyplot as plt
import numpy as np


def retrieve_all_records():
    # setup search
    client = 'foo@bar.com'
    term = '"Neuron"[Journal]'
    # pubmed_fields = 'all'  # default
    chunksize = 5000

    # get records
    results = pm.query_records(term=term, client=client,
                            chunksize=chunksize)
    results.save('data/results.json')


def load_records(filename='data/results.json'):
    import json
    return json.load(open(filename, 'r'))


def load_countries(filename='data/countries'):
    return [s.lower().replace('\n', '') for s in open(filename, 'r').readlines()]


def load_states(filename='data/states'):
    return [s.lower().replace('\n', '') for s in open(filename, 'r').readlines()]


def parse_corresponding_authors_country(countries, states, records):

    data = {}

    icountry = 0
    istate = 0
    total = len(records)

    error = 0

    for r in records:
        try:
            del d
        except:
            pass
        date = int(r['DP'][:4])
        if date not in data:
            data[date] = {}

        if 'Review' in r['PT']:
            art_type = 'Review'
        elif 'Journal Article' in r['PT']:
            art_type = 'Journal Article'
        else:
            art_type = r['PT'][0]

        if art_type not in data:
            data[date][art_type] = {}

        d = {}

        if r.get('AD'):

            found = False

            # Clean affiliations
            for j in (0, 1):

                if not found:
                    try:
                        ad1 = r['AD'].lower().split('.')[j]
                        ad2 = ad1.split(';')[0].split(',')
                        ad = []
                        for s in ad2:
                            ad.append(''.join(c for c in s if not c.isdigit()))

                        # Country should be here
                        country = ad[-1].replace(' ', '')

                        for c in countries:
                            if c == country:
                                if c == 'united states':
                                    c = 'usa'

                                if c in d:
                                    d[c] += 1
                                else:
                                    d[c] = 1
                                icountry += 1
                                found = True
                                break

                        # If country is not found, look for a state
                        if not found:
                            for s in states:
                                if s in ''.join(ad):
                                    if 'usa' in d:
                                        d['usa'] += 1
                                    else:
                                        d['usa'] = 1
                                    istate += 1
                                    found = True
                                    break
                    except:
                        error += 1
                        pass
        data[date][art_type] = d.copy()
    return data, icountry, istate, total, error


def plot_by_article_type(data):
    # import libraries
    import pandas as pd
    import matplotlib.pyplot as plt

    # set font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Helvetica'

    # set the style of the axes and the text color
    plt.rcParams['axes.edgecolor'] = '#333F4B'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['xtick.color'] = '#333F4B'
    plt.rcParams['ytick.color'] = '#333F4B'
    plt.rcParams['text.color'] = '#333F4B'

    new = {}
    for k in data.keys():
        new[k] = sum(data[k].values())
    data = new
    d = sorted(data.items())
    per = [j for i, j in d]
    count = [i for i, j in d]

    count = pd.Series([p/sum(per)*100 for p in per], index=count)
    df = pd.DataFrame({'count': count})
    df = df.sort_values(by='count')

    # we first need a numeric placeholder for the y axis
    my_range = list(range(1, len(df.index) + 1))

    fig, ax = plt.subplots()
    fig.set_size_inches(19, 12)

    # create for each expense type an horizontal line that starts at x = 0 with the length
    # represented by the specific expense percentage value.
    plt.hlines(y=my_range, xmin=0, xmax=df['count'], color='#007ACC', alpha=0.4, linewidth=7)

    # create for each expense type a dot at the level of the expense percentage value
    dots = plt.plot(df['count'], my_range, "o", markersize=9, color='#007ACC', alpha=0.9)

    for x, y in zip(df['count'][::-1], my_range[::-1]):
        # xytext and textcoords are used to offset the labels
        ax.annotate("{:.2f} %".format(x), xy=(x+1, y-.2), color='#007ACC', weight='bold')#, xytext=(5, 5))# textcoords='offset')
    # set labels
    ax.set_xlabel('Percentage', fontsize=15, fontweight='black', color='#333F4B')
    ax.set_ylabel('Publication type')
    plt.title(f'Publications retrieved from Neuron N={sum(per)}')

    # set axis
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.yticks(my_range, df.index)
    # plt.xlim([0, 100])

    # add an horizonal label for the y axis
    fig.text(-0.23, 0.96, 'Publication type', fontsize=5, fontweight='black', color='#333F4B')

    # change the style of the axis spines
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    #ax.spines['bottom'].set_visible(0)
    #ax.get_xaxis().set_visible(False)

    # set the spines position
    ax.spines['bottom'].set_position(('axes', -0.04))
    ax.spines['left'].set_position(('axes', 0.015))
    # plt.xlim([0, 100])
    plt.savefig('fig/' + 'by_articletype'.replace(' ', '_').lower() + '.pdf')


def plot_by_country(data, type_art):
    # import libraries
    import pandas as pd
    import matplotlib.pyplot as plt

    # set font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Helvetica'

    # set the style of the axes and the text color
    plt.rcParams['axes.edgecolor'] = '#333F4B'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['xtick.color'] = '#333F4B'
    plt.rcParams['ytick.color'] = '#333F4B'
    plt.rcParams['text.color'] = '#333F4B'

    d = sorted(data[type_art].items())
    per = [j for i, j in d]
    count = [i for i, j in d]

    count = pd.Series([p/sum(per)*100 for p in per], index=count)
    df = pd.DataFrame({'count': count})
    df = df.sort_values(by='count')

    # we first need a numeric placeholder for the y axis
    my_range = list(range(1, len(df.index) + 1))

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 12)

    # create for each expense type an horizontal line that starts at x = 0 with the length
    # represented by the specific expense percentage value.
    plt.hlines(y=my_range, xmin=0, xmax=df['count'], color='#007ACC', alpha=0.4, linewidth=7)

    # create for each expense type a dot at the level of the expense percentage value
    dots = plt.plot(df['count'], my_range, "o", markersize=9, color='#007ACC', alpha=0.9)

    for x, y in zip(df['count'][::-1], my_range[::-1]):
        # xytext and textcoords are used to offset the labels
        ax.annotate("{:.2f} %".format(x), xy=(x+1, y-.2), color='#007ACC', weight='bold')#, xytext=(5, 5))# textcoords='offset')
    # set labels
    ax.set_xlabel('Percentage', fontsize=15, fontweight='black', color='#333F4B')
    ax.set_ylabel('Country affiliation of first author')
    plt.title(type_art + f' from Neuron N={sum(per)}')

    # set axis
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.yticks(my_range, df.index)
    # plt.xlim([0, 100])

    # add an horizonal label for the y axis
    fig.text(-0.23, 0.96, 'Country affiliation of first author', fontsize=5, fontweight='black', color='#333F4B')

    # change the style of the axis spines
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    #ax.spines['bottom'].set_visible(0)
    #ax.get_xaxis().set_visible(False)

    # set the spines position
    ax.spines['bottom'].set_position(('axes', -0.04))
    ax.spines['left'].set_position(('axes', 0.015))
    # plt.xlim([0, 100])
    plt.savefig('fig/' + type_art.replace(' ', '_').lower() + '.pdf')


def main():
    # retrieve_all_records()
    records = load_records()
    countries = load_countries()
    states = load_states()

    data, icountry, istate, total, error = parse_corresponding_authors_country(
        countries=countries, states=states, records=records)

    print(f'Number of errors while retrieving: {error}')
    print(f'Percentage of data successfully retrieved via country affiliation: {np.round((icountry/total)*100,2)}')
    print(f'Percentage of data successfully retrieved via state affiliation: {np.round((istate/total)*100,2)}')
    print(f'Percentage of errors (not retrieved affiliation): {np.round(((total - (istate+icountry))/total)*100,2)}')
    print('...')
    plot_by_country(data, 'Journal Article')
    plot_by_country(data, 'Review')

    plot_by_article_type(data)

    plt.show()


if __name__ == '__main__':
    main()