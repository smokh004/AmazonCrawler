__author__ = 'shokoufeh'

from bs4 import BeautifulSoup
import urllib, pycurl, cStringIO, ast, sys, time
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

from math import *



posts = []
sentiments = []
# Expected number of arrivals per unit time.
opt = 10
n = 1000
SelectionSet = set()
MaximizeSet = set()

#amazon crawler
def crawl_amazon():
    p1 = "http://www.amazon.com/George-Foreman-GRP99-Generation-Removable/product-reviews/B0002KINSY/ref=cm_cr_pr_top_link_1?ie=UTF8&pageNumber="
    p2 = "&showViewpoints=0&sortBy=byRankDescending"
    file_name = "amazon_reviews.txt"
    with open(file_name, 'w') as fp:
        for pn in xrange(1, 88):
            url = p1 + str(pn) + p2
            amazon_url = p1 + str(pn) + p2
            ur = urllib.urlopen(amazon_url)
            soup = BeautifulSoup(ur.read())
            posts_ = soup.select("div.reviewText")
            for x in posts_: posts.append(x.text)
    return posts

#read amazon/macys reviews from file
def load_reviews(fn):
    posts = []
    with open(fn) as fp:
        for line in fp:
            posts.append(line[:-1])
    return posts

#compute sentiment for comments using text-processing API
def compute_tp_sentiments():
    cnt = 0
    for post in posts:
        try:
            cnt += 1
            buf = cStringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://text-processing.com/api/sentiment/')
            c.setopt(c.WRITEFUNCTION, buf.write)
            postdata = ''
            postdata = 'text=' + post
            c.setopt(c.POSTFIELDS, postdata)
            c.perform()
            val = buf.getvalue()
            data = ast.literal_eval(val)
            data["post"] = post
            sentiments.append(data)
            buf.close()
        except pycurl.error, error:
            errno, errstr = error
            print "An error occured: ", errstr
    print "sentiments computed for %d posts" % cnt
    return sentiments

#compute sentiments using vaderSentiment
def compute_vader_sentiments(posts):
    cnt = 0
    for post in posts:
        cnt += 1
        data = {}
        data["post"] = post
        vs = vaderSentiment(post)
        print vs
        if vs["neg"] >= vs["neu"] and vs["neg"] >= vs["pos"]:
            data["label"] = "neg"
        elif vs["pos"] >= vs["neu"] and vs["pos"] >= vs["neg"]:
            data["label"] = "pos"
        elif vs["neu"] >= vs["neg"] and vs["neu"] >= vs["pos"]:
            data["label"] = "neutral"
        sentiments.append(data)
    print "sentiments computed for %d posts" % cnt
    return sentiments

#overall sentiment summary
def compute_summary(sentiments):
    tot = len(sentiments)
    pos, neg, neu = 0, 0, 0
    for sent in sentiments:
        label = sent['label']
        if label == 'neutral':
            neu += 1
        elif label == 'pos':
            pos += 1
        elif label == 'neg':
            neg += 1
    print "total posts =", tot, "positives =", pos, ", negatives =", neg, ", neutrals =", neu

#run experiment
def run(rev_file = None, sent_file = None):
    if rev_file and sent_file:
        #load crawled amazon reviews from file
        posts = load_reviews(rev_file)
        print len(posts)
        #run sentiment analysis
        sentiments = compute_vader_sentiments(posts)
        with open(sent_file, 'w') as gp:
            for sent in sentiments:
                #print sent
                gp.write(str(sent) + '\n')
        compute_summary(sentiments)
    else:
        posts = crawl_amazon()
        sentiments = compute_vader_sentiments(posts)
        compute_summary(sentiments)




# Make a function iterable, by repeatedly calling it.
def make_iterable(func, *args):
    try:
        while 1:
            yield func(*args)
    except:
        pass
"""
uni_rand = make_iterable(random.uniform, 0, 1)

# A generator for inter-arrival times.
inter_arrival = ( -(1./K)*math.log(u) for u in uni_rand)

# Generate inter-arrival times, then sleep for that long.

time = 0
sum = 0
for t in range(T):
    if time + inter_arrival[0] <= t:
        time += inter_arrival[0]
        item = inter_arrival[0]
        del inter_arrival[0]
        SelectionSet.add(time)
        for e in SelectionSet:
            sum += math.pow((1 - 1/opt)/((1/1-math.exp(-(T-time))) - 1/opt), len(SelectionSet))
            if sum > MaxSum:
                MaxSum = sum """






def main():
    run()

if __name__ == "__main__":
    sys.exit(main())