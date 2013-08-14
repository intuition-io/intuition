require('node.io').scrape(function() {
    this.getHtml('http://www.reddit.com/', function(err, $) {
        var stories = [];
        $('a.title').each(function(title) {
            stories.push(title.text);
        });
        this.emit(stories);
    });
});
