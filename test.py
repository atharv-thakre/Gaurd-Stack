from auth.service import *
from control.admin import *
from control.user import *
init_user_db()

conn = get_user_conn()
cur = conn.cursor()

# cur.execute('''insert into users(uid , email , password , role , is_active , created_at ) values (? , ?, ?, ?, ?, 0)
# ''',(1,"admin", simple_hash("admin") , "admin" , 1 ))

# cur.execute('''insert into users(uid , email , password , role , is_active , created_at) values (? , ?, ?, ?, ?, 0)
# ''',(2,"inactive-admin", simple_hash("admin") , "admin" , 0 ))

# cur.execute('''insert into users(uid , email , password , role , is_active , created_at) values (? , ?, ?, ?, ?, 0)
# ''',(3,"user", simple_hash("admin") , "user" , 1 ))

# cur.execute('''insert into users(uid , email , password , role , is_active , created_at) values (? , ?, ?, ?, ?, 0)
# ''',(4,"inactive-user", simple_hash("admin") , "user" , 0 ))

# conn.commit()

upgarde_user(5,"admin")
activate_user(5,0)

rows = get_all_users()
for i in rows :
    print(i)