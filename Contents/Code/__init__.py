DEBUG = True

PREFIX = '/video/big12sports'
NAME = "Big 12 Sports"

ART = R('art-default.png')
ICON = R('icon-default.png')

ROOT = "http://m.big12sports.com"
URL = ROOT + "/mobile/Video.dbml?db_oem_id=10410"

TEAM_URL = ROOT + "/mediaPortal/4/programlist.dbml?db_oem_id=10410&cid=34621&tag="

MAXRESULTS = 20

TEAMS = {
    'baylor': 'Baylor',
    'iowa-state': 'Iowa State',
    'kansas': 'Kansas',
    'kansas-state': 'Kansas State',
    'oklahoma': 'Oklahoma',
    'oklahoma-state': 'Oklahoma State',
    'tcu': 'TCU',
    'texas': 'Texas',
    'texas-tech': 'Texas Tech',
    'west-virginia': 'West Virginia',
}


SPORTS = {
    "13139": "Football",
    "13134": "Men's Basketball",
    "13131": "Baseball",
    "13136": "Soccer",
    "13135": "Women's Basketball",
    "13213": "Cross Country",
    "92795": "Equestrian",
    "13217": "Golf",
    "13156": "Gymnastics",
    "92796": "Rowing",
    "13137": "Softball",
    "13128": "Swimming & Diving",
    "13126": "Men's Tennis",
    "13132": "Women's Tennis",
    "13212": "Track & Field",
    "13133": "Volleyball",
    "13153": "Wrestling"
}

####################################################################################################
def Start():

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    # Set the default ObjectContainer attributes
    ObjectContainer.title1 = NAME
    ObjectContainer.art = ART
    ObjectContainer.view_group = "List"

    DirectoryObject.thumb = ICON
    VideoClipObject.thumb = ICON

    # Set the default cache time
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3"


####################################################################################################
@handler(PREFIX, "Big 12 Sports")
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(ListTeams), title='Teams'))
    oc.add(DirectoryObject(key=Callback(ListSports), title='Sports'))

    return oc


####################################################################################################
@route(PREFIX + '/list-teams')
def ListTeams():

    oc = ObjectContainer(title1="Teams")

    for team in TEAMS:
        oc.add(DirectoryObject(key=Callback(ListTeamVideos, team=team), title=TEAMS[team]))

    return oc


####################################################################################################
@route(PREFIX + '/list-team-videos')
def ListTeamVideos(team, page="1"):

    page_url = TEAM_URL + team
    log("Retrieving %s" % page_url)

    page = int(page)
    oc = ObjectContainer(title1=TEAMS[team], replace_parent=(page > 1))

    src = HTML.ElementFromURL(page_url)
    items = src.xpath("//ul[@class='programlist']/li")

    for item in items:

        thumb = item.xpath(".//img/@src")[0]
        div = item.xpath(".//div[@class='media-item-desc']")[0]
        title = div.text
        id = div.get("id")
        url = URL + "&ID=" + id

        oc.add(VideoClipObject(
            url=url,
            title=title,
            thumb=thumb
        ))

    return oc


####################################################################################################
@route(PREFIX + '/list-sports')
def ListSports():

    oc = ObjectContainer()

    for sid in SPORTS:
        oc.add(DirectoryObject(key=Callback(ListSportVideos, sport_id=sid), title=SPORTS[sid]))

    return oc


####################################################################################################
@route(PREFIX + '/list-sport-videos')
def ListSportVideos(sport_id, page="1"):

    page_title = SPORTS[sport_id]

    page_url = URL + "&SPID=" + sport_id + "&PAGE=" + page
    log("Retrieving %s" % page_url)

    page = int(page)
    oc = ObjectContainer(title1=page_title, replace_parent=(page > 1))

    src = HTML.ElementFromURL(page_url)

    items = src.xpath("//ul[@class='section-links']/li")

    # first one is different
    hilite = items[0].xpath("./a[@class='highlight']")
    video_url = ROOT + hilite[0].get("href")
    video_title = hilite[0].get("title")
    video_thumb = ROOT + src.xpath(".//video/@poster")[0]

    oc.add(VideoClipObject(
        url=video_url,
        title=video_title,
        thumb=video_thumb
    ))

    for item in items[1:]:

        i = item.xpath("./a[@class='thumbnail']")

        if len(i) < 1:
            continue

        video_url = ROOT + i[0].get("href")
        video_title = i[0].get("title")
        video_thumb = ROOT + i[0].xpath(".//div/@style")[0].replace("background-image:url('", "").replace("')", "")

        oc.add(VideoClipObject(
            url=video_url,
            title=video_title,
            thumb=video_thumb
        ))

    # next page?
    navs = items[-1].xpath("./a[@class='highlight']")
    if len(navs) > 0:
        for nav in navs:
            if nav.text.strip().find('Next') > -1:
                oc.add(NextPageObject(key=Callback(ListSportVideos, sport_id=sport_id, page=page + 1),
                                      title="More Videos..."))

    return oc


####################################################################################################
def log(str):
    if DEBUG:
        Log.Debug(str)