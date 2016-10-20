drop table if exists stations;
create table stations (
  id integer primary key autoincrement,
  url text not null,
  title text not null
);
drop table if exists record_schedule;
create table record_schedule (
  id integer primary key autoincrement,
  url text not null,
  'start' text not null,
  'end' text not null,
  'status' text not null
);
drop table if exists recordings;
create table recordings (
  id integer primary key autoincrement,
  filename text not null,
  'date' text not null
);


