drop table if exists users;
create table users (
    userid text primary key not null,
    username text not null,
    email text not null,
    passwordhash not null
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
