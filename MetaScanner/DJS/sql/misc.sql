create table djs_books
(
    id                integer primary key autoincrement,
    url               text(500) not null,
    index_title       text(500) not null,
    origin_title      text(500) not null,
    gallery_id        integer   not null,
    pages             integer   not null,
    uploaded          text(100) not null,
    path              text(500) not null unique,
    device_tag        text(100) not null default '',
    meta_version      text(10)  not null,
    preview           BLOB,
    secondary_preview BLOB
);

create table djs_associate
(
    id         integer primary key autoincrement,
    gallery_id integer  not null,
    property   text(10) not null,
    p_value    text(50) not null
);

select *
from djs_books;


DELETE
FROM sqlite_sequence
WHERE name = 'djs_associate';


select *
from djs_associate
where gallery_id = 342935;


select distinct property
from djs_associate;