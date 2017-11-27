use scorecards;

CREATE TABLE Flashline_FrontPage(
	ID 				INT		NOT NULL	AUTO_INCREMENT,
	dataDescription TEXT	NOT NULL,
    dataValue		TEXT,
    dataDate		DATE	NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Solutions_FrontPage(
	ID 				INT		NOT NULL	AUTO_INCREMENT,
	dataDescription TEXT	NOT NULL,
	dataValue		TEXT,
    dataDate		DATE	NOT NULL,
    PRIMARY KEY (ID)
);

use scorecards;

CREATE TABLE Soluitions_FrontPageGraph(
	ID 				INT				NOT NULL	AUTO_INCREMENT,
    begT			DATETIME		NOT NULL,
	avb				FLOAT			NOT NULL,
    appPerf			FLOAT			NOT NULL,
    CliCnt			FLOAT			NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Learn_FrontPage(
	ID 				INT		NOT NULL	AUTO_INCREMENT,
	dataDescription TEXT	NOT NULL,
	dataValue		TEXT,
    dataDate		DATE	NOT NULL,
    PRIMARY KEY (ID)
);

use scorecards;

CREATE TABLE Learn_FrontPageGraph(
	ID 				INT				NOT NULL	AUTO_INCREMENT,
    begT			DATETIME		NOT NULL,
	avb				FLOAT			NOT NULL,
    appPerf			FLOAT			NOT NULL,
    CliCnt			FLOAT			NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Banner_FrontPage(
	ID 				INT		NOT NULL	AUTO_INCREMENT,
	dataDescription TEXT	NOT NULL,
	dataValue		TEXT,
    dataDate		DATE	NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Banner_FrontPageGraph(
	ID 				INT				NOT NULL	AUTO_INCREMENT,
    begT			DATETIME		NOT NULL,
	avb				FLOAT			NOT NULL,
    appPerf			FLOAT			NOT NULL,
    CliCnt			FLOAT			NOT NULL,
    PRIMARY KEY (ID)
);