drop table if exists users;
create table users (
    userid text primary key not null,
    username text not null,
    email text not null,
    passwordhash text not null,
    groupstatus text
);
drop table if exists submissions;
create table submissions (
    submissionid text primary key not null,
    userid text not null,
    submissiondate timestamp,
    problemid text not null,
    submissiontext text,
    submissionstatus text,
    executiontime text
);
drop table if exists files;
create table files (
    fileid text primary key not null,
    userid text not null,
    creationdate timestamp,
    lastupdateddate timestamp,
    filename text not null
);
