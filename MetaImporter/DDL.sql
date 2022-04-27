create table djs_books
(
    id           integer primary key autoincrement,
    url          text(300) not null,
    index_title  text(300) not null,
    origin_title text(300) not null,
    gallery_id   integer   not null,
    pages        integer   not null,
    uploaded     text(100) not null,
    path         text(300) not null
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

select *
from djs_books
where gallery_id in (
    select gallery_id
    from djs_associate
    where property = 'Tags' and p_value == 'double penetration' or p_value == 'milf'
);

select distinct property
from djs_associate;