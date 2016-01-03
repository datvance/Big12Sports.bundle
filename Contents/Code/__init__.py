common = SharedCodeService.common

PREFIX = '/video/big12sports'
NAME = "Big 12 Sports"

ART = R('art-default.png')
ICON = R('icon-default.png')

RSS_URL = common.ROOT_URL + "/rss.dbml?db_oem_id=10410&RSS_SPORT_ID=%s&media=ondemand"

RSS_TEAMS_IDS = {
    '13120': 'Baylor',
    '13155': 'Iowa State',
    '13118': 'Kansas',
    '13116': 'Kansas State',
    '13121': 'Oklahoma',
    '13122': 'Oklahoma State',
    '13117': 'TCU',
    '13129': 'Texas',
    '13119': 'Texas Tech',
    '13151': 'West Virginia',
}

RSS_SPORTS_IDS = {
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
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"


####################################################################################################
@handler(PREFIX, "Big 12 Sports")
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(ListRSSCategories, rss_type="teams"), title='Teams'))
    oc.add(DirectoryObject(key=Callback(ListRSSCategories, rss_type="sports"), title='Sports'))

    return oc


####################################################################################################
@route(PREFIX + '/list-rss-categories')
def ListRSSCategories(rss_type):

    oc = ObjectContainer(title1=rss_type.title())

    if rss_type == "sports":
        rss_dict = RSS_SPORTS_IDS
    else:
        rss_dict = RSS_TEAMS_IDS

    for rss_id in rss_dict:
        oc.add(DirectoryObject(key=Callback(ListRSSVideos, rss_id=rss_id, name=rss_dict[rss_id]), title=rss_dict[rss_id]))

    return oc


####################################################################################################
@route(PREFIX + '/list-rss-videos')
def ListRSSVideos(rss_id, name):

    url = RSS_URL % rss_id
    common.log("Retrieving %s" % url)

    oc = ObjectContainer(title1=name)

    rss = XML.ElementFromURL(url)
    items = rss.xpath("//item")

    for item in items:

        try:
            title = item.xpath('./title/text()')[0]
            url = item.xpath('./link/text()')[0]
            thumb = item.xpath(".//enclosure/@url")[1]
            pubDate = item.xpath('./pubDate/text()')[0]
            pub_date = Datetime.ParseDate(pubDate).date()
            summary = item.xpath('./category/text()')[0]

            oc.add(VideoClipObject(
                url=url,
                title=title,
                thumb=thumb,
                originally_available_at=pub_date,
                summary=summary
            ))
        except Exception:
            pass

    return oc
