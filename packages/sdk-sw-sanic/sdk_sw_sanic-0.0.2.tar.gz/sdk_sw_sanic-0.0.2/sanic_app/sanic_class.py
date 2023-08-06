from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import SanicException
from sanic.log import logger
import sqlite3
import subprocess
import base64

from camera import camera_on_cv, stop_camera
from delivered_key import derived_key, same_derived_key
from sdk_functions import change_led, busser_beep, get_media

connection = sqlite3.connect('sdk_db.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS sdk_table (id INT,request_id VARCHAR NOT NULL, is_file_created BOOLEAN , 
        file_name TEXT, created_at DATETIME default CURRENT_TIMESTAMP, request_by TEXT, status BOOLEAN )''')


class SetUpRoutes(HTTPMethodView):
    """here the basic api method of get all data and create data"""

    async def get(self, request):
        """get all data from the table sdk_table"""
        select_all = "SELECT * FROM sdk_table"
        try:
            rows = cursor.execute(select_all).fetchall()
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} while get all data")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        field_names = [i[0] for i in cursor.description]
        row_list = []
        for row in rows:
            students_dict = dict(zip(field_names, row))
            row_list.append(students_dict)
        logger.info('Successfully get all data')

        return json({
            "data": row_list
        })

    async def post(self, request):
        """inserting data to table sdk_table by direct insert sql query"""
        data = request.json
        insert_records = f"INSERT INTO sdk_table (id,request_id, is_file_created, file_name, created_at, \
                            request_by, status) values(?,?,?,?,?,?,?) "
        try:
            contents = data['id'], data['request_id'], data['is_file_created'], data['file_name'], data['created_at'], \
                       data['request_by'], data['status']
        except KeyError as err:
            logger.error(f"KeyError,this {str(err)} field is missing while add data")
            return json(
                {
                    "status": "failed",
                    "message": f"{str(err)} missing"
                }
            )
        try:
            cursor.execute(insert_records, contents)
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)}")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        connection.commit()
        logger.info('Successfully data added')
        return json({
            "data": data
        })


class IdRoutes(HTTPMethodView):
    """herre having the basic api method as getting data by Id , Update by Id,\
    incase needed for delete by id, update single field by id"""

    async def get(self, request, id_):
        """get data by id"""
        select_all = f"SELECT * FROM sdk_table WHERE id={id_}"
        try:
            rows = cursor.execute(select_all).fetchall()
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} while get data of id {id_}")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        field_names = [i[0] for i in cursor.description]
        row_list = []
        for row in rows:
            students_dict = dict(zip(field_names, row))
            row_list.append(students_dict)
        logger.info(f'Successfully get data of {id_}')
        return json({
            "data": row_list
        })

    async def put(self, request, id_):
        """update entire row by id in direct sql query Update"""
        data = request.json
        select_all = f"Update sdk_table set id=?,request_id=?,is_file_created=?,\
                        file_name=?,created_at=?,request_by=?,\
                        status=? where id=?"
        try:
            contents = data['id'], data['request_id'], data['is_file_created'], data['file_name'], data['created_at'], \
                       data['request_by'], data['status'], id_
        except KeyError as err:
            logger.error(f"KeyError,this {str(err)} field is missing while update in {id_}")
            return json(
                {
                    "status": "failed",
                    "message": f"{str(err)} missing"
                }
            )
        try:
            cursor.execute(select_all, contents)
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} while update in {id_}")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        connection.commit()
        logger.info(f'Successfully update data of {id_} as fully')
        return json({
            "data": data
        })

    async def delete(self, id_):
        """delete data by id"""
        select_all = f"DELETE from sdk_table where id=?"
        contents = id_
        try:
            cursor.execute(select_all, contents)
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} while delete {id_}")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        connection.commit()
        logger.info(f'Successfully delete data of {id_}')
        return json({
            "data": "successfully deleted"
        })

    async def patch(self, request, id_):
        """update a single field by id on by giving"""
        data = request.json
        key = list(data.keys())[0]
        value = list(data.values())[0]
        select_all = f"Update sdk_table set {key}=? where id=?"
        try:
            contents = value, id_
        except KeyError as err:
            logger.error(f"KeyError,this {str(err)} field is missing while update {key}")
            return json(
                {
                    "status": "failed",
                    "message": f"{str(err)} missing"
                }
            )
        try:
            cursor.execute(select_all, contents)
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} wihile update by field")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        connection.commit()
        logger.info(f'Successfully update data of {id_} in {key}')
        return json({
            "data": data
        })


class RequestIdRoutes(HTTPMethodView):
    """class function for Request Id"""

    async def get(self, request, request_id):
        """filter data on based by request_id from table"""
        select_all = f"SELECT * FROM sdk_table WHERE request_id='{request_id}'"
        try:
            rows = cursor.execute(select_all).fetchall()
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)} in get request_id")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        field_names = [i[0] for i in cursor.description]
        row_list = []
        for row in rows:
            students_dict = dict(zip(field_names, row))
            row_list.append(students_dict)
        logger.info(f'Successfully get all data by request_id is {request_id}')
        return json({
            "data": row_list
        })


class StatusRoutes(HTTPMethodView):
    """class function for Status"""

    async def get(self, request, status):
        """filtering data on based status"""
        select_all = f"SELECT * FROM sdk_table WHERE status={status}"
        try:
            rows = cursor.execute(select_all).fetchall()
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)}in get status")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        field_names = [i[0] for i in cursor.description]
        row_list = []
        for row in rows:
            students_dict = dict(zip(field_names, row))
            row_list.append(students_dict)
            logger.info(f'Successfully get all data by status is {status}')
        return json({
            "data": row_list
        })


class CreatedAtRoutes(HTTPMethodView):
    """class function for created at"""

    async def get(self, request, created_at):
        """filtering data on based created_at"""
        select_all = f"SELECT * FROM sdk_table WHERE created_at='{created_at}'"
        try:
            rows = cursor.execute(select_all).fetchall()
        except sqlite3.OperationalError as err:
            logger.error(f"sqlite3 OperationalError {str(err)}in get created_at")
            return json(
                {
                    "status": "failed",
                    "message": str(err)
                }
            )
        field_names = [i[0] for i in cursor.description]
        row_list = []
        for row in rows:
            students_dict = dict(zip(field_names, row))
            row_list.append(students_dict)
        logger.info(f'Successfully get all data by created_at is {created_at}')
        return json({
            "data": row_list
        })


class CameraOnRoutes(HTTPMethodView):
    """class function for open camera"""

    async def get(self, request):
        """filtering data on based created_at"""
        camera_on_cv()

        return json(
            {
                "status": "success",
            }
        )


class CameraCloseRoutes(HTTPMethodView):
    """class function for open camera"""

    async def get(self, request):
        """filtering data on based created_at"""
        stop_camera()

        return json(
            {
                "status": "camera closed",
            }
        )


class ImportCLanguage(HTTPMethodView):
    """class function for open camera"""

    async def get(self, request):
        """filtering data on based created_at"""
        file = request.form.get("file")
        subprocess.call(["gcc", f'{file}'])
        subprocess.call("./a.out")
        logger.info("c file is successfully read")

        return json(
            {
                "status": "file upload",
            }
        )


class ChangeLedRoutes(HTTPMethodView):
    """class function for change led"""

    async def get(self, request):
        """filtering data on based created_at"""
        change_led()
        logger.info("change_led is successfully done")

        return json(
            {
                "status": "success",
                "message": "Led change"
            }
        )


class BusserBeepRoutes(HTTPMethodView):
    """class function for busser_beep"""

    async def get(self, request):
        """filtering data on based created_at"""
        busser_beep()
        logger.info("busser_beep is successfully done")

        return json(
            {
                "status": "success",
                "message": "busser_beepe"
            }
        )


class GetMediaRoutes(HTTPMethodView):
    """class function for change led"""

    async def get(self, request):
        """filtering data on based created_at"""
        get_media()
        logger.info("get_media is successfully done")

        return json(
            {
                "status": "success",
                "message": "get_media"
            }
        )


class DerivedKeyRoutes(HTTPMethodView):
    """class function for sending derived key"""

    async def get(self, request):
        """filtering data on based created_at"""
        # derived_key()
        encoded = base64.b64encode(derived_key())
        logger.info("derived_key is successfully send")

        return json(
            {
                "status": "success",
                "data": str(encoded)
            }
        )


class SameDerivedKeyRoutes(HTTPMethodView):
    """class function for sending derived key"""

    async def get(self, request):
        """filtering data on based created_at"""
        # same_derived_key()
        encoded = base64.b64encode(same_derived_key())
        logger.info("same_derived_key is successfully given")

        return json(
            {
                "status": "success",
                "data": str(encoded)
            }
        )
