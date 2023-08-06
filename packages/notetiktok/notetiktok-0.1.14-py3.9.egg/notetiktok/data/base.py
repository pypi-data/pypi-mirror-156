import json
import os

import pandas as pd
from notedrive.sqlalchemy.base import BaseTable, create_engines, meta
from notetool.secret import read_secret
from sqlalchemy import BIGINT, TIMESTAMP, Column, String, Table, func, select

uri = read_secret(cate1='notetiktok', cate2='dataset', cate3='db_path')
uri = uri or f'sqlite:///{os.path.abspath(os.path.dirname(__file__))}/data/notetiktok.db'

engine = create_engines(uri)


class ResourceType:
    UNKNOWN = 0
    PIC = 1
    VIDEO = 2
    M3U8 = 3


# 来源
class SourceDetail(BaseTable):
    def __init__(self, table_name="notetiktok_source_detail", *args, **kwargs):
        super(SourceDetail, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('source_id', String, comment='来源ID', primary_key=True),
                           Column('main_url', String, comment='来源网站主页', default=''),
                           Column('status', BIGINT, comment='状态', default=1),
                           )
        self.create()


# 用户
class AuthorDetail(BaseTable):
    def __init__(self, table_name="notetiktok_author_detail", *args, **kwargs):
        super(AuthorDetail, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('source_id', String, comment='来源ID', primary_key=True),
                           Column('author_id', String, comment='用户ID', primary_key=True),
                           Column('gmt_create', TIMESTAMP(True), server_default=func.now()),
                           Column('gmt_modified', TIMESTAMP(True), server_default=func.now()),
                           Column('status', BIGINT, comment='状态', default=1),
                           Column('name', String, comment='名称', default='无名氏'))
        self.create()


# 资源
class ResourceDetail(BaseTable):
    def __init__(self, table_name="notetiktok_resource_detail", *args, **kwargs):
        super(ResourceDetail, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('source_id', String, comment='来源ID', primary_key=True),
                           Column('resource_id', String, comment='资源ID', primary_key=True),
                           Column('gmt_create', TIMESTAMP(True), server_default=func.now()),
                           Column('gmt_modified', TIMESTAMP(True), server_default=func.now()),
                           Column('status', BIGINT, comment='状态', default=1),
                           Column('resource_type', BIGINT, comment='资源类型', default=0),
                           Column('author_id', String, comment='作者ID', default=''),
                           Column('title', String, comment='标题', default=''),
                           Column('sub_title', String, comment='子标题', default=''),
                           Column('content', String, comment='内容', default=''),
                           Column('url', String, comment='资源地址', default=''),
                           Column('source_url', String, comment='资源原地址', default=''))
        self.create()

    def get_resource(self, start, stop, resource_type=None, author_id=None):
        condition = []
        if resource_type is not None:
            condition.append(self.table.c.resource_type == resource_type)
        if author_id is not None:
            condition.append(self.table.c.author == author_id)

        smt = select([self.table])
        if condition is not None and len(condition) > 0:
            smt = smt.where(*condition)

        df = pd.read_sql(smt.slice(start, stop), self.engine)
        return json.loads(df.to_json(orient='records'))


# 点赞
class FavoriteDetail(BaseTable):
    def __init__(self, table_name="notetiktok_favorite_detail", *args, **kwargs):
        super(FavoriteDetail, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('user_id', String, comment='用户ID', primary_key=True),
                           Column('source_id', String, comment='来源ID', primary_key=True),
                           Column('resource_id', String, comment='资源ID', primary_key=True),
                           Column('gmt_create', TIMESTAMP(True), server_default=func.now()),
                           Column('gmt_modified', TIMESTAMP(True), server_default=func.now()),
                           Column('status', BIGINT, comment='状态', default=1),
                           )
        self.create()

    def get_favor(self, start=0, stop=20, user_id=None, source_id=None):
        condition = []
        if user_id is not None:
            condition.append(self.table.c.user_id == user_id)
        if source_id is not None:
            condition.append(self.table.c.author == source_id)

        smt = select([self.table])
        if condition is not None and len(condition) > 0:
            smt = smt.where(*condition)

        df = pd.read_sql(smt.slice(start, stop), self.engine)
        return json.loads(df.to_json(orient='records'))


# 关注
class FollowDetail(BaseTable):
    def __init__(self, table_name="notetiktok_follow_detail", *args, **kwargs):
        super(FollowDetail, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('user_id', String, comment='用户ID', primary_key=True),
                           Column('source_id', String, comment='来源ID', primary_key=True),
                           Column('author_id', String, comment='作者ID', primary_key=True),
                           Column('gmt_create', TIMESTAMP(True), server_default=func.now()),
                           Column('gmt_modified', TIMESTAMP(True), server_default=func.now()),
                           Column('status', BIGINT, comment='状态', default=1),
                           )
        self.create()

    def get_following(self, start=0, stop=20, user_id=None, source_id=None):
        condition = []
        if user_id is not None:
            condition.append(self.table.c.user_id == user_id)
        if source_id is not None:
            condition.append(self.table.c.author == source_id)

        smt = select([self.table])
        if condition is not None and len(condition) > 0:
            smt = smt.where(*condition)
        smt = smt.order_by(self.table.c.gmt_create.desc())
        df = pd.read_sql(smt.slice(start, stop), self.engine)
        return json.loads(df.to_json(orient='records'))
