import sqlite3

conn = sqlite3.connect('workout_history.db')
c = conn.cursor()

# 테이블 목록
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()

print('=== workout_history.db 테이블 ===')
for table in tables:
    print(f'\nTable: {table[0]}')
    c.execute(f'PRAGMA table_info({table[0]})')
    columns = c.fetchall()
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')
    
    # 샘플 데이터 출력
    c.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = c.fetchone()[0]
    print(f'  Records: {count}')

conn.close()
