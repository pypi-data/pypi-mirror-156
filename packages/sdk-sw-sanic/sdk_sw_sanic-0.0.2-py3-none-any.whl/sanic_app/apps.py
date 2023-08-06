""" Application initializer """
from sanic import Sanic
from sanic_class import DerivedKeyRoutes, SameDerivedKeyRoutes, SetUpRoutes, RequestIdRoutes, StatusRoutes, CreatedAtRoutes, IdRoutes, CameraOnRoutes, \
    ImportCLanguage, CameraCloseRoutes, ChangeLedRoutes, BusserBeepRoutes, GetMediaRoutes
import logging

app = Sanic(__name__)

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename = "logfile.log",
                    filemode = "w",
                    format = Log_Format,
                    level = logging.ERROR)

# def create_app():
#     app = Sanic(__name__)
#     return app

app.add_route(SetUpRoutes.as_view(), "/gets")
app.add_route(IdRoutes.as_view(), "/get/<id_:int>")
app.add_route(RequestIdRoutes.as_view(), "/request_id/<request_id:str>")
app.add_route(StatusRoutes.as_view(), "/status/<status:str>")
app.add_route(CreatedAtRoutes.as_view(), "/created_at/<created_at:str>")
app.add_route(CameraOnRoutes.as_view(), "/camera_on")
app.add_route(CameraCloseRoutes.as_view(), "/camera_off")
app.add_route(ImportCLanguage.as_view(), "/import_c")
app.add_route(ChangeLedRoutes.as_view(), "/change_led")
app.add_route(BusserBeepRoutes.as_view(), "/busser_beep")
app.add_route(GetMediaRoutes.as_view(), "/get_media")
app.add_route(DerivedKeyRoutes.as_view(), "/derived_key")
app.add_route(SameDerivedKeyRoutes.as_view(), "/same_derived_key")



# exception_handler(app=app)

if __name__ == "__main__":
    app.run(port=2000, workers=1)


