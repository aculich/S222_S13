#!/usr/bin/env python
import os
import sys
import pickle
import gdata.youtube
import gdata.youtube.service

def main():
#    logger = logging.getLogger()
#    logger.setLevel(logging.DEBUG)
    yt_service = gdata.youtube.service.YouTubeService()
    old_file_exists = True
    try:
        data_file = open('new_comments.pickle','rb') # append to existing file if possible
        data = pickle.load(data_file)
        data_file.close()
        print "found comments file"
    except:
        data = dict() # no existing file, so start a new dictionary
        old_file_exists = False
        print "starting new file"
    file = open('unique_all_ids',"r") # get the video ids we want
    ids = [x.rstrip() for x in file.readlines()]
    nf = 0

    nvids = len(ids)
    response = []
    
    for i in range(0,nvids):
        id = ids[i]
        if id in data: 
#            print id," exists"
            continue # we already have the comments from this video
        too_fast = True
        while(too_fast): # delay loop to get next set of comments
            too_fast = False
            try:
                comment_feed = yt_service.GetYouTubeVideoCommentFeed(video_id=id)
                data[id] = []
                for comment_entry in comment_feed.entry:
                    data[id].append(comment_entry.content.text)
                     #data[id] = yt_service.GetYouTubeVideoEntry(video_id=id)
            except gdata.service.RequestError, err:
                response = err[0]
#                print "Oops: ", response['body']
                if "too_many" in response['body']:
                    too_fast = True
                    sys.stderr.write("sleeping 10 at %d\n" % i)
                    os.system("sleep 10")
                else:
                    data[id] = None # got a different error, so bump the not-found count and press on
                    nf += 1
        d = data[id]
        print "\nvideo id: " + ids[i]# + "data: ", d # lots of output -- should be redirected to a file
        if d == None:
            print "not found: ", response['body']
        else:
            print "OK"#data[id]
        if i > 0 and i%1000 == 0: # checkpoint every so often and write the pickle file so we can restart from here
            data_file = open('new_comments.pickle','wb')
            pickle.dump(data,data_file)
            data_file.close() 
            
    print nf," videos were not found"
    data_file = open('new_comments.pickle','wb')
    pickle.dump(data,data_file) # write the final pickle file
    data_file.close()

if __name__ == "__main__":
    main()

