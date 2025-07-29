import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from calendar import monthrange
from typing import Optional
from typing import List

def createTable():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Users(
                user_id TEXT,
                UserTag TEXT,
                HaveSub BOOL,
                StartSub TEXT, 
                EndSub TEXT,
                Rate INTEGER
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Posts(
                MessageID TEXT,
                Date TEXT)""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS NotificationMessages (
            days_before INTEGER PRIMARY KEY,
            message TEXT NOT NULL
        )
    """)
    bd.commit()
    cur.close()

def InitNotificationTable():
    conn = sqlite3.connect("Users.bd")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS NotificationMessages (
            days_before INTEGER PRIMARY KEY,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def GetNotificationMessage(days_before: int) -> str | None:
    try:
        conn = sqlite3.connect("Users.bd")
        cur = conn.cursor()
        cur.execute("SELECT message FROM NotificationMessages WHERE days_before = ?", (days_before,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Ошибка при получении уведомления: {e}")
        return None
    finally:
        conn.close()


def GetUsersWithExpiringSubscription(days_before: int = 3) -> List[int]:
    """
    Возвращает список user_id пользователей, у которых подписка заканчивается через days_before дней.
    """
    try:
        bd = sqlite3.connect('Users.bd')
        cur = bd.cursor()

        # Рассчитаем дату, которая сейчас + days_before дней
        target_date = (datetime.now() + timedelta(days=days_before)).date()

        cur.execute("""
            SELECT user_id FROM Users
            WHERE HaveSub = 1 AND DATE(EndSub) = DATE(?)
        """, (target_date.strftime('%Y-%m-%d'),))
        
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Ошибка в GetUsersWithExpiringSubscription: {e}")
        return []
    finally:
        cur.close()
        bd.close()

def GetAllNotificationMessages():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT days_before, message FROM NotificationMessages ORDER BY days_before DESC")
    result = cur.fetchall()
    cur.close()
    return result


def DeleteNotificationMessage(days_before: int) -> bool:
    """
    Удаляет уведомление из таблицы NotificationMessages по ключу days_before.
    Возвращает True, если удаление прошло успешно, False — если такого сообщения не было.
    """
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT 1 FROM NotificationMessages WHERE days_before = ?", (days_before,))
    if cur.fetchone() is None:
        cur.close()
        return False  # Сообщение с таким days_before не найдено
    
    cur.execute("DELETE FROM NotificationMessages WHERE days_before = ?", (days_before,))
    bd.commit()
    cur.close()
    return True

def SetNotificationMessage(days_before: int, message: str) -> bool:
    try:
        conn = sqlite3.connect("Users.bd")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO NotificationMessages (days_before, message)
            VALUES (?, ?)
            ON CONFLICT(days_before) DO UPDATE SET message=excluded.message
        """, (days_before, message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при установке уведомления: {e}")
        return False
    finally:
        conn.close()

def inicialize_Users(user_id,UserTag):
    createTable()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT user_id FROM Users WHERE user_id =?", (user_id,))
    result = cur.fetchone()
    if result:
       pass
    else:
        print("Добавился пользователь: " + str(user_id) + " " + UserTag)
        cur.execute("INSERT INTO Users (user_id, UserTag) VALUES (?, ?)", (user_id, UserTag))
    bd.commit()
    cur.close()

def SaveNewPost(Date,MessageID):
    createTable()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("INSERT INTO Posts (MessageID,Date) VALUES (?,?)",(MessageID,Date))
    try:
        print("Добавился новый пост")
    except:
        print("При сохранении поста возникла ошибка")
    bd.commit()
    cur.close()

import sqlite3
from datetime import datetime, timedelta


def Get_Posts_From_Start_Of_Month():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()

    now = datetime.now()
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    cur.execute("""
        SELECT MessageID, Date FROM Posts
        WHERE Date BETWEEN ? AND ?
    """, (start_month.strftime("%Y-%m-%d %H:%M:%S"), end_today.strftime("%Y-%m-%d %H:%M:%S")))

    posts = cur.fetchall()
    cur.close()

    result = [
        {
            "message_id": row[0],
            "date": datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"),
            "channel_id": -1002899688608  # Заменить на твой канал
        }
        for row in posts
    ]

    return result
    
    


def GetAllUsers():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT user_id,HaveSub,StartSub,EndSub,UserTag  FROM Users")
    result = cur.fetchall()
    if result:
        return result
    else:
        print(result)
        return False


def AddSubUser(userid, Rate):
    from Handlers.MainHandler import PostMessageForNewSub
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()

    now = datetime.now()

    # Получаем текущую подписку
    cur.execute("SELECT HaveSub, EndSub FROM Users WHERE user_id = ?", (userid,))
    row = cur.fetchone()

    if row and row[0]:  # Есть активная подписка
        try:
            current_end = datetime.strptime(row[1], '%Y-%m-%d')
            if current_end >= now:
                start_date = now
                base_date = current_end  # отталкиваемся от текущего конца подписки
            else:
                start_date = now
                base_date = now  # подписка истекла, считаем от сегодняшнего дня
        except Exception as e:
            print(f"Ошибка при разборе даты EndSub: {e}")
            base_date = now
            start_date = now
    else:
        start_date = now
        base_date = now

    # Рассчитываем новую дату окончания подписки
    if Rate == 1:
        if base_date.month == 12:
            end_date = datetime(base_date.year + 1, 1, 1)
        else:
            end_date = datetime(base_date.year, base_date.month + 1, 1)
    elif Rate == 3:
        end_date = base_date + relativedelta(months=3)
    elif Rate == 6:
        end_date = base_date + relativedelta(months=6)
    else:
        end_date = base_date + relativedelta(months=1)  # по умолчанию 1 месяц

    # Сохраняем/обновляем в базе
    cur.execute("SELECT user_id FROM Users WHERE user_id = ?", (userid,))
    if cur.fetchone():
        cur.execute("""UPDATE Users SET 
                        HaveSub = 1,
                        StartSub = ?, 
                        EndSub = ?,
                        Rate = ? 
                        WHERE user_id = ?""",
                    (start_date.strftime('%Y-%m-%d'),
                     end_date.strftime('%Y-%m-%d'),
                     Rate,
                     userid))
    else:
        cur.execute("""INSERT INTO Users (user_id, HaveSub, StartSub, EndSub, Rate)
                       VALUES (?, 1, ?, ?, ?)""",
                    (userid,
                     start_date.strftime('%Y-%m-%d'),
                     end_date.strftime('%Y-%m-%d'),
                     Rate))

    bd.commit()
    cur.close()

def GiveSubManual(userid: int, start_date: str, end_date: str, rate: Optional[int] = None):
    """
    Выдаёт подписку пользователю с произвольной датой начала и конца.

    :param userid: ID пользователя Telegram
    :param start_date: Дата начала в формате 'YYYY-MM-DD'
    :param end_date: Дата окончания в формате 'YYYY-MM-DD'
    :param rate: Опционально — длительность подписки (в месяцах или как захочешь)
    """
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()

    # Проверка: есть ли пользователь в БД
    cur.execute("SELECT user_id FROM Users WHERE user_id = ?", (userid,))
    if cur.fetchone():
        # Обновляем подписку
        cur.execute("""
            UPDATE Users SET
                HaveSub = 1,
                StartSub = ?,
                EndSub = ?,
                Rate = ?
            WHERE user_id = ?
        """, (start_date, end_date, rate, userid))
        print(f"[MANUAL SUB] Обновлена подписка у пользователя {userid}")
    else:
        # Добавляем нового пользователя с подпиской
        cur.execute("""
            INSERT INTO Users (user_id, HaveSub, StartSub, EndSub, Rate)
            VALUES (?, 1, ?, ?, ?)
        """, (userid, start_date, end_date, rate))
        print(f"[MANUAL SUB] Добавлен новый пользователь с подпиской: {userid}")

    bd.commit()
    cur.close()



def RemoveExpiredSubscriptions():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    SubHasEnded = []
    today = datetime.now().date()

    # Найдём всех пользователей с подпиской, срок которой истёк
    cur.execute("""
        SELECT user_id, EndSub FROM Users
        WHERE HaveSub = 1
    """)
    users = cur.fetchall()

    for user_id, end_sub in users:
        try:
            end_date = datetime.strptime(end_sub, "%Y-%m-%d").date()
            if today > end_date:
                # Снимаем подписку
                cur.execute("""
                    UPDATE Users
                    SET HaveSub = 0, Rate = NULL, StartSub = NULL, EndSub = NULL
                    WHERE user_id = ?
                """, (user_id,))
                print(f"Снята подписка с пользователя {user_id}")
                SubHasEnded.append(user_id)

        except Exception as e:
            print(f"Ошибка при проверке подписки у пользователя {user_id}: {e}")
    
    bd.commit()
    cur.close()
    return SubHasEnded

def CheckUser(user_id):
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT Rate,user_id,UserTag FROM Users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    return result


def CheckSubUser(userid):
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    
    # Проверка на наличие пользователя с активной подпиской
    cur.execute("SELECT HaveSub FROM Users WHERE user_id = ?", (userid,))
    result = cur.fetchone()
    
    if result:
        if result[0]:  # если HaveSub == 1
            print("Пользователь имеет подписку")
            cur.execute("SELECT StartSub FROM Users WHERE user_id =?", (userid,))
            return True
        else:
            print("Пользователь найден, но подписки нет")
            return False
    else:
        print("Пользователь не найден")
        return False
    
if __name__ == '__main__':
    GiveSubManual(7961153429,'2021-02-01','2023-02-01',2)