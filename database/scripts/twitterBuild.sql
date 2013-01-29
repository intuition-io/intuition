CREATE TABLE sources(sourceid INTEGER, sourcedesc, PRIMARY KEY(sourceid));
INSERT INTO sources(sourcedesc) VALUES ("twitter");
SELECT * FROM sources;
CREATE TABLE tweets(id INTEGER, sourceid REAL, username TEXT, tweet TEXT, timestamp TIMESTAMP, PRIMARY KEY(id));
