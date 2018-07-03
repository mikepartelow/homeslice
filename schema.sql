create table buttons (
  id integer primary key autoincrement,
  name text not null,
  status text not null,
  timestamp timestamp not null default current_timestamp
);
