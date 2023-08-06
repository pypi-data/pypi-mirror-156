import math
import threading

import pymongo
import requests
from sqltool.mysql_client import MySqlClient

from bson import ObjectId
import datetime
'''
hex_package_info
'''


class PackageFile():
    def __init__(self, version, file_name, file_type, file_md5, package_id, package_type):
        self.version = version
        self.file_name = file_name
        self.file_type = file_type
        self.file_md5 = file_md5
        self.package_id = package_id
        self.package_type = package_type


class PackageInfo():
    def __init__(self, package_name, description, home_page, repository_url, license, package_type):
        self.package_name = package_name
        self.description = description
        self.home_page = home_page
        self.repository_url = repository_url
        self.license = license
        self.package_type = package_type

class PackageVersion():
    def __init__(self, version, license, publish_time, package_name, package_type):
        self.version = version
        self.license = license
        self.publish_time = publish_time
        self.package_name = package_name

        self.package_type = package_type


class PackageDeps():
    def __init__(self, dependency_version_expression, lj_dependency_version_expression, dependency_type, package_name
                 , package_version, dependency_package_name, package_type, requirement=None):
        self.dependency_version_expression = dependency_version_expression
        self.lj_dependency_version_expression = lj_dependency_version_expression
        self.dependency_type = dependency_type
        self.package_name = package_name
        self.package_version = package_version
        self.dependency_package_name = dependency_package_name

        self.package_type = package_type
        self.requirement = requirement


class SqlTool(object):
    def __init__(self):
        self.conn_local = MySqlClient(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd='123',
            db='data_center',
            charset='utf8mb4'
        )
        self.create_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        # self.conn_lj_id = MySqlClient(
        #     host=MYSQL_17_HOST,
        #     port=MYSQL_17_PORT,
        #     user=MYSQL_17_USER,
        #     passwd=MYSQL_17_PASSWORD,
        #     db=MYSQL_17_DB,
        #     charset=MYSQL_17_CHARSET
        # )

    def package_file(self, file: PackageFile):

        sql = f"insert into `package_file`(`version`, `file_name`, `file_type`, `file_md5`, `package_id`, `package_type`" \
              f") values('%s', '%s', '%s', '%s', %d, '%s')"%(file.version, file.file_name, file.file_type, file.file_md5,
                                                        file.package_id, file.package_type)
        return self.conn_local.execute(sql)

    def package_info(self, package: PackageInfo):
        # 如果存在  则进行更新操作
        sql = f"insert into `package_info`(`package_name`, `description` ,`home_page` ,`repository_url` ," \
              "`license` ,`package_type`) values('%s', '%s', '%s', '%s', '%s', '%s')" \
              % (package.package_name, package.description, package.home_page, package.repository_url,
                 package.license, package.package_type)
        return self.conn_local.execute(sql)

    def package_version(self, version: PackageVersion):
        # 如果存在  则进行更新操作
        info_sql = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'"\
                   %(version.package_name, version.package_type)
        data = self.conn_local.get_one(info_sql)
        if data:
            sql = "insert into `package_version`(`version`, `license`, `publish_time`, `package_name`, " \
                  "`package_id`, `package_type`) values" "('%s', '%s', '%s', '%s', %d, '%s')" % \
                  (version.version, version.license, version.publish_time,
                   version.package_name, int(data['id']), data['package_type'])
            return self.conn_local.execute(sql)
        else:
            print('查询信息不存在')

    def package_deps(self, deps: PackageDeps):
        # 如果存在  则进行更新操作
        info_sql = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (deps.package_name, deps.package_type)
        _data = self.conn_local.get_one(info_sql)
        version_sql = "select id from `package_version` where package_name= '%s' and package_type='%s'" \
                   % (deps.package_name, deps.package_type)
        version_id = self.conn_local.get_one(version_sql)
        if _data and version_sql:
            if deps.requirement:
                for require in deps.requirement:
                    deps_info = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'" \
                               % (deps.requirement[require]['app'], deps.package_type)
                    deps_id = self.conn_local.get_one(deps_info)
                    deps_version = "select id from `package_version` where package_name= '%s' and package_type='%s'" \
                                  % (deps.requirement[require]['app'], deps.package_type)
                    deps_version = self.conn_local.get_one(deps_version)

                    sql = f"insert into package_dependencies(`dependency_version_expression`, " \
                          f"`lj_dependency_version_expression`, `dependency_type`, `package_name`, `package_version`, " \
                          f"`dependency_package_name`, `dependency_package_id`, `dependency_version_id`, `package_id`, " \
                          f"`package_type`, `version_id`) values('%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', %d)"%(
                    deps.dependency_version_expression,
                    deps.lj_dependency_version_expression, deps.dependency_type,
                    deps.package_name, deps.package_version, deps.requirement[require]['app'],
                    deps_id['id'],deps_version['id'], _data['id'],
                    _data['package_type'],
                    version_id['id']
                    )
                    print(sql)
                    return self.conn_local.execute(sql)
            else:
                sql = f"insert into package_dependencies(`dependency_version_expression`, " \
                      f"`lj_dependency_version_expression`, `dependency_type`, `package_name`, `package_version`, " \
                      f"`dependency_package_name`, `dependency_package_id`, `dependency_version_id`, `package_id`, " \
                      f"`package_type`, `version_id`) values('%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', %d)" % (
                          deps.dependency_version_expression, deps.lj_dependency_version_expression,
                          deps.dependency_type,
                          deps.package_name, deps.package_version, deps.dependency_package_name,
                          1,
                          '', _data['id'], _data['package_type'],
                          version_id['id']
                      )
                return self.conn_local.execute(sql)
        else:
            print("查询信息不存在")


