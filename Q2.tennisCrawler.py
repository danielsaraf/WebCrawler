import random
import time
import lxml.html as html
import requests

WIKI_PREFIX = "https://en.wikipedia.org"
MAX_CRAWLED = 80
SLEEPING_SECONDS = 3
requested_pages = set()
pages_depth = {}


def getTotalXpath(xpaths):
    # union xpaths expressions list to one xpath expression
    xpath = ""
    for xp in xpaths:
        xpath += xp + "|"
    xpath = xpath[0:len(xpath) - 1]
    return xpath


def dfs(url, xpath, step):
    connection_list = []
    # get url neighbors and update pages_depth and connection_list
    neighbors_list = get_neighbors(url, xpath)
    for url_neighbor in neighbors_list:
        if url_neighbor not in pages_depth:
            pages_depth[url_neighbor] = pages_depth[url] + 1
        if [url, url_neighbor] not in connection_list:
            connection_list.append([url, url_neighbor])

    # shuffle neighbors_list for randomness
    random.shuffle(neighbors_list)

    # reminder is the number of nodes that remind to enter for this dfs section
    reminder = 3 - step
    if reminder == 0:
        # done 3 steps
        return 0, []

    # search for a neighbor that has not been visited yet, and keep dfs from it
    for neighbor in neighbors_list:
        if neighbor not in requested_pages:
            reminder, cl = dfs(neighbor, xpath, step + 1)
            connection_list += cl
            if reminder == 0:  # if done step 3 nodes in this dfs section - return, o.w keep to another neighbor
                return 0, connection_list

    # in case that there is no neighbor that has not been visited yet,
    # tell the father about it with the reminder integer, so it will dfs another son
    return reminder, []


def get_neighbors(url, xpath):
    # sleep for SLEEPING_SECONDS (=3) seconds,
    # load the selected page and return a list of url that respond to xpath expression (concat url prefix)
    neighbors_list = []
    time.sleep(SLEEPING_SECONDS)
    page = requests.get(url)
    requested_pages.add(url)
    doc = html.fromstring(page.content)
    for sub_url in doc.xpath(xpath):
        neighbors_list.append(WIKI_PREFIX + sub_url)
    return neighbors_list


def get_next_url_bfs():
    # sort the dict by the keys values
    sort_dict_by_val = dict(sorted(pages_depth.items(), key=lambda item: item[1]))
    # return the value of the smallest key that has not been visited yet
    for url in list(sort_dict_by_val.keys()):
        if url not in requested_pages:
            return url
    # if every page been visited return None
    return None


def tennisCrawler(url, xpaths):
    # the main list of lists
    connection_list = []
    # union the xpaths
    xpath = getTotalXpath(xpaths)
    # enter the first url to the pages_depth dict (map between pages and their depth from the root page)
    pages_depth[url] = 0
    # crawl for 80 pages max
    while len(requested_pages) < MAX_CRAWLED:
        # get the closest page that has not been visited from pages_depth dict
        next_url = get_next_url_bfs()
        if next_url is None:  # all the pages been visited
            return connection_list
        # make 3 dfs moves and concat the return connection_list to the main list
        a, cl = dfs(next_url, xpath, 1)
        connection_list += cl

    return connection_list


def main():
    # root node - first tennis player
    root_node = 'https://en.wikipedia.org/wiki/Andy_Ram'

    # queries
    partners_expression = '//th[contains(text(),"Partner")]/../../../tbody/tr/td[1+count(../../../tbody/tr/th[contains(text(),"Partner")]/preceding-sibling::*)]/a[contains(@href,"/wiki/")]/@href'
    opponents_expression = '//th[contains(text(),"Opponent")]/../../../tbody/tr/td[1+count(../../../tbody/tr/th[contains(text(),"Opponent")]/preceding-sibling::*)]/a[contains(@href,"/wiki/")]/@href'
    coaches_expression = '//th[contains(text(),"Coach")]/../td/a[contains(@href,"/wiki/")]/@href'
    xpaths_list = [partners_expression, opponents_expression, coaches_expression]

    # start crawler and print result
    print(tennisCrawler(root_node, xpaths_list))


if __name__ == '__main__':
    main()
