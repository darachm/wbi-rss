import marimo

__generated_with = "0.8.22"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __():
    import bs4
    import os
    import json
    import podgen
    import datetime
    return bs4, datetime, json, os, podgen


@app.cell
def __(bs4, os):
    article_list = []
    for each_f in os.listdir('wbi-pages/'):
        with open('wbi-pages/'+each_f,'r') as f:
            article_list.extend(
                    bs4.BeautifulSoup(f,features='html.parser').find_all('article')
                    )
    return article_list, each_f, f


@app.cell
def __():
    def parseWBIepisode(obj):
        title_obj = obj.find(attrs={'data-content-field':'title'})
        time = obj.find('time')
        audio = obj.find(class_='audio-block').find(class_='sqs-audio-embed')
        desc = obj.find(class_='sqs-block-html').find(class_='sqs-html-content').find_all('p')
        return { #'title': title_obj.a.contents[0],
                'episode-page-url': title_obj.a['href'],
                'date': time['datetime'],
                'author': audio['data-author'],
                'duration-seconds': str(int(audio['data-duration-in-ms'])/1000),
                'url': audio['data-url'],
                'title': audio['data-title'],
                'description': "\n".join(map(lambda x: str(x), desc)),
                'links': ( #json.dumps( 
                            sum([ 
                                [ q for q in x ]
                                for x in list(map(
                                        lambda y: list(map( 
                                                lambda z: (z.contents[0], z['href']), 
                                                y.find_all('a')
                                                )) ,
                                        desc))
                                if x != [] and "email-protection" not in x[0][1]
                                ],[]) 
                            )
                }

    # for testing/dev
    #for k,v in parseWBIepisode(article_list[0]).items():
    #    print(k,v)
    return (parseWBIepisode,)


@app.cell
def __(article_list, parseWBIepisode):
    parsed_episodes = list(map(parseWBIepisode,article_list))
    return (parsed_episodes,)


@app.cell
def __(datetime, parsed_episodes, podgen):
    podcast = podgen.Podcast(
            name='We Be Imagining',
            description='''
                The We Be Imagining Podcast examines the intersection of race, 
                tech, surveillance, gender and disability in the COVID-19 era.
                But they let their RSS feed languish into link-rot as far as I
                can find, so I scraped this together from the pages on 
                "The American Assembly" website. Bon appetite.
                ''',
            website='https://americanassembly.org/wbi-podcast',
            explicit=False ) #te he he
    podcast.episodes = map( lambda x: 
                    podgen.Episode(
                            title=x['title'],
                            long_summary=x['description'],
                            link=x['episode-page-url'],
                            publication_date=datetime.datetime.strptime(x['date']+' -0400','%Y-%m-%d %z'),
                            media=podgen.Media(
                                    url=x['url'],
                                    duration=datetime.timedelta(seconds=float(x['duration-seconds']))
                                    )
                            ), 
                parsed_episodes )
    return (podcast,)


@app.cell
def __(podcast):
    with open('wbi.rss','w') as fz:
        fz.write(podcast.rss_str())
    return (fz,)


if __name__ == "__main__":
    app.run()
