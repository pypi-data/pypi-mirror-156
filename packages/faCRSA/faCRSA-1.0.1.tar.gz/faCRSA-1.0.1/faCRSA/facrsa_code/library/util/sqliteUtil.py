import logging
import sqlite3
import traceback


class sqliteUtil():
    def __init__(self):
        self.conn = sqlite3.connect("facrsa.db")
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()
        self.check_table()

    def check_table(self):
        try:
            self.cursor.execute("select * from task")
            self.cursor.execute("select * from user")
            self.cursor.execute("select * from result")
        except:
            self.cursor.execute("""
            CREATE TABLE `user` (
              `uid` int(11) NOT NULL,
              `username` varchar(100) NOT NULL,
              `password` varchar(100) NOT NULL,
              `email` varchar(30) NOT NULL,
              `create_time` datetime(6) NOT NULL
            )
            """)
            self.cursor.execute("""
            CREATE TABLE `task` (
              `tid` varchar(40) NOT NULL,
              `task_name` varchar(100) DEFAULT '0',
              `description` varchar(100) DEFAULT NULL,
              `factor` double NOT NULL DEFAULT '0.0166',
              `email` varchar(50) DEFAULT NULL,
              `private_plugin` varchar(50) NOT NULL DEFAULT '0',
              `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
              `update_time` varchar(30) DEFAULT NULL,
              `del` int(1) DEFAULT '0',
              `status` varchar(1) NOT NULL DEFAULT '2',
              `uid` varchar(8) DEFAULT NULL
            )
            """)
            self.cursor.execute("""
            CREATE TABLE `result` (
              `rid` int(10) NOT NULL,
              `tid` varchar(40) DEFAULT NULL,
              `tid_p` int(3) DEFAULT NULL,
              `user` varchar(50) DEFAULT NULL,
              `image` varchar(1000) DEFAULT NULL,
              `re_img` varchar(200) DEFAULT NULL,
              `trl` varchar(100) DEFAULT '0',
              `trpa` varchar(100) DEFAULT '0',
              `trv` varchar(100) DEFAULT '',
              `tsa` varchar(100) DEFAULT '',
              `mrl` varchar(100) DEFAULT '0',
              `mrpa` varchar(100) DEFAULT '0',
              `msa` varchar(100) DEFAULT '',
              `mrv` varchar(100) DEFAULT '',
              `cha` varchar(100) DEFAULT '',
              `mrd` varchar(100) DEFAULT '',
              `trlp` varchar(100) DEFAULT '0',
              `trap` varchar(100) DEFAULT '0',
              `mrlp` varchar(100) DEFAULT '0',
              `mrap` varchar(100) DEFAULT '0',
              `status` char(100) NOT NULL DEFAULT 'Error'
            )
            """)
            traceback.print_exc()
        finally:
            self.conn.commit()
            # self.cursor.close()
            # self.conn.close()

    def dict_factory(self, cursor, row):
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]
        return d

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            return str(200)
        except:
            traceback.print_exc()
            self.conn.rollback()
            return str(400)
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def fetch_one(self, sql):
        result = ''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except:
            traceback.print_exc()
            self.conn.rollback()
            return str(400)
        finally:
            self.cursor.close()
            self.conn.close()
            return result

    def fetch_all(self, sql):
        results = ''
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except:
            traceback.print_exc()
            self.conn.rollback()
            return str(400)
        finally:
            self.cursor.close()
            self.conn.close()
            return results

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            # 把这些异常保存到一个日志文件中，来分析这些异常
            # 将错误日志输入到目录文件中
            # f = open("\log.txt", 'a')
            # traceback.print_exc(file=f)
            # f.flush()
            # f.close()
            # 如果发生异常，则回滚
            traceback.print_exc()
            self.conn.rollback()
        finally:
            # 最终关闭数据库连接
            self.cursor.close()
            self.conn.close()

    def update(self, sql):
        '''
            更新结果集
        '''
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            self.conn.commit()
            return str(200)
        except:
            traceback.print_exc()
            self.conn.rollback()
            return str(400)
        finally:
            self.cursor.close()
            self.conn.close()
