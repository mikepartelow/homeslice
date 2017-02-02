create table log_entries (
  id integer primary key autoincrement,
  log_name text not null,
  json text not null,
  timestamp timestamp not null default current_timestamp
);

create table buttons (
  id integer primary key autoincrement,
  name text not null,
  status text not null,
  timestamp timestamp not null default current_timestamp
);
